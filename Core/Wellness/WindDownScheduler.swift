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
        var components = DateComponents()
        components.hour = bedtime.hour
        components.minute = bedtime.minute

        for minutes in [30, 15, 5] {
            guard let fireDate = nextFireDate(bedtime: components, minutesBefore: minutes) else { continue }
            let content = UNMutableNotificationContent()
            content.title = localization.localized("wind_down_push_title")
            content.body = localization.localized("wind_down_push_body_\(minutes)")
            content.sound = .default
            content.userInfo = [
                "type": Self.notificationType,
                "minutes_before": minutes,
                "deepLink": minutes == 30 ? "aladdin://voice/day-recap" : "aladdin://wellness/wind-down",
            ]

            let triggerComponents = Calendar.current.dateComponents(
                [.year, .month, .day, .hour, .minute],
                from: fireDate
            )
            let trigger = UNCalendarNotificationTrigger(dateMatching: triggerComponents, repeats: false)
            let request = UNNotificationRequest(
                identifier: identifier(minutesBefore: minutes),
                content: content,
                trigger: trigger
            )
            try? await center.add(request)
        }
    }

    private func nextFireDate(bedtime: DateComponents, minutesBefore: Int) -> Date? {
        let cal = Calendar.current
        guard let tonight = cal.nextDate(
            after: Date(),
            matching: bedtime,
            matchingPolicy: .nextTime
        ) else { return nil }
        return cal.date(byAdding: .minute, value: -minutesBefore, to: tonight)
    }
}
