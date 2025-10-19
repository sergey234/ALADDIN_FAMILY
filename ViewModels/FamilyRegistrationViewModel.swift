import SwiftUI
import Combine

/**
 * 🏠 Family Registration ViewModel
 * Управление процессом прогрессивной регистрации
 * 
 * Отвечает за:
 * - Создание новой семьи
 * - Присоединение к существующей семье
 * - Восстановление доступа
 * - Интеграция с family_registration.py backend
 */

class FamilyRegistrationViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var currentStep: RegistrationStep = .idle
    @Published var showConsentModal: Bool = false
    @Published var showRoleModal: Bool = false
    @Published var showAgeGroupModal: Bool = false
    @Published var showLetterModal: Bool = false
    @Published var showFamilyCreatedModal: Bool = false
    @Published var showSuccessModal: Bool = false
    @Published var consentAccepted: Bool = false
    
    @Published var selectedRole: FamilyRole?
    @Published var selectedAgeGroup: AgeGroup?
    @Published var selectedLetter: String?
    
    @Published var familyID: String?
    @Published var recoveryCode: String?
    @Published var familyMembers: [FamilyMember] = []
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Registration Steps
    
    enum RegistrationStep {
        case idle
        case showingConsent
        case selectingRole
        case selectingAgeGroup
        case selectingLetter
        case creatingFamily
        case showingRecoveryCode
        case completed
    }
    
    // MARK: - Public Methods
    
    /**
     * Начать регистрацию (показать Consent)
     */
    func startRegistration() {
        // Проверяем, было ли согласие дано ранее
        if UserDefaults.standard.bool(forKey: "consent_accepted") {
            // Согласие уже дано - пропускаем
            consentAccepted = true
            showRoleSelection()
        } else {
            // Показываем Consent Modal
            currentStep = .showingConsent
            showConsentModal = true
        }
    }
    
    /**
     * Согласие принято
     */
    func acceptConsent() {
        consentAccepted = true
        UserDefaults.standard.set(true, forKey: "consent_accepted")
        UserDefaults.standard.set(Date(), forKey: "consent_date")
        UserDefaults.standard.set("2.0", forKey: "consent_version")
        showConsentModal = false
        
        // Переходим к выбору роли
        showRoleSelection()
    }
    
    /**
     * Показать выбор роли
     */
    func showRoleSelection() {
        currentStep = .selectingRole
        showRoleModal = true
    }
    
    func onRoleSelected(_ role: FamilyRole) {
        selectedRole = role
        showRoleModal = false
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.currentStep = .selectingAgeGroup
            self.showAgeGroupModal = true
        }
    }
    
    func onAgeGroupSelected(_ ageGroup: AgeGroup) {
        selectedAgeGroup = ageGroup
        showAgeGroupModal = false
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.currentStep = .selectingLetter
            self.showLetterModal = true
        }
    }
    
    func onLetterSelected(_ letter: String) {
        selectedLetter = letter
        showLetterModal = false
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.createFamily()
        }
    }
    
    // MARK: - Create Family
    
    func createFamily() {
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            return
        }
        
        currentStep = .creatingFamily
        isLoading = true
        
        // API request
        let request = CreateFamilyRequest(
            role: role.rawValue,
            age_group: ageGroup.rawValue,
            personal_letter: letter,
            device_type: getDeviceType()
        )
        
        NetworkManager.shared.createFamily(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    self?.recoveryCode = response.recovery_code
                    
                    // Format recovery code for display
                    self?.recoveryCode = self?.formatRecoveryCode(response.family_id) ?? response.recovery_code
                    
                    self?.currentStep = .showingRecoveryCode
                    
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                        self?.showFamilyCreatedModal = true
                    }
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    print("❌ Error creating family: \(error)")
                }
            }
        }
    }
    
    // MARK: - Join Family
    
    func joinFamily(withCode code: String) {
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            return
        }
        
        isLoading = true
        
        let request = JoinFamilyRequest(
            family_id: extractFamilyID(from: code),
            role: role.rawValue,
            age_group: ageGroup.rawValue,
            personal_letter: letter,
            device_type: getDeviceType()
        )
        
        NetworkManager.shared.joinFamily(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    self?.familyMembers = response.members.map { member in
                        FamilyMember(
                            id: member.member_id,
                            letter: member.personal_letter,
                            role: FamilyRole(rawValue: member.role) ?? .other,
                            ageGroup: AgeGroup(rawValue: member.age_group) ?? .adult_24_55,
                            isYou: member.member_id == response.your_member_id
                        )
                    }
                    
                    self?.currentStep = .completed
                    self?.showSuccessModal = true
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    print("❌ Error joining family: \(error)")
                }
            }
        }
    }
    
    // MARK: - Recover Access
    
    func recoverAccess(withCode code: String) {
        isLoading = true
        
        NetworkManager.shared.recoverFamily(familyID: extractFamilyID(from: code)) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    self?.familyMembers = response.members.map { member in
                        FamilyMember(
                            id: member.member_id,
                            letter: member.personal_letter,
                            role: FamilyRole(rawValue: member.role) ?? .other,
                            ageGroup: AgeGroup(rawValue: member.age_group) ?? .adult_24_55,
                            isYou: false
                        )
                    }
                    
                    self?.currentStep = .completed
                    self?.showSuccessModal = true
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    print("❌ Error recovering family: \(error)")
                }
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func formatRecoveryCode(_ familyID: String) -> String {
        // Convert FAM_A1B2C3D4E5F6 → FAM-A1B2-C3D4-E5F6
        let cleaned = familyID.replacingOccurrences(of: "FAM_", with: "")
        let parts = cleaned.enumerated().reduce(into: [String]()) { result, element in
            let index = element.offset
            let char = element.element
            
            if index % 4 == 0 {
                result.append(String(char))
            } else {
                result[result.count - 1].append(char)
            }
        }
        
        return "FAM-" + parts.joined(separator: "-")
    }
    
    private func extractFamilyID(from code: String) -> String {
        // Convert FAM-A1B2-C3D4-E5F6 → FAM_A1B2C3D4E5F6
        let cleaned = code.replacingOccurrences(of: "-", with: "")
        return cleaned.replacingOccurrences(of: "FAM", with: "FAM_")
    }
    
    private func getDeviceType() -> String {
        #if os(iOS)
        if UIDevice.current.userInterfaceIdiom == .pad {
            return "tablet"
        } else {
            return "smartphone"
        }
        #else
        return "smartphone"
        #endif
    }
}

// MARK: - API Models

struct CreateFamilyRequest: Codable {
    let role: String
    let age_group: String
    let personal_letter: String
    let device_type: String
}

struct CreateFamilyResponse: Codable {
    let family_id: String
    let recovery_code: String
    let qr_code_data: String
    let short_code: String
}

struct JoinFamilyRequest: Codable {
    let family_id: String
    let role: String
    let age_group: String
    let personal_letter: String
    let device_type: String
}

struct JoinFamilyResponse: Codable {
    let family_id: String
    let your_member_id: String
    let members: [FamilyMemberResponse]
}

struct FamilyMemberResponse: Codable {
    let member_id: String
    let role: String
    let age_group: String
    let personal_letter: String
}

struct RecoverFamilyResponse: Codable {
    let family_id: String
    let members: [FamilyMemberResponse]
}

// MARK: - Network Manager Extension

extension NetworkManager {
    
    func createFamily(request: CreateFamilyRequest, completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void) {
        guard let url = URL(string: "\(AppConfig.baseURL)/family/create") else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1)))
            return
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try? JSONEncoder().encode(request)
        
        URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(CreateFamilyResponse.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func joinFamily(request: JoinFamilyRequest, completion: @escaping (Result<JoinFamilyResponse, Error>) -> Void) {
        guard let url = URL(string: "\(AppConfig.baseURL)/family/join") else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1)))
            return
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try? JSONEncoder().encode(request)
        
        URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(JoinFamilyResponse.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func recoverFamily(familyID: String, completion: @escaping (Result<RecoverFamilyResponse, Error>) -> Void) {
        guard let url = URL(string: "\(AppConfig.baseURL)/family/recover/\(familyID)") else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1)))
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(RecoverFamilyResponse.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

