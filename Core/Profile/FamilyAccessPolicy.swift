import Foundation

// MARK: - Phase 7.2 — единая политика доступа семьи

/// Централизует клиентские правила:
/// - app-level профили детей (`ChildProfile` / roster actions),
/// - Family Sharing операции (подписки / покупки / Ask to Buy).
///
/// Экранный код не должен самостоятельно интерпретировать `UserDefaults` для прав.
enum FamilyAccessPolicy {
    enum ActorRole: String, Sendable {
        case parent
        case elderly
        case child
        case teenager
        case unknown
    }

    /// Централизованный набор разрешений для семейного/родительского домена (Phase 7.2).
    enum Permission: Sendable {
        case manageAppProfiles
        case manageFamilySharing
        case editFamilyContacts
        case manageFamilyLimits
        case manageCriticalFamilySettings
        case performSensitiveFamilyAction
        case manageParentalControls
        case viewParentalDashboard
    }

    static func resolveActorRole(
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> ActorRole {
        let myMemberId = defaults.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""

        if !myMemberId.isEmpty,
           let me = members.first(where: { row in
               let sid = row.serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
               let rid = row.id.trimmingCharacters(in: .whitespacesAndNewlines)
               let canon = row.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
               return rid == myMemberId || (!sid.isEmpty && sid == myMemberId) || (!canon.isEmpty && canon == myMemberId)
           }) {
            switch me.role {
            case .parent: return .parent
            case .elderly: return .elderly
            case .child: return .child
            case .teenager: return .teenager
            }
        }

        // Мягкий fallback для onboarding / временного рассинха roster<->identity.
        let fallback = (defaults.string(forKey: "current_user_role") ?? "").lowercased()
        if fallback.contains("parent") || fallback.contains("родител") { return .parent }
        if fallback.contains("elderly") || fallback.contains("пожил") { return .elderly }
        if fallback.contains("teen") || fallback.contains("подрост") { return .teenager }
        if fallback.contains("child") || fallback.contains("реб") { return .child }
        return .unknown
    }

    /// Управление app-level профилями детей (добавление/удаление в roster).
    static func canManageAppProfiles(
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> Bool {
        let role = resolveActorRole(members: members, defaults: defaults)
        return role == .parent || role == .elderly
    }

    /// Family Sharing операции (подписка / покупки / Ask to Buy).
    /// Разделяем от app-level профилей: здесь доступ только у parent.
    static func canManageFamilySharing(
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> Bool {
        resolveActorRole(members: members, defaults: defaults) == .parent
    }

    static func hasPermission(
        _ permission: Permission,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> Bool {
        let role = resolveActorRole(members: members, defaults: defaults)
        switch permission {
        case .manageAppProfiles:
            return role == .parent || role == .elderly
        case .manageFamilySharing:
            return role == .parent
        case .editFamilyContacts:
            return role == .parent || role == .elderly
        case .manageFamilyLimits:
            return role == .parent || role == .elderly
        case .manageCriticalFamilySettings:
            return role == .parent || role == .elderly
        case .performSensitiveFamilyAction:
            // Для app-level roster критичные действия доступны parent/elderly + взрослый session gate.
            return role == .parent || role == .elderly
        case .manageParentalControls:
            return role == .parent || role == .elderly
        case .viewParentalDashboard:
            return role == .parent || role == .elderly
        }
    }
}

/// Phase 9.3: shared permission layer consumed by child + elderly interfaces.
enum FamilyPermissionLayer {
    struct Snapshot: Sendable {
        let actorRole: FamilyAccessPolicy.ActorRole
        let canEditContacts: Bool
        let canManageFamilyLimits: Bool
        let canManageCriticalFamilySettings: Bool
    }

    static func snapshot(
        members: [FamilyMemberData] = UnifiedFamilyRoster.load(),
        defaults: UserDefaults = .standard
    ) -> Snapshot {
        let actorRole = FamilyAccessPolicy.resolveActorRole(members: members, defaults: defaults)
        return Snapshot(
            actorRole: actorRole,
            canEditContacts: FamilyAccessPolicy.hasPermission(.editFamilyContacts, members: members, defaults: defaults),
            canManageFamilyLimits: FamilyAccessPolicy.hasPermission(.manageFamilyLimits, members: members, defaults: defaults),
            canManageCriticalFamilySettings: FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members, defaults: defaults)
        )
    }
}

/// Phase 9.3: single roster model reused by child and elderly interfaces.
enum UnifiedFamilyRoster {
    static let rosterKey = FamilyLocalStore.familyMembersKey
    static let phoneDirectoryKey = "family_member_phone_directory_v1"

    struct ContactProjection {
        let id: UUID
        let name: String
        let phone: String
        let relationLocalizationKey: String
        let memberCanonicalId: String
    }

    enum Audience {
        case child
        case elderly
    }

    static func load(defaults: UserDefaults = .standard) -> [FamilyMemberData] {
        guard let raw = defaults.data(forKey: rosterKey),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: raw) else {
            return []
        }
        return decoded
    }

    static func relationLocalizationKey(for role: FamilyMemberCard.FamilyRole, audience: Audience) -> String {
        switch (audience, role) {
        case (.elderly, .parent):
            return "elderly_family_role_parent"
        case (.elderly, .child):
            return "elderly_family_relation_son"
        case (.elderly, .teenager):
            return "elderly_family_role_teenager"
        case (.elderly, .elderly):
            return "elderly_family_relation_you"
        case (.child, .parent):
            return "elderly_family_role_parent"
        case (.child, .child):
            return "elderly_family_role_child"
        case (.child, .teenager):
            return "elderly_family_role_teenager"
        case (.child, .elderly):
            return "family_role_elderly_label"
        }
    }

    static func fallbackPhone(for member: FamilyMemberData) -> String {
        let source = (member.serverMemberId ?? member.id)
        let digits = source.filter(\.isNumber)
        let tail = String(digits.suffix(2)).padding(toLength: 2, withPad: "0", startingAt: 0)
        return "+7 (999) 000-00-\(tail)"
    }

    static func stableContactId(for canonicalId: String) -> UUID {
        // Deterministic UUID based on canonical roster ID.
        let ascii = canonicalId.utf8.map { Int($0) }
        var bytes = [UInt8](repeating: 0, count: 16)
        for (idx, value) in ascii.enumerated() {
            bytes[idx % 16] = bytes[idx % 16] &+ UInt8(value % 256)
        }
        bytes[6] = (bytes[6] & 0x0F) | 0x40
        bytes[8] = (bytes[8] & 0x3F) | 0x80
        let uuid = uuid_t(bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7], bytes[8], bytes[9], bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15])
        return UUID(uuid: uuid)
    }

    static func persistPhoneDirectory(
        entriesByContactId: [UUID: String],
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) {
        let uuidToCanonical: [UUID: String] = Dictionary(
            uniqueKeysWithValues: members.map { member in
                (stableContactId(for: member.canonicalId), member.canonicalId)
            }
        )
        var current = phoneDirectory(defaults: defaults)
        for (contactId, phone) in entriesByContactId {
            guard let canonical = uuidToCanonical[contactId] else { continue }
            let trimmed = phone.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty {
                current.removeValue(forKey: canonical)
            } else {
                current[canonical] = trimmed
            }
        }
        guard let encoded = try? JSONEncoder().encode(current) else { return }
        defaults.set(encoded, forKey: phoneDirectoryKey)
    }

    static func phoneDirectory(defaults: UserDefaults = .standard) -> [String: String] {
        guard let raw = defaults.data(forKey: phoneDirectoryKey),
              let decoded = try? JSONDecoder().decode([String: String].self, from: raw) else {
            return [:]
        }
        return decoded
    }

    static func contactProjections(
        audience: Audience,
        members: [FamilyMemberData],
        defaults: UserDefaults = .standard
    ) -> [ContactProjection] {
        let phoneMap = phoneDirectory(defaults: defaults)
        return members.map { member in
            let canonicalId = member.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
            let normalizedCanonicalId = canonicalId.isEmpty ? member.id : canonicalId
            let phone = phoneMap[normalizedCanonicalId] ?? fallbackPhone(for: member)
            return ContactProjection(
                id: stableContactId(for: normalizedCanonicalId),
                name: member.name,
                phone: phone,
                relationLocalizationKey: relationLocalizationKey(for: member.role, audience: audience),
                memberCanonicalId: normalizedCanonicalId
            )
        }
    }
}

