import Foundation

/// VSL-C P1 — «Сейчас…» status for home chip (local only, no child spy).
enum VoiceSafetyNowStore {
    static let storageKey = "voice_safety_now_v1"
    static let pendingOpenKey = "voice_safety_notes_pending_open"

    static func markPendingOpen(defaults: UserDefaults = .standard) {
        defaults.set(true, forKey: pendingOpenKey)
    }

    static func consumePendingOpen(defaults: UserDefaults = .standard) -> Bool {
        let flag = defaults.bool(forKey: pendingOpenKey)
        if flag { defaults.set(false, forKey: pendingOpenKey) }
        return flag
    }

    struct Snapshot: Codable, Equatable {
        var intentTag: String
        var detail: String
        var updatedAt: Date

        var localizationKey: String {
            switch intentTag {
            case "intent_antifake_url", "intent_security_check":
                return "voice_safety_now_checking"
            case "intent_incident":
                return "voice_safety_now_incident"
            case "intent_status":
                return "voice_safety_now_status"
            case "intent_idea":
                return "voice_safety_now_idea"
            case "intent_remind":
                return "voice_safety_now_remind"
            case "intent_break":
                return "voice_safety_now_break"
            default:
                return "voice_safety_now_note"
            }
        }
    }

    static func save(intentTag: String, detail: String, defaults: UserDefaults = .standard) {
        let snap = Snapshot(
            intentTag: intentTag,
            detail: String(detail.prefix(120)),
            updatedAt: Date()
        )
        if let data = try? JSONEncoder().encode(snap) {
            defaults.set(data, forKey: storageKey)
        }
        let lineKey = snap.localizationKey
        let line = LocalizationManager.shared.localized(lineKey)
        SharedDataManager.updateVoiceSafetyWidgetData(line: line, detail: snap.detail)
        NotificationCenter.default.post(name: .voiceSafetyNowDidChange, object: nil)
    }

    static func load(defaults: UserDefaults = .standard) -> Snapshot? {
        guard let data = defaults.data(forKey: storageKey),
              let snap = try? JSONDecoder().decode(Snapshot.self, from: data) else {
            return nil
        }
        // Stale after 12 hours
        if Date().timeIntervalSince(snap.updatedAt) > 12 * 3600 {
            clear(defaults: defaults)
            return nil
        }
        return snap
    }

    static func clear(defaults: UserDefaults = .standard) {
        defaults.removeObject(forKey: storageKey)
        SharedDataManager.clearVoiceSafetyWidgetData()
        NotificationCenter.default.post(name: .voiceSafetyNowDidChange, object: nil)
    }
}

extension Notification.Name {
    static let voiceSafetyNowDidChange = Notification.Name("VoiceSafetyNowDidChange")
    static let navigateToVoiceNotes = Notification.Name("NavigateToVoiceNotes")
}
