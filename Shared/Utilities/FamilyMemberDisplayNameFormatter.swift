import Foundation

/// W2 UX36 — display names follow app language (never leave "Parent A" on RU UI).
enum FamilyMemberDisplayNameFormatter {
    private static let knownRolePrefixes = [
        "Родитель", "Ребенок", "Ребёнок", "Подросток", "Пожилой", "Люди 60+",
        "Parent", "Child", "Teenager", "Teen", "Elderly", "People 60+", "Grandparent"
    ]

    static func displayName(
        storedName: String,
        role: FamilyMemberCard.FamilyRole? = nil,
        localization: LocalizationManager = .shared
    ) -> String {
        let trimmed = storedName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return role.map { localizedRole($0, localization: localization) }
                ?? localization.localized("family_role_parent_label")
        }

        for known in knownRolePrefixes {
            if trimmed.caseInsensitiveCompare(known) == .orderedSame {
                return localizedRole(matching: known, fallback: role, localization: localization)
            }
            let prefix = "\(known) "
            if trimmed.lowercased().hasPrefix(prefix.lowercased()) {
                let suffix = String(trimmed.dropFirst(known.count).drop(while: { $0 == " " }))
                let roleLabel = localizedRole(matching: known, fallback: role, localization: localization)
                if suffix.isEmpty { return roleLabel }
                return "\(roleLabel) \(suffix)"
            }
        }

        return trimmed
    }

    private static func localizedRole(
        _ role: FamilyMemberCard.FamilyRole,
        localization: LocalizationManager
    ) -> String {
        switch role {
        case .parent: return localization.localized("family_role_parent_label")
        case .child: return localization.localized("family_role_child_label")
        case .teenager: return localization.localized("family_role_teen_label")
        case .elderly: return localization.localized("family_role_elderly_label")
        }
    }

    private static func localizedRole(
        matching known: String,
        fallback: FamilyMemberCard.FamilyRole?,
        localization: LocalizationManager
    ) -> String {
        let lower = known.lowercased()
        if lower.hasPrefix("parent") || lower.hasPrefix("родител") {
            return localization.localized("family_role_parent_label")
        }
        if lower.hasPrefix("child") || lower.hasPrefix("ребен") || lower.hasPrefix("ребён") {
            return localization.localized("family_role_child_label")
        }
        if lower.hasPrefix("teen") || lower.hasPrefix("подрост") {
            return localization.localized("family_role_teen_label")
        }
        if lower.hasPrefix("elder") || lower.hasPrefix("grand") || lower.hasPrefix("пожил") || lower.contains("60") {
            return localization.localized("family_role_elderly_label")
        }
        if let fallback {
            return localizedRole(fallback, localization: localization)
        }
        return localization.localized("family_role_parent_label")
    }
}
