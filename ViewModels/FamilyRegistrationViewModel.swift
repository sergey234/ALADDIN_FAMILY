import SwiftUI
import Combine
import Security

// Import for shared types
import Foundation

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
    
    // ✅ МАППИНГ: Преобразование в формат, который ожидает сервер
    var serverValue: String {
        switch self {
        case .toddler: return "1-6"      // 0-3 → 1-6 (ближайший диапазон)
        case .child: return "7-12"        // 4-12 → 7-12 (ближайший диапазон)
        case .teen: return "13-17"        // 13-17 → 13-17 (точно совпадает)
        case .adult: return "24-55"       // 18-64 → 24-55 (основной диапазон для взрослых)
        case .senior: return "55+"         // 65+ → 55+ (ближайший диапазон)
        }
    }
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

struct FamilyResponse: Codable {
    let success: Bool
    let family_id: String
    let members: [FamilyMemberResponse]
    let your_member_id: String
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
    
    private let apiService = APIService.shared
    
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
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, переход происходит сразу
        currentStep = .selectingAgeGroup
        showAgeGroupModal = true
    }
    
    func onAgeGroupSelected(_ ageGroup: AgeGroup) {
        selectedAgeGroup = ageGroup
        showAgeGroupModal = false
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, переход происходит сразу
        currentStep = .selectingLetter
        showLetterModal = true
    }
    
    func onLetterSelected(_ letter: String) {
        selectedLetter = letter
        showLetterModal = false
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, создание семьи происходит сразу
        createFamily()
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
        print("✅ [FamilyRegistrationViewModel] Роль сохранена: \(role.rawValue)")
        // ✅ ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ: Убеждаемся, что UserDefaults синхронизирован
        UserDefaults.standard.synchronize()
        print("✅ [FamilyRegistrationViewModel] UserDefaults синхронизирован")
        
        currentStep = .creatingFamily
        isLoading = true
        
        // API request
        // ✅ ИСПРАВЛЕНО: Используем serverValue вместо rawValue для возрастной группы
        let request = CreateFamilyRequest(
            role: role.rawValue,
            age_group: ageGroup.serverValue,  // ✅ Преобразуем в формат сервера
            personal_letter: letter,
            device_type: getDeviceType()
        )

        print("🏠 [FamilyRegistrationViewModel.createFamily] ========== СОЗДАНИЕ СЕМЬИ ==========")
        print("🏠 [FamilyRegistrationViewModel.createFamily] Роль: \(role.rawValue)")
        print("🏠 [FamilyRegistrationViewModel.createFamily] Возрастная группа (клиент): \(ageGroup.rawValue)")
        print("🏠 [FamilyRegistrationViewModel.createFamily] Возрастная группа (сервер): \(ageGroup.serverValue)")
        print("🏠 [FamilyRegistrationViewModel.createFamily] Буква: \(letter)")

        // ✅ УДАЛЕНО: Моковые данные - теперь используем реальный API

        // ✅ РАСКОММЕНТИРОВАН: Реальный API код
        apiService.createFamily(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false

                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    self?.recoveryCode = response.recovery_code

                    // ✅ НОВОЕ: Сохраняем your_member_id
                    UserDefaults.standard.set(response.your_member_id, forKey: "your_member_id")
                    print("✅ your_member_id сохранен: \(response.your_member_id)")

                    // ✅ ПОПЫТКА 1: Проверяем, есть ли токены в response
                    if self?.isValidJWTToken(response.access_token) == true,
                       self?.isValidJWTToken(response.refresh_token) == true,
                       let accessToken = response.access_token,
                       let refreshToken = response.refresh_token {
                        // ✅ Токены есть - сохраняем (Попытка 1 успешна)
                        if self?.saveTokens(accessToken: accessToken, refreshToken: refreshToken) == true {
                            print("✅ Попытка 1 успешна: токены сохранены из response")
                        } else {
                            // Ошибка сохранения - используем fallback
                            self?.loginByRecoveryCode(familyID: response.family_id, recoveryCode: response.recovery_code)
                        }
                    } else {
                        // ✅ Токенов нет - используем fallback (Попытка 2)
                        print("ℹ️ Попытка 1: токенов нет в response, используем fallback")
                        self?.loginByRecoveryCode(familyID: response.family_id, recoveryCode: response.recovery_code)
                    }

                    // Format recovery code for display
                    self?.recoveryCode = self?.formatRecoveryCode(response.family_id) ?? response.recovery_code

                    // ✅ НОВОЕ: Автоматически сохраняем Recovery Code в Keychain
                    if let recoveryCode = self?.recoveryCode,
                       let familyID = self?.familyID {
                        let saved = RecoveryCodeStorageManager.shared.saveRecoveryCode(
                            recoveryCode,
                            familyID: familyID
                        )
                        if saved {
                            print("✅ Recovery Code автоматически сохранен в Keychain")
                        }
                    }

                    self?.currentStep = .showingRecoveryCode

                    // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, модал показывается сразу
                    self?.showFamilyCreatedModal = true

                case .failure(let error):
                    print("❌ [FamilyRegistrationViewModel.createFamily] Ошибка создания семьи: \(error)")
                    print("   Тип ошибки: \(type(of: error))")
                    if let decodingError = error as? DecodingError {
                        print("   Детали декодирования:")
                        switch decodingError {
                        case .keyNotFound(let key, let context):
                            print("     - Отсутствует ключ: \(key.stringValue)")
                            print("     - Путь: \(context.codingPath)")
                        case .typeMismatch(let type, let context):
                            print("     - Несоответствие типа: \(type)")
                            print("     - Путь: \(context.codingPath)")
                        case .valueNotFound(let type, let context):
                            print("     - Значение не найдено: \(type)")
                            print("     - Путь: \(context.codingPath)")
                        case .dataCorrupted(let context):
                            print("     - Данные повреждены")
                            print("     - Путь: \(context.codingPath)")
                        @unknown default:
                            print("     - Неизвестная ошибка декодирования")
                        }
                    }
                    self?.errorMessage = error.localizedDescription
                    self?.isLoading = false
                }
            }
        }
    }

    // MARK: - Recovery Code Login (Fallback - Попытка 2)

    /// ✅ ДОБАВЛЕНО: Авторизация по recovery code (Попытка 2 - fallback)
    private func loginByRecoveryCode(familyID: String, recoveryCode: String, retryCount: Int = 0) {
        print("🔄 Попытка 2: авторизация по recovery code (попытка \(retryCount + 1))")

        apiService.loginByRecoveryCode(familyID: familyID, recoveryCode: recoveryCode) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let loginResponse):
                    print("✅ Попытка 2 успешна: получены токены")

                    // Проверяем и сохраняем токены
                    if self?.isValidJWTToken(loginResponse.access_token) == true {
                        if self?.saveTokens(accessToken: loginResponse.access_token, refreshToken: loginResponse.refresh_token) == true {
                            print("✅ Попытка 2 завершена: токены сохранены")
                        } else {
                            print("⚠️ Попытка 2: ошибка сохранения токенов")
                            // Продолжаем без токенов (демо режим)
                        }
                    } else {
                        print("⚠️ Попытка 2: невалидные токены в ответе")
                        // Продолжаем без токенов (демо режим)
                    }

                case .failure(let error):
                    print("❌ Попытка 2 не удалась: \(error.localizedDescription)")

                    // Повторная попытка при сетевых ошибках
                    if let urlError = error as? URLError,
                       (urlError.code == .notConnectedToInternet || urlError.code == .timedOut),
                       retryCount < 2 {
                        print("🔄 Повторная попытка через 5 секунд...")
                        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0) {
                            self?.loginByRecoveryCode(familyID: familyID, recoveryCode: recoveryCode, retryCount: retryCount + 1)
                        }
                    } else {
                        print("⚠️ Попытка 2 окончательно не удалась. Продолжаем в демо режиме")
                        // Продолжаем без токенов (демо режим)
                    }
                }
            }
        }
    }

    // MARK: - Token Validation & Security

    /// ✅ ДОБАВЛЕНО: Валидация JWT токена
    private func isValidJWTToken(_ token: String?) -> Bool {
        guard let token = token,
              !token.isEmpty,
              token != "null",
              token.count > 20, // Минимальная длина JWT
              token.contains(".") else { // JWT содержит точки
            return false
        }
        return true
    }

    /// ✅ ДОБАВЛЕНО: Безопасное логирование авторизации (без recovery code)
    private func logAuthEvent(_ event: String, method: String, hasTokens: Bool = false, familyID: String? = nil) {
        #if DEBUG
        var logMessage = "🔐 [Auth] \(event)"
        logMessage += " | Метод: \(method)"
        logMessage += " | Токены: \(hasTokens ? "✅" : "❌")"
        if let familyID = familyID {
            logMessage += " | FamilyID: \(familyID)"
        }
        // НЕ логируем recovery code для безопасности
        print(logMessage)
        #endif
    }

    // MARK: - Token Management

    /// ✅ ДОБАВЛЕНО: Сохранение токенов с проверкой и повторной попыткой
    private func saveTokens(accessToken: String, refreshToken: String?) -> Bool {
        print("🔐 Сохранение токенов в Keychain...")

        // Попытка 1: Сохраняем токены
        KeychainManager.shared.save(accessToken, forKey: .authToken)
        if let refreshToken = refreshToken {
            KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
        }

        // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
        let loadedAccessToken = KeychainManager.shared.loadString(forKey: .authToken)
        let loadedRefreshToken = refreshToken != nil ? KeychainManager.shared.loadString(forKey: .refreshToken) : nil

        if loadedAccessToken == accessToken &&
           (refreshToken == nil || loadedRefreshToken == refreshToken) {
            print("✅ Токены успешно сохранены и проверены")
            // ✅ УВЕДОМЛЕНИЕ: Отправляем уведомление о успешной авторизации
            NotificationCenter.default.post(name: NSNotification.Name("UserDidLogin"), object: nil)
            return true
        } else {
            print("❌ Ошибка сохранения токенов в Keychain, повторная попытка...")

            // Попытка 2: Повторяем сохранение через 0.5 секунды
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                KeychainManager.shared.save(accessToken, forKey: .authToken)
                if let refreshToken = refreshToken {
                    KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
                }

                // Финальная проверка
                let finalAccessToken = KeychainManager.shared.loadString(forKey: .authToken)
                let finalRefreshToken = refreshToken != nil ? KeychainManager.shared.loadString(forKey: .refreshToken) : nil

                if finalAccessToken == accessToken &&
                   (refreshToken == nil || finalRefreshToken == refreshToken) {
                    print("✅ Токены успешно сохранены после повторной попытки")
                    // ✅ УВЕДОМЛЕНИЕ: Отправляем уведомление о успешной авторизации
                    NotificationCenter.default.post(name: NSNotification.Name("UserDidLogin"), object: nil)
                } else {
                    print("❌ Критическая ошибка: токены не сохранены даже после повторной попытки")
                }
            }
            return false
        }
    }

    // MARK: - Join Family
    
    func joinFamily(withCode code: String) {
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            return
        }

        // ✅ ЗАДАЧА 67: Санитизация кода семьи перед обработкой
        do {
            let sanitizedCode = try code.sanitizedAsFamilyId()
            joinFamilySanitized(withCode: sanitizedCode)

        } catch let error as InputSanitizer.SanitizationError {
            errorMessage = error.localizedDescription
            #if DEBUG
            print("❌ FamilyRegistrationViewModel: Ошибка санитизации кода семьи: \(error.localizedDescription)")
            #endif
        } catch {
            errorMessage = "Произошла неизвестная ошибка при обработке кода семьи."
        }
    }

    // ✅ ЗАДАЧА 67: Приватный метод с санитизированными данными
    private func joinFamilySanitized(withCode sanitizedCode: String) {
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            return
        }

        isLoading = true

        let familyId = extractFamilyID(from: sanitizedCode)
        
        let request = JoinFamilyRequest(
            family_id: familyId,
            role: role.rawValue,
            age_group: ageGroup.serverValue,  // ✅ ИСПРАВЛЕНО: Используем serverValue
            personal_letter: letter,
            device_type: getDeviceType()
        )
        
        apiService.joinFamily(request: request) { [weak self] (result: Result<APIResponse<FamilyResponse>, Error>) in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    // ✅ ИСПРАВЛЕНИЕ: response - это APIResponse, данные в response.data
                    guard let data = response.data else {
                        self?.errorMessage = "Неверный ответ сервера"
                        return
                    }

                    self?.familyID = data.family_id

                    // ✅ НОВОЕ: Сохраняем family_id в UserDefaults
                    UserDefaults.standard.set(data.family_id, forKey: "family_id")
                    
                    // ✅ НОВОЕ: Сохраняем your_member_id
                    UserDefaults.standard.set(data.your_member_id, forKey: "your_member_id")
                    print("✅ your_member_id сохранен: \(data.your_member_id)")

                    self?.familyMembers = data.members.map { member in
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
                    
                    // ✅ НОВОЕ: Инициализируем стартовый баланс единорога для детей
                    // Если это ребенок, устанавливаем стартовый баланс 100 единорогов
                    if role == .child || role == .teenager {
                        let startBalance = 100 // Стартовый баланс для нового ребенка
                        UserDefaults.standard.set(startBalance, forKey: "child_unicorn_balance")
                        print("✅ FamilyRegistration: Установлен стартовый баланс единорога: \(startBalance) 🦄")
                    }
                    
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
        errorMessage = nil

        // ✅ РЕАЛИЗОВАНО: Используем существующий метод recoverFamily из NetworkManager
        let familyID = extractFamilyID(from: code)
        
        // Используем NetworkManager через apiService (метод уже реализован в extension, строка 788)
        apiService.networkManager.recoverFamily(familyID: familyID) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        // Сохраняем family_id
                        self?.familyID = response.familyId
                        UserDefaults.standard.set(response.familyId, forKey: "family_id")
                        
                        // Обновляем список участников
                        self?.familyMembers = response.members.map { member in
                            FamilyMember(
                                id: member.id,
                                name: member.name,
                                role: FamilyRole(storageValue: member.role) ?? .parent,
                                ageGroup: AgeGroup(rawValue: member.role) ?? .adult,
                                isActive: member.status == "protected"
                            )
                        }
                        
                        // Уведомляем об успехе
                        NotificationCenter.default.post(
                            name: NSNotification.Name("FamilyRecoverySuccess"),
                            object: nil
                        )
                        
                        self?.currentStep = .completed
                        self?.showSuccessModal = true
                    } else {
                        self?.errorMessage = response.message
                        NotificationCenter.default.post(
                            name: NSNotification.Name("FamilyRecoveryError"),
                            object: nil,
                            userInfo: ["error": response.message]
                        )
                    }
                    
                case .failure(let error):
                    let errorMessage = error.localizedDescription
                    self?.errorMessage = errorMessage
                    NotificationCenter.default.post(
                        name: NSNotification.Name("FamilyRecoveryError"),
                        object: nil,
                        userInfo: ["error": errorMessage]
                    )
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
        let cardRole: FamilyMemberCard.FamilyRole
        switch role {
        case .parent:
            cardRole = .parent
        case .child:
            cardRole = ageGroup == .teen ? .teenager : .child
        case .teenager:
            cardRole = .teenager
        case .elderly:
            cardRole = .elderly
        }
        
        // Получаем аватар для роли
        let avatar: String
        switch cardRole {
        case .parent: avatar = "👨"
        case .child: avatar = "👧"
        case .teenager: avatar = "🧒"
        case .elderly: avatar = "👵"
        }
        
        // ✅ ИСПРАВЛЕНИЕ: Загружаем существующий список участников
        var existingMembers: [FamilyMemberData] = []
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            existingMembers = decoded
            print("✅ Загружено \(existingMembers.count) существующих участников")
        }
        
        // Проверяем, нет ли уже такого участника (по имени и роли)
        let isDuplicate = existingMembers.contains { existingMember in
            existingMember.name == userName && existingMember.role == cardRole
        }
        
        if !isDuplicate {
            // ✅ ИСПРАВЛЕНИЕ: Добавляем нового участника к существующему списку
            let newMember = FamilyMemberData(
                name: userName,
                role: cardRole,
                avatar: avatar,
                status: .protected,
                threatsBlocked: 0,
                lastActive: "Сейчас"
            )
            existingMembers.append(newMember)
            
            // Сохраняем обновленный список
            if let encoded = try? JSONEncoder().encode(existingMembers) {
                UserDefaults.standard.set(encoded, forKey: "family_members_list")
                print("✅ Создатель семьи добавлен к списку участников: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
            } else {
                print("❌ Ошибка кодирования списка участников")
            }
        } else {
            print("⚠️ Участник уже существует: \(userName) (\(cardRole)), не добавляем дубликат")
        }
    }
    
    /**
     * Сохранить присоединившегося участника в family_members_list
     */
    private func saveJoinedMemberAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup) {
        // Получаем имя пользователя из UserDefaults или используем дефолтное
        let userName = UserDefaults.standard.string(forKey: "current_user_name") ?? "Вы"
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: FamilyMemberCard.FamilyRole
        switch role {
        case .parent:
            cardRole = .parent
        case .child:
            cardRole = ageGroup == .teen ? .teenager : .child
        case .teenager:
            cardRole = .teenager
        case .elderly:
            cardRole = .elderly
        }
        
        // Получаем аватар для роли
        let avatar: String
        switch cardRole {
        case .parent: avatar = "👨"
        case .child: avatar = "👧"
        case .teenager: avatar = "🧒"
        case .elderly: avatar = "👵"
        }
        
        // ✅ ИСПРАВЛЕНИЕ: Загружаем существующий список участников
        var existingMembers: [FamilyMemberData] = []
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            existingMembers = decoded
            print("✅ Загружено \(existingMembers.count) существующих участников")
        }
        
        // Проверяем, нет ли уже такого участника (по имени и роли)
        let isDuplicate = existingMembers.contains { existingMember in
            existingMember.name == userName && existingMember.role == cardRole
        }
        
        if !isDuplicate {
            // ✅ ИСПРАВЛЕНИЕ: Добавляем нового участника к существующему списку
            let newMember = FamilyMemberData(
                name: userName,
                role: cardRole,
                avatar: avatar,
                status: .protected,
                threatsBlocked: 0,
                lastActive: "Сейчас"
            )
            existingMembers.append(newMember)
            
            // Сохраняем обновленный список
            if let encoded = try? JSONEncoder().encode(existingMembers) {
                UserDefaults.standard.set(encoded, forKey: "family_members_list")
                print("✅ Присоединившийся участник добавлен к списку: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
            } else {
                print("❌ Ошибка кодирования списка участников")
            }
        } else {
            print("⚠️ Участник уже существует: \(userName) (\(cardRole)), не добавляем дубликат")
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

