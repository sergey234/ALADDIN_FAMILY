import Foundation

/// fws-02 preset identifiers — 💧 / 📵 / 😴 (reminder only, not bedtime block).
enum FamilyHabitPresetId: String, Codable, CaseIterable, Identifiable {
    case water
    case phoneDown = "phone_down"
    case windDown = "wind_down"

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .water: return "💧"
        case .phoneDown: return "📵"
        case .windDown: return "😴"
        }
    }

    var titleKey: String { "family_habit_\(rawValue)_title" }
    var bodyKey: String { "family_habit_\(rawValue)_body" }
}

struct FamilyHabitPresetSchedule: Codable, Equatable {
    var enabled: Bool
    var hour: Int
    var minute: Int

    static let `default` = FamilyHabitPresetSchedule(enabled: false, hour: 11, minute: 0)

    static func defaultsMap() -> [FamilyHabitPresetId: FamilyHabitPresetSchedule] {
        [
            .water: FamilyHabitPresetSchedule(enabled: false, hour: 11, minute: 0),
            .phoneDown: FamilyHabitPresetSchedule(enabled: false, hour: 21, minute: 0),
            .windDown: FamilyHabitPresetSchedule(enabled: false, hour: 22, minute: 30),
        ]
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
