import XCTest
@testable import ALADDIN

// MARK: - RecoverFamilyResponse для тестов
// Определение из FamilyRegistrationViewModel.swift
struct RecoverFamilyResponse: Codable {
    let success: Bool
    let message: String
    let familyId: String?
    let members: [FamilyMemberResponse]
}

/**
 * 🧪 Mock API Service Tests
 * Автоматизированные тесты для проверки всех критических методов Mock API
 */

class MockAPIServiceTests: XCTestCase {
    
    var apiService: APIService!
    var expectation: XCTestExpectation!
    
    override func setUp() {
        super.setUp()
        // Включаем Mock API для тестов
        AppConfig.useMockAPI = true
        // Используем APIService.shared, который автоматически переключается на Mock API
        apiService = APIService.shared
        expectation = XCTestExpectation(description: "API call completed")
    }
    
    override func tearDown() {
        apiService = nil
        expectation = nil
        AppConfig.useMockAPI = false // Отключаем Mock API после тестов
        super.tearDown()
    }
    
    // MARK: - Test 1: Регистрация и вход
    
    func testLogin() {
        // Given
        let email = "test@aladdin.family"
        let password = "TestPassword123"
        
        // When
        apiService.login(email: email, password: password) { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertNotNil(response.token, "Token should not be nil")
                XCTAssertEqual(response.userId, "user_mock_123", "User ID should match")
                XCTAssertNotNil(response.expiresAt, "ExpiresAt should not be nil")
                print("✅ Test 1.1: Login - SUCCESS")
                print("   Token: \(response.token)")
                print("   User ID: \(response.userId)")
            case .failure(let error):
                XCTFail("Login should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testLogout() {
        // Given
        AppConfig.authToken = "test_token"
        
        // When
        apiService.logout { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success, "Logout should succeed")
                XCTAssertNil(AppConfig.authToken, "Token should be cleared")
                print("✅ Test 1.2: Logout - SUCCESS")
            case .failure(let error):
                XCTFail("Logout should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 2: Загрузка профиля
    
    func testGetUserProfile() {
        // When
        apiService.getUserProfile { [weak self] result in
            // Then
            switch result {
            case .success(let profile):
                XCTAssertEqual(profile.id, "user_mock_123", "Profile ID should match")
                XCTAssertEqual(profile.name, "Test User", "Name should match")
                XCTAssertEqual(profile.email, "test@aladdin.family", "Email should match")
                XCTAssertEqual(profile.subscriptionType, "family", "Subscription type should match")
                XCTAssertEqual(profile.threatsBlocked, 47, "Threats blocked should match")
                XCTAssertEqual(profile.familyMembers, 4, "Family members should match")
                XCTAssertEqual(profile.devices, 8, "Devices should match")
                print("✅ Test 2: GetUserProfile - SUCCESS")
                print("   Name: \(profile.name)")
                print("   Email: \(profile.email)")
                print("   Subscription: \(profile.subscriptionType)")
                print("   Threats Blocked: \(profile.threatsBlocked)")
            case .failure(let error):
                XCTFail("GetUserProfile should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 3: Загрузка семьи
    
    func testGetFamilyMembers() {
        // When
        apiService.getFamilyMembers { [weak self] result in
            // Then
            switch result {
            case .success(let members):
                XCTAssertEqual(members.count, 4, "Should have 4 family members")
                XCTAssertEqual(members[0].name, "Родитель", "First member should be parent")
                XCTAssertEqual(members[0].role, "parent", "First member role should be parent")
                XCTAssertEqual(members[1].name, "Ребенок", "Second member should be child")
                XCTAssertEqual(members[1].role, "child", "Second member role should be child")
                print("✅ Test 3.1: GetFamilyMembers - SUCCESS")
                print("   Members count: \(members.count)")
                for member in members {
                    print("   - \(member.name) (\(member.role)): \(member.status)")
                }
            case .failure(let error):
                XCTFail("GetFamilyMembers should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testGetFamilyStats() {
        // When
        apiService.getFamilyStats { [weak self] result in
            // Then
            switch result {
            case .success(let stats):
                XCTAssertEqual(stats.totalMembers, 4, "Total members should be 4")
                XCTAssertEqual(stats.totalDevices, 8, "Total devices should be 8")
                XCTAssertEqual(stats.totalThreats, 47, "Total threats should be 47")
                XCTAssertEqual(stats.protectionLevel, 95, "Protection level should be 95")
                print("✅ Test 3.2: GetFamilyStats - SUCCESS")
                print("   Total Members: \(stats.totalMembers)")
                print("   Total Devices: \(stats.totalDevices)")
                print("   Total Threats: \(stats.totalThreats)")
                print("   Protection Level: \(stats.protectionLevel)%")
            case .failure(let error):
                XCTFail("GetFamilyStats should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 4: Загрузка тарифов
    
    func testGetTariffs() {
        // When
        apiService.getTariffs { [weak self] result in
            // Then
            switch result {
            case .success(let tariffs):
                XCTAssertEqual(tariffs.count, 4, "Should have 4 tariffs")
                XCTAssertEqual(tariffs[0].id, "free", "First tariff should be free")
                XCTAssertEqual(tariffs[0].price, 0, "Free tariff price should be 0")
                XCTAssertEqual(tariffs[1].id, "personal", "Second tariff should be personal")
                XCTAssertEqual(tariffs[1].price, 299, "Personal tariff price should be 299")
                XCTAssertEqual(tariffs[2].id, "family", "Third tariff should be family")
                XCTAssertEqual(tariffs[2].price, 499, "Family tariff price should be 499")
                XCTAssertTrue(tariffs[2].isRecommended, "Family tariff should be recommended")
                print("✅ Test 4: GetTariffs - SUCCESS")
                for tariff in tariffs {
                    print("   - \(tariff.name): \(tariff.price)₽ (\(tariff.period))")
                }
            case .failure(let error):
                XCTFail("GetTariffs should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 5: QR-оплата
    
    func testCreateQRPayment() {
        // Given
        let request = CreateQRPaymentRequest(
            amount: 499.0,
            currency: "RUB",
            description: "Family subscription",
            tariffId: "family",
            periodMonths: nil
        )
        
        // When
        apiService.createQRPayment(request: request) { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertNotNil(response.paymentId, "Payment ID should not be nil")
                XCTAssertNotNil(response.qrCode, "QR Code should not be nil")
                XCTAssertEqual(response.amount, 499.0, "Amount should match")
                XCTAssertEqual(response.currency, "RUB", "Currency should match")
                XCTAssertEqual(response.status, "pending", "Status should be pending")
                print("✅ Test 5.1: CreateQRPayment - SUCCESS")
                print("   Payment ID: \(response.paymentId)")
                print("   Amount: \(response.amount) \(response.currency)")
                print("   Status: \(response.status)")
            case .failure(let error):
                XCTFail("CreateQRPayment should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testCheckQRPaymentStatus() {
        // Given
        let paymentId = "payment_mock_123"
        
        // When
        apiService.checkQRPaymentStatus(paymentId: paymentId) { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertEqual(response.paymentId, paymentId, "Payment ID should match")
                XCTAssertEqual(response.status, "pending", "Status should be pending")
                XCTAssertEqual(response.amount, 499.0, "Amount should match")
                print("✅ Test 5.2: CheckQRPaymentStatus - SUCCESS")
                print("   Payment ID: \(response.paymentId)")
                print("   Status: \(response.status)")
            case .failure(let error):
                XCTFail("CheckQRPaymentStatus should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 6: VPN статус
    
    func testGetVPNStatus() {
        // When
        apiService.getVPNStatus { [weak self] result in
            // Then
            switch result {
            case .success(let status):
                XCTAssertFalse(status.isConnected, "VPN should be disconnected by default")
                XCTAssertEqual(status.serverLocation, "Германия", "Server location should match")
                XCTAssertEqual(status.ipAddress, "192.168.1.1", "IP address should match")
                XCTAssertEqual(status.ping, 45, "Ping should be 45")
                print("✅ Test 6.1: GetVPNStatus - SUCCESS")
                print("   Connected: \(status.isConnected)")
                print("   Server: \(status.serverLocation)")
                print("   IP: \(status.ipAddress)")
                print("   Ping: \(status.ping)ms")
            case .failure(let error):
                XCTFail("GetVPNStatus should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testGetVPNServers() {
        // When
        apiService.getVPNServers { [weak self] result in
            // Then
            switch result {
            case .success(let servers):
                XCTAssertEqual(servers.count, 4, "Should have 4 VPN servers")
                XCTAssertEqual(servers[0].country, "Германия", "First server should be Germany")
                XCTAssertEqual(servers[0].city, "Берлин", "First server city should be Berlin")
                XCTAssertEqual(servers[1].country, "США", "Second server should be USA")
                print("✅ Test 6.2: GetVPNServers - SUCCESS")
                for server in servers {
                    print("   - \(server.country) (\(server.city)): \(server.status.rawValue), ping: \(server.ping)ms")
                }
            case .failure(let error):
                XCTFail("GetVPNServers should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testConnectVPN() {
        // When
        apiService.connectVPN { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success, "Connect VPN should succeed")
                print("✅ Test 6.3: ConnectVPN - SUCCESS")
            case .failure(let error):
                XCTFail("ConnectVPN should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testDisconnectVPN() {
        // When
        apiService.disconnectVPN { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success, "Disconnect VPN should succeed")
                print("✅ Test 6.4: DisconnectVPN - SUCCESS")
            case .failure(let error):
                XCTFail("DisconnectVPN should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 7: Аналитика
    
    func testGetAnalytics() {
        // Given
        let period = "week"
        
        // When
        apiService.getAnalytics(period: period) { [weak self] result in
            // Then
            switch result {
            case .success(let analytics):
                XCTAssertEqual(analytics.period, period, "Period should match")
                XCTAssertEqual(analytics.threatsDetected, 47, "Threats detected should be 47")
                XCTAssertEqual(analytics.threatsBlocked, 45, "Threats blocked should be 45")
                XCTAssertEqual(analytics.protectionLevel, 95, "Protection level should be 95")
                XCTAssertGreaterThan(analytics.topThreats.count, 0, "Should have top threats")
                print("✅ Test 7.1: GetAnalytics - SUCCESS")
                print("   Period: \(analytics.period)")
                print("   Threats Detected: \(analytics.threatsDetected)")
                print("   Threats Blocked: \(analytics.threatsBlocked)")
                print("   Protection Level: \(analytics.protectionLevel)%")
            case .failure(let error):
                XCTFail("GetAnalytics should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testGetTopThreats() {
        // When
        apiService.getTopThreats { [weak self] result in
            // Then
            switch result {
            case .success(let threats):
                XCTAssertGreaterThan(threats.count, 0, "Should have threats")
                XCTAssertEqual(threats[0].name, "Фишинг", "First threat should be Фишинг")
                XCTAssertEqual(threats[0].count, 15, "First threat count should be 15")
                print("✅ Test 7.2: GetTopThreats - SUCCESS")
                for threat in threats {
                    print("   - \(threat.name): \(threat.count) (\(threat.severity))")
                }
            case .failure(let error):
                XCTFail("GetTopThreats should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 8: Уведомления
    
    func testGetNotifications() {
        // When
        apiService.getNotifications { [weak self] result in
            // Then
            switch result {
            case .success(let notifications):
                XCTAssertGreaterThan(notifications.count, 0, "Should have notifications")
                XCTAssertEqual(notifications[0].title, "Угроза заблокирована", "First notification title should match")
                XCTAssertFalse(notifications[0].isRead, "First notification should be unread")
                print("✅ Test 8: GetNotifications - SUCCESS")
                for notification in notifications {
                    print("   - \(notification.title): \(notification.isRead ? "прочитано" : "не прочитано")")
                }
            case .failure(let error):
                XCTFail("GetNotifications should succeed, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 9: Удаление аккаунта
    
    func testDeleteAccountSuccess() {
        // Given
        let confirmationCode = "УДАЛИТЬ"
        AppConfig.authToken = "test_token"
        
        // When
        apiService.deleteAccount(confirmationCode: confirmationCode) { [weak self] result in
            // Then
            switch result {
            case .success(let response):
                XCTAssertTrue(response.success, "Delete account should succeed")
                XCTAssertNil(AppConfig.authToken, "Token should be cleared")
                print("✅ Test 9.1: DeleteAccount (SUCCESS) - SUCCESS")
                print("   Confirmation code: \(confirmationCode)")
                print("   Token cleared: \(AppConfig.authToken == nil)")
            case .failure(let error):
                XCTFail("DeleteAccount should succeed with correct code, but got error: \(error)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    func testDeleteAccountFailure() {
        // Given
        let confirmationCode = "WRONG"
        
        // When
        apiService.deleteAccount(confirmationCode: confirmationCode) { [weak self] result in
            // Then
            switch result {
            case .success:
                XCTFail("DeleteAccount should fail with wrong code")
            case .failure(let error):
                XCTAssertNotNil(error, "Error should not be nil")
                print("✅ Test 9.2: DeleteAccount (FAILURE) - SUCCESS")
                print("   Confirmation code: \(confirmationCode)")
                print("   Error: \(error.localizedDescription)")
            }
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
    
    // MARK: - Test 10: Симуляция задержки сети
    
    func testNetworkDelay() {
        // Given
        let startTime = Date()
        
        // When
        apiService.getUserProfile { [weak self] result in
            // Then
            let endTime = Date()
            let delay = endTime.timeIntervalSince(startTime)
            
            XCTAssertGreaterThanOrEqual(delay, 0.5, "Delay should be at least 0.5 seconds")
            XCTAssertLessThanOrEqual(delay, 2.0, "Delay should be at most 2.0 seconds (with buffer)")
            print("✅ Test 10: NetworkDelay - SUCCESS")
            print("   Delay: \(String(format: "%.2f", delay)) seconds")
            
            self?.expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 3.0)
    }
}

