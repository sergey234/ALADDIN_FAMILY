import CallKit
import Foundation
import UserNotifications

/// Post-call local notification → Antifake Hub (af-4-03).
@MainActor
final class AntifakeCallObserverService: NSObject, CXCallObserverDelegate {
    static let shared = AntifakeCallObserverService()

    private let observer = CXCallObserver()
    private var activeConnectedCalls: Set<UUID> = []

    private override init() {
        super.init()
    }

    func startIfNeeded() {
        guard AntifakeAccessPolicy.isHubAvailable() else { return }
        observer.setDelegate(self, queue: nil)
        requestNotificationAuthorizationIfNeeded()
    }

    private func requestNotificationAuthorizationIfNeeded() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    nonisolated func callObserver(_ callObserver: CXCallObserver, callChanged call: CXCall) {
        Task { @MainActor in
            if call.hasConnected, !call.hasEnded {
                activeConnectedCalls.insert(call.uuid)
            }
            if call.hasEnded, activeConnectedCalls.contains(call.uuid) {
                activeConnectedCalls.remove(call.uuid)
                await schedulePostCallCheckNotification()
            }
        }
    }

    private func schedulePostCallCheckNotification() async {
        let lastPush = UserDefaults.standard.double(forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
        let now = Date().timeIntervalSince1970
        guard AntifakePostCallPolicy.shouldScheduleNotification(
            reminderEnabled: AppConfig.isAntifakePostCallReminderEnabled,
            lastPushAt: lastPush,
            now: now
        ) else { return }

        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingAntifakePostCallCheck)
        let content = UNMutableNotificationContent()
        content.title = LocalizationManager.shared.localized("antifake_post_call_title")
        content.body = LocalizationManager.shared.localized("antifake_post_call_body")
        content.sound = .default
        content.userInfo = ["deepLink": "aladdin://antifake/call-check"]
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1.5, repeats: false)
        let request = UNNotificationRequest(
            identifier: "antifake_post_call_\(UUID().uuidString)",
            content: content,
            trigger: trigger
        )
        try? await UNUserNotificationCenter.current().add(request)
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
    }
}
