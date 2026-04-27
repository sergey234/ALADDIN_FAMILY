import XCTest
@testable import ALADDIN

@MainActor
final class ComponentCacheServiceTests: XCTestCase {

    func testSaveAndLoadStatus() async {
        let service = ComponentCacheService.shared
        await service.clearAllCache()

        let componentId = "unit_test_status_\(UUID().uuidString)"
        let status = ComponentStatus(
            componentId: componentId,
            isEnabled: true,
            lastUpdate: Date(),
            configuration: nil
        )

        await service.saveStatus(componentId: componentId, status: status)

        let loadedStatus = await service.loadStatus(componentId: componentId)
        XCTAssertNotNil(loadedStatus)
        XCTAssertEqual(loadedStatus?.componentId, componentId)
        XCTAssertTrue(loadedStatus?.isEnabled ?? false)

        await service.clearAllCache()
    }

    func testLoadAllStatusesReturnsMultiple() async {
        let service = ComponentCacheService.shared
        await service.clearAllCache()

        let id1 = "unit_test_c1_\(UUID().uuidString)"
        let id2 = "unit_test_c2_\(UUID().uuidString)"
        let status1 = ComponentStatus(componentId: id1, isEnabled: true, lastUpdate: Date(), configuration: nil)
        let status2 = ComponentStatus(componentId: id2, isEnabled: false, lastUpdate: Date(), configuration: nil)
        await service.saveStatus(componentId: id1, status: status1)
        await service.saveStatus(componentId: id2, status: status2)

        let allStatuses = await service.loadAllStatuses()
        XCTAssertEqual(allStatuses[id1]?.componentId, id1)
        XCTAssertEqual(allStatuses[id2]?.componentId, id2)

        await service.clearAllCache()
    }
}
