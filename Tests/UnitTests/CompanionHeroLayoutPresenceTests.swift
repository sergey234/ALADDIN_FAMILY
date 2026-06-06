import XCTest
@testable import ALADDIN

final class CompanionHeroLayoutPresenceTests: XCTestCase {
    func testResolvePresence_voiceWinsOverPin() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: true,
                isVoiceActive: true,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .alwaysStandard
            ),
            .immersive
        )
    }

    func testResolvePresence_alwaysFocused() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: true,
                isVoiceActive: false,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .alwaysFocused
            ),
            .focused
        )
    }

    func testResolvePresence_alwaysStandard() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: false,
                isVoiceActive: false,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .alwaysStandard
            ),
            .standard
        )
    }

    func testResolvePresence_autoWithMessages() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: false,
                isVoiceActive: false,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .auto
            ),
            .focused
        )
    }

    func testResolvePresence_immersiveDisabled() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: false,
                isVoiceActive: true,
                userPinnedChrome: false,
                immersiveEnabled: false,
                pinMode: .auto
            ),
            .standard
        )
    }
}
