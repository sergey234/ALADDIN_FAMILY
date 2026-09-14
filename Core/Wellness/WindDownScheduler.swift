import Foundation
import UserNotifications

/// fws-18 — local pushes 30/15/5 min before bedtime → sleep story deep link.
final class WindDownScheduler {
    static let shared = WindDownScheduler()
    static let notificationType = "wellness_wind_down"

    private let center = UNUserNotificationCenter.current()
    private let localization = LocalizationManager.shared

    private init() {}

    func identifier(minutesBefore: Int) -> String {
        "wellness.wind_down.\(minutesBefore)m"
    }

    func requestAuthorizationIfNeeded() async -> Bool {
        let settings = await center.notificationSettings()
        switch settings.authorizationStatus {
        case .authorized, .provisional, .ephemeral:
            return true
        case .denied:
            return false
        case .notDetermined:
            return (try? await center.requestAuthorization(options: [.alert, .sound, .badge])) ?? false
        @unknown default:
            return false
        }
    }

    func reschedule() async {
        let ids = [30, 15, 5].map { identifier(minutesBefore: $0) }
        center.removePendingNotificationRequests(withIdentifiers: ids)

        guard WellnessSessionStore.windDownEnabled else { return }

        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized
            || settings.authorizationStatus == .provisional
            || settings.authorizationStatus == .ephemeral else {
            return
        }

        let bedtime = WellnessSessionStore.windDownBedtime
        for minutes in [30, 15, 5] {
            let lead = LocalDailyReminderMath.leadTime(
                bedtimeHour: bedtime.hour,
                bedtimeMinute: bedtime.minute,
                minutesBefore: minutes
            )
            let content = UNMutableNotificationContent()
            content.title = localization.localized("wind_down_push_title")
            content.body = localization.localized("wind_down_push_body_\(minutes)")
            content.sound = .default
            content.userInfo = [
                "type": Self.notificationType,
                "minutes_before": minutes,
                "deepLink": minutes == 30 ? "aladdin://voice/day-recap" : "aladdin://wellness/wind-down",
            ]

            var triggerComponents = DateComponents()
            triggerComponents.hour = lead.hour
            triggerComponents.minute = lead.minute
            let trigger = UNCalendarNotificationTrigger(dateMatching: triggerComponents, repeats: true)
            let request = UNNotificationRequest(
                identifier: identifier(minutesBefore: minutes),
                content: content,
                trigger: trigger
            )
            try? await center.add(request)
        }
    }

    func nextVisibleFire(now: Date = Date()) -> Date? {
        guard WellnessSessionStore.windDownEnabled else { return nil }
        let bedtime = WellnessSessionStore.windDownBedtime
        let lead = LocalDailyReminderMath.leadTime(
            bedtimeHour: bedtime.hour,
            bedtimeMinute: bedtime.minute,
            minutesBefore: 30
        )
        return LocalDailyReminderMath.nextFire(hour: lead.hour, minute: lead.minute, now: now)
    }

    /// Immediate local smoke — does not change the bedtime schedule.
    func fireTestNotification() async {
        await MainActor.run {
            NotificationManager.shared.sendLocalNotification(
                title: localization.localized("wind_down_push_title"),
                body: localization.localized("wellness_wind_down_test_push_body"),
                category: .general,
                userInfo: [
                    "type": Self.notificationType,
                    "minutes_before": 0,
                    "deepLink": "aladdin://wellness/wind-down",
                    "source": "wind_down_test",
                ],
                delay: 1,
                identifier: "wellness.wind_down.test"
            )
        }
    }
}
