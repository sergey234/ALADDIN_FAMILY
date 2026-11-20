import Foundation
import UserNotifications

/// After a site activation code is redeemed, schedule local pushes 7 and 3 days before expiry (L360 stage 4b).
/// Channel: in-app push only (no e-mail / bot). Never asks for notification permission.
final class SiteSubscriptionExpiryReminderScheduler {
    static let shared = SiteSubscriptionExpiryReminderScheduler()

    static let dayOffsets = [7, 3]
    static let identifierPrefix = "site.sub.expiry."
    static let deepLink = "aladdin://tariffs?renew=1"
    private static let expiresKey = "subscription_expires_at_iso"

    private let center = UNUserNotificationCenter.current()
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    static func identifier(daysBefore: Int) -> String {
        "\(identifierPrefix)d\(daysBefore)"
    }

    /// Call after a successful site-code activation (`expiresAt` ISO8601).
    func reschedule(expiresAtISO: String, now: Date = Date()) {
        defaults.set(expiresAtISO, forKey: Self.expiresKey)
        guard let expires = Self.parseISO(expiresAtISO) else { return }
        center.removePendingNotificationRequests(withIdentifiers: Self.dayOffsets.map(Self.identifier(daysBefore:)))
        Task { await self.schedule(expiresAt: expires, now: now) }
    }

    /// Re-apply from UserDefaults (app launch) so reminders survive reinstall of notification requests.
    func rescheduleFromStoredExpiryIfNeeded(now: Date = Date()) {
        let iso = (defaults.string(forKey: Self.expiresKey) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !iso.isEmpty else { return }
        reschedule(expiresAtISO: iso, now: now)
    }

    private func schedule(expiresAt: Date, now: Date) async {
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional else {
            return
        }
        let localization = LocalizationManager.shared
        let calendar = Calendar.current
        for days in Self.dayOffsets {
            guard let fire = calendar.date(byAdding: .day, value: -days, to: expiresAt), fire > now else { continue }
            var comps = calendar.dateComponents([.year, .month, .day], from: fire)
            comps.hour = 11
            comps.minute = 0
            guard let at = calendar.date(from: comps), at > now else { continue }
            let content = UNMutableNotificationContent()
            content.title = localization.localized("site_sub_expiry_push_title")
            content.body = String(
                format: localization.localized(days == 7 ? "site_sub_expiry_push_body_7d" : "site_sub_expiry_push_body_3d"),
                Self.dayMonthLabel(expiresAt, locale: localization.locale)
            )
            content.sound = .default
            content.userInfo = ["type": "site_subscription_expiry", "deepLink": Self.deepLink]
            if #available(iOS 15.0, *) {
                content.interruptionLevel = .timeSensitive
            }
            let trigger = UNCalendarNotificationTrigger(
                dateMatching: calendar.dateComponents([.year, .month, .day, .hour, .minute], from: at),
                repeats: false
            )
            try? await center.add(
                UNNotificationRequest(identifier: Self.identifier(daysBefore: days), content: content, trigger: trigger)
            )
        }
    }

    static func parseISO(_ raw: String) -> Date? {
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = iso.date(from: raw) { return d }
        iso.formatOptions = [.withInternetDateTime]
        if let d = iso.date(from: raw) { return d }
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(secondsFromGMT: 0)
        f.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return f.date(from: raw)
    }

    private static func dayMonthLabel(_ date: Date, locale: Locale) -> String {
        let f = DateFormatter()
        f.locale = locale
        f.dateStyle = .medium
        f.timeStyle = .none
        return f.string(from: date)
    }
}
