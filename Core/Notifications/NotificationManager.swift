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
        delay: TimeInterval = 0
    ) {
        let notificationType = userInfo["type"] as? String ?? ""
        let notificationCenter = UNUserNotificationCenter.current()
        
        // ✅ Проверяем настройки на main thread асинхронно
        Task { @MainActor in
            // Проверка для уведомлений о попытках обхода (локальные события используют bypass_attempt)
            if (notificationType == "bypass" || notificationType == "bypass_attempt")
                && !NotificationManager.shared.notificationSettings.bypassEnabled {
                print("🔕 Уведомление о попытке обхода пропущено (отключено в настройках)")
                return
            }
            
            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = .default
            content.categoryIdentifier = category.rawValue
            content.userInfo = userInfo

            // Persist security events locally to survive temporary backend/API failures.
            self.persistSecurityEventIfNeeded(title: title, body: body, category: category, userInfo: userInfo)
            
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: delay, repeats: false)
            let request = UNNotificationRequest(
                identifier: UUID().uuidString,
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
        sendLocalNotification(
            title: "🛡️ Угроза заблокирована",
            body: "Заблокирован \(threatType) на \(url)",
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
     */
    func sendNetworkProtectionConnectedNotification(server: String) {
        sendLocalNotification(
            title: "🔒 Защита сети подключена",
            body: "Ваше соединение защищено через \(server)",
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
        sendLocalNotification(
            title: "👨‍👩‍👧‍👦 Новый член семьи",
            body: "\(memberName) присоединился к вашей семье",
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
        sendLocalNotification(
            title: "⚠️ Подозрительная активность",
            body: "Обнаружена \(activity) на одном из устройств",
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
            title: "🤖 AI Помощник",
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
        sendLocalNotification(
            title: "🎉 Поздравляем!",
            body: "Ваша подписка успешно активирована! Теперь доступны все функции защиты.",
            category: .general,
            userInfo: [
                "type": "upgrade_success",
                "action": "subscription_activated"
            ]
        )
    }

    /// QA smoke scenario: принудительно создаёт тестовую угрозу
    /// для проверки цепочки отображения уведомлений на устройстве.
    func sendQATestThreatNotification() {
        let correlationId = "qa-threat-\(UUID().uuidString)"
        sendLocalNotification(
            title: "🧪 Тестовая угроза (QA)",
            body: "Сценарий smoke-test: проверка цепочки detect -> notifications UI",
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
    
    // MARK: - Notification Categories
    
    func setupNotificationCategories() {
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
                    title: "Подробнее",
                    options: [.foreground]
                ),
                UNNotificationAction(
                    identifier: "dismiss",
                    title: "Закрыть",
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
                    title: "Открыть семью",
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
                    title: "Открыть защиту сети",
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
                    title: "Ответить",
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
                    title: "Продлить подписку",
                    options: [.foreground]
                ),
                UNNotificationAction(
                    identifier: "dismiss",
                    title: "Закрыть",
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
                    title: "Повторить",
                    options: [.foreground]
                )
            ],
            intentIdentifiers: [],
            options: []
        )
        
        notificationCenter.setNotificationCategories([
            generalCategory,
            securityCategory,
            familyCategory,
            networkProtectionCategory,
            aiCategory,
            subscriptionCategory,
            mnemoCategory
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
    
    // MARK: - Subscription Renewal Notifications
    
    /**
     * Планирование уведомлений о приближающемся окончании подписки
     * Уведомления отправляются за 3 и 1 день до окончания
     */
    func scheduleRenewalNotifications(subscriptionEndDate: Date) {
        // Отменяем предыдущие уведомления о подписке (если есть)
        cancelRenewalNotifications()
        
        // За 3 дня
        let threeDaysBefore = subscriptionEndDate.addingTimeInterval(-3 * 24 * 60 * 60)
        if threeDaysBefore > Date() {
            scheduleSubscriptionNotification(
                date: threeDaysBefore,
                title: "Подписка заканчивается через 3 дня",
                body: "Продлите подписку, чтобы продолжить пользоваться сервисом",
                daysUntilExpiry: 3,
                subscriptionEndDate: subscriptionEndDate
            )
        }
        
        // За 1 день
        let oneDayBefore = subscriptionEndDate.addingTimeInterval(-24 * 60 * 60)
        if oneDayBefore > Date() {
            scheduleSubscriptionNotification(
                date: oneDayBefore,
                title: "Подписка заканчивается завтра",
                body: "Продлите подписку сейчас, чтобы не потерять доступ к функциям",
                daysUntilExpiry: 1,
                subscriptionEndDate: subscriptionEndDate
            )
        }
        
        print("✅ Уведомления о подписке запланированы: за 3 дня и за 1 день")
    }

    /**
     * 📅 Schedule trial expiry notifications
     * Планирует уведомления об окончании trial периода
     */
    func scheduleTrialNotifications(trialEndDate: Date) {
        // Отменяем предыдущие уведомления trial (если есть)
        cancelTrialNotifications()

        // За 7 дней
        let sevenDaysBefore = trialEndDate.addingTimeInterval(-7 * 24 * 60 * 60)
        if sevenDaysBefore > Date() {
            scheduleTrialNotification(
                date: sevenDaysBefore,
                title: "Trial заканчивается через 7 дней",
                body: "Оформите подписку Premium, чтобы сохранить доступ ко всем функциям",
                daysUntilExpiry: 7,
                trialEndDate: trialEndDate
            )
        }

        // За 3 дня
        let threeDaysBefore = trialEndDate.addingTimeInterval(-3 * 24 * 60 * 60)
        if threeDaysBefore > Date() {
            scheduleTrialNotification(
                date: threeDaysBefore,
                title: "Trial заканчивается через 3 дня",
                body: "Осталось всего 3 дня trial периода. Оформите подписку сейчас!",
                daysUntilExpiry: 3,
                trialEndDate: trialEndDate
            )
        }

        // За 1 день
        let oneDayBefore = trialEndDate.addingTimeInterval(-24 * 60 * 60)
        if oneDayBefore > Date() {
            scheduleTrialNotification(
                date: oneDayBefore,
                title: "Trial заканчивается завтра",
                body: "Последний день trial периода. Оформите Premium подписку!",
                daysUntilExpiry: 1,
                trialEndDate: trialEndDate
            )
        }

        print("✅ Уведомления trial запланированы: за 7, 3 и 1 день")
    }

    /**
     * Отмена запланированных уведомлений о подписке
     */
    func cancelRenewalNotifications() {
        notificationCenter.getPendingNotificationRequests { requests in
            let renewalIdentifiers = requests
                .filter { request in
                    let userInfo = request.content.userInfo
                    return userInfo["type"] as? String == "subscription_renewal"
                }
                .map { $0.identifier }
            
            if !renewalIdentifiers.isEmpty {
                self.notificationCenter.removePendingNotificationRequests(withIdentifiers: renewalIdentifiers)
                print("✅ Отменены предыдущие уведомления о подписке: \(renewalIdentifiers.count)")
            }
        }
    }

    /**
     * ❌ Отмена запланированных trial уведомлений
     */
    func cancelTrialNotifications() {
        notificationCenter.getPendingNotificationRequests { requests in
            let trialIdentifiers = requests
                .filter { request in
                    let userInfo = request.content.userInfo
                    return userInfo["type"] as? String == "trial"
                }
                .map { $0.identifier }

            if !trialIdentifiers.isEmpty {
                self.notificationCenter.removePendingNotificationRequests(withIdentifiers: trialIdentifiers)
                print("✅ Отменены предыдущие trial уведомления: \(trialIdentifiers.count)")
            }
        }
    }

    /**
     * Планирование уведомления о подписке на конкретную дату
     */
    private func scheduleSubscriptionNotification(
        date: Date,
        title: String,
        body: String,
        daysUntilExpiry: Int,
        subscriptionEndDate: Date
    ) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = NotificationCategory.subscription.rawValue
        content.userInfo = [
            "type": "subscription_renewal",
            "days": daysUntilExpiry,
            "subscription_end_date": ISO8601DateFormatter().string(from: subscriptionEndDate)
        ]
        
        let dateComponents = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: false)
        
        let identifier = "subscription_renewal_\(Int(date.timeIntervalSince1970))"
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )
        
        notificationCenter.add(request) { error in
            if let error = error {
                print("❌ Ошибка планирования уведомления о подписке: \(error)")
            } else {
                print("✅ Уведомление о подписке запланировано: \(title) на \(date)")
            }
        }
    }

    /**
     * 📅 Schedule single trial notification
     */
    private func scheduleTrialNotification(
        date: Date,
        title: String,
        body: String,
        daysUntilExpiry: Int,
        trialEndDate: Date
    ) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = NotificationCategory.trial.rawValue
        content.userInfo = [
            "type": "trial",
            "days": daysUntilExpiry,
            "trial_end_date": ISO8601DateFormatter().string(from: trialEndDate)
        ]

        let dateComponents = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: false)

        let identifier = "trial_\(Int(date.timeIntervalSince1970))"
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )

        notificationCenter.add(request) { error in
            if let error = error {
                print("❌ Ошибка планирования trial уведомления: \(error)")
            } else {
                print("✅ Trial уведомление запланировано: \(title) на \(date)")
            }
        }
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {

    /// Читает/пишет `notificationSettings` и связанное состояние — вызывать **только с main thread**.
    private func foregroundPresentationOptions(for notification: UNNotification, now: Date) -> UNNotificationPresentationOptions {
        let userInfo = notification.request.content.userInfo
        let notificationType = userInfo["type"] as? String ?? "info"

        // Проверяем режим "Не беспокоить"
        if notificationSettings.doNotDisturbMode {
            if let until = notificationSettings.doNotDisturbUntil, now < until {
                return []
            } else {
                notificationSettings.doNotDisturbMode = false
                notificationSettings.doNotDisturbUntil = nil
                saveSettings()
            }
        }

        // Проверяем режим "Только важные"
        if notificationSettings.importantOnlyMode {
            let isImportant = notificationType == "threat"
                || notificationType == "warning"
                || notificationType == "bypass"
                || notificationType == "bypass_attempt"
            if !isImportant {
                Task { @MainActor in
                    self.onNotificationReceived?(notification)
                }
                return [.badge]
            }
        }

        // Проверяем приоритет
        if notificationSettings.highPriorityOnly {
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
        if let maxPerHour = notificationSettings.maxNotificationsPerHour {
            let notificationsInLastHour = countNotificationsInLastHour()
            if notificationsInLastHour >= maxPerHour {
                return []
            }
        }

        recordNotificationSent()

        let isQuietMode = notificationSettings.quietModeEnabled
        let currentHour = Calendar.current.component(.hour, from: now)
        let quietStart = Int(notificationSettings.quietHoursStart.split(separator: ":").first ?? "22") ?? 22
        let quietEnd = Int(notificationSettings.quietHoursEnd.split(separator: ":").first ?? "8") ?? 8
        let isQuietHours = isQuietMode && (currentHour >= quietStart || currentHour < quietEnd)

        Task { @MainActor in
            self.onNotificationReceived?(notification)
        }

        if isQuietHours {
            return [.badge]
        } else {
            return notificationSettings.soundEnabled ? [.banner, .sound, .badge] : [.banner, .badge]
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

        if let deepLink = userInfo["deepLink"] as? String,
           let url = URL(string: deepLink),
           AntifakeDeepLinkRouter.isPostCallCheckDeepLink(url) {
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToAntifakePostCallCheck"),
                object: nil
            )
            return
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
