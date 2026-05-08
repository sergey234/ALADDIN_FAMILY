import SwiftUI
import Foundation

/**
 * 🔔 Notification Models
 * Модели данных для уведомлений
 * Используются в NotificationsScreen и NotificationsViewModel
 */

// MARK: - Notification Item Model
// Переименован из Notification в NotificationItem для избежания конфликта с Foundation.Notification

struct NotificationItem: Identifiable {
    let id = UUID()
    let icon: String
    let title: String
    let message: String
    let time: String
    var isRead: Bool
    let type: NotificationType
    let correlationId: String?
    
    init(
        icon: String,
        title: String,
        message: String,
        time: String,
        isRead: Bool,
        type: NotificationType,
        correlationId: String? = nil
    ) {
        self.icon = icon
        self.title = title
        self.message = message
        self.time = time
        self.isRead = isRead
        self.type = type
        self.correlationId = correlationId
    }
}

// MARK: - Typealias for backward compatibility
typealias Notification = NotificationItem

// MARK: - Notification Type

enum NotificationType: String, CaseIterable {
    case threat = "Угроза"
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
    case bypassAttempt = "Обход"
    
    var color: Color {
        switch self {
        case .threat: return .red
        case .success: return .green
        case .info: return .blue
        case .warning: return .orange
        case .bypassAttempt: return .warningOrange
        }
    }
    
    // ✅ ЗАДАЧА 20: Локализованное название типа уведомления
    func localizedName() -> String {
        let localizationManager = LocalizationManager.shared
        switch self {
        case .threat:
            return localizationManager.localized("notification_type_threat")
        case .success:
            return localizationManager.localized("notification_type_success")
        case .info:
            return localizationManager.localized("notification_type_info")
        case .warning:
            return localizationManager.localized("notification_type_warning")
        case .bypassAttempt:
            return localizationManager.localized("notification_type_bypass")
        }
    }
    
    // ✅ ЗАДАЧА 20: Ключ локализации для типа
    var localizationKey: String {
        switch self {
        case .threat: return "notification_type_threat"
        case .success: return "notification_type_success"
        case .info: return "notification_type_info"
        case .warning: return "notification_type_warning"
        case .bypassAttempt: return "notification_type_bypass"
        }
    }
}

