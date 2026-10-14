import Foundation

/// W2 UX36 — never show raw `"3h/day"` on UI; always localize hours phrase.
enum ParentalScreenTimeFormat {
    static func display(
        stored: String,
        localization: LocalizationManager = .shared
    ) -> String {
        let digits = stored.filter(\.isNumber)
        if let hours = Int(digits), hours > 0 {
            return String(format: localization.localized("day_strip_screen_hours_format"), hours)
        }
        if let hours = Int(stored.trimmingCharacters(in: .whitespacesAndNewlines)), hours > 0 {
            return String(format: localization.localized("day_strip_screen_hours_format"), hours)
        }
        return localization.localized("day_strip_screen_hours_unknown")
    }

    static func storageValue(hours: Int) -> String {
        "\(max(hours, 0))h/day"
    }
}
