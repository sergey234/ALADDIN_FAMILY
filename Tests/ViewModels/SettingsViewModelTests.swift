//
//  SettingsViewModelTests.swift
//  ALADDINTests
//
//  Created by AI Assistant on 21.02.2026
//  Tests for SettingsViewModel MVVM implementation

import XCTest
import Combine
@testable import ALADDIN

class SettingsViewModelTests: XCTestCase {

    // MARK: - Properties

    private var viewModel: SettingsViewModel!
    private var mockApiService: MockAPIService!
    private var mockNotificationService: MockNotificationService!
    private var mockTariffService: MockTariffService!
    private var mockLocalizationService: MockLocalizationService!
    private var cancellables: Set<AnyCancellable>!

    // MARK: - Setup & Teardown

    override func setUp() {
        super.setUp()

        mockApiService = MockAPIService()
        mockNotificationService = MockNotificationService()
        mockTariffService = MockTariffService()
        mockLocalizationService = MockLocalizationService()

        viewModel = SettingsViewModel(
            apiService: mockApiService,
            notificationService: mockNotificationService,
            tariffService: mockTariffService,
            localizationService: mockLocalizationService
        )

        cancellables = Set<AnyCancellable>()
    }

    override func tearDown() {
        viewModel = nil
        mockApiService = nil
        mockNotificationService = nil
        mockTariffService = nil
        mockLocalizationService = nil
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

    func testInitializationWithAdmin() {
        // Given
        viewModel.isAdmin = true
        mockApiService.componentsResult = .success([
            ComponentStatus(componentId: "test1", isEnabled: true),
            ComponentStatus(componentId: "test2", isEnabled: false)
        ])

        let expectation = expectation(description: "Admin initialization loads components")

        // When
        viewModel.initializeView()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertEqual(self.viewModel.components.count, 2)
            XCTAssertEqual(self.viewModel.components[0].componentId, "test1")
            XCTAssertTrue(self.viewModel.components[0].isEnabled)
            XCTAssertEqual(self.viewModel.components[1].componentId, "test2")
            XCTAssertFalse(self.viewModel.components[1].isEnabled)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    // MARK: - Reactive Bindings Tests

    func testThemeCycling() {
        // Given
        let expectation = expectation(description: "Theme cycling works")

        var themeChanges: [ThemeMode] = []

        viewModel.$selectedTheme
            .dropFirst() // Skip initial value
            .sink { theme in
                themeChanges.append(theme)
                if themeChanges.count == 3 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // When
        viewModel.cycleTheme() // system -> light
        viewModel.cycleTheme() // light -> dark
        viewModel.cycleTheme() // dark -> system

        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(themeChanges, [.light, .dark, .system])
    }

    func testBiometricToggle() {
        // Given
        let expectation = expectation(description: "Biometric binding works")

        var biometricChanges: [Bool] = []

        viewModel.$isBiometricEnabled
            .dropFirst()
            .sink { enabled in
                biometricChanges.append(enabled)
                if biometricChanges.count == 2 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // When
        viewModel.isBiometricEnabled = true
        viewModel.isBiometricEnabled = false

        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(biometricChanges, [true, false])
    }

    func testNotificationSettings() {
        // Given
        let expectation = expectation(description: "Notification settings work")

        var securityChanges: [Bool] = []
        var soundChanges: [Bool] = []

        viewModel.$securityEnabled
            .dropFirst()
            .sink { enabled in
                securityChanges.append(enabled)
            }
            .store(in: &cancellables)

        viewModel.$soundEnabled
            .dropFirst()
            .sink { enabled in
                soundChanges.append(enabled)
                if soundChanges.count == 2 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // When
        viewModel.securityEnabled = true
        viewModel.soundEnabled = true
        viewModel.soundEnabled = false

        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(securityChanges, [true])
        XCTAssertEqual(soundChanges, [true, false])
    }

    // MARK: - API Integration Tests

    func testLoadComponentsSuccess() {
        // Given
        viewModel.isAdmin = true
        let expectedComponents = [
            ComponentStatus(componentId: "comp1", isEnabled: true),
            ComponentStatus(componentId: "comp2", isEnabled: false)
        ]
        mockApiService.componentsResult = .success(expectedComponents)

        let expectation = expectation(description: "Components loaded successfully")

        // When
        viewModel.loadComponents()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertEqual(self.viewModel.components.count, 2)
            XCTAssertEqual(self.viewModel.components[0].componentId, "comp1")
            XCTAssertTrue(self.viewModel.components[0].isEnabled)
            XCTAssertEqual(self.viewModel.components[1].componentId, "comp2")
            XCTAssertFalse(self.viewModel.components[1].isEnabled)
            XCTAssertFalse(self.viewModel.isLoadingComponents)
            XCTAssertNil(self.viewModel.componentsError)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    func testLoadComponentsFailure() {
        // Given
        viewModel.isAdmin = true
        let expectedError = NSError(domain: "TestError", code: 123, userInfo: nil)
        mockApiService.componentsResult = .failure(expectedError)

        let expectation = expectation(description: "Components loading failed")

        // When
        viewModel.loadComponents()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertTrue(self.viewModel.components.isEmpty)
            XCTAssertFalse(self.viewModel.isLoadingComponents)
            XCTAssertNotNil(self.viewModel.componentsError)
            XCTAssertEqual(self.viewModel.componentsError, expectedError.localizedDescription)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    func testLoadComponentsNotAdmin() {
        // Given
        viewModel.isAdmin = false
        let expectation = expectation(description: "Components not loaded for non-admin")

        // When
        viewModel.loadComponents()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertTrue(self.viewModel.components.isEmpty)
            XCTAssertFalse(self.viewModel.isLoadingComponents)
            XCTAssertNil(self.viewModel.componentsError)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    func testToggleComponent() {
        // Given
        viewModel.isAdmin = true
        let component = ComponentStatus(componentId: "test", isEnabled: false)
        viewModel.components = [component]

        // When
        viewModel.toggleComponent(component)

        // Then
        XCTAssertTrue(viewModel.components[0].isEnabled)
    }

    func testToggleComponentNotAdmin() {
        // Given
        viewModel.isAdmin = false
        let component = ComponentStatus(componentId: "test", isEnabled: false)
        viewModel.components = [component]

        // When
        viewModel.toggleComponent(component)

        // Then
        XCTAssertFalse(viewModel.components[0].isEnabled) // Should remain unchanged
    }

    // MARK: - Tariff Integration Tests

    func testCurrentTariff() {
        // Given
        mockTariffService.currentTariff = .premium

        // When & Then
        XCTAssertEqual(viewModel.currentTariff, .premium)
    }

    func testCurrentTariffFallback() {
        // Given
        mockTariffService.currentTariff = nil

        // When & Then
        XCTAssertEqual(viewModel.currentTariff, .free)
    }

    // MARK: - Navigation Tests

    func testShowSettings() {
        // Given
        let expectation = expectation(description: "Settings navigation works")

        viewModel.$showLanguageSettings
            .dropFirst()
            .sink { show in
                if show {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // When
        viewModel.showLanguageSettings = true

        // Then
        waitForExpectations(timeout: 1.0)
    }

    // MARK: - Localization Tests

    func testLocalizedStringsInitialization() {
        // Given
        let expectation = expectation(description: "Localized strings initialized")

        // When
        viewModel.initializeView()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            XCTAssertNotNil(self.viewModel.localizedStrings)
            XCTAssertFalse(self.viewModel.localizedStrings.appSection.isEmpty)
            XCTAssertFalse(self.viewModel.localizedStrings.language.isEmpty)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    // MARK: - Notifications Tests

    func testInitializeNotifications() {
        // Given
        let expectation = expectation(description: "Notifications initialized")

        // When
        viewModel.initializeNotifications()

        // Then
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            // Verify that notification service was called
            XCTAssertTrue(self.mockNotificationService.requestAuthorizationCalled)
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1.0)
    }

    // MARK: - Mock Classes

    class MockAPIService: APIServiceProtocol {
        var componentsResult: Result<[ComponentStatus], Error>?

        func getComponentsList(completion: @escaping (Result<[ComponentStatus], Error>) -> Void) {
            if let result = componentsResult {
                completion(result)
            }
        }
    }

    class MockNotificationService: NotificationServiceProtocol {
        var requestAuthorizationCalled = false

        func requestAuthorization() async -> Bool {
            requestAuthorizationCalled = true
            return true
        }
    }

    class MockTariffService: TariffServiceProtocol {
        var currentTariff: TariffType? = .free
    }

    class MockLocalizationService: LocalizationServiceProtocol {
        var currentLanguage: Language = .russian

        func localized(_ key: String) -> String {
            return key // Return key as-is for testing
        }
    }
}