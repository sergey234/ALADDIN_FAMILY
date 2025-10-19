import XCTest
@testable import ALADDIN

/**
 * 🌐 APIService Unit Tests
 * Тесты для API сервиса
 * Цель: 100% покрытие APIService
 */

class APIServiceTests: XCTestCase {
    
    var apiService: APIService!
    var mockNetworkManager: MockNetworkManager!
    
    override func setUpWithError() throws {
        super.setUp()
        mockNetworkManager = MockNetworkManager()
        apiService = APIService(networkManager: mockNetworkManager)
    }
    
    override func tearDownWithError() throws {
        apiService = nil
        mockNetworkManager = nil
        super.tearDown()
    }
    
    // MARK: - Initialization Tests
    
    func testAPIServiceInitialization() throws {
        XCTAssertNotNil(apiService)
        XCTAssertNotNil(apiService.networkManager)
    }
    
    func testAPIServiceWithCustomNetworkManager() throws {
        let customNetworkManager = NetworkManager()
        let customAPIService = APIService(networkManager: customNetworkManager)
        
        XCTAssertNotNil(customAPIService)
        XCTAssertNotNil(customAPIService.networkManager)
    }
    
    // MARK: - VPN API Tests
    
    func testGetVPNStatus() throws {
        let expectation = XCTestExpectation(description: "Get VPN Status")
        
        apiService.getVPNStatus { result in
            switch result {
            case .success(let status):
                XCTAssertNotNil(status)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testConnectVPN() throws {
        let expectation = XCTestExpectation(description: "Connect VPN")
        
        apiService.connectVPN { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testDisconnectVPN() throws {
        let expectation = XCTestExpectation(description: "Disconnect VPN")
        
        apiService.disconnectVPN { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Family API Tests
    
    func testCreateFamily() throws {
        let expectation = XCTestExpectation(description: "Create Family")
        
        let request = CreateFamilyRequest(
            family_name: "Тестовая Семья",
            family_code: "TEST123",
            recovery_code: "RECOVER123"
        )
        
        apiService.createFamily(request: request) { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testJoinFamily() throws {
        let expectation = XCTestExpectation(description: "Join Family")
        
        let request = JoinFamilyRequest(family_code: "TEST123")
        
        apiService.joinFamily(request: request) { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testRecoverFamily() throws {
        let expectation = XCTestExpectation(description: "Recover Family")
        
        let request = RecoverFamilyRequest(recovery_code: "RECOVER123")
        
        apiService.recoverFamily(request: request) { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Payment API Tests
    
    func testCreateQRPayment() throws {
        let expectation = XCTestExpectation(description: "Create QR Payment")
        
        let request = CreateQRPaymentRequest(
            family_id: "test-family-id",
            tariff: "Premium",
            amount: 590.0,
            payment_method: "sbp"
        )
        
        apiService.createQRPayment(request: request) { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testCheckQRPaymentStatus() throws {
        let expectation = XCTestExpectation(description: "Check QR Payment Status")
        
        apiService.checkQRPaymentStatus(paymentId: "test-payment-id") { result in
            switch result {
            case .success(let response):
                XCTAssertNotNil(response)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Expected success, got error: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Error Handling Tests
    
    func testNetworkErrorHandling() throws {
        let expectation = XCTestExpectation(description: "Network Error Handling")
        
        // Настраиваем мок для возврата ошибки
        mockNetworkManager.shouldReturnError = true
        mockNetworkManager.mockError = NetworkError.networkUnavailable
        
        apiService.getVPNStatus { result in
            switch result {
            case .success:
                XCTFail("Expected error, got success")
            case .failure(let error):
                XCTAssertNotNil(error)
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testTimeoutErrorHandling() throws {
        let expectation = XCTestExpectation(description: "Timeout Error Handling")
        
        // Настраиваем мок для таймаута
        mockNetworkManager.shouldReturnError = true
        mockNetworkManager.mockError = NetworkError.timeout
        
        apiService.connectVPN { result in
            switch result {
            case .success:
                XCTFail("Expected error, got success")
            case .failure(let error):
                XCTAssertNotNil(error)
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Performance Tests
    
    func testAPIServiceCreationPerformance() throws {
        self.measure {
            let service = APIService(networkManager: mockNetworkManager)
            XCTAssertNotNil(service)
        }
    }
    
    func testVPNStatusPerformance() throws {
        self.measure {
            let expectation = XCTestExpectation(description: "Performance Test")
            
            apiService.getVPNStatus { _ in
                expectation.fulfill()
            }
            
            wait(for: [expectation], timeout: 1.0)
        }
    }
    
    // MARK: - Concurrent Access Tests
    
    func testConcurrentAPICalls() throws {
        let expectation = XCTestExpectation(description: "Concurrent API Calls")
        expectation.expectedFulfillmentCount = 3
        
        let queue = DispatchQueue(label: "test.queue", attributes: .concurrent)
        
        queue.async {
            self.apiService.getVPNStatus { _ in
                expectation.fulfill()
            }
        }
        
        queue.async {
            self.apiService.connectVPN { _ in
                expectation.fulfill()
            }
        }
        
        queue.async {
            self.apiService.disconnectVPN { _ in
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
}

// MARK: - Mock Network Manager

class MockNetworkManager: NetworkManager {
    
    var shouldReturnError = false
    var mockError: NetworkError = .unknown
    
    override func get<T: Codable>(endpoint: String, completion: @escaping (Result<T, Error>) -> Void) {
        if shouldReturnError {
            completion(.failure(mockError))
        } else {
            // Возвращаем мок данные
            if T.self == VPNStatusResponse.self {
                let mockResponse = VPNStatusResponse(
                    status: "connected",
                    server: "test-server",
                    ip: "192.168.1.1",
                    country: "Russia"
                ) as! T
                completion(.success(mockResponse))
            } else {
                // Для других типов возвращаем пустой объект
                completion(.failure(NetworkError.unknown))
            }
        }
    }
    
    override func post<T: Codable, U: Codable>(endpoint: String, body: T, completion: @escaping (Result<U, Error>) -> Void) {
        if shouldReturnError {
            completion(.failure(mockError))
        } else {
            // Возвращаем мок данные
            if U.self == CreateFamilyResponse.self {
                let mockResponse = CreateFamilyResponse(
                    success: true,
                    family_id: "test-family-id",
                    message: "Family created successfully"
                ) as! U
                completion(.success(mockResponse))
            } else {
                completion(.failure(NetworkError.unknown))
            }
        }
    }
}

// MARK: - Mock Response Types

struct MockVPNStatusResponse: Codable {
    let status: String
    let server: String
    let ip: String
    let country: String
}

struct MockCreateFamilyResponse: Codable {
    let success: Bool
    let family_id: String
    let message: String
}
