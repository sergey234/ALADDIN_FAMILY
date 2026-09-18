import Foundation

/// VSL-C P1 — local counts of today's voice intents (no network).
struct VoiceDayIntentStats: Equatable {
    var securityChecks: Int = 0
    var incidents: Int = 0
    var ideas: Int = 0
    var reminds: Int = 0
    var notes: Int = 0

    var hasAny: Bool {
        securityChecks + incidents + ideas + reminds + notes > 0
    }

    static func fromTodayNotes(
        _ notes: [VoiceNotesStore.StoredVoiceNote],
        calendar: Calendar = .current
    ) -> VoiceDayIntentStats {
        let today = notes.filter { calendar.isDateInToday($0.createdAt) }
        var stats = VoiceDayIntentStats()
        for note in today {
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
        }
        return stats
    }
}
