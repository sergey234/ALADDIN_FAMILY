import SwiftUI
import Foundation
import UserNotifications

// Master Logger for notifications logging
private let logger = MasterLogger.shared

/// 🔔 Notifications View Model
/// Логика для экрана уведомлений с интеграцией сервера
class NotificationsViewModel: ObservableObject {
    @Published var notifications: [AppNotification] = []
    @Published var unreadCount: Int = 0
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    @Published var lastSuccessfulSyncAt: Date? = nil

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
            var metadata = response.metadata ?? [:]
            if metadata["correlation_id"]?.isEmpty ?? true {
                metadata["correlation_id"] = response.resolvedCorrelationId
            }
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
            self.metadata = metadata
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

        var correlationId: String {
            if let metadataValue = metadata["correlation_id"], !metadataValue.isEmpty {
                return metadataValue
            }
            if let metadataValue = metadata["event_id"], !metadataValue.isEmpty {
                return metadataValue
            }
            return id
        }

        init(from persisted: NotificationManager.PersistedSecurityEvent) {
            self.id = persisted.id
            self.icon = "🛡️"
            self.title = persisted.title
            self.message = persisted.body
            self.timestamp = persisted.timestamp
            self.isRead = false
            self.kind = NotificationKind(from: persisted.type)
            self.priority = .high
            self.actionRequired = false
            self.actionURL = nil
            var metadata = persisted.metadata
            if metadata["correlation_id"]?.isEmpty ?? true {
                metadata["correlation_id"] = persisted.correlationId
            }
            self.metadata = metadata
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
        logger.business("Initializing NotificationsViewModel")
        self.service = service
    }

    static func makeDefaultService() -> NotificationsService {
        logger.business("Creating default notifications service")
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
        logger.business("Loading notifications (includeRead: \(includeRead))")
        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let envelope = try await service.fetchNotifications(includeRead: includeRead, limit: 100)
            let mapped = envelope.notifications.map(AppNotification.init)
            await MainActor.run {
                applyNotifications(mapped, unread: envelope.unreadCount)
                lastSuccessfulSyncAt = Date()
                if mapped.isEmpty {
                    MetricsService.shared.trackUserAction(
                        action: "security_notifications_anomaly",
                        parameters: [
                            "anomaly_code": "notifications_empty_payload",
                            "message": "Notifications API returned empty payload",
                            "severity": "warning",
                            "include_read": includeRead,
                            "unread_count": envelope.unreadCount
                        ]
                    )
                }
            }
        } catch {
            await MainActor.run {
                let persisted = self.notificationManager.loadPersistedSecurityEvents().map(AppNotification.init)
                if !persisted.isEmpty {
                    self.applyNotifications(persisted, unread: persisted.count)
                    MetricsService.shared.trackUserAction(
                        action: "security_notifications_anomaly",
                        parameters: [
                            "anomaly_code": "notifications_local_fallback_activated",
                            "message": "Loaded persisted local security events due to API failure",
                            "severity": "warning",
                            "fallback_count": persisted.count
                        ]
                    )
                }
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
        logger.business("Adding notification from push: \(notification.request.content.title)")
        let userInfo = notification.request.content.userInfo
        let title = notification.request.content.title
        let body = notification.request.content.body

        let notificationId = userInfo["notification_id"] as? String ?? UUID().uuidString
        let typeString = userInfo["type"] as? String ?? "info"
        let icon = userInfo["icon"] as? String ?? "🔔"
        let metadata: [String: String] = userInfo.reduce(into: [:]) { partial, pair in
            guard let key = pair.key as? String else { return }
            if let value = pair.value as? String {
                partial[key] = value
            } else if let value = pair.value as? NSNumber {
                partial[key] = value.stringValue
            }
        }

        let newNotification = AppNotification(
            id: notificationId,
            icon: icon,
            title: title,
            message: body,
            timestamp: Date(),
            isRead: false,
            kind: NotificationKind(from: typeString),
            metadata: metadata
        )

        await MainActor.run {
            if !notifications.contains(where: { $0.id == notificationId }) {
                // Push/local event ускоряет UX, но не является source-of-truth для истории.
                // Источник истины для экрана — backend /api/notifications.
                notifications.insert(newNotification, at: 0)
                updateUnreadCount()
            }
        }

        // Сразу синхронизируемся с сервером, чтобы список и счётчик опирались на backend store.
        await loadNotifications(includeRead: true)
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
        logger.business("Marking notification as read: \(notification.title)")
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
        let unreadCount = notifications.filter { !$0.isRead }.count
        logger.business("Marking all notifications as read (\(unreadCount) unread)")
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
        logger.business("Clearing all notifications (\(notifications.count) total)")
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
            actionURL: actionURL,
            correlationId: correlationId
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



