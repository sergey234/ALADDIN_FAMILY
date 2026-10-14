import XCTest
@testable import ALADDIN

final class UX36W2PresentationTests: XCTestCase {
    func testEicarThreatCardIsHumanNotRawEnglish() {
        let card = DeviceThreatPresentation.present(
            id: "eicar-test",
            name: "EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
            description: "standard anti malware test file"
        )
        XCTAssertFalse(card.title.lowercased().contains("eicar-standard"))
        XCTAssertFalse(card.what.lowercased().contains("standard anti"))
        XCTAssertFalse(card.title.isEmpty)
        XCTAssertFalse(card.action.isEmpty)
    }

    func testFallbackActiveNeverShownRaw() {
        let text = ComponentStatusCopy.localized("fallback_active")
        XCTAssertFalse(text.contains("fallback_active"))
        XCTAssertFalse(text.contains("_"))
    }

    func testParentARolePrefixRemapped() {
        let fromEN = FamilyMemberDisplayNameFormatter.displayName(
            storedName: "Parent A",
            role: .parent
        )
        let fromRU = FamilyMemberDisplayNameFormatter.displayName(
            storedName: "Родитель A",
            role: .parent
        )
        XCTAssertTrue(fromEN.contains("A"), fromEN)
        XCTAssertTrue(fromRU.contains("A"), fromRU)
        // Both resolve through the same role key — should match current app language.
        XCTAssertEqual(fromEN, fromRU)
    }

    func testScreenTimeFormatsLegacyThreeHours() {
        let text = ParentalScreenTimeFormat.display(stored: "3h/day")
        XCTAssertFalse(text.contains("3h/day"))
        XCTAssertTrue(text.contains("3"))
    }
}
