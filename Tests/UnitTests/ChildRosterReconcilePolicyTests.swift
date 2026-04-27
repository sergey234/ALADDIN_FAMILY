import XCTest
@testable import ALADDIN

@MainActor
final class ChildRosterReconcilePolicyTests: XCTestCase {

    func testReconcileInsertAddsNewServerLinkedChildProfile() {
        let result = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [],
            serverMembers: [
                FamilyMemberResponse(
                    id: "srv-child-1",
                    name: "Alice",
                    role: "child",
                    avatar: "👧",
                    status: "protected",
                    threatsBlocked: nil,
                    lastActive: nil,
                    devices: nil
                )
            ],
            familyId: "fam-1",
            removeMissingServerLinkedChildren: true
        )

        XCTAssertEqual(result.profiles.count, 1)
        XCTAssertEqual(result.profiles.first?.serverUserId, "srv-child-1")
        XCTAssertEqual(result.profiles.first?.displayName, "Alice")
        XCTAssertEqual(result.profiles.first?.familyId, "fam-1")
        XCTAssertTrue(result.summary.contains("inserted=1"))
        XCTAssertTrue(result.summary.contains("updated=0"))
    }

    func testReconcileUpdateUsesServerAuthoritativeFieldsAndCountsConflict() {
        let existing = ChildProfile(
            displayName: "Old Name",
            serverUserId: "srv-child-2",
            familyId: "fam-old",
            ageGroup: .school7to10,
            avatarKey: "🙂"
        )

        let result = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [existing],
            serverMembers: [
                FamilyMemberResponse(
                    id: "srv-child-2",
                    name: "New Name",
                    role: "teenager",
                    avatar: "🧒",
                    status: "protected",
                    threatsBlocked: nil,
                    lastActive: nil,
                    devices: nil
                )
            ],
            familyId: "fam-new",
            removeMissingServerLinkedChildren: true
        )

        XCTAssertEqual(result.profiles.count, 1)
        XCTAssertEqual(result.profiles[0].displayName, "New Name")
        XCTAssertEqual(result.profiles[0].avatarKey, "🧒")
        XCTAssertEqual(result.profiles[0].ageGroup, .tween11to13)
        XCTAssertEqual(result.profiles[0].familyId, "fam-new")
        XCTAssertTrue(result.summary.contains("updated=1"))
        XCTAssertTrue(result.summary.contains("conflicts=1"))
        XCTAssertEqual(result.conflicts, 1)
        XCTAssertEqual(result.mergeStrategy, .latestUpdatedAt)
        XCTAssertGreaterThanOrEqual(result.profiles[0].version, 2)
    }

    func testReconcileConflictWithLocalWinsKeepsLocalProfileFields() {
        let existing = ChildProfile(
            displayName: "Local Name",
            serverUserId: "srv-child-3",
            familyId: "fam-old",
            ageGroup: .school7to10,
            avatarKey: "🙂",
            version: 3
        )

        let result = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [existing],
            serverMembers: [
                FamilyMemberResponse(
                    id: "srv-child-3",
                    name: "Server Name",
                    role: "teenager",
                    avatar: "🧒",
                    status: "protected",
                    threatsBlocked: nil,
                    lastActive: nil,
                    devices: nil
                )
            ],
            familyId: "fam-new",
            removeMissingServerLinkedChildren: false,
            mergeStrategy: .localWins
        )

        XCTAssertEqual(result.profiles.count, 1)
        XCTAssertEqual(result.profiles[0].displayName, "Local Name")
        XCTAssertEqual(result.profiles[0].avatarKey, "🙂")
        XCTAssertEqual(result.profiles[0].ageGroup, .school7to10)
        XCTAssertEqual(result.mergeStrategy, .localWins)
        XCTAssertEqual(result.conflicts, 1)
    }

    func testReconcileRemoveDeletesMissingServerLinkedProfilesOnly() {
        let linked = ChildProfile(displayName: "Linked", serverUserId: "srv-linked", familyId: "fam-1")
        let localOnly = ChildProfile(displayName: "Draft Local", serverUserId: nil, familyId: "fam-1")

        let result = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [linked, localOnly],
            serverMembers: [],
            familyId: "fam-1",
            removeMissingServerLinkedChildren: true
        )

        XCTAssertEqual(result.profiles.count, 2, "Empty server list must not trigger removals.")

        let resultWithServer = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [linked, localOnly],
            serverMembers: [
                FamilyMemberResponse(
                    id: "srv-other",
                    name: "Another Child",
                    role: "child",
                    avatar: nil,
                    status: "protected",
                    threatsBlocked: nil,
                    lastActive: nil,
                    devices: nil
                )
            ],
            familyId: "fam-1",
            removeMissingServerLinkedChildren: true
        )

        XCTAssertEqual(resultWithServer.profiles.contains(where: { $0.serverUserId == "srv-linked" }), false)
        XCTAssertEqual(resultWithServer.profiles.contains(where: { $0.serverUserId == nil && $0.displayName == "Draft Local" }), true)
        XCTAssertTrue(resultWithServer.summary.contains("removed=1"))
    }

    func testReconcileWithoutRemoveFlagKeepsMissingServerLinkedProfiles() {
        let linked = ChildProfile(displayName: "Linked", serverUserId: "srv-linked", familyId: "fam-1")

        let result = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [linked],
            serverMembers: [
                FamilyMemberResponse(
                    id: "srv-other",
                    name: "Another Child",
                    role: "child",
                    avatar: nil,
                    status: "protected",
                    threatsBlocked: nil,
                    lastActive: nil,
                    devices: nil
                )
            ],
            familyId: "fam-1",
            removeMissingServerLinkedChildren: false
        )

        XCTAssertTrue(result.profiles.contains(where: { $0.serverUserId == "srv-linked" }))
        XCTAssertTrue(result.summary.contains("removed=0"))
    }

    func testUnifiedFamilyPermissionsChildParentElderlyScenario() {
        let defaults = UserDefaults(suiteName: "FamilyPermissionLayerTests")!
        defaults.removePersistentDomain(forName: "FamilyPermissionLayerTests")

        let members = [
            makeMember(id: "mem-parent", role: .parent, name: "Parent"),
            makeMember(id: "mem-child", role: .child, name: "Child"),
            makeMember(id: "mem-elderly", role: .elderly, name: "Grandma")
        ]

        defaults.set("mem-child", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let childSnapshot = FamilyPermissionLayer.snapshot(members: members, defaults: defaults)
        XCTAssertEqual(childSnapshot.actorRole, .child)
        XCTAssertFalse(childSnapshot.canEditContacts)
        XCTAssertFalse(childSnapshot.canManageFamilyLimits)
        XCTAssertFalse(childSnapshot.canManageCriticalFamilySettings)

        defaults.set("mem-parent", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let parentSnapshot = FamilyPermissionLayer.snapshot(members: members, defaults: defaults)
        XCTAssertEqual(parentSnapshot.actorRole, .parent)
        XCTAssertTrue(parentSnapshot.canEditContacts)
        XCTAssertTrue(parentSnapshot.canManageFamilyLimits)
        XCTAssertTrue(parentSnapshot.canManageCriticalFamilySettings)

        defaults.set("mem-elderly", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let elderlySnapshot = FamilyPermissionLayer.snapshot(members: members, defaults: defaults)
        XCTAssertEqual(elderlySnapshot.actorRole, .elderly)
        XCTAssertTrue(elderlySnapshot.canEditContacts)
        XCTAssertTrue(elderlySnapshot.canManageFamilyLimits)
        XCTAssertTrue(elderlySnapshot.canManageCriticalFamilySettings)
    }

    func testUnifiedFamilyRosterProjectsConsistentContactsForChildAndElderly() {
        let members = [
            makeMember(id: "srv-parent-42", role: .parent, name: "Parent"),
            makeMember(id: "srv-child-43", role: .child, name: "Child"),
            makeMember(id: "srv-elderly-44", role: .elderly, name: "Grandma")
        ]

        let childProjections = UnifiedFamilyRoster.contactProjections(audience: .child, members: members)
        let elderlyProjections = UnifiedFamilyRoster.contactProjections(audience: .elderly, members: members)

        XCTAssertEqual(childProjections.count, 3)
        XCTAssertEqual(elderlyProjections.count, 3)
        XCTAssertTrue(childProjections.allSatisfy { $0.phone.hasPrefix("+7 (999) 000-00-") })
        XCTAssertTrue(elderlyProjections.allSatisfy { $0.phone.hasPrefix("+7 (999) 000-00-") })

        let childElderlyRelationKey = childProjections.first(where: { $0.name == "Grandma" })?.relationLocalizationKey
        let elderlySelfRelationKey = elderlyProjections.first(where: { $0.name == "Grandma" })?.relationLocalizationKey
        XCTAssertEqual(childElderlyRelationKey, "family_role_elderly_label")
        XCTAssertEqual(elderlySelfRelationKey, "elderly_family_relation_you")
    }

    private func makeMember(id: String, role: FamilyMemberCard.FamilyRole, name: String) -> FamilyMemberData {
        FamilyMemberData(
            id: id,
            serverMemberId: id,
            localOnly: false,
            name: name,
            role: role,
            avatar: "🙂",
            status: .protected,
            threatsBlocked: 0,
            lastActive: ""
        )
    }
}
