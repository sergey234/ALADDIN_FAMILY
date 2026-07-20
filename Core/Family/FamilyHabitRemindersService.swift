import Foundation

/// fws-02: fetch/save family habit templates + optional wellness habits sync.
@MainActor
final class FamilyHabitRemindersService: ObservableObject {
    static let shared = FamilyHabitRemindersService()

    @Published private(set) var config: FamilyHabitRemindersConfig = .empty
    @Published private(set) var isConfiguredOnServer = false

    private let cacheKey = "family_habit_reminders_cache_v2"

    private init() {
        loadCache()
    }

    func refreshFromServer(members: [FamilyMemberData]) async {
        let result: Result<FamilyHabitRemindersResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilyHabitReminders { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            config = payload.config
            isConfiguredOnServer = payload.configured
            saveCache()
            await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        case .failure:
            await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        }
    }

    func save(
        config newConfig: FamilyHabitRemindersConfig,
        members: [FamilyMemberData]
    ) async throws {
        struct Body: Codable {
            let presets: [String: FamilyHabitPresetSchedule]
            let memberIds: [String]

            enum CodingKeys: String, CodingKey {
                case presets
                case memberIds = "member_ids"
            }
        }
        let result: Result<FamilyHabitRemindersSaveResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.setFamilyHabitReminders(
                body: Body(presets: newConfig.presets, memberIds: newConfig.memberIds)
            ) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            config = payload.config
            isConfiguredOnServer = payload.configured
            saveCache()
            await syncWellnessHabitsIfOnline(config: config)
            _ = await FamilyHabitRemindersScheduler.shared.requestAuthorizationIfNeeded()
            await FamilyHabitRemindersScheduler.shared.reschedule(config: config, members: members)
        case .failure(let error):
            throw error
        }
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
        config = decoded
    }

    private func saveCache() {
        guard let data = try? JSONEncoder().encode(config) else { return }
        UserDefaults.standard.set(data, forKey: cacheKey)
    }
}
