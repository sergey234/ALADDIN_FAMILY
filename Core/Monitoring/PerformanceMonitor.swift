import Foundation
import UIKit
import os.log

/**
 * 📈 Performance Monitor
 * Отслеживание производительности приложения
 * FPS, память, время загрузки экранов, сетевые метрики
 */
class PerformanceMonitor {

    // MARK: - Logger

    private static let performanceLogger = OSLog(
        subsystem: "com.aladdin.monitoring",
        category: "PerformanceMonitor"
    )

    // MARK: - Singleton

    static let shared = PerformanceMonitor()

    // MARK: - Properties

    private let metricsService = MetricsService()

    // FPS monitoring
    private var displayLink: CADisplayLink?
    private var frameCount: Int = 0
    private var lastFrameTime: CFTimeInterval = 0
    private var currentFPS: Double = 0

    // Memory monitoring
    private var memoryTimer: Timer?

    // Screen load time tracking
    private var screenLoadStartTimes: [String: Date] = [:]

    // Network performance tracking
    private var networkRequestStartTimes: [String: Date] = [:]

    // MARK: - Init

    private init() {
        startFPSMonitoring()
        startMemoryMonitoring()

        #if DEBUG
        print("📈 PerformanceMonitor: Инициализирован, мониторинг запущен")
        #endif

        os_log("📈 PerformanceMonitor: Initialized and monitoring started",
               log: Self.performanceLogger,
               type: .info)
    }

    deinit {
        stopMonitoring()
    }

    // MARK: - Public Methods

    /**
     * Начать отслеживание загрузки экрана
     * - Parameter screenName: Название экрана
     */
    func startScreenLoad(_ screenName: String) {
        screenLoadStartTimes[screenName] = Date()

        #if DEBUG
        print("📈 PerformanceMonitor: Начата загрузка экрана '\(screenName)'")
        #endif
    }

    /**
     * Завершить отслеживание загрузки экрана
     * - Parameter screenName: Название экрана
     */
    func endScreenLoad(_ screenName: String) {
        guard let startTime = screenLoadStartTimes[screenName] else { return }

        let loadTime = Date().timeIntervalSince(startTime)
        screenLoadStartTimes.removeValue(forKey: screenName)

        // Отправляем метрику
        let parameters: [String: Any] = [
            "screen_name": screenName,
            "load_time": loadTime,
            "timestamp": Date().timeIntervalSince1970
        ]

        metricsService.trackUserAction(action: "screen_load_complete", parameters: parameters)

        #if DEBUG
        print("📈 PerformanceMonitor: Экран '\(screenName)' загружен за \(String(format: "%.3f", loadTime)) сек")
        #endif

        os_log("📈 Screen Load: %{public}@ loaded in %.3fs",
               log: Self.performanceLogger,
               type: .info,
               screenName,
               loadTime)
    }

    /**
     * Начать отслеживание сетевого запроса
     * - Parameter requestId: Уникальный ID запроса
     */
    func startNetworkRequest(_ requestId: String) {
        networkRequestStartTimes[requestId] = Date()

        #if DEBUG
        print("📈 PerformanceMonitor: Начался сетевой запрос '\(requestId)'")
        #endif
    }

    /**
     * Завершить отслеживание сетевого запроса
     * - Parameters:
     *   - requestId: Уникальный ID запроса
     *   - bytesTransferred: Количество переданных байт
     */
    func endNetworkRequest(_ requestId: String, bytesTransferred: Int64) {
        guard let startTime = networkRequestStartTimes[requestId] else { return }

        let requestTime = Date().timeIntervalSince(startTime)
        networkRequestStartTimes.removeValue(forKey: requestId)

        // Отправляем метрику
        let parameters: [String: Any] = [
            "request_id": requestId,
            "request_time": requestTime,
            "bytes_transferred": bytesTransferred,
            "timestamp": Date().timeIntervalSince1970
        ]

        metricsService.trackUserAction(action: "network_request_complete", parameters: parameters)

        #if DEBUG
        print("📈 PerformanceMonitor: Сетевой запрос '\(requestId)' завершен за \(String(format: "%.3f", requestTime)) сек, \(bytesTransferred) байт")
        #endif

        os_log("📈 Network Request: %{public}@ completed in %.3fs (%lld bytes)",
               log: Self.performanceLogger,
               type: .info,
               requestId,
               requestTime,
               bytesTransferred)
    }

    /**
     * Отслеживание действия пользователя с производительностью
     * - Parameters:
     *   - action: Название действия
     *   - duration: Время выполнения действия
     *   - additionalParams: Дополнительные параметры
     */
    func trackActionPerformance(_ action: String, duration: TimeInterval, additionalParams: [String: Any]? = nil) {
        var parameters: [String: Any] = [
            "action": action,
            "duration": duration,
            "fps": currentFPS,
            "memory_mb": getMemoryUsageMB(),
            "timestamp": Date().timeIntervalSince1970
        ]

        if let additionalParams = additionalParams {
            parameters.merge(additionalParams) { _, new in new }
        }

        metricsService.trackUserAction(action: "action_performance", parameters: parameters)

        #if DEBUG
        print("📈 PerformanceMonitor: Действие '\(action)' выполнено за \(String(format: "%.3f", duration)) сек (FPS: \(Int(currentFPS)), память: \(String(format: "%.1f", getMemoryUsageMB())) MB)")
        #endif

        os_log("📈 Action Performance: %{public}@ completed in %.3fs (FPS: %d, Memory: %.1f MB)",
               log: Self.performanceLogger,
               type: .info,
               action,
               duration,
               Int(currentFPS),
               getMemoryUsageMB())
    }

    /**
     * Получить текущий FPS
     */
    func getCurrentFPS() -> Double {
        return currentFPS
    }

    /**
     * Получить использование памяти (в MB)
     */
    func getMemoryUsageMB() -> Double {
        let memoryUsage = getMemoryUsage()
        return Double(memoryUsage) / (1024 * 1024)
    }

    // MARK: - Private Methods

    /**
     * Запустить мониторинг FPS
     */
    private func startFPSMonitoring() {
        displayLink = CADisplayLink(target: self, selector: #selector(updateFPS))
        displayLink?.add(to: .main, forMode: .common)
    }

    /**
     * Запустить мониторинг памяти
     */
    private func startMemoryMonitoring() {
        memoryTimer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            self?.checkMemoryUsage()
        }
    }

    /**
     * Остановить весь мониторинг
     */
    private func stopMonitoring() {
        displayLink?.invalidate()
        displayLink = nil

        memoryTimer?.invalidate()
        memoryTimer = nil
    }

    /**
     * Обновление FPS (вызывается CADisplayLink)
     */
    @objc private func updateFPS() {
        frameCount += 1

        let currentTime = CACurrentMediaTime()
        let deltaTime = currentTime - lastFrameTime

        // Обновляем FPS каждую секунду
        if deltaTime >= 1.0 {
            currentFPS = Double(frameCount) / deltaTime
            frameCount = 0
            lastFrameTime = currentTime

            // Отправляем метрику FPS каждые 10 секунд
            if Int(currentTime) % 10 == 0 {
                sendFPSMetric()
            }
        }
    }

    /**
     * Проверка использования памяти
     */
    private func checkMemoryUsage() {
        let memoryUsageMB = getMemoryUsageMB()

        // Отправляем метрику памяти
        let parameters: [String: Any] = [
            "memory_mb": memoryUsageMB,
            "fps": currentFPS,
            "timestamp": Date().timeIntervalSince1970
        ]

        metricsService.trackUserAction(action: "memory_usage_check", parameters: parameters)

        #if DEBUG
        print("📈 PerformanceMonitor: Использование памяти: \(String(format: "%.1f", memoryUsageMB)) MB, FPS: \(Int(currentFPS))")
        #endif

        os_log("📈 Memory Usage: %.1f MB, FPS: %d",
               log: Self.performanceLogger,
               type: .info,
               memoryUsageMB,
               Int(currentFPS))
    }

    /**
     * Отправка метрики FPS
     */
    private func sendFPSMetric() {
        let parameters: [String: Any] = [
            "fps": currentFPS,
            "memory_mb": getMemoryUsageMB(),
            "timestamp": Date().timeIntervalSince1970
        ]

        metricsService.trackUserAction(action: "fps_measurement", parameters: parameters)
    }

    /**
     * Получить использование памяти (в байтах)
     */
    private func getMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4

        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        return kerr == KERN_SUCCESS ? info.resident_size : 0
    }
}

// MARK: - Screen Performance Extensions

extension PerformanceMonitor {

    /**
     * Удобный метод для измерения времени выполнения блока кода
     */
    func measureExecutionTime<T>(_ operationName: String, operation: () throws -> T) rethrows -> T {
        let startTime = Date()
        let result = try operation()
        let duration = Date().timeIntervalSince(startTime)

        trackActionPerformance(operationName, duration: duration)

        return result
    }

    /**
     * Удобный метод для измерения времени выполнения асинхронной операции
     */
    func measureAsyncExecutionTime<T>(_ operationName: String, operation: () async throws -> T) async rethrows -> T {
        let startTime = Date()
        let result = try await operation()
        let duration = Date().timeIntervalSince(startTime)

        trackActionPerformance(operationName, duration: duration)

        return result
    }
}

// MARK: - ViewController Extensions

extension UIViewController {

    /**
     * Начать отслеживание загрузки view controller'а
     */
    func startPerformanceMonitoring() {
        let screenName = String(describing: type(of: self))
        PerformanceMonitor.shared.startScreenLoad(screenName)
    }

    /**
     * Завершить отслеживание загрузки view controller'а
     */
    func endPerformanceMonitoring() {
        let screenName = String(describing: type(of: self))
        PerformanceMonitor.shared.endScreenLoad(screenName)
    }
}

// MARK: - Network Extensions

extension NetworkManager {

    /**
     * Отслеживание сетевых запросов
     */
    func performRequestWithPerformanceMonitoring<T: Decodable>(
        request: URLRequest,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let requestId = UUID().uuidString
        let endpoint = request.url?.path ?? "unknown"

        PerformanceMonitor.shared.startNetworkRequest(requestId)

        // Выполняем запрос через URLSession напрямую
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            // Определяем размер ответа
            let responseSize: Int64 = Int64(data?.count ?? 0)
            
            PerformanceMonitor.shared.endNetworkRequest(requestId, bytesTransferred: responseSize)
            
            // Обрабатываем результат
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "NetworkManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }
        task.resume()
    }
}