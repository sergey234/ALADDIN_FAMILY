import Foundation

/// fws-02 preset identifiers — 💧 / 📵 / 😴 (reminder only, not bedtime block).
enum FamilyHabitPresetId: String, Codable, CaseIterable, Identifiable {
    case water
    case phoneDown = "phone_down"
    case windDown = "wind_down"
    /// p1-8a — medicine reminder (single daily slot; ping ON by default when Due enabled).
    case medicine

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .water: return "💧"
        case .phoneDown: return "📵"
        case .windDown: return "😴"
        case .medicine: return "💊"
        }
    }

    var titleKey: String { "family_habit_\(rawValue)_title" }
    var bodyKey: String { "family_habit_\(rawValue)_body" }
}

/// Allowed daily water goals (liters).
enum FamilyHabitWaterDailyLiters: Double, CaseIterable, Identifiable {
    case half = 0.5
    case one = 1.0
    case oneHalf = 1.5
    case two = 2.0
    case twoHalf = 2.5
    case three = 3.0

    var id: Double { rawValue }

    var labelKey: String {
        switch self {
        case .half: return "family_habit_water_liters_0_5"
        case .one: return "family_habit_water_liters_1"
        case .oneHalf: return "family_habit_water_liters_1_5"
        case .two: return "family_habit_water_liters_2"
        case .twoHalf: return "family_habit_water_liters_2_5"
        case .three: return "family_habit_water_liters_3"
        }
    }

    static func nearest(_ value: Double) -> FamilyHabitWaterDailyLiters {
        allCases.min(by: { abs($0.rawValue - value) < abs($1.rawValue - value) }) ?? .two
    }
}

/// Interval between water pushes (minutes).
enum FamilyHabitWaterInterval: Int, CaseIterable, Identifiable {
    case oneHour = 60
    case oneHalf = 90
    case twoHours = 120
    case threeHours = 180

    var id: Int { rawValue }

    var labelKey: String {
        switch self {
        case .oneHour: return "family_habit_water_interval_1h"
        case .oneHalf: return "family_habit_water_interval_1_5h"
        case .twoHours: return "family_habit_water_interval_2h"
        case .threeHours: return "family_habit_water_interval_3h"
        }
    }

    static func nearest(_ minutes: Int) -> FamilyHabitWaterInterval {
        allCases.min(by: { abs($0.rawValue - minutes) < abs($1.rawValue - minutes) }) ?? .twoHours
    }
}

struct FamilyHabitPresetSchedule: Codable, Equatable {
    var enabled: Bool
    /// Start of reminder window (and single daily time for non-water presets).
    var hour: Int
    var minute: Int
    /// End of window (water only; ignored for other presets).
    var endHour: Int
    var endMinute: Int
    /// Minutes between water pushes.
    var intervalMinutes: Int
    /// Daily water goal in liters.
    var dailyLiters: Double
    /// p1-7a — keep pinging until Done (water default OFF).
    var pingUntilDone: Bool
    /// Minutes between due-pings (clamped 15…30).
    var pingIntervalMinutes: Int
    /// Cap due-pings per day.
    var pingMaxPerDay: Int

    static let `default` = FamilyHabitPresetSchedule(
        enabled: false,
        hour: 11,
        minute: 0,
        endHour: 21,
        endMinute: 0,
        intervalMinutes: 120,
        dailyLiters: 2.0,
        pingUntilDone: false,
        pingIntervalMinutes: 20,
        pingMaxPerDay: 6
    )

    enum CodingKeys: String, CodingKey {
        case enabled, hour, minute
        case endHour = "end_hour"
        case endMinute = "end_minute"
        case intervalMinutes = "interval_minutes"
        case dailyLiters = "daily_liters"
        case pingUntilDone = "ping_until_done"
        case pingIntervalMinutes = "ping_interval_minutes"
        case pingMaxPerDay = "ping_max_per_day"
    }

    init(
        enabled: Bool,
        hour: Int,
        minute: Int,
        endHour: Int = 21,
        endMinute: Int = 0,
        intervalMinutes: Int = 120,
        dailyLiters: Double = 2.0,
        pingUntilDone: Bool = false,
        pingIntervalMinutes: Int = 20,
        pingMaxPerDay: Int = 6
    ) {
        self.enabled = enabled
        self.hour = hour
        self.minute = minute
        self.endHour = endHour
        self.endMinute = endMinute
        self.intervalMinutes = intervalMinutes
        self.dailyLiters = dailyLiters
        self.pingUntilDone = pingUntilDone
        self.pingIntervalMinutes = min(30, max(15, pingIntervalMinutes))
        self.pingMaxPerDay = min(12, max(1, pingMaxPerDay))
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        enabled = try c.decodeIfPresent(Bool.self, forKey: .enabled) ?? false
        hour = try c.decodeIfPresent(Int.self, forKey: .hour) ?? 11
        minute = try c.decodeIfPresent(Int.self, forKey: .minute) ?? 0
        endHour = try c.decodeIfPresent(Int.self, forKey: .endHour) ?? 21
        endMinute = try c.decodeIfPresent(Int.self, forKey: .endMinute) ?? 0
        intervalMinutes = try c.decodeIfPresent(Int.self, forKey: .intervalMinutes) ?? 120
        dailyLiters = try c.decodeIfPresent(Double.self, forKey: .dailyLiters) ?? 2.0
        // p1-7a: water and legacy configs default ping OFF
        pingUntilDone = try c.decodeIfPresent(Bool.self, forKey: .pingUntilDone) ?? false
        let rawPingInterval = try c.decodeIfPresent(Int.self, forKey: .pingIntervalMinutes) ?? 20
        pingIntervalMinutes = min(30, max(15, rawPingInterval))
        let rawPingMax = try c.decodeIfPresent(Int.self, forKey: .pingMaxPerDay) ?? 6
        pingMaxPerDay = min(12, max(1, rawPingMax))
    }

    static func defaultsMap() -> [FamilyHabitPresetId: FamilyHabitPresetSchedule] {
        [
            .water: FamilyHabitPresetSchedule(
                enabled: false, hour: 9, minute: 0, endHour: 21, endMinute: 0,
                intervalMinutes: 120, dailyLiters: 2.0,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            .phoneDown: FamilyHabitPresetSchedule(
                enabled: false, hour: 21, minute: 0,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            .windDown: FamilyHabitPresetSchedule(
                enabled: false, hour: 22, minute: 30,
                pingUntilDone: false, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
            // p1-8a: medicine — 09:00, ping ON default (when Due feature enabled)
            .medicine: FamilyHabitPresetSchedule(
                enabled: false, hour: 9, minute: 0,
                pingUntilDone: true, pingIntervalMinutes: 20, pingMaxPerDay: 6
            ),
        ]
    }

    /// Compact summary for collapsed water row, e.g. `2 л · каждые 2 ч · 09:00–21:00`.
    func waterSummaryLine(localization: LocalizationManager) -> String {
        let liters = FamilyHabitWaterDailyLiters.nearest(dailyLiters)
        let interval = FamilyHabitWaterInterval.nearest(intervalMinutes)
        let litersLabel = localization.localized(liters.labelKey)
        let intervalLabel = localization.localized(interval.labelKey)
        let window = String(
            format: "%02d:%02d–%02d:%02d",
            hour, minute, endHour, endMinute
        )
        return "\(litersLabel) · \(intervalLabel) · \(window)"
    }

    /// Slot times (hour, minute) from start→end stepping by interval (water). Cap 12.
    func waterNotificationSlots(maxSlots: Int = 12) -> [(hour: Int, minute: Int)] {
        let start = hour * 60 + minute
        var end = endHour * 60 + endMinute
        if end <= start {
            end += 24 * 60
        }
        let step = max(30, FamilyHabitWaterInterval.nearest(intervalMinutes).rawValue)
        var slots: [(Int, Int)] = []
        var t = start
        while t <= end && slots.count < maxSlots {
            let wrapped = t % (24 * 60)
            slots.append((wrapped / 60, wrapped % 60))
            t += step
        }
        if slots.isEmpty {
            slots.append((hour, minute))
        }
        return slots
    }
}

struct FamilyHabitRemindersConfig: Codable, Equatable {
    var presets: [String: FamilyHabitPresetSchedule]
    var memberIds: [String]

    enum CodingKeys: String, CodingKey {
        case presets
        case memberIds = "member_ids"
    }

    static let empty = FamilyHabitRemindersConfig(
        presets: FamilyHabitPresetId.allCases.reduce(into: [:]) { acc, preset in
            acc[preset.rawValue] = FamilyHabitPresetSchedule.defaultsMap()[preset] ?? .default
        },
        memberIds: []
    )

    func schedule(for preset: FamilyHabitPresetId) -> FamilyHabitPresetSchedule {
        presets[preset.rawValue] ?? FamilyHabitPresetSchedule.defaultsMap()[preset] ?? .default
    }

    mutating func setSchedule(_ schedule: FamilyHabitPresetSchedule, for preset: FamilyHabitPresetId) {
        presets[preset.rawValue] = schedule
    }
}

struct FamilyHabitRemindersResponse: Codable, Equatable {
    let familyId: String?
    let config: FamilyHabitRemindersConfig
    let configured: Bool
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case config
        case configured
        case updatedAt = "updated_at"
    }
}

struct FamilyHabitRemindersSaveResponse: Codable, Equatable {
    let familyId: String?
    let config: FamilyHabitRemindersConfig
    let configured: Bool
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case config
        case configured
        case updatedAt = "updated_at"
    }
}

enum FamilyHabitRemindersPolicy {
    /// Empty `member_ids` → all minors + elderly in roster.
    static func shouldReceiveReminders(
        config: FamilyHabitRemindersConfig,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> Bool {
        let myMemberId = (defaults.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !myMemberId.isEmpty else { return false }

        if !config.memberIds.isEmpty {
            return config.memberIds.contains(where: { id in
                matchesMember(id: id, myMemberId: myMemberId, members: members)
            })
        }

        let role = FamilyAccessPolicy.resolveActorRole(members: members, defaults: defaults)
        switch role {
        case .child, .teenager, .elderly:
            return true
        case .parent, .unknown:
            return false
        }
    }

    private static func matchesMember(
        id: String,
        myMemberId: String,
        members: [FamilyMemberData]
    ) -> Bool {
        if id == myMemberId { return true }
        return members.contains { member in
            let sid = member.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let canon = member.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
            let rid = member.id.trimmingCharacters(in: .whitespacesAndNewlines)
            return sid == id || canon == id || rid == id || sid == myMemberId || canon == myMemberId
        }
    }
}

struct WellnessHabitCreateResponse: Codable, Equatable {
    let ok: Bool?
}
