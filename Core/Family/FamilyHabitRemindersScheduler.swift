import Foundation
import UserNotifications

/// fws-02: schedules daily local notifications from family templates.
final class FamilyHabitRemindersScheduler {
    static let shared = FamilyHabitRemindersScheduler()

    private let center = UNUserNotificationCenter.current()
    private let localization = LocalizationManager.shared

    private init() {}

    func identifier(for preset: FamilyHabitPresetId) -> String {
        "family.habit.\(preset.rawValue)"
    }

    func reschedule(
        config: FamilyHabitRemindersConfig,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) async {
        let ids = FamilyHabitPresetId.allCases.map { identifier(for: $0) }
        center.removePendingNotificationRequests(withIdentifiers: ids)

        guard FamilyHabitRemindersPolicy.shouldReceiveReminders(
            config: config,
            members: members,
            defaults: defaults
        ) else {
            return
        }

        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized
            || settings.authorizationStatus == .provisional
            || settings.authorizationStatus == .ephemeral else {
            return
        }

        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            guard schedule.enabled else { continue }
            await scheduleDaily(preset: preset, hour: schedule.hour, minute: schedule.minute)
        }
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

    private func scheduleDaily(preset: FamilyHabitPresetId, hour: Int, minute: Int) async {
        let content = UNMutableNotificationContent()
        content.title = localization.localized(preset.titleKey)
        content.body = localization.localized(preset.bodyKey)
        content.sound = .default
        content.userInfo = [
            "type": "family_habit_reminder",
            "preset": preset.rawValue,
        ]

        var components = DateComponents()
        components.hour = max(0, min(23, hour))
        components.minute = max(0, min(59, minute))
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
        let request = UNNotificationRequest(
            identifier: identifier(for: preset),
            content: content,
            trigger: trigger
        )
        try? await center.add(request)
    }
}
