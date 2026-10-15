import Foundation

/// W2 UX36 — never show raw `"3h/day"` / `"1h 36m"` / `"30 min"` on UI; always localize.
enum ParentalScreenTimeFormat {
    static func display(
        stored: String,
        localization: LocalizationManager = .shared
    ) -> String {
        let fromToken = parseHours(from: stored)
        if fromToken > 0 {
            return String(format: localization.localized("day_strip_screen_hours_format"), fromToken)
        }
        if let hours = Int(stored.trimmingCharacters(in: .whitespacesAndNewlines)), hours > 0 {
            return String(format: localization.localized("day_strip_screen_hours_format"), hours)
        }
        return localization.localized("day_strip_screen_hours_unknown")
    }

    static func storageValue(hours: Int) -> String {
        "\(max(hours, 0))h/day"
    }

    /// Localize legacy English duration blobs: `"1h 36m"`, `"18 min"`, `"3h"`.
    static func displayDuration(
        stored: String,
        localization: LocalizationManager = .shared
    ) -> String {
        let parsed = parseDuration(stored)
        if parsed.hours == 0 && parsed.minutes == 0 {
            return localization.localized("duration_unknown")
        }
        return formatDuration(hours: parsed.hours, minutes: parsed.minutes, localization: localization)
    }

    static func formatDuration(
        hours: Int,
        minutes: Int,
        localization: LocalizationManager = .shared
    ) -> String {
        let h = max(hours, 0)
        let m = max(minutes, 0)
        if h > 0 && m > 0 {
            return String(format: localization.localized("duration_hours_minutes_fmt"), h, m)
        }
        if h > 0 {
            return String(format: localization.localized("duration_hours_fmt"), h)
        }
        return String(format: localization.localized("duration_minutes_fmt"), m)
    }

    static func formatMinutes(
        _ minutes: Int,
        localization: LocalizationManager = .shared
    ) -> String {
        formatDuration(hours: 0, minutes: max(minutes, 0), localization: localization)
    }

    // MARK: - Parse

    private static func parseHours(from stored: String) -> Int {
        let lower = stored.lowercased()
        guard let range = lower.range(of: #"(\d+)\s*h"#, options: .regularExpression) else {
            return 0
        }
        return Int(lower[range].filter(\.isNumber)) ?? 0
    }

    private static func parseDuration(_ stored: String) -> (hours: Int, minutes: Int) {
        let lower = stored.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        var hours = 0
        var minutes = 0

        if let hRange = lower.range(of: #"(\d+)\s*h"#, options: .regularExpression) {
            hours = Int(lower[hRange].filter(\.isNumber)) ?? 0
        }

        // Prefer explicit "min" / "мин" before bare "m" (avoids eating "m" from "min").
        if let minRange = lower.range(of: #"(\d+)\s*(min|мин)"#, options: .regularExpression) {
            minutes = Int(lower[minRange].filter(\.isNumber)) ?? 0
        } else if let mRange = lower.range(of: #"(\d+)\s*m\b"#, options: .regularExpression) {
            minutes = Int(lower[mRange].filter(\.isNumber)) ?? 0
        } else if hours == 0, let onlyDigits = Int(lower.filter(\.isNumber)), onlyDigits > 0 {
            minutes = onlyDigits
        }

        return (hours, minutes)
    }
}
