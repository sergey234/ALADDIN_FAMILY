//
//  SettingsViewModelTests.swift
//  ALADDINTests
//
//  Created by AI Assistant on 21.02.2026
//  Tests for SettingsViewModel MVVM implementation

import XCTest
import Combine
@testable import ALADDIN

@MainActor
class SettingsViewModelTests: XCTestCase {

    // MARK: - Properties

    private var viewModel: SettingsViewModel!
    private var cancellables: Set<AnyCancellable>!

    // MARK: - Setup & Teardown

    override func setUp() {
        super.setUp()

        viewModel = SettingsViewModel() // Use default constructor for testing
        cancellables = Set<AnyCancellable>()
    }

    override func tearDown() {
        viewModel = nil
        cancellables = nil

        super.tearDown()
    }

    // MARK: - Initialization Tests

    func testInitialization() {
        // Given
        let expectation = expectation(description: "ViewModel initialized")

        // When
        viewModel.initializeView()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            // Test default values
            XCTAssertFalse(self.viewModel.isNetworkProtectionEnabled)
            XCTAssertFalse(self.viewModel.isBiometricEnabled)
            XCTAssertFalse(self.viewModel.showProfileEdit)
            XCTAssertEqual(self.viewModel.selectedTheme, .system)
            XCTAssertFalse(self.viewModel.securityEnabled)
            XCTAssertFalse(self.viewModel.soundEnabled)
            XCTAssertFalse(self.viewModel.consentAccepted)
            XCTAssertTrue(self.viewModel.components.isEmpty)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    // MARK: - Basic Property Tests

    func testThemeCycling() {
        // Given
        let initialTheme = viewModel.selectedTheme

        // When
        viewModel.cycleTheme()

        // Then
        XCTAssertNotEqual(viewModel.selectedTheme, initialTheme)
    }

    func testPropertyDefaults() {
        // Test default property values
        XCTAssertFalse(viewModel.isNetworkProtectionEnabled)
        XCTAssertFalse(viewModel.isBiometricEnabled)
        XCTAssertFalse(viewModel.showProfileEdit)
        XCTAssertEqual(viewModel.selectedTheme, .system)
        XCTAssertFalse(viewModel.securityEnabled)
        XCTAssertFalse(viewModel.soundEnabled)
        XCTAssertFalse(viewModel.consentAccepted)
        XCTAssertTrue(viewModel.components.isEmpty)
    }

    func testToggleComponent() {
        // Given
        let component = ComponentStatus(componentId: "test", isEnabled: false)
        viewModel.components = [component]

        // When
        viewModel.toggleComponent(component)

        // Then
        XCTAssertTrue(viewModel.components[0].isEnabled)
    }

    func testLocalizedStrings() {
        // Test that localized strings are initialized
        XCTAssertNotNil(viewModel.localizedStrings)
        XCTAssertFalse(viewModel.localizedStrings.appSection.isEmpty)
    }

    // MARK: - Mock Classes (for future complex tests)
    // Mock classes can be added here when services are properly injected
    // For now, we use the default constructor with nil services
}