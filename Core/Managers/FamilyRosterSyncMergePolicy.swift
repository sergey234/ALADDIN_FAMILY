import Foundation

/// Чистая политика выбора источника финального ростера после `GET /api/family/members`
/// (ветвление из `FamilyScreen.syncFamilyMembersFromAPI` — правки логики здесь и в вызове экрана).
enum FamilyRosterSyncMergePolicy {

    enum FinalSource: String, Equatable {
        case merged
        case convertedOnly
    }

    struct ComputedFlags: Equatable {
        let isServerSubset: Bool
        let serverFamilyContextConfirmed: Bool
        let effectivePartialSubset: Bool
    }

    static func computeFlags(
        serverIds: Set<String>,
        localIds: Set<String>,
        serverListNonEmpty: Bool,
        storedFamilyId: String,
        lastResolvedFamilyId: String
    ) -> ComputedFlags {
        let isServerSubset = serverIds.isSubset(of: localIds)
            && serverIds.count < localIds.count
            && serverListNonEmpty

        let s = storedFamilyId.trimmingCharacters(in: .whitespacesAndNewlines)
        let r = lastResolvedFamilyId.trimmingCharacters(in: .whitespacesAndNewlines)
        let serverFamilyContextConfirmed = !s.isEmpty && !r.isEmpty && s == r
        let effectivePartialSubset = isServerSubset && !serverFamilyContextConfirmed

        return ComputedFlags(
            isServerSubset: isServerSubset,
            serverFamilyContextConfirmed: serverFamilyContextConfirmed,
            effectivePartialSubset: effectivePartialSubset
        )
    }

    static func chooseFinalSource(
        flags: ComputedFlags,
        partialRetryCount: Int,
        hasKnownServerMembersInLocal: Bool,
        /// Локально есть родитель/пожилой, но ни один из его id не пришёл в текущем ответе сервера — нельзя схлопывать ростер до «только сервер».
        localParentOrElderMissingFromServer: Bool = false
    ) -> (source: FinalSource, mergeOutcome: String) {
        if localParentOrElderMissingFromServer {
            return (.merged, "keep_merged_parent_elder_missing_from_server_subset")
        }
        if flags.effectivePartialSubset && partialRetryCount >= 3 && !hasKnownServerMembersInLocal {
            return (.convertedOnly, "server_truth_after_retries_no_known_server_ids")
        }
        if flags.effectivePartialSubset {
            return (.merged, "keep_merged_partial_subset")
        }
        if flags.isServerSubset && flags.serverFamilyContextConfirmed {
            return (.merged, "keep_merged_subset_confirmed_context_no_server_only_prune")
        }
        return (.merged, "merged_default")
    }

    /// Не удалять связанных детей из `ChildProfile` при ответе-субсете id относительно локального ростера.
    static func shouldRemoveMissingServerLinkedChildren(
        serverMemberIds: [String],
        localMemberIds: [String]
    ) -> Bool {
        guard !serverMemberIds.isEmpty else { return false }
        let serverSet = Set(serverMemberIds)
        let localSet = Set(localMemberIds)
        let isSubset = serverSet.isSubset(of: localSet) && serverSet.count < localSet.count
        return !isSubset
    }
}
