import XCTest
@testable import ALADDIN

/**
 * ComponentConfigurationService unit tests (aligned with `ComponentConfiguration` model).
 */

@MainActor
final class ComponentConfigurationServiceTests: XCTestCase {

    var service: ComponentConfigurationService!

    override func setUpWithError() throws {
        try super.setUpWithError()
        service = ComponentConfigurationService.shared
    }

    override func tearDownWithError() throws {
        service?.configurations.removeValue(forKey: "crash_detection_agent")
        service?.configurations.removeValue(forKey: "test_component_x")
        service = nil
        try super.tearDownWithError()
    }

    func testGetConfigurationReturnsInMemoryCache() async throws {
        let componentId = "test_component_x"
        let cached = ComponentConfiguration(isEnabled: true, priority: .critical)
        service.configurations[componentId] = cached

        let config = try await service.getConfiguration(for: componentId)
        XCTAssertTrue(config.isEnabled)
        XCTAssertEqual(config.priority, .critical)
    }

    func testValidateConfigurationAcceptsEnabledNormal() throws {
        let config = ComponentConfiguration(isEnabled: true, priority: .normal)
        try service.validateConfiguration(config)
    }

    func testValidateConfigurationRejectsCriticalDisabled() throws {
        let config = ComponentConfiguration(isEnabled: false, priority: .critical)
        XCTAssertThrowsError(try service.validateConfiguration(config))
    }
}
