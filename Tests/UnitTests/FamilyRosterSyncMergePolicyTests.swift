import XCTest
@testable import ALADDIN

@MainActor
final class FamilyRosterSyncMergePolicyTests: XCTestCase {

    func test_subsetWithConfirmedContext_keepsMerged_notServerOnly() {
        let server = ["MEM_CHILD"]
        let local = ["MEM_PARENT", "MEM_CHILD"]
        let flags = FamilyRosterSyncMergePolicy.computeFlags(
            serverIds: Set(server),
            localIds: Set(local),
            serverListNonEmpty: true,
            storedFamilyId: "fam_1",
            lastResolvedFamilyId: "fam_1"
        )
        XCTAssertTrue(flags.isServerSubset)
        XCTAssertTrue(flags.serverFamilyContextConfirmed)
        XCTAssertFalse(flags.effectivePartialSubset)

        let (source, outcome) = FamilyRosterSyncMergePolicy.chooseFinalSource(
            flags: flags,
            partialRetryCount: 0,
            hasKnownServerMembersInLocal: true,
            localParentOrElderMissingFromServer: false
        )
        XCTAssertEqual(source, .merged)
        XCTAssertEqual(outcome, "keep_merged_subset_confirmed_context_no_server_only_prune")
    }

    func test_partialSubset_unconfirmedContext_keepsMerged() {
        let server = ["MEM_CHILD"]
        let local = ["MEM_PARENT", "MEM_CHILD"]
        let flags = FamilyRosterSyncMergePolicy.computeFlags(
            serverIds: Set(server),
            localIds: Set(local),
            serverListNonEmpty: true,
            storedFamilyId: "fam_1",
            lastResolvedFamilyId: ""
        )
        XCTAssertTrue(flags.effectivePartialSubset)

        let (source, outcome) = FamilyRosterSyncMergePolicy.chooseFinalSource(
            flags: flags,
            partialRetryCount: 0,
            hasKnownServerMembersInLocal: true,
            localParentOrElderMissingFromServer: false
        )
        XCTAssertEqual(source, .merged)
        XCTAssertEqual(outcome, "keep_merged_partial_subset")
    }

    func test_partialSubset_afterRetriesWithoutServerIds_acceptsConvertedOnly() {
        let server = ["MEM_CHILD"]
        let local = ["MEM_LOCAL_ONLY", "MEM_CHILD"]
        let flags = FamilyRosterSyncMergePolicy.computeFlags(
            serverIds: Set(server),
            localIds: Set(local),
            serverListNonEmpty: true,
            storedFamilyId: "fam_1",
            lastResolvedFamilyId: ""
        )
        XCTAssertTrue(flags.effectivePartialSubset)

        let (source, outcome) = FamilyRosterSyncMergePolicy.chooseFinalSource(
            flags: flags,
            partialRetryCount: 3,
            hasKnownServerMembersInLocal: false,
            localParentOrElderMissingFromServer: false
        )
        XCTAssertEqual(source, .convertedOnly)
        XCTAssertEqual(outcome, "server_truth_after_retries_no_known_server_ids")
    }

    func test_partialSubset_parentMissingFromServer_neverConvertedOnlyEvenAfterRetries() {
        let server = ["MEM_CHILD"]
        let local = ["MEM_PARENT", "MEM_CHILD"]
        let flags = FamilyRosterSyncMergePolicy.computeFlags(
            serverIds: Set(server),
            localIds: Set(local),
            serverListNonEmpty: true,
            storedFamilyId: "fam_1",
            lastResolvedFamilyId: ""
        )
        XCTAssertTrue(flags.effectivePartialSubset)

        let (source, outcome) = FamilyRosterSyncMergePolicy.chooseFinalSource(
            flags: flags,
            partialRetryCount: 3,
            hasKnownServerMembersInLocal: false,
            localParentOrElderMissingFromServer: true
        )
        XCTAssertEqual(source, .merged)
        XCTAssertEqual(outcome, "keep_merged_parent_elder_missing_from_server_subset")
    }

    func test_shouldRemoveMissingServerLinkedChildren_falseWhenServerSubset() {
        XCTAssertFalse(
            FamilyRosterSyncMergePolicy.shouldRemoveMissingServerLinkedChildren(
                serverMemberIds: ["A"],
                localMemberIds: ["A", "B"]
            )
        )
    }

    func test_shouldRemoveMissingServerLinkedChildren_trueWhenFullOrSuperset() {
        XCTAssertTrue(
            FamilyRosterSyncMergePolicy.shouldRemoveMissingServerLinkedChildren(
                serverMemberIds: ["A", "B"],
                localMemberIds: ["A", "B"]
            )
        )
        XCTAssertTrue(
            FamilyRosterSyncMergePolicy.shouldRemoveMissingServerLinkedChildren(
                serverMemberIds: ["A", "B", "C"],
                localMemberIds: ["A", "B"]
            )
        )
    }
}
