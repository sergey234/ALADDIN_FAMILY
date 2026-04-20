import Foundation
import UIKit
import os.log

/**
 * 📊 Metrics Service
 * Отправка метрик производительности и ошибок на сервер
 * Для мониторинга продакшен приложения
 */
class MetricsService {

    // MARK: - Logger

    private static let metricsLogger = OSLog(
        subsystem: "com.aladdin.monitoring",
        category: "MetricsService"
    )

    // MARK: - Properties

    private let apiService: APIService
    private var pendingMetrics: [Metric] = []
    private let maxBatchSize = 50
    private let uploadInterval: TimeInterval = 30.0 // 30 секунд
    private var lastUploadTime: Date?
    private let queue = DispatchQueue(label: "com.aladdin.metrics", attributes: .concurrent)

    // Timer для автоматической отправки
    private var uploadTimer: Timer?

    // MARK: - Init

    init(apiService: APIService = .shared) {
        self.apiService = apiService
        startPeriodicUpload()

        #if DEBUG
        print("📊 MetricsService: Инициализирован с периодической отправкой каждые \(uploadInterval) сек")
        #endif

        os_log("📊 MetricsService: Initialized with batch size %d, interval %.1fs",
               log: Self.metricsLogger,
               type: .info,
               maxBatchSize,
               uploadInterval)
    }

    deinit {
        uploadTimer?.invalidate()
    }

    // MARK: - Public Methods

    /**
     * Отслеживание API запроса
     * - Parameters:
     *   - endpoint: Путь endpoint'а
     *   - method: HTTP метод
     *   - responseTime: Время ответа в секундах
     *   - statusCode: HTTP статус код
     *   - success: Успешность запроса
     */
    func trackAPIRequest(endpoint: String, method: String, responseTime: TimeInterval, statusCode: Int, success: Bool) {
        let metric = APIMetric(
            timestamp: Date(),
            endpoint: endpoint,
            method: method,
            responseTime: responseTime,
            statusCode: statusCode,
            success: success
        )

        addMetric(metric)
    }

    /**
     * Отслеживание действия пользователя
     * - Parameters:
     *   - action: Название действия
     *   - parameters: Дополнительные параметры
     */
    /// Параметры не должны содержать секреты; перед отправкой ключи вроде password/token скрываются.
    func trackUserAction(action: String, parameters: [String: Any]? = nil) {
        let metric = UserActionMetric(
            timestamp: Date(),
            action: action,
            parameters: Self.sanitizeMetricParameters(parameters)
        )

        addMetric(metric)
    }

    /// Убирает из словаря метрик поля, по имени ключа похожие на секреты (отправка на `/api/metrics/upload` без обязательной авторизации).
    private static func sanitizeMetricParameters(_ parameters: [String: Any]?) -> [String: Any]? {
        guard let parameters, !parameters.isEmpty else { return parameters }
        let blockedSubstrings = ["password", "token", "secret", "authorization", "cookie", "session", "refresh", "bearer"]
        var out: [String: Any] = [:]
        out.reserveCapacity(parameters.count)
        for (key, value) in parameters {
            let lower = key.lowercased()
            if blockedSubstrings.contains(where: { lower.contains($0) }) {
                out[key] = "<redacted>"
            } else {
                out[key] = value
            }
        }
        return out
    }

    /**
     * Отслеживание ошибки
     * - Parameters:
     *   - error: Ошибка
     *   - context: Контекст возникновения ошибки
     */
    func trackError(_ error: Error, context: String? = nil) {
        let metric = ErrorMetric(
            timestamp: Date(),
            errorType: String(describing: type(of: error)),
            errorMessage: error.localizedDescription,
            context: context
        )

        addMetric(metric)
    }

    /**
     * Отслеживание алерта
     * - Parameter alert: Алерт системы
     */
    func trackAlert(_ alert: Alert) {
        let metric = AlertMetric(
            timestamp: Date(),
            alertId: alert.id,
            alertType: alert.type.rawValue,
            severity: alert.severity.rawValue,
            message: alert.message
        )

        addMetric(metric)
    }

    /**
     * Отслеживание отчета о здоровье
     * - Parameter healthStatus: Статус здоровья системы
     */
    func trackHealthReport(_ healthStatus: HealthStatus) {
        let metric = HealthMetric(
            timestamp: Date(),
            status: healthStatus.status.rawValue,
            uptime: healthStatus.uptime,
            activeComponents: healthStatus.activeComponents,
            totalComponents: healthStatus.totalComponents,
            issues: healthStatus.issues
        )

        addMetric(metric)
    }

    /**
     * Принудительная отправка всех метрик на сервер
     * - Parameter completion: Callback с результатом отправки
     */
    func flush(completion: ((Result<Void, Error>) -> Void)? = nil) {
        queue.async {
            self.uploadMetricsNow(completion: completion)
        }
    }

    /**
     * Получить количество ожидающих отправки метрик
     */
    func getPendingMetricsCount() -> Int {
        return queue.sync { pendingMetrics.count }
    }

    // MARK: - Private Methods

    /**
     * Добавление метрики в очередь
     */
    private func addMetric(_ metric: Metric) {
        queue.async(flags: .barrier) {
            self.pendingMetrics.append(metric)

            #if DEBUG
            print("📊 MetricsService: Метрика добавлена (\(self.pendingMetrics.count) в очереди)")
            #endif

            // Если накопилось достаточно метрик, отправляем немедленно
            if self.pendingMetrics.count >= self.maxBatchSize {
                self.uploadMetricsNow()
            }
        }
    }

    /**
     * Запуск периодической отправки метрик
     */
    private func startPeriodicUpload() {
        DispatchQueue.main.async {
            self.uploadTimer = Timer.scheduledTimer(
                withTimeInterval: self.uploadInterval,
                repeats: true
            ) { [weak self] _ in
                self?.queue.async {
                    self?.uploadMetricsNow()
                }
            }
        }
    }

    /**
     * Отправка метрик на сервер немедленно
     */
    private func uploadMetricsNow(completion: ((Result<Void, Error>) -> Void)? = nil) {
        // Проверяем, есть ли метрики для отправки
        guard !pendingMetrics.isEmpty else {
            completion?(.success(()))
            return
        }

        // Копируем метрики для отправки
        let metricsToUpload = pendingMetrics
        let metricsCount = metricsToUpload.count

        // Очищаем очередь
        pendingMetrics.removeAll()

        // Создаем запрос
        let request = MetricsUploadRequest(
            deviceId: getDeviceId(),
            appVersion: AppConfig.appVersion,
            platform: "ios",
            metrics: metricsToUpload
        )

        #if DEBUG
        print("📊 MetricsService: Отправка \(metricsCount) метрик на сервер")
        #endif

        os_log("📊 MetricsService: Uploading %d metrics to server",
               log: Self.metricsLogger,
               type: .info,
               metricsCount)

        // ✅ ИСПРАВЛЕНИЕ: Отправляем метрики БЕЗ требования авторизации
        // Метрики должны отправляться даже для неавторизованных пользователей
        // Это предотвращает краш при отсутствии токена и позволяет собирать метрики от всех пользователей
        apiService.networkManager.post(endpoint: AppConfig.Endpoint.metricsUpload, body: request, requiresAuth: false) { (result: Result<MetricsUploadResponse, Error>) in
            switch result {
            case .success:
                #if DEBUG
                print("✅ MetricsService: Метрики успешно отправлены")
                #endif

                os_log("✅ MetricsService: Metrics uploaded successfully",
                       log: Self.metricsLogger,
                       type: .info)

                self.lastUploadTime = Date()
                completion?(.success(()))

            case .failure(let error):
                // В случае ошибки возвращаем метрики обратно в очередь
                self.queue.async(flags: .barrier) {
                    self.pendingMetrics.insert(contentsOf: metricsToUpload, at: 0)
                }

                #if DEBUG
                print("❌ MetricsService: Ошибка отправки метрик: \(error.localizedDescription)")
                #endif

                os_log("❌ MetricsService: Failed to upload metrics - %{public}@",
                       log: Self.metricsLogger,
                       type: .error,
                       error.localizedDescription)

                completion?(.failure(error))
            }
        }
    }

    /**
     * Получить уникальный ID устройства
     */
    private func getDeviceId() -> String {
        return UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
    }
}

// MARK: - Metric Protocols and Structures

protocol Metric: Codable {
    var timestamp: Date { get }
    var type: String { get }
}

/// API метрика
struct APIMetric: Metric {
    let timestamp: Date
    var type: String = "api_request"
    let endpoint: String
    let method: String
    let responseTime: Double
    let statusCode: Int
    let success: Bool
}

/// Метрика действия пользователя
struct UserActionMetric: Metric {
    let timestamp: Date
    let type: String = "user_action"
    let action: String
    let parameters: [String: Any]?

    // Custom encoding/decoding for parameters
    private enum CodingKeys: String, CodingKey {
        case timestamp, type, action, parameters
    }

    init(timestamp: Date, action: String, parameters: [String: Any]? = nil) {
        self.timestamp = timestamp
        self.action = action
        self.parameters = parameters
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        timestamp = try container.decode(Date.self, forKey: .timestamp)
        action = try container.decode(String.self, forKey: .action)
        
        // Decode parameters from JSON string
        if let jsonString = try? container.decodeIfPresent(String.self, forKey: .parameters),
           let jsonData = jsonString.data(using: .utf8),
           let params = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
            parameters = params
        } else {
            parameters = nil
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(timestamp, forKey: .timestamp)
        try container.encode(type, forKey: .type)
        try container.encode(action, forKey: .action)

        // Convert parameters to JSON string for encoding
        if let parameters = parameters {
            let jsonData = try JSONSerialization.data(withJSONObject: parameters)
            let jsonString = String(data: jsonData, encoding: .utf8)
            try container.encode(jsonString, forKey: .parameters)
        }
    }
}

/// Метрика ошибки
struct ErrorMetric: Metric {
    let timestamp: Date
    let type: String = "error"
    let errorType: String
    let errorMessage: String
    let context: String?
}

/// Метрика алерта
struct AlertMetric: Metric {
    let timestamp: Date
    let type: String = "alert"
    let alertId: String
    let alertType: String
    let severity: String
    let message: String
}

/// Метрика здоровья системы
struct HealthMetric: Metric {
    let timestamp: Date
    var type: String = "health"
    let status: String
    let uptime: Double
    let activeComponents: Int
    let totalComponents: Int
    let issues: [String]
}

// MARK: - Request/Response Models

/// Запрос на отправку метрик
struct MetricsUploadRequest: Codable {
    let deviceId: String
    let appVersion: String
    let platform: String
    let metrics: [Metric]
    
    enum CodingKeys: String, CodingKey {
        case deviceId, appVersion, platform, metrics
    }
    
    init(deviceId: String, appVersion: String, platform: String, metrics: [Metric]) {
        self.deviceId = deviceId
        self.appVersion = appVersion
        self.platform = platform
        self.metrics = metrics
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        deviceId = try container.decode(String.self, forKey: .deviceId)
        appVersion = try container.decode(String.self, forKey: .appVersion)
        platform = try container.decode(String.self, forKey: .platform)
        // Декодирование метрик не требуется (только отправка используется)
        metrics = []
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(deviceId, forKey: .deviceId)
        try container.encode(appVersion, forKey: .appVersion)
        try container.encode(platform, forKey: .platform)
        
        // Кодируем метрики как массив JSON объектов
        var metricsArray = container.nestedUnkeyedContainer(forKey: .metrics)
        let jsonEncoder = JSONEncoder()
        jsonEncoder.dateEncodingStrategy = .iso8601
        
        for metric in metrics {
            // Кодируем каждую метрику в зависимости от её типа
            var metricContainer = metricsArray.nestedContainer(keyedBy: DynamicCodingKey.self)
            
            // Кодируем базовые поля
            if let timestampKey = DynamicCodingKey(stringValue: "timestamp") {
                try metricContainer.encode(metric.timestamp, forKey: timestampKey)
            }
            if let typeKey = DynamicCodingKey(stringValue: "type") {
                try metricContainer.encode(metric.type, forKey: typeKey)
            }
            
            // Кодируем специфичные поля в зависимости от типа метрики
            if let apiMetric = metric as? APIMetric {
                if let key = DynamicCodingKey(stringValue: "endpoint") {
                    try metricContainer.encode(apiMetric.endpoint, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "method") {
                    try metricContainer.encode(apiMetric.method, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "responseTime") {
                    try metricContainer.encode(apiMetric.responseTime, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "statusCode") {
                    try metricContainer.encode(apiMetric.statusCode, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "success") {
                    try metricContainer.encode(apiMetric.success, forKey: key)
                }
            } else if let userMetric = metric as? UserActionMetric {
                if let key = DynamicCodingKey(stringValue: "action") {
                    try metricContainer.encode(userMetric.action, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "parameters"),
                   let params = userMetric.parameters {
                    let jsonData = try JSONSerialization.data(withJSONObject: params)
                    let jsonString = String(data: jsonData, encoding: .utf8) ?? ""
                    try metricContainer.encode(jsonString, forKey: key)
                }
            } else if let errorMetric = metric as? ErrorMetric {
                if let key = DynamicCodingKey(stringValue: "errorType") {
                    try metricContainer.encode(errorMetric.errorType, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "errorMessage") {
                    try metricContainer.encode(errorMetric.errorMessage, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "context"),
                   let context = errorMetric.context {
                    try metricContainer.encode(context, forKey: key)
                }
            } else if let alertMetric = metric as? AlertMetric {
                if let key = DynamicCodingKey(stringValue: "alertId") {
                    try metricContainer.encode(alertMetric.alertId, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "alertType") {
                    try metricContainer.encode(alertMetric.alertType, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "severity") {
                    try metricContainer.encode(alertMetric.severity, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "message") {
                    try metricContainer.encode(alertMetric.message, forKey: key)
                }
            } else if let healthMetric = metric as? HealthMetric {
                if let key = DynamicCodingKey(stringValue: "status") {
                    try metricContainer.encode(healthMetric.status, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "uptime") {
                    try metricContainer.encode(healthMetric.uptime, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "activeComponents") {
                    try metricContainer.encode(healthMetric.activeComponents, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "totalComponents") {
                    try metricContainer.encode(healthMetric.totalComponents, forKey: key)
                }
                if let key = DynamicCodingKey(stringValue: "issues") {
                    try metricContainer.encode(healthMetric.issues, forKey: key)
                }
            }
        }
    }
    
    private struct DynamicCodingKey: CodingKey {
        var stringValue: String
        var intValue: Int?
        
        init?(stringValue: String) {
            self.stringValue = stringValue
        }
        
        init?(intValue: Int) {
            return nil
        }
    }
}

/// Ответ на отправку метрик
struct MetricsUploadResponse: Codable {
    let success: Bool
    let uploadedCount: Int
    let message: String?
}