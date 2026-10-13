import XCTest
@testable import ALADDIN

final class PostCallSafetyPolicyTests: XCTestCase {
    override func setUp() {
        super.setUp()
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.postCallSafetyPromptEnabled)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.postCallSafetyLastShownAt)
    }

    func testDefaultEnabledForAnyRole() {
        XCTAssertTrue(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: nil))
        XCTAssertTrue(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: "personal"))
        XCTAssertTrue(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: "elderly"))
    }

    func testToggleOffDisables() {
        UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.postCallSafetyPromptEnabled)
        XCTAssertFalse(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: "elderly"))
    }

    func testCooldownBlocksRepeat() {
        let now: TimeInterval = 1_000_000
        UserDefaults.standard.set(now - 30, forKey: AppConfig.UserDefaultsKeys.postCallSafetyLastShownAt)
        XCTAssertFalse(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: "parent", now: now))
        UserDefaults.standard.set(now - 200, forKey: AppConfig.UserDefaultsKeys.postCallSafetyLastShownAt)
        XCTAssertTrue(ElderlyScamCallPolicy.shouldPresentSafetyPrompt(role: "parent", now: now))
    }
}
