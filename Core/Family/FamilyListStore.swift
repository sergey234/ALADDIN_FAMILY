import Foundation

/// P1.6 — AnyList-lite local + sync model.
struct FamilyListItem: Identifiable, Equatable, Codable {
    var id: String
    var text: String
    var checked: Bool

    init(id: String = UUID().uuidString, text: String, checked: Bool = false) {
        self.id = id
        self.text = text
        self.checked = checked
    }
}

struct FamilyListPayload: Codable {
    var items: [FamilyListItem]
}

enum FamilyListStore {
    static let draftKey = "family_list_draft_from_voice"
    private static let cacheKey = "family_shared_list_cache_v1"
    private static let checkedRewardPrefix = "family_list_checked_reward_"

    static func loadLocal(defaults: UserDefaults = .standard) -> [FamilyListItem] {
        guard let data = defaults.data(forKey: cacheKey),
              let decoded = try? JSONDecoder().decode(FamilyListPayload.self, from: data) else {
            return []
        }
        return decoded.items
    }

    static func saveLocal(_ items: [FamilyListItem], defaults: UserDefaults = .standard) {
        let payload = FamilyListPayload(items: items)
        if let data = try? JSONEncoder().encode(payload) {
            defaults.set(data, forKey: cacheKey)
        }
    }

    static func consumeVoiceDraft(defaults: UserDefaults = .standard) -> [String] {
        let raw = defaults.string(forKey: draftKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard let raw, !raw.isEmpty else { return [] }
        defaults.removeObject(forKey: draftKey)
        return raw
            .components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    /// Small Unicorn XP every N checked items (idempotent per day + item id).
    @discardableResult
    static func rewardIfNeeded(for item: FamilyListItem, checkedCount: Int) -> UnicornCareReward.GrantResult? {
        guard item.checked, checkedCount > 0, checkedCount % 3 == 0 else { return nil }
        return UnicornCareReward.grant(reason: .listChecked, sourceId: item.id)
    }
}

struct FamilySharedListAPIResponse: Codable {
    let familyId: String?
    let list: FamilyListPayload?
    let configured: Bool?
    let updatedAt: String?

    enum CodingKeys: String, CodingKey {
        case familyId = "family_id"
        case list
        case configured
        case updatedAt = "updated_at"
    }
}
