import XCTest
@testable import ALADDIN

/// P8 Voicebox gates — flags default off; hybrid legacy + experimental path.
final class CompanionVoiceboxSandboxTests: XCTestCase {
    override func tearDown() {
        CompanionVoiceboxFeatureFlags.disableAll()
        super.tearDown()
    }

    func testFlagsDefaultOff() {
        UserDefaults.standard.removeObject(forKey: "companion.voiceboxSandboxEnabled")
        UserDefaults.standard.removeObject(forKey: "companion.voiceboxProdEnabled")
        XCTAssertFalse(CompanionVoiceboxFeatureFlags.sandboxEnabled)
        XCTAssertFalse(CompanionVoiceboxFeatureFlags.prodEnabled)
    }

    func testBrandTTSAllowedWhenSandboxOn() {
        UserDefaults.standard.set(true, forKey: "companion.voiceboxSandboxEnabled")
        let r = CompanionVoiceboxSandbox.evaluate(mode: .brandTTS)
        XCTAssertEqual(r, .allowed(.brandTTS))
    }

    func testDeniedWhenFlagOff() {
        CompanionVoiceboxFeatureFlags.disableAll()
        let r = CompanionVoiceboxSandbox.evaluate(mode: .sttOnly)
        XCTAssertEqual(r, .denied(reason: "voicebox_flag_off"))
    }

    func testHybridLegacyVoiceAlwaysOnWhenFlagsOff() {
        CompanionVoiceboxFeatureFlags.disableAll()
        UserDefaults.standard.removeObject(forKey: "companion.voiceboxSandboxEnabled")
        UserDefaults.standard.removeObject(forKey: "companion.voiceboxProdEnabled")
        XCTAssertTrue(CompanionVoiceboxSandbox.isLegacyCompanionVoiceEnabled)
        XCTAssertFalse(CompanionVoiceboxSandbox.isExperimentalVoiceboxPathEnabled)
        XCTAssertTrue(CompanionVoiceboxSandbox.allowBrandSpeech())
    }

    func testHybridSandboxAllowsBrand() {
        UserDefaults.standard.set(true, forKey: "companion.voiceboxSandboxEnabled")
        UserDefaults.standard.set(false, forKey: "companion.voiceboxProdEnabled")
        XCTAssertTrue(CompanionVoiceboxSandbox.isExperimentalVoiceboxPathEnabled)
        XCTAssertTrue(CompanionVoiceboxSandbox.allowBrandSpeech())
    }

    func testProdFlagDefaultsOff() {
        CompanionVoiceboxFeatureFlags.disableAll()
        UserDefaults.standard.removeObject(forKey: "companion.voiceboxProdEnabled")
        XCTAssertFalse(CompanionVoiceboxFeatureFlags.prodEnabled)
    }
}
