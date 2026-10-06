import Foundation
import UserNotifications

/// fsl-14 — недельный дайджест щита: проверки, тревоги, школа. Без чтения чатов.
struct FamilyShieldWeekDigestSnapshot: Equatable {
    let checksCount: Int
    let alertsCount: Int
    let schoolArrivalsCount: Int
    let weekLabel: String

    var isEmpty: Bool {
        checksCount == 0 && alertsCount == 0 && schoolArrivalsCount == 0
    }
}

enum FamilyShieldWeekDigestStore {
    static let notificationId = "family_shield_weekly_digest"
    static let notificationType = "family_shield_week_digest"
    static let pendingOpenKey = "family_shield_week_digest_pending_open"
    private static let schoolWeekKey = "family_shield_school_arrivals_week_v1"
    private static let schoolWeekStampKey = "family_shield_school_week_stamp_v1"

    static func markPendingOpen(defaults: UserDefaults = .standard) {
        defaults.set(true, forKey: pendingOpenKey)
    }

    static func consumePendingOpen(defaults: UserDefaults = .standard) -> Bool {
        let flag = defaults.bool(forKey: pendingOpenKey)
        if flag { defaults.set(false, forKey: pendingOpenKey) }
        return flag
    }

    static func recordSchoolArrival(now: Date = Date(), calendar: Calendar = .current) {
        purgeWeekIfNeeded(now: now, calendar: calendar)
        let n = UserDefaults.standard.integer(forKey: schoolWeekKey)
        UserDefaults.standard.set(n + 1, forKey: schoolWeekKey)
    }

    static func build(
        now: Date = Date(),
        calendar: Calendar = .current,
        localization: LocalizationManager = .shared
    ) -> FamilyShieldWeekDigestSnapshot {
        purgeWeekIfNeeded(now: now, calendar: calendar)
        guard let start = calendar.date(byAdding: .day, value: -6, to: calendar.startOfDay(for: now)) else {
            return FamilyShieldWeekDigestSnapshot(
                checksCount: 0,
                alertsCount: 0,
                schoolArrivalsCount: 0,
                weekLabel: ""
            )
        }
        let checks = AntifakeCheckHistoryStore.load().filter { $0.checkedAt >= start && $0.checkedAt <= now }
        let alerts = checks.filter {
            let v = $0.verdict.lowercased()
            return v.contains("fake") || v == "high"
        }.count
        let school = UserDefaults.standard.integer(forKey: schoolWeekKey)
        let fmt = DateFormatter()
        fmt.locale = localization.locale
        fmt.dateFormat = "dd.MM"
        let weekLabel = "\(fmt.string(from: start))–\(fmt.string(from: now))"
        return FamilyShieldWeekDigestSnapshot(
            checksCount: checks.count,
            alertsCount: alerts,
            schoolArrivalsCount: school,
            weekLabel: weekLabel
        )
    }

    static func scheduleWeeklyReminderIfNeeded(localization: LocalizationManager = .shared) {
        let center = UNUserNotificationCenter.current()
        center.getNotificationSettings { settings in
            guard settings.authorizationStatus == .authorized
                || settings.authorizationStatus == .provisional else { return }
            center.removePendingNotificationRequests(withIdentifiers: [notificationId])
            var date = DateComponents()
            date.weekday = 1 // Sunday
            date.hour = 18
            date.minute = 0
            let content = UNMutableNotificationContent()
            content.title = localization.localized("week_digest_push_title")
            content.body = localization.localized("week_digest_push_body")
            content.sound = .default
            content.userInfo = [
                "type": notificationType,
                "deepLink": "aladdin://family",
            ]
            let trigger = UNCalendarNotificationTrigger(dateMatching: date, repeats: true)
            let request = UNNotificationRequest(identifier: notificationId, content: content, trigger: trigger)
            center.add(request, withCompletionHandler: nil)
        }
    }

    private static func purgeWeekIfNeeded(now: Date, calendar: Calendar) {
        let stamp = weekStamp(now: now, calendar: calendar)
        let saved = UserDefaults.standard.string(forKey: schoolWeekStampKey)
        if saved != stamp {
            UserDefaults.standard.set(stamp, forKey: schoolWeekStampKey)
            UserDefaults.standard.set(0, forKey: schoolWeekKey)
        }
    }

    private static func weekStamp(now: Date, calendar: Calendar) -> String {
        let week = calendar.component(.weekOfYear, from: now)
        let year = calendar.component(.yearForWeekOfYear, from: now)
        return "\(year)-W\(week)"
    }
}
