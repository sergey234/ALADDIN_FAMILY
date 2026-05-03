import Foundation

/// A1 / fam-1: последний снимок синка `GET /api/family/members` без Xcode-логов.
/// Файл: **Documents/family_sync_last.json** (Файлы → On My iPhone → ALADDIN).
/// Без имён — только id, роли, флаги merge и снимок `UserDefaults` ключа ростера.
enum FamilySyncDebugSnapshot {
    private static let filename = "family_sync_last.json"

    struct Flags: Encodable {
        let skipCrossFamilyMerge: Bool
        let effectivePartialSubset: Bool
        let isServerSubset: Bool
        let serverFamilyContextConfirmed: Bool
        let mergeOutcome: String
        let partialRetryCountAtDecision: Int
        let storedFamilyId: String
        let lastResolvedFamilyId: String
    }

    private struct ServerRow: Encodable {
        let id: String
        let role: String
    }

    private struct RosterRow: Encodable {
        let id: String
        let role: String
        let serverMemberId: String?
        let localOnly: Bool?
        let isCurrentUser: Bool
    }

    private struct Payload: Encodable {
        let capturedAt: String
        let endpoint: String
        let userDefaultsKeys: KeysRef
        let yourMemberId: String?
        let currentUserRole: String?
        let flags: Flags
        let serverMembersGET: [ServerRow]
        let localBefore: [RosterRow]
        let localAfterInMemory: [RosterRow]
        let decodedFromFamilyMembersListKey: [RosterRow]?
        let note: String
    }

    private struct KeysRef: Encodable {
        let familyMembersList: String
        let yourMemberId: String
        let currentUserRole: String
    }

    static func writeAfterFamilyMembersSync(
        serverMembers: [FamilyMemberResponse],
        localBefore: [FamilyMemberData],
        localAfter: [FamilyMemberData],
        flags: Flags
    ) {
        let defaults = UserDefaults.standard
        let yourId = defaults.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let role = defaults.string(forKey: "current_user_role")
        let decodedRows: [RosterRow]? = {
            guard let data = defaults.data(forKey: FamilyLocalStore.familyMembersKey),
                  let list = try? JSONDecoder().decode([FamilyMemberData].self, from: data)
            else { return nil }
            return list.map { RosterRow(id: $0.id, role: $0.role.rawValue, serverMemberId: $0.serverMemberId, localOnly: $0.localOnly, isCurrentUser: $0.isCurrentUser) }
        }()

        let payload = Payload(
            capturedAt: ISO8601DateFormatter().string(from: Date()),
            endpoint: AppConfig.Endpoint.familyMembers,
            userDefaultsKeys: KeysRef(
                familyMembersList: FamilyLocalStore.familyMembersKey,
                yourMemberId: FamilyLocalStore.yourMemberIdUserDefaultsKey,
                currentUserRole: "current_user_role"
            ),
            yourMemberId: yourId,
            currentUserRole: role,
            flags: flags,
            serverMembersGET: serverMembers.map { ServerRow(id: $0.id, role: $0.role) },
            localBefore: localBefore.map { RosterRow(id: $0.id, role: $0.role.rawValue, serverMemberId: $0.serverMemberId, localOnly: $0.localOnly, isCurrentUser: $0.isCurrentUser) },
            localAfterInMemory: localAfter.map { RosterRow(id: $0.id, role: $0.role.rawValue, serverMemberId: $0.serverMemberId, localOnly: $0.localOnly, isCurrentUser: $0.isCurrentUser) },
            decodedFromFamilyMembersListKey: decodedRows,
            note: "mergeOutcome keep_merged_subset_confirmed_context_no_server_only_prune means server had fewer ids than local but roster was NOT replaced with server-only list (safe after add-child races)."
        )

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        guard let data = try? encoder.encode(payload) else { return }

        DispatchQueue.global(qos: .utility).async {
            guard let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else { return }
            let url = dir.appendingPathComponent(filename, isDirectory: false)
            try? data.write(to: url, options: [.atomic])
        }
    }
}
