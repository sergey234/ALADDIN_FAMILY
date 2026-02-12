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

    private let service: NotificationsService
    private let notificationManager = NotificationManager.shared

    private static let relativeFormatter: RelativeDateTimeFormatter = {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter
    }()

    static func relativeTime(for date: Date, reference: Date = Date()) -> String {
        relativeFormatter.localizedString(for: date, relativeTo: reference)
    }

    struct AppNotification: Identifiable {
        let id: String
        let icon: String
        let title: String
        let message: String
        let timestamp: Date
        var isRead: Bool
        let kind: NotificationKind
        let priority: NotificationPriority
        let actionRequired: Bool
        let actionURL: String?
        let metadata: [String: String]

        init(from response: NotificationResponse) {
            self.id = response.id
            self.icon = response.icon.isEmpty ? "🔔" : response.icon
            self.title = response.title
            self.message = response.message
            self.timestamp = response.timestamp
            self.isRead = response.isRead
            self.kind = NotificationKind(from: response.type)
            self.priority = response.defaultPriority
            self.actionRequired = response.actionRequired ?? false
            self.actionURL = response.actionUrl
            self.metadata = response.metadata ?? [:]
        }

        init(id: String,
             icon: String,
             title: String,
             message: String,
             timestamp: Date,
             isRead: Bool,
             kind: NotificationKind,
             priority: NotificationPriority = .low,
             actionRequired: Bool = false,
             actionURL: String? = nil,
             metadata: [String: String] = [:]) {
            self.id = id
            self.icon = icon
            self.title = title
            self.message = message
            self.timestamp = timestamp
            self.isRead = isRead
            self.kind = kind
            self.priority = priority
            self.actionRequired = actionRequired
            self.actionURL = actionURL
            self.metadata = metadata
        }

        var isImportant: Bool {
            kind == .threat || kind == .warning || kind == .bypassAttempt
        }
    }

    enum NotificationKind {
        case threat
        case success
        case info
        case warning
        case bypassAttempt

        init(from raw: String) {
            let value = raw.lowercased()
            switch value {
            case "threat", "security_alert", "threat_detected", "emergency":
                self = .threat
            case "warning", "system_update", "subscription_expiring", "subscription_expired":
                self = .warning
            case "bypass", "bypass_attempt", "bypassattempt", "attempt_bypass":
                self = .bypassAttempt
            case "success", "payment_success", "subscription_activated", "referral_reward":
                self = .success
            default:
                self = .info
            }
        }
    }

    init(service: NotificationsService = NotificationsViewModel.makeDefaultService()) {
        self.service = service
    }

    static func makeDefaultService() -> NotificationsService {
        let baseURL = URL(string: AppConfig.baseURL) ?? URL(string: "https://api.aladdin.family/api")!
        return RemoteNotificationsService(
            baseURL: baseURL,
            authTokenProvider: {
                if let token = KeychainManager.shared.loadString(forKey: .authToken) {
                    return token
                }
                return AppConfig.authToken
            }
        )
    }

    @MainActor
    private func applyNotifications(_ newNotifications: [AppNotification], unread: Int) {
        notifications = newNotifications.sorted { $0.timestamp > $1.timestamp }
        unreadCount = unread
        isLoading = false
    }

    func loadNotifications(includeRead: Bool = true) async {
        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let envelope = try await service.fetchNotifications(includeRead: includeRead, limit: 100)
            let mapped = envelope.notifications.map(AppNotification.init)
            await MainActor.run {
                applyNotifications(mapped, unread: envelope.unreadCount)
            }
        } catch {
            await MainActor.run {
                // ✅ ИСПРАВЛЕНО: Убран fallback на mock данные
                // При ошибке показываем только сообщение об ошибке
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    // ✅ ИСПРАВЛЕНО: Метод loadMockNotifications() удален
    // Теперь используются только реальные API вызовы через RemoteNotificationsService

    func addNotificationFromPush(_ notification: UNNotification) async {
        let userInfo = notification.request.content.userInfo
        let title = notification.request.content.title
        let body = notification.request.content.body

        let notificationId = userInfo["notification_id"] as? String ?? UUID().uuidString
        let typeString = userInfo["type"] as? String ?? "info"
        let icon = userInfo["icon"] as? String ?? "🔔"

        let newNotification = AppNotification(
            id: notificationId,
            icon: icon,
            title: title,
            message: body,
            timestamp: Date(),
            isRead: false,
            kind: NotificationKind(from: typeString)
        )

        await MainActor.run {
            if !notifications.contains(where: { $0.id == notificationId }) {
                notifications.insert(newNotification, at: 0)
                updateUnreadCount()
            }
        }
    }

    @MainActor
    func addNotification(_ notification: AppNotification) {
        if !notifications.contains(where: { $0.id == notification.id }) {
            notifications.insert(notification, at: 0)
            updateUnreadCount()
        }
    }

    @MainActor
    func markAsRead(_ notification: AppNotification) {
        guard let index = notifications.firstIndex(where: { $0.id == notification.id }) else { return }
        if notifications[index].isRead { return }

        notifications[index].isRead = true
        updateUnreadCount()

        let notificationId = notification.id
        Task {
            do {
                let unread = try await service.markNotificationAsRead(notificationId)
                await MainActor.run {
                    self.unreadCount = unread
                }
            } catch {
                await MainActor.run {
                    if let revertIndex = self.notifications.firstIndex(where: { $0.id == notificationId }) {
                        self.notifications[revertIndex].isRead = false
                        self.updateUnreadCount()
                    }
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }

    @MainActor
    func markAllAsRead() {
        let unreadIds = notifications.filter { !$0.isRead }.map { $0.id }
        guard !unreadIds.isEmpty else { return }

        notifications = notifications.map { var item = $0; item.isRead = true; return item }
        updateUnreadCount()

        Task {
            for id in unreadIds {
                do {
                    let unread = try await service.markNotificationAsRead(id)
                    await MainActor.run {
                        self.unreadCount = unread
                    }
                } catch {
                    await MainActor.run {
                        if let revertIndex = self.notifications.firstIndex(where: { $0.id == id }) {
                            self.notifications[revertIndex].isRead = false
                            self.updateUnreadCount()
                        }
                        self.errorMessage = error.localizedDescription
                    }
                }
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
            return notifications.filter { $0.kind == .threat }
        case .bypass:
            return notifications.filter { $0.kind == .bypassAttempt }
        case .success:
            return notifications.filter { $0.kind == .success }
        case .info:
            return notifications.filter { $0.kind == .info }
        case .warning:
            return notifications.filter { $0.kind == .warning }
        }
    }

    func filterCount(for filter: NotificationFilter) -> Int {
        switch filter {
        case .all:
            return notifications.count
        case .unread:
            return notifications.filter { !$0.isRead }.count
        case .threats:
            return notifications.filter { $0.kind == .threat }.count
        case .bypass:
            return notifications.filter { $0.kind == .bypassAttempt }.count
        case .success:
            return notifications.filter { $0.kind == .success }.count
        case .info:
            return notifications.filter { $0.kind == .info }.count
        case .warning:
            return notifications.filter { $0.kind == .warning }.count
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
            id: id,
            icon: icon,
            title: title,
            message: message,
            time: NotificationsViewModel.relativeTime(for: timestamp),
            isRead: isRead,
            type: kind.toNotificationType(),
            timestamp: timestamp,
            actionRequired: actionRequired,
            actionURL: actionURL
        )
    }
}

extension NotificationsViewModel.NotificationKind {
    func toNotificationType() -> NotificationType {
        switch self {
        case .threat: return .threat
        case .success: return .success
        case .info: return .info
        case .warning: return .warning
        case .bypassAttempt: return .bypassAttempt
        }
    }
}



