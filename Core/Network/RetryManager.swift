import Foundation

/**
 * Менеджер повторных попыток для сетевых запросов
 * Обеспечивает умный retry с экспоненциальной задержкой
 */
class RetryManager {
    
    // MARK: - Configuration
    
    /// Максимальное количество попыток
    let maxRetries: Int
    
    /// Базовая задержка между попытками (в секундах)
    let baseDelay: TimeInterval
    
    /// Максимальная задержка между попытками (в секундах)
    let maxDelay: TimeInterval
    
    /// Множитель для экспоненциальной задержки
    let backoffMultiplier: Double
    
    /// Случайный джиттер для избежания thundering herd
    let jitterRange: ClosedRange<Double>
    
    // MARK: - State
    
    /// Текущее количество попыток
    private var currentAttempt: Int = 0
    
    /// Время начала первой попытки
    private var startTime: Date?
    
    /// Общее время выполнения всех попыток
    private var totalTime: TimeInterval = 0
    
    // MARK: - Initialization
    
    init(
        maxRetries: Int = 3,
        baseDelay: TimeInterval = 1.0,
        maxDelay: TimeInterval = 30.0,
        backoffMultiplier: Double = 2.0,
        jitterRange: ClosedRange<Double> = 0.1...0.3
    ) {
        self.maxRetries = maxRetries
        self.baseDelay = baseDelay
        self.maxDelay = maxDelay
        self.backoffMultiplier = backoffMultiplier
        self.jitterRange = jitterRange
    }
    
    // MARK: - Public Methods
    
    /**
     * Выполняет операцию с retry механизмом
     * - Parameter operation: Асинхронная операция, которая может завершиться ошибкой
     * - Returns: Результат операции или ошибку после всех попыток
     */
    func execute<T>(
        operation: @escaping () async throws -> T
    ) async -> Result<T, NetworkError> {
        
        reset()
        startTime = Date()
        
        for attempt in 1...maxRetries {
            currentAttempt = attempt
            
            print("🔄 Retry: Попытка \(attempt)/\(maxRetries)")
            
            do {
                let result = try await operation()
                
                // Успешное выполнение
                totalTime = Date().timeIntervalSince(startTime ?? Date())
                print("✅ Retry: Успешно выполнено за \(attempt) попытку(ок) за \(String(format: "%.2f", totalTime))с")
                
                return .success(result)
                
            } catch let error as NetworkError {
                // Обрабатываем NetworkError
                if !error.isRetryable || attempt == maxRetries {
                    totalTime = Date().timeIntervalSince(startTime ?? Date())
                    print("❌ Retry: Финальная ошибка после \(attempt) попыток за \(String(format: "%.2f", totalTime))с: \(error.localizedDescription)")
                    return .failure(error)
                }
                
                // Вычисляем задержку для следующей попытки
                let delay = calculateDelay(for: attempt)
                print("⏳ Retry: Ошибка \(error.localizedDescription), повтор через \(String(format: "%.1f", delay))с")
                
                // Ждем перед следующей попыткой
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                
            } catch {
                // Обрабатываем другие ошибки
                let networkError = NetworkError.unknown(error)
                
                if !networkError.isRetryable || attempt == maxRetries {
                    totalTime = Date().timeIntervalSince(startTime ?? Date())
                    print("❌ Retry: Финальная ошибка после \(attempt) попыток за \(String(format: "%.2f", totalTime))с: \(error.localizedDescription)")
                    return .failure(networkError)
                }
                
                // Вычисляем задержку для следующей попытки
                let delay = calculateDelay(for: attempt)
                print("⏳ Retry: Ошибка \(error.localizedDescription), повтор через \(String(format: "%.1f", delay))с")
                
                // Ждем перед следующей попыткой
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            }
        }
        
        // Этот код не должен выполняться, но на всякий случай
        totalTime = Date().timeIntervalSince(startTime ?? Date())
        print("❌ Retry: Неожиданное завершение после \(maxRetries) попыток за \(String(format: "%.2f", totalTime))с")
        return .failure(.unknown(nil))
    }
    
    /**
     * Выполняет операцию с retry для конкретного типа ошибки
     * - Parameter operation: Асинхронная операция
     * - Parameter retryCondition: Условие для retry (по умолчанию - все retryable ошибки)
     * - Returns: Результат операции или ошибку
     */
    func execute<T>(
        operation: @escaping () async throws -> T,
        retryCondition: @escaping (NetworkError) -> Bool = { $0.isRetryable }
    ) async -> Result<T, NetworkError> {
        
        reset()
        startTime = Date()
        
        for attempt in 1...maxRetries {
            currentAttempt = attempt
            
            print("🔄 Retry: Попытка \(attempt)/\(maxRetries)")
            
            do {
                let result = try await operation()
                
                // Успешное выполнение
                totalTime = Date().timeIntervalSince(startTime ?? Date())
                print("✅ Retry: Успешно выполнено за \(attempt) попытку(ок) за \(String(format: "%.2f", totalTime))с")
                
                return .success(result)
                
            } catch let error as NetworkError {
                // Проверяем условие retry
                if !retryCondition(error) || attempt == maxRetries {
                    totalTime = Date().timeIntervalSince(startTime ?? Date())
                    print("❌ Retry: Финальная ошибка после \(attempt) попыток за \(String(format: "%.2f", totalTime))с: \(error.localizedDescription)")
                    return .failure(error)
                }
                
                // Вычисляем задержку для следующей попытки
                let delay = calculateDelay(for: attempt)
                print("⏳ Retry: Ошибка \(error.localizedDescription), повтор через \(String(format: "%.1f", delay))с")
                
                // Ждем перед следующей попыткой
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                
            } catch {
                // Обрабатываем другие ошибки
                let networkError = NetworkError.unknown(error)
                
                if !retryCondition(networkError) || attempt == maxRetries {
                    totalTime = Date().timeIntervalSince(startTime ?? Date())
                    print("❌ Retry: Финальная ошибка после \(attempt) попыток за \(String(format: "%.2f", totalTime))с: \(error.localizedDescription)")
                    return .failure(networkError)
                }
                
                // Вычисляем задержку для следующей попытки
                let delay = calculateDelay(for: attempt)
                print("⏳ Retry: Ошибка \(error.localizedDescription), повтор через \(String(format: "%.1f", delay))с")
                
                // Ждем перед следующей попыткой
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            }
        }
        
        totalTime = Date().timeIntervalSince(startTime ?? Date())
        print("❌ Retry: Неожиданное завершение после \(maxRetries) попыток за \(String(format: "%.2f", totalTime))с")
        return .failure(.unknown(nil))
    }
    
    // MARK: - Private Methods
    
    /**
     * Вычисляет задержку для следующей попытки
     * Использует экспоненциальную задержку с джиттером
     */
    private func calculateDelay(for attempt: Int) -> TimeInterval {
        // Экспоненциальная задержка: baseDelay * (backoffMultiplier ^ (attempt - 1))
        let exponentialDelay = baseDelay * pow(backoffMultiplier, Double(attempt - 1))
        
        // Ограничиваем максимальной задержкой
        let cappedDelay = min(exponentialDelay, maxDelay)
        
        // Добавляем случайный джиттер (±10-30%)
        let jitter = Double.random(in: jitterRange)
        let jitterFactor = 1.0 + (Double.random(in: -jitter...jitter))
        
        let finalDelay = cappedDelay * jitterFactor
        
        print("🧮 Retry: Задержка для попытки \(attempt): \(String(format: "%.2f", finalDelay))с (базовая: \(String(format: "%.2f", cappedDelay))с, джиттер: \(String(format: "%.1f", jitterFactor * 100))%)")
        
        return finalDelay
    }
    
    /**
     * Сбрасывает состояние менеджера
     */
    private func reset() {
        currentAttempt = 0
        startTime = nil
        totalTime = 0
    }
    
    // MARK: - Statistics
    
    /**
     * Возвращает статистику выполнения
     */
    var statistics: RetryStatistics {
        return RetryStatistics(
            totalAttempts: currentAttempt,
            totalTime: totalTime,
            maxRetries: maxRetries,
            successRate: currentAttempt > 0 ? (currentAttempt == 1 ? 1.0 : 0.0) : 0.0
        )
    }
}

// MARK: - RetryStatistics

/**
 * Статистика выполнения retry операций
 */
struct RetryStatistics {
    let totalAttempts: Int
    let totalTime: TimeInterval
    let maxRetries: Int
    let successRate: Double
    
    var averageTimePerAttempt: TimeInterval {
        return totalAttempts > 0 ? totalTime / Double(totalAttempts) : 0
    }
    
    var wasSuccessful: Bool {
        return successRate > 0
    }
    
    var description: String {
        return """
        Retry Statistics:
        - Попыток: \(totalAttempts)/\(maxRetries)
        - Общее время: \(String(format: "%.2f", totalTime))с
        - Среднее время на попытку: \(String(format: "%.2f", averageTimePerAttempt))с
        - Успешность: \(String(format: "%.1f", successRate * 100))%
        - Результат: \(wasSuccessful ? "✅ Успех" : "❌ Неудача")
        """
    }
}

// MARK: - RetryManager Extensions

extension RetryManager {
    
    /**
     * Создает RetryManager для критических операций
     * Больше попыток, больше задержка
     */
    static func critical() -> RetryManager {
        return RetryManager(
            maxRetries: 5,
            baseDelay: 2.0,
            maxDelay: 60.0,
            backoffMultiplier: 2.5,
            jitterRange: 0.2...0.4
        )
    }
    
    /**
     * Создает RetryManager для быстрых операций
     * Меньше попыток, меньше задержка
     */
    static func fast() -> RetryManager {
        return RetryManager(
            maxRetries: 2,
            baseDelay: 0.5,
            maxDelay: 5.0,
            backoffMultiplier: 1.5,
            jitterRange: 0.1...0.2
        )
    }
    
    /**
     * Создает RetryManager для операций с большими данными
     * Умеренные настройки для баланса между надежностью и скоростью
     */
    static func balanced() -> RetryManager {
        return RetryManager(
            maxRetries: 3,
            baseDelay: 1.0,
            maxDelay: 30.0,
            backoffMultiplier: 2.0,
            jitterRange: 0.1...0.3
        )
    }
    
    /**
     * Создает RetryManager для операций с пользовательским интерфейсом
     * Быстрый отклик, но достаточная надежность
     */
    static func ui() -> RetryManager {
        return RetryManager(
            maxRetries: 2,
            baseDelay: 0.3,
            maxDelay: 3.0,
            backoffMultiplier: 1.8,
            jitterRange: 0.05...0.15
        )
    }
}

