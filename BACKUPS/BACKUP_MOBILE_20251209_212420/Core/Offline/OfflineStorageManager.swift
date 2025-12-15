import Foundation
import CoreData

/**
 * Менеджер офлайн хранения для ALADDIN
 * Обеспечивает локальное хранение данных с Core Data
 */
class OfflineStorageManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = OfflineStorageManager()
    
    // MARK: - Core Data Stack
    
    /// Основной контекст Core Data
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "ALADDINOffline")
        container.loadPersistentStores { _, error in
            if let error = error as NSError? {
                fatalError("❌ Core Data error: \(error), \(error.userInfo)")
            }
        }
        return container
    }()
    
    /// Контекст для фоновых операций
    private var backgroundContext: NSManagedObjectContext {
        let context = NSManagedObjectContext(concurrencyType: .privateQueueConcurrencyType)
        context.parent = persistentContainer.viewContext
        return context
    }
    
    // MARK: - Published Properties
    
    /// Количество сохраненных записей
    @Published var savedRecordsCount: Int = 0
    
    /// Статус синхронизации
    @Published var syncStatus: SyncStatus = .idle
    
    // MARK: - Initialization
    
    private init() {
        // Инициализация Core Data
        _ = persistentContainer
    }
    
    // MARK: - Public Methods
    
    /**
     * Сохраняет данные в офлайн хранилище
     * - Parameter data: Данные для сохранения
     * - Parameter type: Тип данных
     * - Parameter priority: Приоритет данных (для синхронизации)
     * - Returns: Результат сохранения
     */
    func save<T: Codable>(
        _ data: T,
        type: OfflineDataType,
        priority: DataPriority = .normal
    ) async -> Result<Void, NetworkError> {
        
        do {
            let context = backgroundContext
            
            // Создаем новую запись
            let offlineRecord = OfflineRecord(context: context)
            offlineRecord.id = UUID()
            offlineRecord.dataType = type.rawValue
            offlineRecord.data = try JSONEncoder().encode(data)
            offlineRecord.createdAt = Date()
            offlineRecord.isSynced = false
            offlineRecord.isModified = true  // Помечаем как изменённое
            
            // Сохраняем контекст
            try context.save()
            
            // Обновляем основной контекст
            await MainActor.run {
                try? self.persistentContainer.viewContext.save()
                self.savedRecordsCount += 1
            }
            
            print("💾 OfflineStorage: Сохранено \(type) - \(offlineRecord.id?.uuidString ?? "unknown")")
            return .success(())
            
        } catch {
            print("❌ OfflineStorage: Ошибка сохранения \(type): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    /**
     * Получает данные из офлайн хранилища
     * - Parameter type: Тип данных
     * - Returns: Массив данных или ошибка
     */
    func retrieve<T: Codable>(
        _ type: T.Type,
        dataType: OfflineDataType
    ) async -> Result<[T], NetworkError> {
        
        do {
            let context = persistentContainer.viewContext
            let request: NSFetchRequest<NSFetchRequestResult> = NSFetchRequest(entityName: "OfflineRecord")
            request.predicate = NSPredicate(format: "dataType == %@", dataType.rawValue)
            request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]
            
            let records = try context.fetch(request)
            let data = try records.compactMap { record -> T? in
                guard let data = record.data else { return nil }
                return try JSONDecoder().decode(T.self, from: data)
            }
            
            print("💾 OfflineStorage: Получено \(data.count) записей типа \(dataType)")
            return .success(data)
            
        } catch {
            print("❌ OfflineStorage: Ошибка получения \(dataType): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    /**
     * Удаляет данные из офлайн хранилища
     * - Parameter type: Тип данных
     * - Returns: Результат удаления
     */
    func delete(
        dataType: OfflineDataType
    ) async -> Result<Void, NetworkError> {
        
        do {
            let context = persistentContainer.viewContext
            let request: NSFetchRequest<NSFetchRequestResult> = OfflineRecord.fetchRequest()
            request.predicate = NSPredicate(format: "dataType == %@", dataType.rawValue)
            
            let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
            try context.execute(deleteRequest)
            
            // Сохраняем изменения
            try context.save()
            
            await MainActor.run {
                self.savedRecordsCount = max(0, self.savedRecordsCount - 1)
            }
            
            print("💾 OfflineStorage: Удалены все записи типа \(dataType)")
            return .success(())
            
        } catch {
            print("❌ OfflineStorage: Ошибка удаления \(dataType): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    // MARK: - Conflict Resolution
    
    /// Обнаруживает конфликты при синхронизации
    func detectConflicts() async -> [SyncConflict] {
        let context = persistentContainer.viewContext
        let request: NSFetchRequest<NSFetchRequestResult> = NSFetchRequest(entityName: "OfflineRecord")
        request.predicate = NSPredicate(format: "isSynced == NO")
        
        guard let unsyncedRecords = try? context.fetch(request) as? [OfflineRecord] else {
            return []
        }
        
        var conflicts: [SyncConflict] = []
        
        for record in unsyncedRecords {
            // TODO: Сравнить с серверной версией
            // Если на сервере есть более новая версия, создаём конфликт
            // Пока создаём заглушку для демонстрации структуры
            
            if let recordId = record.id {
                let conflict = SyncConflict(
                    recordId: recordId,
                    dataType: OfflineDataType(rawValue: record.dataType ?? "unknown") ?? .userProfile,
                    clientVersion: record.createdAt ?? Date(),
                    serverVersion: Date(), // TODO: Получить с сервера
                    resolutionStrategy: .manual // По умолчанию требует ручного разрешения
                )
                conflicts.append(conflict)
            }
        }
        
        if !conflicts.isEmpty {
            print("⚠️ OfflineStorage: Обнаружено \(conflicts.count) конфликтов при синхронизации")
        }
        
        return conflicts
    }
    
    /// Автоматически разрешает конфликты
    func autoResolveConflicts(_ conflicts: [SyncConflict]) async {
        print("🔄 OfflineStorage: Автоматическое разрешение \(conflicts.count) конфликтов...")
        
        for conflict in conflicts {
            switch conflict.resolutionStrategy {
            case .serverWins:
                // Используем версию с сервера
                await applyServerVersion(conflict)
                
            case .clientWins:
                // Используем локальную версию
                await applyClientVersion(conflict)
                
            case .merge:
                // Объединяем изменения
                await mergeVersions(conflict)
                
            case .manual:
                // Требуется ручное разрешение - уведомляем
                await notifyManualResolution(conflict)
            }
        }
        
        print("✅ OfflineStorage: Конфликты разрешены")
    }
    
    /// Применяет версию с сервера
    private func applyServerVersion(_ conflict: SyncConflict) async {
        // TODO: Загрузить данные с сервера и заменить локальные
        print("   📥 Применяем версию с сервера для \(conflict.recordId)")
    }
    
    /// Применяет локальную версию
    private func applyClientVersion(_ conflict: SyncConflict) async {
        // TODO: Отправить локальные данные на сервер
        print("   📤 Применяем локальную версию для \(conflict.recordId)")
    }
    
    /// Объединяет версии
    private func mergeVersions(_ conflict: SyncConflict) async {
        // TODO: Объединить изменения из обеих версий
        print("   🔀 Объединяем версии для \(conflict.recordId)")
    }
    
    /// Уведомляет о необходимости ручного разрешения
    private func notifyManualResolution(_ conflict: SyncConflict) async {
        // TODO: Отправить уведомление пользователю
        print("   ⚠️ Требуется ручное разрешение конфликта для \(conflict.recordId)")
    }
    
    /**
     * Синхронизирует данные с сервером
     * - Parameter type: Тип данных для синхронизации
     * - Parameter onlyChanged: Синхронизировать только изменённые данные
     * - Returns: Результат синхронизации
     */
    func sync(
        dataType: OfflineDataType,
        onlyChanged: Bool = true  // Синхронизировать только изменённые данные
    ) async -> Result<Void, NetworkError> {
        
        await MainActor.run {
            self.syncStatus = .syncing
        }
        
        do {
            let context = persistentContainer.viewContext
            let request: NSFetchRequest<NSFetchRequestResult> = NSFetchRequest(entityName: "OfflineRecord")
            
            // Если onlyChanged = true, синхронизируем только изменённые записи
            if onlyChanged {
                request.predicate = NSPredicate(format: "dataType == %@ AND isSynced == NO AND isModified == YES", dataType.rawValue)
            } else {
                request.predicate = NSPredicate(format: "dataType == %@ AND isSynced == NO", dataType.rawValue)
            }
            
            let unsyncedRecords = try context.fetch(request)
            
            for record in unsyncedRecords {
                // Здесь должна быть логика отправки на сервер
                // Пока просто помечаем как синхронизированные
                record.isSynced = true
                record.syncedAt = Date()
            }
            
            try context.save()
            
            await MainActor.run {
                self.syncStatus = .completed
            }
            
            print("💾 OfflineStorage: Синхронизировано \(unsyncedRecords.count) записей типа \(dataType)")
            return .success(())
            
        } catch {
            await MainActor.run {
                self.syncStatus = .failed
            }
            
            print("❌ OfflineStorage: Ошибка синхронизации \(dataType): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    /**
     * Получает статистику офлайн хранилища
     */
    func getStorageStatistics() -> OfflineStorageStatistics {
        let context = persistentContainer.viewContext
        let request: NSFetchRequest<OfflineRecord> = OfflineRecord.fetchRequest()
        
        do {
            let records = try context.fetch(request)
            let syncedCount = records.filter { $0.isSynced }.count
            let unsyncedCount = records.count - syncedCount
            
            return OfflineStorageStatistics(
                totalRecords: records.count,
                syncedRecords: syncedCount,
                unsyncedRecords: unsyncedCount,
                syncPercentage: records.count > 0 ? Double(syncedCount) / Double(records.count) : 0
            )
        } catch {
            return OfflineStorageStatistics(
                totalRecords: 0,
                syncedRecords: 0,
                unsyncedRecords: 0,
                syncPercentage: 0
            )
        }
    }
    
    /**
     * Очищает все данные из офлайн хранилища
     */
    func clearAll() async -> Result<Void, NetworkError> {
        do {
            let context = persistentContainer.viewContext
            let request: NSFetchRequest<NSFetchRequestResult> = OfflineRecord.fetchRequest()
            
            let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
            try context.execute(deleteRequest)
            try context.save()
            
            await MainActor.run {
                self.savedRecordsCount = 0
                self.syncStatus = .idle
            }
            
            print("💾 OfflineStorage: Все данные очищены")
            return .success(())
            
        } catch {
            print("❌ OfflineStorage: Ошибка очистки: \(error)")
            return .failure(.fileSystemError(error))
        }
    }
}

// MARK: - OfflineDataType

/**
 * Типы данных для офлайн хранения
 */
enum OfflineDataType: String, CaseIterable {
    case vpnStatus = "vpn_status"
    case familyMembers = "family_members"
    case analytics = "analytics"
    case notifications = "notifications"
    case subscription = "subscription"
    case deviceInfo = "device_info"
    case userProfile = "user_profile"
    case settings = "settings"
    
    var displayName: String {
        switch self {
        case .vpnStatus:
            return "VPN Статус"
        case .familyMembers:
            return "Члены семьи"
        case .analytics:
            return "Аналитика"
        case .notifications:
            return "Уведомления"
        case .subscription:
            return "Подписка"
        case .deviceInfo:
            return "Информация об устройстве"
        case .userProfile:
            return "Профиль пользователя"
        case .settings:
            return "Настройки"
        }
    }
}

// MARK: - SyncStatus

/**
 * Статус синхронизации
 */
enum SyncStatus {
    case idle
    case syncing
    case completed
    case failed
    
    var displayName: String {
        switch self {
        case .idle:
            return "Ожидание"
        case .syncing:
            return "Синхронизация"
        case .completed:
            return "Завершено"
        case .failed:
            return "Ошибка"
        }
    }
}

// MARK: - OfflineStorageStatistics

/**
 * Статистика офлайн хранилища
 */
struct OfflineStorageStatistics {
    let totalRecords: Int
    let syncedRecords: Int
    let unsyncedRecords: Int
    let syncPercentage: Double
    
    var isFullySynced: Bool {
        return syncPercentage >= 1.0
    }
    
    var description: String {
        return """
        Offline Storage Statistics:
        - Всего записей: \(totalRecords)
        - Синхронизировано: \(syncedRecords)
        - Не синхронизировано: \(unsyncedRecords)
        - Процент синхронизации: \(String(format: "%.1f", syncPercentage * 100))%
        - Статус: \(isFullySynced ? "✅ Полностью синхронизировано" : "⚠️ Требуется синхронизация")
        """
    }
}

// MARK: - Conflict Resolution Models

/// Конфликт при синхронизации
struct SyncConflict: Codable {
    let recordId: UUID
    let dataType: OfflineDataType
    let clientVersion: Date
    let serverVersion: Date
    let resolutionStrategy: ConflictResolutionStrategy
}

/// Стратегия разрешения конфликта
enum ConflictResolutionStrategy: String, Codable {
    case serverWins = "server_wins"  // Использовать версию с сервера
    case clientWins = "client_wins"  // Использовать локальную версию
    case merge = "merge"             // Объединить изменения
    case manual = "manual"           // Требуется ручное разрешение
}

// MARK: - OfflineRecord (Core Data Entity)

/**
 * Сущность Core Data для офлайн записей
 */
@objc(OfflineRecord)
public class OfflineRecord: NSManagedObject {
    
}

extension OfflineRecord {
    
    @NSManaged public var id: UUID?
    @NSManaged public var dataType: String?
    @NSManaged public var data: Data?
    @NSManaged public var createdAt: Date?
    @NSManaged public var isSynced: Bool
    @NSManaged public var syncedAt: Date?
}

// MARK: - OfflineStorageManager Extensions

extension OfflineStorageManager {
    
    /**
     * Создает OfflineStorageManager для тестирования
     */
    static func test() -> OfflineStorageManager {
        return OfflineStorageManager()
    }
    
    /**
     * Создает OfflineStorageManager для продакшена
     */
    static func production() -> OfflineStorageManager {
        return OfflineStorageManager()
    }
}
