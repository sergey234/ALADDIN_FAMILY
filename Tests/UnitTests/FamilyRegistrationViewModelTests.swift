import XCTest
@testable import ALADDIN

@MainActor
final class FamilyRegistrationViewModelTests: XCTestCase {
    
    private var viewModel: FamilyRegistrationViewModel!
    private let defaults = UserDefaults.standard
    
    override func setUpWithError() throws {
        viewModel = FamilyRegistrationViewModel()
        resetUserDefaults()
    }
    
    override func tearDownWithError() throws {
        resetUserDefaults()
        viewModel = nil
    }
    
    func testStartRegistrationShowsConsentModal() {
        XCTAssertFalse(viewModel.showConsentModal)
        viewModel.startRegistration()
        XCTAssertTrue(viewModel.showConsentModal)
    }
    
    func testAcceptConsentStoresUserDefaultsAndShowsRoleSelection() {
        viewModel.startRegistration()
        viewModel.acceptConsent()
        
        XCTAssertTrue(viewModel.consentAccepted)
        XCTAssertFalse(viewModel.showConsentModal)
        XCTAssertTrue(viewModel.showRoleModal)
        XCTAssertEqual(viewModel.currentStep, .selectingRole)
        XCTAssertTrue(defaults.bool(forKey: AppConfig.UserDefaultsKeys.consentAccepted))
    }
    
    func testRoleSelectionTriggersAgeGroupSelection() {
        let expectation = expectation(description: "Age group modal should appear")
        viewModel.showRoleSelection()
        viewModel.onRoleSelected(.parent)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            if self.viewModel.showAgeGroupModal && self.viewModel.currentStep == .selectingAgeGroup {
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 1.0)
        XCTAssertEqual(viewModel.selectedRole, .parent)
    }
    
    func testAgeGroupSelectionTriggersLetterSelection() {
        viewModel.showRoleSelection()
        viewModel.onRoleSelected(.child)
        let expectation = expectation(description: "Letter modal should appear")
        viewModel.onAgeGroupSelected(.teen)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            if self.viewModel.showLetterModal && self.viewModel.currentStep == .selectingLetter {
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 1.0)
        XCTAssertEqual(viewModel.selectedAgeGroup, .teen)
    }
    
    func testLetterSelectionTriggersFamilyCreation() {
        viewModel.showRoleSelection()
        viewModel.onRoleSelected(.parent)
        viewModel.onAgeGroupSelected(.adult)
        let expectation = expectation(description: "Family creation should finish")
        viewModel.onLetterSelected("А")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            if self.viewModel.familyID != nil && self.viewModel.recoveryCode != nil {
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 1.5)
        XCTAssertEqual(viewModel.currentStep, .showingRecoveryCode)
        XCTAssertNotNil(viewModel.familyID)
        XCTAssertNotNil(viewModel.recoveryCode)
    }
    
    func testCreateFamilyRequiresSelections() {
        viewModel.createFamily()
        XCTAssertNil(viewModel.familyID)
        XCTAssertNil(viewModel.recoveryCode)
    }
    
    func testSaveAndClearUserRole() {
        viewModel.saveUserRole(.parent)
        XCTAssertEqual(viewModel.getCurrentUserRole(), .parent)
        XCTAssertTrue(viewModel.hasUserRole())
        
        viewModel.clearUserRole()
        XCTAssertNil(viewModel.getCurrentUserRole())
        XCTAssertFalse(viewModel.hasUserRole())
    }
    
    func testJoinFamilyWithoutSelectionsDoesNotStartLoading() {
        viewModel.joinFamily(withCode: "FAM-TEST-0000-0000")
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.familyID)
    }
    
    private func resetUserDefaults() {
        defaults.removeObject(forKey: "current_user_role")
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.consentAccepted)
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.consentDate)
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.consentVersion)
    }
}
