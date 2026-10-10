import Foundation
import UserNotifications

/// Family habit local notifications.
/// Water + medicine: multiple daily slots in start→end window (same calendar style as WindDown).
/// Phone / wind_down: one daily time.
/// Custom (fhc-03/15): `window` / `once_daily` / `once_at` under `family.habit.custom.<id>`.
final class FamilyHabitRemindersScheduler {
    static let shared = FamilyHabitRemindersScheduler()

    private let center = UNUserNotificationCenter.current()
    private let localization = LocalizationManager.shared
    private let waterIdPrefix = "family.habit.water."
    private let medicineIdPrefix = "family.habit.medicine."
    private let maxWindowSlots = 12
    static let categoryIdentifier = "family_habit"
    static let doneActionIdentifier = "FAMILY_HABIT_DONE"
    static let customPresetPrefix = "custom."
    static let customIdNamespace = "family.habit.custom."

    private init() {}

    // MARK: - Custom id helpers (testable, no title in logs)

    static func customPresetRaw(id: String) -> String {
        "\(customPresetPrefix)\(id)"
    }

    static func customDailyIdentifier(id: String) -> String {
        "\(customIdNamespace)\(id)"
    }

    static func customSlotPrefix(id: String) -> String {
        "\(customIdNamespace)\(id)."
    }

    /// fhc-15 — one-shot once_at notification id.
    static func customOnceAtIdentifier(id: String) -> String {
        "\(customIdNamespace)\(id).at"
    }

    static func customId(fromPresetRaw presetRaw: String) -> String? {
        guard presetRaw.hasPrefix(customPresetPrefix) else { return nil }
        let id = String(presetRaw.dropFirst(customPresetPrefix.count))
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return id.isEmpty ? nil : id
    }

    /// Whether a pending notification id belongs to this preset (including custom.<uuid>).
    static func pendingIdentifier(_ pendingId: String, matchesPresetRaw presetRaw: String) -> Bool {
        if let customId = customId(fromPresetRaw: presetRaw) {
            let daily = customDailyIdentifier(id: customId)
            let prefix = customSlotPrefix(id: customId)
            return pendingId == daily || pendingId.hasPrefix(prefix)
        }
        if presetRaw == FamilyHabitPresetId.water.rawValue {
            return pendingId.hasPrefix("family.habit.water.")
                || pendingId == "family.habit.water"
        }
        if presetRaw == FamilyHabitPresetId.medicine.rawValue {
            return pendingId.hasPrefix("family.habit.medicine.")
                || pendingId == "family.habit.medicine"
        }
        return pendingId == "family.habit.\(presetRaw)"
            || pendingId.hasPrefix("family.habit.\(presetRaw).")
    }

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

    /// Mark habit done: Unicorn XP (presets only) + clear pending, then reschedule.
    /// Custom habits: clear/reschedule only — no XP / streak (REGISTRY stop-list).
    @discardableResult
    func handleDone(
        presetRaw: String,
        config: FamilyHabitRemindersConfig? = nil,
        members: [FamilyMemberData] = []
    ) async -> UnicornCareReward.GrantResult {
        let isCustom = Self.customId(fromPresetRaw: presetRaw) != nil
        let result: UnicornCareReward.GrantResult
        if isCustom {
            let childId = UnicornRewardsStore.resolveActiveChildId()
            result = UnicornCareReward.GrantResult(
                applied: false,
                balance: UnicornRewardsStore.readBalance(for: childId),
                love: 0,
                hunger: 0,
                amount: 0
            )
            if let id = Self.customId(fromPresetRaw: presetRaw) {
                let mode = config?.custom.first(where: { $0.id == id })?.mode.rawValue
                FamilyHabitCustomAnalytics.log(.done, id: id, mode: mode)
                print("✅ family habit done custom id=\(id) (no XP)")
            }
        } else {
            result = UnicornCareReward.grant(
                reason: .habitDone,
                sourceId: presetRaw,
                childId: UnicornRewardsStore.resolveActiveChildId()
            )
            _ = HabitStreakStore.shared.recordDone(sourceId: presetRaw)
        }
        await clearPending(forPreset: presetRaw)
        if let config {
            await reschedule(config: config, members: members)
        }
        return result
    }

    func clearPending(forPreset presetRaw: String) async {
        let pending = await center.pendingNotificationRequests()
        let ids = pending
            .map(\.identifier)
            .filter { Self.pendingIdentifier($0, matchesPresetRaw: presetRaw) }
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
            print("🔕 family habits: policy skipped (remindOnThisDevice / member)")
            return
        }

        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized
            || settings.authorizationStatus == .provisional
            || settings.authorizationStatus == .ephemeral else {
            print("🔕 family habits: notification auth missing")
            return
        }

        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            guard schedule.enabled else { continue }
            switch preset {
            case .water:
                await scheduleWindowSlots(
                    presetRaw: FamilyHabitPresetId.water.rawValue,
                    slots: schedule.windowNotificationSlots(maxSlots: maxWindowSlots),
                    idPrefix: waterIdPrefix,
                    title: localization.localized("family_habit_water_title"),
                    body: {
                        let liters = FamilyHabitWaterDailyLiters.nearest(schedule.dailyLiters)
                        let litersLabel = localization.localized(liters.labelKey)
                        return String(
                            format: localization.localized("family_habit_water_push_body_fmt"),
                            litersLabel
                        )
                    }(),
                    windowLabel: schedule.windowTimeRangeLabel,
                    extraUserInfo: ["daily_liters": schedule.dailyLiters]
                )
            case .medicine:
                await scheduleWindowSlots(
                    presetRaw: FamilyHabitPresetId.medicine.rawValue,
                    slots: schedule.windowNotificationSlots(maxSlots: maxWindowSlots),
                    idPrefix: medicineIdPrefix,
                    title: localization.localized(FamilyHabitPresetId.medicine.titleKey),
                    body: localization.localized(FamilyHabitPresetId.medicine.bodyKey),
                    windowLabel: schedule.windowTimeRangeLabel
                )
            case .phoneDown, .windDown:
                await scheduleDaily(
                    presetRaw: preset.rawValue,
                    hour: schedule.hour,
                    minute: schedule.minute,
                    identifier: identifier(for: preset),
                    title: localization.localized(preset.titleKey),
                    body: localization.localized(preset.bodyKey)
                )
            }
            await scheduleDuePingChain(
                presetRaw: preset.rawValue,
                title: localization.localized(preset.titleKey),
                bodyFallback: localization.localized(preset.bodyKey),
                hour: schedule.hour,
                minute: schedule.minute,
                pingUntilDone: schedule.pingUntilDone,
                pingIntervalMinutes: schedule.pingIntervalMinutes,
                pingMaxPerDay: schedule.pingMaxPerDay
            )
        }

        await scheduleCustomReminders(config.custom)

        let pending = await center.pendingNotificationRequests()
        let habitPending = pending.filter { $0.identifier.hasPrefix("family.habit.") }
        let customPending = habitPending.filter { $0.identifier.hasPrefix(Self.customIdNamespace) }
        print("✅ family habits pending: \(habitPending.count) (custom=\(customPending.count))")
    }

    // MARK: - Custom (fhc-03)

    private func scheduleCustomReminders(_ items: [FamilyHabitCustomReminder]) async {
        var scheduled = 0
        var skippedOnceAt = 0
        var skippedOther = 0
        for item in FamilyHabitCustomReminder.normalizedList(items) {
            guard item.modeRecognized else {
                skippedOther += 1
                print("⏭ family habit custom id=\(item.id) mode=unrecognized skip")
                continue
            }
            guard item.enabled, !item.title.isEmpty else {
                skippedOther += 1
                continue
            }
            switch item.mode {
            case .onceAt:
                guard let fireDate = item.fireAtDate, fireDate > Date() else {
                    skippedOnceAt += 1
                    print("⏭ family habit custom id=\(item.id) mode=once_at past_or_missing")
                    continue
                }
                let presetRaw = Self.customPresetRaw(id: item.id)
                await scheduleOnceAt(
                    presetRaw: presetRaw,
                    fireDate: fireDate,
                    identifier: Self.customOnceAtIdentifier(id: item.id),
                    title: pushTitle(for: item),
                    body: pushBody(for: item)
                )
                // Due-ping optional only when fire is today (same calendar day).
                let cal = Calendar.current
                if item.pingUntilDone, cal.isDateInToday(fireDate) {
                    await scheduleDuePingChain(
                        presetRaw: presetRaw,
                        title: pushTitle(for: item),
                        bodyFallback: pushBody(for: item),
                        hour: cal.component(.hour, from: fireDate),
                        minute: cal.component(.minute, from: fireDate),
                        pingUntilDone: true,
                        pingIntervalMinutes: item.pingIntervalMinutes,
                        pingMaxPerDay: min(item.pingMaxPerDay, 3)
                    )
                }
                scheduled += 1
                print("✅ family habit custom id=\(item.id) mode=once_at")
            case .window:
                let slots = item.windowNotificationSlots(maxSlots: maxWindowSlots)
                let presetRaw = Self.customPresetRaw(id: item.id)
                await scheduleWindowSlots(
                    presetRaw: presetRaw,
                    slots: slots,
                    idPrefix: Self.customSlotPrefix(id: item.id),
                    title: pushTitle(for: item),
                    body: pushBody(for: item),
                    windowLabel: item.windowTimeRangeLabel
                )
                await scheduleDuePingChain(
                    presetRaw: presetRaw,
                    title: pushTitle(for: item),
                    bodyFallback: pushBody(for: item),
                    hour: item.hour,
                    minute: item.minute,
                    pingUntilDone: item.pingUntilDone,
                    pingIntervalMinutes: item.pingIntervalMinutes,
                    pingMaxPerDay: item.pingMaxPerDay
                )
                scheduled += 1
            case .onceDaily:
                let presetRaw = Self.customPresetRaw(id: item.id)
                await scheduleDaily(
                    presetRaw: presetRaw,
                    hour: item.hour,
                    minute: item.minute,
                    identifier: Self.customDailyIdentifier(id: item.id),
                    title: pushTitle(for: item),
                    body: pushBody(for: item)
                )
                await scheduleDuePingChain(
                    presetRaw: presetRaw,
                    title: pushTitle(for: item),
                    bodyFallback: pushBody(for: item),
                    hour: item.hour,
                    minute: item.minute,
                    pingUntilDone: item.pingUntilDone,
                    pingIntervalMinutes: item.pingIntervalMinutes,
                    pingMaxPerDay: item.pingMaxPerDay
                )
                scheduled += 1
                print("✅ family habit custom id=\(item.id) mode=once_daily")
            }
        }
        if scheduled > 0 || skippedOnceAt > 0 || skippedOther > 0 {
            print(
                "✅ family habit custom summary scheduled=\(scheduled) once_at_skip=\(skippedOnceAt) other_skip=\(skippedOther)"
            )
        }
    }

    private func pushTitle(for item: FamilyHabitCustomReminder) -> String {
        let emoji = item.emoji.trimmingCharacters(in: .whitespacesAndNewlines)
        if emoji.isEmpty {
            return item.title
        }
        return "\(emoji) \(item.title)"
    }

    private func pushBody(for item: FamilyHabitCustomReminder) -> String {
        let fmt = localization.localized("family_habit_custom_push_body_fmt")
        if fmt == "family_habit_custom_push_body_fmt" {
            return item.scheduleSummaryLine(localization: localization)
        }
        return String(format: fmt, item.title)
    }

    /// fhc-05 — smoke push in ~1s; same category/Done as real custom reminders.
    func fireCustomTestNotification(for item: FamilyHabitCustomReminder) async {
        let presetRaw = Self.customPresetRaw(id: item.id)
        let content = UNMutableNotificationContent()
        content.title = {
            let emoji = item.emoji.trimmingCharacters(in: .whitespacesAndNewlines)
            return emoji.isEmpty ? item.title : "\(emoji) \(item.title)"
        }()
        let bodyFmt = localization.localized("family_habit_custom_test_push_body")
        if bodyFmt == "family_habit_custom_test_push_body" {
            content.body = String(
                format: localization.localized("family_habit_custom_push_body_fmt"),
                item.title
            )
        } else {
            content.body = bodyFmt
        }
        content.sound = .default
        content.categoryIdentifier = Self.categoryIdentifier
        content.userInfo = [
            "type": "family_habit_reminder",
            "preset": presetRaw,
            "deepLink": UnicornDeepLinkRouter.habitReminderDeepLink(preset: presetRaw),
            "source": "custom_test",
        ]
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        let request = UNNotificationRequest(
            identifier: "\(Self.customSlotPrefix(id: item.id))test",
            content: content,
            trigger: trigger
        )
        _ = await requestAuthorizationIfNeeded()
        do {
            try await center.add(request)
            print("✅ family habit custom test id=\(item.id)")
            FamilyHabitCustomAnalytics.log(.testPush, id: item.id, mode: item.mode.rawValue)
        } catch {
            print("❌ family habit custom test failed id=\(item.id)")
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
        let legacy = FamilyHabitPresetId.allCases.map { identifier(for: $0) }
        center.removePendingNotificationRequests(withIdentifiers: legacy)
    }

    /// Follow-up pings after primary slot until Done / max N (flag OFF by default).
    private func scheduleDuePingChain(
        presetRaw: String,
        title: String,
        bodyFallback: String,
        hour: Int,
        minute: Int,
        pingUntilDone: Bool,
        pingIntervalMinutes: Int,
        pingMaxPerDay: Int
    ) async {
        guard FamilyHabitDuePingFeature.isEnabled else { return }
        guard pingUntilDone else { return }

        let interval = min(30, max(15, pingIntervalMinutes))
        let maxPings = min(12, max(1, pingMaxPerDay))
        let cal = Calendar.current
        let now = Date()
        var base = cal.date(
            bySettingHour: max(0, min(23, hour)),
            minute: max(0, min(59, minute)),
            second: 0,
            of: now
        ) ?? now
        if base <= now {
            base = cal.date(byAdding: .day, value: 1, to: base) ?? base
        }

        let bodyKey = "family_habit_ping_body"
        let body: String = {
            let localized = localization.localized(bodyKey)
            if localized == bodyKey {
                return bodyFallback
            }
            return localized
        }()

        for i in 1..<maxPings {
            guard let fire = cal.date(byAdding: .minute, value: i * interval, to: base) else {
                continue
            }
            let hours = fire.timeIntervalSince(base) / 3600
            if hours > 18 { break }

            let comps = cal.dateComponents([.year, .month, .day, .hour, .minute], from: fire)
            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
            let dueId: String
            if let customId = Self.customId(fromPresetRaw: presetRaw) {
                dueId = "\(Self.customSlotPrefix(id: customId))due.\(i)"
            } else {
                dueId = "family.habit.\(presetRaw).due.\(i)"
            }
            await enqueue(
                identifier: dueId,
                title: title,
                body: body,
                preset: presetRaw,
                type: "family_habit_due_ping",
                trigger: trigger,
                extraUserInfo: ["due_index": i]
            )
        }
    }

    /// Multiple repeating calendar slots in [start, end] — same reliability pattern as WindDownScheduler.
    private func scheduleWindowSlots(
        presetRaw: String,
        slots: [(hour: Int, minute: Int)],
        idPrefix: String,
        title: String,
        body: String,
        windowLabel: String,
        extraUserInfo: [String: Any] = [:]
    ) async {
        for (index, slot) in slots.enumerated() {
            var components = DateComponents()
            components.hour = slot.hour
            components.minute = slot.minute
            let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
            var info = extraUserInfo
            info["slot"] = index
            await enqueue(
                identifier: "\(idPrefix)\(index)",
                title: title,
                body: body,
                preset: presetRaw,
                type: "family_habit_reminder",
                trigger: trigger,
                extraUserInfo: info
            )
        }
        if presetRaw.hasPrefix(Self.customPresetPrefix), let id = Self.customId(fromPresetRaw: presetRaw) {
            print("✅ family habit custom id=\(id) window slots=\(slots.count) \(windowLabel)")
        } else {
            print("✅ family habit \(presetRaw): \(slots.count) slots \(windowLabel)")
        }
    }

    private func scheduleDaily(
        presetRaw: String,
        hour: Int,
        minute: Int,
        identifier: String,
        title: String,
        body: String
    ) async {
        var components = DateComponents()
        components.hour = max(0, min(23, hour))
        components.minute = max(0, min(59, minute))
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
        await enqueue(
            identifier: identifier,
            title: title,
            body: body,
            preset: presetRaw,
            type: "family_habit_reminder",
            trigger: trigger
        )
    }

    /// fhc-15 — one-shot calendar trigger (device-local components, repeats: false).
    private func scheduleOnceAt(
        presetRaw: String,
        fireDate: Date,
        identifier: String,
        title: String,
        body: String
    ) async {
        let comps = Calendar.current.dateComponents(
            [.year, .month, .day, .hour, .minute],
            from: fireDate
        )
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
        await enqueue(
            identifier: identifier,
            title: title,
            body: body,
            preset: presetRaw,
            type: "family_habit_reminder",
            trigger: trigger,
            extraUserInfo: ["once_at": true]
        )
    }

    /// Awaited `UNUserNotificationCenter.add` (WindDown-style) — not fire-and-forget Task.
    private func enqueue(
        identifier: String,
        title: String,
        body: String,
        preset: String,
        type: String,
        trigger: UNNotificationTrigger,
        extraUserInfo: [String: Any] = [:]
    ) async {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = Self.categoryIdentifier
        var userInfo: [String: Any] = [
            "type": type,
            "preset": preset,
            "deepLink": UnicornDeepLinkRouter.habitReminderDeepLink(preset: preset),
        ]
        for (key, value) in extraUserInfo {
            userInfo[key] = value
        }
        content.userInfo = userInfo

        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )
        do {
            try await center.add(request)
        } catch {
            print("❌ family habit schedule failed \(identifier): \(error.localizedDescription)")
        }
    }
}
