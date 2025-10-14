import XCTest
@testable import ALADDINMobile

class CertificatePinningTests: XCTestCase {
    
    var certificatePinningManager: CertificatePinningManager!
    var networkManager: ALADDINNetworkManager!
    
    override func setUp() {
        super.setUp()
        certificatePinningManager = CertificatePinningManager.shared
        networkManager = ALADDINNetworkManager.shared
    }
    
    override func tearDown() {
        certificatePinningManager = nil
        networkManager = nil
        super.tearDown()
    }
    
    // MARK: - Certificate Pinning Tests
    
    func testCertificatePinningManagerInitialization() {
        // Проверяем, что менеджер инициализируется
        XCTAssertNotNil(certificatePinningManager)
    }
    
    func testPinnedHostsList() {
        // Проверяем, что список защищенных хостов не пустой
        let status = certificatePinningManager.getPinningStatus()
        XCTAssertFalse(status.isEmpty)
        
        // Проверяем наличие основных хостов
        XCTAssertTrue(status.keys.contains("api.aladdin.security"))
        XCTAssertTrue(status.keys.contains("ai.aladdin.security"))
        XCTAssertTrue(status.keys.contains("vpn.aladdin.security"))
    }
    
    func testCertificateValidation() {
        // Создаем мок сертификат для тестирования
        let mockTrust = createMockSecTrust()
        let host = "api.aladdin.security"
        
        // Тестируем валидацию (в реальном тесте здесь был бы настоящий сертификат)
        let isValid = certificatePinningManager.validateCertificate(mockTrust, host: host)
        
        // В тестовой среде ожидаем false, так как используем мок
        XCTAssertFalse(isValid)
    }
    
    func testInvalidHostValidation() {
        let mockTrust = createMockSecTrust()
        let invalidHost = "malicious-site.com"
        
        let isValid = certificatePinningManager.validateCertificate(mockTrust, host: invalidHost)
        XCTAssertFalse(isValid)
    }
    
    // MARK: - Network Manager Tests
    
    func testNetworkManagerInitialization() {
        XCTAssertNotNil(networkManager)
    }
    
    func testSecureRequest() {
        let expectation = XCTestExpectation(description: "Secure request")
        
        // Тестируем безопасный запрос
        networkManager.secureRequest(
            "test",
            method: .get,
            responseType: TestResponse.self
        ) { result in
            switch result {
            case .success:
                XCTFail("Expected failure in test environment")
            case .failure(let error):
                // Ожидаем ошибку в тестовой среде
                XCTAssertNotNil(error)
            }
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testPinningStatus() {
        let status = networkManager.getPinningStatus()
        XCTAssertFalse(status.isEmpty)
    }
    
    // MARK: - Helper Methods
    
    private func createMockSecTrust() -> SecTrust {
        // Создаем мок SecTrust для тестирования
        var trust: SecTrust?
        let result = SecTrustCreateWithCertificates(
            createMockCertificate(),
            SecPolicyCreateSSL(true, "api.aladdin.security" as CFString),
            &trust
        )
        
        XCTAssertEqual(result, errSecSuccess)
        return trust!
    }
    
    private func createMockCertificate() -> SecCertificate {
        // Создаем мок сертификат для тестирования
        let mockCertData = Data("mock_certificate_data".utf8)
        let cert = SecCertificateCreateWithData(nil, mockCertData as CFData)
        return cert!
    }
}

// MARK: - Test Response Model
struct TestResponse: Codable {
    let message: String
    let success: Bool
}

// MARK: - Performance Tests
class CertificatePinningPerformanceTests: XCTestCase {
    
    func testCertificateValidationPerformance() {
        let manager = CertificatePinningManager.shared
        let mockTrust = createMockSecTrust()
        
        measure {
            for _ in 0..<1000 {
                _ = manager.validateCertificate(mockTrust, host: "api.aladdin.security")
            }
        }
    }
    
    private func createMockSecTrust() -> SecTrust {
        var trust: SecTrust?
        let result = SecTrustCreateWithCertificates(
            createMockCertificate(),
            SecPolicyCreateSSL(true, "api.aladdin.security" as CFString),
            &trust
        )
        
        XCTAssertEqual(result, errSecSuccess)
        return trust!
    }
    
    private func createMockCertificate() -> SecCertificate {
        let mockCertData = Data("mock_certificate_data".utf8)
        let cert = SecCertificateCreateWithData(nil, mockCertData as CFData)
        return cert!
    }
}

