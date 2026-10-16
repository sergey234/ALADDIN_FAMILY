import Foundation

/// SSOT: who may collect/apply Apple Screen Time in ALADDIN.
///
/// ## Age taxonomies in the app (must stay aligned)
///
/// | Band (canonical) | Child UI (`08`)     | Parental / Family modal | ContentAgeBand       | Reg. AgeGroup (server) |
/// |------------------|---------------------|-------------------------|----------------------|------------------------|
/// | kids             | kids (1–6)          | toddler (1–6 / 0–5)     | kids_1_6             | Toddler / Child        |
/// | school           | school (7–12)       | school (7–13 / 6–12)    | school_7_12          | Child (4–12)           |
/// | teen             | teen (13–17)        | teen (14–17 / 13–17)    | teen_13_17           | Teen (13–17)           |
/// | youngAdult       | youngAdult (18–22)  | adult (18+)             | youngAdult_18_22     | Adult (18–64)*         |
///
/// \* Registration `Adult` on a **child/teenager** role = supervised young adult / 20+.
///    Registration `Senior` + role `elderly` = **not** Screen Time.
///
/// ## Roles
/// Supervised: `child`, `teenager`/`teen`, `young_adult` (+ aliases).
/// Excluded: `parent`, `elderly` / `senior` / `grandparent`, admin/caregiver.
enum FamilyScreenTimeEligibility {
    static let ageGroupKey = "current_user_age_group"
    /// Parental Control modal / Family settings (`@AppStorage`).
    static let parentalAgeGroupKey = "parental_age_group"

    /// Canonical band ids used across Child UI + eligibility.
    enum CanonicalBand: String, CaseIterable {
        case kids
        case school
        case teen
        case youngAdult
    }

    private static let supervisedRoles: Set<String> = [
        "child",
        "teenager",
        "teen",
        "young_adult",
        "youngadult",
        "young-adult",
        "adult_child",
        "adultchild",
        "kid",
        "kids",
        "school"
    ]

    private static let excludedRoles: Set<String> = [
        "parent",
        "admin",
        "elderly",
        "grandparent",
        "senior",
        "caregiver"
    ]

    /// All tokens that mean a supervised child age band (any taxonomy).
    private static let supervisedAgeTokens: Set<String> = [
        // Canonical + Child UI
        "kids", "kid", "school", "teen", "teenager",
        "youngadult", "young_adult", "young-adult",
        // Parental / Family modal cases
        "toddler", "preschool", "elementary",
        "adult", // parental AgeGroup.adult = 18+ under family care (never alone without role check below)
        // Numeric / loc chips
        "1-6", "0-5", "0-3", "4-12", "7-12", "7-13", "6-12",
        "13-17", "14-17",
        "18+", "18-22", "18-64", "20+", "20-22", "24-55",
        // ContentAgeBand raw
        "kids_1_6", "school_7_12", "teen_13_17", "youngadult_18_22",
        // Registration display leftovers (normalized)
        "toddler(0-3)", "child(4-12)", "teen(13-17)", "adult(18-64)"
    ]

    // MARK: - Device (collect / apply / POST usage)

    /// Call on the phone that should run Monitor/Picker/Shield.
    static func isSupervisedDevice(
        role: String? = UserDefaults.standard.string(forKey: "current_user_role"),
        ageGroup: String? = nil
    ) -> Bool {
        let resolvedAge = ageGroup ?? resolvedStoredAgeGroup()
        let r = normalize(role)
        if r.isEmpty {
            // No role yet — only clear child bands (not bare parental "adult" alone).
            return isSupervisedAgeGroup(resolvedAge, allowParentalAdultAlone: false)
        }
        if excludedRoles.contains(r) { return false }
        if supervisedRoles.contains(r) { return true }
        return isSupervisedAgeGroup(resolvedAge, allowParentalAdultAlone: false)
    }

    // MARK: - Parent UI (lists / pull usage for member)

    static func isSupervisedMember(role: String?, ageGroup: String? = nil) -> Bool {
        let r = normalize(role)
        if excludedRoles.contains(r) { return false }
        if supervisedRoles.contains(r) { return true }
        if r.isEmpty {
            return isSupervisedAgeGroup(ageGroup, allowParentalAdultAlone: true)
        }
        return isSupervisedAgeGroup(ageGroup, allowParentalAdultAlone: true)
    }

    static func isSupervisedMember(role: FamilyMemberCard.FamilyRole) -> Bool {
        switch role {
        case .child, .teenager: return true
        case .parent, .elderly: return false
        }
    }

    static func isSupervisedAgeGroup(_ raw: String?, allowParentalAdultAlone: Bool = true) -> Bool {
        let a = normalize(raw)
        guard !a.isEmpty else { return false }
        if a == "adult" || a == "adult(18-64)" {
            return allowParentalAdultAlone
        }
        if supervisedAgeTokens.contains(a) { return true }
        if canonicalBand(from: raw) != nil { return true }
        // Fuzzy labels: "18-22 лет", "young adult", "малыш", etc.
        if a.contains("young") && a.contains("adult") { return true }
        if a.contains("toddler") || a.contains("малыш") || a.contains("preschool") { return true }
        if a.contains("school") || a.contains("школь") { return true }
        if a.contains("teen") || a.contains("подрост") { return true }
        if a.contains("1-6") || a.contains("7-12") || a.contains("7-13") || a.contains("13-17") || a.contains("14-17") {
            return true
        }
        if a.contains("18+") || a.contains("18-22") || a.contains("20+") { return true }
        return false
    }

    /// Map any taxonomy token → canonical band (kids / school / teen / youngAdult).
    static func canonicalBand(from raw: String?) -> CanonicalBand? {
        let a = normalize(raw)
        guard !a.isEmpty else { return nil }
        if ["kids", "kid", "toddler", "preschool", "1-6", "0-5", "0-3", "kids_1_6", "toddler(0-3)"].contains(a)
            || a.contains("малыш") {
            return .kids
        }
        if ["school", "elementary", "7-12", "7-13", "6-12", "4-12", "school_7_12", "child(4-12)"].contains(a)
            || a.contains("школь") {
            return .school
        }
        if ["teen", "teenager", "13-17", "14-17", "teen_13_17", "teen(13-17)"].contains(a)
            || a.contains("подрост") {
            return .teen
        }
        if [
            "youngadult", "young_adult", "young-adult", "adult", "adult_child", "adultchild",
            "18+", "18-22", "18-64", "20+", "20-22", "24-55",
            "youngadult_18_22", "adult(18-64)"
        ].contains(a) || (a.contains("young") && a.contains("adult")) {
            return .youngAdult
        }
        return nil
    }

    /// Prefer Child UI key; fall back to parental modal age.
    static func resolvedStoredAgeGroup() -> String? {
        if let v = UserDefaults.standard.string(forKey: ageGroupKey), !v.isEmpty { return v }
        if let v = UserDefaults.standard.string(forKey: parentalAgeGroupKey), !v.isEmpty { return v }
        return nil
    }

    /// Persist age band from ChildInterface (kids / school / teen / youngAdult).
    /// Does **not** overwrite `current_user_role` — Child UI keeps `child` for server/roster compat.
    static func persistAgeGroupFromChildInterface(_ age: String) {
        let token = childInterfaceAgeToken(age)
        guard !token.isEmpty else { return }
        UserDefaults.standard.set(token, forKey: ageGroupKey)
        // Keep parental modal key in sync when device is the child phone.
        if let band = canonicalBand(from: token) {
            let parentalRaw: String
            switch band {
            case .kids: parentalRaw = "toddler"
            case .school: parentalRaw = "school"
            case .teen: parentalRaw = "teen"
            case .youngAdult: parentalRaw = "adult"
            }
            UserDefaults.standard.set(parentalRaw, forKey: parentalAgeGroupKey)
        }
        if let ag = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) {
            ag.set(token, forKey: ageGroupKey)
        }
    }

    /// Token for ChildInterface `AgeGroup` cases → canonical string.
    static func childInterfaceAgeToken(_ caseName: String) -> String {
        switch normalize(caseName) {
        case "kids", "kid": return CanonicalBand.kids.rawValue
        case "school": return CanonicalBand.school.rawValue
        case "teen", "teenager": return CanonicalBand.teen.rawValue
        case "youngadult", "young_adult", "young-adult": return CanonicalBand.youngAdult.rawValue
        default:
            return canonicalBand(from: caseName)?.rawValue ?? caseName.trimmingCharacters(in: .whitespacesAndNewlines)
        }
    }

    private static func normalize(_ raw: String?) -> String {
        (raw ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .replacingOccurrences(of: " ", with: "")
    }
}
