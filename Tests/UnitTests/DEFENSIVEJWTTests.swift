//
//  DEFENSIVEJWTTests.swift
//  ALADDIN
//

import XCTest
@testable import ALADDIN

@MainActor
final class DEFENSIVEJWTTests: XCTestCase {

    override func setUp() {
        super.setUp()
        clearAllTestData()
    }

    override func tearDown() {
        clearAllTestData()
        super.tearDown()
    }

    private func clearAllTestData() {
        KeychainManager.shared.delete(forKey: .authToken)
        KeychainManager.shared.delete(forKey: .refreshToken)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
        SubscriptionManager.shared.setCurrentTokenForTesting(nil)
    }

    func testTokenValidatorScenarios() {
        clearAllTestData()
        XCTAssertEqual(TokenValidator.validateCurrentToken(), .none)

        setInvalidToken()
        XCTAssertEqual(TokenValidator.validateCurrentToken(), .invalid)

        setExpiredToken()
        XCTAssertEqual(TokenValidator.validateCurrentToken(), .expired)

        setExpiringSoonToken()
        XCTAssertEqual(TokenValidator.validateCurrentToken(), .needsRefresh)

        setValidToken()
        XCTAssertEqual(TokenValidator.validateCurrentToken(), .valid)
    }

    func testClearTokenMethod() async {
        let testToken = createTestToken()
        SubscriptionManager.shared.setCurrentTokenForTesting(testToken)
        KeychainManager.shared.save(testToken.token, forKey: .authToken)
        UserDefaults.standard.set(testToken.token, forKey: AppConfig.UserDefaultsKeys.authToken)

        XCTAssertNotNil(SubscriptionManager.shared.currentToken)

        await SubscriptionManager.shared.clearToken()

        XCTAssertNil(SubscriptionManager.shared.currentToken)
        XCTAssertNil(KeychainManager.shared.loadString(forKey: .authToken))
        XCTAssertNil(UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken))
    }

    func testDEFENSIVEJWTIntegration() async {
        _ = TokenValidator.validateCurrentToken()
        await SubscriptionManager.shared.clearToken()
    }

    private func createTestToken(expiryOffset: TimeInterval = 3600, tokenString: String? = nil) -> JWTToken {
        let deviceId = "test-device-\(UUID().uuidString)"
        let token = tokenString ?? "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.signature"
        let expiresAt = Date().addingTimeInterval(expiryOffset)
        let issuedAt = Date().addingTimeInterval(-120)
        let limits = SubscriptionLimits(
            maxDevices: 2,
            maxAIMessages: 10,
            maxScans: 10,
            maxReports: 10,
            currentUsage: UsageCounters()
        )
        return JWTToken(
            token: token,
            deviceId: deviceId,
            subscriptionLevel: .trial,
            trialInfo: nil,
            expiresAt: expiresAt,
            issuedAt: issuedAt,
            issuer: "unit-test",
            limits: limits,
            components: []
        )
    }

    private func setInvalidToken() {
        SubscriptionManager.shared.setCurrentTokenForTesting(
            createTestToken(tokenString: "invalid.jwt.token")
        )
    }

    private func setExpiredToken() {
        SubscriptionManager.shared.setCurrentTokenForTesting(createTestToken(expiryOffset: -3600))
    }

    private func setExpiringSoonToken() {
        SubscriptionManager.shared.setCurrentTokenForTesting(createTestToken(expiryOffset: 120))
    }

    private func setValidToken() {
        SubscriptionManager.shared.setCurrentTokenForTesting(createTestToken(expiryOffset: 7200))
    }
}
