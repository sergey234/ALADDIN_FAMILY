import XCTest
@testable import ALADDIN

/**
 * 🧪 ComponentStatusService Unit Tests
 * Тесты для сервиса управления статусами компонентов
 */

@MainActor
class ComponentStatusServiceTests: XCTestCase {
    
    var service: ComponentStatusService!
    var mockAPIService: MockAPIServiceForComponents!
    var mockCacheService: MockComponentCacheService!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        mockAPIService = MockAPIServiceForComponents()
        mockCacheService = MockComponentCacheService()
        
        // Note: ComponentStatusService использует init с параметрами по умолчанию
        // Для тестов нужно будет либо сделать init доступным, либо использовать другой подход
        service = ComponentStatusService.shared
    }
    
    override func tearDownWithError() throws {
        service = nil
        mockAPIService = nil
        mockCacheService = nil
        try super.tearDownWithError()
    }
    
    // MARK: - Get Status Tests
    
    func testGetStatusSuccess() async throws {
        // Arrange
        let componentId = "crash_detection_agent"
        let expectedStatus = ComponentStatus(
            componentId: componentId,
            isEnabled: true,
            lastUpdate: Date()
        )
        mockAPIService.stubStatus = expectedStatus
        
        // Act
        let status = try await service.getStatus(for: componentId)
        
        // Assert
        XCTAssertEqual(status.componentId, componentId)
        XCTAssertTrue(status.isEnabled)
    }
    
    func testGetStatusFromCache() async throws {
        // Arrange
        let componentId = "crash_detection_agent"
        let cachedStatus = ComponentStatus(
            componentId: componentId,
            isEnabled: true,
            lastUpdate: Date()
        )
        service.componentStatuses[componentId] = cachedStatus
        
        // Act
        let status = try await service.getStatus(for: componentId)
        
        // Assert
        XCTAssertEqual(status.componentId, componentId)
        XCTAssertTrue(status.isEnabled)
    }
    
    // MARK: - Update Status Tests
    
    func testUpdateStatusSuccess() async throws {
        // Arrange
        let componentId = "crash_detection_agent"
        mockAPIService.shouldSucceed = true
        
        // Act
        try await service.updateStatus(
            componentId: componentId,
            isEnabled: true
        )
        
        // Assert
        let status = service.componentStatuses[componentId]
        XCTAssertNotNil(status)
        XCTAssertTrue(status?.isEnabled ?? false)
    }
    
    func testUpdateStatusFailure() async {
        // Arrange
        let componentId = "crash_detection_agent"
        mockAPIService.shouldSucceed = false
        mockAPIService.error = ComponentError.networkError("Network error")
        
        // Act & Assert
        do {
            try await service.updateStatus(
                componentId: componentId,
                isEnabled: true
            )
            XCTFail("Should have thrown an error")
        } catch {
            XCTAssertNotNil(error)
        }
    }
    
    // MARK: - Load Critical Components Tests
    
    func testLoadCriticalComponentsSuccess() async throws {
        // Arrange
        mockAPIService.shouldSucceed = true
        
        // Act
        try await service.loadCriticalComponentsStatus()
        
        // Assert
        XCTAssertFalse(service.isLoading)
        XCTAssertNotNil(service.lastUpdate)
    }
    
    func testLoadCriticalComponentsFailure() async {
        // Arrange
        mockAPIService.shouldSucceed = false
        mockAPIService.error = ComponentError.networkError("Network error")
        
        // Act & Assert
        do {
            try await service.loadCriticalComponentsStatus()
            XCTFail("Should have thrown an error")
        } catch {
            XCTAssertNotNil(error)
        }
    }
}

// MARK: - Mock Services

class MockAPIServiceForComponents {
    var stubStatus: ComponentStatus?
    var shouldSucceed = true
    var error: ComponentError?
    
    func getComponentStatus(componentId: String) async throws -> ComponentStatus {
        if shouldSucceed {
            return stubStatus ?? ComponentStatus(
                componentId: componentId,
                isEnabled: false,
                lastUpdate: Date()
            )
        } else {
            throw error ?? ComponentError.networkError("Mock error")
        }
    }
    
    func updateComponentStatus(componentId: String, isEnabled: Bool, configuration: ComponentConfiguration?) async throws {
        if !shouldSucceed {
            throw error ?? ComponentError.networkError("Mock error")
        }
    }
}

class MockComponentCacheService {
    var cachedStatuses: [String: ComponentStatus] = [:]
    
    func saveStatus(componentId: String, status: ComponentStatus) async {
        cachedStatuses[componentId] = status
    }
    
    func loadStatus(componentId: String) async -> ComponentStatus? {
        return cachedStatuses[componentId]
    }
    
    func loadAllStatuses() async -> [String: ComponentStatus] {
        return cachedStatuses
    }
}

