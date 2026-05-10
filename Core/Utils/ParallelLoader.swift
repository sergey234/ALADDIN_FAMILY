import Foundation

/**
 * 🚀 Parallel Loader
 * Утилита для параллельной загрузки с лимитом одновременных запросов и приоритизацией
 */

/// Приоритет загрузки компонента
enum ComponentLoadPriority: Int, Comparable {
    case critical = 0    // Критичные компоненты (загружаются первыми)
    case high = 1        // Важные компоненты
    case normal = 2      // Обычные компоненты
    case low = 3         // Низкоприоритетные компоненты
    
    static func < (lhs: ComponentLoadPriority, rhs: ComponentLoadPriority) -> Bool {
        return lhs.rawValue < rhs.rawValue
    }
}

/// Элемент для загрузки с приоритетом
struct PrioritizedLoadItem<T> {
    let id: String
    let priority: ComponentLoadPriority
    let loadTask: () async throws -> T
    
    init(id: String, priority: ComponentLoadPriority = .normal, loadTask: @escaping () async throws -> T) {
        self.id = id
        self.priority = priority
        self.loadTask = loadTask
    }
}

/**
 * Параллельная загрузка с лимитом и приоритизацией
 */
class ParallelLoader {
    
    /// Максимальное количество одновременных запросов (по умолчанию 10)
    static let defaultMaxConcurrent = 10
    
    /// Выполнить загрузку с лимитом параллельных запросов и приоритизацией
    static func executeWithLimit<T>(
        items: [PrioritizedLoadItem<T>],
        maxConcurrent: Int = defaultMaxConcurrent,
        onProgress: ((String, T) -> Void)? = nil
    ) async throws -> [String: T] {
        // Сортируем по приоритету (критичные первыми)
        let sortedItems = items.sorted { $0.priority < $1.priority }
        
        var results: [String: T] = [:]
        var errors: [String: Error] = [:]
        
        // Создаем семафор для ограничения параллельных запросов
        let semaphore = AsyncSemaphore(count: maxConcurrent)
        
        // Используем TaskGroup для параллельной загрузки
        try await withThrowingTaskGroup(of: (String, Result<T, Error>).self) { group in
            for item in sortedItems {
                // Ждем доступного слота перед добавлением задачи
                await semaphore.wait()
                
                group.addTask {
                    defer {
                        // Освобождаем слот после завершения
                        Task {
                            await semaphore.signal()
                        }
                    }
                    
                    do {
                        let result = try await item.loadTask()
                        return (item.id, .success(result))
                    } catch {
                        return (item.id, .failure(error))
                    }
                }
            }
            
            // Собираем результаты
            for try await (id, result) in group {
                switch result {
                case .success(let value):
                    results[id] = value
                    // onProgress часто обновляет @Published / ObservableObject — только с MainActor
                    if let onProgress {
                        await MainActor.run {
                            onProgress(id, value)
                        }
                    }
                case .failure(let error):
                    errors[id] = error
                    print("⚠️ ParallelLoader: Ошибка загрузки \(id): \(error.localizedDescription)")
                }
            }
        }
        
        // Если есть ошибки, но есть и успешные результаты, не пробрасываем ошибку
        // Просто логируем ошибки
        if !errors.isEmpty && !results.isEmpty {
            print("⚠️ ParallelLoader: Загружено \(results.count)/\(items.count) элементов. Ошибок: \(errors.count)")
        }
        
        // Если все запросы завершились ошибкой, пробрасываем первую ошибку
        if results.isEmpty && !errors.isEmpty {
            throw errors.values.first ?? NSError(domain: "ParallelLoader", code: -1)
        }
        
        return results
    }
}

/// Асинхронный семафор для ограничения параллельных операций
actor AsyncSemaphore {
    private var count: Int
    private var waiters: [CheckedContinuation<Void, Never>] = []
    
    init(count: Int) {
        self.count = count
    }
    
    func wait() async {
        if count > 0 {
            count -= 1
        } else {
            await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
                waiters.append(continuation)
            }
        }
    }
    
    func signal() async {
        if let waiter = waiters.first {
            waiters.removeFirst()
            waiter.resume()
        } else {
            count += 1
        }
    }
}

