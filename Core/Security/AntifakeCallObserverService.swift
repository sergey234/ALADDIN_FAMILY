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
        let safetyOn = ElderlyScamCallPolicy.shouldPresentSafetyPrompt(
            role: UserDefaults.standard.string(forKey: "current_user_role")
        )
        let callsOn = CallsAccessPolicy.isAvailable()
        guard safetyOn || callsOn || AntifakeAccessPolicy.isHubAvailable() else { return }
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
        let role = UserDefaults.standard.string(forKey: "current_user_role")
        let now = Date().timeIntervalSince1970

        // 1) Safety first (red/green) — for everyone when toggle is on. Avoid stacking with memory sheet.
        if ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: role, now: now) {
            UserDefaults.standard.set(now, forKey: AppConfig.UserDefaultsKeys.postCallSafetyLastShownAt)
            ElderlyScamCallGate.shared.isPresented = true
            return
        }

        // 2) Calls memory after-sheet (trial / Family / Premium).
        CallsLifecycleService.shared.handleCallEnded()

        // 3) Antifake «upload recording?» push (separate toggle + 15 min cooldown).
        let lastPush = UserDefaults.standard.double(forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
        guard AntifakePostCallPolicy.shouldScheduleNotification(
            reminderEnabled: AppConfig.isAntifakePostCallReminderEnabled,
            lastPushAt: lastPush,
            now: now
        ) else { return }

        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingAntifakePostCallCheck)
        NotificationManager.shared.sendAntifakePostCallNotification()
        UserDefaults.standard.set(now, forKey: AppConfig.UserDefaultsKeys.antifakePostCallLastPushAt)
    }
}

enum ElderlyScamCallPolicy {
    static let repeatGuardSeconds: TimeInterval = 8
    /// Min gap between red/green safety screens (avoid spam after short callbacks).
    static let presentCooldownSeconds: TimeInterval = 2 * 60
    /// Same raw values as `FamilyRole`: parent, child, teenager, elderly.
    static let familyRoles: Set<String> = ["parent", "child", "teenager", "elderly"]

    /// User-facing toggle: Settings → post-call safety prompt (default ON for all users).
    static func shouldPresentSafetyPrompt(role: String?, now: TimeInterval = Date().timeIntervalSince1970) -> Bool {
        guard AppConfig.isPostCallSafetyPromptEnabled else { return false }
        let last = UserDefaults.standard.double(forKey: AppConfig.UserDefaultsKeys.postCallSafetyLastShownAt)
        if last > 0, now - last < presentCooldownSeconds { return false }
        // Product decision 2026-10-13: all categories, not only elderly/family.
        _ = role
        return true
    }

    /// Legacy name — prefer `shouldPresentSafetyPrompt`. Kept for call sites / tests.
    static func showsFullScreen(role: String?) -> Bool {
        shouldPresentSafetyPrompt(role: role)
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
