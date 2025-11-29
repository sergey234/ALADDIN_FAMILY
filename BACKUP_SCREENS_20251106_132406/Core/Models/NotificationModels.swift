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
    
    init(icon: String, title: String, message: String, time: String, isRead: Bool, type: NotificationType) {
        self.icon = icon
        self.title = title
        self.message = message
        self.time = time
        self.isRead = isRead
        self.type = type
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
}

