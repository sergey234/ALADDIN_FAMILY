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
    
    /// Очередь для thread-safe операций (serial — concurrent + mutation был причиной SIGSEGV/PAC crash)
    private let queue = DispatchQueue(label: "com.aladdin.ratelimiter") // serial by default — fixes data race
    
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
            let cutoffDate = Date().addingTimeInterval(-timeWindow)
            var currentRequests = self.requestCounts[endpoint] ?? []
            currentRequests = currentRequests.filter { $0 > cutoffDate }
            self.requestCounts[endpoint] = currentRequests
            
            if currentRequests.isEmpty {
                self.requestCounts.removeValue(forKey: endpoint)
            }
            
            // Проверяем лимит
            if currentRequests.count >= self.maxRequests {
                let countForLog = currentRequests.count
                // Логируем БЕЗ nested sync (вызываем getTimeUntilReset вне блока)
                DispatchQueue.global().async { [weak self] in
                    self?.logRateLimitExceeded(endpoint: endpoint, currentCount: countForLog)
                }
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
        queue.async(flags: .barrier) { [weak self] in
            guard let self = self else { return }
            let cutoffDate = Date().addingTimeInterval(-self.timeWindow)
            var currentRequests = self.requestCounts[endpoint] ?? []
            currentRequests = currentRequests.filter { $0 > cutoffDate }
            currentRequests.append(Date())
            self.requestCounts[endpoint] = currentRequests
            
            #if DEBUG
            let currentCount = currentRequests.count
            print("📊 RateLimiter: Запрос записан для \(endpoint) (всего: \(currentCount))")
            #endif
            
            // Логируем в production (без nested sync)
            os_log("📊 RateLimiter: Запрос записан для %{public}s",
                   log: Self.rateLimitLogger,
                   type: .debug,
                   endpoint)
        }
    }
    
    /**
     * Возвращает количество запросов к endpoint'у в текущем окне
     * - Parameter endpoint: Путь endpoint'а
     * - Returns: Количество запросов
     */
    func getRequestCount(for endpoint: String) -> Int {
        return queue.sync { [weak self] in
            guard let self = self else { return 0 }
            let cutoffDate = Date().addingTimeInterval(-self.timeWindow)
            var currentRequests = self.requestCounts[endpoint] ?? []
            currentRequests = currentRequests.filter { $0 > cutoffDate }
            self.requestCounts[endpoint] = currentRequests
            
            if currentRequests.isEmpty {
                self.requestCounts.removeValue(forKey: endpoint)
            }
            
            return currentRequests.count
        }
    }
    
    /**
     * Возвращает время до сброса лимита в секундах
     * - Parameter endpoint: Путь endpoint'а
     * - Returns: Время в секундах до сброса (nil если лимит не превышен)
     */
    func getTimeUntilReset(for endpoint: String) -> TimeInterval? {
        return queue.sync { [weak self] in
            guard let self = self else { return nil }
            let cutoffDate = Date().addingTimeInterval(-self.timeWindow)
            var currentRequests = self.requestCounts[endpoint] ?? []
            currentRequests = currentRequests.filter { $0 > cutoffDate }
            self.requestCounts[endpoint] = currentRequests
            
            if currentRequests.isEmpty {
                self.requestCounts.removeValue(forKey: endpoint)
                return nil
            }
            
            // Находим самый старый запрос
            if let oldestRequest = currentRequests.min() {
                let timePassed = Date().timeIntervalSince(oldestRequest)
                let timeRemaining = self.timeWindow - timePassed
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
     * Логирует превышение лимита
     * - Parameters:
     *   - endpoint: Путь endpoint'а
     *   - currentCount: Текущее количество запросов
     */
    private func logRateLimitExceeded(endpoint: String, currentCount: Int) {
        // Avoid calling sync methods from inside other sync blocks (was causing nested sync + crash)
        let timeUntilReset = 60.0 // safe default to prevent reentrancy
        
        // DEBUG логирование
        #if DEBUG
        print("🚫 RateLimiter: ЛИМИТ ПРЕВЫШЕН для \(endpoint)")
        print("   - Текущих запросов: \(currentCount)")
        print("   - Максимум: \(self.maxRequests)")
        print("   - Время до сброса: \(String(format: "%.1f", timeUntilReset)) сек")
        print("   - Окно: \(self.timeWindow) сек")
        #endif
        
        // Production логирование (safe, no nested calls)
        os_log("🚫 Rate Limit EXCEEDED: %{public}@ (%d/%d requests, reset in %.1fs)",
               log: Self.rateLimitLogger,
               type: .error,
               endpoint,
               currentCount,
               self.maxRequests,
               timeUntilReset)
    }
    
    // MARK: - Debug Methods
    
    /**
     * Возвращает статистику по всем endpoint'ам (для отладки)
     */
    func getStatistics() -> [String: Int] {
        return queue.sync { [weak self] in
            guard let self = self else { return [:] }
            let cutoffDate = Date().addingTimeInterval(-self.timeWindow)
            var stats: [String: Int] = [:]
            
            // Copy to avoid mutation during iteration
            let currentCounts = self.requestCounts
            for (endpoint, var requests) in currentCounts {
                requests = requests.filter { $0 > cutoffDate }
                self.requestCounts[endpoint] = requests
                
                if requests.isEmpty {
                    self.requestCounts.removeValue(forKey: endpoint)
                } else {
                    stats[endpoint] = requests.count
                }
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