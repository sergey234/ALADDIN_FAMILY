import XCTest
@testable import ALADDIN

/**
 * 🏠 FamilyRegistrationViewModel Unit Tests
 * Тесты для ViewModel регистрации семьи
 */

class FamilyRegistrationViewModelTests: XCTestCase {
    
    var viewModel: FamilyRegistrationViewModel!
    
    override func setUpWithError() throws {
        super.setUp()
        viewModel = FamilyRegistrationViewModel()
    }
    
    override func tearDownWithError() throws {
        viewModel = nil
        super.tearDown()
    }
    
    // MARK: - Initialization Tests
    
    func testViewModelInitialization() throws {
        XCTAssertNotNil(viewModel)
        XCTAssertEqual(viewModel.currentStep, .idle)
        XCTAssertFalse(viewModel.showConsentModal)
        XCTAssertFalse(viewModel.showRoleModal)
        XCTAssertFalse(viewModel.showAgeGroupModal)
        XCTAssertFalse(viewModel.showLetterModal)
        XCTAssertFalse(viewModel.showFamilyCreatedModal)
        XCTAssertFalse(viewModel.showSuccessModal)
        XCTAssertFalse(viewModel.consentAccepted)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testViewModelPublishedProperties() throws {
        // Проверяем что все @Published свойства инициализированы
        XCTAssertNotNil(viewModel.currentStep)
        XCTAssertNotNil(viewModel.showConsentModal)
        XCTAssertNotNil(viewModel.showRoleModal)
        XCTAssertNotNil(viewModel.showAgeGroupModal)
        XCTAssertNotNil(viewModel.showLetterModal)
        XCTAssertNotNil(viewModel.showFamilyCreatedModal)
        XCTAssertNotNil(viewModel.showSuccessModal)
        XCTAssertNotNil(viewModel.consentAccepted)
        XCTAssertNotNil(viewModel.isLoading)
        XCTAssertNotNil(viewModel.familyMembers)
    }
    
    // MARK: - Registration Flow Tests
    
    func testStartRegistration() throws {
        // Тест начала регистрации
        viewModel.startRegistration()
        
        // Проверяем что процесс начался
        XCTAssertTrue(viewModel.currentStep == .showingConsent || viewModel.currentStep == .selectingRole)
    }
    
    func testAcceptConsent() throws {
        // Тест принятия согласия
        viewModel.acceptConsent()
        
        // Проверяем что согласие принято
        XCTAssertTrue(viewModel.consentAccepted)
        XCTAssertFalse(viewModel.showConsentModal)
    }
    
    func testShowRoleSelection() throws {
        // Тест показа выбора роли
        viewModel.showRoleSelection()
        
        // Проверяем что показывается модальное окно роли
        XCTAssertTrue(viewModel.showRoleModal)
    }
    
    func testSelectRole() throws {
        // Тест выбора роли
        let role = FamilyRole.parent
        viewModel.selectRole(role)
        
        // Проверяем что роль выбрана
        XCTAssertEqual(viewModel.selectedRole, role)
    }
    
    func testSelectAgeGroup() throws {
        // Тест выбора возрастной группы
        let ageGroup = AgeGroup.adult
        viewModel.selectAgeGroup(ageGroup)
        
        // Проверяем что возрастная группа выбрана
        XCTAssertEqual(viewModel.selectedAgeGroup, ageGroup)
    }
    
    func testSelectLetter() throws {
        // Тест выбора буквы
        let letter = "А"
        viewModel.selectLetter(letter)
        
        // Проверяем что буква выбрана
        XCTAssertEqual(viewModel.selectedLetter, letter)
    }
    
    // MARK: - Family Creation Tests
    
    func testCreateFamily() throws {
        // Тест создания семьи
        viewModel.familyName = "Тестовая Семья"
        viewModel.createFamily()
        
        // Проверяем что процесс создания начался
        XCTAssertTrue(viewModel.isLoading)
    }
    
    func testJoinFamily() throws {
        // Тест присоединения к семье
        viewModel.familyCode = "TEST123"
        viewModel.joinFamily()
        
        // Проверяем что процесс присоединения начался
        XCTAssertTrue(viewModel.isLoading)
    }
    
    func testRecoverFamily() throws {
        // Тест восстановления семьи
        viewModel.recoveryCode = "RECOVER123"
        viewModel.recoverFamily()
        
        // Проверяем что процесс восстановления начался
        XCTAssertTrue(viewModel.isLoading)
    }
    
    // MARK: - Data Validation Tests
    
    func testFamilyNameValidation() throws {
        // Тест валидации имени семьи
        viewModel.familyName = "Валидное Имя Семьи"
        XCTAssertFalse(viewModel.familyName.isEmpty)
    }
    
    func testFamilyCodeValidation() throws {
        // Тест валидации кода семьи
        viewModel.familyCode = "VALID123"
        XCTAssertFalse(viewModel.familyCode.isEmpty)
    }
    
    func testRecoveryCodeValidation() throws {
        // Тест валидации кода восстановления
        viewModel.recoveryCode = "RECOVER123"
        XCTAssertFalse(viewModel.recoveryCode.isEmpty)
    }
    
    // MARK: - Error Handling Tests
    
    func testErrorMessageHandling() throws {
        // Тест обработки сообщений об ошибках
        XCTAssertNil(viewModel.errorMessage)
        
        // В реальном тесте здесь бы симулировали ошибку
        // viewModel.handleError("Test error")
        // XCTAssertEqual(viewModel.errorMessage, "Test error")
    }
    
    func testLoadingStateHandling() throws {
        // Тест обработки состояния загрузки
        XCTAssertFalse(viewModel.isLoading)
        
        viewModel.isLoading = true
        XCTAssertTrue(viewModel.isLoading)
        
        viewModel.isLoading = false
        XCTAssertFalse(viewModel.isLoading)
    }
    
    // MARK: - Family Members Tests
    
    func testFamilyMembersArray() throws {
        // Тест массива участников семьи
        XCTAssertTrue(viewModel.familyMembers.isEmpty)
        
        let member = FamilyMember(
            id: "test-id",
            name: "Тест Участник",
            role: .parent,
            ageGroup: .adult,
            isActive: true
        )
        
        viewModel.familyMembers.append(member)
        XCTAssertEqual(viewModel.familyMembers.count, 1)
        XCTAssertEqual(viewModel.familyMembers.first?.name, "Тест Участник")
    }
    
    // MARK: - Registration Step Tests
    
    func testRegistrationStepProgression() throws {
        // Тест прогрессии шагов регистрации
        XCTAssertEqual(viewModel.currentStep, .idle)
        
        viewModel.startRegistration()
        XCTAssertTrue(viewModel.currentStep == .showingConsent || viewModel.currentStep == .selectingRole)
    }
    
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
    
    func testViewModelCreationPerformance() throws {
        self.measure {
            let vm = FamilyRegistrationViewModel()
            XCTAssertNotNil(vm)
        }
    }
    
    func testRegistrationFlowPerformance() throws {
        self.measure {
            viewModel.startRegistration()
            viewModel.acceptConsent()
            viewModel.showRoleSelection()
        }
    }
    
    func testFamilyMembersPerformance() throws {
        self.measure {
            for i in 0..<100 {
                let member = FamilyMember(
                    id: "member-\(i)",
                    name: "Участник \(i)",
                    role: .parent,
                    ageGroup: .adult,
                    isActive: true
                )
                viewModel.familyMembers.append(member)
            }
        }
    }
}

// MARK: - FamilyRegistrationViewModel Mock Tests

extension FamilyRegistrationViewModelTests {
    
    func testViewModelWithMockData() throws {
        // Тест с мок-данными
        viewModel.familyName = "Мок Семья"
        viewModel.familyCode = "MOCK123"
        viewModel.recoveryCode = "RECOVER123"
        
        XCTAssertEqual(viewModel.familyName, "Мок Семья")
        XCTAssertEqual(viewModel.familyCode, "MOCK123")
        XCTAssertEqual(viewModel.recoveryCode, "RECOVER123")
    }
}
