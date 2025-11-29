import SwiftUI
import Combine
import Security

// MARK: - Missing Types (Added by Assistant)
enum FamilyRole: String, Codable, CaseIterable, Identifiable {
    case parent = "parent"
    case child = "child"
    case teenager = "teenager"
    case elderly = "elderly"
    var id: String { rawValue }
}


extension FamilyRole {
    static var selectableRoles: [FamilyRole] { [.parent, .child, .teenager, .elderly] }
    
    var nameLocalizationKey: String {
        switch self {
        case .parent: return "family_role_parent_name"
        case .child: return "family_role_child_name"
        case .teenager: return "family_role_teenager_name"
        case .elderly: return "family_role_elderly_name"
        }
    }
    
    var descriptionLocalizationKey: String {
        switch self {
        case .parent: return "family_role_parent_description"
        case .child: return "family_role_child_description"
        case .teenager: return "family_role_teenager_description"
        case .elderly: return "family_role_elderly_description"
        }
    }
    
    var systemImageName: String {
        switch self {
        case .parent: return "person.2.fill"
        case .child: return "person.fill"
        case .teenager: return "person.3.fill"
        case .elderly: return "heart.circle.fill"
        }
    }
    
    init?(storageValue: String) {
        self.init(rawValue: storageValue.lowercased())
    }
}

enum AgeGroup: String, Codable, CaseIterable, Identifiable {
    case toddler = "Toddler (0-3)"
    case child = "Child (4-12)"
    case teen = "Teen (13-17)"
    case adult = "Adult (18-64)"
    case senior = "Senior (65+)"
    var id: String { self.rawValue }
}

struct FamilyMember: Codable, Identifiable {
    let id: String
    var name: String
    var role: FamilyRole
    var ageGroup: AgeGroup
    var isActive: Bool
}

struct RecoverFamilyResponse: Codable {
    let success: Bool
    let message: String
    let familyId: String?
    let members: [FamilyMemberResponse]
}

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
    
    // MARK: - Dependencies
    
    private let networkManager = NetworkManager()
    
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
    
    // MARK: - User Role Management
    
    /**
     * Сохранить роль пользователя
     */
    func saveUserRole(_ role: FamilyRole) {
        UserDefaults.standard.set(role.rawValue, forKey: "current_user_role")
        // Role saved
    }
    
    /**
     * Получить текущую роль пользователя
     */
    func getCurrentUserRole() -> FamilyRole? {
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
              let role = FamilyRole(storageValue: roleString) else {
            return nil
        }
        return role
    }
    
    /**
     * Проверить, есть ли сохранённая роль
     */
    func hasUserRole() -> Bool {
        return getCurrentUserRole() != nil
    }
    
    /**
     * Удалить сохранённую роль (для выхода)
     */
    func clearUserRole() {
        UserDefaults.standard.removeObject(forKey: "current_user_role")
        // Role cleared
    }
    
    // MARK: - Public Methods
    
    /**
     * Начать регистрацию (показать Consent)
     */
    func startRegistration() {
        // Показываем модал согласия
        showConsentModal = true
    }
    
    /**
     * Согласие принято
     */
    func acceptConsent() {
        consentAccepted = true
        
        // Сохраняем согласие
        // TODO: В будущем заменить на Keychain для безопасности
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.consentAccepted)
        UserDefaults.standard.set(Date(), forKey: AppConfig.UserDefaultsKeys.consentDate)
        UserDefaults.standard.set(AppConfig.Consent.currentVersion, forKey: AppConfig.UserDefaultsKeys.consentVersion)
        
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
        
        // ✅ СОХРАНЯЕМ РОЛЬ ПОЛЬЗОВАТЕЛЯ
        saveUserRole(role)
        
        currentStep = .creatingFamily
        isLoading = true
        
        // API request (закомментировано, используем mock данные)
        let _ = CreateFamilyRequest(
            role: role.rawValue,
            age_group: ageGroup.rawValue,
            personal_letter: letter,
            device_type: getDeviceType()
        )
        
        // МОКОВЫЕ ДАННЫЕ для тестирования (без реального API)
        isLoading = false
        
        // Генерируем фиктивные данные
        let mockFamilyID = "FAM_\(UUID().uuidString.prefix(12))"
        let mockRecoveryCode = "FAM-A1B2-C3D4-E5F6"
        
        familyID = mockFamilyID
        recoveryCode = mockRecoveryCode
        
        // ✅ НОВОЕ: Сохраняем family_id в UserDefaults
        UserDefaults.standard.set(mockFamilyID, forKey: "family_id")
        
        // ✅ НОВОЕ: Сохраняем создателя семьи в family_members_list
        saveCreatorAsFamilyMember(role: role, ageGroup: ageGroup)
        
        currentStep = .showingRecoveryCode
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.showFamilyCreatedModal = true
        }
        
        /* ЗАКОММЕНТИРОВАННЫЙ API КОД
        networkManager.createFamily(request: request) { [weak self] result in
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
                }
            }
        }
        */
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
        
        networkManager.joinFamily(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    
                    // ✅ НОВОЕ: Сохраняем family_id в UserDefaults
                    UserDefaults.standard.set(response.family_id, forKey: "family_id")
                    
                    self?.familyMembers = response.members.map { member in
                        FamilyMember(
                            id: member.id,
                            name: member.name,
                            role: FamilyRole(storageValue: member.role) ?? .parent,
                            ageGroup: AgeGroup(rawValue: member.role) ?? .adult,
                            isActive: member.status == "protected"
                        )
                    }
                    
                    // ✅ НОВОЕ: Сохраняем присоединившегося участника в family_members_list
                    self?.saveJoinedMemberAsFamilyMember(role: role, ageGroup: ageGroup)
                    
                    self?.currentStep = .completed
                    self?.showSuccessModal = true
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    // MARK: - Recover Access
    
    func recoverAccess(withCode code: String) {
        isLoading = true
        
        networkManager.recoverFamily(familyID: extractFamilyID(from: code)) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    self?.familyID = response.familyId
                    self?.familyMembers = response.members.map { member in
                        FamilyMember(
                            id: member.id,
                            name: member.name,
                            role: FamilyRole(storageValue: member.role) ?? .parent,
                            ageGroup: AgeGroup(rawValue: member.role) ?? .adult,
                            isActive: member.status == "protected"
                        )
                    }
                    
                    self?.currentStep = .completed
                    self?.showSuccessModal = true
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
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
    
    // MARK: - Save Family Members to UserDefaults
    
    /**
     * Сохранить создателя семьи в family_members_list
     */
    private func saveCreatorAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup) {
        // Получаем имя пользователя из UserDefaults или используем дефолтное
        let userName = UserDefaults.standard.string(forKey: "current_user_name") ?? "Вы"
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: String
        switch role {
        case .parent:
            cardRole = "parent"
        case .child:
            cardRole = ageGroup == .teen ? "teenager" : "child"
        case .teenager:
            cardRole = "teenager"
        case .elderly:
            cardRole = "elderly"
        }
        
        // Получаем аватар для роли
        let avatar: String
        switch cardRole {
        case "parent": avatar = "👨"
        case "child": avatar = "👧"
        case "teenager": avatar = "🧒"
        case "elderly": avatar = "👵"
        default: avatar = "👤"
        }
        
        // Создаём структуру для сохранения
        let memberData: [String: Any] = [
            "id": UUID().uuidString,
            "name": userName,
            "role": cardRole,
            "avatar": avatar,
            "status": "protected",
            "threatsBlocked": 0,
            "lastActive": "Сейчас"
        ]
        
        // Сохраняем в UserDefaults
        var members: [[String: Any]] = [memberData]
        
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let existingMembers = try? JSONSerialization.jsonObject(with: savedData) as? [[String: Any]] {
            // Если есть существующие участники, проверяем, не дублируем ли мы
            if !existingMembers.contains(where: { ($0["name"] as? String) == userName }) {
                members = existingMembers + [memberData]
            } else {
                // Обновляем существующего участника
                members = existingMembers.map { member in
                    if (member["name"] as? String) == userName {
                        return memberData
                    }
                    return member
                }
            }
        }
        
        // Кодируем и сохраняем
        if let encoded = try? JSONSerialization.data(withJSONObject: members) {
            UserDefaults.standard.set(encoded, forKey: "family_members_list")
            print("✅ Создатель семьи сохранён в family_members_list: \(userName) (\(cardRole))")
            
            // Уведомляем другие экраны об изменении
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        } else {
            print("❌ Ошибка сохранения создателя семьи")
        }
    }
    
    /**
     * Сохранить присоединившегося участника в family_members_list
     */
    private func saveJoinedMemberAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup) {
        // Получаем имя пользователя из UserDefaults или используем дефолтное
        let userName = UserDefaults.standard.string(forKey: "current_user_name") ?? "Вы"
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: String
        switch role {
        case .parent:
            cardRole = "parent"
        case .child:
            cardRole = ageGroup == .teen ? "teenager" : "child"
        case .teenager:
            cardRole = "teenager"
        case .elderly:
            cardRole = "elderly"
        }
        
        // Получаем аватар для роли
        let avatar: String
        switch cardRole {
        case "parent": avatar = "👨"
        case "child": avatar = "👧"
        case "teenager": avatar = "🧒"
        case "elderly": avatar = "👵"
        default: avatar = "👤"
        }
        
        // Создаём структуру для сохранения
        let memberData: [String: Any] = [
            "id": UUID().uuidString,
            "name": userName,
            "role": cardRole,
            "avatar": avatar,
            "status": "protected",
            "threatsBlocked": 0,
            "lastActive": "Сейчас"
        ]
        
        // Загружаем существующих участников и добавляем нового
        var members: [[String: Any]] = []
        
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let existingMembers = try? JSONSerialization.jsonObject(with: savedData) as? [[String: Any]] {
            members = existingMembers
            
            // Проверяем, нет ли уже этого участника
            if !members.contains(where: { ($0["name"] as? String) == userName }) {
                members.append(memberData)
            } else {
                // Обновляем существующего участника
                members = members.map { member in
                    if (member["name"] as? String) == userName {
                        return memberData
                    }
                    return member
                }
            }
        } else {
            // Если нет существующих участников, создаём список с новым участником
            members = [memberData]
        }
        
        // Кодируем и сохраняем
        if let encoded = try? JSONSerialization.data(withJSONObject: members) {
            UserDefaults.standard.set(encoded, forKey: "family_members_list")
            print("✅ Присоединившийся участник сохранён в family_members_list: \(userName) (\(cardRole))")
            
            // Уведомляем другие экраны об изменении
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        } else {
            print("❌ Ошибка сохранения присоединившегося участника")
        }
    }
}

// MARK: - API Models

struct CreateFamilyRequest: Codable {
    let role: String
    let age_group: String
    let personal_letter: String
    let device_type: String
}


struct JoinFamilyRequest: Codable {
    let family_id: String
    let role: String
    let age_group: String
    let personal_letter: String
    let device_type: String
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

