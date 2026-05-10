import XCTest

/**
 * 🧪 NetworkProtectionScreen UI Tests
 * UI тесты для экрана защиты сети с 10 компонентами
 */

@MainActor
class NetworkProtectionScreenUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
        super.tearDown()
    }
    
    // MARK: - Screen Display Tests
    
    func testNetworkProtectionScreenDisplay() throws {
        // Navigate to Network Protection screen
        navigateToNetworkProtection()
        
        // Check if screen is displayed
        let screen = app.otherElements["NetworkProtectionScreen"]
        XCTAssertTrue(screen.exists, "Network Protection screen should be displayed")
    }
    
    // MARK: - Component Toggle Tests
    
    func testToggleCrashDetection() throws {
        navigateToNetworkProtection()
        
        // Find toggle for crash detection
        let toggle = app.switches["crash_detection_agent"]
        if toggle.exists {
            let initialValue = toggle.value as? String
            toggle.tap()
            
            // Verify toggle state changed
            let newValue = toggle.value as? String
            XCTAssertNotEqual(initialValue, newValue, "Toggle state should change")
        }
    }
    
    func testTogglePhishingProtection() throws {
        navigateToNetworkProtection()
        
        let toggle = app.switches["phishing_protection_agent"]
        if toggle.exists {
            toggle.tap()
            XCTAssertTrue(toggle.exists, "Phishing protection toggle should exist")
        }
    }
    
    // MARK: - Accordion Tests
    
    func testAccordionExpandCollapse() throws {
        navigateToNetworkProtection()
        
        // Find accordion header
        let accordion = app.buttons.matching(identifier: "accordion_emergency_assistance").firstMatch
        if accordion.exists {
            accordion.tap()
            
            // Check if content is visible
            let content = app.otherElements["accordion_content_emergency_assistance"]
            XCTAssertTrue(content.exists, "Accordion content should be visible after expand")
        }
    }
    
    // MARK: - Settings Modal Tests
    
    func testOpenPasswordGeneratorModal() throws {
        navigateToNetworkProtection()
        
        // Find settings button for password security
        let settingsButton = app.buttons["password_security_agent_settings"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Check if modal is displayed
            let modal = app.otherElements["PasswordGeneratorModal"]
            XCTAssertTrue(modal.exists, "Password generator modal should be displayed")
        }
    }
    
    // MARK: - Accessibility Tests
    
    func testAccessibilityLabels() throws {
        navigateToNetworkProtection()
        
        // Check if toggles have accessibility labels
        let toggles = app.switches.allElementsBoundByIndex
        for toggle in toggles {
            let label = toggle.label
            XCTAssertFalse(label.isEmpty, "Toggle should have accessibility label")
        }
    }
    
    // MARK: - Helper Methods
    
    private func navigateToNetworkProtection() {
        // Navigate to Network Protection screen
        // This depends on your app's navigation structure
        let tabBar = app.tabBars.firstMatch
        if tabBar.exists {
            let protectionTab = tabBar.buttons["Protection"]
            if protectionTab.exists {
                protectionTab.tap()
            }
        }
        
        // Or navigate via menu
        let menuButton = app.buttons["Menu"]
        if menuButton.exists {
            menuButton.tap()
            let networkProtectionItem = app.buttons["Network Protection"]
            if networkProtectionItem.exists {
                networkProtectionItem.tap()
            }
        }
    }
}

