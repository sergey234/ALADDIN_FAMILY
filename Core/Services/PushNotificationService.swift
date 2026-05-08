import Foundation
import UserNotifications

/**
 * 🔔 Push Notification Service
 * Управление push-уведомлениями для семейного чата
 */

class PushNotificationService: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = PushNotificationService()
    
    // MARK: - Published Properties
    
    @Published var isAuthorized: Bool = false
    @Published var isEnabled: Bool = true
    
    // MARK: - Private Properties
    
    private let notificationCenter = UNUserNotificationCenter.current()
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        // Delegate notifications централизован в NotificationManager.
        // Иначе возникает race: последний назначивший delegate перехватывает события.
        checkAuthorizationStatus()
    }
    
    // MARK: - Authorization
    
    func requestAuthorization() {
        notificationCenter.requestAuthorization(options: [.alert, .sound, .badge]) { [weak self] granted, error in
            DispatchQueue.main.async {
                self?.isAuthorized = granted
            }
            
            if let error = error {
                print("❌ PushNotificationService: Ошибка запроса разрешения: \(error.localizedDescription)")
            } else {
                print("✅ PushNotificationService: Разрешение \(granted ? "предоставлено" : "отклонено")")
            }
        }
    }
    
    private func checkAuthorizationStatus() {
        notificationCenter.getNotificationSettings { [weak self] settings in
            DispatchQueue.main.async {
                self?.isAuthorized = settings.authorizationStatus == .authorized
            }
        }
    }
    
    // MARK: - Send Notification
    
    func sendChatNotification(message: String, sender: String, familyId: String?) {
        guard isEnabled && isAuthorized else { return }
        
        let content = UNMutableNotificationContent()
        content.title = String(format: LocalizationManager.shared.localized("family_chat_notification_new_message"), sender)
        content.body = message
        content.sound = .default
        content.badge = 1
        content.userInfo = [
            "type": "family_chat",
            "familyId": familyId ?? "",
            "sender": sender
        ]
        
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 0.1, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )
        
        notificationCenter.add(request) { error in
            if let error = error {
                print("❌ PushNotificationService: Ошибка отправки уведомления: \(error.localizedDescription)")
            } else {
                print("✅ PushNotificationService: Уведомление отправлено")
            }
        }
    }
    
    // MARK: - Settings
    
    func updateSettings(sound: Bool, vibration: Bool) {
        // Сохраняем настройки
        UserDefaults.standard.set(sound, forKey: "chat_notification_sound")
        UserDefaults.standard.set(vibration, forKey: "chat_notification_vibration")
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension PushNotificationService: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Показываем уведомление даже когда приложение открыто
        completionHandler([.banner, .sound, .badge])
    }
    
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        
        if let type = userInfo["type"] as? String, type == "family_chat" {
            // Навигация к чату
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToFamilyChat"),
                object: nil,
                userInfo: userInfo
            )
        }
        
        completionHandler()
    }
}

