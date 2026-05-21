import Foundation
import Network
import Combine
import SwiftUI

/**
 * Менеджер офлайн режима для ALADDIN
 * Обеспечивает работу приложения без интернета
 */
class OfflineManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = OfflineManager()
    
    // MARK: - Published Properties
    
    /// Статус подключения к интернету
    @Published var isOnline: Bool = true
    
    /// Включен ли офлайн режим
    @Published var isOfflineModeEnabled: Bool = true
    
    /// Очередь: in-memory generic-операции + pending в `UnifiedOfflineStore` (Core Data)
    @Published var pendingOperationsCount: Int = 0
    
    // MARK: - New Unified Layer (Phase 2026)
    /// Единый store — без хранения `shared`, чтобы не было цикла инициализации с `UnifiedOfflineStore`.
    var unifiedStore: UnifiedOfflineStore { UnifiedOfflineStore.shared }
    
    // MARK: - Dependencies
    
    private let networkMonitor: NWPathMonitor
    private let queue = DispatchQueue(label: "OfflineManager")
    private let storageManager: StorageManager
    private let cacheManager: CacheManager
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - State (generic closures остаются только в памяти; персистентные данные — в UnifiedOfflineStore)
    /// Очередь операций для выполнения при восстановлении соединения
    private var pendingOperations: [OfflineOperation] = []
    
    /// Максимальное количество операций в очереди
    private let maxPendingOperations = 100
    /// Legacy in-memory enqueue from `execute(...)` is disabled.
    /// Runtime source of truth for persistent offline sync is `UnifiedOfflineStore`.
    private let allowAutomaticLegacyEnqueue = false
    
    // MARK: - Initialization
    
    private init(
        storageManager: StorageManager = StorageManager.shared,
        cacheManager: CacheManager = CacheManager.shared
    ) {
        self.storageManager = storageManager
        self.cacheManager = cacheManager
        
        self.networkMonitor = NWPathMonitor()
        setupNetworkMonitoring()
        loadPendingOperations()
        observeUnifiedPendingCount()
        refreshMergedPendingCount()
    }
    
    deinit {
        networkMonitor.cancel()
    }
    
    private func observeUnifiedPendingCount() {
        UnifiedOfflineStore.shared.$pendingCount
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in
                self?.refreshMergedPendingCount()
            }
            .store(in: &cancellables)
    }
    
    private func refreshMergedPendingCount() {
        DispatchQueue.main.async {
            self.pendingOperationsCount = self.pendingOperations.count + UnifiedOfflineStore.shared.pendingCount
        }
    }
    
    // MARK: - Public Methods
    
    func execute<T>(
        operation: @escaping () async throws -> T,
        requiresOnline: Bool = true,
        priority: DataPriority = .normal
    ) async -> Result<T, NetworkError> {
        
        if !requiresOnline {
            do {
                let result = try await operation()
                return .success(result)
            } catch let error as NetworkError {
                return .failure(error)
            } catch {
                return .failure(.unknown(error))
            }
        }
        
        if isOnline {
            do {
                let result = try await operation()
                return .success(result)
            } catch let error as NetworkError {
                if error.isRetryable && allowAutomaticLegacyEnqueue {
                    addToPendingQueue(operation: operation, error: error, priority: priority)
                }
                return .failure(error)
            } catch {
                let networkError = NetworkError.unknown(error)
                if networkError.isRetryable && allowAutomaticLegacyEnqueue {
                    addToPendingQueue(operation: operation, error: networkError, priority: priority)
                }
                return .failure(networkError)
            }
        } else {
            if allowAutomaticLegacyEnqueue {
                addToPendingQueue(operation: operation, error: .noConnection, priority: priority)
            }
            return .failure(.noConnection)
        }
    }
    
    func addToPendingQueue<T>(
        operation: @escaping () async throws -> T,
        error: NetworkError,
        priority: DataPriority = .normal
    ) {
        let offlineOperation = OfflineOperation(
            id: UUID(),
            operation: operation,
            error: error,
            createdAt: Date(),
            retryCount: 0,
            priority: priority
        )
        
        pendingOperations.append(offlineOperation)
        
        if pendingOperations.count > maxPendingOperations {
            pendingOperations.removeFirst()
        }
        
        refreshMergedPendingCount()
        savePendingOperations()
        SyncEngine.shared.publish(
            domain: .offline,
            operation: "legacy_in_memory_enqueue",
            state: .pending,
            metadata: [
                "reason": error.localizedDescription,
                "priority": "\(priority.rawValue)"
            ]
        )
        
        print("📴 OfflineManager: Операция добавлена в очередь (всего in-memory: \(pendingOperations.count))")
    }
    
    /// Выполняет синхронизацию с приоритетами
    func syncWithPriorities() async {
        print("🔄 OfflineManager: Синхронизация с приоритетами...")
        await syncData(priority: .critical)
        await syncData(priority: .important)
        await syncData(priority: .normal)
        print("✅ OfflineManager: Синхронизация с приоритетами завершена")
    }
    
    private func syncData(priority: DataPriority) async {
        let priorityOperations = pendingOperations.filter { $0.priority == priority }
        print("   📤 Синхронизация данных приоритета: \(priority) (\(priorityOperations.count) операций)")
        for operation in priorityOperations {
            await processOperation(operation)
        }
    }
    
    func processPendingOperations() async {
        guard isOnline else { return }
        
        await UnifiedOfflineStore.shared.syncAll()
        
        let operationsToProcess = pendingOperations
        pendingOperations.removeAll()
        
        print("📴 OfflineManager: Обрабатываем \(operationsToProcess.count) in-memory операций из очереди")
        
        for operation in operationsToProcess {
            await processOperation(operation)
        }
        
        savePendingOperations()
        refreshMergedPendingCount()
    }
    
    func clearPendingOperations() {
        pendingOperations.removeAll()
        savePendingOperations()
        refreshMergedPendingCount()
        print("📴 OfflineManager: Очередь in-memory операций очищена")
    }
    
    func getOfflineStatistics() -> OfflineStatistics {
        OfflineStatistics(
            isOnline: isOnline,
            pendingOperationsCount: pendingOperations.count + UnifiedOfflineStore.shared.pendingCount,
            isOfflineModeEnabled: isOfflineModeEnabled,
            oldestPendingOperation: pendingOperations.min { $0.createdAt < $1.createdAt }?.createdAt,
            newestPendingOperation: pendingOperations.max { $0.createdAt < $1.createdAt }?.createdAt
        )
    }
    
    // MARK: - Private Methods
    
    private func setupNetworkMonitoring() {
        networkMonitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                let wasOnline = self?.isOnline ?? false
                self?.isOnline = path.status == .satisfied
                
                if !wasOnline && self?.isOnline == true {
                    Task { [weak self] in
                        await self?.processPendingOperations()
                    }
                }
                
                print("📴 OfflineManager: Статус сети: \(self?.isOnline == true ? "Онлайн" : "Офлайн")")
            }
        }
        
        networkMonitor.start(queue: queue)
    }
    
    private func processOperation(_ operation: OfflineOperation) async {
        do {
            _ = try await operation.operation()
            print("✅ OfflineManager: Операция \(operation.id) выполнена успешно")
            refreshMergedPendingCount()
        } catch {
            operation.retryCount += 1
            
            if operation.retryCount < 3 {
                pendingOperations.append(operation)
                print("⚠️ OfflineManager: Операция \(operation.id) не выполнена, попытка \(operation.retryCount)/3")
            } else {
                print("❌ OfflineManager: Операция \(operation.id) удалена после 3 неудачных попыток")
            }
            refreshMergedPendingCount()
        }
    }
    
    private func loadPendingOperations() {
        pendingOperations = []
    }
    
    private func savePendingOperations() {
        print("📴 OfflineManager: Сохранено \(pendingOperations.count) in-memory операций (generic closures не сериализуются)")
    }
}

// MARK: - OfflineOperation

private class OfflineOperation {
    let id: UUID
    let operation: () async throws -> Any
    let error: NetworkError
    let createdAt: Date
    let priority: DataPriority
    var retryCount: Int
    
    init<T>(
        id: UUID,
        operation: @escaping () async throws -> T,
        error: NetworkError,
        createdAt: Date,
        retryCount: Int,
        priority: DataPriority
    ) {
        self.id = id
        self.operation = operation
        self.error = error
        self.createdAt = createdAt
        self.retryCount = retryCount
        self.priority = priority
    }
}

// MARK: - OfflineStatistics

struct OfflineStatistics {
    let isOnline: Bool
    let pendingOperationsCount: Int
    let isOfflineModeEnabled: Bool
    let oldestPendingOperation: Date?
    let newestPendingOperation: Date?
    
    var hasPendingOperations: Bool {
        pendingOperationsCount > 0
    }
    
    var oldestOperationAge: TimeInterval? {
        guard let oldest = oldestPendingOperation else { return nil }
        return Date().timeIntervalSince(oldest)
    }
    
    var description: String {
        """
        Offline Statistics:
        - Статус: \(isOnline ? "Онлайн" : "Офлайн")
        - Офлайн режим: \(isOfflineModeEnabled ? "Включен" : "Выключен")
        - Операций в очереди (оценка): \(pendingOperationsCount)
        - Самая старая операция: \(oldestOperationAge != nil ? "\(String(format: "%.1f", oldestOperationAge!))с назад" : "Нет")
        """
    }
}

// MARK: - P7 Thin Reactive Layer (SyncEngine v1)

enum SyncDomain: String, CaseIterable, Hashable {
    case offline
    case familyChat
    case aiStreaming
    case family
    case settings
    case networkProtection
}

enum SyncState: Equatable {
    case idle
    case local
    case pending
    case syncing
    case synced
    case conflict
    case error(String)
}

extension SyncState {
    func localizedTitle(using localizationManager: LocalizationManager) -> String {
        let isRussian = localizationManager.currentLanguage == .russian
        switch self {
        case .idle:
            return isRussian ? "Ожидание" : "Idle"
        case .local:
            return isRussian ? "Локально" : "Local"
        case .pending:
            return isRussian ? "В очереди" : "Pending"
        case .syncing:
            return isRussian ? "Синхронизация" : "Syncing"
        case .synced:
            return isRussian ? "Синхронизировано" : "Synced"
        case .conflict:
            return isRussian ? "Конфликт" : "Conflict"
        case .error:
            return isRussian ? "Ошибка" : "Error"
        }
    }

    var statusColor: Color {
        switch self {
        case .idle, .local:
            return .gray
        case .pending:
            return .orange
        case .syncing:
            return .blue
        case .synced:
            return .green
        case .conflict, .error:
            return .red
        }
    }
}

struct SyncEvent: Identifiable {
    let id = UUID()
    let timestamp: Date
    let domain: SyncDomain
    let operation: String
    let state: SyncState
    let recordId: String?
    let metadata: [String: String]
}

/// Единая reactive-шина синхронизации (P7 v1): агрегирует состояния realtime/offline потоков.
final class SyncEngine: ObservableObject {
    static let shared = SyncEngine()

    @Published private(set) var latestStateByDomain: [SyncDomain: SyncState] = {
        var initial: [SyncDomain: SyncState] = [:]
        SyncDomain.allCases.forEach { initial[$0] = .idle }
        return initial
    }()
    @Published private(set) var lastEvent: SyncEvent?

    let events = PassthroughSubject<SyncEvent, Never>()
    private var pendingPublishWorkItem: DispatchWorkItem?
    private let publishCoalesceInterval: TimeInterval = 0.08

    private init() {}

    func publish(
        domain: SyncDomain,
        operation: String,
        state: SyncState,
        recordId: String? = nil,
        metadata: [String: String] = [:]
    ) {
        let event = SyncEvent(
            timestamp: Date(),
            domain: domain,
            operation: operation,
            state: state,
            recordId: recordId,
            metadata: metadata
        )
        DispatchQueue.main.async { [weak self] in
            guard let self else { return }
            let work = DispatchWorkItem { [weak self] in
                guard let self else { return }
                self.pendingPublishWorkItem = nil
                self.latestStateByDomain[domain] = state
                self.lastEvent = event
                self.events.send(event)
            }
            self.pendingPublishWorkItem?.cancel()
            self.pendingPublishWorkItem = work
            DispatchQueue.main.asyncAfter(deadline: .now() + self.publishCoalesceInterval, execute: work)
        }
    }
}

// MARK: - OfflineManager Extensions

extension OfflineManager {
    
    static func critical() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = true
        return manager
    }
    
    static func standard() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = true
        return manager
    }
    
    static func onlineOnly() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = false
        return manager
    }
}
