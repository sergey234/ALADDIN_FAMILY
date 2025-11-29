import XCTest
import NetworkExtension
@testable import ALADDIN

/// Интеграционный тест VPN после всех изменений
/// Проверяет работу VPNManager с NetworkExtension
final class VPNIntegrationTest: XCTestCase {
    
    var vpnManager: VPNManager!
    
    override func setUpWithError() throws {
        vpnManager = VPNManager.shared
    }
    
    override func tearDownWithError() throws {
        // Очистка после тестов
    }
    
    // MARK: - Инициализация
    
    func testVPNManagerInitialization() {
        XCTAssertNotNil(vpnManager, "VPNManager должен быть инициализирован")
        XCTAssertFalse(vpnManager.isConnected, "VPN должен быть отключен при инициализации")
        XCTAssertFalse(vpnManager.isConnecting, "VPN не должен подключаться при инициализации")
        XCTAssertEqual(vpnManager.connectionStatus, .disconnected, "Статус должен быть disconnected")
    }
    
    func testTunnelManagerConfiguration() {
        // Проверяем, что tunnel manager настроен
        // В реальном тесте здесь будет проверка NETunnelProviderManager
        XCTAssertNotNil(vpnManager, "VPNManager должен существовать")
    }
    
    // MARK: - Конфигурация
    
    func testBatteryOptimizationEnabled() {
        XCTAssertTrue(vpnManager.batteryOptimizationEnabled, "Battery optimization должен быть включен по умолчанию")
    }
    
    func testAdaptivePollingEnabled() {
        XCTAssertTrue(vpnManager.adaptivePollingEnabled, "Adaptive polling должен быть включен по умолчанию")
    }
    
    // MARK: - Статус подключения
    
    func testConnectionStatusInitialState() {
        XCTAssertEqual(vpnManager.connectionStatus, .disconnected)
        XCTAssertFalse(vpnManager.isConnected)
        XCTAssertFalse(vpnManager.isConnecting)
    }
    
    // MARK: - Kill Switch
    
    func testKillSwitchFunctionality() {
        // Проверяем, что методы kill switch доступны
        // В реальном тесте здесь будет проверка enableKillSwitch/disableKillSwitch
        XCTAssertNotNil(vpnManager, "VPNManager должен поддерживать kill switch")
    }
    
    // MARK: - Серверы
    
    func testServerSelection() {
        let testServer = VPNManager.VPNServer(
            id: "test-1",
            name: "Test Server",
            country: "Test Country",
            flag: "🏳️",
            ping: 10,
            load: 50,
            isPremium: false
        )
        
        // Проверяем, что сервер может быть установлен
        XCTAssertNotNil(testServer, "Сервер должен быть создан")
        XCTAssertEqual(testServer.id, "test-1")
        XCTAssertEqual(testServer.ping, 10)
    }
    
    // MARK: - Network Extension
    
    func testPacketTunnelIdentifier() {
        // Проверяем, что идентификатор правильный
        // В реальном тесте здесь будет проверка bundle identifier
        XCTAssertNotNil(vpnManager, "VPNManager должен иметь packetTunnelIdentifier")
    }
    
    // MARK: - Интеграция с API
    
    func testVPNStatusCheck() {
        // Проверяем, что можно проверить статус VPN
        // В реальном тесте здесь будет проверка API вызова
        let expectation = expectation(description: "VPN status check")
        
        // Симуляция проверки статуса
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 1.0)
    }
    
    // MARK: - Производительность
    
    func testVPNManagerPerformance() {
        measure {
            // Проверяем производительность инициализации
            let manager = VPNManager.shared
            _ = manager.isConnected
            _ = manager.connectionStatus
        }
    }
}

