import Foundation

/// Circles B — local group labels inside one `family_id` (not a second roster).
enum FamilyGroupLabelStore {
    struct Group: Codable, Identifiable, Equatable {
        var id: UUID
        var title: String
        var memberIds: [String]

        init(id: UUID = UUID(), title: String, memberIds: [String]) {
            self.id = id
            self.title = title
            self.memberIds = memberIds
        }
    }

    private static let storageKey = "aladdin_family_group_labels_v1"
    private static let selectedFilterKey = "aladdin_family_group_filter_id_v1"

    static func load(familyId: String? = nil) -> [Group] {
        let fid = resolvedFamilyId(familyId)
        guard !fid.isEmpty,
              let data = UserDefaults.standard.data(forKey: storageKey),
              let bag = try? JSONDecoder().decode([String: [Group]].self, from: data) else {
            return []
        }
        return bag[fid] ?? []
    }

    static func save(_ groups: [Group], familyId: String? = nil) {
        let fid = resolvedFamilyId(familyId)
        guard !fid.isEmpty else { return }
        var bag: [String: [Group]] = [:]
        if let data = UserDefaults.standard.data(forKey: storageKey),
           let decoded = try? JSONDecoder().decode([String: [Group]].self, from: data) {
            bag = decoded
        }
        bag[fid] = groups
        if let encoded = try? JSONEncoder().encode(bag) {
            UserDefaults.standard.set(encoded, forKey: storageKey)
        }
    }

    static func upsert(_ group: Group, familyId: String? = nil) {
        var groups = load(familyId: familyId)
        if let idx = groups.firstIndex(where: { $0.id == group.id }) {
            groups[idx] = group
        } else {
            groups.append(group)
        }
        save(groups, familyId: familyId)
    }

    static func delete(id: UUID, familyId: String? = nil) {
        var groups = load(familyId: familyId)
        groups.removeAll { $0.id == id }
        save(groups, familyId: familyId)
        if selectedFilterGroupId == id {
            selectedFilterGroupId = nil
        }
    }

    /// `nil` = whole family (default).
    static var selectedFilterGroupId: UUID? {
        get {
            guard let raw = UserDefaults.standard.string(forKey: selectedFilterKey),
                  let id = UUID(uuidString: raw) else { return nil }
            return id
        }
        set {
            if let newValue {
                UserDefaults.standard.set(newValue.uuidString, forKey: selectedFilterKey)
            } else {
                UserDefaults.standard.removeObject(forKey: selectedFilterKey)
            }
        }
    }

    static func selectedGroup(familyId: String? = nil) -> Group? {
        guard let id = selectedFilterGroupId else { return nil }
        return load(familyId: familyId).first { $0.id == id }
    }

    static func loadRosterMembers() -> [FamilyMemberData] {
        _ = FamilyLocalStore.validatePersistedRosterAgainstCurrentFamily()
        guard let data = UserDefaults.standard.data(forKey: FamilyLocalStore.familyMembersKey),
              let members = try? JSONDecoder().decode([FamilyMemberData].self, from: data) else {
            return []
        }
        return members
    }

    private static func resolvedFamilyId(_ explicit: String?) -> String {
        let trimmed = (explicit ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty { return trimmed }
        return FamilyLocalStore.loadPersistedFamilyId()
    }
}
