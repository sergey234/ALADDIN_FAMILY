
// Quick test to verify SettingsScreen compiles
import SwiftUI
import XCTest

@MainActor
class QuickSettingsTest: XCTestCase {
    func testSettingsScreenCreation() {
        let screen = SettingsScreen()
        XCTAssertNotNil(screen)
    }
}

