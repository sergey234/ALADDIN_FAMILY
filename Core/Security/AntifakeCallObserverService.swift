import CallKit
import Combine
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
        let familyRole = ElderlyScamCallPolicy.showsFullScreen(
            role: UserDefaults.standard.string(forKey: "current_user_role")
        )
        guard familyRole || AntifakeAccessPolicy.isHubAvailable() else { return }
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
        let familyRole = ElderlyScamCallPolicy.showsFullScreen(
            role: UserDefaults.standard.string(forKey: "current_user_role")
        )
        if familyRole {
            ElderlyScamCallGate.shared.isPresented = true
            return
        }

        let lastPush = UserDefaults.standard.double(forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
        let now = Date().timeIntervalSince1970
        guard AntifakePostCallPolicy.shouldScheduleNotification(
            reminderEnabled: AppConfig.isAntifakePostCallReminderEnabled,
            lastPushAt: lastPush,
            now: now
        ) else { return }

        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingAntifakePostCallCheck)
        NotificationManager.shared.sendAntifakePostCallNotification()
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
    }
}

enum ElderlyScamCallPolicy {
    static let repeatGuardSeconds: TimeInterval = 8
    /// Same raw values as `FamilyRole`: parent, child, teenager, elderly.
    static let familyRoles: Set<String> = ["parent", "child", "teenager", "elderly"]

    static func showsFullScreen(role: String?) -> Bool {
        guard let role else { return false }
        return familyRoles.contains(role)
    }

    static func sendsFamilyAlert(pressedMoneyOrCode: Bool) -> Bool {
        pressedMoneyOrCode
    }

    static func allowsAnotherSend(lastSentAt: TimeInterval, now: TimeInterval) -> Bool {
        now - lastSentAt >= repeatGuardSeconds
    }
}

@MainActor
final class ElderlyScamCallGate: ObservableObject {
    static let shared = ElderlyScamCallGate()
    @Published var isPresented = false
    private init() {}
}
