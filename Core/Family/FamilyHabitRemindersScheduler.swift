import Foundation
import UserNotifications

/// fws-02: schedules local notifications from family templates.
/// Water: multiple daily slots in start→end window; other presets: one daily time.
final class FamilyHabitRemindersScheduler {
    static let shared = FamilyHabitRemindersScheduler()

    private let center = UNUserNotificationCenter.current()
    private let localization = LocalizationManager.shared
    private let waterIdPrefix = "family.habit.water."
    private let maxWaterSlots = 12
    static let categoryIdentifier = "family_habit"
    static let doneActionIdentifier = "FAMILY_HABIT_DONE"

    private init() {}

    /// Register Done action category (call from NotificationManager.setupNotificationCategories).
    static func makeNotificationCategory(doneTitle: String) -> UNNotificationCategory {
        let done = UNNotificationAction(
            identifier: doneActionIdentifier,
            title: doneTitle,
            options: []
        )
        return UNNotificationCategory(
            identifier: categoryIdentifier,
            actions: [done],
            intentIdentifiers: [],
            options: []
        )
    }

    /// P0.1 — mark habit done: Unicorn XP + clear today's pending for preset.
    @discardableResult
    func handleDone(presetRaw: String) async -> UnicornCareReward.GrantResult {
        let result = UnicornCareReward.grant(
            reason: .habitDone,
            sourceId: presetRaw,
            childId: UnicornRewardsStore.resolveActiveChildId()
        )
        _ = HabitStreakStore.shared.recordDone(sourceId: presetRaw)
        await clearPending(forPreset: presetRaw)
        return result
    }

    func clearPending(forPreset presetRaw: String) async {
        let pending = await center.pendingNotificationRequests()
        let ids = pending
            .map(\.identifier)
            .filter { id in
                if presetRaw == FamilyHabitPresetId.water.rawValue {
                    return id.hasPrefix(waterIdPrefix) || id == identifier(for: .water)
                }
                return id == "family.habit.\(presetRaw)" || id.hasPrefix("family.habit.\(presetRaw).")
            }
        if !ids.isEmpty {
            center.removePendingNotificationRequests(withIdentifiers: ids)
        }
    }

    func identifier(for preset: FamilyHabitPresetId) -> String {
        "family.habit.\(preset.rawValue)"
    }

    func reschedule(
        config: FamilyHabitRemindersConfig,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) async {
        await clearPendingFamilyHabitNotifications()

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
            if preset == .water {
                await scheduleWaterSlots(schedule)
            } else {
                await scheduleDaily(
                    preset: preset,
                    hour: schedule.hour,
                    minute: schedule.minute,
                    identifier: identifier(for: preset)
                )
            }
            // p1-7b — Due-ping chain (flag OFF by default; cleared on Done)
            await scheduleDuePingChain(preset: preset, schedule: schedule)
        }
    }

    /// p1-7b: follow-up pings after primary slot until Done / max N (today→tomorrow base).
    private func scheduleDuePingChain(
        preset: FamilyHabitPresetId,
        schedule: FamilyHabitPresetSchedule
    ) async {
        guard FamilyHabitDuePingFeature.isEnabled else { return }
        guard schedule.pingUntilDone else { return }

        let interval = min(30, max(15, schedule.pingIntervalMinutes))
        let maxPings = min(12, max(1, schedule.pingMaxPerDay))
        let cal = Calendar.current
        let now = Date()
        var base = cal.date(
            bySettingHour: max(0, min(23, schedule.hour)),
            minute: max(0, min(59, schedule.minute)),
            second: 0,
            of: now
        ) ?? now
        if base <= now {
            base = cal.date(byAdding: .day, value: 1, to: base) ?? base
        }

        let title = localization.localized(preset.titleKey)
        let bodyKey = "family_habit_ping_body"
        let body: String = {
            let localized = localization.localized(bodyKey)
            if localized == bodyKey {
                return localization.localized(preset.bodyKey)
            }
            return localized
        }()

        // i = 1..<max: follow-ups after primary (primary already scheduled)
        for i in 1..<maxPings {
            guard let fire = cal.date(byAdding: .minute, value: i * interval, to: base) else {
                continue
            }
            // Cap chain within ~18h of base to avoid overnight spam for water
            let hours = fire.timeIntervalSince(base) / 3600
            if hours > 18 { break }

            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = .default
            content.userInfo = [
                "type": "family_habit_due_ping",
                "preset": preset.rawValue,
                "due_index": i,
                "deepLink": UnicornDeepLinkRouter.habitReminderDeepLink(preset: preset.rawValue),
            ]
            content.categoryIdentifier = Self.categoryIdentifier

            let comps = cal.dateComponents([.year, .month, .day, .hour, .minute], from: fire)
            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
            let request = UNNotificationRequest(
                identifier: "family.habit.\(preset.rawValue).due.\(i)",
                content: content,
                trigger: trigger
            )
            try? await center.add(request)
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

    private func clearPendingFamilyHabitNotifications() async {
        let pending = await center.pendingNotificationRequests()
        let ids = pending
            .map(\.identifier)
            .filter { $0.hasPrefix("family.habit.") }
        if !ids.isEmpty {
            center.removePendingNotificationRequests(withIdentifiers: ids)
        }
        // Also remove known single-id presets if any linger without prefix match edge cases
        let legacy = FamilyHabitPresetId.allCases.map { identifier(for: $0) }
        center.removePendingNotificationRequests(withIdentifiers: legacy)
    }

    private func scheduleWaterSlots(_ schedule: FamilyHabitPresetSchedule) async {
        let slots = schedule.waterNotificationSlots(maxSlots: maxWaterSlots)
        let liters = FamilyHabitWaterDailyLiters.nearest(schedule.dailyLiters)
        let litersLabel = localization.localized(liters.labelKey)
        let title = localization.localized("family_habit_water_title")
        let body = String(
            format: localization.localized("family_habit_water_push_body_fmt"),
            litersLabel
        )

        for (index, slot) in slots.enumerated() {
            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = .default
            content.userInfo = [
                "type": "family_habit_reminder",
                "preset": FamilyHabitPresetId.water.rawValue,
                "slot": index,
                "daily_liters": schedule.dailyLiters,
                "deepLink": UnicornDeepLinkRouter.habitReminderDeepLink(preset: FamilyHabitPresetId.water.rawValue),
            ]
            content.categoryIdentifier = Self.categoryIdentifier

            var components = DateComponents()
            components.hour = slot.hour
            components.minute = slot.minute
            let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
            let request = UNNotificationRequest(
                identifier: "\(waterIdPrefix)\(index)",
                content: content,
                trigger: trigger
            )
            try? await center.add(request)
        }
    }

    private func scheduleDaily(
        preset: FamilyHabitPresetId,
        hour: Int,
        minute: Int,
        identifier: String
    ) async {
        let content = UNMutableNotificationContent()
        content.title = localization.localized(preset.titleKey)
        content.body = localization.localized(preset.bodyKey)
        content.sound = .default
        content.userInfo = [
            "type": "family_habit_reminder",
            "preset": preset.rawValue,
            "deepLink": UnicornDeepLinkRouter.habitReminderDeepLink(preset: preset.rawValue),
        ]
        content.categoryIdentifier = Self.categoryIdentifier

        var components = DateComponents()
        components.hour = max(0, min(23, hour))
        components.minute = max(0, min(59, minute))
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )
        try? await center.add(request)
    }
}
