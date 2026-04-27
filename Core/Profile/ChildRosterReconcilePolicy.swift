import Foundation

// MARK: - Phase 7.2 — child roster cross-device reconcile policy

@MainActor
enum ChildRosterReconcilePolicy {
    enum MergeStrategy: Sendable {
        case serverWins
        case localWins
        case latestUpdatedAt
    }

    struct ReconcileResult: Sendable {
        let profiles: [ChildProfile]
        let summary: String
        let conflicts: Int
        let mergeStrategy: MergeStrategy
    }

    static func reconcile(
        existingProfiles: [ChildProfile],
        serverMembers: [FamilyMemberResponse],
        familyId: String?,
        removeMissingServerLinkedChildren: Bool,
        mergeStrategy: MergeStrategy = .latestUpdatedAt,
        serverSnapshotAt: Date = Date()
    ) -> ReconcileResult {
        let childRoles: Set<String> = ["child", "teenager", "teen"]
        let serverChildren = serverMembers.filter { childRoles.contains($0.role.lowercased()) }
        let serverIds = Set(serverChildren.map(\.id))

        var nextProfiles = existingProfiles
        var inserted = 0
        var updated = 0
        var removed = 0
        var conflicts = 0

        for member in serverChildren {
            let roleLower = member.role.lowercased()
            let serverAgeGroup: ChildAgeGroup? = {
                if roleLower == "teenager" || roleLower == "teen" { return .tween11to13 }
                if roleLower == "child" { return .school7to10 }
                return nil
            }()
            let normalizedServerName = member.name.trimmingCharacters(in: .whitespacesAndNewlines)
            let normalizedServerAvatar = member.avatar?.trimmingCharacters(in: .whitespacesAndNewlines)
            let serverId = member.id.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !serverId.isEmpty else { continue }

            if let idx = nextProfiles.firstIndex(where: { ($0.serverUserId ?? "").trimmingCharacters(in: .whitespacesAndNewlines) == serverId }) {
                var current = nextProfiles[idx]
                let hadConflict =
                    current.displayName.trimmingCharacters(in: .whitespacesAndNewlines) != normalizedServerName ||
                    ((current.avatarKey ?? "").trimmingCharacters(in: .whitespacesAndNewlines) != (normalizedServerAvatar ?? "")) ||
                    (serverAgeGroup != nil && current.ageGroup != serverAgeGroup)
                if hadConflict { conflicts += 1 }

                let shouldUseServer: Bool = {
                    switch mergeStrategy {
                    case .serverWins:
                        return true
                    case .localWins:
                        return !hadConflict
                    case .latestUpdatedAt:
                        let localTs = current.updatedAt
                        return serverSnapshotAt >= localTs
                    }
                }()

                if shouldUseServer {
                    current.displayName = normalizedServerName.isEmpty ? current.displayName : normalizedServerName
                    current.familyId = familyId ?? current.familyId
                    if let normalizedServerAvatar, !normalizedServerAvatar.isEmpty {
                        current.avatarKey = normalizedServerAvatar
                    }
                    if let serverAgeGroup {
                        current.ageGroup = serverAgeGroup
                    }
                    current.lastServerUpdatedAt = serverSnapshotAt
                }
                current.updatedAt = Date()
                current.version = max(1, current.version) + 1
                nextProfiles[idx] = current
                updated += 1
            } else {
                let newProfile = ChildProfile(
                    displayName: normalizedServerName.isEmpty ? "Child" : normalizedServerName,
                    serverUserId: serverId,
                    familyId: familyId,
                    ageGroup: serverAgeGroup,
                    avatarKey: normalizedServerAvatar,
                    version: 1,
                    lastServerUpdatedAt: serverSnapshotAt
                )
                nextProfiles.append(newProfile)
                inserted += 1
            }
        }

        if removeMissingServerLinkedChildren, !serverChildren.isEmpty {
            let before = nextProfiles.count
            nextProfiles.removeAll { profile in
                guard let sid = profile.serverUserId?.trimmingCharacters(in: .whitespacesAndNewlines), !sid.isEmpty else {
                    return false
                }
                return !serverIds.contains(sid)
            }
            removed = max(0, before - nextProfiles.count)
        }

        let summary = "serverChildren=\(serverChildren.count) inserted=\(inserted) updated=\(updated) removed=\(removed) conflicts=\(conflicts) strategy=\(describe(mergeStrategy))"
        return ReconcileResult(profiles: nextProfiles, summary: summary, conflicts: conflicts, mergeStrategy: mergeStrategy)
    }

    private static func describe(_ strategy: MergeStrategy) -> String {
        switch strategy {
        case .serverWins: return "serverWins"
        case .localWins: return "localWins"
        case .latestUpdatedAt: return "latestUpdatedAt"
        }
    }
}
