import XCTest
@testable import ALADDIN

/// RWD: caregiver resolve из roster (FamilyAccessPolicy), не из «последнего экрана».
final class FamilyAccessPolicyCaregiverTests: XCTestCase {

    private var defaults: UserDefaults!
    private let suiteName = "FamilyAccessPolicyCaregiverTests.suite"

    override func setUp() {
        super.setUp()
        defaults = UserDefaults(suiteName: suiteName)
        defaults.removePersistentDomain(forName: suiteName)
    }

    override func tearDown() {
        defaults.removePersistentDomain(forName: suiteName)
        defaults = nil
        super.tearDown()
    }

    private func member(
        id: String,
        role: FamilyMemberCard.FamilyRole,
        serverId: String? = nil
    ) -> FamilyMemberData {
        FamilyMemberData(
            id: id,
            serverMemberId: serverId ?? id,
            localOnly: false,
            name: "T",
            role: role,
            avatar: "👤",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
    }

    func testParentInRosterIsCaregiver() {
        let myId = "MEM_PARENT_1"
        defaults.set(myId, forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        defaults.set("child", forKey: "current_user_role") // устаревший UD не должен побеждать roster
        let members = [member(id: myId, role: .parent)]
        XCTAssertTrue(FamilyAccessPolicy.isCaregiver(members: members, defaults: defaults))
        XCTAssertTrue(
            FamilyAccessPolicy.isCaregiverForRewardsUI(forceChildMode: false, members: members, defaults: defaults)
        )
    }

    func testElderlyInRosterIsCaregiver() {
        let myId = "MEM_ELDER_1"
        defaults.set(myId, forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let members = [member(id: myId, role: .elderly)]
        XCTAssertTrue(FamilyAccessPolicy.isCaregiver(members: members, defaults: defaults))
    }

    func testChildInRosterIsNotCaregiver() {
        let myId = "MEM_CHILD_1"
        defaults.set(myId, forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        defaults.set("parent", forKey: "current_user_role")
        let members = [member(id: myId, role: .child)]
        XCTAssertFalse(FamilyAccessPolicy.isCaregiver(members: members, defaults: defaults))
    }

    func testForceChildModeHidesCaregiverEvenIfParent() {
        let myId = "MEM_PARENT_2"
        defaults.set(myId, forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        let members = [member(id: myId, role: .parent)]
        XCTAssertFalse(
            FamilyAccessPolicy.isCaregiverForRewardsUI(forceChildMode: true, members: members, defaults: defaults)
        )
    }

    func testSyncCurrentUserRoleWritesParent() {
        let myId = "MEM_PARENT_3"
        defaults.set(myId, forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        defaults.set("child", forKey: "current_user_role")
        let members = [member(id: myId, role: .parent)]
        FamilyAccessPolicy.syncCurrentUserRoleDefaults(members: members, defaults: defaults)
        XCTAssertEqual(defaults.string(forKey: "current_user_role"), "parent")
    }
}
