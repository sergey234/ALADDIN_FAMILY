import Foundation

/// p2-9h — FamilyChallenge feature gate (psych-05b CTA uses same key).
enum FamilyChallengesFeature {
    static let flagKey = "feature_family_challenges"
    static let maxActive = 5
    static let draftFromWellnessKey = "family_challenge_draft_from_wellness"

    /// Default ON after p2-9h ships so close-sheet CTA can appear.
    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: flagKey) == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: flagKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: flagKey) }
    }
}

struct FamilyChallenge: Identifiable, Equatable, Codable {
    var id: String
    var title: String
    var emoji: String
    var memberIds: [String]
    var enabled: Bool
    var createdBy: String

    enum CodingKeys: String, CodingKey {
        case id, title, emoji, enabled
        case memberIds = "member_ids"
        case createdBy = "created_by"
    }

    init(
        id: String = UUID().uuidString,
        title: String,
        emoji: String = "🏁",
        memberIds: [String] = [],
        enabled: Bool = true,
        createdBy: String = ""
    ) {
        self.id = id
        self.title = title
        self.emoji = emoji.isEmpty ? "🏁" : emoji
        self.memberIds = memberIds
        self.enabled = enabled
        self.createdBy = createdBy
    }

    var medalSourceId: String {
        HabitMedalSourcesSettings.challengeSourceId(id)
    }
}

struct FamilyChallengesPayload: Codable {
    var challenges: [FamilyChallenge]
}

struct FamilyChallengesAPIResponse: Codable {
    let familyId: String?
    let challenges: [FamilyChallenge]?
    let configured: Bool?
    let max: Int?
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case challenges
        case configured
        case max
        case updatedAt = "updated_at"
    }
}

/// Local cache + Done→XP/streak. Sync is best-effort via API.
enum FamilyChallengesStore {
    private static let cacheKey = "family_challenges_cache_v1"
    private static let donePrefix = "family_challenge_done_"

    static func loadLocal(defaults: UserDefaults = .standard) -> [FamilyChallenge] {
        guard let data = defaults.data(forKey: cacheKey),
              let decoded = try? JSONDecoder().decode(FamilyChallengesPayload.self, from: data) else {
            return []
        }
        return Array(decoded.challenges.prefix(FamilyChallengesFeature.maxActive))
    }

    static func saveLocal(_ challenges: [FamilyChallenge], defaults: UserDefaults = .standard) {
        let capped = Array(challenges.prefix(FamilyChallengesFeature.maxActive))
        let payload = FamilyChallengesPayload(challenges: capped)
        if let data = try? JSONEncoder().encode(payload) {
            defaults.set(data, forKey: cacheKey)
        }
    }

    static func consumeWellnessDraft(defaults: UserDefaults = .standard) -> String? {
        let raw = defaults.string(forKey: FamilyChallengesFeature.draftFromWellnessKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard let raw, raw.count >= 2 else { return nil }
        defaults.removeObject(forKey: FamilyChallengesFeature.draftFromWellnessKey)
        return raw
    }

    private static func dayStamp(_ date: Date = Date()) -> String {
        let f = DateFormatter()
        f.calendar = Calendar.current
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: date)
    }

    /// Idempotent Done for today → Unicorn XP + streak/medal source `challenge:<id>`.
    @discardableResult
    static func markDoneToday(
        challenge: FamilyChallenge,
        memberId: String? = nil,
        defaults: UserDefaults = .standard
    ) -> UnicornCareReward.GrantResult? {
        guard challenge.enabled else { return nil }
        let member = (memberId ?? UnicornRewardsStore.resolveActiveChildId() ?? "guest")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let day = dayStamp()
        let doneKey = "\(donePrefix)\(day)_\(challenge.id)_\(member)"
        if defaults.bool(forKey: doneKey) {
            return nil
        }
        defaults.set(true, forKey: doneKey)
        let result = UnicornCareReward.grant(
            reason: .challengeDone,
            sourceId: challenge.id,
            childId: memberId,
            defaults: defaults
        )
        _ = HabitStreakStore.shared.recordDone(
            sourceId: challenge.medalSourceId,
            memberId: memberId
        )
        return result
    }

    static func isDoneToday(
        challengeId: String,
        memberId: String? = nil,
        defaults: UserDefaults = .standard
    ) -> Bool {
        let member = (memberId ?? UnicornRewardsStore.resolveActiveChildId() ?? "guest")
        let day = dayStamp()
        return defaults.bool(forKey: "\(donePrefix)\(day)_\(challengeId)_\(member)")
    }
}
