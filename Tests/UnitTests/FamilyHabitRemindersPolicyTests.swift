import XCTest
@testable import ALADDIN

final class FamilyHabitRemindersPolicyTests: XCTestCase {
    private let testDefaultsSuite = "FamilyHabitRemindersPolicyTests.\(UUID().uuidString)"

    private func makeDefaults() -> UserDefaults {
        let defaults = UserDefaults(suiteName: testDefaultsSuite)!
        defaults.removePersistentDomain(forName: testDefaultsSuite)
        return defaults
    }

    func testEmptyMemberIdsTargetsMinorsOnly() {
        let teen = FamilyMemberData(
            id: "teen-1",
            serverMemberId: "teen-1",
            name: "Teen",
            role: .teenager,
            avatar: "🧒",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let config = FamilyHabitRemindersConfig.empty
        let defaults = makeDefaults()
        defaults.set("teen-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [teen],
                defaults: defaults
            )
        )
    }

    func testParentReceivesWhenRemindOnThisDeviceDefault() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        // key unset → default ON

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testParentExcludedWhenRemindOnThisDeviceOff() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: defaults)

        XCTAssertFalse(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: FamilyHabitRemindersConfig.empty,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testParentIncludedWhenListedInMemberIds() {
        let parent = FamilyMemberData(
            id: "parent-1",
            serverMemberId: "parent-1",
            name: "Parent",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 0,
            lastActive: "now"
        )
        let defaults = makeDefaults()
        defaults.set("parent-1", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        FamilyHabitRemindersPolicy.setRemindOnThisDevice(false, defaults: defaults)
        var config = FamilyHabitRemindersConfig.empty
        config.memberIds = ["parent-1"]

        XCTAssertTrue(
            FamilyHabitRemindersPolicy.shouldReceiveReminders(
                config: config,
                members: [parent],
                defaults: defaults
            )
        )
    }

    func testWaterSlotsAcrossWindow() {
        let schedule = FamilyHabitPresetSchedule(
            enabled: true,
            hour: 9,
            minute: 0,
            endHour: 15,
            endMinute: 0,
            intervalMinutes: 120,
            dailyLiters: 2.0
        )
        let slots = schedule.waterNotificationSlots()
        XCTAssertEqual(slots.map { "\($0.hour):\($0.minute)" }, ["9:0", "11:0", "13:0", "15:0"])
    }

    func testWaterLegacyDecodeDefaultsPingOff() throws {
        let json = """
        {"enabled":true,"hour":10,"minute":30}
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(FamilyHabitPresetSchedule.self, from: json)
        XCTAssertTrue(decoded.enabled)
        XCTAssertEqual(decoded.hour, 10)
        XCTAssertEqual(decoded.endHour, 21)
        XCTAssertEqual(decoded.intervalMinutes, 120)
        XCTAssertEqual(decoded.dailyLiters, 2.0, accuracy: 0.01)
        XCTAssertFalse(decoded.pingUntilDone)
        XCTAssertEqual(decoded.pingIntervalMinutes, 20)
        XCTAssertEqual(decoded.pingMaxPerDay, 6)
    }

    func testPingIntervalClamped15to30() {
        let low = FamilyHabitPresetSchedule(
            enabled: true, hour: 9, minute: 0,
            pingUntilDone: true, pingIntervalMinutes: 5, pingMaxPerDay: 6
        )
        XCTAssertEqual(low.pingIntervalMinutes, 15)
        let high = FamilyHabitPresetSchedule(
            enabled: true, hour: 9, minute: 0,
            pingUntilDone: true, pingIntervalMinutes: 90, pingMaxPerDay: 6
        )
        XCTAssertEqual(high.pingIntervalMinutes, 30)
    }

    func testWaterDefaultPingOffInDefaultsMap() {
        let water = FamilyHabitPresetSchedule.defaultsMap()[.water]!
        XCTAssertFalse(water.pingUntilDone)
    }

    func testNoShowGraceClampAndCheckTime() {
        XCTAssertEqual(GeofenceNoShowSchedule.clampGrace(5), 15)
        XCTAssertEqual(GeofenceNoShowSchedule.clampGrace(45), 30)
        let schedule = GeofenceNoShowSchedule(
            placeName: "School",
            hour: 8,
            minute: 30,
            graceMinutes: 15
        )
        let check = schedule.checkHourMinute()
        XCTAssertEqual(check.hour, 8)
        XCTAssertEqual(check.minute, 45)
        let late = GeofenceNoShowSchedule(
            placeName: "School",
            hour: 8,
            minute: 50,
            graceMinutes: 30
        )
        let check2 = late.checkHourMinute()
        XCTAssertEqual(check2.hour, 9)
        XCTAssertEqual(check2.minute, 20)
    }

    func testMedicineDefaultSlotExists() {
        let medicine = FamilyHabitPresetSchedule.defaultsMap()[.medicine]!
        XCTAssertEqual(medicine.hour, 9)
        XCTAssertEqual(medicine.minute, 0)
        XCTAssertTrue(medicine.pingUntilDone)
    }
}
