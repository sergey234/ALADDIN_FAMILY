import XCTest
@testable import ALADDIN

final class FamilyHabitRemindersPolicyTests: XCTestCase {
    func testEmptyMemberIdsTargetsMinorsOnly() {
        let teen = FamilyMemberData(
            id: "teen-1",
            name: "Teen",
            role: .teenager,
            avatar: "🧒",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now",
            serverMemberId: "teen-1"
        )
        let config = FamilyHabitRemindersConfig.empty
        var defaults = UserDefaults.standard
        defaults.set("teen-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [teen],
                defaults: defaults
            )
        )
    }

    func testParentExcludedWhenMemberIdsEmpty() {
        let parent = FamilyMemberData(
            id: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now",
            serverMemberId: "parent-1"
        )
        var defaults = UserDefaults.standard
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)

        XCTAssertFalse(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [parent],
                defaults: defaults
            )
        )
    }
}
