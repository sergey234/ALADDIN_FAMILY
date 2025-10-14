import SwiftUI

/// 🔔 Notifications View Model
/// Логика для экрана уведомлений
class NotificationsViewModel: ObservableObject {
    
    @Published var notifications: [AppNotification] = []
    @Published var unreadCount: Int = 0
    
    struct AppNotification: Identifiable {
        let id = UUID()
        let icon: String
        let title: String
        let message: String
        let time: String
        var isRead: Bool
        let type: NotificationType
    }
    
    enum NotificationType {
        case threat, success, info, warning
    }
    
    init() {
        loadNotifications()
    }
    
    func loadNotifications() {
        notifications = [
            AppNotification(icon: "🛡️", title: "Угроза заблокирована", message: "Заблокирован вредоносный сайт", time: "5 мин назад", isRead: false, type: .threat),
            AppNotification(icon: "✅", title: "VPN подключён", message: "Ваше соединение защищено", time: "1 час назад", isRead: true, type: .success),
            AppNotification(icon: "⚠️", title: "Подозрительная активность", message: "Обнаружена попытка доступа", time: "2 часа назад", isRead: true, type: .warning),
            AppNotification(icon: "ℹ️", title: "Обновление доступно", message: "Доступна новая версия ALADDIN", time: "Вчера", isRead: true, type: .info)
        ]
        updateUnreadCount()
    }
    
    func markAsRead(_ notification: AppNotification) {
        if let index = notifications.firstIndex(where: { $0.id == notification.id }) {
            notifications[index].isRead = true
            updateUnreadCount()
        }
    }
    
    func markAllAsRead() {
        notifications = notifications.map { var n = $0; n.isRead = true; return n }
        updateUnreadCount()
    }
    
    private func updateUnreadCount() {
        unreadCount = notifications.filter { !$0.isRead }.count
    }
}



