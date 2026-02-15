import Foundation
import UserNotifications
import UIKit

/**
 * 🔔 Notification Manager
 * Управление push и локальными уведомлениями
 * Интеграция с сервером для отправки уведомлений
 * ✅ @Published свойства автоматически обновляются на main thread
 * ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: @MainActor для безопасности на реальных устройствах
 */

@MainActor
class NotificationManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = NotificationManager()
    
    // MARK: - Published Properties
    
    @Published var isAuthorized: Bool = false
    @Published var deviceToken: String?
    @Published var notificationSettings: NotificationSettings = NotificationSettings()
    
    // Callback для добавления уведомления в список экрана
    var onNotificationReceived: ((UNNotification) -> Void)?
    
    // Трекинг частоты уведомлений
    private var notificationHistory: [(date: Date, count: Int)] = []
    private let historyCleanupInterval: TimeInterval = 3600 // 1 час
    
    // MARK: - Private Properties
    
    private let notificationCenter = UNUserNotificationCenter.current()
    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard
    private let settingsKey = "notificationSettings"
    
    // MARK: - Init
    
    private override init() {
        super.init()
        notificationCenter.delegate = self
        // ✅ Инициализация на main thread для @Published свойств
        DispatchQueue.main.async { [weak self] in
            self?.checkAuthorizationStatus()
            self?.loadSettings()
        }
    }
    
    // MARK: - Authorization
    
    /**
     * Запросить разрешение на уведомления
     */
    func requestAuthorization() async -> Bool {
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
            DispatchQueue.main.async {
                self.isAuthorized = settings.authorizationStatus == .authorized
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
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            apiService.registerDeviceToken(token) { result in
                #if DEBUG
                print("📱 Register device token result: \(result)")
                #endif
                continuation.resume()
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
            // Проверка для уведомлений о попытках обхода
            if notificationType == "bypass" && !NotificationManager.shared.notificationSettings.bypassEnabled {
                print("🔕 Уведомление о попытке обхода пропущено (отключено в настройках)")
                return
            }
            
            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = .default
            content.categoryIdentifier = category.rawValue
            content.userInfo = userInfo
            
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
        
        notificationCenter.setNotificationCategories([
            generalCategory,
            securityCategory,
            familyCategory,
            networkProtectionCategory,
            aiCategory,
            subscriptionCategory
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
     * ✅ Обновление @Published свойств на main thread
     */
    private func loadSettings() {
        guard let data = userDefaults.data(forKey: settingsKey) else {
            // Используем настройки по умолчанию
            DispatchQueue.main.async { [weak self] in
                self?.notificationSettings = NotificationSettings()
            }
            return
        }
        
        do {
            let decoder = JSONDecoder()
            let settings = try decoder.decode(NotificationSettings.self, from: data)
            // ✅ Обновляем @Published свойство на main thread
            DispatchQueue.main.async { [weak self] in
                self?.notificationSettings = settings
                print("✅ Notification settings loaded")
            }
        } catch {
            print("❌ Failed to load notification settings: \(error), using defaults")
            DispatchQueue.main.async { [weak self] in
                self?.notificationSettings = NotificationSettings()
            }
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
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    
    /**
     * Обработка уведомления когда приложение в foreground
     * ✅ nonisolated: методы делегата могут вызываться не на main thread
     * ✅ ИСПРАВЛЕНО: Используем continuation для синхронного доступа к @MainActor свойствам
     */
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let now = Date()
        let userInfo = notification.request.content.userInfo
        let notificationType = userInfo["type"] as? String ?? "info"
        
        // ✅ ИСПРАВЛЕНО: Используем DispatchQueue.main.sync для синхронного доступа к @MainActor свойствам
        // Методы делегата могут вызываться не на main thread, поэтому используем sync
        let options: UNNotificationPresentationOptions = DispatchQueue.main.sync {
            // Проверяем режим "Не беспокоить"
            if self.notificationSettings.doNotDisturbMode {
                if let until = self.notificationSettings.doNotDisturbUntil, now < until {
                    // Режим активен - не показываем ничего
                    return [] as UNNotificationPresentationOptions
                } else {
                    // Время истекло - отключаем режим
                    self.notificationSettings.doNotDisturbMode = false
                    self.notificationSettings.doNotDisturbUntil = nil
                    self.saveSettings() // Сохраняем изменение
                }
            }
            
            // Проверяем режим "Только важные"
            if self.notificationSettings.importantOnlyMode {
                let isImportant = notificationType == "threat" || notificationType == "warning"
                if !isImportant {
                    // Не важное уведомление - тихий режим
                    Task { @MainActor in
                        self.onNotificationReceived?(notification)
                    }
                    return [.badge] as UNNotificationPresentationOptions
                }
            }
            
            // Проверяем приоритет
            if self.notificationSettings.highPriorityOnly {
                let priorityString = userInfo["priority"] as? String
                let priority = priorityString != nil ? NotificationPriority(from: priorityString!) : NotificationPriority.high
                if priority != .high {
                    // Не высокий приоритет - тихий режим
                    Task { @MainActor in
                        self.onNotificationReceived?(notification)
                    }
                    return [.badge] as UNNotificationPresentationOptions
                }
            }
            
            // Проверяем частоту уведомлений
            if let maxPerHour = self.notificationSettings.maxNotificationsPerHour {
                let notificationsInLastHour = self.countNotificationsInLastHour()
                if notificationsInLastHour >= maxPerHour {
                    // Превышен лимит - не показываем
                    return [] as UNNotificationPresentationOptions
                }
            }
            
            // Обновляем историю
            self.recordNotificationSent()
            
            // Проверяем тихий режим
            let isQuietMode = self.notificationSettings.quietModeEnabled
            let currentHour = Calendar.current.component(.hour, from: now)
            let quietStart = Int(self.notificationSettings.quietHoursStart.split(separator: ":").first ?? "22") ?? 22
            let quietEnd = Int(self.notificationSettings.quietHoursEnd.split(separator: ":").first ?? "8") ?? 8
            let isQuietHours = isQuietMode && (currentHour >= quietStart || currentHour < quietEnd)
            
            // Уведомляем ViewModel о новом уведомлении
            Task { @MainActor in
                self.onNotificationReceived?(notification)
            }
            
            // Если тихий режим - только badge, без звука и баннера
            if isQuietHours {
                return [.badge] as UNNotificationPresentationOptions
            } else {
                // Показывать уведомления даже когда приложение активно
                return self.notificationSettings.soundEnabled ? [.banner, .sound, .badge] : [.banner, .badge]
            }
        }
        
        completionHandler(options)
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
