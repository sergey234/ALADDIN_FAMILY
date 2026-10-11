import Foundation

/// qa-01: «Удалить у себя» — hide message ids only on this device (not server wipe).
enum FamilyChatLocalHiddenStore {
    private static let key = "family_chat_hidden_message_ids_v1"
    private static let maxIds = 500

    static func hiddenIds(defaults: UserDefaults = .standard) -> Set<String> {
        let arr = defaults.stringArray(forKey: key) ?? []
        return Set(arr)
    }

    static func hide(messageId: String, defaults: UserDefaults = .standard) {
        let trimmed = messageId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        var ids = defaults.stringArray(forKey: key) ?? []
        if !ids.contains(trimmed) {
            ids.append(trimmed)
        }
        if ids.count > maxIds {
            ids = Array(ids.suffix(maxIds))
        }
        defaults.set(ids, forKey: key)
        defaults.synchronize()
    }

    static func isHidden(_ messageId: String, defaults: UserDefaults = .standard) -> Bool {
        hiddenIds(defaults: defaults).contains(messageId)
    }

    /// Own message and age ≤ 24h → may call server delete-for-everyone.
    static func canDeleteForEveryone(isCurrentUser: Bool, rawTimestamp: String?, now: Date = Date()) -> Bool {
        guard isCurrentUser else { return false }
        guard let raw = rawTimestamp?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else {
            return false
        }
        guard let created = parseTimestamp(raw) else { return false }
        return now.timeIntervalSince(created) <= 24 * 60 * 60
    }

    private static func parseTimestamp(_ raw: String) -> Date? {
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = iso.date(from: raw) { return d }
        iso.formatOptions = [.withInternetDateTime]
        if let d = iso.date(from: raw) { return d }
        let df = DateFormatter()
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = TimeZone(secondsFromGMT: 0)
        df.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return df.date(from: raw)
    }
}
