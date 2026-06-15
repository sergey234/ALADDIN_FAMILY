import Foundation

/// E-05 / E-08 — post-call reminder toggle + 15 min push cooldown.
enum AntifakePostCallPolicy {
    static let cooldownSeconds: TimeInterval = 15 * 60

    static func shouldScheduleNotification(
        reminderEnabled: Bool,
        lastPushAt: TimeInterval,
        now: TimeInterval
    ) -> Bool {
        guard reminderEnabled else { return false }
        if lastPushAt > 0, now - lastPushAt < cooldownSeconds {
            return false
        }
        return true
    }
}
