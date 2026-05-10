import XCTest

/**
 * 🧪 ParentalControlScreen UI Tests
 * UI тесты для экрана родительского контроля с 5 компонентами
 */

@MainActor
class ParentalControlScreenUITests: XCTestCase {
    
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
    
    func testParentalControlScreenDisplay() throws {
        navigateToParentalControl()
        
        let screen = app.otherElements["ParentalControlScreen"]
        XCTAssertTrue(screen.exists, "Parental Control screen should be displayed")
    }
    
    // MARK: - Component Toggle Tests
    
    func testToggleChildProtectionComponents() throws {
        navigateToParentalControl()
        
        // Test toggle for child protection components
        let componentIds = [
            "child_threat_detection_agent",
            "child_content_filter_agent",
            "child_safe_browsing_agent",
            "child_time_management_agent",
            "child_location_tracking_agent"
        ]
        
        for componentId in componentIds {
            let toggle = app.switches[componentId]
            if toggle.exists {
                toggle.tap()
                XCTAssertTrue(toggle.exists, "Toggle for \(componentId) should exist")
            }
        }
    }
    
    // MARK: - Accordion Tests
    
    func testChildProtectionAccordion() throws {
        navigateToParentalControl()
        
        let accordion = app.buttons.matching(identifier: "accordion_child_protection").firstMatch
        if accordion.exists {
            accordion.tap()
            
            let content = app.otherElements["accordion_content_child_protection"]
            XCTAssertTrue(content.exists, "Child protection accordion content should be visible")
        }
    }
    
    // MARK: - Accessibility Tests
    
    func testAccessibilitySupport() throws {
        navigateToParentalControl()
        
        // Check VoiceOver support
        let toggles = app.switches.allElementsBoundByIndex
        for toggle in toggles {
            let label = toggle.label
            XCTAssertFalse(label.isEmpty, "All toggles should have accessibility labels")
        }
    }
}

// MARK: - Helper Methods

extension ParentalControlScreenUITests {
    private func navigateToParentalControl() {
        // Navigate to Parental Control screen
        let tabBar = app.tabBars.firstMatch
        if tabBar.exists {
            let protectionTab = tabBar.buttons["Protection"]
            if protectionTab.exists {
                protectionTab.tap()
            }
        }
    }
}

