import Foundation
import UserNotifications
import UIKit

// Master Logger for notification logging
private let logger = MasterLogger.shared

/**
 * 🔔 Notification Manager
 * Управление push и локальными уведомлениями
 * Интеграция с сервером для отправки уведомлений
 * ✅ ИСПРАВЛЕНО: Вернулись к подходу из бэкапа (без @MainActor, синхронная инициализация)
 */

class NotificationManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = NotificationManager()
    
    // MARK: - Published Properties
    
    @Published var isAuthorized: Bool = false
    @Published var deviceToken: String?
    @Published var notificationSettings: NotificationSettings = NotificationSettings()
    @Published var pendingRequestsCount: Int = 0
    @Published var deliveredNotificationsCount: Int = 0
    
    // Callback для добавления уведомления в список экрана
    var onNotificationReceived: ((UNNotification) -> Void)?
    
    // Трекинг частоты уведомлений
    private var notificationHistory: [(date: Date, count: Int)] = []
    private let historyCleanupInterval: TimeInterval = 3600 // 1 час
    
    // MARK: - Private Properties
    
    private let notificationCenter = UNUserNotificationCenter.current()
    private let userDefaults = UserDefaults.standard
    private let settingsKey = "notificationSettings"
    private let persistedSecurityEventsKey = "persistedSecurityEventsV1"
    private let persistedSecurityEventsMaxCount = 200
    private let persistedSecurityEventsMaxAge: TimeInterval = 7 * 24 * 60 * 60
    private var didRequestAuthorizationThisSession = false
    
    // MARK: - Init
    
    private override init() {
        super.init()
        // ВРЕМЕННО ОТКЛЮЧЕНО: logger.business("Initializing NotificationManager")
        print("🔔 Initializing NotificationManager")
        notificationCenter.delegate = self
        // ✅ ИСПРАВЛЕНО: Синхронная инициализация (как в бэкапах - работало)
        checkAuthorizationStatus()
        loadSettings()
        setupNotificationCategories()
        // ВРЕМЕННО ОТКЛЮЧЕНО: logger.business("NotificationManager initialized successfully")
        print("✅ NotificationManager initialized successfully")
    }
    
    // MARK: - Authorization
    
    /**
     * Запросить разрешение на уведомления
     */
    func requestAuthorization() async -> Bool {
        // ВРЕМЕННО ОТКЛЮЧЕНО: logger.business("Requesting notification authorization from user")
        print("🔔 Requesting notification authorization from user")
        didRequestAuthorizationThisSession = true
        do {
            let granted = try await notificationCenter.requestAuthorization(
                options: [.alert, .badge, .sound, .provisional]
            )
            
            await MainActor.run {
                self.isAuthorized = granted
            }
            
            if granted {
                await registerForRemoteNotifications()
            }
            
            return granted
        } catch {
            print("❌ Notification authorization error: \(error)")
            return false
        }
    }

    /// Запрашивает разрешение только если статус `.notDetermined` и ещё не спрашивали в этой сессии.
    func requestAuthorizationIfNeeded() async -> Bool {
        let settings = await notificationCenter.notificationSettings()
        let status = settings.authorizationStatus
        let alreadyAuthorized = status == .authorized || status == .provisional
        await MainActor.run {
            self.isAuthorized = alreadyAuthorized
        }
        if status != .notDetermined {
            didRequestAuthorizationThisSession = true
            if alreadyAuthorized {
                await registerForRemoteNotifications()
            }
            return alreadyAuthorized
        }
        guard !didRequestAuthorizationThisSession else {
            return isAuthorized
        }
        return await requestAuthorization()
    }
    
    /**
     * Проверить статус авторизации
     */
    private func checkAuthorizationStatus() {
        notificationCenter.getNotificationSettings { settings in
            // ✅ ИСПРАВЛЕНО: Обновляем СРАЗУ (callback уже на main thread)
            DispatchQueue.main.async {
                self.isAuthorized = settings.authorizationStatus == .authorized
            }
        }
    }

    var delegateOwnerLabel: String {
        "NotificationManager"
    }

    /// Обновляет runtime-диагностику пайплайна уведомлений.
    func refreshRuntimeDiagnostics() {
        notificationCenter.getPendingNotificationRequests { requests in
            DispatchQueue.main.async {
                self.pendingRequestsCount = requests.count
            }
        }
        notificationCenter.getDeliveredNotifications { notifications in
            DispatchQueue.main.async {
                self.deliveredNotificationsCount = notifications.count
            }
        }
    }
    
    // MARK: - Remote Notifications
    
    /**
     * Регистрация для удаленных уведомлений
     */
    private func registerForRemoteNotifications() async {
        await MainActor.run {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }
    
    /**
     * Обработка успешной регистрации токена
     */
    func didRegisterForRemoteNotifications(deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        self.deviceToken = token
        
        // Отправить токен на сервер
        Task {
            await sendDeviceTokenToServer(token: token)
        }
    }
    
    /**
     * Обработка ошибки регистрации
     */
    func didFailToRegisterForRemoteNotifications(error: Error) {
        print("❌ Failed to register for remote notifications: \(error)")
    }
    
    // MARK: - Server Integration
    
    /**
     * Отправить токен устройства на сервер
     */
    private func sendDeviceTokenToServer(token: String) async {
        logger.business("Sending device token to server: \(token.prefix(8))...")
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            Task { @MainActor in
                APIService.shared.registerDeviceToken(token) { result in
                    #if DEBUG
                    print("📱 Register device token result: \(result)")
                    #endif
                    APIService.shared.antifakeRegisterFamilyPushToken(token) { antifakeResult in
                        #if DEBUG
                        print("📱 Antifake family push token: \(antifakeResult)")
                        #endif
                    }
                    continuation.resume()
                }
            }
        }
    }
    
    // MARK: - Local Notifications
    
    /**
     * Отправить локальное уведомление
     * ✅ nonisolated: может вызываться из любого потока
     */
    nonisolated func sendLocalNotification(
        title: String,
        body: String,
        category: NotificationCategory = .general,
        userInfo: [String: Any] = [:],
        delay: TimeInterval = 0,
        sound: UNNotificationSound = .default,
        badge: NSNumber? = nil,
        identifier: String? = nil
    ) {
        let notificationType = userInfo["type"] as? String ?? ""
        let notificationCenter = UNUserNotificationCenter.current()
        // iOS requires UNTimeIntervalNotificationTrigger interval > 0 (assert / EXC_BAD_ACCESS at 0).
        let safeDelay = max(delay, 0.15)
        
        // ✅ Проверяем настройки на main thread асинхронно
        Task { @MainActor in
            // Проверка для уведомлений о попытках обхода (локальные события используют bypass_attempt)
            if (notificationType == "bypass" || notificationType == "bypass_attempt")
                && !NotificationManager.shared.notificationSettings.bypassEnabled {
                print("🔕 Уведомление о попытке обхода пропущено (отключено в настройках)")
                return
            }

            let settings = NotificationManager.shared.notificationSettings
            if !Self.isCategoryEnabled(category, settings: settings) {
                print("🔕 Уведомление категории \(category.rawValue) пропущено (выключено в настройках)")
                return
            }
            
            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = sound
            content.categoryIdentifier = category.rawValue
            content.userInfo = userInfo
            if let badge {
                content.badge = badge
            }

            // Persist security events locally to survive temporary backend/API failures.
            self.persistSecurityEventIfNeeded(title: title, body: body, category: category, userInfo: userInfo)
            
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: safeDelay, repeats: false)
            let request = UNNotificationRequest(
                identifier: identifier ?? UUID().uuidString,
                content: content,
                trigger: trigger
            )
            
            notificationCenter.add(request) { error in
                if let error = error {
                    print("❌ Failed to send local notification: \(error)")
                } else {
                    print("✅ Local notification sent: \(title)")
                }
            }
        }
    }

    /**
     * Schedule a local notification (calendar / interval trigger) through the same
     * category + bypass gates as immediate sends. Presentation filters still apply
     * in willPresent when the app is foreground.
     */
    nonisolated func scheduleLocalNotification(
        identifier: String,
        title: String,
        body: String,
        category: NotificationCategory = .general,
        userInfo: [String: Any] = [:],
        trigger: UNNotificationTrigger,
        sound: UNNotificationSound = .default,
        badge: NSNumber? = nil
    ) {
        let notificationType = userInfo["type"] as? String ?? ""
        let notificationCenter = UNUserNotificationCenter.current()

        Task { @MainActor in
            if (notificationType == "bypass" || notificationType == "bypass_attempt")
                && !NotificationManager.shared.notificationSettings.bypassEnabled {
                print("🔕 Scheduled bypass notification skipped (disabled)")
                return
            }

            let settings = NotificationManager.shared.notificationSettings
            if !Self.isCategoryEnabled(category, settings: settings) {
                print("🔕 Scheduled \(category.rawValue) skipped (category off)")
                return
            }

            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = sound
            content.categoryIdentifier = category.rawValue
            content.userInfo = userInfo
            if let badge {
                content.badge = badge
            }

            let request = UNNotificationRequest(
                identifier: identifier,
                content: content,
                trigger: trigger
            )
            notificationCenter.add(request) { error in
                if let error = error {
                    print("❌ Failed to schedule local notification: \(error)")
                } else {
                    print("✅ Local notification scheduled: \(identifier)")
                }
            }
        }
    }

    /// Category master toggles from Notification Settings.
    private static func isCategoryEnabled(_ category: NotificationCategory, settings: NotificationSettings) -> Bool {
        switch category {
        case .security:
            return settings.securityEnabled
        case .family:
            return settings.familyEnabled
        case .networkProtection:
            return settings.networkProtectionEnabled
        case .ai:
            return settings.aiEnabled
        case .general, .subscription, .trial, .mnemo, .familyHabit:
            return true
        }
    }

    // MARK: - Local security event persistence

    struct PersistedSecurityEvent: Codable {
        let id: String
        let title: String
        let body: String
        let type: String
        let timestamp: Date
        let correlationId: String
        let metadata: [String: String]
    }

    func loadPersistedSecurityEvents() -> [PersistedSecurityEvent] {
        guard let data = userDefaults.data(forKey: persistedSecurityEventsKey) else {
            return []
        }
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let events = try decoder.decode([PersistedSecurityEvent].self, from: data)
            let now = Date()
            return events
                .filter { now.timeIntervalSince($0.timestamp) <= persistedSecurityEventsMaxAge }
                .sorted { $0.timestamp > $1.timestamp }
        } catch {
            print("❌ Failed to decode persisted security events: \(error)")
            return []
        }
    }

    func clearPersistedSecurityEvents() {
        userDefaults.removeObject(forKey: persistedSecurityEventsKey)
    }

    private func persistSecurityEventIfNeeded(
        title: String,
        body: String,
        category: NotificationCategory,
        userInfo: [String: Any]
    ) {
        guard category == .security else { return }
        let type = (userInfo["type"] as? String ?? "security_alert").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !type.isEmpty else { return }

        let correlationId = (userInfo["correlation_id"] as? String)
            ?? (userInfo["event_id"] as? String)
            ?? "local-\(UUID().uuidString)"
        let normalizedCorrelation = correlationId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalizedCorrelation.isEmpty else { return }

        let metadata = userInfo.reduce(into: [String: String]()) { partial, pair in
            guard let key = pair.key as? String else { return }
            if let value = pair.value as? String {
                partial[key] = value
            } else if let value = pair.value as? NSNumber {
                partial[key] = value.stringValue
            }
        }

        var events = loadPersistedSecurityEvents()
        if events.contains(where: { $0.correlationId == normalizedCorrelation }) {
            return
        }

        let event = PersistedSecurityEvent(
            id: UUID().uuidString,
            title: title,
            body: body,
            type: type,
            timestamp: Date(),
            correlationId: normalizedCorrelation,
            metadata: metadata
        )
        events.insert(event, at: 0)
        if events.count > persistedSecurityEventsMaxCount {
            events = Array(events.prefix(persistedSecurityEventsMaxCount))
        }

        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            let data = try encoder.encode(events)
            userDefaults.set(data, forKey: persistedSecurityEventsKey)
        } catch {
            print("❌ Failed to persist security event: \(error)")
        }
    }
    
    // MARK: - Predefined Notifications
    
    /**
     * Уведомление о блокировке угрозы
     */
    func sendThreatBlockedNotification(threatType: String, url: String) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_threat_blocked_title"),
            body: String(format: L.localized("push_threat_blocked_body"), threatType, url),
            category: .security,
            userInfo: [
                "type": "threat_blocked",
                "threat_type": threatType,
                "url": url
            ]
        )
    }
    
    /**
     * Уведомление о подключении Network Protection
     * Deprecated for user notifications matrix — ALADDIN product push set does not include VPN/NP.
     * Kept for legacy call sites only; do not add to smoke/QA.
     */
    func sendNetworkProtectionConnectedNotification(server: String) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_network_protection_connected_title"),
            body: String(format: L.localized("push_network_protection_connected_body"), server),
            category: .networkProtection,
            userInfo: [
                "type": "network_protection_connected",
                "server": server
            ]
        )
    }
    
    /**
     * Уведомление о добавлении члена семьи
     */
    func sendFamilyMemberAddedNotification(memberName: String) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_family_member_added_title"),
            body: String(format: L.localized("push_family_member_added_body"), memberName),
            category: .family,
            userInfo: [
                "type": "family_member_added",
                "member_name": memberName
            ]
        )
    }
    
    /**
     * Уведомление о подозрительной активности
     */
    func sendSuspiciousActivityNotification(activity: String) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_suspicious_activity_title"),
            body: String(format: L.localized("push_suspicious_activity_body"), activity),
            category: .security,
            userInfo: [
                "type": "suspicious_activity",
                "activity": activity
            ]
        )
    }
    
    /**
     * Уведомление о новом сообщении от AI
     */
    func sendAIMessageNotification(message: String) {
        sendLocalNotification(
            title: LocalizationManager.shared.localized("push_ai_assistant_title"),
            body: message,
            category: .ai,
            userInfo: [
                "type": "ai_message",
                "message": message
            ]
        )
    }

    /**
     * 🔥 Уведомление об успешном upgrade из trial в платную подписку
     */
    func showUpgradeSuccessNotification() {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_upgrade_success_title"),
            body: L.localized("push_upgrade_success_body"),
            category: .general,
            userInfo: [
                "type": "upgrade_success",
                "action": "subscription_activated"
            ]
        )
    }

    /// Soft smoke for parents — general category, no fake threat.
    func sendSoftTestNotification() {
        sendLocalNotification(
            title: LocalizationManager.shared.localized("notification_help_test_title"),
            body: LocalizationManager.shared.localized("notification_help_test_body"),
            category: .general,
            userInfo: [
                "type": "soft_test",
                "source": "notification_settings_help"
            ],
            delay: 1
        )
    }

    /// QA smoke scenario: принудительно создаёт тестовую угрозу
    /// для проверки цепочки отображения уведомлений на устройстве.
    func sendQATestThreatNotification() {
        let L = LocalizationManager.shared
        let correlationId = "qa-threat-\(UUID().uuidString)"
        sendLocalNotification(
            title: L.localized("push_qa_threat_title"),
            body: L.localized("push_qa_threat_body"),
            category: .security,
            userInfo: [
                "type": "threat_detected",
                "priority": "high",
                "correlation_id": correlationId,
                "event_id": correlationId,
                "source": "qa_forced_scenario"
            ]
        )
    }

    // MARK: - Product send paths (single channel)

    /// Family chat local banner — same filters/delay as all other product locals.
    func sendFamilyChatNotification(message: String, sender: String, familyId: String?) {
        sendLocalNotification(
            title: String(
                format: LocalizationManager.shared.localized("family_chat_notification_new_message"),
                sender
            ),
            body: message,
            category: .family,
            userInfo: [
                "type": "family_chat",
                "familyId": familyId ?? "",
                "sender": sender
            ],
            delay: 0.2,
            badge: 1
        )
    }

    func sendAntivirusScanCompleteNotification(threatsFound: Int) {
        let L = LocalizationManager.shared
        let hasThreats = threatsFound > 0
        sendLocalNotification(
            title: L.localized("push_antivirus_complete_title"),
            body: hasThreats
                ? String(format: L.localized("push_antivirus_complete_body_threats"), threatsFound)
                : L.localized("push_antivirus_complete_body_clean"),
            category: .security,
            userInfo: [
                "type": "antivirus_scan_complete",
                "threats_found": threatsFound,
                "priority": hasThreats ? "high" : "normal",
                "correlation_id": "scan-complete-\(UUID().uuidString)"
            ],
            delay: 0.2,
            sound: hasThreats ? .defaultCritical : .default,
            badge: hasThreats ? 1 : 0
        )
    }

    func sendAntivirusScanFailedNotification() {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_antivirus_failed_title"),
            body: L.localized("push_antivirus_failed_body"),
            category: .security,
            userInfo: [
                "type": "antivirus_scan_failed",
                "correlation_id": "scan-failed-\(UUID().uuidString)"
            ],
            delay: 0.2
        )
    }

    func sendDownloadedFileThreatNotification(fileName: String) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_downloaded_file_threat_title"),
            body: String(format: L.localized("push_downloaded_file_threat_body"), fileName),
            category: .security,
            userInfo: [
                "type": "downloaded_file_threat",
                "file_name": fileName,
                "priority": "high",
                "correlation_id": "download-threat-\(UUID().uuidString)"
            ],
            delay: 0.2,
            sound: .defaultCritical
        )
    }

    func sendCrashDetectionNotification() {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_crash_detection_title"),
            body: L.localized("push_crash_detection_body"),
            category: .general,
            userInfo: [
                "type": "crash_detection",
                "priority": "high",
                "correlation_id": "crash-\(UUID().uuidString)"
            ],
            delay: 0.2,
            sound: .defaultCritical
        )
    }

    func sendAntifakePostCallNotification() {
        sendLocalNotification(
            title: LocalizationManager.shared.localized("antifake_post_call_title"),
            body: LocalizationManager.shared.localized("antifake_post_call_body"),
            category: .general,
            userInfo: [
                "type": "antifake_post_call",
                "deepLink": "aladdin://antifake/call-check"
            ],
            delay: 1.5,
            identifier: "antifake_post_call_\(UUID().uuidString)"
        )
    }
    
    // MARK: - Notification Categories
    
    func setupNotificationCategories() {
        let L = LocalizationManager.shared
        let generalCategory = UNNotificationCategory(
            identifier: NotificationCategory.general.rawValue,
            actions: [],
            intentIdentifiers: [],
            options: []
        )
        
        let securityCategory = UNNotificationCategory(
            identifier: NotificationCategory.security.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "view_details",
                    title: L.localized("notif_action_view_details"),
                    options: [.foreground]
                ),
                UNNotificationAction(
                    identifier: "dismiss",
                    title: L.localized("notif_action_dismiss"),
                    options: []
                )
            ],
            intentIdentifiers: [],
            options: []
        )
        
        let familyCategory = UNNotificationCategory(
            identifier: NotificationCategory.family.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "view_family",
                    title: L.localized("notif_action_open_family"),
                    options: [.foreground]
                )
            ],
            intentIdentifiers: [],
            options: []
        )
        
        let networkProtectionCategory = UNNotificationCategory(
            identifier: NotificationCategory.networkProtection.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "view_network_protection",
                    title: L.localized("notif_action_open_network_protection"),
                    options: [.foreground]
                )
            ],
            intentIdentifiers: [],
            options: []
        )
        
        let aiCategory = UNNotificationCategory(
            identifier: NotificationCategory.ai.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "reply",
                    title: L.localized("notif_action_reply"),
                    options: [.foreground]
                )
            ],
            intentIdentifiers: [],
            options: []
        )
        
        let subscriptionCategory = UNNotificationCategory(
            identifier: NotificationCategory.subscription.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "view_tariffs",
                    title: L.localized("notif_action_renew"),
                    options: [.foreground]
                ),
                UNNotificationAction(
                    identifier: "dismiss",
                    title: L.localized("notif_action_dismiss"),
                    options: []
                )
            ],
            intentIdentifiers: [],
            options: []
        )

        let mnemoCategory = UNNotificationCategory(
            identifier: NotificationCategory.mnemo.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "open_mnemo_review",
                    title: L.localized("notif_action_retry"),
                    options: [.foreground]
                )
            ],
            intentIdentifiers: [],
            options: []
        )

        let habitDoneTitle = L.localized("family_habit_done")
        let familyHabitCategory = FamilyHabitRemindersScheduler.makeNotificationCategory(
            doneTitle: habitDoneTitle
        )
        
        notificationCenter.setNotificationCategories([
            generalCategory,
            securityCategory,
            familyCategory,
            networkProtectionCategory,
            aiCategory,
            subscriptionCategory,
            mnemoCategory,
            familyHabitCategory
        ])
    }
    
    // MARK: - Settings
    
    /**
     * Обновить настройки уведомлений
     */
    func updateNotificationSettings(_ settings: NotificationSettings) {
        self.notificationSettings = settings
        saveSettings()
        
        // Применить настройки
        Task {
            await applyNotificationSettings(settings)
        }
    }
    
    private func applyNotificationSettings(_ settings: NotificationSettings) async {
        // Настройки уже применены через @Published var notificationSettings
        // Все режимы проверяются в real-time в willPresent
        print("📱 Notification settings applied: \(settings)")
    }
    
    // MARK: - Settings Persistence
    
    /**
     * Сохранить настройки в UserDefaults
     * ✅ Публичный метод для сохранения настроек извне
     */
    func saveSettings() {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(notificationSettings)
            userDefaults.set(data, forKey: settingsKey)
            userDefaults.synchronize()
            print("✅ Notification settings saved")
        } catch {
            print("❌ Failed to save notification settings: \(error)")
        }
    }
    
    /**
     * Загрузить настройки из UserDefaults
     * ✅ ИСПРАВЛЕНО: Синхронная установка (как в бэкапах - работало)
     */
    private func loadSettings() {
        #if DEBUG
        print("🔴 NOTIFICATION_MANAGER: loadSettings() начат")
        #endif
        guard let data = userDefaults.data(forKey: settingsKey) else {
            // Используем настройки по умолчанию
            notificationSettings = NotificationSettings()
            #if DEBUG
            print("🔴 NOTIFICATION_MANAGER: loadSettings() - используем настройки по умолчанию")
            #endif
            return
        }
        
        do {
            let decoder = JSONDecoder()
            let settings = try decoder.decode(NotificationSettings.self, from: data)
            notificationSettings = settings
            print("✅ Notification settings loaded")
            #if DEBUG
            print("🔴 NOTIFICATION_MANAGER: loadSettings() завершен, notificationSettings = \(notificationSettings)")
            #endif
        } catch {
            print("❌ Failed to load notification settings: \(error), using defaults")
            notificationSettings = NotificationSettings()
            #if DEBUG
            print("🔴 NOTIFICATION_MANAGER: loadSettings() - ошибка, используем настройки по умолчанию")
            #endif
        }
    }
    
    // MARK: - Notification Frequency Tracking
    
    /**
     * Записывает отправку уведомления для отслеживания частоты
     */
    private func recordNotificationSent() {
        let now = Date()
        
        // Очищаем старые записи (старше часа)
        notificationHistory = notificationHistory.filter { now.timeIntervalSince($0.date) < historyCleanupInterval }
        
        // Добавляем текущую запись
        if let lastEntry = notificationHistory.last, Calendar.current.isDate(lastEntry.date, inSameDayAs: now) {
            // Увеличиваем счетчик для текущего часа
            let hour = Calendar.current.component(.hour, from: now)
            let lastHour = Calendar.current.component(.hour, from: lastEntry.date)
            if hour == lastHour {
                notificationHistory[notificationHistory.count - 1] = (date: now, count: lastEntry.count + 1)
            } else {
                notificationHistory.append((date: now, count: 1))
            }
        } else {
            notificationHistory.append((date: now, count: 1))
        }
    }
    
    /**
     * Подсчитывает количество уведомлений за последний час
     */
    private func countNotificationsInLastHour() -> Int {
        let now = Date()
        let oneHourAgo = now.addingTimeInterval(-3600)
        
        return notificationHistory
            .filter { $0.date >= oneHourAgo }
            .reduce(0) { $0 + $1.count }
    }
    
    // MARK: - Subscription / Trial dojim (retention)

    /// Deep link → тарифы (CTA «Продлить»). Без VPN-текстов.
    static let tariffsDeepLink = "aladdin://tariffs"

    /**
     * Dojim платной подписки (по духу бота, без VPN):
     * −3 / −1 / день 0 / +1 / +3. Одно окно = один id.
     */
    func scheduleRenewalNotifications(subscriptionEndDate: Date) {
        cancelRenewalNotifications()

        let L = LocalizationManager.shared
        let endDay = Calendar.current.startOfDay(for: subscriptionEndDate)
        let windows: [(Int, String, String, String, String)] = [
            (-3, "before.3", "subscription_renewal",
             L.localized("dojim_sub_before_3_title"),
             L.localized("dojim_sub_before_3_body")),
            (-1, "before.1", "subscription_renewal",
             L.localized("dojim_sub_before_1_title"),
             L.localized("dojim_sub_before_1_body")),
            (0, "expired.0", "subscription_expired",
             L.localized("dojim_sub_expired_0_title"),
             L.localized("dojim_sub_expired_0_body")),
            (1, "expired.1", "subscription_expired",
             L.localized("dojim_sub_expired_1_title"),
             L.localized("dojim_sub_expired_1_body")),
            (3, "expired.3", "subscription_expired",
             L.localized("dojim_sub_expired_3_title"),
             L.localized("dojim_sub_expired_3_body")),
        ]

        for (offset, suffix, type, title, body) in windows {
            guard let day = Calendar.current.date(byAdding: .day, value: offset, to: endDay) else { continue }
            let fire = Self.dojimFireDate(on: day, fallbackInstant: subscriptionEndDate, offsetDays: offset)
            scheduleDojimCalendarNotification(
                identifier: "dojim.subscription.\(suffix)",
                fireDate: fire,
                title: title,
                body: body,
                category: .subscription,
                type: type,
                extra: [
                    "days_offset": offset,
                    "subscription_end_date": ISO8601DateFormatter().string(from: subscriptionEndDate),
                    "source": "subscription_dojim_p1",
                ]
            )
        }

        print("✅ Dojim подписки: −3/−1/0/+1/+3 от \(subscriptionEndDate)")
    }

    /**
     * Trial dojim: −7 / −3 / −1 / день 0 / +1 / +3.
     */
    func scheduleTrialNotifications(trialEndDate: Date) {
        cancelTrialNotifications()

        let L = LocalizationManager.shared
        let endDay = Calendar.current.startOfDay(for: trialEndDate)
        let windows: [(Int, String, String, String, String)] = [
            (-7, "before.7", "trial",
             L.localized("dojim_trial_before_7_title"),
             L.localized("dojim_trial_before_7_body")),
            (-3, "before.3", "trial",
             L.localized("dojim_trial_before_3_title"),
             L.localized("dojim_trial_before_3_body")),
            (-1, "before.1", "trial",
             L.localized("dojim_trial_before_1_title"),
             L.localized("dojim_trial_before_1_body")),
            (0, "expired.0", "trial_expired",
             L.localized("dojim_trial_expired_0_title"),
             L.localized("dojim_trial_expired_0_body")),
            (1, "expired.1", "trial_expired",
             L.localized("dojim_trial_expired_1_title"),
             L.localized("dojim_trial_expired_1_body")),
            (3, "expired.3", "trial_expired",
             L.localized("dojim_trial_expired_3_title"),
             L.localized("dojim_trial_expired_3_body")),
        ]

        for (offset, suffix, type, title, body) in windows {
            guard let day = Calendar.current.date(byAdding: .day, value: offset, to: endDay) else { continue }
            let fire = Self.dojimFireDate(on: day, fallbackInstant: trialEndDate, offsetDays: offset)
            scheduleDojimCalendarNotification(
                identifier: "dojim.trial.\(suffix)",
                fireDate: fire,
                title: title,
                body: body,
                category: .trial,
                type: type,
                extra: [
                    "days_offset": offset,
                    "trial_end_date": ISO8601DateFormatter().string(from: trialEndDate),
                    "source": "trial_dojim_p1",
                ]
            )
        }

        print("✅ Dojim trial: −7/−3/−1/0/+1/+3 от \(trialEndDate)")
    }

    /// Немедленный баннер «уже истекла» + перепланирование хвоста +1/+3.
    func sendSubscriptionExpiredBanner(planName: String, endDate: Date) {
        let L = LocalizationManager.shared
        sendLocalNotification(
            title: L.localized("push_subscription_expired_now_title"),
            body: String(format: L.localized("push_subscription_expired_now_body"), planName),
            category: .subscription,
            userInfo: [
                "type": "subscription_expired",
                "days_offset": 0,
                "deepLink": Self.tariffsDeepLink,
                "source": "subscription_expired_now",
            ],
            delay: 0.2
        )
        scheduleRenewalNotifications(subscriptionEndDate: endDate)
    }

    func cancelRenewalNotifications() {
        removePendingDojim(prefix: "dojim.subscription.")
        notificationCenter.getPendingNotificationRequests { requests in
            let legacy = requests
                .filter { ($0.content.userInfo["type"] as? String) == "subscription_renewal" }
                .map(\.identifier)
            if !legacy.isEmpty {
                self.notificationCenter.removePendingNotificationRequests(withIdentifiers: legacy)
            }
        }
    }

    func cancelTrialNotifications() {
        removePendingDojim(prefix: "dojim.trial.")
        notificationCenter.getPendingNotificationRequests { requests in
            let legacy = requests
                .filter {
                    let t = $0.content.userInfo["type"] as? String
                    return t == "trial" || t == "trial_expired"
                }
                .map(\.identifier)
            if !legacy.isEmpty {
                self.notificationCenter.removePendingNotificationRequests(withIdentifiers: legacy)
            }
        }
    }

    private func removePendingDojim(prefix: String) {
        notificationCenter.getPendingNotificationRequests { requests in
            let ids = requests.map(\.identifier).filter { $0.hasPrefix(prefix) }
            if !ids.isEmpty {
                self.notificationCenter.removePendingNotificationRequests(withIdentifiers: ids)
                print("🔔 Dojim cancelled prefix=\(prefix) count=\(ids.count)")
            }
        }
    }

    /// 10:00 local; for day 0 if morning passed, use end instant if still future.
    private static func dojimFireDate(on day: Date, fallbackInstant: Date, offsetDays: Int) -> Date {
        let morning = Calendar.current.date(bySettingHour: 10, minute: 0, second: 0, of: day) ?? day
        let now = Date()
        if morning > now { return morning }
        if offsetDays == 0, fallbackInstant > now { return fallbackInstant }
        return morning
    }

    private func scheduleDojimCalendarNotification(
        identifier: String,
        fireDate: Date,
        title: String,
        body: String,
        category: NotificationCategory,
        type: String,
        extra: [String: Any]
    ) {
        guard fireDate > Date().addingTimeInterval(30) else { return }

        var userInfo = extra
        userInfo["type"] = type
        userInfo["deepLink"] = Self.tariffsDeepLink

        let comps = Calendar.current.dateComponents(
            [.year, .month, .day, .hour, .minute],
            from: fireDate
        )
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
        scheduleLocalNotification(
            identifier: identifier,
            title: title,
            body: body,
            category: category,
            userInfo: userInfo,
            trigger: trigger
        )
    }

}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {

    /// Читает/пишет `notificationSettings` и связанное состояние — вызывать **только с main thread**.
    private func foregroundPresentationOptions(for notification: UNNotification, now: Date) -> UNNotificationPresentationOptions {
        let userInfo = notification.request.content.userInfo
        let notificationType = userInfo["type"] as? String ?? "info"

        // Проверяем режим "Не беспокоить"
        let isSmoke = Self.isSmokeOrQaUserInfo(userInfo)
        if notificationSettings.doNotDisturbMode && !isSmoke {
            if let until = notificationSettings.doNotDisturbUntil {
                if now < until {
                    return []
                }
                // Until elapsed — clear DND automatically.
                notificationSettings.doNotDisturbMode = false
                notificationSettings.doNotDisturbUntil = nil
                saveSettings()
            } else {
                // DND on without until date still mutes banners (UI may omit until).
                return []
            }
        }

        // Проверяем режим "Только важные"
        if notificationSettings.importantOnlyMode && !isSmoke {
            let isImportant = Self.isImportantNotificationType(notificationType)
            if !isImportant {
                Task { @MainActor in
                    self.onNotificationReceived?(notification)
                }
                return [.badge]
            }
        }

        // Проверяем приоритет
        if notificationSettings.highPriorityOnly && !isSmoke {
            let priorityString = userInfo["priority"] as? String
            let priority = priorityString != nil ? NotificationPriority(from: priorityString!) : NotificationPriority.high
            if priority != .high {
                Task { @MainActor in
                    self.onNotificationReceived?(notification)
                }
                return [.badge]
            }
        }

        // Проверяем частоту уведомлений
        // Exact match for “only ~10 banners”: default cap is often 10/hour — smoke must not be clipped.
        if !isSmoke, let maxPerHour = notificationSettings.maxNotificationsPerHour {
            let notificationsInLastHour = countNotificationsInLastHour()
            if notificationsInLastHour >= maxPerHour {
                print("🔕 Rate limit: \(notificationsInLastHour)/\(maxPerHour) — banner suppressed for type=\(notificationType)")
                return []
            }
        }

        if !isSmoke {
            recordNotificationSent()
        }

        let currentHour = Calendar.current.component(.hour, from: now)
        let quietStart = Int(notificationSettings.quietHoursStart.split(separator: ":").first ?? "22") ?? 22
        let quietEnd = Int(notificationSettings.quietHoursEnd.split(separator: ":").first ?? "8") ?? 8
        let inQuietWindow = currentHour >= quietStart || currentHour < quietEnd
        // Quiet hours toggle OR legacy quiet mode both mute banners in the window.
        let isQuietHours = !isSmoke
            && (notificationSettings.quietHoursEnabled || notificationSettings.quietModeEnabled)
            && inQuietWindow

        Task { @MainActor in
            self.onNotificationReceived?(notification)
        }

        if isQuietHours {
            return [.badge]
        } else {
            return notificationSettings.soundEnabled ? [.banner, .sound, .badge] : [.banner, .badge]
        }
    }

    /// Soft-test / QA / smoke-matrix must always be allowed to present banners.
    private static func isSmokeOrQaUserInfo(_ userInfo: [AnyHashable: Any]) -> Bool {
        let source = (userInfo["source"] as? String) ?? ""
        if source == "notification_smoke_matrix"
            || source == "notification_settings_help"
            || source == "qa_forced_scenario"
            || source == "wind_down_test" {
            return true
        }
        let type = (userInfo["type"] as? String) ?? ""
        return type == "soft_test"
    }

    /// Clears hourly frequency counters (call before smoke fire-all).
    func resetNotificationFrequencyHistory() {
        notificationHistory.removeAll()
        print("🔔 Notification frequency history cleared (smoke)")
    }

    /// Types that still show a banner when «Important only» is on.
    private static func isImportantNotificationType(_ type: String) -> Bool {
        switch type {
        case "threat",
             "warning",
             "bypass",
             "bypass_attempt",
             "threat_detected",
             "threat_blocked",
             "suspicious_activity",
             "iot_device_compromised",
             "antivirus_scan_complete",
             "antivirus_scan_failed",
             "downloaded_file_threat",
             "crash_detection":
            return true
        default:
            return false
        }
    }
    
    /**
     * Обработка уведомления когда приложение в foreground
     * ✅ nonisolated: методы делегата могут вызываться на любом потоке (в т.ч. на main — iOS 18+ / сцены).
     * ⚠️ Никогда не вызывать `DispatchQueue.main.sync`, уже находясь на main — мгновенный deadlock (SIGTRAP libdispatch).
     */
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let now = Date()
        let options: UNNotificationPresentationOptions
        if Thread.isMainThread {
            options = self.foregroundPresentationOptions(for: notification, now: now)
        } else {
            options = DispatchQueue.main.sync {
                self.foregroundPresentationOptions(for: notification, now: now)
            }
        }

        completionHandler(options)

        processRemoteBypassMonitoringIngestIfNeeded(notification)
    }

    /// int-3: APNs → echo `POST …/monitoring/events` на JWT текущего профиля (ребёнок ок, родитель — тихий отказ API).
    private func processRemoteBypassMonitoringIngestIfNeeded(_ notification: UNNotification) {
        guard notification.request.trigger is UNPushNotificationTrigger else { return }
        let userInfo = notification.request.content.userInfo
        Task { @MainActor in
            ParentalControlManager.shared.ingestBypassMonitoringFromPushUserInfo(userInfo)
        }
    }
    
    /**
     * Обработка нажатия на уведомление
     * ✅ nonisolated: методы делегата могут вызываться не на main thread
     */
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        processRemoteBypassMonitoringIngestIfNeeded(response.notification)

        let userInfo = response.notification.request.content.userInfo
        
        // ✅ Обработка действий на main thread
        Task { @MainActor in
            // Обработка действий
            switch response.actionIdentifier {
            case "view_details":
                self.handleViewDetailsAction(userInfo: userInfo)
            case "view_family":
                self.handleViewFamilyAction(userInfo: userInfo)
            case "view_network_protection":
                self.handleViewNetworkProtectionAction(userInfo: userInfo)
            case "reply":
                self.handleReplyAction(userInfo: userInfo)
            case FamilyHabitRemindersScheduler.doneActionIdentifier:
                self.handleFamilyHabitDoneAction(userInfo: userInfo)
            default:
                self.handleDefaultAction(userInfo: userInfo)
            }
        }
        
        completionHandler()
    }
    
    private func handleViewDetailsAction(userInfo: [AnyHashable: Any]) {
        // TODO: Навигация к деталям угрозы
        print("🔍 View details action triggered")
    }
    
    private func handleViewFamilyAction(userInfo: [AnyHashable: Any]) {
        // TODO: Навигация к экрану семьи
        print("👨‍👩‍👧‍👦 View family action triggered")
    }
    
    private func handleViewNetworkProtectionAction(userInfo: [AnyHashable: Any]) {
        // TODO: Навигация к экрану Network Protection
        print("🔒 View Network Protection action triggered")
    }
    
    private func handleReplyAction(userInfo: [AnyHashable: Any]) {
        // TODO: Навигация к AI помощнику
        print("🤖 Reply action triggered")
    }

    private func handleFamilyHabitDoneAction(userInfo: [AnyHashable: Any]) {
        let preset = (userInfo["preset"] as? String)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard !preset.isEmpty else { return }
        Task {
            let result = await FamilyHabitRemindersScheduler.shared.handleDone(presetRaw: preset)
            if result.applied {
                HapticFeedback.notification(.success)
            }
        }
    }
    
    private func handleDefaultAction(userInfo: [AnyHashable: Any]) {
        // Специальная маршрутизация для семейного чата, чтобы сохранить поведение
        // после централизации UNUserNotificationCenterDelegate в NotificationManager.
        if let type = userInfo["type"] as? String, type == "family_chat" {
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToFamilyChat"),
                object: nil,
                userInfo: userInfo as? [String: Any]
            )
            return
        }

        if let type = userInfo["type"] as? String, type == MnemonicNotificationScheduler.userInfoType {
            let category = userInfo["category"] as? String ?? ChildCategoryKey.games
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToMnemoReview"),
                object: nil,
                userInfo: ["category": category]
            )
            return
        }

        if let type = userInfo["type"] as? String, type == WindDownScheduler.notificationType {
            if let deepLink = userInfo["deepLink"] as? String,
               let url = URL(string: deepLink),
               CompanionDeepLinkRouter.isVoiceDayRecapDeepLink(url) {
                VoiceDayRecapService.markPendingOpen()
                NotificationCenter.default.post(
                    name: NSNotification.Name("NavigateToVoiceDayRecap"),
                    object: nil
                )
                return
            }
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToWellnessWindDown"),
                object: nil,
                userInfo: userInfo as? [String: Any]
            )
            return
        }

        if let deepLink = userInfo["deepLink"] as? String,
           let url = URL(string: deepLink) {
            if url.host == "tariffs" || url.absoluteString.hasPrefix(Self.tariffsDeepLink) {
                NotificationCenter.default.post(
                    name: NSNotification.Name("NavigateToTariffs"),
                    object: nil
                )
                return
            }
            if AntifakeDeepLinkRouter.isPostCallCheckDeepLink(url) {
                NotificationCenter.default.post(
                    name: NSNotification.Name("NavigateToAntifakePostCallCheck"),
                    object: nil
                )
                return
            }
            // inf-deeplink — Unicorn habit / check-in / recap / focus
            if let dest = UnicornDeepLinkRouter.parse(url) {
                switch dest {
                case .companionTalk:
                    NotificationCenter.default.post(
                        name: NSNotification.Name("NavigateToCompanionTalkNow"),
                        object: nil
                    )
                case .wellnessCheckin:
                    NotificationCenter.default.post(
                        name: NSNotification.Name("NavigateToWellnessCheckin"),
                        object: nil
                    )
                case .voiceDayRecap:
                    VoiceDayRecapService.markPendingOpen()
                    NotificationCenter.default.post(
                        name: NSNotification.Name("NavigateToVoiceDayRecap"),
                        object: nil
                    )
                case .focusSession:
                    NotificationCenter.default.post(
                        name: NSNotification.Name("NavigateToFocusSession"),
                        object: nil
                    )
                case .familyHabits, .habitDone:
                    NotificationCenter.default.post(
                        name: NSNotification.Name("NavigateToFamily"),
                        object: nil
                    )
                }
                return
            }
        }
        
        // TODO: Обработка обычного нажатия
        print("📱 Default notification action triggered")
    }
}

// MARK: - Supporting Types

enum NotificationCategory: String, CaseIterable {
    case general = "general"
    case security = "security"
    case family = "family"
    case networkProtection = "network_protection"
    case ai = "ai"
    case subscription = "subscription"
    case trial = "trial"
    case mnemo = "mnemo"
    case familyHabit = "family_habit"
}

struct NotificationSettings: Codable, Equatable {
    var securityEnabled: Bool = true
    var familyEnabled: Bool = true
    var networkProtectionEnabled: Bool = true
    var aiEnabled: Bool = true
    var bypassEnabled: Bool = true  // НОВАЯ настройка!
    var soundEnabled: Bool = true
    var badgeEnabled: Bool = true
    var quietModeEnabled: Bool = false
    var quietHoursEnabled: Bool = false
    var quietHoursStart: String = "22:00"
    var quietHoursEnd: String = "08:00"
    
    // Новые режимы
    var importantOnlyMode: Bool = false // Только важные (угрозы безопасности)
    var doNotDisturbMode: Bool = false // Не беспокоить (полное отключение)
    var doNotDisturbUntil: Date? // Время окончания режима "Не беспокоить"
    var highPriorityOnly: Bool = false // Только уведомления высокого приоритета
    var maxNotificationsPerHour: Int? // Ограничение частоты (nil = без ограничений)
    
    // Equatable - автоматически генерируется Swift компилятором для структур
}
