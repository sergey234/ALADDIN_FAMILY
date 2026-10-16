import XCTest
@testable import ALADDIN

final class FamilyScreenTimeEligibilityTests: XCTestCase {

    func testCanonicalBandsFromAllTaxonomies() {
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "kids"), .kids)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "toddler"), .kids)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "1-6"), .kids)

        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "school"), .school)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "7-13"), .school)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "school_7_12"), .school)

        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "teen"), .teen)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "14-17"), .teen)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "teenager"), .teen)

        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "youngAdult"), .youngAdult)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "adult"), .youngAdult)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "18+"), .youngAdult)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "20+"), .youngAdult)
        XCTAssertEqual(FamilyScreenTimeEligibility.canonicalBand(from: "18-22"), .youngAdult)
    }

    func testSupervisedRolesIncludeAllChildBands() {
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "kids"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "school"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "teenager", ageGroup: "teen"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "youngAdult"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "adult"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "toddler"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "young_adult", ageGroup: nil))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "child", ageGroup: "20+"))
    }

    func testExcludedParentAndElderly() {
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedDevice(role: "parent", ageGroup: "youngAdult"))
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedDevice(role: "elderly", ageGroup: "adult"))
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedDevice(role: "senior", ageGroup: "20+"))
        // Bare parental "adult" without role must not auto-enable on unknown device
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedDevice(role: "", ageGroup: "adult"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedDevice(role: "", ageGroup: "kids"))
    }

    func testMemberLists() {
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedMember(role: "young_adult"))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedMember(role: .child))
        XCTAssertTrue(FamilyScreenTimeEligibility.isSupervisedMember(role: .teenager))
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedMember(role: .parent))
        XCTAssertFalse(FamilyScreenTimeEligibility.isSupervisedMember(role: .elderly))
    }

    func testChildInterfaceTokens() {
        XCTAssertEqual(FamilyScreenTimeEligibility.childInterfaceAgeToken("kids"), "kids")
        XCTAssertEqual(FamilyScreenTimeEligibility.childInterfaceAgeToken("school"), "school")
        XCTAssertEqual(FamilyScreenTimeEligibility.childInterfaceAgeToken("teen"), "teen")
        XCTAssertEqual(FamilyScreenTimeEligibility.childInterfaceAgeToken("youngAdult"), "youngAdult")
    }
}
