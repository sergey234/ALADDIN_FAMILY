import Foundation
import UserNotifications

/// VSL-C P2 — weekly family safety digest from local voice intent tags (no child spy).
struct VoiceWeeklyDigestResult: Equatable, Identifiable {
    let id: UUID
    var weekLabel: String
    var stats: VoiceDayIntentStats
    var topLines: [String]

    init(
        id: UUID = UUID(),
        weekLabel: String,
        stats: VoiceDayIntentStats,
        topLines: [String]
    ) {
        self.id = id
        self.weekLabel = weekLabel
        self.stats = stats
        self.topLines = topLines
    }
}

enum VoiceWeeklyDigestService {
    static let notificationId = "voice_safety_weekly_digest"
    static let notificationType = "voice_weekly_digest"
    static let pendingOpenKey = "voice_weekly_digest_pending_open"

    static func markPendingOpen(defaults: UserDefaults = .standard) {
        defaults.set(true, forKey: pendingOpenKey)
    }

    static func consumePendingOpen(defaults: UserDefaults = .standard) -> Bool {
        let flag = defaults.bool(forKey: pendingOpenKey)
        if flag { defaults.set(false, forKey: pendingOpenKey) }
        return flag
    }

    /// Last 7 days (including today), local notes only.
    static func build(notes: [VoiceNotesStore.StoredVoiceNote], now: Date = Date(), calendar: Calendar = .current) -> VoiceWeeklyDigestResult {
        guard let start = calendar.date(byAdding: .day, value: -6, to: calendar.startOfDay(for: now)) else {
            return VoiceWeeklyDigestResult(weekLabel: "", stats: VoiceDayIntentStats(), topLines: [])
        }
        let inWeek = notes.filter { $0.createdAt >= start && $0.createdAt <= now }
        var stats = VoiceDayIntentStats()
        var top: [String] = []
        for note in inWeek.sorted(by: { $0.createdAt > $1.createdAt }) {
            let tags = Set(note.tags)
            if tags.contains("intent_antifake_url") || tags.contains("intent_security_check") {
                stats.securityChecks += 1
            } else if tags.contains("intent_incident") {
                stats.incidents += 1
            } else if tags.contains("intent_idea") {
                stats.ideas += 1
            } else if tags.contains("intent_remind") {
                stats.reminds += 1
            } else {
                stats.notes += 1
            }
            let line = note.summary.isEmpty ? note.transcriptPreview : note.summary
            let cleaned = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if !cleaned.isEmpty,
               !cleaned.hasPrefix("voice_notes_"),
               top.count < 5 {
                top.append(String(cleaned.prefix(100)))
            }
        }
        let fmt = DateFormatter()
        fmt.dateStyle = .medium
        fmt.timeStyle = .none
        let weekLabel = "\(fmt.string(from: start)) – \(fmt.string(from: now))"
        return VoiceWeeklyDigestResult(weekLabel: weekLabel, stats: stats, topLines: top)
    }

    /// Schedule Sunday 19:00 local repeating reminder (idempotent replace).
    static func ensureSundaySchedule() {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: [notificationId])

        var comps = DateComponents()
        comps.weekday = 1 // Sunday
        comps.hour = 19
        comps.minute = 0
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: true)

        NotificationManager.shared.scheduleLocalNotification(
            identifier: notificationId,
            title: LocalizationManager.shared.localized("voice_weekly_digest_push_title"),
            body: LocalizationManager.shared.localized("voice_weekly_digest_push_body"),
            category: .security,
            userInfo: [
                "type": notificationType,
                "deepLink": "aladdin://voice/weekly"
            ],
            trigger: trigger
        )
    }
}
