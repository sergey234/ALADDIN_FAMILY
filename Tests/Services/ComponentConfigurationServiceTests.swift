import XCTest
@testable import ALADDIN

/**
 * 🧪 ComponentConfigurationService Unit Tests
 * Тесты для сервиса управления конфигурациями компонентов
 */

@MainActor
class ComponentConfigurationServiceTests: XCTestCase {
    
    var service: ComponentConfigurationService!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        service = ComponentConfigurationService.shared
    }
    
    override func tearDownWithError() throws {
        service = nil
        try super.tearDownWithError()
    }
    
    // MARK: - Get Configuration Tests
    
    func testGetConfigurationSuccess() async throws {
        // Arrange
        let componentId = "crash_detection_agent"
        let expectedConfig = ComponentConfiguration(
            componentId: componentId,
            settings: ["enabled": true]
        )
        
        // Act
        let config = try await service.getConfiguration(for: componentId)
        
        // Assert
        XCTAssertEqual(config.componentId, componentId)
    }
    
    // MARK: - Save Configuration Tests
    
    func testSaveConfigurationSuccess() async throws {
        // Arrange
        let componentId = "crash_detection_agent"
        let config = ComponentConfiguration(
            componentId: componentId,
            settings: ["enabled": true]
        )
        
        // Act
        try await service.saveConfiguration(config)
        
        // Assert
        let savedConfig = service.configurations[componentId]
        XCTAssertNotNil(savedConfig)
    }
}

