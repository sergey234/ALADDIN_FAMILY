import Foundation

/// UX-36 W6 — SSOT for «Вы с нами с …» / registration date.
/// Never invent "today" on each launch; freeze the earliest known account date.
enum AccountRegistrationDateStore {
    static let userDefaultsKey = "registration_date"
    private static let isoKey = "registration_date_iso_v1"

    /// Stable date for this device account, if known.
    static func resolvedDate(defaults: UserDefaults = .standard) -> Date? {
        if let date = defaults.object(forKey: userDefaultsKey) as? Date {
            return date
        }
        if let iso = defaults.string(forKey: isoKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !iso.isEmpty,
           let parsed = parseISO(iso) {
            // Backfill Date object for older readers.
            defaults.set(parsed, forKey: userDefaultsKey)
            return parsed
        }
        return nil
    }

    /// Capture from server / JWT once. Never moves the date later; earlier server date wins.
    @discardableResult
    static func captureIfNeeded(
        _ candidate: Date?,
        defaults: UserDefaults = .standard
    ) -> Date? {
        guard let candidate else { return resolvedDate(defaults: defaults) }
        let normalized = Calendar.current.startOfDay(for: candidate)
        if let existing = resolvedDate(defaults: defaults) {
            let existingDay = Calendar.current.startOfDay(for: existing)
            if normalized < existingDay {
                persist(normalized, defaults: defaults)
                return normalized
            }
            return existing
        }
        persist(normalized, defaults: defaults)
        return normalized
    }

    /// Parse ISO / display strings from profile API and freeze if needed.
    @discardableResult
    static func captureFromServerString(
        _ raw: String?,
        defaults: UserDefaults = .standard
    ) -> Date? {
        let trimmed = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return resolvedDate(defaults: defaults) }
        if let iso = parseISO(trimmed) {
            return captureIfNeeded(iso, defaults: defaults)
        }
        // Already-localized display string — do not invent a new Date from it.
        return resolvedDate(defaults: defaults)
    }

    /// Formatted for UI, or nil when unknown (caller shows pending-sync copy).
    static func displayString(
        locale: Locale,
        defaults: UserDefaults = .standard
    ) -> String? {
        guard let date = resolvedDate(defaults: defaults) else { return nil }
        let formatter = DateFormatter()
        formatter.dateFormat = "d MMMM yyyy"
        formatter.locale = locale
        return formatter.string(from: date)
    }

    /// RU / EN helper matching existing profile formatters.
    static func displayString(isRussian: Bool, defaults: UserDefaults = .standard) -> String? {
        displayString(
            locale: Locale(identifier: isRussian ? "ru_RU" : "en_US"),
            defaults: defaults
        )
    }

    private static func persist(_ date: Date, defaults: UserDefaults) {
        defaults.set(date, forKey: userDefaultsKey)
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        var encoded = iso.string(from: date)
        if encoded.isEmpty {
            iso.formatOptions = [.withInternetDateTime]
            encoded = iso.string(from: date)
        }
        defaults.set(encoded, forKey: isoKey)
    }

    private static func parseISO(_ raw: String) -> Date? {
        let fractional = ISO8601DateFormatter()
        fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = fractional.date(from: raw) { return d }
        let plain = ISO8601DateFormatter()
        plain.formatOptions = [.withInternetDateTime]
        if let d = plain.date(from: raw) { return d }
        // Date-only YYYY-MM-DD
        let df = DateFormatter()
        df.calendar = Calendar(identifier: .gregorian)
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = TimeZone(secondsFromGMT: 0)
        df.dateFormat = "yyyy-MM-dd"
        return df.date(from: String(raw.prefix(10)))
    }
}
