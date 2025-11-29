import Foundation
import UserNotifications
import UIKit

/**
 * 🔔 Notification Manager
 * Управление push и локальными уведомлениями
 * Интеграция с сервером для отправки уведомлений
 */

class NotificationManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = NotificationManager()
    
    // MARK: - Published Properties
    
    @Published var isAuthorized: Bool = false
    @Published var deviceToken: String?
    @Published var notificationSettings: NotificationSettings = NotificationSettings()
    
    // MARK: - Private Properties
    
    private let notificationCenter = UNUserNotificationCenter.current()
    private let apiService = APIService(networkManager: NetworkManager())
    
    // MARK: - Init
    
    private override init() {
        super.init()
        notificationCenter.delegate = self
        checkAuthorizationStatus()
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
     */
    func sendLocalNotification(
        title: String,
        body: String,
        category: NotificationCategory = .general,
        userInfo: [String: Any] = [:],
        delay: TimeInterval = 0
    ) {
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
     * Уведомление о подключении VPN
     */
    func sendVPNConnectedNotification(server: String) {
        sendLocalNotification(
            title: "🔒 VPN подключен",
            body: "Ваше соединение защищено через \(server)",
            category: .vpn,
            userInfo: [
                "type": "vpn_connected",
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
        
        let vpnCategory = UNNotificationCategory(
            identifier: NotificationCategory.vpn.rawValue,
            actions: [
                UNNotificationAction(
                    identifier: "view_vpn",
                    title: "Открыть VPN",
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
        
        notificationCenter.setNotificationCategories([
            generalCategory,
            securityCategory,
            familyCategory,
            vpnCategory,
            aiCategory
        ])
    }
    
    // MARK: - Settings
    
    /**
     * Обновить настройки уведомлений
     */
    func updateNotificationSettings(_ settings: NotificationSettings) {
        self.notificationSettings = settings
        
        // Применить настройки
        Task {
            await applyNotificationSettings(settings)
        }
    }
    
    private func applyNotificationSettings(_ settings: NotificationSettings) async {
        // TODO: Реализовать применение настроек уведомлений
        print("📱 Notification settings updated: \(settings)")
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    
    /**
     * Обработка уведомления когда приложение в foreground
     */
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Показывать уведомления даже когда приложение активно
        completionHandler([.banner, .sound, .badge])
    }
    
    /**
     * Обработка нажатия на уведомление
     */
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        
        // Обработка действий
        switch response.actionIdentifier {
        case "view_details":
            handleViewDetailsAction(userInfo: userInfo)
        case "view_family":
            handleViewFamilyAction(userInfo: userInfo)
        case "view_vpn":
            handleViewVPNAction(userInfo: userInfo)
        case "reply":
            handleReplyAction(userInfo: userInfo)
        default:
            handleDefaultAction(userInfo: userInfo)
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
    
    private func handleViewVPNAction(userInfo: [AnyHashable: Any]) {
        // TODO: Навигация к экрану VPN
        print("🔒 View VPN action triggered")
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
    case vpn = "vpn"
    case ai = "ai"
}

struct NotificationSettings: Codable {
    var securityEnabled: Bool = true
    var familyEnabled: Bool = true
    var vpnEnabled: Bool = true
    var aiEnabled: Bool = true
    var soundEnabled: Bool = true
    var badgeEnabled: Bool = true
    var quietHoursEnabled: Bool = false
    var quietHoursStart: String = "22:00"
    var quietHoursEnd: String = "08:00"
}
