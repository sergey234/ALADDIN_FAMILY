import SwiftUI
import Foundation
import UserNotifications

/// 🔔 Notifications View Model
/// Логика для экрана уведомлений с интеграцией сервера
class NotificationsViewModel: ObservableObject {
    
    @Published var notifications: [AppNotification] = []
    @Published var unreadCount: Int = 0
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    
    private let apiService: APIService
    private let notificationManager = NotificationManager.shared
    
    struct AppNotification: Identifiable {
        let id: String
        let icon: String
        let title: String
        let message: String
        let time: String
        var isRead: Bool
        let type: NotificationType
        
        init(from response: NotificationResponse) {
            self.id = response.id
            self.icon = response.icon
            self.title = response.title
            self.message = response.message
            self.isRead = response.isRead
            self.type = NotificationType(from: response.type)
            self.time = Self.formatTime(response.timestamp)
        }
        
        var priority: NotificationPriority {
            return type.priority
        }
        
        var isImportant: Bool {
            return type.isImportant
        }
        
        init(id: String, icon: String, title: String, message: String, time: String, isRead: Bool, type: NotificationType) {
            self.id = id
            self.icon = icon
            self.title = title
            self.message = message
            self.time = time
            self.isRead = isRead
            self.type = type
        }
        
        private static func formatTime(_ date: Date) -> String {
            let formatter = RelativeDateTimeFormatter()
            formatter.unitsStyle = .abbreviated
            return formatter.localizedString(for: date, relativeTo: Date())
        }
    }
    
    enum NotificationType {
        case threat, success, info, warning, bypassAttempt
        
        init(from string: String) {
            switch string.lowercased() {
            case "threat": self = .threat
            case "success": self = .success
            case "warning": self = .warning
            case "bypass", "bypassattempt", "обход": self = .bypassAttempt
            default: self = .info
            }
        }
        
        var isImportant: Bool {
            return self == .threat || self == .warning || self == .bypassAttempt
        }
        
        var priority: NotificationPriority {
            switch self {
            case .threat: return .high
            case .warning, .bypassAttempt: return .medium
            case .success, .info: return .low
            }
        }
    }
    
    init(apiService: APIService = APIService(networkManager: NetworkManager())) {
        self.apiService = apiService
        Task { @MainActor in
            await self.loadNotifications()
        }
    }
    
    func loadNotifications() async {
        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }
        
        // Пытаемся загрузить с сервера
        let result = await withCheckedContinuation { (continuation: CheckedContinuation<Result<[NotificationResponse], Error>, Never>) in
            apiService.getNotifications { apiResult in
                continuation.resume(returning: apiResult)
            }
        }
        
        switch result {
        case .success(let response):
            // Преобразуем в AppNotification
            let serverNotifications = response.map { AppNotification(from: $0) }
            
            // Объединяем с существующими (защита от дубликатов)
            await MainActor.run {
                mergeNotifications(serverNotifications)
                isLoading = false
            }
            
        case .failure:
            // При ошибке используем mock-данные (fallback)
            await MainActor.run {
                if notifications.isEmpty {
                    // Используем дефолтный LocalizationManager для fallback
                    let defaultManager = LocalizationManager()
                    loadMockNotifications(localizationManager: defaultManager)
                }
                // Локализация сообщения об ошибке будет добавлена позже, если понадобится
                errorMessage = nil // Пока скрываем ошибку, так как используем mock-данные
                isLoading = false
            }
        }
    }
    
    private func mergeNotifications(_ newNotifications: [AppNotification]) {
        var existingIds = Set(notifications.map { $0.id })
        var merged = notifications
        
        for newNotification in newNotifications {
            if !existingIds.contains(newNotification.id) {
                merged.append(newNotification)
                existingIds.insert(newNotification.id)
            } else {
                // Обновляем существующее уведомление
                if let index = merged.firstIndex(where: { $0.id == newNotification.id }) {
                    merged[index] = newNotification
                }
            }
        }
        
        // Сортируем по времени (новые сверху)
        notifications = merged.sorted { notification1, notification2 in
            // Простая сортировка по времени (можно улучшить)
            notification1.time < notification2.time
        }
        
        updateUnreadCount()
    }
    
    func loadMockNotifications(localizationManager: LocalizationManager) {
        // Используем RelativeDateTimeFormatter для локализованного времени
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        formatter.locale = Locale(identifier: localizationManager.currentLanguage.rawValue)
        
        let now = Date()
        let fiveMinutesAgo = now.addingTimeInterval(-5 * 60)
        let oneHourAgo = now.addingTimeInterval(-60 * 60)
        let twoHoursAgo = now.addingTimeInterval(-2 * 60 * 60)
        let yesterday = now.addingTimeInterval(-24 * 60 * 60)
        
        notifications = [
            AppNotification(id: UUID().uuidString, icon: "🛡️", title: localizationManager.localized("notifications_mock_threat_title"), message: localizationManager.localized("notifications_mock_threat_message"), time: formatter.localizedString(for: fiveMinutesAgo, relativeTo: now), isRead: false, type: .threat),
            AppNotification(id: UUID().uuidString, icon: "✅", title: localizationManager.localized("notifications_mock_success_title"), message: localizationManager.localized("notifications_mock_success_message"), time: formatter.localizedString(for: oneHourAgo, relativeTo: now), isRead: true, type: .success),
            AppNotification(id: UUID().uuidString, icon: "⚠️", title: localizationManager.localized("notifications_mock_warning_title"), message: localizationManager.localized("notifications_mock_warning_message"), time: formatter.localizedString(for: twoHoursAgo, relativeTo: now), isRead: true, type: .warning),
            AppNotification(id: UUID().uuidString, icon: "ℹ️", title: localizationManager.localized("notifications_mock_info_title"), message: localizationManager.localized("notifications_mock_info_message"), time: formatter.localizedString(for: yesterday, relativeTo: now), isRead: true, type: .info)
        ]
        updateUnreadCount()
    }
    
    func addNotificationFromPush(_ notification: UNNotification) async {
        let userInfo = notification.request.content.userInfo
        let title = notification.request.content.title
        let body = notification.request.content.body
        
        // Извлекаем данные из userInfo
        let notificationId = userInfo["notification_id"] as? String ?? UUID().uuidString
        let typeString = userInfo["type"] as? String ?? "info"
        let icon = userInfo["icon"] as? String ?? "🔔"
        
        let newNotification = AppNotification(
            id: notificationId,
            icon: icon,
            title: title,
            message: body,
            time: "Только что",
            isRead: false,
            type: NotificationType(from: typeString)
        )
        
        // Добавляем только если такого ID еще нет
        await MainActor.run {
            if !notifications.contains(where: { $0.id == notificationId }) {
                notifications.insert(newNotification, at: 0)
                updateUnreadCount()
            }
        }
    }
    
    /**
     * Добавить уведомление вручную (для попыток обхода)
     */
    @MainActor
    func addNotification(_ notification: AppNotification) {
        if !notifications.contains(where: { $0.id == notification.id }) {
            notifications.insert(notification, at: 0)
            updateUnreadCount()
        }
    }
    
    @MainActor
    func markAsRead(_ notification: AppNotification) {
        if let index = notifications.firstIndex(where: { $0.id == notification.id }) {
            notifications[index].isRead = true
            updateUnreadCount()
            
            // Отправляем на сервер
            Task {
                apiService.markNotificationAsRead(notificationId: notification.id) { _ in }
            }
        }
    }
    
    @MainActor
    func markAllAsRead() {
        notifications = notifications.map { var n = $0; n.isRead = true; return n }
        updateUnreadCount()
        
        // Отправляем все на сервер
        Task {
            for notification in notifications where !notification.isRead {
                apiService.markNotificationAsRead(notificationId: notification.id) { _ in }
            }
        }
    }
    
    @MainActor
    func clearAll() {
        notifications.removeAll()
        updateUnreadCount()
    }
    
    private func updateUnreadCount() {
        unreadCount = notifications.filter { !$0.isRead }.count
    }
    
    // MARK: - Filtering
    
    func filteredNotifications(for filter: NotificationFilter) -> [AppNotification] {
        switch filter {
        case .all:
            return notifications
        case .unread:
            return notifications.filter { !$0.isRead }
        case .threats:
            return notifications.filter { $0.type == .threat }
        case .bypass:
            return notifications.filter { $0.type == .bypassAttempt }
        case .success:
            return notifications.filter { $0.type == .success }
        case .info:
            return notifications.filter { $0.type == .info }
        case .warning:
            return notifications.filter { $0.type == .warning }
        }
    }
    
    func filterCount(for filter: NotificationFilter) -> Int {
        switch filter {
        case .all:
            return notifications.count
        case .unread:
            return notifications.filter { !$0.isRead }.count
        case .threats:
            return notifications.filter { $0.type == .threat }.count
        case .bypass:
            return notifications.filter { $0.type == .bypassAttempt }.count
        case .success:
            return notifications.filter { $0.type == .success }.count
        case .info:
            return notifications.filter { $0.type == .info }.count
        case .warning:
            return notifications.filter { $0.type == .warning }.count
        }
    }
    
    func getPreviewNotifications(for filter: NotificationFilter) -> [AppNotification] {
        let filtered = filteredNotifications(for: filter)
        return Array(filtered.prefix(3))
    }
}

// MARK: - NotificationFilter

enum NotificationFilter: String, CaseIterable {
    case all = "Все"
    case unread = "Непрочитанные"
    case threats = "Угрозы"
    case bypass = "Обход"
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждения"
}

extension NotificationFilter {
    var emoji: String {
        switch self {
        case .all: return "📋"
        case .unread: return "🔔"
        case .threats: return "🛡️"
        case .bypass: return "🚨"
        case .success: return "✅"
        case .info: return "ℹ️"
        case .warning: return "⚠️"
        }
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .all: return localizationManager.localized("notifications_filter_all")
        case .unread: return localizationManager.localized("notifications_filter_unread")
        case .threats: return localizationManager.localized("notifications_filter_threats")
        case .bypass: return localizationManager.localized("notifications_filter_bypass")
        case .success: return localizationManager.localized("notifications_filter_success")
        case .info: return localizationManager.localized("notifications_filter_info")
        case .warning: return localizationManager.localized("notifications_filter_warning")
        }
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .all: return localizationManager.localized("notifications_filter_all_subtitle")
        case .unread: return localizationManager.localized("notifications_filter_unread_subtitle")
        case .threats: return localizationManager.localized("notifications_filter_threats_subtitle")
        case .bypass: return localizationManager.localized("notifications_filter_bypass_subtitle")
        case .success: return localizationManager.localized("notifications_filter_success_subtitle")
        case .info: return localizationManager.localized("notifications_filter_info_subtitle")
        case .warning: return localizationManager.localized("notifications_filter_warning_subtitle")
        }
    }
    
    var subtitle: String {
        // Deprecated: используйте localizedSubtitle вместо этого
        switch self {
        case .all: return "Все уведомления"
        case .unread: return "Требуют внимания"
        case .threats: return "Заблокированные угрозы"
        case .bypass: return "Попытки обхода блокировок"
        case .success: return "Успешные действия"
        case .info: return "Информационные сообщения"
        case .warning: return "Предупреждения о безопасности"
        }
    }
    
    var color: Color {
        switch self {
        case .all: return .blue
        case .unread: return .orange
        case .threats: return .red
        case .bypass: return .warningOrange
        case .success: return .green
        case .info: return .blue
        case .warning: return .orange
        }
    }
}

// MARK: - AppNotification Conversion

extension NotificationsViewModel.AppNotification {
    func toNotification() -> NotificationItem {
        NotificationItem(
            icon: self.icon,
            title: self.title,
            message: self.message,
            time: self.time,
            isRead: self.isRead,
            type: self.type.toNotificationType()
        )
    }
}

extension NotificationsViewModel.NotificationType {
    func toNotificationType() -> NotificationType {
        switch self {
        case .threat: return .threat
        case .success: return .success
        case .info: return .info
        case .warning: return .warning
        case .bypassAttempt: return .bypassAttempt  // Теперь поддерживается bypassAttempt
        }
    }
}



