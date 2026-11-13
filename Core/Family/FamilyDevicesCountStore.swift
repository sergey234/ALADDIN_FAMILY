import Foundation

/// QA-09 A: one SSOT for family device count across Main / Devices / Profile.
/// Both screens still fetch `GET /api/devices`; this store holds the last deduped count
/// and broadcasts so every surface can refresh on appear.
@MainActor
enum FamilyDevicesCountStore {
    private static let countKey = "aladdin_family_devices_count_ssot_v1"
    static let didChange = Notification.Name("FamilyDevicesCountSSOTDidChange")

    static var cachedCount: Int {
        UserDefaults.standard.integer(forKey: countKey)
    }

    static func publish(count: Int) {
        let safe = max(0, count)
        let previous = UserDefaults.standard.integer(forKey: countKey)
        UserDefaults.standard.set(safe, forKey: countKey)
        guard safe != previous else { return }
        NotificationCenter.default.post(
            name: didChange,
            object: nil,
            userInfo: ["count": safe]
        )
    }

    static func deduplicatedCount(from ids: [String]) -> Int {
        var seen = Set<String>()
        return ids.filter { seen.insert($0).inserted }.count
    }
}
