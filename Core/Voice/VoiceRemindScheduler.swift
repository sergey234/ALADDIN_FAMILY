import Foundation
import UserNotifications

/// VSL-C P2 — local reminder from voice «не забыть …» (default +1 hour).
enum VoiceRemindScheduler {
    static let idPrefix = "voice_remind_"

    static func schedule(fromRemainder remainder: String, noteId: UUID) {
        let body = remainder.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !body.isEmpty else { return }

        let fire = Date().addingTimeInterval(60 * 60)
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: max(60, fire.timeIntervalSinceNow), repeats: false)
        let id = idPrefix + noteId.uuidString

        NotificationManager.shared.scheduleLocalNotification(
            identifier: id,
            title: LocalizationManager.shared.localized("voice_remind_push_title"),
            body: String(body.prefix(120)),
            category: .general,
            userInfo: [
                "type": "voice_remind",
                "deepLink": "aladdin://voice/log",
                "noteId": noteId.uuidString
            ],
            trigger: trigger
        )
    }
}
