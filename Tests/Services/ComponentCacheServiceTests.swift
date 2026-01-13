import XCTest
@testable import ALADDIN

/**
 * 🧪 ComponentCacheService Unit Tests
 * Тесты для сервиса кэширования компонентов
 */

@MainActor
class ComponentCacheServiceTests: XCTestCase {
    
    var service: ComponentCacheService!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        service = ComponentCacheService.shared
    }
    
    override func tearDownWithError() throws {
        service = nil
        try super.tearDownWithError()
    }
    
    // MARK: - Save Status Tests
    
    func testSaveStatus() async {
        // Arrange
        let componentId = "crash_detection_agent"
        let status = ComponentStatus(
            componentId: componentId,
            isEnabled: true,
            lastUpdate: Date()
        )
        
        // Act
        await service.saveStatus(componentId: componentId, status: status)
        
        // Assert
        let loadedStatus = await service.loadStatus(componentId: componentId)
        XCTAssertNotNil(loadedStatus)
        XCTAssertEqual(loadedStatus?.componentId, componentId)
    }
    
    // MARK: - Load Status Tests
    
    func testLoadStatus() async {
        // Arrange
        let componentId = "crash_detection_agent"
        let status = ComponentStatus(
            componentId: componentId,
            isEnabled: true,
            lastUpdate: Date()
        )
        await service.saveStatus(componentId: componentId, status: status)
        
        // Act
        let loadedStatus = await service.loadStatus(componentId: componentId)
        
        // Assert
        XCTAssertNotNil(loadedStatus)
        XCTAssertEqual(loadedStatus?.componentId, componentId)
        XCTAssertTrue(loadedStatus?.isEnabled ?? false)
    }
    
    // MARK: - Load All Statuses Tests
    
    func testLoadAllStatuses() async {
        // Arrange
        let status1 = ComponentStatus(
            componentId: "component1",
            isEnabled: true,
            lastUpdate: Date()
        )
        let status2 = ComponentStatus(
            componentId: "component2",
            isEnabled: false,
            lastUpdate: Date()
        )
        await service.saveStatus(componentId: "component1", status: status1)
        await service.saveStatus(componentId: "component2", status: status2)
        
        // Act
        let allStatuses = await service.loadAllStatuses()
        
        // Assert
        XCTAssertEqual(allStatuses.count, 2)
        XCTAssertNotNil(allStatuses["component1"])
        XCTAssertNotNil(allStatuses["component2"])
    }
}

