import Foundation

/// fws-02: fetch/save family habit templates + optional wellness habits sync.
/// fhc-08: encode/decode `custom[]`, soft-fail sync never wipes presets/custom with `.empty`.
@MainActor
final class FamilyHabitRemindersService: ObservableObject {
    static let shared = FamilyHabitRemindersService()

    @Published private(set) var config: FamilyHabitRemindersConfig = .empty
    @Published private(set) var isConfiguredOnServer = false
    /// Localized key for last sync problem (cleared on success). Never means local wipe.
    @Published private(set) var lastSyncErrorKey: String?

    private let cacheKey = "family_habit_reminders_cache_v2"

    private init() {
        loadCache()
    }

    /// POST body for habit-reminders (includes custom — fhc-08).
    struct HabitRemindersBody: Codable, Equatable {
        let presets: [String: FamilyHabitPresetSchedule]
        let memberIds: [String]
        let custom: [FamilyHabitCustomReminder]

        enum CodingKeys: String, CodingKey {
            case presets
            case memberIds = "member_ids"
            case custom
        }

        init(from config: FamilyHabitRemindersConfig) {
            presets = config.presets
            memberIds = config.memberIds
            custom = FamilyHabitCustomReminder.normalizedList(config.custom)
        }
    }

    func refreshFromServer(members: [FamilyMemberData]) async {
        let localBefore = config
        let result: Result<FamilyHabitRemindersResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilyHabitReminders { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            // Server with no row returns defaults (water/medicine hour=9). Never wipe a
            // local schedule the user already set on this phone.
            if payload.configured {
                applyServerConfig(payload.config, localFallback: localBefore, configured: true)
            } else {
                isConfiguredOnServer = false
                lastSyncErrorKey = nil
                if Self.hasUserScheduledTimes(localBefore) {
                    // Keep local — do not assign .empty
                    config = localBefore
                    saveCache()
                }
            }
            await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        case .failure:
            // Soft-fail: leave presets + custom untouched
            lastSyncErrorKey = "family_habit_custom_sync_failed"
            await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        }
    }

    /// True if any preset differs from factory defaults (time / window / enabled).
    static func hasUserScheduledTimes(_ config: FamilyHabitRemindersConfig) -> Bool {
        if !config.custom.isEmpty { return true }
        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            let factory = FamilyHabitPresetSchedule.defaultsMap()[preset] ?? .default
            if schedule.enabled { return true }
            if schedule.hour != factory.hour || schedule.minute != factory.minute { return true }
            if schedule.endHour != factory.endHour || schedule.endMinute != factory.endMinute {
                return true
            }
            if schedule.intervalMinutes != factory.intervalMinutes { return true }
        }
        return false
    }

    /// Older servers omit medicine end_hour / interval — keep local window when missing.
    static func mergeWindowFields(
        server: FamilyHabitRemindersConfig,
        local: FamilyHabitRemindersConfig
    ) -> FamilyHabitRemindersConfig {
        var merged = server
        for preset in [FamilyHabitPresetId.water, .medicine] {
            var s = server.schedule(for: preset)
            let l = local.schedule(for: preset)
            // If server dropped window (legacy medicine normalize), restore from local.
            if preset == .medicine {
                let serverLooksSingleSlot = s.endHour == 21 && s.endMinute == 0
                    && s.intervalMinutes == 120
                    && (l.endHour != s.endHour || l.endMinute != s.endMinute
                        || l.intervalMinutes != s.intervalMinutes)
                if serverLooksSingleSlot && (l.enabled || l.hour != 9 || l.minute != 0) {
                    if s.hour == 9 && s.minute == 0 && (l.hour != 9 || l.minute != 0) {
                        s.hour = l.hour
                        s.minute = l.minute
                    }
                    s.endHour = l.endHour
                    s.endMinute = l.endMinute
                    s.intervalMinutes = l.intervalMinutes
                }
            }
            // Prefer local start time when server bounced back to factory 09:00
            // but local still has a custom time and same enabled flag.
            if s.enabled == l.enabled,
               s.hour == 9, s.minute == 0,
               (l.hour != 9 || l.minute != 0) {
                s.hour = l.hour
                s.minute = l.minute
            }
            merged.setSchedule(s, for: preset)
        }
        // fhc-05/08 — older API omits/empties custom[]; never wipe local custom until server stores it.
        if merged.custom.isEmpty && !local.custom.isEmpty {
            merged.custom = local.custom
        } else {
            merged.custom = FamilyHabitCustomReminder.normalizedList(merged.custom)
        }
        return merged
    }

    /// fhc-08 — only call after HTTP 200 + decode OK. Never used on failure paths.
    func applyServerConfig(
        _ server: FamilyHabitRemindersConfig,
        localFallback: FamilyHabitRemindersConfig,
        configured: Bool
    ) {
        config = Self.mergeWindowFields(server: server, local: localFallback)
        isConfiguredOnServer = configured
        lastSyncErrorKey = nil
        saveCache()
    }

    /// Policy helper for tests: failure must not yield `.empty` when user had data.
    static func configAfterSyncFailure(
        previous: FamilyHabitRemindersConfig,
        attempted: FamilyHabitRemindersConfig
    ) -> FamilyHabitRemindersConfig {
        // Optimistic local-first: keep attempted (includes custom). Never substitute empty.
        if Self.hasUserScheduledTimes(attempted) || Self.hasUserScheduledTimes(previous) {
            return attempted
        }
        return previous
    }

    /// hab-03 — reschedule from local cache without network (scene active / Done).
    func rescheduleFromCache(members: [FamilyMemberData]) async {
        await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
    }

    struct LocalSaveOutcome {
        var notificationsGranted: Bool
        var queuedForServer: Bool
        var needsManualRetry: Bool
        var nextFire: Date?
        /// Localized key when server sync failed (local schedule still applied).
        var syncErrorKey: String?
    }

    /// Local cache + daily push first. Server is queued if the request fails.
    func saveLocalThenSync(
        config newConfig: FamilyHabitRemindersConfig,
        members: [FamilyMemberData]
    ) async -> LocalSaveOutcome {
        let previous = config
        var toSave = newConfig
        toSave.normalizeCustom()
        // Optimistic local — never assign .empty here
        config = toSave
        saveCache()
        let granted = await FamilyHabitRemindersScheduler.shared.requestAuthorizationIfNeeded()
        await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        let nextFire = earliestNextFire(config: config)
        do {
            try await pushServerOnly(config: config)
            await syncWellnessHabitsIfOnline(config: config)
            lastSyncErrorKey = nil
            return LocalSaveOutcome(
                notificationsGranted: granted,
                queuedForServer: false,
                needsManualRetry: false,
                nextFire: nextFire,
                syncErrorKey: nil
            )
        } catch {
            // Soft-fail: keep local presets+custom (already in `config`). Never wipe to empty.
            config = Self.configAfterSyncFailure(previous: previous, attempted: toSave)
            saveCache()
            if AladdinOutboundErrorPolicy.shouldEnqueue(error) {
                await AladdinOutboundQueue.shared.enqueueHabitConfig(config)
                lastSyncErrorKey = nil
                return LocalSaveOutcome(
                    notificationsGranted: granted,
                    queuedForServer: true,
                    needsManualRetry: false,
                    nextFire: nextFire,
                    syncErrorKey: nil
                )
            }
            let errorKey = Self.syncErrorKey(for: error, hadCustom: !toSave.custom.isEmpty)
            lastSyncErrorKey = errorKey
            return LocalSaveOutcome(
                notificationsGranted: granted,
                queuedForServer: false,
                needsManualRetry: true,
                nextFire: nextFire,
                syncErrorKey: errorKey
            )
        }
    }

    static func syncErrorKey(for error: Error, hadCustom: Bool) -> String {
        if hadCustom, AladdinOutboundErrorPolicy.isPermanentFailure(error) {
            return "family_habit_custom_server_outdated"
        }
        return "family_habit_custom_sync_failed"
    }

    func save(
        config newConfig: FamilyHabitRemindersConfig,
        members: [FamilyMemberData]
    ) async throws {
        _ = await saveLocalThenSync(config: newConfig, members: members)
    }

    func pushServerOnly(config newConfig: FamilyHabitRemindersConfig) async throws {
        let body = HabitRemindersBody(from: newConfig)
        let result: Result<FamilyHabitRemindersSaveResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.setFamilyHabitReminders(body: body) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            applyServerConfig(payload.config, localFallback: newConfig, configured: payload.configured)
        case .failure(let error):
            // Do not mutate config here — caller owns soft-fail / keep local.
            throw error
        }
    }

    func earliestNextFire(config: FamilyHabitRemindersConfig, now: Date = Date()) -> Date? {
        var dates: [Date] = []
        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            guard schedule.enabled else { continue }
            switch preset {
            case .water, .medicine:
                for slot in schedule.windowNotificationSlots() {
                    dates.append(LocalDailyReminderMath.nextFire(hour: slot.hour, minute: slot.minute, now: now))
                }
            case .phoneDown, .windDown:
                dates.append(LocalDailyReminderMath.nextFire(hour: schedule.hour, minute: schedule.minute, now: now))
            }
        }
        for item in FamilyHabitCustomReminder.normalizedList(config.custom) where item.shouldScheduleLocally {
            switch item.mode {
            case .window:
                for slot in item.windowNotificationSlots() {
                    dates.append(LocalDailyReminderMath.nextFire(hour: slot.hour, minute: slot.minute, now: now))
                }
            case .onceDaily:
                dates.append(LocalDailyReminderMath.nextFire(hour: item.hour, minute: item.minute, now: now))
            case .onceAt:
                if let fire = item.fireAtDate, fire > now {
                    dates.append(fire)
                }
            }
        }
        return dates.min()
    }

    /// fhc-15 — after Done on once_at, disable that custom row and soft-sync.
    func disableCustomAfterOnceAtDone(id: String, members: [FamilyMemberData]) async {
        var next = config
        guard let idx = next.custom.firstIndex(where: { $0.id == id }) else { return }
        guard next.custom[idx].mode == .onceAt else { return }
        next.custom[idx].enabled = false
        next.normalizeCustom()
        _ = await saveLocalThenSync(config: next, members: members)
    }

    private func syncWellnessHabitsIfOnline(config: FamilyHabitRemindersConfig) async {
        for preset in FamilyHabitPresetId.allCases {
            let schedule = config.schedule(for: preset)
            guard schedule.enabled else { continue }
            let ifThen = ifThenLine(for: preset, schedule: schedule)
            _ = await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
                APIService.shared.createWellnessHabit(ifThen: ifThen) { _ in
                    continuation.resume()
                }
            }
        }
    }

    private func ifThenLine(for preset: FamilyHabitPresetId, schedule: FamilyHabitPresetSchedule) -> String {
        if preset == .water {
            let liters = FamilyHabitWaterDailyLiters.nearest(schedule.dailyLiters)
            let litersLabel = LocalizationManager.shared.localized(liters.labelKey)
            let body = String(
                format: LocalizationManager.shared.localized("family_habit_water_push_body_fmt"),
                litersLabel
            )
            return String(
                format: LocalizationManager.shared.localized("family_habit_if_then_template"),
                schedule.hour,
                schedule.minute,
                body
            )
        }
        let tail = LocalizationManager.shared.localized(preset.bodyKey)
        return String(
            format: LocalizationManager.shared.localized("family_habit_if_then_template"),
            schedule.hour,
            schedule.minute,
            tail
        )
    }

    private func loadCache() {
        guard let data = UserDefaults.standard.data(forKey: cacheKey),
              let decoded = try? JSONDecoder().decode(FamilyHabitRemindersConfig.self, from: data) else {
            return
        }
        // Soft-load: never replace with empty if decode somehow empty but we had nothing — OK
        config = decoded
    }

    private func saveCache() {
        guard let data = try? JSONEncoder().encode(config) else { return }
        UserDefaults.standard.set(data, forKey: cacheKey)
    }
}
