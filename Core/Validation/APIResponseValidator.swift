import Foundation
import os.log

/// Как сопоставлять ответ статуса компонента с запрошенным `componentId` (эндпоинты get/enable/disable).
enum ComponentStatusAPIResolutionPolicy {
    /// Id из URL/запроса — канон: расхождение в теле не ломает клиент.
    case canonicalRequestIdAlwaysWins
    /// Непустой `component_id` в envelope должен совпадать с запросом.
    case rejectMismatchedExplicitComponentId
}

/**
 * 🛡️ API Response Validator
 * Валидация данных, получаемых от API
 * Предотвращает краши приложения от некорректных данных
 */
struct APIResponseValidator {

    // MARK: - Component status (envelope / flat → ComponentStatus)

    /// Единая сборка `ComponentStatus` из `ComponentStatusResponse` для `APIService` get/enable/disable.
    static func makeComponentStatus(
        from response: ComponentStatusResponse,
        canonicalComponentId: String,
        policy: ComponentStatusAPIResolutionPolicy = .canonicalRequestIdAlwaysWins
    ) throws -> ComponentStatus {
        let derived = response.componentStatus

        if case .rejectMismatchedExplicitComponentId = policy {
            if let bodyId = response.componentId, !bodyId.isEmpty, bodyId != canonicalComponentId {
                throw NetworkError.decodingError(NSError(
                    domain: "APIResponseValidator",
                    code: 10,
                    userInfo: [NSLocalizedDescriptionKey: "component_id mismatch: expected \(canonicalComponentId), got \(bodyId)"]
                ))
            }
        }

        return ComponentStatus(
            componentId: canonicalComponentId,
            isEnabled: derived.isEnabled,
            lastUpdate: derived.lastUpdate,
            configuration: derived.configuration
        )
    }

    // MARK: - Logger

    private static let validationLogger = OSLog(
        subsystem: "com.aladdin.validation",
        category: "APIResponseValidator"
    )

    // MARK: - Public Methods

    /**
     * Валидирует любой Codable объект
     * - Parameters:
     *   - response: Объект для валидации
     *   - type: Тип объекта
     * - Throws: ValidationError если валидация не пройдена
     */
    static func validate<T: Decodable>(_ response: T, type: T.Type) throws {
        let typeName = String(describing: type)

        #if DEBUG
        print("🛡️ APIResponseValidator: Валидация \(typeName)")
        #endif

        // Production логирование
        os_log("🛡️ Validating %{public}@", log: Self.validationLogger, type: .info, typeName)

        // Handle arrays (common for list endpoints like family members)
        if typeName.contains("Array<") || typeName.hasPrefix("[") {
            #if DEBUG
            print("🛡️ APIResponseValidator: Array type \(typeName) - skipping detailed validation (individual elements validated upstream)")
            #endif
            os_log("🛡️ Array type %{public}@ - validation skipped (elements handled individually)", log: Self.validationLogger, type: .info, typeName)
            // Success for arrays - no further validation needed here
        }
        // Handle specific responses that don't have dedicated validators yet
        else if let _ = response as? RecoveryCodeLoginResponse {
            #if DEBUG
            print("✅ RecoveryCodeLoginResponse validated (no complex fields)")
            #endif
            // Simple success - tokens already handled in business logic
        }
        else if let reconcile = response as? ReconcileFamilyResponse {
            try validateReconcileFamilyResponse(reconcile)
        }
        // Handle MetricsUploadResponse
        else if let metricsResponse = response as? MetricsUploadResponse {
            try validateMetricsUploadResponse(metricsResponse)
        }
        else {
            switch response {
            case let analytics as AnalyticsResponse:
                try validateAnalyticsResponse(analytics)
            case let familyMember as FamilyMemberResponse:
                try validateFamilyMemberResponse(familyMember)
            case let deviceDetail as DeviceDetailResponse:
                try validateDeviceDetailResponse(deviceDetail)
            case let protectionStats as ProtectionStatsResponse:
                try validateProtectionStatsResponse(protectionStats)
            case let familyChatMessage as FamilyChatMessageResponse:
                try validateFamilyChatMessageResponse(familyChatMessage)
            case let createFamily as CreateFamilyResponse:
                try validateCreateFamilyResponse(createFamily)
            case let familyStats as FamilyStatsResponse:
                try validateFamilyStatsResponse(familyStats)
            case let cancelSub as SubscriptionCancelResponse:
                try validateSubscriptionCancelResponse(cancelSub)
            case let jwtReg as JWTDeviceRegisterResponse:
                try validateJWTDeviceRegisterResponse(jwtReg)
            case let device as DeviceResponse:
                try validateDeviceResponse(device)
            case let eventsBatch as SubscriptionEventsBatchResponse:
                try validateSubscriptionEventsBatchResponse(eventsBatch)
            default:
                // Для неизвестных типов просто проверяем что объект не nil
                #if DEBUG
                print("⚠️ APIResponseValidator: Неизвестный тип \(typeName) - пропускаем валидацию")
                #endif
                os_log("⚠️ Unknown type %{public}@ - skipping validation", log: Self.validationLogger, type: .info, typeName)
                break
            }
        }

        #if DEBUG
        print("✅ APIResponseValidator: Валидация \(typeName) пройдена")
        #endif
    }

    // MARK: - Analytics Response Validation

    private static func validateAnalyticsResponse(_ response: AnalyticsResponse) throws {
        // Проверяем числовые значения
        guard response.threatsDetected >= 0 else {
            throw ValidationError.invalidValue(field: "threatsDetected", value: response.threatsDetected, reason: "должно быть >= 0")
        }

        guard response.threatsBlocked >= 0 else {
            throw ValidationError.invalidValue(field: "threatsBlocked", value: response.threatsBlocked, reason: "должно быть >= 0")
        }

        guard response.itemsScanned >= 0 else {
            throw ValidationError.invalidValue(field: "itemsScanned", value: response.itemsScanned, reason: "должно быть >= 0")
        }

        guard response.protectionLevel >= 0 && response.protectionLevel <= 100 else {
            throw ValidationError.invalidRange(field: "protectionLevel", value: response.protectionLevel, range: "0-100")
        }

        // Проверяем period
        let validPeriods = ["day", "week", "month", "year"]
        guard validPeriods.contains(response.period) else {
            throw ValidationError.invalidValue(field: "period", value: response.period, reason: "должен быть одним из: \(validPeriods.joined(separator: ", "))")
        }

        // Проверяем topThreats
        for threat in response.topThreats {
            guard threat.count >= 0 else {
                throw ValidationError.invalidValue(field: "topThreats[\(threat.id)].count", value: threat.count, reason: "должно быть >= 0")
            }

            let validSeverities = ["low", "medium", "high", "critical"]
            guard validSeverities.contains(threat.severity) else {
                throw ValidationError.invalidValue(field: "topThreats[\(threat.id)].severity", value: threat.severity, reason: "должен быть одним из: \(validSeverities.joined(separator: ", "))")
            }
        }

        // Проверяем threatsByType
        for threatType in response.threatsByType {
            guard threatType.count >= 0 else {
                throw ValidationError.invalidValue(field: "threatsByType[\(threatType.type)].count", value: threatType.count, reason: "должно быть >= 0")
            }
        }
    }

    // MARK: - Family Member Response Validation

    private static func validateFamilyMemberResponse(_ response: FamilyMemberResponse) throws {
        // Проверяем обязательные поля
        guard !response.id.isEmpty else {
            throw ValidationError.emptyField(field: "id")
        }

        guard !response.name.isEmpty else {
            throw ValidationError.emptyField(field: "name")
        }

        guard !response.role.isEmpty else {
            throw ValidationError.emptyField(field: "role")
        }

        // Проверяем числовые значения (с учётом опциональности)
        let threatsBlocked = response.threatsBlocked ?? 0
        guard threatsBlocked >= 0 else {
            throw ValidationError.invalidValue(field: "threatsBlocked", value: threatsBlocked, reason: "должно быть >= 0")
        }
        
        let devices = response.devices ?? 0
        guard devices >= 0 else {
            throw ValidationError.invalidValue(field: "devices", value: devices, reason: "должно быть >= 0")
        }

        // Проверяем допустимые значения enum
        let validRoles = ["parent", "child", "teenager", "elderly"]
        guard validRoles.contains(response.role) else {
            throw ValidationError.invalidValue(field: "role", value: response.role, reason: "должен быть одним из: \(validRoles.joined(separator: ", "))")
        }

        let validStatuses = ["protected", "warning", "danger", "offline"]
        if let status = response.status {
            guard validStatuses.contains(status) else {
                throw ValidationError.invalidValue(field: "status", value: status, reason: "должен быть одним из: \(validStatuses.joined(separator: ", "))")
            }
        }

        // Проверяем формат lastActive (должна быть валидная дата)
        if let lastActive = response.lastActive, !lastActive.isEmpty {
            let isoFormatter = ISO8601DateFormatter()
            if isoFormatter.date(from: lastActive) == nil {
                // Мягкий fallback: принимаем формат "HH:mm" без падения
                let timeFormatter = DateFormatter()
                timeFormatter.locale = Locale(identifier: "en_US_POSIX")
                timeFormatter.timeZone = TimeZone(secondsFromGMT: 0)
                timeFormatter.dateFormat = "HH:mm"
                
                if timeFormatter.date(from: lastActive) == nil {
                    // Не удалось распарсить ни как ISO8601, ни как HH:mm — не падаем, логируем предупреждение
                    os_log("⚠️ Validation warning: lastActive has non-standard format: %{public}@",
                           log: Self.validationLogger,
                           type: .error,
                           lastActive)
                    // Решение: не бросаем ошибку, чтобы не ломать UI; отображение берёт дефолт
                }
            }
        }
    }

    // MARK: - Device List / Add Response
    
    private static func validateDeviceResponse(_ response: DeviceResponse) throws {
        guard !response.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw ValidationError.emptyField(field: "id")
        }
        if response.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            #if DEBUG
            print("⚠️ DeviceResponse: пустое name (серверный объект допускает заглушку)")
            #endif
        }
        #if DEBUG
        print("✅ DeviceResponse validated: id=\(response.id.prefix(8))…")
        #endif
    }
    
    private static func validateSubscriptionEventsBatchResponse(_ response: SubscriptionEventsBatchResponse) throws {
        if response.success == false, (response.message?.isEmpty ?? true) {
            #if DEBUG
            print("⚠️ SubscriptionEventsBatchResponse: success=false без message (серверный ack)")
            #endif
            os_log("⚠️ Subscription events batch: success=false, empty message", log: Self.validationLogger, type: .info)
        }
        #if DEBUG
        print("✅ SubscriptionEventsBatchResponse validated")
        #endif
    }
    
    // MARK: - Device Detail Response Validation

    private static func validateDeviceDetailResponse(_ response: DeviceDetailResponse) throws {
        // Проверяем обязательные поля
        guard !response.id.isEmpty else {
            throw ValidationError.emptyField(field: "id")
        }

        guard !response.name.isEmpty else {
            throw ValidationError.emptyField(field: "name")
        }

        guard !response.owner.isEmpty else {
            throw ValidationError.emptyField(field: "owner")
        }

        // Проверяем числовые значения
        guard response.threatsBlocked >= 0 else {
            throw ValidationError.invalidValue(field: "threatsBlocked", value: response.threatsBlocked, reason: "должно быть >= 0")
        }

        guard response.dataUsage >= 0 else {
            throw ValidationError.invalidValue(field: "dataUsage", value: response.dataUsage, reason: "должно быть >= 0")
        }

        // Проверяем batteryLevel если он задан
        if let batteryLevel = response.batteryLevel {
            guard batteryLevel >= 0 && batteryLevel <= 100 else {
                throw ValidationError.invalidRange(field: "batteryLevel", value: batteryLevel, range: "0-100")
            }
        }

        // Проверяем допустимые значения
        let validStatuses = ["online", "offline", "warning", "danger", "protected"]
        guard validStatuses.contains(response.status) else {
            throw ValidationError.invalidValue(field: "status", value: response.status, reason: "должен быть одним из: \(validStatuses.joined(separator: ", "))")
        }

        let validTypes = ["iphone", "ipad", "mac", "android", "windows", "linux"]
        guard validTypes.contains(response.type.lowercased()) else {
            throw ValidationError.invalidValue(field: "type", value: response.type, reason: "должен быть одним из: \(validTypes.joined(separator: ", "))")
        }

        // Проверяем формат IP адреса если он задан
        if let ipAddress = response.ipAddress, !ipAddress.isEmpty {
            let ipRegex = "^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$"
            let ipPredicate = NSPredicate(format: "SELF MATCHES %@", ipRegex)
            guard ipPredicate.evaluate(with: ipAddress) else {
                throw ValidationError.invalidFormat(field: "ipAddress", value: ipAddress, expectedFormat: "IPv4 address (xxx.xxx.xxx.xxx)")
            }
        }
    }

    // MARK: - Protection Stats Response Validation

    private static func validateProtectionStatsResponse(_ response: ProtectionStatsResponse) throws {
        // Проверяем числовые значения
        guard response.functionsActive >= 0 else {
            throw ValidationError.invalidValue(field: "functionsActive", value: response.functionsActive, reason: "должно быть >= 0")
        }

        guard response.threatsBlocked >= 0 else {
            throw ValidationError.invalidValue(field: "threatsBlocked", value: response.threatsBlocked, reason: "должно быть >= 0")
        }

        guard response.securityScore >= 0 && response.securityScore <= 100 else {
            throw ValidationError.invalidRange(field: "securityScore", value: response.securityScore, range: "0-100")
        }

        // Проверяем protectionLevel
        let validLevels = ["basic", "standard", "premium", "maximum"]
        guard validLevels.contains(response.protectionLevel.lowercased()) else {
            throw ValidationError.invalidValue(field: "protectionLevel", value: response.protectionLevel, reason: "должен быть одним из: \(validLevels.joined(separator: ", "))")
        }

        // Проверяем activeComponents
        guard !response.activeComponents.isEmpty else {
            throw ValidationError.emptyField(field: "activeComponents")
        }

        // Проверяем lastScan (должна быть валидная дата)
        if !response.lastScan.isEmpty {
            let isoFormatter = ISO8601DateFormatter()
            guard isoFormatter.date(from: response.lastScan) != nil else {
                throw ValidationError.invalidFormat(field: "lastScan", value: response.lastScan, expectedFormat: "ISO 8601 date")
            }
        }

        // Проверяем recommendations (опционально)
        if let recommendations = response.recommendations {
            for recommendation in recommendations {
                guard !recommendation.isEmpty else {
                    throw ValidationError.invalidValue(field: "recommendations", value: "пустая строка", reason: "рекомендации не должны быть пустыми")
                }
            }
        }
    }

    // MARK: - Family Chat Message Response Validation

    private static func validateFamilyChatMessageResponse(_ response: FamilyChatMessageResponse) throws {
        // Проверяем обязательные поля
        guard !response.id.isEmpty else {
            throw ValidationError.emptyField(field: "id")
        }

        guard !response.sender.isEmpty else {
            throw ValidationError.emptyField(field: "sender")
        }

        guard !response.timestamp.isEmpty else {
            throw ValidationError.emptyField(field: "timestamp")
        }

        // Проверяем timestamp формат
        let isoFormatter = ISO8601DateFormatter()
        guard isoFormatter.date(from: response.timestamp) != nil else {
            throw ValidationError.invalidFormat(field: "timestamp", value: response.timestamp, expectedFormat: "ISO 8601 date")
        }

        // Проверяем messageType если задан
        if let messageType = response.messageType {
            let validTypes = ["text", "voice", "image", "video"]
            guard validTypes.contains(messageType) else {
                throw ValidationError.invalidValue(field: "messageType", value: messageType, reason: "должен быть одним из: \(validTypes.joined(separator: ", "))")
            }
        }

        // Проверяем readStatus если задан
        if let readStatus = response.readStatus {
            let validStatuses = ["sent", "delivered", "read"]
            guard validStatuses.contains(readStatus) else {
                throw ValidationError.invalidValue(field: "readStatus", value: readStatus, reason: "должен быть одним из: \(validStatuses.joined(separator: ", "))")
            }
        }

        // Проверяем voiceDuration если задано
        if let voiceDuration = response.voiceDuration {
            guard voiceDuration > 0 else {
                throw ValidationError.invalidValue(field: "voiceDuration", value: voiceDuration, reason: "должно быть > 0")
            }
        }

        // Проверяем URL поля
        if let voiceUrl = response.voiceUrl {
            guard isValidURL(voiceUrl) else {
                throw ValidationError.invalidFormat(field: "voiceUrl", value: voiceUrl, expectedFormat: "valid URL")
            }
        }

        if let mediaUrl = response.mediaUrl {
            guard isValidURL(mediaUrl) else {
                throw ValidationError.invalidFormat(field: "mediaUrl", value: mediaUrl, expectedFormat: "valid URL")
            }
        }
    }

    // MARK: - Create Family Response Validation

    private static func validateReconcileFamilyResponse(_ response: ReconcileFamilyResponse) throws {
        guard !response.familyId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw ValidationError.emptyField(field: "familyId")
        }
        guard response.total >= 0, response.invalidRoles >= 0, response.fixedStatuses >= 0 else {
            throw ValidationError.invalidValue(field: "reconcile_counts", value: response.total, reason: "counts must be >= 0")
        }
    }

    private static func validateCreateFamilyResponse(_ response: CreateFamilyResponse) throws {
        // ✅ ИСПРАВЛЕНО: Валидация обновлена для новой структуры CreateFamilyResponse
        
        // Проверяем обязательные поля
        guard !response.family_id.isEmpty else {
            throw ValidationError.emptyField(field: "family_id")
        }

        guard !response.short_code.isEmpty else {
            throw ValidationError.emptyField(field: "short_code")
        }

        guard !response.creator_member_id.isEmpty else {
            throw ValidationError.emptyField(field: "creator_member_id")
        }

        guard !response.qr_code_data.isEmpty else {
            throw ValidationError.emptyField(field: "qr_code_data")
        }

        guard !response.expires_at.isEmpty else {
            throw ValidationError.emptyField(field: "expires_at")
        }

        // ✅ Проверяем вычисляемые свойства
        guard !response.recovery_code.isEmpty else {
            throw ValidationError.emptyField(field: "recovery_code")
        }

        guard !response.your_member_id.isEmpty else {
            throw ValidationError.emptyField(field: "your_member_id")
        }

        // ✅ Проверяем members (теперь опциональное поле)
        if let members = response.members, !members.isEmpty {
            // Валидируем каждого члена семьи
            for member in members {
                try validateFamilyMemberResponse(member)
            }
        }
        // Если members отсутствует - это не ошибка (опциональное поле)
    }

    // MARK: - Metrics Upload Response Validation
    private static func validateMetricsUploadResponse(_ response: MetricsUploadResponse) throws {
        // Простая валидация ответа загрузки метрик
        guard response.success else {
            // Даже если success=false, не бросаем ошибку — просто логируем
            os_log("⚠️ Metrics upload reported success=false: %{public}@", 
                   log: Self.validationLogger, type: .info, response.message ?? "unknown")
            return
        }

        guard response.uploadedCount >= 0 else {
            throw ValidationError.invalidValue(field: "uploadedCount", 
                                             value: response.uploadedCount, 
                                             reason: "должно быть >= 0")
        }

        #if DEBUG
        print("✅ MetricsUploadResponse validated: success=\(response.success), uploaded=\(response.uploadedCount)")
        #endif
    }

    // MARK: - Family Stats
    
    private static func validateFamilyStatsResponse(_ response: FamilyStatsResponse) throws {
        guard response.totalMembers >= 0 else {
            throw ValidationError.invalidValue(field: "totalMembers", value: response.totalMembers, reason: "должно быть >= 0")
        }
        guard response.totalDevices >= 0 else {
            throw ValidationError.invalidValue(field: "totalDevices", value: response.totalDevices, reason: "должно быть >= 0")
        }
        guard response.totalThreats >= 0 else {
            throw ValidationError.invalidValue(field: "totalThreats", value: response.totalThreats, reason: "должно быть >= 0")
        }
        #if DEBUG
        print("✅ FamilyStatsResponse validated: members=\(response.totalMembers) devices=\(response.totalDevices)")
        #endif
    }
    
    // MARK: - Subscription / JWT
    
    private static func validateSubscriptionCancelResponse(_ response: SubscriptionCancelResponse) throws {
        let hasNewToken = !(response.newToken?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ?? true)
        if !response.success,
           (response.status?.isEmpty ?? true),
           (response.message?.isEmpty ?? true),
           !hasNewToken,
           response.subscription == nil {
            throw ValidationError.invalidValue(field: "success", value: response.success, reason: "ожидалось success, статус/сообщение, new_token или subscription от сервера")
        }
        #if DEBUG
        print("✅ SubscriptionCancelResponse validated: success=\(response.success)")
        #endif
    }
    
    private static func validateJWTDeviceRegisterResponse(_ response: JWTDeviceRegisterResponse) throws {
        guard !response.token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw ValidationError.emptyField(field: "token")
        }
        guard !response.deviceId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw ValidationError.emptyField(field: "deviceId")
        }
        #if DEBUG
        print("✅ JWTDeviceRegisterResponse validated (token length=\(response.token.count))")
        #endif
    }
    
    // MARK: - Helper Methods

    private static func isValidURL(_ string: String) -> Bool {
        guard let url = URL(string: string) else { return false }
        return url.scheme != nil && url.host != nil
    }
}

// MARK: - Validation Error

enum ValidationError: LocalizedError {
    case emptyField(field: String)
    case invalidValue(field: String, value: Any, reason: String)
    case invalidRange(field: String, value: Any, range: String)
    case invalidFormat(field: String, value: String, expectedFormat: String)

    var errorDescription: String? {
        switch self {
        case .emptyField(let field):
            return "Поле '\(field)' не может быть пустым"
        case .invalidValue(let field, let value, let reason):
            return "Неверное значение поля '\(field)': \(value). \(reason)"
        case .invalidRange(let field, let value, let range):
            return "Значение поля '\(field)': \(value) вне допустимого диапазона \(range)"
        case .invalidFormat(let field, let value, let expectedFormat):
            return "Неверный формат поля '\(field)': '\(value)'. Ожидается: \(expectedFormat)"
        }
    }

    var failureReason: String? {
        switch self {
        case .emptyField:
            return "Обязательное поле не заполнено"
        case .invalidValue:
            return "Получены некорректные данные от сервера"
        case .invalidRange:
            return "Значение выходит за допустимые границы"
        case .invalidFormat:
            return "Неверный формат данных"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .emptyField:
            return "Свяжитесь с поддержкой - проблема на стороне сервера"
        case .invalidValue, .invalidRange, .invalidFormat:
            return "Попробуйте обновить приложение или повторить запрос позже"
        }
    }
}