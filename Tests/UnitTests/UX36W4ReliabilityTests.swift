import XCTest
@testable import ALADDIN

/// UX-36 W4 — human soft-fail for companion / crash / no raw HTTP in UI.
final class UX36W4ReliabilityTests: XCTestCase {

    func testCompanionErrorMapper_maps504ToHumanMessage() {
        let loc = LocalizationManager.shared
        let mapped = CompanionErrorMapper.message(
            for: NetworkError.httpError(504),
            localizationManager: loc
        )
        XCTAssertEqual(mapped, loc.localized("companion_error_hero_unavailable"))
        XCTAssertFalse(mapped.lowercased().contains("504"))
        XCTAssertFalse(mapped.lowercased().contains("http"))
    }

    func testCompanionErrorMapper_mapsTimeoutToHumanMessage() {
        let loc = LocalizationManager.shared
        let mapped = CompanionErrorMapper.message(
            for: NetworkError.timeout,
            localizationManager: loc
        )
        XCTAssertEqual(mapped, loc.localized("companion_error_hero_unavailable"))
    }

    func testCrashDetectionError_locationOffersSettings() {
        let presentation = CrashDetectionError.locationUnavailable.reliabilityPresentation
        XCTAssertTrue(presentation.offerOpenSettings)
        XCTAssertFalse(presentation.message.lowercased().contains("http"))
    }

    func testSanitizerKeepsScreenshotStatusOnce() {
        let raw = """
        From the ALADDIN knowledge base:
        ### family_chat_e2ee_decrypt_failed
        Could not decrypt. Refresh keys or wait for a resend.
        ### family_chat_e2ee_setup
        Setting up end-to-end encryption…
        (Based on the in-app knowledge base.)
        """
        let out = AIAssistantResponseSanitizer.userFacingText(from: raw)
        XCTAssertFalse(out.contains("###"))
        XCTAssertFalse(out.contains("family_chat_e2ee"))
        XCTAssertEqual(out.components(separatedBy: "Could not decrypt").count - 1, 1)
        XCTAssertEqual(out.components(separatedBy: "Setting up end-to-end encryption").count - 1, 1)
        XCTAssertFalse(out.contains("Setting up message protection"))
    }

    func testStreamFallbackIncludes504AndTimeout() {
        let gateway = NSError(domain: "CompanionStream", code: 504, userInfo: nil)
        XCTAssertTrue(CompanionStreamingService.shouldFallbackStreamToChat(gateway))
        XCTAssertTrue(CompanionStreamingService.shouldFallbackStreamToChat(URLError(.timedOut)))
        let denied = NSError(domain: "CompanionStream", code: 401, userInfo: nil)
        XCTAssertFalse(CompanionStreamingService.shouldFallbackStreamToChat(denied))
    }

    func testCrashDetectionError_accelerometerNoSettings() {
        let presentation = CrashDetectionError.accelerometerUnavailable.reliabilityPresentation
        XCTAssertFalse(presentation.offerOpenSettings)
    }
}
