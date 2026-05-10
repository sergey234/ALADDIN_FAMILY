import XCTest
@testable import ALADDIN

@MainActor
final class SharedDataManagerTests: XCTestCase {

    override func setUpWithError() throws {
        SharedDataManager.clearAllData()
    }

    override func tearDownWithError() throws {
        SharedDataManager.clearAllData()
    }

    func testUpdateAndRetrieveFamilyProtectionData() {
        SharedDataManager.updateFamilyProtectionData(isEnabled: true, childrenOnline: 3, threatsBlocked: 12)

        let data = SharedDataManager.getFamilyProtectionData()
        XCTAssertTrue(data.isEnabled)
        XCTAssertEqual(data.childrenOnline, 3)
        XCTAssertEqual(data.threatsBlocked, 12)
    }

    func testUpdateAndRetrieveNetworkProtectionData() {
        SharedDataManager.updateNetworkProtectionData(
            isConnected: true,
            server: "Германия",
            speed: "55 Мбит/с",
            uptime: "2ч 15м"
        )

        let data = SharedDataManager.getNetworkProtectionData()
        XCTAssertTrue(data.isConnected)
        XCTAssertEqual(data.server, "Германия")
        XCTAssertEqual(data.speed, "55 Мбит/с")
        XCTAssertEqual(data.uptime, "2ч 15м")
    }

    func testUpdateAndRetrieveAnalyticsData() {
        SharedDataManager.updateAnalyticsData(
            threatsBlocked: 20,
            websitesBlocked: 5,
            appsBlocked: 2,
            dataSaved: "1.5 ГБ",
            protectionLevel: "Высокий"
        )

        let data = SharedDataManager.getAnalyticsData()
        XCTAssertEqual(data.threatsBlocked, 20)
        XCTAssertEqual(data.websitesBlocked, 5)
        XCTAssertEqual(data.appsBlocked, 2)
        XCTAssertEqual(data.dataSaved, "1.5 ГБ")
        XCTAssertEqual(data.protectionLevel, "Высокий")
    }

    func testLastUpdateChangesAfterDataUpdate() {
        let before = SharedDataManager.getLastUpdate()
        SharedDataManager.updateFamilyProtectionData(isEnabled: true, childrenOnline: 1, threatsBlocked: 1)
        let after = SharedDataManager.getLastUpdate()
        XCTAssertTrue(after >= before)
    }

    func testClearAllDataResetsStoredValues() {
        SharedDataManager.updateFamilyProtectionData(isEnabled: true, childrenOnline: 2, threatsBlocked: 8)
        SharedDataManager.updateNetworkProtectionData(isConnected: true, server: "США", speed: "20 Мбит/с", uptime: "1ч")
        SharedDataManager.updateAnalyticsData(threatsBlocked: 5, websitesBlocked: 3, appsBlocked: 1, dataSaved: "500 МБ", protectionLevel: "Средний")

        SharedDataManager.clearAllData()

        let family = SharedDataManager.getFamilyProtectionData()
        let net = SharedDataManager.getNetworkProtectionData()
        let analytics = SharedDataManager.getAnalyticsData()

        XCTAssertFalse(family.isEnabled)
        XCTAssertEqual(family.childrenOnline, 0)
        XCTAssertEqual(family.threatsBlocked, 0)

        XCTAssertFalse(net.isConnected)
        XCTAssertEqual(net.server, "Не подключен")
        XCTAssertEqual(net.speed, "0 Мбит/с")
        XCTAssertEqual(net.uptime, "0м")

        XCTAssertEqual(analytics.threatsBlocked, 0)
        XCTAssertEqual(analytics.websitesBlocked, 0)
        XCTAssertEqual(analytics.appsBlocked, 0)
        XCTAssertEqual(analytics.dataSaved, "0 ГБ")
        XCTAssertEqual(analytics.protectionLevel, "Средний")
    }
}
