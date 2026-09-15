import SwiftUI
import Foundation
import UserNotifications

// Master Logger for notifications logging
private let logger = MasterLogger.shared

/*
 Карта данных (экран Уведомления и связанные потоки) — int-1 / согласование с бэкендом:

 - Список уведомлений: `GET /api/notifications` (query `familyId`, `includeRead`, `limit`) через `RemoteNotificationsService`.
   Ответ: элементы с полями `type`, `metadata` (в т.ч. `correlation_id`), `timestamp`.
 - При успешном `GET /api/notifications`: список мержится с локальными `PersistedSecurityEvent` без дубликатов по `correlation_id` (int-4).
 - Локальный fallback только при ошибке API: `PersistedSecurityEvent` → те же `AppNotification`.
 - Главный экран / семья: агрегаты угроз и семейной защиты — `GET /api/parental-control/stats` и связанные экраны;
   подписи «угрозы» — про данные защиты устройств / CB, не про bypass и не сумма с Safari без пояснения.
 - int-15 / p1-1: тексты главная ↔ уведомления ↔ отчёты согласованы в `LocalizationManager` (`main_family_network_protection_*`,
   `notifications_statistics_subtitle`, `notifications_stat_threat_typed`, `reports_bypass_attempts_desc`, фильтр `notifications_filter_threats_subtitle`).
 - Обход (bypass): счётчики — `GET /api/parental/bypass/stats` + локальный журнал при офлайне;
   серверная запись событий — `POST /api/parental-control/monitoring/events` (kind/payload «bypass»)
   → `parental_bypass_stats` + in-app уведомление (`bypass_attempt`).
 - Мониторинг/отчёты РК: `GET /api/parental-control/monitoring/detail`, отчёты — `/reports/daily` и т.д.;
   Safari Content Blocker — отдельный контур телеметрии, не смешивать с метрикой обхода.
*/

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
        relativeFormatter.locale = LocalizationManager.shared.locale
        return relativeFormatter.localizedString(for: date, relativeTo: reference)
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
        /// Original API / local event type (`antivirus_scan_complete`, `threat_blocked`, …).
        let rawType: String

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
            self.rawType = response.type
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
             metadata: [String: String] = [:],
             rawType: String = "") {
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
            self.rawType = rawType.isEmpty ? Self.inferredRawType(kind: kind, title: title) : rawType
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
            self.rawType = persisted.type
        }

        func localizedTitle(_ localizationManager: LocalizationManager) -> String {
            NotificationCopyLocalizer.localizedTitle(
                rawType: rawType,
                bakedTitle: title,
                metadata: metadata,
                localizationManager: localizationManager
            )
        }

        func localizedMessage(_ localizationManager: LocalizationManager) -> String {
            NotificationCopyLocalizer.localizedMessage(
                rawType: rawType,
                bakedMessage: message,
                metadata: metadata,
                localizationManager: localizationManager
            )
        }

        private static func inferredRawType(kind: NotificationKind, title: String) -> String {
            switch kind {
            case .threat: return "threat"
            case .warning: return "warning"
            case .bypassAttempt: return "bypass_attempt"
            case .success: return "success"
            case .info: return "info"
            }
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
            case "threat", "security_alert", "threat_detected", "threat_blocked",
                 "emergency", "antivirus_scan_complete", "antivirus_scan_failed",
                 "downloaded_file_threat", "suspicious_activity", "qa_threat":
                self = .threat
            case "warning", "system_update", "subscription_expiring", "subscription_expired":
                self = .warning
            case "bypass", "bypass_attempt", "bypassattempt", "attempt_bypass":
                self = .bypassAttempt
            case "success", "payment_success", "subscription_activated", "referral_reward", "upgrade_success":
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

    /// int-4: после успешной синхронизации добавляем офлайн-события, если их `correlation_id` ещё нет в ответе API.
    internal static func mergeRemoteNotificationsWithPersistedLocal(
        remote: [AppNotification],
        persisted: [AppNotification]
    ) -> [AppNotification] {
        var seenCorrelation = Set<String>()
        for n in remote {
            let key = n.correlationId.trimmingCharacters(in: .whitespacesAndNewlines)
            if !key.isEmpty { seenCorrelation.insert(key) }
        }
        var merged = remote
        for p in persisted {
            let key = p.correlationId.trimmingCharacters(in: .whitespacesAndNewlines)
            if !key.isEmpty, seenCorrelation.contains(key) { continue }
            if !key.isEmpty { seenCorrelation.insert(key) }
            merged.append(p)
        }
        return merged.sorted { $0.timestamp > $1.timestamp }
    }

    func loadNotifications(includeRead: Bool = true) async {
        logger.business("Loading notifications (includeRead: \(includeRead))")
        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let envelope = try await service.fetchNotifications(includeRead: includeRead, limit: 100)
            let remoteMapped = envelope.notifications.map(AppNotification.init)
            let persistedMapped = notificationManager.loadPersistedSecurityEvents().map(AppNotification.init)
            let merged = Self.mergeRemoteNotificationsWithPersistedLocal(remote: remoteMapped, persisted: persistedMapped)
            let mergedUnread = merged.filter { !$0.isRead }.count
            await MainActor.run {
                applyNotifications(merged, unread: mergedUnread)
                lastSuccessfulSyncAt = Date()
                if remoteMapped.isEmpty {
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
        case .threats: return "Уведомления с типом «угроза»"
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
    func toNotification(localizationManager: LocalizationManager = .shared) -> NotificationItem {
        NotificationItem(
            id: id,
            icon: icon,
            title: localizedTitle(localizationManager),
            message: localizedMessage(localizationManager),
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




/// Remaps baked server/local RU (or EN) notification copy to LocalizationManager keys at display time.
enum NotificationCopyLocalizer {
    static func localizedTitle(
        rawType: String,
        bakedTitle: String,
        metadata: [String: String],
        localizationManager: LocalizationManager = .shared
    ) -> String {
        if let key = titleKey(forRawType: rawType) {
            return localizationManager.localized(key)
        }
        if let key = titleKey(forBakedTitle: bakedTitle) {
            return localizationManager.localized(key)
        }
        return bakedTitle
    }

    static func localizedMessage(
        rawType: String,
        bakedMessage: String,
        metadata: [String: String],
        localizationManager: LocalizationManager = .shared
    ) -> String {
        let type = rawType.lowercased()
        switch type {
        case "antivirus_scan_complete":
            let n = Int(metadata["threats_found"] ?? "") ?? 0
            return n > 0
                ? String(format: localizationManager.localized("push_antivirus_complete_body_threats"), n)
                : localizationManager.localized("push_antivirus_complete_body_clean")
        case "antivirus_scan_failed":
            return localizationManager.localized("push_antivirus_failed_body")
        case "downloaded_file_threat":
            let name = metadata["file_name"] ?? extractQuotedFileName(from: bakedMessage) ?? "file"
            return String(format: localizationManager.localized("push_downloaded_file_threat_body"), name)
        case "threat_blocked":
            return remappedOrBaked(
                bakedMessage,
                localizationManager: localizationManager,
                knownBodies: [
                    ("Заблокирован", "push_threat_blocked_body"),
                ]
            )
        case "threat_detected", "security_alert", "threat":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        case "suspicious_activity":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        case "bypass_attempt", "bypass":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        default:
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                // Format bodies that need a count extracted from baked RU text.
                if key == "push_antivirus_complete_body_threats",
                   let n = firstInt(in: bakedMessage) {
                    return String(format: localizationManager.localized(key), n)
                }
                if key == "push_downloaded_file_threat_body",
                   let name = extractQuotedFileName(from: bakedMessage) {
                    return String(format: localizationManager.localized(key), name)
                }
                let localized = localizationManager.localized(key)
                return localized.contains("%") ? bakedMessage : localized
            }
            return bakedMessage
        }
    }

    private static func firstInt(in text: String) -> Int? {
        let digits = text.compactMap { $0.isNumber ? $0 : nil }
        // Prefer first contiguous number
        if let match = text.range(of: #"\d+"#, options: .regularExpression) {
            return Int(text[match])
        }
        _ = digits
        return nil
    }

    private static func titleKey(forRawType rawType: String) -> String? {
        switch rawType.lowercased() {
        case "threat_blocked": return "push_threat_blocked_title"
        case "threat_detected", "security_alert": return "push_threat_detected_title"
        case "suspicious_activity": return "push_suspicious_activity_title"
        case "bypass_attempt", "bypass": return "push_bypass_attempt_title"
        case "family_member_added": return "push_family_member_added_title"
        case "antivirus_scan_complete": return "push_antivirus_complete_title"
        case "antivirus_scan_failed": return "push_antivirus_failed_title"
        case "downloaded_file_threat": return "push_downloaded_file_threat_title"
        case "crash_detection": return "push_crash_detection_title"
        case "iot_device_compromised": return "push_iot_compromised_title"
        case "upgrade_success", "subscription_activated": return "push_upgrade_success_title"
        case "subscription_expired": return "push_subscription_expired_now_title"
        case "ai_message": return "push_ai_assistant_title"
        case "qa_threat": return "push_qa_threat_title"
        default: return nil
        }
    }

    private static func titleKey(forBakedTitle title: String) -> String? {
        let t = title.trimmingCharacters(in: .whitespacesAndNewlines)
        let map: [String: String] = [
            "🛡️ Угроза заблокирована": "push_threat_blocked_title",
            "Угроза заблокирована": "push_threat_blocked_title",
            "🛡️ Обнаружена угроза": "push_threat_detected_title",
            "Угроза обнаружена": "push_threat_detected_title",
            "⚠️ Подозрительная активность": "push_suspicious_activity_title",
            "Подозрительная активность": "push_suspicious_activity_title",
            "🚨 Попытка обхода": "push_bypass_attempt_title",
            "Попытка обхода": "push_bypass_attempt_title",
            "👨‍👩‍👧‍👦 Новый член семьи": "push_family_member_added_title",
            "Новый член семьи": "push_family_member_added_title",
            "Антивирусное сканирование завершено": "push_antivirus_complete_title",
            "Antivirus scan complete": "push_antivirus_complete_title",
            "Ошибка антивирусного сканирования": "push_antivirus_failed_title",
            "Antivirus scan failed": "push_antivirus_failed_title",
            "Подозрительный файл обнаружен": "push_downloaded_file_threat_title",
            "Suspicious file detected": "push_downloaded_file_threat_title",
            "🚨 Авария обнаружена": "push_crash_detection_title",
            "⚠️ Устройство скомпрометировано": "push_iot_compromised_title",
            "🎉 Поздравляем!": "push_upgrade_success_title",
            "Подписка закончилась": "push_subscription_expired_now_title",
            "🤖 AI Помощник": "push_ai_assistant_title",
            "🧪 Тестовая угроза (QA)": "push_qa_threat_title",
            // Smoke matrix labels (settings screen)
            "Антивирус: скан OK/угрозы": "push_antivirus_complete_title",
            "Антивирус: ошибка скана": "push_antivirus_failed_title",
            "Подозрительный файл": "push_downloaded_file_threat_title",
        ]
        return map[t]
    }

    private static func bodyKey(forBakedMessage message: String) -> String? {
        let m = message.trimmingCharacters(in: .whitespacesAndNewlines)
        let exact: [String: String] = [
            "Угроз не обнаружено. Система в безопасности.": "push_antivirus_complete_body_clean",
            "No threats found. Your system is safe.": "push_antivirus_complete_body_clean",
            "Не удалось выполнить сканирование. Проверьте подключение к интернету.": "push_antivirus_failed_body",
            "Could not complete the scan. Check your internet connection.": "push_antivirus_failed_body",
            "Проверьте ситуацию и при необходимости вызовите экстренные службы": "push_crash_detection_body",
            "Ваша подписка успешно активирована! Теперь доступны все функции защиты.": "push_upgrade_success_body",
            "Сценарий smoke-test: проверка цепочки detect -> notifications UI": "push_qa_threat_body",
        ]
        if let key = exact[m] { return key }
        if m.hasPrefix("Обнаружено ") && m.contains("угроз") {
            return "push_antivirus_complete_body_threats"
        }
        if m.hasPrefix("Found ") && m.contains("threat") {
            return "push_antivirus_complete_body_threats"
        }
        if m.contains("может содержать угрозу") || m.contains("may contain a threat") {
            return "push_downloaded_file_threat_body"
        }
        return nil
    }

    private static func remappedOrBaked(
        _ baked: String,
        localizationManager: LocalizationManager,
        knownBodies: [(String, String)]
    ) -> String {
        for (needle, key) in knownBodies where baked.contains(needle) {
            return localizationManager.localized(key)
        }
        return baked
    }

    private static func extractQuotedFileName(from message: String) -> String? {
        if let r1 = message.range(of: #"'(.*?)'"#, options: .regularExpression) {
            return String(message[r1]).trimmingCharacters(in: CharacterSet(charactersIn: "'"))
        }
        if let r2 = message.range(of: #""(.*?)""#, options: .regularExpression) {
            return String(message[r2]).trimmingCharacters(in: CharacterSet(charactersIn: "\""))
        }
        return nil
    }
}
