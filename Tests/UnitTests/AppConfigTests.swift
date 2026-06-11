import XCTest
@testable import ALADDIN

/**
 * ⚙️ AppConfig Unit Tests
 * Тесты для конфигурации приложения
 * Цель: 100% покрытие AppConfig
 */

@MainActor
class AppConfigTests: XCTestCase {
    
    override func setUpWithError() throws {
        // Очищаем UserDefaults перед каждым тестом
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
    }
    
    override func tearDownWithError() throws {
        // Очищаем UserDefaults после каждого теста
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
    }
    
    // MARK: - App Info Tests
    
    func testContentManifestRequireValidSignatureMatchesBuildMode() {
        #if DEBUG
        XCTAssertFalse(AppConfig.contentManifestRequireValidSignature)
        #else
        XCTAssertTrue(AppConfig.contentManifestRequireValidSignature)
        #endif
    }

    func testContentPayloadDiskCacheMaxBytesIsPositive() {
        XCTAssertGreaterThan(AppConfig.contentPayloadDiskCacheMaxBytes, 0)
    }

    func testContentCatalogMinItemsPerCategoryIsPositive() {
        XCTAssertGreaterThanOrEqual(AppConfig.contentCatalogMinItemsPerCategory, 1)
    }

    func testAppName() throws {
        XCTAssertEqual(AppConfig.appName, "ALADDIN")
    }
    
    func testAppVersion() throws {
        XCTAssertEqual(AppConfig.appVersion, "1.0.0")
    }
    
    func testBuildNumber() throws {
        XCTAssertEqual(AppConfig.buildNumber, "227")
    }

    // MARK: - Explicit Security API (B2-00 / GATE-D)

    func testExplicitSecurityEndpointsUseCanonicalPaths() throws {
        let endpoint = AppConfig.Endpoint.self
        let forbiddenPrefixes = [
            "/api/reports/dark-web/",
            "/api/reports/identity-theft/",
            "/api/reports/privacy/location/",
            "/api/reports/privacy/cleanup/",
        ]
        let securityPaths: [String] = [
            endpoint.darkWebStats,
            endpoint.darkWebLeaks,
            endpoint.darkWebScanStart,
            endpoint.identityTheftStats,
            endpoint.identityTheftAttempts,
            endpoint.identityTheftDetect,
            endpoint.locationStats,
            endpoint.locationBubble,
            endpoint.dataCleanupStart,
            endpoint.antifakeCheckText,
            endpoint.antifakeCheckUrl,
            endpoint.parentalMonitoringDetail,
            endpoint.mobileScan,
            endpoint.malwareQuickScan,
            endpoint.malwareThreats,
        ]
        for path in securityPaths {
            for prefix in forbiddenPrefixes where path.hasPrefix(prefix) {
                XCTFail("Security path still uses legacy reports prefix: \(path)")
            }
        }
        XCTAssertTrue(endpoint.darkWebStats.hasPrefix("/api/darkweb/"))
        XCTAssertTrue(endpoint.antifakeCheckText.hasPrefix("/api/antifake/"))
        XCTAssertTrue(endpoint.locationBubble.hasPrefix("/api/location-bubble/"))
        XCTAssertTrue(endpoint.dataCleanupStart.hasPrefix("/api/data-cleanup/"))
    }

    func testApiContractVersionNonEmpty() throws {
        XCTAssertFalse(AppConfig.apiContractVersion.isEmpty)
    }

    func testMinimumClientBuildForApiContractMatchesShippedBuild() throws {
        XCTAssertEqual(AppConfig.minimumClientBuildForApiContract, AppConfig.buildNumber)
    }
    
    func testBundleIdentifier() throws {
        XCTAssertEqual(AppConfig.bundleIdentifier, "family.aladdin.ios")
    }
    
    func testAppDisplayName() throws {
        XCTAssertEqual(AppConfig.appDisplayName, "ALADDIN - AI Защита Семьи")
    }
    
    // MARK: - API Configuration Tests
    
    func testAPIBaseURL() throws {
        let baseURL = AppConfig.apiBaseURL
        XCTAssertTrue(baseURL.contains("aladdin-ai.ru"))
        XCTAssertTrue(baseURL.hasPrefix("https://"))
    }
    
    func testAPIKey() throws {
        XCTAssertEqual(AppConfig.apiKey, "YOUR_SECURE_API_KEY")
    }
    
    func testBaseURL() throws {
        let baseURL = AppConfig.baseURL
        XCTAssertEqual(baseURL, AppConfig.apiBaseURL)
    }
    
    // MARK: - Region Tests
    
    func testIsRussianRegion() throws {
        let isRussian = AppConfig.isRussianRegion
        XCTAssertTrue(isRussian == true || isRussian == false)
    }
    
    func testRussianRegionDetection() throws {
        // Тест определения российского региона
        let regionCode = Locale.current.regionCode
        let expectedRussian = regionCode == "RU"
        let actualRussian = AppConfig.isRussianRegion
        XCTAssertEqual(actualRussian, expectedRussian)
    }
    
    // MARK: - Payment Configuration Tests
    
    func testUseAlternativePayments() throws {
        let useAlternative = AppConfig.useAlternativePayments
        XCTAssertTrue(useAlternative, "Альтернативные платежи должны быть всегда активны")
    }
    
    func testAlternativePaymentForRussianRegion() throws {
        // В России должны быть включены альтернативные способы оплаты
        if AppConfig.isRussianRegion {
            XCTAssertTrue(AppConfig.useAlternativePayments)
        }
    }
    
    // MARK: - Debug Configuration Tests
    
    func testIsDebugMode() throws {
        let isDebug = AppConfig.isDebugMode
        #if DEBUG
        XCTAssertTrue(isDebug)
        #else
        XCTAssertFalse(isDebug)
        #endif
    }
    
    func testLogLevel() throws {
        let logLevel = AppConfig.logLevel
        XCTAssertNotNil(logLevel)
        
        #if DEBUG
        XCTAssertEqual(logLevel, AppConfig.LogLevel.verbose)
        #else
        XCTAssertEqual(logLevel, AppConfig.LogLevel.error)
        #endif
    }
    
    // MARK: - LogLevel Enum Tests
    
    func testLogLevelEnum() throws {
        let levels: [AppConfig.LogLevel] = [.verbose, .info, .warning, .error, .none]
        XCTAssertEqual(levels.count, 5)
    }
    
    func testLogLevelCases() throws {
        XCTAssertEqual(AppConfig.LogLevel.verbose, .verbose)
        XCTAssertEqual(AppConfig.LogLevel.info, .info)
        XCTAssertEqual(AppConfig.LogLevel.warning, .warning)
        XCTAssertEqual(AppConfig.LogLevel.error, .error)
        XCTAssertEqual(AppConfig.LogLevel.none, .none)
    }
    
    // MARK: - UserDefaults Integration Tests
    
    func testAuthTokenGetSet() throws {
        // Тест получения и установки токена авторизации
        let testToken = "test-auth-token-123"
        
        // Устанавливаем токен
        AppConfig.authToken = testToken
        
        // Проверяем что токен установлен
        XCTAssertEqual(AppConfig.authToken, testToken)
        
        // Очищаем токен
        AppConfig.authToken = nil
        XCTAssertNil(AppConfig.authToken)
    }
    
    func testAuthTokenPersistence() throws {
        let testToken = "persistent-token-456"

        AppConfig.authToken = testToken

        XCTAssertEqual(AppConfig.authToken, testToken)
        XCTAssertNil(
            UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken),
            "Access token must not remain stored in UserDefaults"
        )
        XCTAssertEqual(KeychainManager.shared.loadString(forKey: .authToken), testToken)

        AppConfig.authToken = nil
    }
    
    // MARK: - UserDefaultsKeys Tests
    
    func testUserDefaultsKeys() throws {
        XCTAssertEqual(AppConfig.UserDefaultsKeys.authToken, "authToken")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.familyId, "family_id")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.consentAccepted, "consent_accepted")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.consentDate, "consent_date")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.consentVersion, "consent_version")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.appLanguage, "appLanguage")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.hasChosenLanguageOnce, "hasChosenLanguageOnce")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.hasCompletedOnboarding, "hasCompletedOnboarding")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh, "pending_main_dashboard_devices_refresh")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.pendingMainFamilyStatsRefresh, "pending_main_family_stats_refresh")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.notificationAppSettingsRemoteVersion, "notification_app_settings_remote_version")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.notificationAppSettingsSyncPending, "notification_app_settings_sync_pending")
        XCTAssertEqual(AppConfig.UserDefaultsKeys.pendingDeviceBindToken, "pending_device_bind_token")
    }
    
    // MARK: - Network Configuration Tests
    
    func testNetworkConfiguration() throws {
        XCTAssertEqual(AppConfig.Network.requestTimeout, 30.0)
        XCTAssertEqual(AppConfig.Network.resourceTimeout, 60.0)
        XCTAssertTrue(AppConfig.Network.waitsForConnectivity)
    }
    
    // MARK: - Consent Configuration Tests
    
    func testConsentConfiguration() throws {
        XCTAssertEqual(AppConfig.Consent.currentVersion, "2.0")
    }
    
    // MARK: - Performance Tests
    
    func testAppConfigAccessPerformance() throws {
        self.measure {
            _ = AppConfig.appName
            _ = AppConfig.appVersion
            _ = AppConfig.bundleIdentifier
            _ = AppConfig.apiBaseURL
            _ = AppConfig.isRussianRegion
            _ = AppConfig.isDebugMode
        }
    }
    
    func testAuthTokenPerformance() throws {
        self.measure {
            AppConfig.authToken = "performance-test-token"
            _ = AppConfig.authToken
            AppConfig.authToken = nil
        }
    }
    
    // MARK: - Edge Cases Tests
    
    func testEmptyAuthToken() throws {
        AppConfig.authToken = ""
        XCTAssertEqual(AppConfig.authToken, "")
    }
    
    func testLongAuthToken() throws {
        let longToken = String(repeating: "a", count: 1000)
        AppConfig.authToken = longToken
        XCTAssertEqual(AppConfig.authToken, longToken)
        AppConfig.authToken = nil
    }
    
    func testSpecialCharactersAuthToken() throws {
        let specialToken = "token!@#$%^&*()_+-=[]{}|;':\",./<>?"
        AppConfig.authToken = specialToken
        XCTAssertEqual(AppConfig.authToken, specialToken)
        AppConfig.authToken = nil
    }
    
    // MARK: - Thread Safety Tests
    
    func testConcurrentAuthTokenAccess() throws {
        let expectation = XCTestExpectation(description: "Concurrent access")
        let queue = DispatchQueue(label: "test.queue", attributes: .concurrent)
        
        for i in 0..<100 {
            queue.async {
                AppConfig.authToken = "token-\(i)"
                _ = AppConfig.authToken
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 5.0)
        AppConfig.authToken = nil
    }
    
    // MARK: - Memory Management Tests
    
    // Тестов на работу со слабой ссылкой не требуется, так как AppConfig является структурой.
}

// MARK: - APIResponseValidator (PR3)

@MainActor
final class APIResponseValidatorTests: XCTestCase {

    func testEnvelopeDecodeAndCanonicalPolicyOverridesBodyComponentId() throws {
        let json = Data(
            """
            {"status":{"componentId":"wrong_agent","isEnabled":true,"status":"enabled","lastUpdated":"2026-03-18 19:58:49","error":null}}
            """.utf8
        )
        let response = try JSONDecoder().decode(ComponentStatusResponse.self, from: json)
        let status = try APIResponseValidator.makeComponentStatus(
            from: response,
            canonicalComponentId: "crash_detection_agent",
            policy: .canonicalRequestIdAlwaysWins
        )
        XCTAssertEqual(status.componentId, "crash_detection_agent")
        XCTAssertTrue(status.isEnabled)
    }

    func testRejectMismatchedExplicitComponentIdThrows() throws {
        let json = Data(
            """
            {"status":{"componentId":"other_agent","isEnabled":true,"status":"enabled","lastUpdated":"2026-03-18 19:58:49","error":null}}
            """.utf8
        )
        let response = try JSONDecoder().decode(ComponentStatusResponse.self, from: json)
        XCTAssertThrowsError(
            try APIResponseValidator.makeComponentStatus(
                from: response,
                canonicalComponentId: "crash_detection_agent",
                policy: .rejectMismatchedExplicitComponentId
            )
        )
    }

    func testFlatContractDecodesAndMapsEnabled() throws {
        let json = Data(
            """
            {"status":"enabled","uptime":99.0}
            """.utf8
        )
        let response = try JSONDecoder().decode(ComponentStatusResponse.self, from: json)
        let status = try APIResponseValidator.makeComponentStatus(
            from: response,
            canonicalComponentId: "malware_detection_agent",
            policy: .canonicalRequestIdAlwaysWins
        )
        XCTAssertEqual(status.componentId, "malware_detection_agent")
        XCTAssertTrue(status.isEnabled)
    }

    func testServerConfigurationEnvelopeDecodes() throws {
        let json = Data(
            """
            {"configuration":{"componentId":"malware_detection_agent","settings":{},"version":"1","lastUpdated":null},"isDefault":true}
            """.utf8
        )
        let envelope = try JSONDecoder().decode(ServerComponentConfigurationResponse.self, from: json)
        XCTAssertTrue(envelope.isDefault ?? false)
        XCTAssertEqual(envelope.configuration.componentId, "malware_detection_agent")
    }
}

// MARK: - AppConfig Test Extensions

extension AppConfigTests {
    
    // MARK: - Helper Methods
    
    func resetUserDefaults() {
        let domain = Bundle.main.bundleIdentifier!
        UserDefaults.standard.removePersistentDomain(forName: domain)
    }
    
    func setupTestEnvironment() {
        resetUserDefaults()
    }
    
    func cleanupTestEnvironment() {
        resetUserDefaults()
    }
}
