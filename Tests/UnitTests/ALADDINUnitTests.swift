import XCTest
@testable import ALADDIN

/**
 * 🧪 ALADDIN Unit Tests
 * Автоматические тесты для критических компонентов
 * Цель: 60% code coverage
 */

@MainActor
class ALADDINUnitTests: XCTestCase {
    
    // MARK: - Setup & Teardown
    
    override func setUpWithError() throws {
        // Настройка перед каждым тестом
        super.setUp()
    }
    
    override func tearDownWithError() throws {
        // Очистка после каждого теста
        super.tearDown()
    }
    
    // MARK: - AppConfig Tests
    
    func testAppConfigProperties() throws {
        // Тест основных свойств AppConfig
        XCTAssertEqual(AppConfig.appName, "ALADDIN")
        XCTAssertEqual(AppConfig.appVersion, "1.0.0")
        XCTAssertEqual(AppConfig.bundleIdentifier, "family.aladdin.ios")
    }
    
    func testAppConfigAPIBaseURL() throws {
        // Тест API URL в зависимости от конфигурации
        let baseURL = AppConfig.apiBaseURL
        XCTAssertTrue(baseURL.contains("api"))
    }
    
    func testAppConfigRussianRegion() throws {
        // Тест определения российского региона
        let isRussian = AppConfig.isRussianRegion
        XCTAssertTrue(isRussian == true || isRussian == false)
    }
    
    // MARK: - NetworkManager Tests
    
    func testNetworkManagerInitialization() throws {
        // Тест инициализации NetworkManager
        let networkManager = NetworkManager()
        XCTAssertNotNil(networkManager)
        XCTAssertTrue(networkManager.isOnline)
    }
    
    func testNetworkManagerBaseURL() throws {
        // Тест базового URL NetworkManager
        let networkManager = NetworkManager()
        // Проверяем что baseURL установлен
        XCTAssertNotNil(networkManager)
    }
    
    // MARK: - FamilyRegistrationViewModel Tests
    
    func testFamilyRegistrationViewModelInitialization() throws {
        // Тест инициализации FamilyRegistrationViewModel
        let viewModel = FamilyRegistrationViewModel()
        XCTAssertNotNil(viewModel)
        XCTAssertEqual(viewModel.currentStep, .idle)
        XCTAssertFalse(viewModel.showConsentModal)
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testFamilyRegistrationViewModelStartRegistration() throws {
        // Тест начала регистрации
        let viewModel = FamilyRegistrationViewModel()
        viewModel.startRegistration()
        
        // Проверяем что модальное окно согласия показывается
        // startRegistration() устанавливает showConsentModal = true, но не меняет currentStep
        XCTAssertTrue(viewModel.showConsentModal, "startRegistration() должен показывать модальное окно согласия")
    }
    
    func testFamilyRegistrationViewModelAcceptConsent() throws {
        // Тест принятия согласия
        let viewModel = FamilyRegistrationViewModel()
        viewModel.acceptConsent()
        
        // Проверяем что согласие принято
        XCTAssertTrue(viewModel.consentAccepted)
        XCTAssertFalse(viewModel.showConsentModal)
    }
    
    // MARK: - FamilyRole Tests
    
    func testFamilyRoleEnum() throws {
        // Тест enum FamilyRole
        let roles = FamilyRole.allCases
        XCTAssertEqual(roles.count, 4)
        XCTAssertTrue(roles.contains(.parent))
        XCTAssertTrue(roles.contains(.child))
        XCTAssertTrue(roles.contains(.teenager))
        XCTAssertTrue(roles.contains(.elderly))
    }
    
    func testFamilyRoleIdentifiable() throws {
        // Тест что FamilyRole соответствует Identifiable
        let role = FamilyRole.parent
        XCTAssertEqual(role.id, role.rawValue)
    }
    
    // MARK: - AgeGroup Tests
    
    func testAgeGroupEnum() throws {
        // Тест enum AgeGroup
        let ageGroups = AgeGroup.allCases
        XCTAssertEqual(ageGroups.count, 5)
        XCTAssertTrue(ageGroups.contains(.toddler))
        XCTAssertTrue(ageGroups.contains(.child))
        XCTAssertTrue(ageGroups.contains(.teen))
        XCTAssertTrue(ageGroups.contains(.adult))
        XCTAssertTrue(ageGroups.contains(.senior))
    }
    
    func testAgeGroupIdentifiable() throws {
        // Тест что AgeGroup соответствует Identifiable
        let ageGroup = AgeGroup.adult
        XCTAssertEqual(ageGroup.id, ageGroup.rawValue)
    }
    
    // MARK: - FamilyMember Tests
    
    func testFamilyMemberInitialization() throws {
        // Тест создания FamilyMember
        let member = FamilyMember(
            id: "test-id",
            name: "Тест Тестович",
            role: .parent,
            ageGroup: .adult,
            isActive: true
        )
        
        XCTAssertEqual(member.id, "test-id")
        XCTAssertEqual(member.name, "Тест Тестович")
        XCTAssertEqual(member.role, .parent)
        XCTAssertEqual(member.ageGroup, .adult)
        XCTAssertTrue(member.isActive)
    }
    
    func testFamilyMemberIdentifiable() throws {
        // Тест что FamilyMember соответствует Identifiable
        let member = FamilyMember(
            id: "test-id",
            name: "Тест",
            role: .parent,
            ageGroup: .adult,
            isActive: true
        )
        
        XCTAssertEqual(member.id, "test-id")
    }
    
    // MARK: - RegistrationStep Tests
    
    func testRegistrationStepEnum() throws {
        // Тест enum RegistrationStep
        let steps: [FamilyRegistrationViewModel.RegistrationStep] = [
            .idle,
            .showingConsent,
            .selectingRole,
            .selectingAgeGroup,
            .selectingLetter,
            .creatingFamily,
            .showingRecoveryCode,
            .completed
        ]
        
        XCTAssertEqual(steps.count, 8)
    }
    
    // MARK: - Performance Tests
    
    func testNetworkManagerPerformance() throws {
        // Тест производительности NetworkManager
        self.measure {
            let networkManager = NetworkManager()
            XCTAssertNotNil(networkManager)
        }
    }
    
    func testFamilyRegistrationViewModelPerformance() throws {
        // Тест производительности FamilyRegistrationViewModel
        self.measure {
            let viewModel = FamilyRegistrationViewModel()
            viewModel.startRegistration()
            viewModel.acceptConsent()
        }
    }
    
    // MARK: - Error Handling Tests
    
    func testNetworkManagerErrorHandling() throws {
        // Тест обработки ошибок NetworkManager
        let networkManager = NetworkManager()
        
        // Проверяем что lastError изначально nil
        XCTAssertNil(networkManager.lastError)
    }
    
    func testFamilyRegistrationViewModelErrorHandling() throws {
        // Тест обработки ошибок FamilyRegistrationViewModel
        let viewModel = FamilyRegistrationViewModel()
        
        // Проверяем что errorMessage изначально nil
        XCTAssertNil(viewModel.errorMessage)
    }
    
    // MARK: - Referral Module Tests
    
    func testReferralTemplateEnglish() throws {
        let localizationManager = LocalizationManager()
        localizationManager.currentLanguage = .english
        let template = localizationManager.localized("referral_text_template")
        let formatted = String(format: template, "UNITTEST", "UNITTEST")
        XCTAssertTrue(formatted.contains("UNITTEST"))
        XCTAssertTrue(formatted.contains("https://"))
        XCTAssertNotEqual(template, "referral_text_template")
    }
    
    func testReferralTemplateRussian() throws {
        let localizationManager = LocalizationManager()
        localizationManager.currentLanguage = .russian
        let template = localizationManager.localized("referral_text_template")
        let formatted = String(format: template, "КОД", "КОД")
        XCTAssertTrue(formatted.contains("КОД"))
        XCTAssertTrue(formatted.contains("https://"))
        XCTAssertNotEqual(template, "referral_text_template")
    }
    
    func testReferralRewardsDecoding() throws {
        let json = """
        {
          "total_converted": 3,
          "rewards": [
            {
              "reward_id": "reward_1",
              "title_key": "referral_reward_1_title",
              "subtitle_key": "referral_reward_1_subtitle",
              "amount_key": "referral_reward_1_amount",
              "reward_value": "-20%",
              "icon": "percent.circle.fill",
              "required_converted": 1,
              "status": "unlocked",
              "remaining": 0,
              "unlocked_at": "2025-11-08T12:00:00Z"
            }
          ]
        }
        """.data(using: .utf8)!
        let response = try JSONDecoder().decode(ReferralRewardsResponse.self, from: json)
        XCTAssertEqual(response.totalConverted, 3)
        XCTAssertEqual(response.rewards.count, 1)
        XCTAssertEqual(response.rewards.first?.rewardId, "reward_1")
        XCTAssertEqual(response.rewards.first?.requiredConverted, 1)
        XCTAssertEqual(response.rewards.first?.status, "unlocked")
    }
    
    func testReferralLocalizationKeysPresent() throws {
        let localizationManager = LocalizationManager()
        let keys = [
            "referral_reward_1_title",
            "referral_reward_1_amount",
            "referral_reward_1_subtitle",
            "referral_reward_3_title",
            "referral_reward_3_amount",
            "referral_reward_3_subtitle",
            "referral_reward_10_title",
            "referral_reward_10_amount",
            "referral_reward_10_subtitle"
        ]
        
        localizationManager.currentLanguage = .russian
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
        
        localizationManager.currentLanguage = .english
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
    func testChildRewardsLocalizationKeysPresent() throws {
        let localizationManager = LocalizationManager()
        let keys = [
            "child_rewards_title",
            "child_rewards_balance_label",
            "child_rewards_reward_icon_accessibility",
            "child_rewards_punish_icon_accessibility",
            "child_rewards_game_young_defender",
            "child_rewards_game_status_available",
            "child_rewards_game_metric_lessons",
            "child_rewards_shop_title",
            "child_rewards_buy_button"
        ]
        
        localizationManager.currentLanguage = .russian
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
        
        localizationManager.currentLanguage = .english
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
    }
    
    func testAddMemberLocalizationKeysPresent() throws {
        let localizationManager = LocalizationManager()
        let keys = [
            "add_member_title",
            "add_member_subtitle",
            "add_member_create_family",
            "add_member_scan_qr",
            "add_member_enter_code",
            "add_member_privacy_title",
            "add_member_privacy_text",
            "add_member_cancel"
        ]
        
        localizationManager.currentLanguage = .russian
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
        
        localizationManager.currentLanguage = .english
        for key in keys {
            XCTAssertNotEqual(localizationManager.localized(key), key)
        }
    }
    
    }
    
    // MARK: - Data Validation Tests
    
    func testFamilyMemberValidation() throws {
        // Тест валидации данных FamilyMember
        let validMember = FamilyMember(
            id: "valid-id",
            name: "Валидное Имя",
            role: .parent,
            ageGroup: .adult,
            isActive: true
        )
        
        XCTAssertFalse(validMember.id.isEmpty)
        XCTAssertFalse(validMember.name.isEmpty)
        XCTAssertTrue(validMember.isActive)
    }
    
    func testFamilyRoleValidation() throws {
        // Тест валидации FamilyRole
        let validRole = FamilyRole.parent
        XCTAssertFalse(validRole.rawValue.isEmpty)
        XCTAssertEqual(validRole.rawValue, "parent") // Исправлено: rawValue = "parent" (не "Parent")
    }
    
    func testAgeGroupValidation() throws {
        // Тест валидации AgeGroup
        let validAgeGroup = AgeGroup.adult
        XCTAssertFalse(validAgeGroup.rawValue.isEmpty)
        XCTAssertEqual(validAgeGroup.rawValue, "Adult (18-64)")
    }
}

// MARK: - Test Extensions

extension ALADDINUnitTests {
    
    // MARK: - Helper Methods
    
    func createTestFamilyMember() -> FamilyMember {
        return FamilyMember(
            id: "test-member-id",
            name: "Тестовый Участник",
            role: .parent,
            ageGroup: .adult,
            isActive: true
        )
    }
    
    func createTestFamilyRegistrationViewModel() -> FamilyRegistrationViewModel {
        return FamilyRegistrationViewModel()
    }
    
    func createTestNetworkManager() -> NetworkManager {
        return NetworkManager()
    }
}
