import SwiftUI

/// 📱 Device Model
/// Модель устройства для экрана устройств
struct Device: Identifiable {
    let id = UUID()
    let name: String
    let owner: String
    let type: DeviceType
    let status: DeviceStatus
    let lastActive: String
}

enum DeviceType: String, CaseIterable {
    case iphone = "iphone"
    case mac = "mac"
    case ipad = "ipad"
    case android = "android"
    
    var icon: String {
        switch self {
        case .iphone: return "iphone"
        case .mac: return "laptopcomputer"
        case .ipad: return "ipad"
        case .android: return "phone"
        }
    }
    
    var displayName: String {
        switch self {
        case .iphone: return "iPhone"
        case .mac: return "Mac"
        case .ipad: return "iPad"
        case .android: return "Android"
        }
    }
}

enum DeviceStatus: String, CaseIterable {
    case protected = "protected"
    case warning = "warning"
    case danger = "danger"
    case inactive = "inactive"
    
    var color: Color {
        switch self {
        case .protected: return .green
        case .warning: return .orange
        case .danger: return .red
        case .inactive: return .gray
        }
    }
    
    var displayName: String {
        switch self {
        case .protected: return "Защищено"
        case .warning: return "Предупреждение"
        case .danger: return "Опасность"
        case .inactive: return "Неактивно"
        }
    }
}

/// 🔧 Function Status
/// Статус функции устройства
enum FunctionStatus: String, CaseIterable {
    case enabled = "enabled"
    case disabled = "disabled"
    case warning = "warning"
    
    var color: Color {
        switch self {
        case .enabled: return .green
        case .disabled: return .gray
        case .warning: return .orange
        }
    }
    
    var displayName: String {
        switch self {
        case .enabled: return "Включено"
        case .disabled: return "Отключено"
        case .warning: return "Предупреждение"
        }
    }
}
