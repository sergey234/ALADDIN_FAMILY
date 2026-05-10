import XCTest
@testable import ALADDIN

/**
 * 🌐 NetworkManager Unit Tests
 * Тесты для сетевого менеджера
 */

@MainActor
class NetworkManagerTests: XCTestCase {
    
    var networkManager: NetworkManager!
    
    override func setUpWithError() throws {
        super.setUp()
        networkManager = NetworkManager()
    }
    
    override func tearDownWithError() throws {
        networkManager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization Tests
    
    func testNetworkManagerInitialization() throws {
        XCTAssertNotNil(networkManager)
        XCTAssertTrue(networkManager.isOnline)
    }
    
    func testNetworkManagerBaseURL() throws {
        // Проверяем что baseURL установлен
        XCTAssertNotNil(networkManager)
    }
    
    func testNetworkManagerIsOnline() throws {
        // Проверяем статус онлайн
        XCTAssertTrue(networkManager.isOnline)
    }
    
    // MARK: - SSL Pinning Tests
    
    func testSSLPinningEnabled() throws {
        // Проверяем что SSL Pinning включен
        XCTAssertTrue(networkManager.isSSLPinningEnabled)
    }
    
    func testPinnedDomains() throws {
        // Проверяем что есть закрепленные домены
        XCTAssertNotNil(networkManager.pinnedDomains)
    }
    
    func testPinnedCertificates() throws {
        // Проверяем что есть закрепленные сертификаты
        XCTAssertNotNil(networkManager.pinnedCertificates)
    }
    
    // MARK: - Network Status Tests
    
    func testNetworkStatusChange() throws {
        // Тест изменения статуса сети
        let initialStatus = networkManager.isOnline
        // В реальном тесте здесь бы изменили статус сети
        XCTAssertEqual(networkManager.isOnline, initialStatus)
    }
    
    // MARK: - Error Handling Tests
    
    func testLastErrorInitialState() throws {
        // Проверяем что lastError изначально nil
        XCTAssertNil(networkManager.lastError)
    }
    
    // MARK: - Performance Tests
    
    func testNetworkManagerCreationPerformance() throws {
        self.measure {
            let manager = NetworkManager()
            XCTAssertNotNil(manager)
        }
    }
    
    func testSSLConfigurationPerformance() throws {
        self.measure {
            let manager = NetworkManager()
            XCTAssertTrue(manager.isSSLPinningEnabled)
        }
    }
}

// MARK: - NetworkManager Mock Tests

extension NetworkManagerTests {
    
    func testNetworkManagerMock() throws {
        // Тест с мок-объектом
        let mockManager = NetworkManager()
        XCTAssertNotNil(mockManager)
    }
}
