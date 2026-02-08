import Foundation
import Combine

/**
 * 📊 Production Monitoring Service
 * Система мониторинга для продакшена
 * Отслеживает производительность, ошибки и алерты
 */

class ProductionMonitoringService {
    static let shared = ProductionMonitoringService()

    // MARK: - Properties

    private let analyticsService: AnalyticsService
    private var cancellables = Set<AnyCancellable>()

    // Метрики производительности
    private var apiResponseTimes: [String: [TimeInterval]] = [:]
    private var errorCounts: [String: Int] = [:]
    private let maxSamplesPerEndpoint = 100

    // Пороги алертов
    private let alertThresholds = AlertThresholds()

    // MARK: - Initialization

    private init(analyticsService: AnalyticsService = AnalyticsService.shared) {
        self.analyticsService = analyticsService
        setupPeriodicReporting()
    }

    // MARK: - Public Methods

    /// Отследить API запрос
    func trackAPIRequest(
        endpoint: String,
        method: String,
        responseTime: TimeInterval,
        statusCode: Int,
        error: Error? = nil
    ) {
        // Записываем время ответа
        trackResponseTime(endpoint: endpoint, responseTime: responseTime)

        // Записываем ошибку если есть
        if let error = error {
            trackError(endpoint: endpoint, error: error)
        }

        // Проверяем пороги алертов
        checkAlertThresholds(endpoint: endpoint, responseTime: responseTime, statusCode: statusCode)

        // Отправляем в аналитику
        analyticsService.trackAPIRequest(
            endpoint: endpoint,
            method: method,
            responseTime: responseTime,
            statusCode: statusCode,
            success: error == nil
        )
    }

    /// Отследить пользовательское действие
    func trackUserAction(action: String, parameters: [String: Any]? = nil) {
        analyticsService.trackUserAction(action: action, parameters: parameters)
    }

    /// Отследить ошибку приложения
    func trackAppError(error: Error, context: String? = nil) {
        let errorInfo: [String: Any] = [
            "error_type": String(describing: type(of: error)),
            "error_description": error.localizedDescription,
            "context": context ?? "unknown",
            "timestamp": Date().timeIntervalSince1970
        ]

        analyticsService.trackError(error: error, context: context)
        checkErrorAlertThresholds(errorInfo: errorInfo)
    }

    /// Получить метрики производительности
    func getPerformanceMetrics() -> PerformanceMetrics {
        var metrics: [String: EndpointMetrics] = [:]

        for (endpoint, times) in apiResponseTimes {
            let sortedTimes = times.sorted()
            let p95 = calculatePercentile(times: sortedTimes, percentile: 0.95)
            let p99 = calculatePercentile(times: sortedTimes, percentile: 0.99)
            let avg = times.reduce(0, +) / Double(times.count)

            metrics[endpoint] = EndpointMetrics(
                endpoint: endpoint,
                averageResponseTime: avg,
                p95ResponseTime: p95,
                p99ResponseTime: p99,
                totalRequests: times.count,
                errorCount: errorCounts[endpoint] ?? 0
            )
        }

        return PerformanceMetrics(
            endpoints: metrics,
            totalRequests: metrics.values.reduce(0) { $0 + $1.totalRequests },
            totalErrors: metrics.values.reduce(0) { $0 + $1.errorCount },
            timestamp: Date()
        )
    }

    /// Проверить здоровье системы
    func performHealthCheck() async -> HealthStatus {
        let metrics = getPerformanceMetrics()

        // Проверяем критические метрики
        let criticalEndpoints = ["crash_detection_agent", "emergency_response_bot"]
        var criticalIssues: [String] = []

        for endpoint in criticalEndpoints {
            if let endpointMetrics = metrics.endpoints[endpoint] {
                if endpointMetrics.p95ResponseTime > alertThresholds.criticalResponseTime {
                    criticalIssues.append("\(endpoint): P95 \(String(format: "%.2f", endpointMetrics.p95ResponseTime))s")
                }
                if endpointMetrics.errorCount > alertThresholds.maxErrorsPerEndpoint {
                    criticalIssues.append("\(endpoint): \(endpointMetrics.errorCount) ошибок")
                }
            }
        }

        let status: HealthStatus.Status
        if criticalIssues.isEmpty && metrics.totalErrors == 0 {
            status = .healthy
        } else if criticalIssues.isEmpty {
            status = .warning
        } else {
            status = .critical
        }

        return HealthStatus(
            status: status,
            metrics: metrics,
            issues: criticalIssues,
            timestamp: Date()
        )
    }

    // MARK: - Private Methods

    private func trackResponseTime(endpoint: String, responseTime: TimeInterval) {
        if apiResponseTimes[endpoint] == nil {
            apiResponseTimes[endpoint] = []
        }

        apiResponseTimes[endpoint]?.append(responseTime)

        // Ограничиваем количество сэмплов
        if let count = apiResponseTimes[endpoint]?.count, count > maxSamplesPerEndpoint {
            apiResponseTimes[endpoint]?.removeFirst(count - maxSamplesPerEndpoint)
        }
    }

    private func trackError(endpoint: String, error: Error) {
        errorCounts[endpoint, default: 0] += 1
    }

    private func checkAlertThresholds(endpoint: String, responseTime: TimeInterval, statusCode: Int) {
        // Проверяем P95 для endpoint
        if let times = apiResponseTimes[endpoint], times.count >= 10 {
            let sortedTimes = times.sorted()
            let p95 = calculatePercentile(times: sortedTimes, percentile: 0.95)

            if p95 > alertThresholds.criticalResponseTime {
                sendAlert(
                    type: .performance,
                    message: "P95 response time exceeded: \(endpoint) - \(String(format: "%.2f", p95))s",
                    severity: .critical
                )
            } else if p95 > alertThresholds.warningResponseTime {
                sendAlert(
                    type: .performance,
                    message: "P95 response time warning: \(endpoint) - \(String(format: "%.2f", p95))s",
                    severity: .warning
                )
            }
        }

        // Проверяем ошибки
        if let errorCount = errorCounts[endpoint], errorCount > alertThresholds.maxErrorsPerEndpoint {
            sendAlert(
                type: .error,
                message: "High error rate: \(endpoint) - \(errorCount) errors",
                severity: .critical
            )
        }

        // Проверяем HTTP статус
        if statusCode >= 500 {
            sendAlert(
                type: .error,
                message: "Server error: \(endpoint) - HTTP \(statusCode)",
                severity: .critical
            )
        } else if statusCode >= 400 {
            sendAlert(
                type: .error,
                message: "Client error: \(endpoint) - HTTP \(statusCode)",
                severity: .warning
            )
        }
    }

    private func checkErrorAlertThresholds(errorInfo: [String: Any]) {
        // Проверяем частоту ошибок
        let totalErrors = errorCounts.values.reduce(0, +)
        if totalErrors > alertThresholds.maxTotalErrors {
            sendAlert(
                type: .error,
                message: "High total error count: \(totalErrors) errors",
                severity: .critical
            )
        }
    }

    private func sendAlert(type: AlertType, message: String, severity: AlertSeverity) {
        let alert = Alert(
            id: UUID().uuidString,
            type: type,
            message: message,
            severity: severity,
            timestamp: Date()
        )

        // Отправляем в аналитику
        analyticsService.trackAlert(alert: alert)

        // В продакшене здесь можно отправить push уведомление разработчикам
        #if !DEBUG
        print("🚨 PRODUCTION ALERT: [\(severity.rawValue.uppercased())] \(message)")
        #endif
    }

    private func setupPeriodicReporting() {
        // Отправляем отчет каждые 5 минут
        Timer.publish(every: 300, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.sendPeriodicReport()
            }
            .store(in: &cancellables)
    }

    private func sendPeriodicReport() {
        Task {
            let healthStatus = await performHealthCheck()
            analyticsService.trackHealthReport(healthStatus: healthStatus)
        }
    }

    private func calculatePercentile(times: [TimeInterval], percentile: Double) -> TimeInterval {
        guard !times.isEmpty else { return 0 }

        let index = Int(Double(times.count - 1) * percentile)
        return times[index]
    }
}

// MARK: - Supporting Types

struct AlertThresholds {
    let warningResponseTime: TimeInterval = 1.0    // 1 секунда
    let criticalResponseTime: TimeInterval = 3.0   // 3 секунды
    let maxErrorsPerEndpoint = 5                   // 5 ошибок на endpoint
    let maxTotalErrors = 20                        // 20 ошибок всего
}

struct EndpointMetrics {
    let endpoint: String
    let averageResponseTime: TimeInterval
    let p95ResponseTime: TimeInterval
    let p99ResponseTime: TimeInterval
    let totalRequests: Int
    let errorCount: Int
}

struct PerformanceMetrics {
    let endpoints: [String: EndpointMetrics]
    let totalRequests: Int
    let totalErrors: Int
    let timestamp: Date
}

struct HealthStatus {
    enum Status: String {
        case healthy = "healthy"
        case warning = "warning"
        case critical = "critical"
    }

    let status: Status
    let metrics: PerformanceMetrics
    let issues: [String]
    let timestamp: Date
}

enum AlertType: String {
    case performance = "performance"
    case error = "error"
    case security = "security"
}

enum AlertSeverity: String {
    case info = "info"
    case warning = "warning"
    case critical = "critical"
}

struct Alert {
    let id: String
    let type: AlertType
    let message: String
    let severity: AlertSeverity
    let timestamp: Date
}