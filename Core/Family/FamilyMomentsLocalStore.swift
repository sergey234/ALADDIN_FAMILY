import Foundation

/// p2-9a/e lite — local Moments until full Moments API (text-only, private family).
struct FamilyMomentLocal: Codable, Identifiable, Equatable {
    let id: String
    let text: String
    let childId: String?
    let createdAt: String
    let kind: String
}

enum FamilyMomentsLocalStore {
    private static let key = "family_moments_local_v1"

    static func list(defaults: UserDefaults = .standard) -> [FamilyMomentLocal] {
        guard let data = defaults.data(forKey: key),
              let items = try? JSONDecoder().decode([FamilyMomentLocal].self, from: data) else {
            return []
        }
        return items.sorted { $0.createdAt > $1.createdAt }
    }

    @discardableResult
    static func append(
        text: String,
        childId: String? = nil,
        kind: String = "manual",
        defaults: UserDefaults = .standard
    ) -> FamilyMomentLocal {
        let item = FamilyMomentLocal(
            id: UUID().uuidString,
            text: text,
            childId: childId,
            createdAt: ISO8601DateFormatter().string(from: Date()),
            kind: kind
        )
        var all = list(defaults: defaults)
        all.insert(item, at: 0)
        if let data = try? JSONEncoder().encode(all) {
            defaults.set(data, forKey: key)
        }
        return item
    }
}
