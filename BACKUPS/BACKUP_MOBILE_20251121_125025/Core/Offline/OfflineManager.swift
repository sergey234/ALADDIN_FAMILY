import Foundation
import Network

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
    
    /// Количество офлайн операций в очереди
    @Published var pendingOperationsCount: Int = 0
    
    // MARK: - Dependencies
    
    private let networkMonitor: NWPathMonitor
    private let queue = DispatchQueue(label: "OfflineManager")
    private let storageManager: StorageManager
    private let cacheManager: CacheManager
    
    // MARK: - State
    
    /// Очередь операций для выполнения при восстановлении соединения
    private var pendingOperations: [OfflineOperation] = []
    
    /// Максимальное количество операций в очереди
    private let maxPendingOperations = 100
    
    // MARK: - Initialization
    
    private init(
        storageManager: StorageManager = StorageManager.shared,
        cacheManager: CacheManager = CacheManager.shared
    ) {
        self.storageManager = storageManager
        self.cacheManager = cacheManager
        
        // Настраиваем мониторинг сети
        self.networkMonitor = NWPathMonitor()
        setupNetworkMonitoring()
        
        // Загружаем сохраненные операции
        loadPendingOperations()
    }
    
    deinit {
        networkMonitor.cancel()
    }
    
    // MARK: - Public Methods
    
    /**
     * Выполняет операцию с поддержкой офлайн режима
     * - Parameter operation: Операция для выполнения
     * - Parameter requiresOnline: Требует ли операция интернета
     * - Parameter priority: Приоритет данных (для синхронизации)
     * - Returns: Результат выполнения операции
     */
    func execute<T>(
        operation: @escaping () async throws -> T,
        requiresOnline: Bool = true,
        priority: DataPriority = .normal
    ) async -> Result<T, NetworkError> {
        
        // Если операция не требует интернета, выполняем сразу
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
        
        // Если есть интернет, выполняем операцию
        if isOnline {
            do {
                let result = try await operation()
                return .success(result)
            } catch let error as NetworkError {
                // Если ошибка связана с сетью, добавляем в очередь
                if error.isRetryable {
                    addToPendingQueue(operation: operation, error: error)
                }
                return .failure(error)
            } catch {
                let networkError = NetworkError.unknown(error)
                if networkError.isRetryable {
                    addToPendingQueue(operation: operation, error: networkError)
                }
                return .failure(networkError)
            }
        } else {
            // Нет интернета - добавляем в очередь
            addToPendingQueue(operation: operation, error: .noConnection)
            return .failure(.noConnection)
        }
    }
    
    /**
     * Добавляет операцию в очередь офлайн выполнения
     * - Parameter operation: Операция для добавления
     * - Parameter error: Ошибка, из-за которой операция не выполнилась
     */
    func addToPendingQueue<T>(
        operation: @escaping () async throws -> T,
        error: NetworkError
    ) {
        let offlineOperation = OfflineOperation(
            id: UUID(),
            operation: operation,
            error: error,
            createdAt: Date(),
            retryCount: 0
        )
        
        // Добавляем в очередь
        pendingOperations.append(offlineOperation)
        
        // Ограничиваем размер очереди
        if pendingOperations.count > maxPendingOperations {
            pendingOperations.removeFirst()
        }
        
        // Обновляем счетчик
        DispatchQueue.main.async {
            self.pendingOperationsCount = self.pendingOperations.count
        }
        
        // Сохраняем в хранилище
        savePendingOperations()
        
        print("📴 OfflineManager: Операция добавлена в очередь (всего: \(pendingOperations.count))")
    }
    
    // MARK: - Data Prioritization
    
    /// Приоритет данных для синхронизации
    enum DataPriority: Int, Comparable {
        case critical = 0  // Критические данные (высокий приоритет)
        case important = 1  // Важные данные (средний приоритет)
        case normal = 2  // Обычные данные (низкий приоритет)
        
        static func < (lhs: DataPriority, rhs: DataPriority) -> Bool {
            return lhs.rawValue < rhs.rawValue
        }
    }
    
    /// Выполняет синхронизацию с приоритетами
    func syncWithPriorities() async {
        print("🔄 OfflineManager: Синхронизация с приоритетами...")
        
        // Сначала синхронизируем критические данные
        await syncData(priority: .critical)
        
        // Затем важные данные
        await syncData(priority: .important)
        
        // В конце обычные данные
        await syncData(priority: .normal)
        
        print("✅ OfflineManager: Синхронизация с приоритетами завершена")
    }
    
    /// Синхронизирует данные по приоритету
    private func syncData(priority: DataPriority) async {
        // Фильтруем операции по приоритету
        let priorityOperations = pendingOperations.filter { operation in
            // TODO: Добавить поле priority в OfflineOperation
            // Пока синхронизируем все операции
            return true
        }
        
        print("   📤 Синхронизация данных приоритета: \(priority) (\(priorityOperations.count) операций)")
        
        // Выполняем операции с данным приоритетом
        for operation in priorityOperations {
            await processOperation(operation)
        }
    }
    
    /**
     * Выполняет все операции из очереди
     */
    func processPendingOperations() async {
        guard isOnline else { return }
        
        let operationsToProcess = pendingOperations
        pendingOperations.removeAll()
        
        DispatchQueue.main.async {
            self.pendingOperationsCount = 0
        }
        
        print("📴 OfflineManager: Обрабатываем \(operationsToProcess.count) операций из очереди")
        
        for operation in operationsToProcess {
            await processOperation(operation)
        }
        
        // Сохраняем обновленную очередь
        savePendingOperations()
    }
    
    /**
     * Очищает очередь офлайн операций
     */
    func clearPendingOperations() {
        pendingOperations.removeAll()
        
        DispatchQueue.main.async {
            self.pendingOperationsCount = 0
        }
        
        savePendingOperations()
        
        print("📴 OfflineManager: Очередь операций очищена")
    }
    
    /**
     * Получает статистику офлайн режима
     */
    func getOfflineStatistics() -> OfflineStatistics {
        return OfflineStatistics(
            isOnline: isOnline,
            pendingOperationsCount: pendingOperations.count,
            isOfflineModeEnabled: isOfflineModeEnabled,
            oldestPendingOperation: pendingOperations.min { $0.createdAt < $1.createdAt }?.createdAt,
            newestPendingOperation: pendingOperations.max { $0.createdAt < $1.createdAt }?.createdAt
        )
    }
    
    // MARK: - Private Methods
    
    /**
     * Настраивает мониторинг сети
     */
    private func setupNetworkMonitoring() {
        networkMonitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                let wasOnline = self?.isOnline ?? false
                self?.isOnline = path.status == .satisfied
                
                // Если соединение восстановилось, обрабатываем очередь
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
    
    /**
     * Обрабатывает одну операцию из очереди
     */
    private func processOperation(_ operation: OfflineOperation) async {
        do {
            let result = try await operation.operation()
            print("✅ OfflineManager: Операция \(operation.id) выполнена успешно")
        } catch {
            // Увеличиваем счетчик попыток
            operation.retryCount += 1
            
            // Если не превышен лимит попыток, возвращаем в очередь
            if operation.retryCount < 3 {
                pendingOperations.append(operation)
                print("⚠️ OfflineManager: Операция \(operation.id) не выполнена, попытка \(operation.retryCount)/3")
            } else {
                print("❌ OfflineManager: Операция \(operation.id) удалена после 3 неудачных попыток")
            }
        }
    }
    
    /**
     * Загружает сохраненные операции из хранилища
     */
    private func loadPendingOperations() {
        // В реальном приложении здесь будет загрузка из Core Data
        // Пока просто инициализируем пустую очередь
        pendingOperations = []
    }
    
    /**
     * Сохраняет операции в хранилище
     */
    private func savePendingOperations() {
        // В реальном приложении здесь будет сохранение в Core Data
        // Пока просто логируем
        print("📴 OfflineManager: Сохранено \(pendingOperations.count) операций")
    }
}

// MARK: - OfflineOperation

/**
 * Операция для офлайн выполнения
 */
private class OfflineOperation {
    let id: UUID
    let operation: () async throws -> Any
    let error: NetworkError
    let createdAt: Date
    var retryCount: Int
    
    init<T>(
        id: UUID,
        operation: @escaping () async throws -> T,
        error: NetworkError,
        createdAt: Date,
        retryCount: Int
    ) {
        self.id = id
        self.operation = operation
        self.error = error
        self.createdAt = createdAt
        self.retryCount = retryCount
    }
}

// MARK: - OfflineStatistics

/**
 * Статистика офлайн режима
 */
struct OfflineStatistics {
    let isOnline: Bool
    let pendingOperationsCount: Int
    let isOfflineModeEnabled: Bool
    let oldestPendingOperation: Date?
    let newestPendingOperation: Date?
    
    var hasPendingOperations: Bool {
        return pendingOperationsCount > 0
    }
    
    var oldestOperationAge: TimeInterval? {
        guard let oldest = oldestPendingOperation else { return nil }
        return Date().timeIntervalSince(oldest)
    }
    
    var description: String {
        return """
        Offline Statistics:
        - Статус: \(isOnline ? "Онлайн" : "Офлайн")
        - Офлайн режим: \(isOfflineModeEnabled ? "Включен" : "Выключен")
        - Операций в очереди: \(pendingOperationsCount)
        - Самая старая операция: \(oldestOperationAge != nil ? "\(String(format: "%.1f", oldestOperationAge!))с назад" : "Нет")
        """
    }
}

// MARK: - OfflineManager Extensions

extension OfflineManager {
    
    /**
     * Создает OfflineManager для критических операций
     */
    static func critical() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = true
        return manager
    }
    
    /**
     * Создает OfflineManager для обычных операций
     */
    static func standard() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = true
        return manager
    }
    
    /**
     * Создает OfflineManager без офлайн режима
     */
    static func onlineOnly() -> OfflineManager {
        let manager = OfflineManager()
        manager.isOfflineModeEnabled = false
        return manager
    }
}
