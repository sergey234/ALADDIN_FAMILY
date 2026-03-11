import XCTest
@testable import ALADDIN

/**
 * 🧪 NetworkProtectionViewModel Unit Tests
 * Тесты для ViewModel экрана защиты сети
 * Покрытие: все методы toggle и загрузка статусов
 */

@MainActor
class NetworkProtectionViewModelTests: XCTestCase {
    
    var viewModel: NetworkProtectionViewModel!
    var mockStatusService: MockComponentStatusService!
    var mockConfigurationService: MockComponentConfigurationService!
    var mockRetryManager: MockRetryManager!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        mockStatusService = MockComponentStatusService()
        mockConfigurationService = MockComponentConfigurationService()
        mockRetryManager = MockRetryManager()
        
        viewModel = NetworkProtectionViewModel(
            statusService: mockStatusService,
            configurationService: mockConfigurationService,
            retryManager: mockRetryManager
        )
    }
    
    override func tearDownWithError() throws {
        viewModel = nil
        mockStatusService = nil
        mockConfigurationService = nil
        mockRetryManager = nil
        try super.tearDownWithError()
    }
    
    // MARK: - Initialization Tests
    
    func testInitialization() {
        XCTAssertNotNil(viewModel)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertFalse(viewModel.crashDetectionEnabled)
        XCTAssertFalse(viewModel.roadsideAssistanceEnabled)
        XCTAssertFalse(viewModel.emergencyResponseEnabled)
    }
    
    // MARK: - Load Components Status Tests
    
    func testLoadCriticalComponentsSuccess() async {
        // Arrange
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.loadComponentStatuses()
        
        // Assert
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testLoadCriticalComponentsFailure() async {
        // Arrange
        mockStatusService.shouldSucceed = false
        mockStatusService.error = ComponentError.networkError("Network error")
        
        // Act
        await viewModel.loadComponentStatuses()
        
        // Assert
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNotNil(viewModel.errorMessage)
    }
    
    // MARK: - Toggle Crash Detection Tests
    
    func testToggleCrashDetectionEnable() async {
        // Arrange
        viewModel.crashDetectionEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleCrashDetection(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
        
        // Assert
        XCTAssertTrue(viewModel.crashDetectionEnabled)
    }
    
    func testToggleCrashDetectionDisable() async {
        // Arrange
        viewModel.crashDetectionEnabled = true
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleCrashDetection(false)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
        
        // Assert
        XCTAssertFalse(viewModel.crashDetectionEnabled)
    }
    
    // MARK: - Toggle Roadside Assistance Tests
    
    func testToggleRoadsideAssistance() async {
        // Arrange
        viewModel.roadsideAssistanceEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleRoadsideAssistance(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.roadsideAssistanceEnabled)
    }
    
    // MARK: - Toggle Emergency Response Tests
    
    func testToggleEmergencyResponse() async {
        // Arrange
        viewModel.emergencyResponseEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleEmergencyResponse(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.emergencyResponseEnabled)
    }
    
    // MARK: - Toggle Emergency Event Tests
    
    func testToggleEmergencyEvent() async {
        // Arrange
        viewModel.emergencyEventEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleEmergencyEvent(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.emergencyEventEnabled)
    }
    
    // MARK: - Toggle Phishing Protection Tests
    
    func testTogglePhishingProtection() async {
        // Arrange
        viewModel.phishingProtectionEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.togglePhishingProtection(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.phishingProtectionEnabled)
    }
    
    // MARK: - Toggle Malware Detection Tests
    
    func testToggleMalwareDetection() async {
        // Arrange
        viewModel.malwareDetectionEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleMalwareDetection(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.malwareDetectionEnabled)
    }
    
    // MARK: - Toggle Network Security Tests
    
    func testToggleNetworkSecurity() async {
        // Arrange
        viewModel.networkSecurityEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleNetworkSecurity(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.networkSecurityEnabled)
    }
    
    // MARK: - Toggle Incident Response Tests
    
    func testToggleIncidentResponse() async {
        // Arrange
        viewModel.incidentResponseEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.toggleIncidentResponse(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.incidentResponseEnabled)
    }
    
    // MARK: - Toggle Password Security Tests
    
    func testTogglePasswordSecurity() async {
        // Arrange
        viewModel.passwordSecurityEnabled = false
        mockStatusService.shouldSucceed = true
        
        // Act
        await viewModel.togglePasswordSecurity(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert
        XCTAssertTrue(viewModel.passwordSecurityEnabled)
    }
    
    // MARK: - Error Handling Tests
    
    func testToggleWithNetworkError() async {
        // Arrange
        let initialValue = viewModel.crashDetectionEnabled
        mockStatusService.shouldSucceed = false
        mockStatusService.error = ComponentError.networkError("Network error")
        
        // Act
        await viewModel.toggleCrashDetection(true)
        
        // Wait for async operation
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        // Assert - should rollback to initial value
        XCTAssertEqual(viewModel.crashDetectionEnabled, initialValue)
        XCTAssertNotNil(viewModel.errorMessage)
    }
}

// MARK: - Mock Services

class MockComponentStatusService: ComponentStatusService {
    var shouldSucceed = true
    var error: ComponentError?
    
    override func getStatus(for componentId: String, priority: ComponentPriority = .normal) async throws -> ComponentStatus {
        if shouldSucceed {
            return ComponentStatus(
                componentId: componentId,
                isEnabled: false,
                lastUpdate: Date()
            )
        } else {
            throw error ?? ComponentError.networkError("Mock error")
        }
    }
    
    override func updateStatus(componentId: String, isEnabled: Bool, configuration: ComponentConfiguration? = nil) async throws {
        if !shouldSucceed {
            throw error ?? ComponentError.networkError("Mock error")
        }
        // Update local status
        componentStatuses[componentId] = ComponentStatus(
            componentId: componentId,
            isEnabled: isEnabled,
            lastUpdate: Date(),
            configuration: configuration
        )
    }
    
    override func loadCriticalComponentsStatus() async throws {
        if !shouldSucceed {
            throw error ?? ComponentError.networkError("Mock error")
        }
        // Mock implementation
    }
}

class MockComponentConfigurationService: ComponentConfigurationService {
    // Mock implementation
}

class MockRetryManager: RetryManager {
    override func execute<T>(operation: @escaping () async throws -> T) async -> Result<T, NetworkError> {
        do {
            let result = try await operation()
            return .success(result)
        } catch {
            return .failure(NetworkError.unknown(error))
        }
    }
}

