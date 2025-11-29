import SwiftUI

/// 🔧 Function Status
/// Статус функций устройства
enum FunctionStatus: String, Codable, CaseIterable {
    case protected = "protected"
    case warning = "warning"
    case danger = "danger"
    case inactive = "inactive"
    case active = "active"
    
    var color: Color {
        switch self {
        case .protected, .active:
            return .green
        case .warning:
            return .orange
        case .danger:
            return .red
        case .inactive:
            return .gray
        }
    }
    
    var displayName: String {
        switch self {
        case .protected:
            return "Защищено"
        case .warning:
            return "Предупреждение"
        case .danger:
            return "Опасность"
        case .inactive:
            return "Неактивно"
        case .active:
            return "Активно"
        }
    }
    
    var icon: String {
        switch self {
        case .protected, .active:
            return "checkmark.shield.fill"
        case .warning:
            return "exclamationmark.triangle.fill"
        case .danger:
            return "xmark.shield.fill"
        case .inactive:
            return "minus.circle.fill"
        }
    }
}
