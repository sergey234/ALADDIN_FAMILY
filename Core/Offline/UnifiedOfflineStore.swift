import Foundation
import CoreData
import Combine
import UIKit

/// 🚀 UnifiedOfflineStore v2
/// Единый reactive слой оффлайн-хранения для всего приложения
/// Цель: сделать оффлайн "из коробки" по принципу InstantDB-like подхода
/// - Автоматический merge при восстановлении связи
/// - Приоритезация данных (critical, important, normal)
/// - Reactive обновления через Combine
/// - Минимальный код на стороне ViewModel/экранов
final class UnifiedOfflineStore: ObservableObject {
    
    static let shared = UnifiedOfflineStore()
    
    /// Фаза синхронизации store (не путать с `OfflineStorageManager.SyncStatus`)
    @Published private(set) var storeSyncPhase: UnifiedStoreSyncPhase = .idle
    @Published var pendingCount: Int = 0
    @Published var lastSyncDate: Date?
    
    private let persistentContainer: NSPersistentContainer
    private let backgroundContext: NSManagedObjectContext
    private let viewContext: NSManagedObjectContext
    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard
    
    private var cancellables = Set<AnyCancellable>()
    private let lastSyncTimestampKey = "unified_offline_last_sync_timestamp"
    private let offlineDeviceIdKey = "unified_offline_device_id"
    
    private init() {
        let model = UnifiedOfflineManagedObjectModelFactory.makeModel()
        self.persistentContainer = NSPersistentContainer(name: "ALADDINUnifiedOffline", managedObjectModel: model)
        self.persistentContainer.loadPersistentStores { description, error in
            if let error = error {
                fatalError("❌ UnifiedOfflineStore: Failed to load persistent stores: \(error)")
            }
        }
        
        self.viewContext = persistentContainer.viewContext
        self.backgroundContext = NSManagedObjectContext(concurrencyType: .privateQueueConcurrencyType)
        self.backgroundContext.parent = viewContext
        
        loadPendingCount()
        // Откладываем подписку на `OfflineManager`, иначе deadlock при первом доступе
        // `OfflineManager.shared` → `UnifiedOfflineStore.shared` → снова `OfflineManager.shared`.
        DispatchQueue.main.async { [weak self] in
            self?.setupAutomaticSync()
        }
    }
    
    // MARK: - Public API ("из коробки" — основной интерфейс для всех менеджеров)

    /// Универсальное сохранение (используется всеми менеджерами)
    func save<T: Codable>(
        _ object: T,
        type: OfflineDataType,
        priority: DataPriority = .normal
    ) async -> Result<Void, Error> {
        let result = await saveToCoreData(object: object, type: type, priority: priority)
        if case .success = result {
            objectWillChange.send() // Reactive update
            SyncEngine.shared.publish(
                domain: syncDomain(for: type),
                operation: "local_save",
                state: .pending,
                metadata: ["type": type.rawValue, "priority": "\(priority.rawValue)"]
            )
        }
        return result
    }

    /// Получить данные определённого типа с автоматическим merge при онлайн
    func fetch<T: Codable>(
        type: OfflineDataType
    ) async -> Result<[T], Error> {
        let result: Result<[T], Error> = await fetchFromCoreData(type: type)

        if OfflineManager.shared.isOnline {
            Task {
                await performFullSync()
            }
        }
        return result
    }

    /// Специализированный метод для чата (используется FamilyChatOfflineManager)
    func saveChatMessage(_ message: FamilyChatMessageResponse, isPending: Bool = false) async -> Result<Void, Error> {
        let type: OfflineDataType = isPending ? .familyChatMessage : .familyChatMessage
        return await save(message, type: type, priority: isPending ? .critical : .normal)
    }

    /// Специализированный fetch для чата
    func fetchChatMessages() async -> Result<[FamilyChatMessageResponse], Error> {
        await fetchFromCoreData(type: .familyChatMessage)
    }

    /// Полная синхронизация всех pending данных
    func syncAll() async {
        await performFullSync()
    }
    
    /// Удаление записей определённого типа в unified-хранилище
    func delete(type: OfflineDataType) async -> Result<Void, Error> {
        let context = viewContext
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "dataType == %@", type.rawValue)
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
        
        do {
            try context.execute(deleteRequest)
            try context.save()
            updatePendingCount()
            return .success(())
        } catch {
            return .failure(error)
        }
    }
    
    /// Очистка unified-хранилища полностью
    func clearAll() async -> Result<Void, Error> {
        let context = viewContext
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "UnifiedOfflineRecord")
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
        do {
            try context.execute(deleteRequest)
            try context.save()
            updatePendingCount()
            return .success(())
        } catch {
            return .failure(error)
        }
    }
    
    /// Обнаружение конфликтов на основе client/server version
    func detectConflicts() async -> [SyncConflict] {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "isSynced == false")
        
        guard let pending = try? viewContext.fetch(request) else {
            return []
        }
        
        return pending.compactMap { record in
            guard let id = record.id,
                  let rawType = record.dataType,
                  let dataType = OfflineDataType(rawValue: rawType)
            else { return nil }
            
            let clientVersion = record.clientVersion ?? record.createdAt ?? Date.distantPast
            let serverVersion = record.serverVersion ?? Date.distantPast
            
            guard serverVersion > clientVersion else { return nil }
            
            return SyncConflict(
                recordId: id,
                dataType: dataType,
                clientVersion: clientVersion,
                serverVersion: serverVersion,
                resolutionStrategy: preferredConflictStrategy(for: dataType)
            )
        }
    }
    
    /// Статистика unified-хранилища
    func statistics() -> OfflineStorageStatistics {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        do {
            let records = try viewContext.fetch(request)
            let synced = records.filter(\.isSynced).count
            let unsynced = records.count - synced
            return OfflineStorageStatistics(
                totalRecords: records.count,
                syncedRecords: synced,
                unsyncedRecords: unsynced,
                syncPercentage: records.isEmpty ? 0 : Double(synced) / Double(records.count)
            )
        } catch {
            return OfflineStorageStatistics(totalRecords: 0, syncedRecords: 0, unsyncedRecords: 0, syncPercentage: 0)
        }
    }

    /// Разрешение конфликтов (реализовано здесь как центральное место)
    func resolveConflicts(strategy: ConflictResolutionStrategy = .serverWins) async {
        print("🔄 UnifiedOfflineStore: Resolving conflicts with strategy: \(strategy)")
        let context = viewContext
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "isSynced == false")

        do {
            let records = try context.fetch(request)
            var resolvedCount = 0
            for record in records {
                let localDate = record.clientVersion ?? record.createdAt ?? .distantPast
                let remoteDate = record.serverVersion ?? .distantPast
                let hasVersionConflict = remoteDate > localDate
                let strategyToApply = (strategy == .manual)
                    ? preferredConflictStrategy(for: OfflineDataType(rawValue: record.dataType ?? "") ?? .settings)
                    : strategy
                
                switch strategyToApply {
                case .serverWins:
                    if hasVersionConflict {
                        record.clientVersion = remoteDate
                    }
                    record.isSynced = true
                    record.isModified = false
                    record.syncedAt = Date()
                    resolvedCount += 1
                    
                case .clientWins:
                    // Оставляем локальную версию источником истины.
                    record.clientVersion = Date()
                    record.isSynced = false
                    record.isModified = true
                    
                case .merge:
                    if let mergedPayload = mergedPayloadWithLatestSynced(for: record) {
                        record.data = mergedPayload
                    }
                    record.isSynced = true
                    record.isModified = false
                    record.syncedAt = Date()
                    resolvedCount += 1
                    
                case .manual:
                    // Ничего не делаем: запись остаётся pending для ручного разбора.
                    continue
                }
            }
            try context.save()
            updatePendingCount()
            print("✅ UnifiedOfflineStore: Resolved \(resolvedCount) conflicts, pending manual: \(records.count - resolvedCount)")
        } catch {
            print("❌ UnifiedOfflineStore: Conflict resolution failed: \(error)")
        }
    }
    
    // MARK: - Private Core Data Operations
    
    private func saveToCoreData<T: Codable>(
        object: T,
        type: OfflineDataType,
        priority: DataPriority
    ) async -> Result<Void, Error> {
        let context = backgroundContext
        
        return await withCheckedContinuation { continuation in
            context.perform {
                if type == .aiInteraction {
                    // Храним только последний checkpoint стрима, чтобы не раздувать оффлайн-таблицу.
                    let cleanupRequest = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
                    cleanupRequest.predicate = NSPredicate(format: "dataType == %@ AND isSynced == false", type.rawValue)
                    if let oldRows = try? context.fetch(cleanupRequest) {
                        oldRows.forEach { context.delete($0) }
                    }
                }
                
                let record = UnifiedOfflineRecord(context: context)
                record.id = UUID()
                record.dataType = type.rawValue
                record.createdAt = Date()
                record.isSynced = false
                record.priority = Int16(priority.rawValue)
                record.isModified = true
                record.clientVersion = Date()
                
                do {
                    record.data = try JSONEncoder().encode(object)
                    try context.save()
                    
                    // Propagate to view context
                    self.viewContext.performAndWait {
                        try? self.viewContext.save()
                        if type == .aiInteraction {
                            self.collapseAIInteractionCheckpoints(in: self.viewContext)
                        }
                    }
                    
                    self.updatePendingCount()
                    continuation.resume(returning: .success(()))
                } catch {
                    continuation.resume(returning: .failure(error))
                }
            }
        }
    }
    
    private func fetchFromCoreData<T: Codable>(type: OfflineDataType) async -> Result<[T], Error> {
        let context = viewContext
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "dataType == %@", type.rawValue)
        request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]
        
        do {
            let records = try context.fetch(request)
            var result: [T] = []
            
            for record in records {
                if let data = record.data,
                   let decoded = try? JSONDecoder().decode(T.self, from: data) {
                    result.append(decoded)
                }
            }
            return .success(result)
        } catch {
            return .failure(error)
        }
    }
    
    private func performFullSync() async {
        guard storeSyncPhase != .syncing else { return }
        guard OfflineManager.shared.isOnline else { return }
        do {
            _ = try resolvedUserId()
        } catch {
            storeSyncPhase = .error
            print("❌ UnifiedOfflineStore: Sync aborted — \(error.localizedDescription)")
            return
        }
        
        storeSyncPhase = .syncing
        SyncEngine.shared.publish(domain: .offline, operation: "full_sync_start", state: .syncing)
        
        let pushResult = await pushPendingRecords()
        
        do {
            let remote = try await pullRemoteChanges()
            mergeRemoteData(remote.data)
            collapseAIInteractionCheckpoints(in: viewContext)
            saveLastSyncTimestamp(remote.lastSyncTimestamp)
        } catch {
            print("⚠️ UnifiedOfflineStore: Remote pull failed: \(error.localizedDescription)")
            // Push часть уже выполнена; не прерываем весь процесс.
        }
        
        if pushResult.failedCount > 0 {
            storeSyncPhase = .error
            SyncEngine.shared.publish(
                domain: .offline,
                operation: "full_sync_finished",
                state: .error("push_failed"),
                metadata: ["pushed": "\(pushResult.pushedCount)", "failed": "\(pushResult.failedCount)"]
            )
        } else {
            storeSyncPhase = .idle
            lastSyncDate = Date()
            SyncEngine.shared.publish(
                domain: .offline,
                operation: "full_sync_finished",
                state: .synced,
                metadata: ["pushed": "\(pushResult.pushedCount)", "failed": "0"]
            )
        }
        
        updatePendingCount()
        print("✅ UnifiedOfflineStore: Full sync completed (failed: \(pushResult.failedCount), pushed: \(pushResult.pushedCount))")
    }

    private func pushPendingRecords() async -> (pushedCount: Int, failedCount: Int) {
        let unsyncedRecords = fetchUnsyncedRecordsSorted()
        var pushedCount = 0
        var failedCount = 0

        for record in unsyncedRecords where record.isModified {
            var pushed = false
            var attempt = 0
            let maxAttempts = 3

            while !pushed && attempt < maxAttempts {
                attempt += 1
                do {
                    try await pushRecordToServer(record)
                    markRecordAsSynced(objectID: record.objectID)
                    pushed = true
                    pushedCount += 1
                    SyncEngine.shared.publish(
                        domain: syncDomain(forRawType: record.dataType),
                        operation: "push_record",
                        state: .synced,
                        recordId: record.id?.uuidString,
                        metadata: ["attempt": "\(attempt)"]
                    )
                } catch {
                    if attempt >= maxAttempts {
                        failedCount += 1
                        SyncEngine.shared.publish(
                            domain: syncDomain(forRawType: record.dataType),
                            operation: "push_record",
                            state: .error(error.localizedDescription),
                            recordId: record.id?.uuidString,
                            metadata: ["attempt": "\(attempt)"]
                        )
                        print("⚠️ UnifiedOfflineStore: Failed to sync record \(record.objectID) after \(attempt) attempts: \(error.localizedDescription)")
                    } else {
                        let delayNs = UInt64(pow(2.0, Double(attempt - 1)) * 250_000_000.0) // 250ms, 500ms
                        try? await Task.sleep(nanoseconds: delayNs)
                    }
                }
            }
        }

        return (pushedCount, failedCount)
    }
    
    private func setupAutomaticSync() {
        OfflineManager.shared.$isOnline
            .sink { [weak self] isOnline in
                if isOnline && self?.storeSyncPhase != .syncing {
                    Task {
                        await self?.performFullSync()
                    }
                }
            }
            .store(in: &cancellables)
    }
    
    private func updatePendingCount() {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "isSynced == false")
        
        viewContext.perform {
            do {
                let count = try self.viewContext.count(for: request)
                DispatchQueue.main.async {
                    self.pendingCount = count
                }
            } catch {}
        }
    }
    
    private func loadPendingCount() {
        updatePendingCount()
    }
    
    private func fetchUnsyncedRecordsSorted() -> [UnifiedOfflineRecord] {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "isSynced == false")
        request.sortDescriptors = [
            NSSortDescriptor(key: "priority", ascending: true),
            NSSortDescriptor(key: "createdAt", ascending: true)
        ]
        do {
            return try viewContext.fetch(request)
        } catch {
            print("❌ UnifiedOfflineStore: Failed to fetch unsynced records: \(error.localizedDescription)")
            return []
        }
    }
    
    private func pushRecordToServer(_ record: UnifiedOfflineRecord) async throws {
        let userId = try resolvedUserId()
        let deviceId = resolvedDeviceId()
        guard let dataType = record.dataType, !dataType.isEmpty else {
            throw NSError(domain: "UnifiedOfflineStore", code: 1001, userInfo: [NSLocalizedDescriptionKey: "Missing dataType"])
        }
        guard let payloadData = record.data else {
            throw NSError(domain: "UnifiedOfflineStore", code: 1002, userInfo: [NSLocalizedDescriptionKey: "Missing payload data"])
        }
        
        let payload = try payloadDictionary(from: payloadData)
        let version: Int
        if let clientVersion = record.clientVersion ?? record.createdAt {
            version = max(1, Int(clientVersion.timeIntervalSince1970))
        } else {
            version = max(1, Int(Date().timeIntervalSince1970))
        }
        
        let _: OfflineDataResponse = try await withCheckedThrowingContinuation { continuation in
            self.apiService.updateOfflineData(
                userId: userId,
                dataId: record.id?.uuidString,
                dataType: dataType,
                data: payload,
                deviceId: deviceId,
                version: version
            ) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    private func pullRemoteChanges() async throws -> SyncOfflineStorageResponse {
        let userId = try resolvedUserId()
        let deviceId = resolvedDeviceId()
        let timestamp = userDefaults.string(forKey: lastSyncTimestampKey)
        
        return try await withCheckedThrowingContinuation { continuation in
            self.apiService.syncOfflineStorage(
                userId: userId,
                deviceId: deviceId,
                lastSyncTimestamp: timestamp,
                dataTypes: nil
            ) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    private func mergeRemoteData(_ remoteData: [OfflineDataResponse]) {
        guard !remoteData.isEmpty else { return }
        
        viewContext.performAndWait {
            do {
                for item in remoteData {
                    let incomingId = UUID(uuidString: item.dataId)
                    let record: UnifiedOfflineRecord
                    if let incomingId,
                       let existing = fetchRecord(id: incomingId, dataType: item.dataType, in: viewContext) {
                        record = existing
                    } else {
                        record = UnifiedOfflineRecord(context: viewContext)
                        record.id = incomingId ?? UUID()
                    }
                    record.dataType = item.dataType
                    record.createdAt = isoDate(item.lastModified) ?? Date()
                    record.data = encodeAnyCodableDictionary(item.data)
                    record.isSynced = true
                    record.isModified = false
                    record.syncedAt = Date()
                    record.serverVersion = isoDate(item.lastModified) ?? Date()
                    record.priority = Int16(DataPriority.normal.rawValue)
                }
                collapseAIInteractionCheckpoints(in: viewContext)
                try viewContext.save()
            } catch {
                print("❌ UnifiedOfflineStore: Failed to merge remote data: \(error.localizedDescription)")
            }
        }
    }
    
    private func markRecordAsSynced(objectID: NSManagedObjectID) {
        viewContext.performAndWait {
            guard let record = try? viewContext.existingObject(with: objectID) as? UnifiedOfflineRecord else { return }
            record.isSynced = true
            record.isModified = false
            record.syncedAt = Date()
            record.serverVersion = Date()
            do {
                try viewContext.save()
            } catch {
                print("❌ UnifiedOfflineStore: Failed to mark record synced: \(error.localizedDescription)")
            }
        }
    }
    
    private func payloadDictionary(from payloadData: Data) throws -> [String: AnyCodable] {
        let json = try JSONSerialization.jsonObject(with: payloadData, options: [])
        guard let dictionary = json as? [String: Any] else {
            throw NSError(domain: "UnifiedOfflineStore", code: 1003, userInfo: [NSLocalizedDescriptionKey: "Offline payload is not JSON object"])
        }
        return dictionary.mapValues { AnyCodable($0) }
    }
    
    private func encodeAnyCodableDictionary(_ payload: [String: AnyCodable]) -> Data? {
        let raw = payload.mapValues { $0.value }
        return try? JSONSerialization.data(withJSONObject: raw, options: [])
    }
    
    private func isoDate(_ value: String?) -> Date? {
        guard let value, !value.isEmpty else { return nil }
        let formatter = ISO8601DateFormatter()
        return formatter.date(from: value)
    }
    
    private func saveLastSyncTimestamp(_ value: String) {
        userDefaults.set(value, forKey: lastSyncTimestampKey)
    }
    
    private func fetchRecord(
        id: UUID,
        dataType: String,
        in context: NSManagedObjectContext
    ) -> UnifiedOfflineRecord? {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.fetchLimit = 1
        request.predicate = NSPredicate(format: "id == %@ AND dataType == %@", id as CVarArg, dataType)
        return try? context.fetch(request).first
    }
    
    private func mergedPayloadWithLatestSynced(for local: UnifiedOfflineRecord) -> Data? {
        guard let localId = local.id, let dataType = local.dataType else {
            return local.data
        }
        guard let remote = fetchRecord(id: localId, dataType: dataType, in: viewContext),
              remote.isSynced,
              let remoteData = remote.data,
              let localData = local.data else {
            return local.data
        }
        
        guard
            let remoteJSON = try? JSONSerialization.jsonObject(with: remoteData) as? [String: Any],
            let localJSON = try? JSONSerialization.jsonObject(with: localData) as? [String: Any]
        else {
            return local.data
        }
        
        var merged = remoteJSON
        localJSON.forEach { merged[$0.key] = $0.value } // локальные изменения приоритетны
        return try? JSONSerialization.data(withJSONObject: merged, options: [])
    }

    /// Для AI-stream checkpoint храним только наиболее свежую запись (unsynced приоритетнее synced).
    private func collapseAIInteractionCheckpoints(in context: NSManagedObjectContext) {
        let request = NSFetchRequest<UnifiedOfflineRecord>(entityName: "UnifiedOfflineRecord")
        request.predicate = NSPredicate(format: "dataType == %@", OfflineDataType.aiInteraction.rawValue)
        request.sortDescriptors = [
            NSSortDescriptor(key: "isSynced", ascending: true), // false (pending) раньше true
            NSSortDescriptor(key: "clientVersion", ascending: false),
            NSSortDescriptor(key: "createdAt", ascending: false)
        ]

        guard let rows = try? context.fetch(request), rows.count > 1 else { return }
        // Первый элемент в текущей сортировке — канонический checkpoint.
        for duplicate in rows.dropFirst() {
            context.delete(duplicate)
        }
    }

    private func preferredConflictStrategy(for type: OfflineDataType) -> ConflictResolutionStrategy {
        switch type {
        case .aiInteraction, .familyChatMessage:
            // Для временных/потоковых данных важнее не затирать локальный прогресс.
            return .clientWins
        case .settings, .userSettings, .networkProtectionStatus:
            // Настройки и policy на устройстве должны совпадать с сервером.
            return .serverWins
        default:
            return .merge
        }
    }

    private func syncDomain(for type: OfflineDataType) -> SyncDomain {
        switch type {
        case .familyChatMessage:
            return .familyChat
        case .aiInteraction:
            return .aiStreaming
        default:
            return .offline
        }
    }

    private func syncDomain(forRawType rawType: String?) -> SyncDomain {
        guard let rawType, let type = OfflineDataType(rawValue: rawType) else { return .offline }
        return syncDomain(for: type)
    }
    
    private func resolvedUserId() throws -> String {
        if let userId = userDefaults.string(forKey: "user_id")?.trimmingCharacters(in: .whitespacesAndNewlines),
           !userId.isEmpty {
            return userId
        }
        throw NSError(
            domain: "UnifiedOfflineStore",
            code: 1004,
            userInfo: [NSLocalizedDescriptionKey: "Missing user_id for offline sync identity"]
        )
    }
    
    private func resolvedDeviceId() -> String {
        if let stored = userDefaults.string(forKey: offlineDeviceIdKey), !stored.isEmpty {
            return stored
        }
        let newId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        userDefaults.set(newId, forKey: offlineDeviceIdKey)
        return newId
    }
}

// MARK: - Supporting Types (только для UnifiedOfflineStore)

enum UnifiedStoreSyncPhase: String {
    case idle
    case syncing
    case error
}
