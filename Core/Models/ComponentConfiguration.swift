import Foundation

/**
 * ⚙️ Component Configuration Model
 * Модель для хранения конфигурации компонента
 * Поддерживает разные типы настроек для разных компонентов
 */

struct ComponentConfiguration: Codable, Equatable {
    /// Базовые настройки (для всех компонентов)
    var isEnabled: Bool
    var priority: ComponentPriority
    
    /// Дополнительные настройки (JSON для гибкости)
    var additionalSettings: [String: AnyCodable]?
    
    /// Настройки для конкретных типов компонентов
    var messengerSettings: MessengerSettings?
    var monitoringSettings: MonitoringSettings?
    var emergencySettings: EmergencySettings?
    var privacySettings: PrivacySettings?
    
    init(
        isEnabled: Bool = false,
        priority: ComponentPriority = .normal,
        additionalSettings: [String: AnyCodable]? = nil,
        messengerSettings: MessengerSettings? = nil,
        monitoringSettings: MonitoringSettings? = nil,
        emergencySettings: EmergencySettings? = nil,
        privacySettings: PrivacySettings? = nil
    ) {
        self.isEnabled = isEnabled
        self.priority = priority
        self.additionalSettings = additionalSettings
        self.messengerSettings = messengerSettings
        self.monitoringSettings = monitoringSettings
        self.emergencySettings = emergencySettings
        self.privacySettings = privacySettings
    }
}

// MARK: - Component Priority

enum ComponentPriority: String, Codable, CaseIterable {
    case critical = "critical"
    case normal = "normal"
    case low = "low"
    
    var displayName: String {
        switch self {
        case .critical: return "Критичный"
        case .normal: return "Обычный"
        case .low: return "Низкий"
        }
    }
}

// MARK: - Messenger Settings

struct MessengerSettings: Codable, Equatable {
    var scanMessages: Bool
    var scanMedia: Bool
    var blockSuspicious: Bool
    var notifyOnThreat: Bool
    
    init(
        scanMessages: Bool = true,
        scanMedia: Bool = true,
        blockSuspicious: Bool = false,
        notifyOnThreat: Bool = true
    ) {
        self.scanMessages = scanMessages
        self.scanMedia = scanMedia
        self.blockSuspicious = blockSuspicious
        self.notifyOnThreat = notifyOnThreat
    }
}

// MARK: - Monitoring Settings

struct MonitoringSettings: Codable, Equatable {
    var checkFrequency: MonitoringFrequency
    var alertThreshold: Int
    var notifyOnDetection: Bool
    
    init(
        checkFrequency: MonitoringFrequency = .daily,
        alertThreshold: Int = 1,
        notifyOnDetection: Bool = true
    ) {
        self.checkFrequency = checkFrequency
        self.alertThreshold = alertThreshold
        self.notifyOnDetection = notifyOnDetection
    }
}

enum MonitoringFrequency: String, Codable, CaseIterable {
    case realtime = "realtime"
    case hourly = "hourly"
    case daily = "daily"
    case weekly = "weekly"
    
    var displayName: String {
        switch self {
        case .realtime: return "В реальном времени"
        case .hourly: return "Каждый час"
        case .daily: return "Ежедневно"
        case .weekly: return "Еженедельно"
        }
    }
}

// MARK: - Emergency Settings

struct EmergencySettings: Codable, Equatable {
    var autoCall: Bool
    var autoSMS: Bool
    var notifyContacts: [String]
    var responseTime: Int // секунды
    
    init(
        autoCall: Bool = false,
        autoSMS: Bool = true,
        notifyContacts: [String] = [],
        responseTime: Int = 30
    ) {
        self.autoCall = autoCall
        self.autoSMS = autoSMS
        self.notifyContacts = notifyContacts
        self.responseTime = responseTime
    }
}

// MARK: - Privacy Settings

struct PrivacySettings: Codable, Equatable {
    var hideLocation: Bool
    var anonymizeData: Bool
    var blockTrackers: Bool
    var clearHistory: Bool
    
    init(
        hideLocation: Bool = false,
        anonymizeData: Bool = false,
        blockTrackers: Bool = true,
        clearHistory: Bool = false
    ) {
        self.hideLocation = hideLocation
        self.anonymizeData = anonymizeData
        self.blockTrackers = blockTrackers
        self.clearHistory = clearHistory
    }
}

// MARK: - AnyCodable Helper

/// Helper для кодирования/декодирования Any значений
struct AnyCodable: Codable, Equatable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dictionary = try? container.decode([String: AnyCodable].self) {
            value = dictionary.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "AnyCodable value cannot be decoded")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodable($0) })
        case let dictionary as [String: Any]:
            try container.encode(dictionary.mapValues { AnyCodable($0) })
        default:
            // Fallback for types that might not be explicitly handled but are Codable
            if let encodable = value as? Encodable {
                try encodable.encode(to: encoder)
            } else {
                throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: container.codingPath, debugDescription: "AnyCodable value cannot be encoded"))
            }
        }
    }
    
    static func == (lhs: AnyCodable, rhs: AnyCodable) -> Bool {
        // Простое сравнение для базовых типов
        if let lhsBool = lhs.value as? Bool, let rhsBool = rhs.value as? Bool {
            return lhsBool == rhsBool
        }
        if let lhsInt = lhs.value as? Int, let rhsInt = rhs.value as? Int {
            return lhsInt == rhsInt
        }
        if let lhsDouble = lhs.value as? Double, let rhsDouble = rhs.value as? Double {
            return lhsDouble == rhsDouble
        }
        if let lhsString = lhs.value as? String, let rhsString = rhs.value as? String {
            return lhsString == rhsString
        }
        return false
    }
}

