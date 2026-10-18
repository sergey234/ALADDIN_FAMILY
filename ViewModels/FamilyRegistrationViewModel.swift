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

enum FamilyInviteCodeParser {
    struct Payload: Equatable {
        let familyId: String
        let displayCode: String
        let inviteToken: String?
    }

    private struct QRPayload: Decodable {
        let type: String?
        let family_id: String?
        let familyId: String?
        let invite_token: String?
        let inviteToken: String?
        let code: String?
    }

    static func parse(_ raw: String) -> Payload? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        if let data = trimmed.data(using: .utf8),
           let qr = try? JSONDecoder().decode(QRPayload.self, from: data),
           qr.type == nil || qr.type == "family_registration" {
            let rawFamilyId = qr.family_id ?? qr.familyId ?? qr.code
            guard let payload = parseFamilyId(rawFamilyId) else { return nil }
            let token = (qr.invite_token ?? qr.inviteToken)?
                .trimmingCharacters(in: .whitespacesAndNewlines)
            return Payload(
                familyId: payload.familyId,
                displayCode: payload.displayCode,
                inviteToken: token?.isEmpty == false ? token : nil
            )
        }

        if let url = URL(string: trimmed), url.scheme != nil {
            guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else { return nil }
            let query = components.queryItems ?? []
            let host = components.host?.lowercased()
            let pathParts = components.path.split(separator: "/").map(String.init)
            let pathCode: String?
            if pathParts.count >= 3,
               pathParts[0].lowercased() == "family",
               pathParts[1].lowercased() == "invite" {
                pathCode = pathParts[2]
            } else if host == "family",
                      pathParts.count >= 2,
                      pathParts[0].lowercased() == "invite" {
                pathCode = pathParts[1]
            } else if host == "invite",
                      pathParts.count >= 1,
                      pathParts[0].uppercased().hasPrefix("FAM") {
                pathCode = pathParts[0]
            } else if pathParts.count >= 2,
                      pathParts[0].lowercased() == "invite",
                      pathParts[1].uppercased().hasPrefix("FAM") {
                pathCode = pathParts[1]
            } else {
                pathCode = nil
            }
            let rawFamilyId = query.first(where: { ["family_id", "familyId", "code"].contains($0.name) })?.value ?? pathCode
            guard let payload = parseFamilyId(rawFamilyId) else { return nil }
            let token = query.first(where: { ["invite_token", "inviteToken"].contains($0.name) })?.value?
                .trimmingCharacters(in: .whitespacesAndNewlines)
            return Payload(
                familyId: payload.familyId,
                displayCode: payload.displayCode,
                inviteToken: token?.isEmpty == false ? token : nil
            )
        }

        return parseFamilyId(trimmed)
    }

    static func displayCode(fromFamilyId familyId: String) -> String? {
        parseFamilyId(familyId)?.displayCode
    }

    static func inviteCodeForDisplay(fromScannedString raw: String) -> String? {
        parse(raw)?.displayCode
    }

    private static func parseFamilyId(_ raw: String?) -> Payload? {
        guard let raw else { return nil }
        let alnum = raw
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .uppercased()
            .filter { $0.isLetter || $0.isNumber }

        guard alnum.hasPrefix("FAM") else { return nil }
        let body = String(alnum.dropFirst(3).prefix(12))
        guard body.count == 12, body.allSatisfy({ $0.isLetter || $0.isNumber }) else { return nil }

        let familyId = "FAM_\(body)"
        let first = String(body.prefix(4))
        let second = String(body.dropFirst(4).prefix(4))
        let third = String(body.dropFirst(8).prefix(4))
        return Payload(familyId: familyId, displayCode: "FAM-\(first)-\(second)-\(third)", inviteToken: nil)
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

@MainActor
class FamilyRegistrationViewModel: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService: APIService

    init(apiService: APIService? = nil) {
        self.apiService = apiService ?? APIService.shared
    }
    
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
    @Published var familyInviteQRPayload: String?
    @Published var lastJoinedMemberId: String?
    @Published var familyMembers: [FamilyMember] = []
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    /// qa-16: drives Retry vs Tariffs CTA — never wipe family via Retry on limit/403.
    @Published var registrationErrorKind: RegistrationErrorKind = .none

    enum RegistrationErrorKind: Equatable {
        case none
        case tariffLimit
        case nonRetryable
        case networkRetryable
    }
    
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
    
    @MainActor func onLetterSelected(_ letter: String) {
        selectedLetter = letter
        showLetterModal = false
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #1: Сохраняем имя пользователя на основе выбранной буквы
        // Формируем имя: "Родитель A", "Ребенок B", "Подросток C", "Пожилой D" и т.д.
        if let role = selectedRole {
            let roleName: String
            switch role {
            case .parent: roleName = LocalizationManager.shared.localized("family_role_parent_label")
            case .child: roleName = LocalizationManager.shared.localized("family_role_child_label")
            case .teenager: roleName = LocalizationManager.shared.localized("family_role_teen_label")
            case .elderly: roleName = LocalizationManager.shared.localized("family_role_elderly_label")
            }
            let userName = "\(roleName) \(letter)"
            if !UserDefaults.standard.bool(forKey: "admin_add_mode") {
                UserDefaults.standard.set(userName, forKey: "current_user_name")
                UserDefaults.standard.synchronize()
                logger.business("✅ User name saved: \(userName)")
            } else {
                logger.business("🛡️ ADMIN-ADD: skipping current_user_name overwrite (\(userName))")
            }
        }
        
        // ✅ ИСПРАВЛЕНО: Убрана искусственная задержка, создание семьи происходит сразу
        createFamily()
    }
    
    // MARK: - Create Family
    
    @MainActor func createFamily() {
        logger.business("Creating family with role: \(selectedRole?.rawValue ?? "none")")
        
        // Сбрасываем admin_add_mode только если на устройстве ещё нет семьи (истинная первичная регистрация).
        // Если family_id уже есть, admin_add_mode означает «добавить участника в текущую семью» — не сбрасывать (иначе всегда уходит в family/create).
        let existingFamilyId = (FamilyLocalStore.loadPersistedFamilyId() ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let hasExistingFamilyOnDevice = !existingFamilyId.isEmpty
        let wasAdminAddMode = UserDefaults.standard.bool(forKey: "admin_add_mode")
        if wasAdminAddMode && !hasExistingFamilyOnDevice {
            logger.business("⚠️ ADMIN_ADD_MODE active but no family_id — resetting (avoid addMember 404 before family exists)")
            UserDefaults.standard.set(false, forKey: "admin_add_mode")
            UserDefaults.standard.synchronize()
            VisualLogger.shared.log("🔄 Reset admin_add_mode (no family on device)", level: .warning, category: "FAMILY")
        }
        
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
        if !UserDefaults.standard.bool(forKey: "admin_add_mode") {
            saveUserRole(role)
            logger.business("Family role saved: \(role.rawValue)")
            // ✅ ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ: Убеждаемся, что UserDefaults синхронизирован
            UserDefaults.standard.synchronize()
            logger.business("UserDefaults synchronized")
        } else {
            logger.business("🛡️ ADMIN-ADD: skipping family role save (\(role.rawValue))")
        }
        
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

        let userName: String
        let roleName: String
        switch role {
        case .parent: roleName = LocalizationManager.shared.localized("family_role_parent_label")
        case .child: roleName = LocalizationManager.shared.localized("family_role_child_label")
        case .teenager: roleName = LocalizationManager.shared.localized("family_role_teen_label")
        case .elderly: roleName = LocalizationManager.shared.localized("family_role_elderly_label")
        }
        userName = "\(roleName) \(letter)"

        // ✅ UPDATED: Uses single source SubscriptionManager.canAddFamilyMember (no more duplicate logic)
        // This unifies admin_add_mode with FamilyScreen and eliminates bypass.
        if UserDefaults.standard.bool(forKey: "admin_add_mode") {
            logger.business("========== ADDING MEMBER (admin-add mode) ==========")

            if FamilyLocalStore.isLikelyStaleFamilyContextForCurrentAccount() {
                logger.business("⚠️ ADMIN_ADD: stale family_id without roster identity — switching to createFamily()")
                VisualLogger.shared.log(
                    "🔄 Stale family_id on device (not your server family) — creating new family",
                    level: .warning,
                    category: "FAMILY"
                )
                UserDefaults.standard.set(false, forKey: "admin_add_mode")
                UserDefaults.standard.synchronize()
                FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                // Fall through to POST /api/family/create below.
            } else {
            
            // Load current family count for accurate check
            var currentCount = 1 // at least the creator
            if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
               let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
                currentCount = decoded.count
            }
            
            let (allowed, message, _) = SubscriptionManager.shared.canAddFamilyMember(currentCount: currentCount)
            if !allowed {
                let limit = SubscriptionManager.currentFamilyLimit
                logger.business("🚫 TARIFF LIMIT REACHED in admin_add_mode: \(currentCount)/\(limit)")
                VisualLogger.shared.log("🚫 TARIFF LIMIT: cannot add more members (\(currentCount)/\(limit))", level: .warning, category: "FAMILY")
                // Hybrid-B: prefer canAdd message with server used/max — never a lone inflated "3".
                self.errorMessage = message
                    ?? SubscriptionManager.shared.familyRosterLimitReachedUserMessage(
                        used: currentCount,
                        limit: limit
                    )
                self.registrationErrorKind = .tariffLimit
                self.isLoading = false
                self.currentStep = .idle
                UserDefaults.standard.set(false, forKey: "admin_add_mode")
                UserDefaults.standard.synchronize()
                return
            }
            
            Task {
                do {
                    let response = try await apiService.addFamilyMember(name: userName, role: role.serverValue)
                    
                    await MainActor.run {
                        self.isLoading = false
                        
                        // Сохраняем добавленного участника локально
                        self.saveCreatorAsFamilyMember(
                            role: role,
                            ageGroup: ageGroup,
                            serverMemberId: response.id,
                            explicitName: userName
                        )

                        let newMemberId = response.id.trimmingCharacters(in: .whitespacesAndNewlines)
                        if !newMemberId.isEmpty {
                            UserDefaults.standard.set(newMemberId, forKey: FamilyLocalStore.pendingPostAdminAddDeviceMemberIdKey)
                            UserDefaults.standard.set(userName, forKey: FamilyLocalStore.pendingPostAdminAddDeviceMemberNameKey)
                            UserDefaults.standard.synchronize()
                        }
                        
                        // Сброс флага
                        UserDefaults.standard.set(false, forKey: "admin_add_mode")
                        UserDefaults.standard.synchronize()
                        
                        // Завершаем процесс
                        self.currentStep = .completed
                        self.showSuccessModal = true
                    }
                } catch {
                    await MainActor.run {
                        self.isLoading = false
                        
                        let errorDesc = error.localizedDescription.lowercased()
                        logger.business("❌ addFamilyMember failed: \(error.localizedDescription)")
                        
                        // qa-16: NEVER auto-createFamily on add failure when family already exists /
                        // limit / forbidden — that wiped the old member on Retry.
                        if Self.isFamilyMemberLimitError(error) {
                            // Hybrid-B: keep API/server capacity text (used/max), do not remap to lone local "3".
                            let apiText = error.localizedDescription.trimmingCharacters(in: .whitespacesAndNewlines)
                            self.errorMessage = apiText.isEmpty
                                ? SubscriptionManager.shared.familyRosterLimitReachedUserMessage()
                                : apiText
                            self.registrationErrorKind = .tariffLimit
                            UserDefaults.standard.set(false, forKey: "admin_add_mode")
                            UserDefaults.standard.synchronize()
                            self.currentStep = .idle
                            VisualLogger.shared.log("🚫 FAMILY_ADD tariff limit — no createFamily fallback", level: .warning, category: "FAMILY")
                            return
                        }

                        let isStaleFamilyContext = errorDesc.contains("family_context_stale")
                        let isForbiddenAdminAdd = errorDesc.contains("only administrators")
                            || errorDesc.contains("forbidden")
                            || errorDesc.contains("доступ запрещен")
                            || errorDesc.contains("403")
                        // Soft recovery only when device has NO confirmed family (true first registration).
                        let canFallbackCreate = FamilyLocalStore.needsServerFamilyCreation()
                        if canFallbackCreate,
                           (errorDesc.contains("family not found") || errorDesc.contains("404") || errorDesc.contains("not found")
                            || isStaleFamilyContext) {
                            VisualLogger.shared.log("🔄 FAMILY_ADD no local family → createFamily()", level: .warning, category: "FAMILY")
                            UserDefaults.standard.set(false, forKey: "admin_add_mode")
                            UserDefaults.standard.synchronize()
                            self.currentStep = .idle
                            Task { @MainActor [weak self] in
                                try? await Task.sleep(nanoseconds: 500_000_000)
                                self?.createFamily()
                            }
                            return
                        }

                        if isForbiddenAdminAdd || isStaleFamilyContext {
                            self.errorMessage = LocalizationManager.shared.localized("family_add_forbidden_or_stale")
                            self.registrationErrorKind = .nonRetryable
                            UserDefaults.standard.set(false, forKey: "admin_add_mode")
                            UserDefaults.standard.synchronize()
                            self.currentStep = .idle
                            VisualLogger.shared.log("❌ FAMILY_ADD forbidden/stale — no createFamily wipe", level: .error, category: "FAMILY")
                            return
                        }

                        self.errorMessage = Self.userFacingFamilyErrorMessage(from: error)
                        self.registrationErrorKind = .networkRetryable
                        self.currentStep = .idle
                        VisualLogger.shared.log("❌ Ошибка добавления участника: \(error.localizedDescription)", level: .error, category: "FAMILY")
                    }
                }
            }
            return
            }
        }

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
                    self?.familyInviteQRPayload = response.qr_code_data

                    FamilyLocalStore.resetPersistedCachesIfFamilyChanged(newFamilyId: response.family_id)
                    FamilyLocalStore.persistFamilyId(response.family_id)
                    FamilyLocalStore.persistFamilyCreatorMemberId(response.creator_member_id)

                    // ✅ BUILD 115: Сохраняем your_member_id с диагностикой
                    // ✅ КРЕПОСТЬ 2.1: Асинхронный разрыв - UserDefaults.set в async для предотвращения рекурсии
                    let memberIdToSave = response.your_member_id
                    DispatchQueue.main.async {
                        // В admin-add режиме НЕ меняем your_member_id (оставляем сессию родителя)
                        if !UserDefaults.standard.bool(forKey: "admin_add_mode") {
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
                        } else {
                            logger.business("🛡️ ADMIN-ADD: skipping your_member_id overwrite (keep parent)")
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
                        self?.saveCreatorAsFamilyMember(
                            role: role,
                            ageGroup: ageGroup,
                            serverMemberId: response.your_member_id,
                            explicitName: userName
                        )
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
                        self?.errorMessage = LocalizationManager.shared.localized("family_session_expired")
                        self?.registrationErrorKind = .nonRetryable
                        VisualLogger.shared.log("⚠️ FAMILY CREATE unauthorized/session-expired", level: .warning, category: "FAMILY")
                    default:
                        if Self.isFamilyMemberLimitError(error) {
                            let apiText = error.localizedDescription.trimmingCharacters(in: .whitespacesAndNewlines)
                            self?.errorMessage = apiText.isEmpty
                                ? SubscriptionManager.shared.familyRosterLimitReachedUserMessage()
                                : apiText
                            self?.registrationErrorKind = .tariffLimit
                        } else {
                            self?.errorMessage = Self.userFacingFamilyErrorMessage(from: error)
                            self?.registrationErrorKind = .networkRetryable
                        }
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
        // Если это поток admin-add (родитель добавляет другого участника), не трогаем текущую сессию
        if UserDefaults.standard.bool(forKey: "admin_add_mode") {
            #if DEBUG
            VisualLogger.shared.log("🛡️ ADMIN-ADD: skipping saveTokens to keep parent session", level: .info, category: "AUTH")
            #endif
            return true
        }
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
        FamilyLocalStore.reconcileFamilyContextWithCurrentJWT()
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
            errorMessage = LocalizationManager.shared.localized("invitation_join_profile_required")
            return
        }

        guard let invitePayload = FamilyInviteCodeParser.parse(code) else {
            errorMessage = LocalizationManager.shared.localized("invitation_invalid_code")
            return
        }

        joinFamilySanitized(with: invitePayload, role: role, ageGroup: ageGroup, letter: letter)
    }

    private func joinFamilySanitized(with invitePayload: FamilyInviteCodeParser.Payload, role: FamilyRole, ageGroup: AgeGroup, letter: String) {
        isLoading = true

        let request = JoinFamilyRequest(
            family_id: invitePayload.familyId,
            invite_code: invitePayload.displayCode,
            invite_token: invitePayload.inviteToken,
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
                    self?.lastJoinedMemberId = data.your_member_id

                    FamilyLocalStore.resetPersistedCachesIfFamilyChanged(newFamilyId: data.family_id)
                    FamilyLocalStore.persistFamilyId(data.family_id)
                    
                    // ✅ BUILD 115: Сохраняем your_member_id с диагностикой
                    // ✅ КРЕПОСТЬ 2.1: Асинхронный разрыв - UserDefaults.set в async для предотвращения рекурсии
                    let memberIdToSave = data.your_member_id
                    DispatchQueue.main.async {
                        if !UserDefaults.standard.bool(forKey: "admin_add_mode") {
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
                        } else {
                            logger.business("🛡️ ADMIN-ADD: skipping your_member_id overwrite on join (keep parent)")
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
                    self?.saveJoinedMemberAsFamilyMember(
                        role: role,
                        ageGroup: ageGroup,
                        serverMemberId: data.your_member_id
                    )
                    
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
                        guard let recoveredFamilyId = response.familyId, !recoveredFamilyId.isEmpty else {
                            self?.errorMessage = "Не удалось определить family_id после восстановления"
                            NotificationCenter.default.post(
                                name: NSNotification.Name("FamilyRecoveryError"),
                                object: nil,
                                userInfo: ["error": self?.errorMessage ?? "missing family_id"]
                            )
                            return
                        }

                        // Сохраняем family_id
                        self?.familyID = recoveredFamilyId
                        FamilyLocalStore.resetPersistedCachesIfFamilyChanged(newFamilyId: recoveredFamilyId)
                        FamilyLocalStore.persistFamilyId(recoveredFamilyId)
                        UserDefaults.standard.synchronize()

                        // Критично для защищенных family endpoints:
                        // после recover поднимаем JWT через login-by-recovery-code,
                        // иначе следующий вызов /api/family/* может получить 403.
                        self?.apiService.loginByRecoveryCode(
                            familyID: recoveredFamilyId,
                            recoveryCode: recoveredFamilyId
                        ) { loginResult in
                            DispatchQueue.main.async {
                                switch loginResult {
                                case .success(let loginResponse):
                                    let _ = self?.saveTokens(
                                        accessToken: loginResponse.access_token,
                                        refreshToken: loginResponse.refresh_token
                                    )
                                case .failure(let loginError):
                                    // Не блокируем recover flow, но явно логируем отсутствие токена.
                                    logger.business("⚠️ recoverAccess: login-by-recovery-code failed: \(loginError.localizedDescription)")
                                }
                            }
                        }
                        
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
    private func saveCreatorAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup, serverMemberId: String? = nil, explicitName: String? = nil) {
        // Получаем имя пользователя из явного параметра, иначе из UserDefaults или используем дефолтное
        let userName = explicitName ?? UserDefaults.standard.string(forKey: "current_user_name") ?? "Вы"
        
        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ПОДРОСТКА: Добавляем логирование для отладки
        print("🔍 saveCreatorAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), userName=\(userName)")
        
        // Загружаем существующий список участников ПЕРЕД проверкой isFirstUser
        var existingMembers: [FamilyMemberData] = []
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            existingMembers = decoded
        }
        
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ДЛЯ ПРОДА: Первый пользователь ВСЕГДА .parent
        let isFirstUser = existingMembers.isEmpty || 
                         !UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        
        // Преобразуем FamilyRole в FamilyMemberCard.FamilyRole
        let cardRole: FamilyMemberCard.FamilyRole
        if isFirstUser {
            cardRole = .parent
            print("👑 FIRST USER FORCED TO PARENT: \(userName) (was \(role.rawValue))")
            VisualLogger.shared.log("👑 FIRST USER FORCED TO .parent: \(userName) (original role: \(role.rawValue))", level: .success, category: "FAMILY")
        } else {
            switch role {
            case .parent:
                cardRole = .parent
            case .child:
                cardRole = ageGroup == .teen ? .teenager : .child
            case .teenager:
                cardRole = .teenager
                print("✅ Подросток: роль .teenager преобразована в cardRole .teenager")
            case .elderly:
                cardRole = .elderly
            }
        }
        
        print("🔍 saveCreatorAsFamilyMember: cardRole=\(cardRole) (isFirstUser=\(isFirstUser))")
        VisualLogger.shared.log("🔍 saveCreatorAsFamilyMember: role=\(role.rawValue), ageGroup=\(ageGroup.rawValue), cardRole=\(cardRole) (isFirstUser=\(isFirstUser))", level: .info, category: "FAMILY")
        
        // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ ПОДРОСТКА
        if role == .teenager && !isFirstUser {
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
        
        // Загрузка existingMembers уже выполнена выше (для isFirstUser). Пропускаем дублирование.
        // existingMembers уже содержит актуальный список
        
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
            let serverId = serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines)
            let newMember = FamilyMemberData(
                id: (serverId?.isEmpty == false ? serverId! : UUID().uuidString),
                serverMemberId: (serverId?.isEmpty == false ? serverId : nil),
                localOnly: (serverId?.isEmpty != false), // true если нет serverId
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
                let fid = (FamilyLocalStore.loadPersistedFamilyId() ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                FamilyLocalStore.persistRosterSnapshotFamilyId(fid)
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация UserDefaults
                UserDefaults.standard.synchronize()
                print("✅ Создатель семьи добавлен к списку участников: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                if cardRole == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК: Сохранено в UserDefaults - всего участников: \(existingMembers.count)", level: .success, category: "FAMILY")
                    MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Сохранено в UserDefaults - всего участников: \(existingMembers.count)")
                    
                    // Проверяем, что в ростере сохранена та же роль карточки (важно для .child + возраст .teen → cardRole .teenager).
                    if let verifyData = UserDefaults.standard.data(forKey: "family_members_list"),
                       let verifyDecoded = try? JSONDecoder().decode([FamilyMemberData].self, from: verifyData) {
                        let saved = verifyDecoded.contains { $0.role == cardRole && $0.name == userName }
                        if saved {
                            VisualLogger.shared.log("✅ ПОДРОСТОК: Подтверждено сохранение в UserDefaults!", level: .success, category: "FAMILY")
                            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК: Подтверждено сохранение в UserDefaults!")
                        } else {
                            VisualLogger.shared.log("❌ ПОДРОСТОК: ОШИБКА - участник с ролью \(cardRole.rawValue) НЕ найден после сохранения!", level: .error, category: "FAMILY")
                            MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК: ОШИБКА - участник с ролью \(cardRole.rawValue) НЕ найден после сохранения!")
                        }
                    }
                }
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
                FamilyLocalStore.notifyFamilyMembersUpdated()
                
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
    private func saveJoinedMemberAsFamilyMember(role: FamilyRole, ageGroup: AgeGroup, serverMemberId: String? = nil) {
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
            let serverId = serverMemberId?.trimmingCharacters(in: .whitespacesAndNewlines)
            let newMember = FamilyMemberData(
                id: (serverId?.isEmpty == false ? serverId! : UUID().uuidString),
                serverMemberId: (serverId?.isEmpty == false ? serverId : nil),
            localOnly: (serverId?.isEmpty != false),
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
                let fid = (FamilyLocalStore.loadPersistedFamilyId() ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                FamilyLocalStore.persistRosterSnapshotFamilyId(fid)
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация UserDefaults
                UserDefaults.standard.synchronize()
                print("✅ Присоединившийся участник добавлен к списку: \(userName) (\(cardRole)). Всего участников: \(existingMembers.count)")
                
                if cardRole == .teenager {
                    VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Сохранено в UserDefaults - всего участников: \(existingMembers.count)", level: .success, category: "FAMILY")
                    MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): Сохранено в UserDefaults - всего участников: \(existingMembers.count)")
                    
                    if let verifyData = UserDefaults.standard.data(forKey: "family_members_list"),
                       let verifyDecoded = try? JSONDecoder().decode([FamilyMemberData].self, from: verifyData) {
                        let saved = verifyDecoded.contains { $0.role == cardRole && $0.name == userName }
                        if saved {
                            VisualLogger.shared.log("✅ ПОДРОСТОК (JOINED): Подтверждено сохранение в UserDefaults!", level: .success, category: "FAMILY")
                            MasterLogger.shared.log(.info, category: .business, message: "✅ ПОДРОСТОК (JOINED): Подтверждено сохранение в UserDefaults!")
                        } else {
                            VisualLogger.shared.log("❌ ПОДРОСТОК (JOINED): ОШИБКА - участник с ролью \(cardRole.rawValue) НЕ найден после сохранения!", level: .error, category: "FAMILY")
                            MasterLogger.shared.log(.error, category: .business, message: "❌ ПОДРОСТОК (JOINED): ОШИБКА - участник с ролью \(cardRole.rawValue) НЕ найден после сохранения!")
                        }
                    }
                }
                
                // Уведомляем другие экраны об изменении
                NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
                FamilyLocalStore.notifyFamilyMembersUpdated()
                
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

    private static func userFacingFamilyErrorMessage(from error: Error) -> String {
        switch NetworkError.from(error) {
        case .serviceUnavailable(let message):
            return message ?? LocalizationManager.shared.localized("family_service_temporarily_unavailable")
        case .endpointFeatureUnavailable:
            return LocalizationManager.shared.localized("family_service_unavailable_deploy")
        default:
            let raw = error.localizedDescription
            // Never surface raw English server jargon for limit/forbidden.
            if isFamilyMemberLimitError(error) {
                let apiText = raw.trimmingCharacters(in: .whitespacesAndNewlines)
                if !apiText.isEmpty, apiText.lowercased().contains("/") || apiText.lowercased().contains("сервер") || apiText.lowercased().contains("server") {
                    return apiText
                }
                return SubscriptionManager.shared.familyRosterLimitReachedUserMessage()
            }
            return raw
        }
    }

    /// Server/client signals that the tariff roster cap was hit (never createFamily).
    static func isFamilyMemberLimitError(_ error: Error) -> Bool {
        let desc = error.localizedDescription.lowercased()
        if desc.contains("лимит участников")
            || desc.contains("member limit")
            || desc.contains("limit reached")
            || desc.contains("достигнут лимит")
            || desc.contains("обновите тариф")
            || desc.contains("upgrade your plan")
            || desc.contains("upgrade your subscription")
            || desc.contains("family_roster_full")
            || desc.contains("roster_full")
            || desc.contains("max_slots")
            || desc.contains("no slots")
            || desc.contains("0 slots") {
            return true
        }
        switch NetworkError.from(error) {
        case .badRequest(let msg), .forbidden(let msg), .conflict(let msg):
            let m = (msg ?? "").lowercased()
            return m.contains("limit") || m.contains("лимит") || m.contains("roster") || m.contains("slots")
        case .httpError(let code) where code == 409 || code == 402:
            return desc.contains("limit") || desc.contains("лимит") || desc.contains("roster") || desc.contains("slots")
        default:
            return false
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
    let invite_code: String?
    let invite_token: String?
    let role: String
    let age_group: String
    let personal_letter: String
    let device_type: String
}

struct FamilyInviteCreateRequest: Codable {
    let family_id: String?
}

struct FamilyInvitePreflightRequest: Codable {
    let family_id: String
    let invite_code: String?
    let invite_token: String?
}

struct FamilyInviteResponse: Codable {
    let success: Bool
    let family_id: String
    let invite_code: String
    let invite_token: String
    let expires_at: String
    let qr_code_data: String
    let message: String?
    let error: String?
}

struct FamilyInvitePreflightResponse: Codable {
    let success: Bool
    let family_id: String
    let invite_code: String
    let expires_at: String
    let can_join: Bool
    let message: String?
    let error: String?
}



// MARK: - Network Manager Extension

extension NetworkManager {
    
    func createFamily(request: CreateFamilyRequest, completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void) {
        post(endpoint: AppConfig.Endpoint.createFamily, body: request, requiresAuth: true, completion: completion)
    }
    
    func joinFamily(request: JoinFamilyRequest, completion: @escaping (Result<JoinFamilyResponse, Error>) -> Void) {
        post(endpoint: AppConfig.Endpoint.joinFamily, body: request, requiresAuth: true, completion: completion)
    }

    func preflightFamilyInvite(
        request: FamilyInvitePreflightRequest,
        completion: @escaping (Result<FamilyInvitePreflightResponse, Error>) -> Void
    ) {
        post(endpoint: AppConfig.Endpoint.familyInvitePreflight, body: request, requiresAuth: false, completion: completion)
    }
    
    func recoverFamily(familyID: String, completion: @escaping (Result<RecoverFamilyResponse, Error>) -> Void) {
        get(endpoint: "\(AppConfig.Endpoint.recoverFamily)/\(familyID)", requiresAuth: true, completion: completion)
    }
}

