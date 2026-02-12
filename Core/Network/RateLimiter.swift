import Foundation
import os.log

/**
 * 🛡️ Rate Limiter
 * Защита от перегрузки сервера и DDoS атак
 * Ограничивает частоту API запросов на уровне приложения
 */
class RateLimiter {
    
    // MARK: - Logger
    
    private static let rateLimitLogger = OSLog(
        subsystem: "com.aladdin.network",
        category: "RateLimiter"
    )
    
    // MARK: - Properties
    
    /// Максимальное количество запросов в временном окне
    private let maxRequests: Int
    
    /// Размер временного окна в секундах
    private let timeWindow: TimeInterval
    
    /// История запросов по endpoint'ам
    private var requestCounts: [String: [Date]] = [:]
    
    /// Очередь для thread-safe операций
    private let queue = DispatchQueue(label: "com.aladdin.ratelimiter", attributes: .concurrent)
    
    // MARK: - Init
    
    /**
     * Инициализирует Rate Limiter
     * - Parameters:
     *   - maxRequests: Максимальное количество запросов в окне (по умолчанию 100)
     *   - timeWindow: Временное окно в секундах (по умолчанию 60 - 1 минута)
     */
    init(maxRequests: Int = 100, timeWindow: TimeInterval = 60.0) {
        self.maxRequests = maxRequests
        self.timeWindow = timeWindow
        
        #if DEBUG
        print("🛡️ RateLimiter: Инициализирован (макс \(maxRequests) запросов / \(timeWindow) сек)")
        #endif
        
        // Логируем в production
        os_log("🛡️ RateLimiter: Инициализирован с лимитом %{public}d запросов в %{public}.1f сек",
               log: Self.rateLimitLogger,
               type: .info,
               maxRequests,
               timeWindow)
    }
    
    // MARK: - Public Methods
    
    /**
     * Проверяет, можно ли сделать запрос к указанному endpoint'у
     * - Parameter endpoint: Путь endpoint'а (например "/api/analytics")
     * - Returns: true если запрос разрешен, false если лимит превышен
     */
    func canMakeRequest(to endpoint: String) -> Bool {
        return queue.sync {
            // Очищаем старые записи
            cleanOldRequests(for: endpoint)
            
            // Получаем текущие запросы для endpoint'а
            let currentRequests = requestCounts[endpoint] ?? []
            
            // Проверяем лимит
            if currentRequests.count >= maxRequests {
                // Лимит превышен - логируем
                logRateLimitExceeded(endpoint: endpoint, currentCount: currentRequests.count)
                return false
            }
            
            return true
        }
    }
    
    /**
     * Регистрирует новый запрос к endpoint'у
     * - Parameter endpoint: Путь endpoint'а
     */
    func recordRequest(to endpoint: String) {
        queue.async(flags: .barrier) {
            // Очищаем старые записи
            self.cleanOldRequests(for: endpoint)
            
            // Добавляем новую запись
            let now = Date()
            if self.requestCounts[endpoint] == nil {
                self.requestCounts[endpoint] = []
            }
            self.requestCounts[endpoint]?.append(now)
            
            #if DEBUG
            let currentCount = self.requestCounts[endpoint]?.count ?? 0
            print("📊 RateLimiter: Запрос записан для \(endpoint) (всего: \(currentCount))")
            #endif
        }
    }
    
    /**
     * Возвращает количество запросов к endpoint'у в текущем окне
     * - Parameter endpoint: Путь endpoint'а
     * - Returns: Количество запросов
     */
    func getRequestCount(for endpoint: String) -> Int {
        return queue.sync {
            cleanOldRequests(for: endpoint)
            return requestCounts[endpoint]?.count ?? 0
        }
    }
    
    /**
     * Возвращает время до сброса лимита в секундах
     * - Parameter endpoint: Путь endpoint'а
     * - Returns: Время в секундах до сброса (nil если лимит не превышен)
     */
    func getTimeUntilReset(for endpoint: String) -> TimeInterval? {
        return queue.sync {
            guard let requests = requestCounts[endpoint], !requests.isEmpty else {
                return nil
            }
            
            // Находим самый старый запрос
            if let oldestRequest = requests.min() {
                let timePassed = Date().timeIntervalSince(oldestRequest)
                let timeRemaining = timeWindow - timePassed
                return max(0, timeRemaining)
            }
            
            return nil
        }
    }
    
    /**
     * Сбрасывает счетчик для endpoint'а (для тестирования)
     * - Parameter endpoint: Путь endpoint'а
     */
    func resetCounter(for endpoint: String) {
        queue.async(flags: .barrier) {
            self.requestCounts.removeValue(forKey: endpoint)
            
            #if DEBUG
            print("🔄 RateLimiter: Счетчик сброшен для \(endpoint)")
            #endif
        }
    }
    
    /**
     * Сбрасывает все счетчики (для тестирования)
     */
    func resetAllCounters() {
        queue.async(flags: .barrier) {
            self.requestCounts.removeAll()
            
            #if DEBUG
            print("🔄 RateLimiter: Все счетчики сброшены")
            #endif
        }
    }
    
    // MARK: - Private Methods
    
    /**
     * Очищает устаревшие записи запросов
     * - Parameter endpoint: Путь endpoint'а
     */
    private func cleanOldRequests(for endpoint: String) {
        let cutoffDate = Date().addingTimeInterval(-timeWindow)
        
        if var requests = requestCounts[endpoint] {
            // Фильтруем только актуальные запросы
            requests = requests.filter { $0 > cutoffDate }
            requestCounts[endpoint] = requests
        }
    }
    
    /**
     * Логирует превышение лимита
     * - Parameters:
     *   - endpoint: Путь endpoint'а
     *   - currentCount: Текущее количество запросов
     */
    private func logRateLimitExceeded(endpoint: String, currentCount: Int) {
        let timeUntilReset = getTimeUntilReset(for: endpoint) ?? 0
        
        // DEBUG логирование
        #if DEBUG
        print("🚫 RateLimiter: ЛИМИТ ПРЕВЫШЕН для \(endpoint)")
        print("   - Текущих запросов: \(currentCount)")
        print("   - Максимум: \(maxRequests)")
        print("   - Время до сброса: \(String(format: "%.1f", timeUntilReset)) сек")
        print("   - Окно: \(timeWindow) сек")
        #endif
        
        // Production логирование
        os_log("🚫 Rate Limit EXCEEDED: %{public}@ (%d/%d requests, reset in %.1fs)",
               log: Self.rateLimitLogger,
               type: .error,
               endpoint,
               currentCount,
               maxRequests,
               timeUntilReset)
    }
    
    // MARK: - Debug Methods
    
    /**
     * Возвращает статистику по всем endpoint'ам (для отладки)
     */
    func getStatistics() -> [String: Int] {
        return queue.sync {
            var stats: [String: Int] = [:]
            
            for (endpoint, requests) in requestCounts {
                cleanOldRequests(for: endpoint)
                stats[endpoint] = requestCounts[endpoint]?.count ?? 0
            }
            
            return stats
        }
    }
    
    /**
     * Печатает статистику в консоль (для отладки)
     */
    func printStatistics() {
        let stats = getStatistics()
        
        print("📊 RateLimiter Statistics:")
        print("   - Max requests: \(maxRequests)")
        print("   - Time window: \(timeWindow) seconds")
        print("   - Active endpoints: \(stats.count)")
        
        for (endpoint, count) in stats.sorted(by: { $0.value > $1.value }) {
            let percentage = Double(count) / Double(maxRequests) * 100
            print("     \(endpoint): \(count)/\(maxRequests) (\(String(format: "%.1f", percentage))%)")
        }
    }
}