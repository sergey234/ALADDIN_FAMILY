import XCTest
@testable import ALADDIN

/// GATES: CHN storefront → Family Chat / Companion / AI Assistant off; non-CHN unchanged.
final class ChinaMainlandComplianceTests: XCTestCase {

    override func tearDown() {
        ChinaMainlandCompliance.resetForTesting()
        super.tearDown()
    }

    func testMainlandChinaRestrictsEncryptedChatAndAIGC() {
        ChinaMainlandCompliance.testingOverrideIsMainlandChina = true
        XCTAssertTrue(ChinaMainlandCompliance.isMainlandChinaAppStore)
        XCTAssertTrue(ChinaMainlandCompliance.restrictsEncryptedChatAndAIGC)
        XCTAssertFalse(AppConfig.isFamilyChatAvailable)
        XCTAssertFalse(AppConfig.isCompanionAvailable)
        XCTAssertFalse(AppConfig.isAIAssistantAvailable)
        XCTAssertFalse(AppConfig.isFamilyChatE2EEEnabled)
    }

    func testNonChinaKeepsSurfacesOn() {
        ChinaMainlandCompliance.testingOverrideIsMainlandChina = false
        XCTAssertFalse(ChinaMainlandCompliance.isMainlandChinaAppStore)
        XCTAssertFalse(ChinaMainlandCompliance.restrictsEncryptedChatAndAIGC)
        XCTAssertTrue(AppConfig.isFamilyChatAvailable)
        XCTAssertTrue(AppConfig.isCompanionAvailable)
        XCTAssertTrue(AppConfig.isAIAssistantAvailable)
        XCTAssertTrue(AppConfig.isFamilyChatE2EEEnabled)
    }

    func testOnlyMainlandCodeIsCHN() {
        XCTAssertEqual(ChinaMainlandCompliance.mainlandChinaStorefrontCode, "CHN")
    }
}
