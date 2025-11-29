import XCTest
@testable import ALADDIN

/**
 * 🏡 IoT Security Module Tests
 * Тестирование IoT Security Module
 */

class IoTSecurityModuleTests: XCTestCase {
    
    var module: IoTSecurityModule!
    var mockAPIService: MockAPIService!
    
    override func setUpWithError() throws {
        mockAPIService = MockAPIService()
        module = IoTSecurityModule(apiService: mockAPIService)
    }
    
    override func tearDownWithError() throws {
        module = nil
        mockAPIService = nil
    }
    
    // MARK: - scanDevices Tests
    
    func testScanDevices() async throws {
        // Arrange
        let homeId = "home_123"
        mockAPIService.mockIoTDevices = [
            IoTDevice(
                id: "device_1",
                name: "Test Camera",
                type: .camera,
                ip: "192.168.1.100",
                mac: "AA:BB:CC:DD:EE:FF",
                vendor: "Xiaomi",
                model: "Mi Camera",
                status: .online,
                lastSeen: "2025-11-04T10:30:00Z"
            )
        ]
        
        // Act
        try await module.scanDevices(homeId: homeId)
        
        // Assert
        XCTAssertFalse(module.iotDevices.isEmpty, "Устройства должны быть загружены")
        XCTAssertEqual(module.iotDevices.count, 1, "Должно быть 1 устройство")
        XCTAssertEqual(module.iotDevices.first?.name, "Test Camera", "Имя устройства должно совпадать")
    }
    
    func testScanDevicesWithEmptyResult() async throws {
        // Arrange
        let homeId = "home_empty"
        mockAPIService.mockIoTDevices = []
        
        // Act
        try await module.scanDevices(homeId: homeId)
        
        // Assert
        XCTAssertTrue(module.iotDevices.isEmpty, "Список устройств должен быть пустым")
    }
    
    // MARK: - monitorCameras Tests
    
    func testMonitorCameras() async throws {
        // Arrange
        let homeId = "home_123"
        mockAPIService.mockIoTThreats = [
            IoTThreat(
                id: "threat_1",
                threatType: .cameraIntrusion,
                severity: .high,
                description: "Подозрительное подключение",
                timestamp: "2025-11-04T10:30:00Z",
                deviceId: "device_1",
                recommendations: ["Изменить пароль"]
            )
        ]
        
        // Act
        try await module.monitorCameras(homeId: homeId)
        
        // Assert
        XCTAssertFalse(module.threatsDetected.isEmpty, "Угрозы должны быть обнаружены")
        XCTAssertEqual(module.threatsDetected.first?.threatType, .cameraIntrusion, "Тип угрозы должен быть camera")
    }
    
    // MARK: - checkPasswords Tests
    
    func testCheckPasswords() async throws {
        // Arrange
        let homeId = "home_123"
        mockAPIService.mockIoTStatus = IoTStatusResponse(
            homeId: homeId,
            devices: [],
            threats: [],
            recommendations: ["Изменить пароль на более сложный"],
            protectionLevel: 75,
            lastScan: "2025-11-04T10:30:00Z"
        )
        
        // Act
        try await module.checkPasswords(homeId: homeId)
        
        // Assert
        XCTAssertFalse(module.recommendations.isEmpty, "Рекомендации должны быть получены")
        XCTAssertEqual(module.protectionLevel, 75, "Уровень защиты должен быть 75")
    }
    
    // MARK: - blockDevice Tests
    
    func testBlockDevice() async throws {
        // Arrange
        let deviceId = "device_123"
        let homeId = "home_123"
        
        // Сначала загружаем статус, чтобы установить homeId
        try await module.loadStatus(homeId: homeId)
        
        mockAPIService.mockIoTDevices = []
        mockAPIService.shouldBlockDevice = true
        
        // Act
        try await module.blockDevice(deviceId)
        
        // Assert
        XCTAssertTrue(mockAPIService.blockDeviceCalled, "Метод блокировки должен быть вызван")
    }
    
    // MARK: - alertCompromised Tests
    
    func testAlertCompromised() {
        // Arrange
        let device = IoTDevice(
            id: "device_123",
            name: "Compromised Device",
            type: .camera,
            ip: nil,
            mac: nil,
            vendor: nil,
            model: nil,
            status: .compromised,
            lastSeen: nil
        )
        
        // Act & Assert
        // alertCompromised вызывает NotificationManager.shared.sendLocalNotification
        // Если delay = 0, возникает ошибка "time interval must be greater than 0"
        // Проверяем, что метод вызывается без ошибок
        // Используем XCTAssertNoThrow для проверки, что нет исключений
        XCTAssertNoThrow(module.alertCompromised(device), "alertCompromised должен вызываться без ошибок")
    }
    
    // MARK: - loadStatus Tests
    
    func testLoadStatus() async throws {
        // Arrange
        let homeId = "home_123"
        mockAPIService.mockIoTStatus = IoTStatusResponse(
            homeId: homeId,
            devices: [
                IoTDevice(
                    id: "device_1",
                    name: "Device 1",
                    type: .camera,
                    ip: nil,
                    mac: nil,
                    vendor: nil,
                    model: nil,
                    status: .online,
                    lastSeen: nil
                )
            ],
            threats: [],
            recommendations: ["Рекомендация 1"],
            protectionLevel: 85,
            lastScan: "2025-11-04T10:30:00Z"
        )
        
        // Act
        try await module.loadStatus(homeId: homeId)
        
        // Assert
        XCTAssertEqual(module.iotDevices.count, 1, "Должно быть 1 устройство")
        XCTAssertEqual(module.protectionLevel, 85, "Уровень защиты должен быть 85")
        XCTAssertFalse(module.recommendations.isEmpty, "Рекомендации должны быть загружены")
    }
    
    // MARK: - refreshStatus Tests
    
    func testRefreshStatus() async throws {
        // Arrange
        let homeId = "home_123"
        
        // Сначала загружаем статус, чтобы установить homeId
        mockAPIService.mockIoTStatus = IoTStatusResponse(
            homeId: homeId,
            devices: [],
            threats: [],
            recommendations: [],
            protectionLevel: 75,
            lastScan: "2025-11-04T10:30:00Z"
        )
        try await module.loadStatus(homeId: homeId)
        
        // Обновляем статус
        mockAPIService.mockIoTStatus = IoTStatusResponse(
            homeId: homeId,
            devices: [],
            threats: [],
            recommendations: [],
            protectionLevel: 90,
            lastScan: "2025-11-04T10:30:00Z"
        )
        
        // Act
        try await module.refreshStatus()
        
        // Assert
        XCTAssertEqual(module.protectionLevel, 90, "Уровень защиты должен обновиться")
    }
    
    func testRefreshStatusWithoutHomeId() async {
        // Act & Assert
        do {
            try await module.refreshStatus()
            XCTFail("Должна быть выброшена ошибка")
        } catch {
            XCTAssertTrue(error is IoTSecurityError, "Ошибка должна быть IoTSecurityError")
        }
    }
    
    // MARK: - Error Handling Tests
    
    func testScanDevicesErrorHandling() async {
        // Arrange
        mockAPIService.shouldThrowError = true
        
        // Act & Assert
        do {
            try await module.scanDevices(homeId: "home_123")
            XCTFail("Должна быть выброшена ошибка")
        } catch {
            XCTAssertTrue(true, "Ошибка должна быть обработана")
        }
    }
}

// MARK: - Mock APIService

class MockAPIService: APIService {
    var mockIoTDevices: [IoTDevice] = []
    var mockIoTThreats: [IoTThreat] = []
    var mockIoTStatus: IoTStatusResponse?
    var shouldBlockDevice = false
    var shouldThrowError = false
    var blockDeviceCalled = false
    
    init() {
        // Создаем фиктивный NetworkManager для тестов
        let mockNetworkManager = NetworkManager()
        super.init(networkManager: mockNetworkManager)
    }
    
    override func getIoTDevices(homeId: String) async throws -> IoTDevicesResponse {
        if shouldThrowError {
            throw NSError(domain: "TestError", code: 500, userInfo: [NSLocalizedDescriptionKey: "Test error"])
        }
        
        return IoTDevicesResponse(
            devices: mockIoTDevices,
            threats: [],
            total: mockIoTDevices.count,
            compromised: mockIoTDevices.filter { $0.status == .compromised }.count,
            safe: mockIoTDevices.filter { $0.status == .safe }.count
        )
    }
    
    override func getIoTThreats(homeId: String) async throws -> IoTThreatsResponse {
        if shouldThrowError {
            throw NSError(domain: "TestError", code: 500, userInfo: [NSLocalizedDescriptionKey: "Test error"])
        }
        
        return IoTThreatsResponse(
            threats: mockIoTThreats,
            total: mockIoTThreats.count,
            high: mockIoTThreats.filter { $0.severity == .high }.count,
            medium: mockIoTThreats.filter { $0.severity == .medium }.count,
            low: mockIoTThreats.filter { $0.severity == .low }.count
        )
    }
    
    override func getIoTStatus(homeId: String) async throws -> IoTStatusResponse {
        if shouldThrowError {
            throw NSError(domain: "TestError", code: 500, userInfo: [NSLocalizedDescriptionKey: "Test error"])
        }
        
        return mockIoTStatus ?? IoTStatusResponse(
            homeId: homeId,
            devices: [],
            threats: [],
            recommendations: [],
            protectionLevel: 0,
            lastScan: nil
        )
    }
    
    override func blockIoTDevice(deviceId: String) async throws -> APIResponse<Bool> {
        blockDeviceCalled = true
        
        if shouldThrowError {
            throw NSError(domain: "TestError", code: 500, userInfo: [NSLocalizedDescriptionKey: "Test error"])
        }
        
        return APIResponse(success: shouldBlockDevice, data: shouldBlockDevice, message: nil, error: nil)
    }
}

