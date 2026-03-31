import SwiftUI
import Combine
import Security

// Import for shared types
import Foundation

// Master Logger for family registration logging
private let logger = MasterLogger.shared

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
    
    /// ✅ ИСПРАВЛЕНИЕ ПОДРОСТКА: Маппинг роли для отправки на сервер
    /// Сервер принимает только: "parent", "child", "elderly", "other"
    /// Подросток отправляется как "child" + age_group="13-17"
    var serverValue: String {
        switch self {
        case .parent:
            return "parent"
        case .child:
            return "child"
        case .teenager:
            return "child"  // ✅ Подросток → child для сервера
        case .elderly:
            return "elderly"
        }
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
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование
        print("🔍 onRoleSelected: role=\(role.rawValue)")
        if role == .teenager {
            print("✅ Выбрана роль Подросток (.teenager)")
            VisualLogger.shared.log("✅ ПОДРОСТОК: Выбрана роль .teenager", level: .success, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Выбрана роль .teenager")
        }
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, переход происходит сразу
        currentStep = .selectingAgeGroup
        showAgeGroupModal = true
    }
    
    func onAgeGroupSelected(_ ageGroup: AgeGroup) {
        selectedAgeGroup = ageGroup
        showAgeGroupModal = false
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование
        print("🔍 onAgeGroupSelected: ageGroup=\(ageGroup.rawValue)")
        if ageGroup == .teen {
            print("✅ Выбрана возрастная группа Подросток (.teen)")
        }
        if let role = selectedRole {
            print("   - Текущая роль: \(role.rawValue)")
            if role == .teenager && ageGroup == .teen {
                print("✅ Комбинация: роль .teenager + возрастная группа .teen")
                VisualLogger.shared.log("✅ ПОДРОСТОК: Комбинация role=.teenager + ageGroup=.teen", level: .success, category: "FAMILY")
                MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Комбинация role=.teenager + ageGroup=.teen")
            }
        }
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, переход происходит сразу
        currentStep = .selectingLetter
        showLetterModal = true
    }
    
    func onLetterSelected(_ letter: String) {
        selectedLetter = letter
        showLetterModal = false
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #1: Сохраняем имя пользователя на основе выбранной буквы
        // Формируем имя: "Родитель A", "Ребенок B", "Подросток C", "Пожилой D" и т.д.
        if let role = selectedRole {
            let roleName: String
            switch role {
            case .parent: roleName = "Родитель"
            case .child: roleName = "Ребенок"
            case .teenager: roleName = "Подросток"
            case .elderly: roleName = "Пожилой"
            }
            let userName = "\(roleName) \(letter)"
            UserDefaults.standard.set(userName, forKey: "current_user_name")
            UserDefaults.standard.synchronize()
            logger.business("✅ User name saved: \(userName)")
        }
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, создание семьи происходит сразу
        createFamily()
    }
    
    // MARK: - Create Family
    
    func createFamily() {
        logger.business("Creating family with role: \(selectedRole?.rawValue ?? "none")")
        
        // ✅ ИСПРАВЛЕНИЕ ПОДРОСТКА: Детальное логирование
        if let role = selectedRole, role == .teenager {
            VisualLogger.shared.log("🔍 ПОДРОСТОК: createFamily() вызван", level: .info, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "🔍 ПОДРОСТОК: createFamily() вызван")
        }
        
        guard let role = selectedRole,
              let ageGroup = selectedAgeGroup,
              let letter = selectedLetter else {
            // ✅ ИСПРАВЛЕНИЕ ПОДРОСТКА: Логирование если данные отсутствуют
            if selectedRole == nil {
                VisualLogger.shared.log("❌ ПОДРОСТОК: selectedRole = nil!", level: .error, category: "FAMILY")
                MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: selectedRole = nil!")
            }
            if selectedAgeGroup == nil {
                VisualLogger.shared.log("❌ ПОДРОСТОК: selectedAgeGroup = nil!", level: .error, category: "FAMILY")
                MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: selectedAgeGroup = nil!")
            }
            if selectedLetter == nil {
                VisualLogger.shared.log("❌ ПОДРОСТОК: selectedLetter = nil!", level: .error, category: "FAMILY")
                MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: selectedLetter = nil!")
            }
            return
        }
        
        // ✅ ИСПРАВЛЕНИЕ ПОДРОСТКА: Логирование перед созданием
        if role == .teenager {
            VisualLogger.shared.log("✅ ПОДРОСТОК: Данные готовы - role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), letter=\(letter)", level: .success, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Данные готовы - role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), letter=\(letter)")
        }
        
        // ✅ СОХРАНЯЕМ РОЛЬ ПОЛЬЗОВАТЕЛЯ
        saveUserRole(role)
        logger.business("Family role saved: \(role.rawValue)")
        // ✅ ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ: Убеждаемся, что UserDefaults синхронизирован
        UserDefaults.standard.synchronize()
        logger.business("UserDefaults synchronized")
        
        currentStep = .creatingFamily
        isLoading = true
        
        // API request
        // ✅ ИСПРАВЛЕНО: Используем serverValue для роли и возрастной группы
        let request = CreateFamilyRequest(
            role: role.serverValue,  // ✅ ИСПРАВЛЕНО: Подросток → "child" для сервера
            age_group: ageGroup.serverValue,  // ✅ Преобразуем в формат сервера
            personal_letter: letter,
            device_type: getDeviceType()
        )

        logger.business("========== CREATING FAMILY ==========")
        logger.business("Role (client): \(role.rawValue)")
        logger.business("Role (server): \(role.serverValue)")  // ✅ ИСПРАВЛЕНО: Логируем serverValue
        logger.business("Age group (client): \(ageGroup.rawValue)")
        logger.business("Age group (server): \(ageGroup.serverValue)")
        logger.business("Personal letter length: \(letter.count) characters")

        // ✅ УДАЛЕНО: Моковые данные - теперь используем реальный API

        // ✅ РАСКОММЕНТИРОВАН: Реальный API код
        apiService.createFamily(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false

                switch result {
                case .success(let response):
                    self?.familyID = response.family_id
                    self?.recoveryCode = response.recovery_code

                    // ✅ BUILD 115: Сохраняем your_member_id с диагностикой
                    // ✅ КРЕПОСТЬ 2.1: Асинхронный разрыв - UserDefaults.set в async для предотвращения рекурсии
                    let memberIdToSave = response.your_member_id
                    DispatchQueue.main.async {
                        UserDefaults.standard.set(memberIdToSave, forKey: "your_member_id")
                        logger.business("✅ Member ID saved: \(memberIdToSave)")
                        logger.business("✅ FamilyRegistrationViewModel: your_member_id сохранен при создании семьи: \(memberIdToSave)")
                        
                        // ✅ BUILD 115: Проверяем сохранение
                        let savedId = UserDefaults.standard.string(forKey: "your_member_id")
                        if savedId == memberIdToSave {
                            logger.business("✅ FamilyRegistrationViewModel: Проверка успешна - ID сохранен корректно")
                        } else {
                            logger.business("❌ FamilyRegistrationViewModel: ОШИБКА - ID не сохранен!")
                        }
                    }

                    // ✅ ПОПЫТКА 1: Проверяем, есть ли токены в response
                    if self?.isValidJWTToken(response.access_token) == true,
                       self?.isValidJWTToken(response.refresh_token) == true,
                       let accessToken = response.access_token,
                       let refreshToken = response.refresh_token {
                        // ✅ Токены есть - сохраняем (Попытка 1 успешна)
                        if self?.saveTokens(accessToken: accessToken, refreshToken: refreshToken) == true {
                            logger.business("Attempt 1 successful: tokens saved from response")
                        } else {
                            // Ошибка сохранения - используем fallback
                            self?.loginByRecoveryCode(familyID: response.family_id, recoveryCode: response.recovery_code)
                        }
                    } else {
                        // ✅ Токенов нет - используем fallback (Попытка 2)
                        logger.business("Attempt 1: no tokens in response, using fallback")
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
                            logger.business("Recovery Code automatically saved to Keychain")
                        }
                    }

                    // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #1: Сохраняем создателя семьи в список участников
                    // Это должно вызываться ДО показа модала, чтобы участник был сохранен
                    if let role = self?.selectedRole,
                       let ageGroup = self?.selectedAgeGroup {
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование
                        print("🔍 Создание семьи: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue)")
                        self?.saveCreatorAsFamilyMember(role: role, ageGroup: ageGroup)
                        logger.business("✅ Creator saved as family member: \(role.rawValue), ageGroup: \(ageGroup.rawValue)")
                        
                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация UserDefaults
                        UserDefaults.standard.synchronize()
                    } else {
                        print("❌ ОШИБКА: selectedRole или selectedAgeGroup отсутствуют!")
                        if self?.selectedRole == nil {
                            print("   - selectedRole = nil")
                        }
                        if self?.selectedAgeGroup == nil {
                            print("   - selectedAgeGroup = nil")
                        }
                    }

                    self?.currentStep = .showingRecoveryCode

                    // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, модал показывается сразу
                    self?.showFamilyCreatedModal = true

                case .failure(let error):
                    logger.error("Family creation failed", error: error)
                    
                    // ✅ ИСПРАВЛЕНИЕ ПОДРОСТКА: Детальное логирование ошибки
                    if let role = self?.selectedRole, role == .teenager {
                        VisualLogger.shared.log("❌ ПОДРОСТОК: Ошибка создания семьи - \(error.localizedDescription)", level: .error, category: "FAMILY")
                        MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: Ошибка создания семьи - \(error.localizedDescription)")
                    }
                    
                    if let decodingError = error as? DecodingError {
                        logger.error("Decoding error details: \(decodingError.localizedDescription)")
                        if let role = self?.selectedRole, role == .teenager {
                            VisualLogger.shared.log("❌ ПОДРОСТОК: Decoding error - \(decodingError.localizedDescription)", level: .error, category: "FAMILY")
                    }
                    }
                    
                    let networkError = NetworkError.from(error)
                    switch networkError {
                    case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
                        self?.errorMessage = "Сессия истекла. Обновите вход и попробуйте снова."
                        VisualLogger.shared.log("⚠️ FAMILY CREATE unauthorized/session-expired", level: .warning, category: "FAMILY")
                    default:
                        self?.errorMessage = error.localizedDescription
                    }
                    self?.isLoading = false
                    self?.currentStep = .idle  // ✅ ИСПРАВЛЕНИЕ: Возвращаемся в idle при ошибке
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
                        if self?.isFamilyCompatibleJWT(loginResponse.access_token) == true {
                            if self?.saveTokens(accessToken: loginResponse.access_token, refreshToken: loginResponse.refresh_token) == true {
                                print("✅ Попытка 2 завершена: токены сохранены")
                            } else {
                                print("⚠️ Попытка 2: ошибка сохранения токенов")
                                // Продолжаем без токенов (демо режим)
                            }
                        } else {
                            // Safety net: не сохраняем recovery JWT, если он может вызвать Invalid user_id in token.
                            self?.bootstrapFamilyCompatibleToken { success in
                                if success {
                                    print("✅ Попытка 2 завершена: сохранен family-совместимый device token")
                                } else if self?.saveTokens(accessToken: loginResponse.access_token, refreshToken: loginResponse.refresh_token) == true {
                                    print("⚠️ Bootstrap не удался, сохранен recovery token как fallback")
                                } else {
                                    print("⚠️ Попытка 2: не удалось сохранить fallback token")
                                }
                            }
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

    private func isFamilyCompatibleJWT(_ token: String) -> Bool {
        guard
            let payload = decodeJWTPayload(token),
            let identityRaw = payload["user_id"] ?? payload["id"] ?? payload["sub"]
        else {
            return false
        }
        if let idInt = identityRaw as? Int {
            return idInt > 0
        }
        if let idString = identityRaw as? String {
            return Int(idString) != nil
        }
        return false
    }

    private func decodeJWTPayload(_ token: String) -> [String: Any]? {
        let parts = token.split(separator: ".")
        guard parts.count >= 2 else { return nil }
        var base64 = String(parts[1])
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        let padding = 4 - (base64.count % 4)
        if padding < 4 {
            base64 += String(repeating: "=", count: padding)
        }
        guard
            let data = Data(base64Encoded: base64),
            let json = try? JSONSerialization.jsonObject(with: data),
            let payload = json as? [String: Any]
        else {
            return nil
        }
        return payload
    }

    private func bootstrapFamilyCompatibleToken(completion: @escaping (Bool) -> Void) {
        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        let deviceType = UIDevice.current.userInterfaceIdiom == .pad ? "tablet" : "smartphone"
        let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: deviceType)

        apiService.registerDeviceAnonymously(request: request) { [weak self] result in
            DispatchQueue.main.async {
                guard let self = self else {
                    completion(false)
                    return
                }
                switch result {
                case .success(let response):
                    completion(self.saveTokens(accessToken: response.token, refreshToken: response.refreshToken))
                case .failure:
                    completion(false)
                }
            }
        }
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
        #if DEBUG
        let startMessage = """
        🔐🔐🔐 FamilyRegistrationViewModel.saveTokens: Начало сохранения токенов
           - Access token длина: \(accessToken.count)
           - Refresh token: \(refreshToken != nil ? "✅ есть (длина: \(refreshToken!.count))" : "❌ нет")
        """
        VisualLogger.shared.log(startMessage, level: .info, category: "AUTH")
        print(startMessage)
        #endif
        logger.business("Saving tokens to Keychain (access: \(accessToken.prefix(10))..., refresh: \(refreshToken?.prefix(10) ?? "none")...)")

        // Попытка 1: Сохраняем токены
        KeychainManager.shared.save(accessToken, forKey: .authToken)
        #if DEBUG
        VisualLogger.shared.log("💾 FamilyRegistrationViewModel.saveTokens: Access token сохранен в Keychain", level: .success, category: "AUTH")
        print("💾 FamilyRegistrationViewModel.saveTokens: Access token сохранен в Keychain")
        #endif
        
        if let refreshToken = refreshToken {
            KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
            #if DEBUG
            VisualLogger.shared.log("💾 FamilyRegistrationViewModel.saveTokens: Refresh token сохранен в Keychain", level: .success, category: "AUTH")
            print("💾 FamilyRegistrationViewModel.saveTokens: Refresh token сохранен в Keychain")
            #endif
        }
        
        // ✅ КРИТИЧНО: Также сохраняем токен в AppConfig для NetworkManager
        AppConfig.authToken = accessToken
        #if DEBUG
        VisualLogger.shared.log("💾 FamilyRegistrationViewModel.saveTokens: Access token установлен в AppConfig.authToken", level: .success, category: "AUTH")
        print("💾 FamilyRegistrationViewModel.saveTokens: Access token установлен в AppConfig.authToken")
        #endif

        // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
        let loadedAccessToken = KeychainManager.shared.loadString(forKey: .authToken)
        let loadedRefreshToken = refreshToken != nil ? KeychainManager.shared.loadString(forKey: .refreshToken) : nil

        if loadedAccessToken == accessToken &&
           (refreshToken == nil || loadedRefreshToken == refreshToken) {
            logger.business("Tokens successfully saved and verified")
            #if DEBUG
            let successMessage = """
            ✅ FamilyRegistrationViewModel.saveTokens: Токены успешно сохранены и проверены
               - Access token в Keychain: ✅
               - Refresh token в Keychain: \(refreshToken != nil ? "✅" : "N/A")
               - AppConfig.authToken: \(AppConfig.authToken != nil ? "✅ установлен" : "❌ не установлен")
            """
            VisualLogger.shared.log(successMessage, level: .success, category: "AUTH")
            print(successMessage)
            #endif
            // ✅ УВЕДОМЛЕНИЕ: Отправляем уведомление о успешной авторизации
            NotificationCenter.default.post(name: NSNotification.Name("UserDidLogin"), object: nil)
            #if DEBUG
            VisualLogger.shared.log("📢 FamilyRegistrationViewModel.saveTokens: Отправлено уведомление UserDidLogin", level: .info, category: "AUTH")
            print("📢 FamilyRegistrationViewModel.saveTokens: Отправлено уведомление UserDidLogin")
            #endif
            return true
        } else {
            #if DEBUG
            let errorMessage = """
            ❌ FamilyRegistrationViewModel.saveTokens: Ошибка сохранения токенов в Keychain
               - Access token совпадает: \(loadedAccessToken == accessToken ? "✅" : "❌")
               - Refresh token совпадает: \(refreshToken == nil ? "N/A" : (loadedRefreshToken == refreshToken ? "✅" : "❌"))
               - Повторная попытка через 0.5 секунды...
            """
            VisualLogger.shared.log(errorMessage, level: .error, category: "AUTH")
            print(errorMessage)
            #endif
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
            role: role.serverValue,  // ✅ ИСПРАВЛЕНО: Подросток → "child" для сервера
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
                    
                    // ✅ BUILD 115: Сохраняем your_member_id с диагностикой
                    // ✅ КРЕПОСТЬ 2.1: Асинхронный разрыв - UserDefaults.set в async для предотвращения рекурсии
                    let memberIdToSave = data.your_member_id
                    DispatchQueue.main.async {
                        UserDefaults.standard.set(memberIdToSave, forKey: "your_member_id")
                        logger.business("✅ Member ID saved: \(memberIdToSave)")
                        logger.business("✅ FamilyRegistrationViewModel: your_member_id сохранен при присоединении к семье: \(memberIdToSave)")
                        
                        // ✅ BUILD 115: Проверяем сохранение
                        let savedId = UserDefaults.standard.string(forKey: "your_member_id")
                        if savedId == memberIdToSave {
                            logger.business("✅ FamilyRegistrationViewModel: Проверка успешна - ID сохранен корректно")
                        } else {
                            logger.business("❌ FamilyRegistrationViewModel: ОШИБКА - ID не сохранен!")
                        }
                    }

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
                    // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование
                    print("🔍 Присоединение к семье: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue)")
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
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование для отладки
        print("🔍 saveCreatorAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), userName=\(userName)")
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: FamilyMemberCard.FamilyRole
        switch role {
        case .parent:
            cardRole = .parent
        case .child:
            // ✅ ИСПРАВЛЕНИЕ: Если роль .child и возрастная группа .teen, преобразуем в .teenager
            cardRole = ageGroup == .teen ? .teenager : .child
        case .teenager:
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Роль .teenager всегда преобразуется в .teenager
            cardRole = .teenager
            print("✅ Подросток: роль .teenager преобразована в cardRole .teenager")
        case .elderly:
            cardRole = .elderly
        }
        
        print("🔍 saveCreatorAsFamilyMember: cardRole=\(cardRole)")
        VisualLogger.shared.log("🔍 saveCreatorAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)", level: .info, category: "FAMILY")
        
        // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ ПОДРОСТКА
        if role == .teenager {
            print("✅ ПОДРОСТОК: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)")
            VisualLogger.shared.log("✅ ПОДРОСТОК: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)", level: .success, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)")
            if cardRole != .teenager {
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: cardRole не соответствует .teenager!")
                VisualLogger.shared.log("❌ КРИТИЧЕСКАЯ ОШИБКА: cardRole не соответствует .teenager!", level: .error, category: "FAMILY")
                MasterLogger.shared.log(.error, category: .business, message: "❌ КРИТИЧЕСКАЯ ОШИБКА: cardRole не соответствует .teenager!")
            }
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
            VisualLogger.shared.log("✅ Загружено \(existingMembers.count) существующих участников из UserDefaults", level: .info, category: "FAMILY")
        } else {
            VisualLogger.shared.log("⚠️ Не удалось загрузить существующих участников из UserDefaults", level: .warning, category: "FAMILY")
        }
        
        // Проверяем, нет ли уже такого участника (по имени и роли)
        let isDuplicate = existingMembers.contains { existingMember in
            existingMember.name == userName && existingMember.role == cardRole
        }
        
        if role == .teenager {
            VisualLogger.shared.log("🔍 ПОДРОСТОК: Проверка дубликатов - userName=\(userName), cardRole=\(cardRole), isDuplicate=\(isDuplicate)", level: .info, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "🔍 ПОДРОСТОК: Проверка дубликатов - userName=\(userName), cardRole=\(cardRole), isDuplicate=\(isDuplicate)")
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
            
            if role == .teenager {
                VisualLogger.shared.log("✅ ПОДРОСТОК: Новый участник создан - name=\(userName), role=\(cardRole.rawValue)", level: .success, category: "FAMILY")
                MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Новый участник создан - name=\(userName), role=\(cardRole.rawValue)")
            }
            
            // Сохраняем обновленный список
            if let encoded = try? JSONEncoder().encode(existingMembers) {
                UserDefaults.standard.set(encoded, forKey: "family_members_list")
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация UserDefaults
                UserDefaults.standard.synchronize()
                print("✅ Создатель семьи добавлен к списку участников: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                if role == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК: Сохранено в UserDefaults - всего участников: \(existingMembers.count)", level: .success, category: "FAMILY")
                    MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Сохранено в UserDefaults - всего участников: \(existingMembers.count)")
                    
                    // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Проверяем что подросток действительно сохранен
                    if let verifyData = UserDefaults.standard.data(forKey: "family_members_list"),
                       let verifyDecoded = try? JSONDecoder().decode([FamilyMemberData].self, from: verifyData) {
                        let teenagerFound = verifyDecoded.contains { $0.role == .teenager && $0.name == userName }
                        if teenagerFound {
                            VisualLogger.shared.log("✅ ПОДРОСТОК: Подтверждено сохранение в UserDefaults!", level: .success, category: "FAMILY")
                            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Подтверждено сохранение в UserDefaults!")
                        } else {
                            VisualLogger.shared.log("❌ ПОДРОСТОК: ОШИБКА - подросток НЕ найден после сохранения!", level: .error, category: "FAMILY")
                            MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: ОШИБКА - подросток НЕ найден после сохранения!")
                        }
                    }
                }
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
                NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
                
                if role == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК: Отправлены уведомления об обновлении", level: .success, category: "FAMILY")
                }
            } else {
                print("❌ Ошибка кодирования списка участников")
                if role == .teenager {
                    VisualLogger.shared.log("❌ ПОДРОСТОК: ОШИБКА кодирования списка участников!", level: .error, category: "FAMILY")
                    MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: ОШИБКА кодирования списка участников!")
                }
            }
        } else {
            print("⚠️ Участник уже существует: \(userName) (\(cardRole)), не добавляем дубликат")
            if role == .teenager {
                VisualLogger.shared.log("⚠️ ПОДРОСТОК: Участник уже существует (дубликат)", level: .warning, category: "FAMILY")
                MasterLogger.shared.log(.warn, category: .business, message: "⚠️ ПОДРОСТОК: Участник уже существует (дубликат)")
            }
        }
    }
    
    /**
     * Сохранить присоединившегося участника в family_members_list
     */
    private func saveJoinedMemberAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup) {
        // Получаем имя пользователя из UserDefaults или используем дефолтное
        let userName = UserDefaults.standard.string(forKey: "current_user_name") ?? "Вы"
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование для отладки
        print("🔍 saveJoinedMemberAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), userName=\(userName)")
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: FamilyMemberCard.FamilyRole
        switch role {
        case .parent:
            cardRole = .parent
        case .child:
            // ✅ ИСПРАВЛЕНИЕ: Если роль .child и возрастная группа .teen, преобразуем в .teenager
            cardRole = ageGroup == .teen ? .teenager : .child
        case .teenager:
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Роль .teenager всегда преобразуется в .teenager
            cardRole = .teenager
            print("✅ Подросток: роль .teenager преобразована в cardRole .teenager")
        case .elderly:
            cardRole = .elderly
        }
        
        print("🔍 saveJoinedMemberAsFamilyMember: cardRole=\(cardRole)")
        VisualLogger.shared.log("🔍 saveJoinedMemberAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)", level: .info, category: "FAMILY")
        
        // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ ПОДРОСТКА
        if role == .teenager {
            print("✅ ПОДРОСТОК: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)")
            VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)", level: .success, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole)")
            if cardRole != .teenager {
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: cardRole не соответствует .teenager!")
                VisualLogger.shared.log("❌ КРИТИЧЕСКАЯ ОШИБКА (JOINED): cardRole не соответствует .teenager!", level: .error, category: "FAMILY")
                MasterLogger.shared.log(.error, category: .business, message: "❌ КРИТИЧЕСКАЯ ОШИБКА (JOINED): cardRole не соответствует .teenager!")
            }
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
            VisualLogger.shared.log("✅ (JOINED) Загружено \(existingMembers.count) существующих участников из UserDefaults", level: .info, category: "FAMILY")
        } else {
            VisualLogger.shared.log("⚠️ (JOINED) Не удалось загрузить существующих участников из UserDefaults", level: .warning, category: "FAMILY")
        }
        
        // Проверяем, нет ли уже такого участника (по имени и роли)
        let isDuplicate = existingMembers.contains { existingMember in
            existingMember.name == userName && existingMember.role == cardRole
        }
        
        if role == .teenager {
            VisualLogger.shared.log("🔍 ПОДРОСТОК (JOINED): Проверка дубликатов - userName=\(userName), cardRole=\(cardRole), isDuplicate=\(isDuplicate)", level: .info, category: "FAMILY")
            MasterLogger.shared.log(.info, category: .business, message: "🔍 ПОДРОСТОК (JOINED): Проверка дубликатов - userName=\(userName), cardRole=\(cardRole), isDuplicate=\(isDuplicate)")
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
            
            if role == .teenager {
                VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Новый участник создан - name=\(userName), role=\(cardRole.rawValue)", level: .success, category: "FAMILY")
                MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): Новый участник создан - name=\(userName), role=\(cardRole.rawValue)")
            }
            
            // Сохраняем обновленный список
            if let encoded = try? JSONEncoder().encode(existingMembers) {
                UserDefaults.standard.set(encoded, forKey: "family_members_list")
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация UserDefaults
                UserDefaults.standard.synchronize()
                print("✅ Присоединившийся участник добавлен к списку: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                if role == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Сохранено в UserDefaults - всего участников: \(existingMembers.count)", level: .success, category: "FAMILY")
                    MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): Сохранено в UserDefaults - всего участников: \(existingMembers.count)")
                    
                    // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Проверяем что подросток действительно сохранен
                    if let verifyData = UserDefaults.standard.data(forKey: "family_members_list"),
                       let verifyDecoded = try? JSONDecoder().decode([FamilyMemberData].self, from: verifyData) {
                        let teenagerFound = verifyDecoded.contains { $0.role == .teenager && $0.name == userName }
                        if teenagerFound {
                            VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Подтверждено сохранение в UserDefaults!", level: .success, category: "FAMILY")
                            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): Подтверждено сохранение в UserDefaults!")
                        } else {
                            VisualLogger.shared.log("❌ ПОДРОСТОК (JOINED): ОШИБКА - подросток НЕ найден после сохранения!", level: .error, category: "FAMILY")
                            MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК (JOINED): ОШИБКА - подросток НЕ найден после сохранения!")
                        }
                    }
                }
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
                NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
                
                if role == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Отправлены уведомления об обновлении", level: .success, category: "FAMILY")
                }
            } else {
                print("❌ Ошибка кодирования списка участников")
                if role == .teenager {
                    VisualLogger.shared.log("❌ ПОДРОСТОК (JOINED): ОШИБКА кодирования списка участников!", level: .error, category: "FAMILY")
                    MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК (JOINED): ОШИБКА кодирования списка участников!")
                }
            }
        } else {
            print("⚠️ Участник уже существует: \(userName) (\(cardRole)), не добавляем дубликат")
            if role == .teenager {
                VisualLogger.shared.log("⚠️ ПОДРОСТОК (JOINED): Участник уже существует (дубликат)", level: .warning, category: "FAMILY")
                MasterLogger.shared.log(.warn, category: .business, message: "⚠️ ПОДРОСТОК (JOINED): Участник уже существует (дубликат)")
            }
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

