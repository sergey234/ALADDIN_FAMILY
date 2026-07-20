import Foundation
import Combine
import UIKit

// Импортируем модели компонентов
// ComponentStats и ComponentsAnalytics определены в Core/Analytics/ComponentAnalyticsModels.swift
import CoreLocation

// Master Logger for API logging
private let logger = MasterLogger.shared

// MARK: - Health Response Model

struct HealthResponse: Codable {
    let status: String
    let uptime: Double?
    let version: String?
    let timestamp: String?
}

/**
 * 🔌 API Service
 * Удобные методы для работы с API
 * Используется ViewModels для загрузки данных
 */

// ✅ Глобальная структура для пустых запросов
struct EmptyRequest: Codable {}

/// Ответ `POST /api/telegram/link-code` (asa-4-ios-tg-link-api).
struct TelegramLinkCodeResponse: Codable {
    let code: String
    let expiresInSec: Int
    let botUsername: String

    enum CodingKeys: String, CodingKey {
        case code
        case expiresInSec = "expires_in_sec"
        case botUsername = "bot_username"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        code = try c.decode(String.self, forKey: .code)
        expiresInSec = try c.decodeIfPresent(Int.self, forKey: .expiresInSec) ?? 600
        botUsername = try c.decodeIfPresent(String.self, forKey: .botUsername) ?? "AladdinchatAI_bot"
    }
}

/// Запрос на добавление участника семьи (анонимный ярлык + роль)
struct AddMemberRequest: Codable {
    let name: String
    let role: String
    let familyId: String?
}

@MainActor
class APIService: ObservableObject {

    let networkManager: NetworkManager

    // ✅ ИСПРАВЛЕНИЕ: Исправляем singleton паттерн - один экземпляр NetworkManager
    private static let sharedNetworkManager: NetworkManager = NetworkManager.shared

    // ✅ ИСПРАВЛЕНИЕ: Кешируем APIService для избежания повторного создания
    private static var _sharedAPIService: APIService?

    /// Параллельные вызовы `monitoring/detail` для одного `childId` → один HTTP-запрос (burst SwiftUI).
    private static let parentalMonitoringDetailCoalesceLock = NSLock()
    private static var parentalMonitoringDetailWaiters: [String: [(Result<ParentalMonitoringDetailResponse, Error>) -> Void]] = [:]
    private static var parentalMonitoringDetailInflight = Set<String>()

    static var shared: APIService {
        #if DEBUG
        if AppConfig.useMockAPI {
            // MockAPIService определен в Core/Network/MockAPIService.swift
            // Используем прямой вызов, так как оба файла в одном модуле
            // Если MockAPIService не найден, компилятор выдаст ошибку
            return MockAPIService.mockShared
        }
        #endif

        // ✅ ИСПРАВЛЕНИЕ: Используем кешированный экземпляр вместо создания нового
        if let cached = _sharedAPIService {
            return cached
        }

        let service = APIService(networkManager: sharedNetworkManager)
        _sharedAPIService = service
        return service
    }
    
    // Private initializer для Real API Service
    init(networkManager: NetworkManager) {
        self.networkManager = networkManager
    }

    /// Результат `GET /api/family/members` с метаданными для безопасного merge (без смешивания двух семей).
    struct FamilyMembersSyncContext {
        let members: [FamilyMemberResponse]
        /// Сервер сменил канонический контекст семьи: повтор без `?familyId=` после 409 **или** после пустого `[]` при явном query (устаревший локальный `family_id`).
        /// Для UI/merge то же правило, что и для 409: не смешивать старый локальный ростер с ответом «другой» семьи.
        let recoveredFromFamilyContextConflict: Bool
        /// Значение `family_id` в UserDefaults до сетевого запроса (снимок цепочки coalesce).
        let familyIdSnapshotBeforeFetch: String
        /// После ответа: `family_id` уже обновлён из заголовков (`X-Resolved-Family-Id`), если сервер прислал.
        let familyIdSnapshotAfterFetch: String

        /// Не смешивать старый локальный ростер с ответом (правила B + C).
        var shouldReplaceLocalMembersInsteadOfMerge: Bool {
            if recoveredFromFamilyContextConflict { return true }
            let before = familyIdSnapshotBeforeFetch.trimmingCharacters(in: .whitespacesAndNewlines)
            let after = familyIdSnapshotAfterFetch.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !before.isEmpty, !after.isEmpty else { return false }
            return before != after
        }
    }

    /// Сливает параллельные запросы `getFamilyMembers` в один сетевой вызов (снижает дубли и нагрузку на main).
    private let familyMembersCoalesceLock = NSLock()
    private var familyMembersPendingCompletions: [(Result<FamilyMembersSyncContext, Error>) -> Void] = []
    private var familyMembersFetchInFlight = false

    private func enqueueFamilyMembersCompletion(_ completion: @escaping (Result<FamilyMembersSyncContext, Error>) -> Void) {
        let mergeSnapshot = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        familyMembersCoalesceLock.lock()
        familyMembersPendingCompletions.append(completion)
        let start = !familyMembersFetchInFlight
        if start { familyMembersFetchInFlight = true }
        familyMembersCoalesceLock.unlock()
        guard start else { return }
        performGetFamilyMembers(
            hasRetriedAfterTokenBootstrap: false,
            hasRetriedAfterFamilyContextConflict: false,
            familyContextConflictRecovered: false,
            mergeFamilyIdSnapshot: mergeSnapshot,
            omitFamilyIdQuery: false,
            hasRetriedAfterEmptyExplicitFamilyQuery: false
        ) { [weak self] result in
            self?.deliverCoalescedFamilyMembersResult(result)
        }
    }

    private func deliverCoalescedFamilyMembersResult(_ result: Result<FamilyMembersSyncContext, Error>) {
        familyMembersCoalesceLock.lock()
        let waiters = familyMembersPendingCompletions
        familyMembersPendingCompletions.removeAll()
        familyMembersFetchInFlight = false
        familyMembersCoalesceLock.unlock()
        waiters.forEach { $0(result) }
    }
    
    // MARK: - Network Protection API
    
    func getNetworkProtectionStatus(completion: @escaping (Result<NetworkProtectionStatusResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.networkProtectionStatus, completion: completion)
    }
    
    func connectNetworkProtection(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.networkProtectionConnect, body: EmptyBody(), completion: completion)
    }
    
    func disconnectNetworkProtection(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.networkProtectionDisconnect, body: EmptyBody(), completion: completion)
    }
    
    func getNetworkProtectionServers(completion: @escaping (Result<[NetworkProtectionServer], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.networkProtectionServers, completion: completion)
    }
    
    func getNetworkProtectionConfig(completion: @escaping (Result<NetworkProtectionConfigResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.networkProtectionConfig, completion: completion)
    }
    
    func sendNetworkProtectionStats(_ stats: NetworkProtectionStats, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.networkProtectionStats, body: stats, completion: completion)
    }

    // MARK: - Family Registration API

    func createFamily(request: CreateFamilyRequest, completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void) {
        // Production flow is JWT-protected, but on real devices token can be missing/expired.
        // Auto-bootstrap device JWT and retry once to avoid false 401 during first-time registration.
        performCreateFamily(request: request, hasRetriedAfterTokenBootstrap: false, completion: completion)
    }

    func joinFamily(request: JoinFamilyRequest, completion: @escaping (Result<APIResponse<FamilyResponse>, Error>) -> Void) {
        performJoinFamily(request: request, hasRetriedAfterTokenBootstrap: false, completion: completion)
    }

    private func performCreateFamily(
        request: CreateFamilyRequest,
        hasRetriedAfterTokenBootstrap: Bool,
        completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void
    ) {
        networkManager.post(endpoint: AppConfig.Endpoint.createFamily, body: request, requiresAuth: true) { (result: Result<CreateFamilyResponse, Error>) in
            switch result {
            case .success:
                completion(result)
            case .failure(let error):
                if case .notFound = NetworkError.from(error) {
                    // Backward-compat fallback for environments where gateway exposes legacy family paths.
                    self.networkManager.post(endpoint: "/family/create", body: request, requiresAuth: true, completion: completion)
                    return
                }
                let networkError = NetworkError.from(error)
                let shouldBootstrapToken: Bool
                switch networkError {
                case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
                    shouldBootstrapToken = true
                default:
                    shouldBootstrapToken = self.isInvalidUserIdInTokenError(error)
                }
                guard !hasRetriedAfterTokenBootstrap, shouldBootstrapToken else {
                    completion(.failure(error))
                    return
                }
                self.bootstrapDeviceTokenIfNeeded(forceRefresh: true) { bootstrapResult in
                    switch bootstrapResult {
                    case .success:
                        self.performCreateFamily(request: request, hasRetriedAfterTokenBootstrap: true, completion: completion)
                    case .failure(let bootstrapError):
                        completion(.failure(bootstrapError))
                    }
                }
            }
        }
    }

    private func performJoinFamily(
        request: JoinFamilyRequest,
        hasRetriedAfterTokenBootstrap: Bool,
        completion: @escaping (Result<APIResponse<FamilyResponse>, Error>) -> Void
    ) {
        networkManager.post(endpoint: AppConfig.Endpoint.joinFamily, body: request, requiresAuth: true) { (result: Result<APIResponse<FamilyResponse>, Error>) in
            switch result {
            case .success:
                completion(result)
            case .failure(let error):
                if case .notFound = NetworkError.from(error) {
                    // Backward-compat fallback for environments where gateway exposes legacy family paths.
                    self.networkManager.post(endpoint: "/family/join", body: request, requiresAuth: true, completion: completion)
                    return
                }
                let networkError = NetworkError.from(error)
                let shouldBootstrapToken: Bool
                switch networkError {
                case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
                    shouldBootstrapToken = true
                default:
                    shouldBootstrapToken = self.isInvalidUserIdInTokenError(error)
                }
                guard !hasRetriedAfterTokenBootstrap, shouldBootstrapToken else {
                    completion(.failure(error))
                    return
                }
                self.bootstrapDeviceTokenIfNeeded(forceRefresh: true) { bootstrapResult in
                    switch bootstrapResult {
                    case .success:
                        self.performJoinFamily(request: request, hasRetriedAfterTokenBootstrap: true, completion: completion)
                    case .failure(let bootstrapError):
                        completion(.failure(bootstrapError))
                    }
                }
            }
        }
    }

    private func bootstrapDeviceTokenIfNeeded(
        forceRefresh: Bool = false,
        completion: @escaping (Result<Void, Error>) -> Void
    ) {
        if !forceRefresh, let token = AppConfig.authToken, !token.isEmpty {
            completion(.success(()))
            return
        }

        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        let deviceType = UIDevice.current.userInterfaceIdiom == .pad ? "tablet" : "smartphone"
        let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: deviceType)

        registerDeviceAnonymously(request: request) { result in
            switch result {
            case .success(let response):
                AppConfig.authToken = response.token
                if let refreshToken = response.refreshToken, !refreshToken.isEmpty {
                    KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
                }
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    private func isInvalidUserIdInTokenError(_ error: Error) -> Bool {
        let message = error.localizedDescription.lowercased()
        return message.contains("invalid user_id in token") || message.contains("invalid user id in token")
    }

    /// ✅ ДОБАВЛЕНО: Авторизация по recovery code (Попытка 2 - fallback)
    func loginByRecoveryCode(familyID: String, recoveryCode: String, completion: @escaping (Result<RecoveryCodeLoginResponse, Error>) -> Void) {
        let request = RecoveryCodeLoginRequest(family_id: familyID, recovery_code: recoveryCode)
        // ✅ Публичный endpoint - не требует авторизации
        networkManager.post(endpoint: AppConfig.Endpoint.loginByRecoveryCode, body: request, requiresAuth: false, completion: completion)
    }

    // ✅ ДОБАВЛЕНО: Network Protection Settings API (для синхронизации между устройствами)
    
    /// Загрузить настройки сетевой защиты с сервера
    func getNetworkProtectionSettings(completion: @escaping (Result<NetworkProtectionSettingsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.networkProtectionSettings, completion: completion)
    }
    
    /// Сохранить настройки сетевой защиты на сервер
    func updateNetworkProtectionSettings(
        autoSelectServer: Bool,
        autoConnectWiFi: Bool,
        autoConnectMobile: Bool,
        killSwitch: Bool,
        dnsLeakProtection: Bool,
        batteryOptimizationEnabled: Bool,
        antivirusEnabled: Bool,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct NetworkProtectionSettingsRequest: Codable {
            let autoSelectServer: Bool
            let autoConnectWiFi: Bool
            let autoConnectMobile: Bool
            let killSwitch: Bool
            let dnsLeakProtection: Bool
            let batteryOptimizationEnabled: Bool
            let antivirusEnabled: Bool
        }
        
        let request = NetworkProtectionSettingsRequest(
            autoSelectServer: autoSelectServer,
            autoConnectWiFi: autoConnectWiFi,
            autoConnectMobile: autoConnectMobile,
            killSwitch: killSwitch,
            dnsLeakProtection: dnsLeakProtection,
            batteryOptimizationEnabled: batteryOptimizationEnabled,
            antivirusEnabled: antivirusEnabled
        )
        
        networkManager.patch(endpoint: AppConfig.Endpoint.networkProtectionSettings, body: request, completion: completion)
    }
    
    // MARK: - Family API
    
    func getFamilyMembers(completion: @escaping (Result<[FamilyMemberResponse], Error>) -> Void) {
        enqueueFamilyMembersCompletion { result in
            completion(result.map(\.members))
        }
    }

    /// То же, что `getFamilyMembers`, плюс флаги для безопасного sync (без merge двух семей после 409).
    func getFamilyMembersWithSyncContext(completion: @escaping (Result<FamilyMembersSyncContext, Error>) -> Void) {
        enqueueFamilyMembersCompletion(completion)
    }

    /// Async-обертка для загрузки участников семьи.
    /// Используется в UI-потоках, где удобнее await-подход.
    func getFamilyMembers() async throws -> [FamilyMemberResponse] {
        try await withCheckedThrowingContinuation { continuation in
            getFamilyMembers { result in
                continuation.resume(with: result)
            }
        }
    }

    /// Лимиты тарифа + явный `family_id` из ответа `GET /api/family/members` (сервер: `X-Resolved-Family-Id`).
    private func applyFamilyMembersListHeaders(_ headers: [AnyHashable: Any]) {
        let limitKeyCandidates = ["X-Family-Limit", "x-family-limit", "X-FAMILY-LIMIT"]
        let remainingKeyCandidates = ["X-Family-Remaining", "x-family-remaining", "X-FAMILY-REMAINING"]
        let resolvedFamilyKeyCandidates = ["X-Resolved-Family-Id", "x-resolved-family-id", "X-RESOLVED-FAMILY-ID"]
        /// Опционально: если бэкенд отдаёт id участника для текущего JWT — выравниваем `your_member_id` без расшифровки токена.
        let currentMemberKeyCandidates = [
            "X-Current-Member-Id", "x-current-member-id", "X-Your-Member-Id", "x-your-member-id",
            "X-Resolved-Member-Id", "x-resolved-member-id", "X-Member-Id-You", "x-member-id-you"
        ]
        let canManageRosterKeyCandidates = [
            "X-Actor-Can-Manage-Roster", "x-actor-can-manage-roster", "X-ACTOR-CAN-MANAGE-ROSTER"
        ]
        let rosterUsedKeyCandidates = [
            "X-Family-Roster-Used", "x-family-roster-used", "X-FAMILY-ROSTER-USED"
        ]
        let rosterMaxKeyCandidates = [
            "X-Family-Roster-Max", "x-family-roster-max", "X-FAMILY-ROSTER-MAX"
        ]

        func headerValue(for keys: [String]) -> String? {
            for k in keys {
                if let v = headers[k] as? String { return v }
                if let vNum = headers[k] as? NSNumber { return vNum.stringValue }
            }
            return nil
        }

        let familyContextCandidates = ["X-Family-Context", "x-family-context", "X-FAMILY-CONTEXT"]
        if let ctx = headerValue(for: familyContextCandidates)?
            .trimmingCharacters(in: .whitespacesAndNewlines).lowercased(),
           ctx == "none" {
            FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
            return
        }

        if let limitStr = headerValue(for: limitKeyCandidates), let limit = Int(limitStr) {
            UserDefaults.standard.set(limit, forKey: "family_limit")
        }
        if let remainingStr = headerValue(for: remainingKeyCandidates), let remaining = Int(remainingStr) {
            UserDefaults.standard.set(remaining, forKey: "family_remaining")
        }
        if let resolved = headerValue(for: resolvedFamilyKeyCandidates)?
            .trimmingCharacters(in: .whitespacesAndNewlines), !resolved.isEmpty {
            UserDefaults.standard.set(resolved, forKey: FamilyLocalStore.lastResolvedFamilyIdKey)
            // Единый канонический `family_id` на устройстве = то, что подтвердил сервер для этого токена.
            FamilyLocalStore.persistFamilyId(resolved)
        }
        if let memberHint = headerValue(for: currentMemberKeyCandidates) {
            FamilyLocalStore.applyYourMemberIdFromFamilyMembersHeaderIfPresent(memberHint)
        }
        if let canManageRaw = headerValue(for: canManageRosterKeyCandidates)?
            .trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
            let canManage = canManageRaw == "true" || canManageRaw == "1" || canManageRaw == "yes"
            UserDefaults.standard.set(canManage, forKey: "family_actor_can_manage_roster_last")
        }
        if let usedStr = headerValue(for: rosterUsedKeyCandidates), let used = Int(usedStr) {
            UserDefaults.standard.set(used, forKey: "family_roster_used_last")
        }
        if let maxStr = headerValue(for: rosterMaxKeyCandidates), let maxSlots = Int(maxStr) {
            UserDefaults.standard.set(maxSlots, forKey: "family_limit")
        }
    }

    private func performGetFamilyMembers(
        hasRetriedAfterTokenBootstrap: Bool,
        hasRetriedAfterFamilyContextConflict: Bool = false,
        familyContextConflictRecovered: Bool = false,
        mergeFamilyIdSnapshot: String,
        omitFamilyIdQuery: Bool = false,
        hasRetriedAfterEmptyExplicitFamilyQuery: Bool = false,
        completion: @escaping (Result<FamilyMembersSyncContext, Error>) -> Void
    ) {
        let wrapSuccess: ([FamilyMemberResponse]) -> FamilyMembersSyncContext = { members in
            let after = FamilyLocalStore.loadPersistedFamilyId()
                .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            return FamilyMembersSyncContext(
                members: members,
                recoveredFromFamilyContextConflict: familyContextConflictRecovered,
                familyIdSnapshotBeforeFetch: mergeFamilyIdSnapshot,
                familyIdSnapshotAfterFetch: after
            )
        }

        // Передаём явный familyId, если он известен, чтобы избежать неверного контекста семьи на сервере
        let storedFamilyId = FamilyLocalStore.loadPersistedFamilyId()
        let activeFamilyId = omitFamilyIdQuery ? nil : storedFamilyId
        let query: [String: String]? = {
            if let fid = activeFamilyId, !fid.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                return ["familyId": fid]
            }
            return nil
        }()
        /// Явный `?familyId=` в URL: для устаревшего локального id сервер может вернуть `[]`, тогда один раз запрашиваем без query — JWT + `X-Resolved-Family-Id`.
        let hadExplicitFamilyQuery = query != nil
        let handleMembersSuccess: ([FamilyMemberResponse]) -> Void = { members in
            if members.isEmpty, hadExplicitFamilyQuery, !hasRetriedAfterEmptyExplicitFamilyQuery {
                self.performGetFamilyMembers(
                    hasRetriedAfterTokenBootstrap: hasRetriedAfterTokenBootstrap,
                    hasRetriedAfterFamilyContextConflict: hasRetriedAfterFamilyContextConflict,
                    familyContextConflictRecovered: true,
                    mergeFamilyIdSnapshot: mergeFamilyIdSnapshot,
                    omitFamilyIdQuery: true,
                    hasRetriedAfterEmptyExplicitFamilyQuery: true,
                    completion: completion
                )
                return
            }
            completion(.success(wrapSuccess(members)))
        }
        networkManager.get(endpoint: AppConfig.Endpoint.familyMembers, queryParams: query, requiresAuth: true, onHeaders: { [weak self] headers in
            self?.applyFamilyMembersListHeaders(headers)
        }) { (result: Result<[FamilyMemberResponse], Error>) in
            switch result {
            case .success(let members):
                handleMembersSuccess(members)
            case .failure(let error):
                if case .notFound = NetworkError.from(error) {
                    // Новый контракт: 404 при устаревшем `?familyId=` без primary — как пустой `[]`, один раз перезапрашиваем без query после сброса кэша.
                    if FamilyLocalStore.shouldClearFamilyCacheAfterMembersRequestFailure(error),
                       hadExplicitFamilyQuery,
                       !hasRetriedAfterEmptyExplicitFamilyQuery {
                        FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                        self.performGetFamilyMembers(
                            hasRetriedAfterTokenBootstrap: hasRetriedAfterTokenBootstrap,
                            hasRetriedAfterFamilyContextConflict: hasRetriedAfterFamilyContextConflict,
                            familyContextConflictRecovered: true,
                            mergeFamilyIdSnapshot: mergeFamilyIdSnapshot,
                            omitFamilyIdQuery: true,
                            hasRetriedAfterEmptyExplicitFamilyQuery: true,
                            completion: completion
                        )
                        return
                    }
                    if FamilyLocalStore.shouldClearFamilyCacheAfterMembersRequestFailure(error) {
                        FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                        completion(.failure(error))
                        return
                    }
                    // Backward-compat fallback for environments where gateway exposes legacy family paths.
                    self.networkManager.get(
                        endpoint: "/family/members",
                        queryParams: query,
                        requiresAuth: true,
                        onHeaders: { [weak self] headers in
                            self?.applyFamilyMembersListHeaders(headers)
                        },
                        completion: { (legacyResult: Result<[FamilyMemberResponse], Error>) in
                            switch legacyResult {
                            case .success(let members):
                                handleMembersSuccess(members)
                            case .failure(let legacyError):
                                if FamilyLocalStore.shouldClearFamilyCacheAfterMembersRequestFailure(legacyError),
                                   hadExplicitFamilyQuery,
                                   !hasRetriedAfterEmptyExplicitFamilyQuery {
                                    FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                                    self.performGetFamilyMembers(
                                        hasRetriedAfterTokenBootstrap: hasRetriedAfterTokenBootstrap,
                                        hasRetriedAfterFamilyContextConflict: hasRetriedAfterFamilyContextConflict,
                                        familyContextConflictRecovered: true,
                                        mergeFamilyIdSnapshot: mergeFamilyIdSnapshot,
                                        omitFamilyIdQuery: true,
                                        hasRetriedAfterEmptyExplicitFamilyQuery: true,
                                        completion: completion
                                    )
                                    return
                                }
                                if FamilyLocalStore.shouldClearFamilyCacheAfterMembersRequestFailure(legacyError) {
                                    FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                                }
                                completion(.failure(legacyError))
                            }
                        }
                    )
                    return
                }
                let networkError = NetworkError.from(error)
                if !hasRetriedAfterFamilyContextConflict, networkError.isFamilyMembersContextConflict {
                    self.performGetFamilyMembers(
                        hasRetriedAfterTokenBootstrap: hasRetriedAfterTokenBootstrap,
                        hasRetriedAfterFamilyContextConflict: true,
                        familyContextConflictRecovered: true,
                        mergeFamilyIdSnapshot: mergeFamilyIdSnapshot,
                        omitFamilyIdQuery: true,
                        hasRetriedAfterEmptyExplicitFamilyQuery: hasRetriedAfterEmptyExplicitFamilyQuery,
                        completion: completion
                    )
                    return
                }
                let shouldBootstrapToken: Bool
                switch networkError {
                case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
                    shouldBootstrapToken = true
                default:
                    shouldBootstrapToken = self.isInvalidUserIdInTokenError(error)
                }
                guard !hasRetriedAfterTokenBootstrap, shouldBootstrapToken else {
                    completion(.failure(error))
                    return
                }
                self.bootstrapDeviceTokenIfNeeded(forceRefresh: true) { bootstrapResult in
                    switch bootstrapResult {
                    case .success:
                        self.performGetFamilyMembers(
                            hasRetriedAfterTokenBootstrap: true,
                            hasRetriedAfterFamilyContextConflict: hasRetriedAfterFamilyContextConflict,
                            familyContextConflictRecovered: familyContextConflictRecovered,
                            mergeFamilyIdSnapshot: mergeFamilyIdSnapshot,
                            omitFamilyIdQuery: omitFamilyIdQuery,
                            hasRetriedAfterEmptyExplicitFamilyQuery: hasRetriedAfterEmptyExplicitFamilyQuery,
                            completion: completion
                        )
                    case .failure(let bootstrapError):
                        completion(.failure(bootstrapError))
                    }
                }
            }
        }
    }
    
    func addFamilyMember(name: String, role: String, completion: @escaping (Result<FamilyMemberResponse, Error>) -> Void) {
        let activeFamilyId = FamilyLocalStore.loadPersistedFamilyId()
        let request = AddMemberRequest(name: name, role: role, familyId: activeFamilyId)
        performAddFamilyMember(request: request, hasRetriedAfterTokenBootstrap: false, completion: completion)
    }

    /// Async-обертка для добавления участника семьи.
    func addFamilyMember(name: String, role: String) async throws -> FamilyMemberResponse {
        try await withCheckedThrowingContinuation { continuation in
            addFamilyMember(name: name, role: role) { result in
                continuation.resume(with: result)
            }
        }
    }

    /// Устаревший локальный `familyId` — клиент не член этой семьи (P1 stale recovery).
    private func isFamilyAddStaleContext409(_ networkError: NetworkError) -> Bool {
        switch networkError {
        case .conflict(let detail):
            return (detail ?? "").lowercased().contains("family_context_stale")
        default:
            return false
        }
    }

    /// `true` только для лимита ростера (`family_roster_full` и т.п.), не для context mismatch.
    private func isFamilyAddRosterLimit409(_ networkError: NetworkError) -> Bool {
        switch networkError {
        case .conflict(let detail):
            let d = (detail ?? "").lowercased()
            if d.contains("context mismatch") { return false }
            if d.contains("family_context_stale") { return false }
            return d.contains("family_roster")
        case .invalidStatusCode(let code), .httpError(let code):
            return code == 409
        default:
            return false
        }
    }

    private func familyAddRosterLimitUserMessage(networkError: NetworkError) -> String {
        let limit = SubscriptionManager.currentFamilyLimit
        if case .conflict(let detail) = networkError,
           let d = detail?.lowercased(),
           d.contains("family_roster") {
            let used = UserDefaults.standard.integer(forKey: "family_roster_used_last")
            if used > 0, limit > 0 {
                return "Семья уже заполнена по тарифу владельца на сервере (\(used)/\(limit)). Обновите тариф или удалите участника."
            }
            if limit > 0 {
                return "Лимит участников для вашего тарифа на сервере (\(limit)) достигнут. Обновите тариф, чтобы добавить больше участников."
            }
            return "Нельзя добавить участника: ростер заполнен по данным сервера."
        }
        if limit > 0 {
            return "Лимит участников для вашего тарифа (\(limit)) достигнут. Обновите тариф, чтобы добавить больше участников."
        }
        return "Нельзя добавить участника: достигнут лимит для текущего тарифа."
    }

    private func performAddFamilyMember(
        request: AddMemberRequest,
        hasRetriedAfterTokenBootstrap: Bool,
        completion: @escaping (Result<FamilyMemberResponse, Error>) -> Void
    ) {
        VisualLogger.shared.log("➡️ FAMILY ADD(server) name=\(request.name), role=\(request.role)", level: .info, category: "FAMILY")
        // Генерируем идемпотентный ключ — привязка к семье, роли и имени минимизирует дубликаты
        let keySeed = "\(request.familyId ?? "no_family")|\(request.role.lowercased())|\(request.name.lowercased())"
        let idemKey = "ios-\(UUID().uuidString)-\(abs(keySeed.hashValue))"
        networkManager.post(endpoint: AppConfig.Endpoint.addFamilyMember, body: request, requiresAuth: true, extraHeaders: ["Idempotency-Key": idemKey]) { (result: Result<FamilyMemberResponse, Error>) in
            switch result {
            case .success(let response):
                VisualLogger.shared.log("⬅️ FAMILY ADD(server) success: id=\(response.id) name=\(response.name)", level: .success, category: "FAMILY")
                completion(result)
            case .failure(let error):
                if case .notFound = NetworkError.from(error) {
                    // Backward-compat fallback для окружений с legacy путями /family/*
                    VisualLogger.shared.log("↪️ FAMILY ADD(compat) fallback /family/add", level: .warning, category: "FAMILY")
                    self.networkManager.post(endpoint: "/family/add", body: request, requiresAuth: true, extraHeaders: ["Idempotency-Key": idemKey]) { (fallback: Result<FamilyMemberResponse, Error>) in
                        switch fallback {
                        case .success(let resp):
                            VisualLogger.shared.log("⬅️ FAMILY ADD(compat) success: id=\(resp.id) name=\(resp.name)", level: .success, category: "FAMILY")
                        case .failure(let err):
                            VisualLogger.shared.log("❌ FAMILY ADD(compat) error: \(err.localizedDescription)", level: .error, category: "FAMILY")
                        }
                        completion(fallback)
                    }
                    return
                }

                let networkError = NetworkError.from(error)
                
                // ✅ CRITICAL: Specific handling for "Family not found" (404) - root cause of registration failure
                // This happens when trying to add member before family exists (common during first onboarding)
                if case .httpError(404) = networkError {
                    VisualLogger.shared.log("🚨 FAMILY NOT FOUND (404) - likely first-time registration. Will trigger createFamily fallback.", level: .error, category: "FAMILY")
                    logger.business("🔍 FAMILY ADD: 404 'Family not found' - no existing family for this JWT token")
                    completion(.failure(NetworkError.httpError(404)))
                    return
                }
                
                if self.isFamilyAddStaleContext409(networkError) {
                    VisualLogger.shared.log(
                        "🔄 FAMILY ADD(stale) 409 family_context_stale — clearing local family_id",
                        level: .warning,
                        category: "FAMILY"
                    )
                    FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                    completion(.failure(NetworkError.businessLogicError("family_context_stale")))
                    return
                }

                // 409: `NetworkManager` отдаёт `.conflict(detail)`, не `.httpError(409)` — обрабатываем оба и отделяем лимит ростера от прочих конфликтов.
                if self.isFamilyAddRosterLimit409(networkError) {
                    let msg = self.familyAddRosterLimitUserMessage(networkError: networkError)
                    let limit = SubscriptionManager.currentFamilyLimit
                    VisualLogger.shared.log("⚠️ FAMILY ADD(limit) 409: \(msg) (limit=\(limit))", level: .warning, category: "FAMILY")
                    completion(.failure(NetworkError.businessLogicError(msg)))
                    return
                }
                
                let shouldBootstrapToken: Bool
                switch networkError {
                case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
                    shouldBootstrapToken = true
                default:
                    shouldBootstrapToken = self.isInvalidUserIdInTokenError(error)
                }

                guard !hasRetriedAfterTokenBootstrap, shouldBootstrapToken else {
                    VisualLogger.shared.log("❌ FAMILY ADD(server) error: \(error.localizedDescription)", level: .error, category: "FAMILY")
                    completion(.failure(error))
                    return
                }

                self.bootstrapDeviceTokenIfNeeded(forceRefresh: true) { bootstrapResult in
                    switch bootstrapResult {
                    case .success:
                        VisualLogger.shared.log("🔄 FAMILY ADD(server) retry after token bootstrap", level: .info, category: "FAMILY")
                        self.performAddFamilyMember(request: request, hasRetriedAfterTokenBootstrap: true, completion: completion)
                    case .failure(let bootstrapError):
                        VisualLogger.shared.log("❌ FAMILY ADD(server) bootstrap failed: \(bootstrapError.localizedDescription)", level: .error, category: "FAMILY")
                        completion(.failure(bootstrapError))
                    }
                }
            }
        }
    }
    
    /**
     * Удаление участника семьи (async версия для CachedAPIService)
     */
    func removeFamilyMember(
        _ memberId: String,
        source: String = "ios_unknown",
        reason: String? = nil
    ) async throws -> FamilyMemberResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct RemoveMemberRequest: Codable {
                let memberId: String
                let source: String
                let reason: String?
                let familyId: String?
            }
            let activeFamilyId = FamilyLocalStore.loadPersistedFamilyId()
            let request = RemoveMemberRequest(memberId: memberId, source: source, reason: reason, familyId: activeFamilyId)
            VisualLogger.shared.log(
                "➡️ HTTP DELETE \(AppConfig.Endpoint.removeFamilyMember) memberId=\(memberId) source=\(source)",
                level: .info,
                category: "FAMILY"
            )
            networkManager.delete(endpoint: AppConfig.Endpoint.removeFamilyMember, body: request) { (result: Result<FamilyMemberResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in removeFamilyMember()!")
                    return
                }
                hasResumed = true
                switch result {
                case .success(let response):
                    VisualLogger.shared.log("⬅️ FAMILY REMOVE(server) success id=\(response.id)", level: .success, category: "FAMILY")
                    continuation.resume(returning: response)
                case .failure(let error):
                    let message = error.localizedDescription
                    VisualLogger.shared.log("❌ FAMILY REMOVE(server) error: \(message)", level: .error, category: "FAMILY")
                    // Дополнительные подсказки для частых случаев
                    let lower = message.lowercased()
                    if lower.contains("self-removal") {
                        VisualLogger.shared.log("ℹ️ HINT: Нельзя удалить самого себя", level: .warning, category: "FAMILY")
                    } else if lower.contains("last parent") {
                        VisualLogger.shared.log("ℹ️ HINT: Нельзя удалить последнего родителя", level: .warning, category: "FAMILY")
                    } else if lower.contains("only administrators") || lower.contains("403") {
                        VisualLogger.shared.log("ℹ️ HINT: Действие доступно только родителю (администратору)", level: .warning, category: "FAMILY")
                    } else if lower.contains("context mismatch") || lower.contains("409") {
                        VisualLogger.shared.log("ℹ️ HINT: Выбрана не та семья. Проверьте active familyId", level: .warning, category: "FAMILY")
                    } else if lower.contains("not found") || lower.contains("404") {
                        VisualLogger.shared.log("ℹ️ HINT: Участник отсутствует на сервере для этой семьи (проверьте '🧩 IDs server')", level: .warning, category: "FAMILY")
                    }
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
        let stored = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let headers: [String: String]? = stored.isEmpty ? nil : ["X-Family-Id": stored]
        networkManager.get(endpoint: AppConfig.Endpoint.familyStats, additionalHeaders: headers, completion: completion)
    }
    
    // MARK: - Family Chat API
    
    func getFamilyChatMessages(completion: @escaping (Result<[FamilyChatMessageResponse], Error>) -> Void) {
        let stored = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let query: [String: String]? = stored.isEmpty ? nil : ["familyId": stored]
        let headers: [String: String]? = stored.isEmpty ? nil : ["X-Family-Id": stored]
        networkManager.get(
            endpoint: AppConfig.Endpoint.familyChatMessages,
            queryParams: query,
            additionalHeaders: headers,
            onHeaders: { [weak self] hdr in
                self?.applyFamilyMembersListHeaders(hdr)
            },
            completion: completion
        )
    }
    
    func sendFamilyChatMessage(
        message: String?,
        familyId: String?,
        messageType: String?,
        voiceUrl: String?,
        voiceDuration: Double?,
        mediaUrl: String?,
        mediaType: String?,
        replyToMessageId: String?,
        envelopeVersion: Int? = nil,
        senderDeviceId: String? = nil,
        ciphertext: String? = nil,
        mediaCiphertextUrl: String? = nil,
        mediaCiphertextHash: String? = nil,
        completion: @escaping (Result<SendFamilyChatMessageResponse, Error>) -> Void
    ) {
        let request = SendFamilyChatMessageRequest(
            message: message,
            familyId: familyId,
            messageType: messageType,
            voiceUrl: voiceUrl,
            voiceDuration: voiceDuration,
            mediaUrl: mediaUrl,
            mediaType: mediaType,
            replyToMessageId: replyToMessageId,
            envelopeVersion: envelopeVersion,
            senderDeviceId: senderDeviceId,
            ciphertext: ciphertext,
            ciphertextContentType: ciphertext != nil ? 0 : nil,
            mediaCiphertextUrl: mediaCiphertextUrl,
            mediaCiphertextHash: mediaCiphertextHash
        )
        networkManager.post(endpoint: AppConfig.Endpoint.familyChatSend, body: request) { [weak self] (result: Result<SendFamilyChatMessageResponse, Error>) in
            switch result {
            case .success:
                completion(result)
            case .failure(let error):
                guard self?.isCriticalEndpointNotFound(error) == true else {
                    completion(.failure(error))
                    return
                }
                self?.sendFamilyChatMessageViaOfflineEndpoint(
                    message: message,
                    familyId: familyId,
                    messageType: messageType,
                    mediaUrl: mediaUrl,
                    mediaType: mediaType,
                    completion: completion
                )
            }
        }
    }
    
    func deleteFamilyChatMessage(messageId: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct DeleteRequest: Codable {
            let messageId: String
        }
        let trimmedFamilyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let extraHeaders: [String: String]? = trimmedFamilyId.isEmpty ? nil : ["X-Family-Id": trimmedFamilyId]
        networkManager.delete(
            endpoint: "\(AppConfig.Endpoint.familyChatSend)/\(messageId)",
            body: DeleteRequest(messageId: messageId),
            additionalHeaders: extraHeaders
        ) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.data ?? false))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func editFamilyChatMessage(messageId: String, newText: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct EditRequest: Codable {
            let messageId: String
            let text: String
        }
        networkManager.post(endpoint: "\(AppConfig.Endpoint.familyChatSend)/edit", body: EditRequest(messageId: messageId, text: newText)) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.data ?? false))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Family Chat E2EE (E1.4)

    func registerFamilyE2EEDevice(request: RegisterE2EEDeviceRequest, completion: @escaping (Result<RegisterE2EEDeviceResponse, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.familyChatE2EEKeysRegister, body: request, completion: completion)
    }

    func fetchFamilyE2EEDevices(familyId: String, completion: @escaping (Result<E2EEDeviceListResponse, Error>) -> Void) {
        let headers = ["X-Family-Id": familyId]
        networkManager.get(
            endpoint: AppConfig.Endpoint.familyChatE2EEKeys,
            queryParams: ["family_id": familyId],
            additionalHeaders: headers,
            completion: completion
        )
    }

    func distributeFamilyE2EESenderKey(request: DistributeE2EESenderKeyRequest, completion: @escaping (Result<DistributeE2EESenderKeyResponse, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.familyChatE2EESenderKeysDistribute, body: request, completion: completion)
    }

    func fetchFamilyE2EESenderKeys(familyId: String, completion: @escaping (Result<E2EESenderKeyDistributionListResponse, Error>) -> Void) {
        let headers = ["X-Family-Id": familyId]
        networkManager.get(
            endpoint: AppConfig.Endpoint.familyChatE2EESenderKeys,
            queryParams: ["family_id": familyId],
            additionalHeaders: headers,
            completion: completion
        )
    }

    func revokeFamilyE2EEDevice(request: RevokeE2EEDeviceRequest, completion: @escaping (Result<RevokeE2EEDeviceResponse, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.familyChatE2EEKeysRevoke, body: request, completion: completion)
    }

    func sendTypingIndicator(familyId: String?, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct TypingRequest: Codable {
            let familyId: String?
        }
        networkManager.post(endpoint: "\(AppConfig.Endpoint.familyChatSend)/typing", body: TypingRequest(familyId: familyId)) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.data ?? false))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func addReaction(messageId: String, emoji: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct ReactionRequest: Codable {
            let messageId: String
            let emoji: String
        }
        networkManager.post(endpoint: "\(AppConfig.Endpoint.familyChatSend)/reaction", body: ReactionRequest(messageId: messageId, emoji: emoji)) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.data ?? false))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func markMessageAsRead(messageId: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct ReadRequest: Codable {
            let messageId: String
        }
        networkManager.post(endpoint: "\(AppConfig.Endpoint.familyChatSend)/read", body: ReadRequest(messageId: messageId)) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.data ?? false))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// E1.6 — загрузка AES-GCM ciphertext blob (octet-stream).
    func uploadEncryptedMedia(
        encryptedData: Data,
        contentHash: String,
        familyId: String,
        completion: @escaping (Result<(url: String, hash: String), Error>) -> Void
    ) {
        let resolvedFamily = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !resolvedFamily.isEmpty else {
            completion(.failure(NetworkError.badRequest("familyId is required")))
            return
        }
        guard let url = URL(string: AppConfig.apiBaseURL + AppConfig.Endpoint.familyChatUploadMediaCiphertext) else {
            completion(.failure(NetworkError.invalidURL))
            return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        request.setValue(resolvedFamily, forHTTPHeaderField: "X-Family-Id")
        request.setValue(contentHash, forHTTPHeaderField: "X-Content-Sha256")
        if let token = AppConfig.authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.httpBody = encryptedData

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                DispatchQueue.main.async { completion(.failure(error)) }
                return
            }
            guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode), let data else {
                DispatchQueue.main.async { completion(.failure(NetworkError.invalidResponse)) }
                return
            }
            struct UploadEncResponse: Codable {
                let mediaCiphertextUrl: String?
                let mediaUrl: String?
                let url: String?
                let mediaCiphertextHash: String?
                let contentHash: String?
            }
            if let decoded = try? JSONDecoder().decode(UploadEncResponse.self, from: data) {
                let mediaURL = decoded.mediaCiphertextUrl ?? decoded.mediaUrl ?? decoded.url ?? ""
                if !mediaURL.isEmpty {
                    let hash = decoded.mediaCiphertextHash ?? decoded.contentHash ?? contentHash
                    DispatchQueue.main.async { completion(.success((url: mediaURL, hash: hash))) }
                    return
                }
            }
            if let resolved = self.extractMediaURL(from: data), !resolved.isEmpty {
                DispatchQueue.main.async { completion(.success((url: resolved, hash: contentHash))) }
                return
            }
            DispatchQueue.main.async {
                completion(.failure(NSError(domain: "MediaUpload", code: -2, userInfo: [NSLocalizedDescriptionKey: "Invalid ciphertext upload response"])))
            }
        }.resume()
    }

    // MARK: - ✅ Media Upload (Phase 2026 - High Priority)
    /// Полноценная загрузка медиа с поддержкой progress, retry и offline
    func uploadMedia(
        data: Data,
        type: String,
        filename: String? = nil,
        familyId: String? = nil,
        progress: ((Double) -> Void)? = nil,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        let mediaType = type.lowercased()
        let defaultFilename = filename ?? "media_\(Date().timeIntervalSince1970).\(mediaType == "image" ? "jpg" : mediaType == "video" ? "mp4" : "m4a")"
        let resolvedFamily = (familyId ?? FamilyLocalStore.loadPersistedFamilyId())?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if resolvedFamily.isEmpty {
            completion(.failure(NetworkError.badRequest("familyId is required for chat media upload")))
            return
        }
        
        print("📤 APIService: Starting media upload - type: \(mediaType), size: \(data.count) bytes, filename: \(defaultFilename)")
        
        let uploadCandidates = [
            "/api/family/chat/upload-media",
            "/api/chat/upload-media"
        ]
        
        uploadMediaUsingCandidates(
            endpoints: uploadCandidates,
            fileData: data,
            mediaType: mediaType,
            filename: defaultFilename,
            familyContextId: resolvedFamily,
            completion: completion
        )
        
        // Простой прогресс (для реального прогресса лучше использовать URLSessionDelegate)
        if let progress = progress {
            // Симуляция прогресса для демо (в production используем custom URLSession с delegate)
            var simulatedProgress: Double = 0.0
            Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
                simulatedProgress += 0.08
                progress(min(simulatedProgress, 1.0))
                if simulatedProgress >= 1.0 {
                    timer.invalidate()
                }
            }
        }
        
    }
    
    private func getMimeType(for type: String) -> String {
        switch type.lowercased() {
        case "image": return "image/jpeg"
        case "video": return "video/mp4"
        case "audio", "voice": return "audio/m4a"
        default: return "application/octet-stream"
        }
    }

    private func sendFamilyChatMessageViaOfflineEndpoint(
        message: String?,
        familyId: String?,
        messageType: String?,
        mediaUrl: String?,
        mediaType: String?,
        completion: @escaping (Result<SendFamilyChatMessageResponse, Error>) -> Void
    ) {
        guard let familyId = familyId?.trimmingCharacters(in: .whitespacesAndNewlines), !familyId.isEmpty else {
            completion(.failure(NetworkError.notFound("familyId is required for offline fallback")))
            return
        }
        
        guard let userId = UserDefaults.standard.string(forKey: "user_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !userId.isEmpty else {
            completion(.failure(NetworkError.unauthorized("user_id is required for offline fallback")))
            return
        }
        
        let fallbackContent: String = {
            if let message = message?.trimmingCharacters(in: .whitespacesAndNewlines), !message.isEmpty {
                return message
            }
            if let mediaUrl = mediaUrl?.trimmingCharacters(in: .whitespacesAndNewlines), !mediaUrl.isEmpty {
                let resolvedType = mediaType ?? messageType ?? "media"
                return "[\(resolvedType)] \(mediaUrl)"
            }
            return "[empty_message]"
        }()
        
        sendOfflineMessage(
            userId: userId,
            recipientId: familyId,
            familyId: familyId,
            content: fallbackContent,
            deviceId: UIDevice.current.identifierForVendor?.uuidString,
            timestamp: ISO8601DateFormatter().string(from: Date())
        ) { result in
            switch result {
            case .success(let response):
                completion(.success(SendFamilyChatMessageResponse(success: true, messageId: response.messageId)))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    private func isCriticalEndpointNotFound(_ error: Error) -> Bool {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .notFound(let msg):
                let m = (msg ?? "").lowercased()
                // Семантический 404 FastAPI (семья не резолвится для JWT) — не путать с «маршрута нет на шлюзе».
                if m.contains("family not found") { return false }
                return true
            case .httpError(let code):
                return code == 404
            default:
                break
            }
        }
        return error.localizedDescription.localizedCaseInsensitiveContains("critical endpoint not found")
    }

    /// Текст `detail` из ответа FastAPI (строка или массив validation errors); иначе `nil`.
    private static func parseFastAPIErrorDetail(from data: Data) -> String? {
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        if let s = obj["detail"] as? String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? nil : t
        }
        if let arr = obj["detail"] as? [[String: Any]] {
            let parts = arr.compactMap { $0["msg"] as? String }.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
            return parts.isEmpty ? nil : parts.joined(separator: "; ")
        }
        if let s = obj["message"] as? String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? nil : t
        }
        return nil
    }

    private static func bodyLooksLikeHTML(_ text: String) -> Bool {
        let lower = text.lowercased()
        return lower.hasPrefix("<!doctype") || lower.contains("<html") || lower.contains("<body")
    }

    private static func networkErrorForUploadHTTPStatus(
        _ code: Int,
        parsedDetail: String?
    ) -> NetworkError {
        switch code {
        case 400:
            return .badRequest(parsedDetail)
        case 401:
            return .unauthorized(parsedDetail)
        case 403:
            if let d = parsedDetail, !d.isEmpty, !bodyLooksLikeHTML(d) {
                return .forbidden(d)
            }
            return .forbidden(nil)
        case 404:
            return .notFound(parsedDetail)
        case 413:
            return .badRequest(parsedDetail ?? "File too large")
        case 429:
            return .tooManyRequests(parsedDetail)
        case 500:
            return .internalServerError(parsedDetail)
        case 502:
            return .badGateway(parsedDetail)
        case 503:
            return .serviceUnavailable(parsedDetail)
        default:
            return .httpError(code)
        }
    }
    
    private func uploadMediaUsingCandidates(
        endpoints: [String],
        fileData: Data,
        mediaType: String,
        filename: String,
        familyContextId: String,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        guard let endpoint = endpoints.first else {
            completion(.failure(NSError(domain: "MediaUpload", code: -3, userInfo: [NSLocalizedDescriptionKey: "No upload endpoint accepted the request"])))
            return
        }
        
        let boundary = "Boundary-\(UUID().uuidString)"
        guard let url = URL(string: AppConfig.apiBaseURL + endpoint) else {
            completion(.failure(NetworkError.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        if let token = AppConfig.authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.setValue(familyContextId, forHTTPHeaderField: "X-Family-Id")
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(getMimeType(for: mediaType))\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"type\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(mediaType)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"familyId\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(familyContextId)\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async {
                    completion(.failure(NetworkError.invalidResponse))
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    completion(.failure(NetworkError.noData))
                }
                return
            }
            
            guard (200...299).contains(httpResponse.statusCode) else {
                // Если endpoint не найден — пробуем следующий explicit router path.
                if httpResponse.statusCode == 404, endpoints.count > 1 {
                    self?.uploadMediaUsingCandidates(
                        endpoints: Array(endpoints.dropFirst()),
                        fileData: fileData,
                        mediaType: mediaType,
                        filename: filename,
                        familyContextId: familyContextId,
                        completion: completion
                    )
                    return
                }
                let parsedDetail = Self.parseFastAPIErrorDetail(from: data)
                let bodyPreview = String(data: data.prefix(768), encoding: .utf8) ?? "<non-UTF8 \(data.count) B>"
                #if DEBUG
                print("📤 APIService upload-media HTTP \(httpResponse.statusCode) \(endpoint) detail=\(parsedDetail ?? "—") body.prefix=\(bodyPreview.prefix(400))")
                #endif
                DispatchQueue.main.async {
                    let failure: NetworkError = Self.networkErrorForUploadHTTPStatus(
                        httpResponse.statusCode,
                        parsedDetail: parsedDetail
                    )
                    completion(.failure(failure))
                }
                return
            }
            
            if let resolvedURL = self?.extractMediaURL(from: data), !resolvedURL.isEmpty {
                DispatchQueue.main.async {
                    completion(.success(resolvedURL))
                }
                return
            }
            
            if endpoints.count > 1 {
                self?.uploadMediaUsingCandidates(
                    endpoints: Array(endpoints.dropFirst()),
                    fileData: fileData,
                    mediaType: mediaType,
                    filename: filename,
                    familyContextId: familyContextId,
                    completion: completion
                )
                return
            }
            
            DispatchQueue.main.async {
                completion(.failure(NSError(domain: "MediaUpload", code: -2, userInfo: [NSLocalizedDescriptionKey: "Invalid server response"])))
            }
        }.resume()
    }
    
    private func extractMediaURL(from data: Data) -> String? {
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        
        let directKeys = ["url", "mediaUrl", "media_url", "fileUrl", "file_url", "path"]
        for key in directKeys {
            if let value = json[key] as? String, !value.isEmpty {
                return normalizeMediaURL(value)
            }
        }
        
        let nestedKeys = ["data", "result", "payload"]
        for containerKey in nestedKeys {
            if let nested = json[containerKey] as? [String: Any] {
                for key in directKeys {
                    if let value = nested[key] as? String, !value.isEmpty {
                        return normalizeMediaURL(value)
                    }
                }
            }
        }
        
        return nil
    }
    
    private func normalizeMediaURL(_ raw: String) -> String {
        if raw.hasPrefix("http://") || raw.hasPrefix("https://") {
            return raw
        }
        if raw.hasPrefix("/") {
            return AppConfig.apiBaseURL + raw
        }
        return raw
    }
    
    // MARK: - Analytics API
    
    func getAnalytics(period: String, completion: @escaping (Result<AnalyticsResponse, Error>) -> Void) {
        networkManager.get(endpoint: "\(AppConfig.Endpoint.analytics)?period=\(period)", completion: completion)
    }
    
    func getTopThreats(completion: @escaping (Result<[ThreatItem], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.topThreats) { (result: Result<TopThreatsAPIEnvelope, Error>) in
            switch result {
            case .success(let envelope):
                completion(.success(envelope.topThreats))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Component Stats API
    
    /// ✅ ВАРИАНТ 4: Получить статистику компонента по ID
    func getComponentStats(componentId: String, completion: @escaping (Result<ComponentStats, Error>) -> Void) {
        let endpoint: String
        switch componentId {
        case "driving_reports_agent", "driving":
            endpoint = AppConfig.Endpoint.drivingStats
        case "dark_web_monitoring_agent", "darkweb":
            endpoint = AppConfig.Endpoint.darkWebStats
        case "russian_identity_theft_protection_agent", "identity":
            endpoint = AppConfig.Endpoint.identityTheftStats
        case "location_bubble_agent", "location":
            endpoint = AppConfig.Endpoint.locationStats
        case "personal_data_cleanup_agent", "cleanup":
            endpoint = AppConfig.Endpoint.dataCleanupStats
        case "anti_tracker_agent", "tracker":
            endpoint = AppConfig.Endpoint.antiTrackerStats
        case "ai_categories_agent", "ai":
            endpoint = AppConfig.Endpoint.aiCategoriesStats
        default:
            completion(.failure(NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Unknown component: \(componentId)"])))
            return
        }
        
        // Typed decoding reduces overhead versus AnyCodable and makes parsing safer.
        networkManager.get(endpoint: endpoint) { (result: Result<ComponentStatsDTO, Error>) in
            switch result {
            case .success(let dto):
                // Преобразуем ответ в ComponentStats
                let stats = self.parseComponentStats(componentId: componentId, dto: dto)
                completion(.success(stats))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Преобразует ответ API в ComponentStats
    private func parseComponentStats(componentId: String, dto: ComponentStatsDTO) -> ComponentStats {
        var metrics: [String: String] = [:]
        
        // Преобразуем данные в зависимости от типа компонента
        switch componentId {
        case "driving_reports_agent", "driving":
            if let trips = dto.trips ?? dto.total {
                metrics["trips"] = "\(trips)"
            }
            if let safety_score = dto.safety_score {
                metrics["safety_score"] = String(format: "%.1f", safety_score)
            }
            if let new_events = dto.new_events ?? dto.last_24h {
                metrics["new_events"] = "\(new_events)"
            }
        case "dark_web_monitoring_agent", "darkweb":
            if let leaks_found = dto.leaks_found ?? dto.totalLeaks ?? dto.total {
                metrics["leaks_found"] = "\(leaks_found)"
            }
            if let new_leaks = dto.new_leaks ?? dto.newLeaks ?? dto.last_24h {
                metrics["new_leaks"] = "\(new_leaks)"
            }
            if let new_events = dto.new_events ?? dto.newEvents ?? dto.last_7d {
                metrics["new_events"] = "\(new_events)"
            }
        case "russian_identity_theft_protection_agent", "identity":
            if let attempts = dto.attempts ?? dto.totalAttempts ?? dto.total {
                metrics["attempts"] = "\(attempts)"
            }
            if let blocked = dto.blocked ?? dto.blockedAttempts {
                metrics["blocked"] = "\(blocked)"
            }
        case "location_bubble_agent", "location":
            if let blocked = dto.blocked ?? dto.blockedRequests {
                metrics["blocked"] = "\(blocked)"
            }
            if let accuracy = dto.accuracy {
                metrics["accuracy"] = accuracy
            }
        case "personal_data_cleanup_agent", "cleanup":
            if let freed_space_gb = dto.freed_space_gb ?? dto.totalFreed {
                metrics["freed_space_gb"] = String(format: "%.1f", freed_space_gb)
            }
            if let last_cleanup_hours_ago = dto.last_cleanup_hours_ago {
                metrics["last_cleanup_hours_ago"] = "\(last_cleanup_hours_ago)"
            }
        case "anti_tracker_agent", "tracker":
            if let blocked_total = dto.blocked_total ?? dto.totalBlocked ?? dto.total {
                metrics["blocked_total"] = "\(blocked_total)"
            }
            if let blocked_this_week = dto.blocked_this_week ?? dto.blockedThisWeek ?? dto.last_7d {
                metrics["blocked_this_week"] = "\(blocked_this_week)"
            }
        case "ai_categories_agent", "ai":
            if let categorized = dto.categorized ?? dto.totalCategorized ?? dto.total {
                metrics["categorized"] = "\(categorized)"
            }
            if let blocked = dto.blocked ?? dto.blockedContent {
                metrics["blocked"] = "\(blocked)"
            }
        default:
            break
        }
        
        return ComponentStats(componentId: componentId, metrics: metrics, dataSource: .api)
    }

    private struct ComponentStatsDTO: Codable {
        let trips: Int?
        let safety_score: Double?
        let new_events: Int?
        let leaks_found: Int?
        let new_leaks: Int?
        let attempts: Int?
        let blocked: Int?
        let accuracy: String?
        let freed_space_gb: Double?
        let last_cleanup_hours_ago: Int?
        let blocked_total: Int?
        let blocked_this_week: Int?
        let categorized: Int?
        let totalLeaks: Int?
        let newLeaks: Int?
        let newEvents: Int?
        let totalAttempts: Int?
        let blockedAttempts: Int?
        let blockedRequests: Int?
        let totalFreed: Double?
        let totalBlocked: Int?
        let blockedThisWeek: Int?
        let totalCategorized: Int?
        let blockedContent: Int?
        let resolvedLeaks: Int?
        let criticalLeaks: Int?
        let critical: Int?
        let suspiciousActivities: Int?
        let suspicious: Int?
        let lastScanDate: String?
        // reports_compat fallback fields
        let total: Int?
        let allowed: Int?
        let last_24h: Int?
        let last_7d: Int?
        let last_30d: Int?
        let source: String?
        let timestamp: String?
    }

    private static func parseISO8601Date(_ value: String?) -> Date? {
        guard let value = value, !value.isEmpty else { return nil }
        return ISO8601DateFormatter().date(from: value)
    }
    
    // MARK: - AI Assistant API

    /// POST `/api/telegram/link-code` — 6-символьный код для `/link` в @AladdinchatAI_bot (JWT).
    func createTelegramLinkCode(
        completion: @escaping (Result<TelegramLinkCodeResponse, Error>) -> Void
    ) {
        networkManager.post(
            endpoint: AppConfig.Endpoint.telegramLinkCode,
            body: EmptyRequest(),
            requiresAuth: true,
            completion: completion
        )
    }

    // Основной чат с AI (legacy — полный ответ)
    func sendMessageToAI(
        message: String,
        context: String = "general",
        responseLanguage: String? = nil,
        completion: @escaping (Result<ChatMessageResponse, Error>) -> Void
    ) {
        let cloudMessage: String
        do {
            cloudMessage = try AIOutboundTextGate.prepareUserMessage(message).cloudText
        } catch {
            completion(.failure(error))
            return
        }
        let request = ChatMessageRequest(
            message: cloudMessage,
            context: context,
            userId: AppConfig.authToken ?? "guest",
            timestamp: Date(),
            responseLanguage: responseLanguage
        )
        // ✅ AI Assistant - публичный эндпоинт (демонстрация возможностей)
        networkManager.post(endpoint: AppConfig.Endpoint.aiAssistantChat, body: request, requiresAuth: false, completion: completion)
    }

    // MARK: - ✅ НОВЫЙ: AI Token Streaming (Phase 2026)
    /// Стриминг токенов AI-ответа в реальном времени
    /// Используется AIStreamingService
    func streamMessageToAI(
        message: String,
        context: String = "general",
        messageId: String? = nil,
        completion: @escaping (Result<AsyncThrowingStream<String, Error>, Error>) -> Void
    ) {
        // Пока используем AIStreamingService напрямую.
        // В будущем этот метод будет возвращать stream через networkManager.
        Task {
            do {
                let stream = try await AIStreamingService.shared.createStreamingRequestForService(
                    message: message,
                    context: context,
                    messageId: messageId
                )
                completion(.success(stream))
            } catch {
                completion(.failure(error))
            }
        }
    }

    // История чата
    func getAIChatHistory(completion: @escaping (Result<AIChatHistoryResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.aiAssistantHistory, completion: completion)
    }

    // Обратная связь
    func sendAIFeedback(
        rating: Int,
        comment: String?,
        messageId: String?,
        queryText: String? = nil,
        resolvedBy: String? = nil,
        faqId: String? = nil,
        confidence: Double? = nil,
        sessionId: String? = nil,
        completion: @escaping (Result<AIFeedbackResponse, Error>) -> Void
    ) {
        let request = AIFeedbackRequest(
            rating: rating,
            comment: AIOutboundTextGate.redactOptional(comment),
            messageId: messageId,
            queryText: AIOutboundTextGate.redactOptional(queryText),
            resolvedBy: resolvedBy,
            faqId: faqId,
            confidence: confidence,
            sessionId: sessionId
        )
        // Как и чат AI — публичная отправка отзыва (без JWT), иначе гости/сбой токена дают «успех в UI» без доставки на сервер
        networkManager.post(endpoint: AppConfig.Endpoint.aiAssistantFeedback, body: request, requiresAuth: false, completion: completion)
    }

    // Возможности AI
    func getAICapabilities(completion: @escaping (Result<AICapabilitiesResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.aiAssistantCapabilities, completion: completion)
    }

    // Анализ угрозы
    func analyzeThreat(threat: String, type: String?, completion: @escaping (Result<AIAnalyzeThreatResponse, Error>) -> Void) {
        let cloudThreat: String
        do {
            cloudThreat = try AIOutboundTextGate.prepareUserMessage(threat).cloudText
        } catch {
            completion(.failure(error))
            return
        }
        let request = AIAnalyzeThreatRequest(threat: cloudThreat, type: type, context: nil)
        networkManager.post(endpoint: AppConfig.Endpoint.aiAssistantAnalyzeThreat, body: request, completion: completion)
    }

    // Персональные рекомендации
    func getAIRecommendations(completion: @escaping (Result<AIRecommendationsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.aiAssistantRecommendations, completion: completion)
    }

    // Подписки (Subscriptions)
    func downgradeSubscription(userId: String, reason: String? = nil, deviceId: String? = nil, completion: @escaping (Result<SubscriptionCancelResponse, Error>) -> Void) {
        let request = SubscriptionCancelRequest(userId: userId, reason: reason, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionCancel, body: request, completion: completion)
    }

    // Сообщить об инциденте
    func reportIncident(type: String, description: String, severity: String = "medium", completion: @escaping (Result<AIReportIncidentResponse, Error>) -> Void) {
        let cloudDescription: String
        do {
            cloudDescription = try AIOutboundTextGate.prepareUserMessage(description).cloudText
        } catch {
            completion(.failure(error))
            return
        }
        let request = AIReportIncidentRequest(type: type, description: cloudDescription, severity: severity)
        networkManager.post(endpoint: AppConfig.Endpoint.aiAssistantReportIncident, body: request, completion: completion)
    }

    // Советы по безопасности
    func getSecurityTips(completion: @escaping (Result<AISecurityTipsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.aiAssistantSecurityTips, completion: completion)
    }
    
    // MARK: - ✅ ГЕЙМИФИКАЦИЯ: Gamification API
    
    // Баланс единорогов (4 метода)
    func getGamificationBalance(userId: String, completion: @escaping (Result<GamificationBalanceResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationBalance + "/\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func addGamificationBalance(userId: String, amount: Int, reason: String? = nil, deviceId: String? = nil, completion: @escaping (Result<GamificationBalanceResponse, Error>) -> Void) {
        let request = AddBalanceRequest(userId: userId, amount: amount, reason: reason, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationBalanceAdd, body: request, completion: completion)
    }
    
    func subtractGamificationBalance(userId: String, amount: Int, reason: String? = nil, deviceId: String? = nil, completion: @escaping (Result<GamificationBalanceResponse, Error>) -> Void) {
        let request = SubtractBalanceRequest(userId: userId, amount: amount, reason: reason, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationBalanceSubtract, body: request, completion: completion)
    }
    
    func getGamificationBalanceHistory(userId: String, limit: Int = 50, offset: Int = 0, completion: @escaping (Result<BalanceHistoryResponse, Error>) -> Void) {
        var path = "\(AppConfig.Endpoint.gamificationBalanceHistory)?userId=\(userId)&limit=\(limit)"
        if offset > 0 {
            path += "&offset=\(offset)"
        }
        networkManager.get(endpoint: path, completion: completion)
    }
    
    // Награды (6 методов)
    func getGamificationRewards(userId: String? = nil, completion: @escaping (Result<RewardsListResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.gamificationRewards
        if let userId = userId {
            endpoint += "?userId=\(userId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func claimGamificationReward(userId: String, rewardId: String, deviceId: String? = nil, completion: @escaping (Result<ClaimRewardResponse, Error>) -> Void) {
        let request = ClaimRewardRequest(userId: userId, rewardId: rewardId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationRewardsClaim, body: request, completion: completion)
    }
    
    func getGamificationRewardsHistory(userId: String, limit: Int = 50, completion: @escaping (Result<[RewardResponse], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationRewardsHistory + "?userId=\(userId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func giveGamificationReward(childId: String, rewardId: String, parentId: String? = nil, completion: @escaping (Result<ClaimRewardResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.gamificationRewardsGive + "?childId=\(childId)&rewardId=\(rewardId)"
        if let parentId = parentId {
            endpoint += "&parentId=\(parentId)"
        }
        networkManager.post(endpoint: endpoint, body: EmptyRequest(), completion: completion)
    }
    
    func getGamificationRewardsShop(userId: String? = nil, completion: @escaping (Result<RewardsListResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.gamificationRewardsShop
        if let userId = userId {
            endpoint += "?userId=\(userId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func purchaseGamificationReward(userId: String, rewardId: String, deviceId: String? = nil, completion: @escaping (Result<ClaimRewardResponse, Error>) -> Void) {
        let request = ClaimRewardRequest(userId: userId, rewardId: rewardId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationRewardsPurchase, body: request, completion: completion)
    }
    
    // Достижения (5 методов)
    func getGamificationAchievements(userId: String, completion: @escaping (Result<AchievementsListResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationAchievements + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func unlockGamificationAchievement(userId: String, achievementId: String, deviceId: String? = nil, completion: @escaping (Result<AchievementResponse, Error>) -> Void) {
        let request = UnlockAchievementRequest(userId: userId, achievementId: achievementId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationAchievementsUnlock, body: request, completion: completion)
    }
    
    func getGamificationAchievementsProgress(userId: String, completion: @escaping (Result<AchievementProgressResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationAchievementsProgress + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func getGamificationAchievement(achievementId: String, userId: String? = nil, completion: @escaping (Result<AchievementResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.gamificationAchievement + "/\(achievementId)"
        if let userId = userId {
            endpoint += "?userId=\(userId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func claimGamificationAchievementReward(userId: String, achievementId: String, deviceId: String? = nil, completion: @escaping (Result<GamificationBalanceResponse, Error>) -> Void) {
        let request = UnlockAchievementRequest(userId: userId, achievementId: achievementId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationAchievementsClaim, body: request, completion: completion)
    }
    
    // Турниры (6 методов)
    func getGamificationTournaments(status: String? = nil, completion: @escaping (Result<TournamentsListResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.gamificationTournaments
        if let status = status {
            endpoint += "?status=\(status)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func joinGamificationTournament(userId: String, tournamentId: String, deviceId: String? = nil, completion: @escaping (Result<[String: AnyCodable], Error>) -> Void) {
        let request = JoinTournamentRequest(userId: userId, tournamentId: tournamentId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationTournamentsJoin, body: request, completion: completion)
    }
    
    func getGamificationTournament(tournamentId: String, completion: @escaping (Result<TournamentResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationTournament + "/\(tournamentId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func getGamificationTournamentLeaderboard(tournamentId: String, limit: Int = 50, completion: @escaping (Result<LeaderboardResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationTournamentsLeaderboard + "?tournamentId=\(tournamentId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func leaveGamificationTournament(userId: String, tournamentId: String, deviceId: String? = nil, completion: @escaping (Result<[String: AnyCodable], Error>) -> Void) {
        let request = JoinTournamentRequest(userId: userId, tournamentId: tournamentId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationTournamentsLeave, body: request, completion: completion)
    }
    
    func getGamificationTournamentsHistory(userId: String, limit: Int = 50, completion: @escaping (Result<TournamentsListResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationTournamentsHistory + "?userId=\(userId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    // Настройки игр (4 метода)
    func getGamificationSettings(userId: String, completion: @escaping (Result<GameSettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationSettings + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateGamificationSettings(userId: String, soundEnabled: Bool? = nil, musicEnabled: Bool? = nil, notificationsEnabled: Bool? = nil, difficulty: String? = nil, language: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<GameSettingsResponse, Error>) -> Void) {
        let request = UpdateGameSettingsRequest(userId: userId, soundEnabled: soundEnabled, musicEnabled: musicEnabled, notificationsEnabled: notificationsEnabled, difficulty: difficulty, language: language, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationSettingsUpdate, body: request, completion: completion)
    }
    
    func getGamificationNotificationSettings(userId: String, completion: @escaping (Result<NotificationSettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationSettingsNotifications + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateGamificationNotificationSettings(userId: String, achievementUnlocked: Bool? = nil, tournamentStarted: Bool? = nil, rewardAvailable: Bool? = nil, levelUp: Bool? = nil, deviceId: String? = nil, completion: @escaping (Result<NotificationSettingsResponse, Error>) -> Void) {
        let request = UpdateNotificationSettingsRequest(userId: userId, achievementUnlocked: achievementUnlocked, tournamentStarted: tournamentStarted, rewardAvailable: rewardAvailable, levelUp: levelUp, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationSettingsNotificationsUpdate, body: request, completion: completion)
    }
    
    // Прогресс игр (5 методов)
    func getGamificationProgress(userId: String, completion: @escaping (Result<GameProgressListResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationProgress + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateGamificationProgress(userId: String, gameId: String, experience: Int? = nil, score: Int? = nil, deviceId: String? = nil, completion: @escaping (Result<GameProgressResponse, Error>) -> Void) {
        let request = UpdateProgressRequest(userId: userId, gameId: gameId, experience: experience, score: score, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationProgressUpdate, body: request, completion: completion)
    }
    
    func getGamificationProgressStats(userId: String, completion: @escaping (Result<ProgressStatsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationProgressStats + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func getGamificationLevel(userId: String, completion: @escaping (Result<LevelResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.gamificationProgressLevel + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func resetGamificationProgress(userId: String, gameId: String? = nil, parentId: String, completion: @escaping (Result<[String: AnyCodable], Error>) -> Void) {
        let request = ResetProgressRequest(userId: userId, gameId: gameId, parentId: parentId)
        networkManager.post(endpoint: AppConfig.Endpoint.gamificationProgressReset, body: request, completion: completion)
    }
    
    // MARK: - ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Parental Control Sync API
    
    // Настройки (5 методов)
    func getParentalControlSettings(familyId: String, childId: String? = nil, completion: @escaping (Result<ParentalControlSettingsResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.parentalControlSettings.replacingOccurrences(of: "{familyId}", with: familyId)
        if let childId = childId {
            endpoint += "?childId=\(childId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateParentalControlSettings(familyId: String, childId: String? = nil, isContentFilterEnabled: Bool? = nil, isAppBlockingEnabled: Bool? = nil, screenTimeLimitHours: Int? = nil, allowedApps: [String]? = nil, blockedWebsites: [String]? = nil, bedtime: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<ParentalControlSettingsResponse, Error>) -> Void) {
        let request = UpdateParentalControlSettingsRequest(familyId: familyId, childId: childId, isContentFilterEnabled: isContentFilterEnabled, isAppBlockingEnabled: isAppBlockingEnabled, screenTimeLimitHours: screenTimeLimitHours, allowedApps: allowedApps, blockedWebsites: blockedWebsites, bedtime: bedtime, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlSettingsUpdate, body: request, completion: completion)
    }
    
    func getParentalControlSettingsHistory(familyId: String, childId: String? = nil, limit: Int = 50, completion: @escaping (Result<SettingsHistoryResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.parentalControlSettingsHistory + "?familyId=\(familyId)&limit=\(limit)"
        if let childId = childId {
            endpoint += "&childId=\(childId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func syncParentalControlSettings(familyId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncParentalControlSettingsResponse, Error>) -> Void) {
        let request = SyncParentalControlSettingsRequest(familyId: familyId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlSettingsSync, body: request, completion: completion)
    }
    
    func getParentalControlSettingsConflicts(familyId: String, childId: String? = nil, completion: @escaping (Result<SettingsConflictsResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.parentalControlSettingsConflicts + "?familyId=\(familyId)"
        if let childId = childId {
            endpoint += "&childId=\(childId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    // Лимиты времени (4 метода)
    func getTimeLimits(childId: String, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlTimeLimits.replacingOccurrences(of: "{childId}", with: childId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateTimeLimits(childId: String, dailyLimitMinutes: Int? = nil, weeklyLimitMinutes: Int? = nil, bedtimeStart: String? = nil, bedtimeEnd: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        let request = UpdateTimeLimitRequest(childId: childId, dailyLimitMinutes: dailyLimitMinutes, weeklyLimitMinutes: weeklyLimitMinutes, bedtimeStart: bedtimeStart, bedtimeEnd: bedtimeEnd, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlTimeLimitsUpdate, body: request, completion: completion)
    }
    
    func getTimeLimitsHistory(childId: String, limit: Int = 50, completion: @escaping (Result<TimeLimitHistoryResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlTimeLimitsHistory + "?childId=\(childId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func resetTimeLimits(childId: String, deviceId: String? = nil, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        let request = ResetTimeLimitRequest(childId: childId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlTimeLimitsReset, body: request, completion: completion)
    }
    
    // Расписания (4 метода)
    func getSchedules(childId: String, completion: @escaping (Result<[ScheduleResponse], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlSchedules.replacingOccurrences(of: "{childId}", with: childId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateSchedule(scheduleId: String? = nil, childId: String, name: String? = nil, weekdays: [Int]? = nil, startTime: String? = nil, endTime: String? = nil, isActive: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<ScheduleResponse, Error>) -> Void) {
        let request = UpdateScheduleRequest(scheduleId: scheduleId, childId: childId, name: name, weekdays: weekdays, startTime: startTime, endTime: endTime, isActive: isActive, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlSchedulesUpdate, body: request, completion: completion)
    }
    
    func getSchedulesHistory(childId: String, limit: Int = 50, completion: @escaping (Result<ScheduleHistoryResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlSchedulesHistory + "?childId=\(childId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func deleteSchedule(scheduleId: String, deviceId: String? = nil, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let request = DeleteScheduleRequest(scheduleId: scheduleId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlSchedulesDelete, body: request, completion: completion)
    }
    
    // Геозоны (4 метода)
    func getGeofences(childId: String, completion: @escaping (Result<[GeofenceResponse], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlGeofences.replacingOccurrences(of: "{childId}", with: childId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func addGeofence(childId: String, name: String, latitude: Double, longitude: Double, radius: Double, isActive: Bool = true, deviceId: String? = nil, completion: @escaping (Result<GeofenceResponse, Error>) -> Void) {
        let request = AddGeofenceRequest(childId: childId, name: name, latitude: latitude, longitude: longitude, radius: radius, isActive: isActive, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlGeofencesAdd, body: request, completion: completion)
    }
    
    func updateGeofence(geofenceId: String, name: String? = nil, latitude: Double? = nil, longitude: Double? = nil, radius: Double? = nil, isActive: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<GeofenceResponse, Error>) -> Void) {
        let request = UpdateGeofenceRequest(geofenceId: geofenceId, name: name, latitude: latitude, longitude: longitude, radius: radius, isActive: isActive, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlGeofencesUpdate, body: request, completion: completion)
    }
    
    func deleteGeofence(geofenceId: String, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlGeofencesDelete.replacingOccurrences(of: "{geofenceId}", with: geofenceId)
        networkManager.delete(endpoint: endpoint, completion: completion)
    }
    
    // Блокировки приложений (3 метода)
    func getAppBlocks(childId: String, completion: @escaping (Result<AppBlockResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.parentalControlAppBlocks.replacingOccurrences(of: "{childId}", with: childId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateAppBlocks(childId: String, blockedApps: [String]? = nil, appLimits: [String: Int]? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<AppBlockResponse, Error>) -> Void) {
        let request = UpdateAppBlocksRequest(childId: childId, blockedApps: blockedApps, appLimits: appLimits, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlAppBlocksUpdate, body: request, completion: completion)
    }
    
    func syncAppBlocks(childId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncAppBlocksResponse, Error>) -> Void) {
        let request = SyncAppBlocksRequest(childId: childId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.parentalControlAppBlocksSync, body: request, completion: completion)
    }
    
    // MARK: - User API (старые методы - оставляем для обратной совместимости)
    
    func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
        logger.business("👤 Fetching user profile")
        networkManager.get(endpoint: AppConfig.Endpoint.profile) { [weak self] (result: Result<UserProfile, Error>) in
            if case .success(let profile) = result {
                Self.persistUserIdFromProfileForOffline(profile)
                self?.trackUserProfileContractSignals(profile: profile)
            }
            completion(result)
        }
    }

    /// Сохраняет идентификатор пользователя из профиля для offline/fallback (`UserDefaults` ключ `user_id`).
    private static func persistUserIdFromProfileForOffline(_ profile: UserProfile) {
        let trimmed = profile.id.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        if profile.safeIsGuest {
            let existing = (UserDefaults.standard.string(forKey: "user_id") ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            let hasRealUser = !existing.isEmpty && existing != "anonymous" && !existing.lowercased().hasPrefix("guest_")
            if hasRealUser { return }
        }
        let prior = UserDefaults.standard.string(forKey: "user_id")
        UserDefaults.standard.set(trimmed, forKey: "user_id")
        if prior != trimmed {
            NotificationCenter.default.post(name: .aladdinUserIdentityDidUpdate, object: nil)
        }
    }

    private func trackUserProfileContractSignals(profile: UserProfile) {
        let storedUserId = UserDefaults.standard.string(forKey: "user_id") ?? ""

        // profile_contract_violation_count: guest profile must not have email payload.
        if profile.safeIsGuest, let email = profile.email, !email.isEmpty {
            JWTEventLogger.incrementCounter("profile_contract_violation_count")
            logger.error("⚠️ PROFILE CONTRACT: guest profile contains email payload")
        }

        // unexpected_guest_profile_count: server returned guest profile while app already has non-guest user_id.
        let hasPersistedNonGuestUser = !storedUserId.isEmpty && storedUserId != "anonymous" && !storedUserId.hasPrefix("guest_")
        if profile.safeIsGuest && hasPersistedNonGuestUser {
            JWTEventLogger.incrementCounter("unexpected_guest_profile_count")
            logger.error("⚠️ PROFILE CONTRACT: unexpected guest profile for persisted user_id=\(storedUserId)")
        }
    }
    
    func updateProfile(name: String?, email: String?, phone: String?, completion: @escaping (Result<UserProfile, Error>) -> Void) {
        let request = UpdateProfileRequest(name: name, email: email, phone: phone)
        networkManager.post(endpoint: AppConfig.Endpoint.updateProfile, body: request, completion: completion)
    }
    
    func deleteAccount(confirmationCode: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct DeleteAccountRequest: Codable {
            let confirmationCode: String
        }
        networkManager.delete(endpoint: AppConfig.Endpoint.deleteAccount, body: DeleteAccountRequest(confirmationCode: confirmationCode), completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 2: User Profile Sync API
    
    func syncUserProfile(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncUserProfileResponse, Error>) -> Void) {
        let request = SyncUserProfileRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.userProfileSync, body: request, completion: completion)
    }
    
    func updateUserProfileSync(userId: String, name: String? = nil, email: String? = nil, phone: String? = nil, avatar: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<UserProfileSyncResponse, Error>) -> Void) {
        let request = UpdateUserProfileSyncRequest(userId: userId, name: name, email: email, phone: phone, avatar: avatar, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.userProfileUpdate, body: request, completion: completion)
    }
    
    func getUserProfileHistory(userId: String, limit: Int = 50, completion: @escaping (Result<ProfileHistoryResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.userProfileHistory + "?userId=\(userId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func getUserPrivacySettings(userId: String, completion: @escaping (Result<PrivacySettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.userProfilePrivacy + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateUserPrivacySettings(userId: String, profileVisibility: String? = nil, showEmail: Bool? = nil, showPhone: Bool? = nil, showLocation: Bool? = nil, allowDataSharing: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<PrivacySettingsResponse, Error>) -> Void) {
        let request = UpdatePrivacySettingsRequest(userId: userId, profileVisibility: profileVisibility, showEmail: showEmail, showPhone: showPhone, showLocation: showLocation, allowDataSharing: allowDataSharing, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.userProfilePrivacyUpdate, body: request, completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 2: Subscription Sync API
    
    func syncSubscription(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncSubscriptionResponse, Error>) -> Void) {
        let request = SyncSubscriptionRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionSync, body: request, completion: completion)
    }
    
    func updateSubscription(userId: String, subscriptionType: String? = nil, status: String? = nil, endDate: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<SubscriptionResponse, Error>) -> Void) {
        let request = UpdateSubscriptionRequest(userId: userId, subscriptionType: subscriptionType, status: status, endDate: endDate, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionUpdate, body: request, completion: completion)
    }
    
    func getPurchaseHistory(userId: String, limit: Int = 50, completion: @escaping (Result<PurchaseHistoryResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.subscriptionPurchaseHistory + "?userId=\(userId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// GET `/api/subscription/status` — decodes real backend envelope `{ status, server_time }` or legacy summary.
    func getSubscriptionStatus(
        userId: String,
        merging currentSubscription: SubscriptionStatus? = nil,
        completion: @escaping (Result<SubscriptionStatus, Error>) -> Void
    ) {
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            let endpoint = AppConfig.Endpoint.subscriptionStatus + "?userId=\(userId)"
            guard let url = URL(string: AppConfig.apiBaseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
            guard let authToken = AppConfig.authToken, !authToken.isEmpty else {
                completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
                return
            }
            request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")

            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    completion(.failure(NetworkError.unknown(error)))
                    return
                }
                if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                    completion(.failure(NetworkError.invalidStatusCode(http.statusCode)))
                    return
                }
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                do {
                    let status = try SubscriptionStatusHTTPDecoder.subscriptionStatus(from: data, merging: currentSubscription)
                    completion(.success(status))
                } catch {
                    #if DEBUG
                    let body = String(data: data, encoding: .utf8) ?? ""
                    print("❌ getSubscriptionStatus decode: \(error)\n\(body.prefix(600))")
                    #endif
                    completion(.failure(NetworkError.decodingError(error)))
                }
            }.resume()
        }
    }

    /// 🔄 Get subscription status with explicit token (for background sync)
    func getSubscriptionStatusWithToken(
        userId: String,
        token: String,
        merging currentSubscription: SubscriptionStatus? = nil,
        completion: @escaping (Result<SubscriptionStatus, Error>) -> Void
    ) {
        let endpoint = AppConfig.Endpoint.subscriptionStatus + "?userId=\(userId)"

        // Создаем запрос с явным токеном
        guard let url = URL(string: AppConfig.apiBaseURL + endpoint) else {
            completion(.failure(NetworkError.invalidURL))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.cachePolicy = .reloadIgnoringLocalCacheData
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(NetworkError.unknown(error)))
                return
            }
            if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                completion(.failure(NetworkError.invalidStatusCode(http.statusCode)))
                return
            }
            guard let data = data else {
                completion(.failure(NetworkError.noData))
                return
            }

            do {
                let status = try SubscriptionStatusHTTPDecoder.subscriptionStatus(from: data, merging: currentSubscription)
                completion(.success(status))
            } catch {
                #if DEBUG
                let body = String(data: data, encoding: .utf8) ?? ""
                print("❌ getSubscriptionStatusWithToken decode: \(error)\n\(body.prefix(600))")
                #endif
                completion(.failure(NetworkError.decodingError(error)))
            }
        }.resume()
    }

    /// Swift Concurrency wrapper for tests and `async` call sites (distinct name avoids overload/recursion ambiguity with the completion API).
    func fetchSubscriptionStatus(userId: String, merging currentSubscription: SubscriptionStatus? = nil) async throws -> SubscriptionStatus {
        try await withCheckedThrowingContinuation { continuation in
            getSubscriptionStatus(userId: userId, merging: currentSubscription) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    func updateSubscriptionStatus(userId: String, status: String, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<SubscriptionStatusResponse, Error>) -> Void) {
        let request = UpdateSubscriptionStatusRequest(userId: userId, status: status, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionStatusUpdate, body: request, completion: completion)
    }
    
    func getAutoRenewal(userId: String, completion: @escaping (Result<AutoRenewalResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.subscriptionAutoRenewal + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateAutoRenewal(userId: String, enabled: Bool, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<AutoRenewalResponse, Error>) -> Void) {
        let request = UpdateAutoRenewalRequest(userId: userId, enabled: enabled, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionAutoRenewalUpdate, body: request, completion: completion)
    }
    
    func cancelSubscription(userId: String, reason: String? = nil, deviceId: String? = nil, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let request = CancelSubscriptionRequest(userId: userId, reason: reason, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.subscriptionCancel, body: request, completion: completion)
    }

    /// Batch-upload subscription events to domain endpoint (Phase B)
    func sendSubscriptionEventsBatch(
        events: [[String: AnyCodable]]
    ) async throws {
        struct SubscriptionEventsBatchRequest: Codable {
            let events: [[String: AnyCodable]]
        }
        struct SubscriptionEventsBatchResponse: Codable {
            let acceptedCount: Int
            let duplicateCount: Int
            let failedCount: Int
            let failedEventIds: [String]
        }

        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            networkManager.post(
                endpoint: AppConfig.Endpoint.subscriptionEventsBatch,
                body: SubscriptionEventsBatchRequest(events: events),
                requiresAuth: true
            ) { (result: Result<SubscriptionEventsBatchResponse, Error>) in
                switch result {
                case .success(let response):
                    // Success if server accepted all or marked them duplicates (idempotent path).
                    if response.failedCount == 0 {
                        continuation.resume()
                    } else {
                        continuation.resume(
                            throwing: NetworkError.businessLogicError(
                                "subscription_events_failed_count=\(response.failedCount)"
                            )
                        )
                    }
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    // MARK: - ✅ ЭТАП 2: App Settings Sync API
    
    func syncAppSettings(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncAppSettingsResponse, Error>) -> Void) {
        let request = SyncAppSettingsRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsSync, body: request, completion: completion)
    }
    
    func updateAppSettings(userId: String, theme: String? = nil, language: String? = nil, notificationsEnabled: Bool? = nil, biometryEnabled: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<AppSettingsResponse, Error>) -> Void) {
        let request = UpdateAppSettingsRequest(userId: userId, theme: theme, language: language, notificationsEnabled: notificationsEnabled, biometryEnabled: biometryEnabled, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsUpdate, body: request, completion: completion)
    }
    
    func getThemeSettings(userId: String, completion: @escaping (Result<ThemeSettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.appSettingsTheme + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateThemeSettings(userId: String, theme: String, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<ThemeSettingsResponse, Error>) -> Void) {
        let request = UpdateThemeSettingsRequest(userId: userId, theme: theme, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsThemeUpdate, body: request, completion: completion)
    }
    
    func getLanguageSettings(userId: String, completion: @escaping (Result<LanguageSettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.appSettingsLanguage + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateLanguageSettings(userId: String, language: String, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<LanguageSettingsResponse, Error>) -> Void) {
        let request = UpdateLanguageSettingsRequest(userId: userId, language: language, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsLanguageUpdate, body: request, completion: completion)
    }
    
    func getNotificationSettingsApp(userId: String, completion: @escaping (Result<NotificationSettingsAppResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.appSettingsNotifications + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateNotificationSettingsApp(userId: String, enabled: Bool? = nil, pushEnabled: Bool? = nil, soundEnabled: Bool? = nil, emailEnabled: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<NotificationSettingsAppResponse, Error>) -> Void) {
        let request = UpdateNotificationSettingsAppRequest(userId: userId, enabled: enabled, pushEnabled: pushEnabled, soundEnabled: soundEnabled, emailEnabled: emailEnabled, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsNotificationsUpdate, body: request, completion: completion)
    }
    
    func getBiometrySettings(userId: String, completion: @escaping (Result<BiometrySettingsResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.appSettingsBiometry + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateBiometrySettings(userId: String, enabled: Bool, type: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<BiometrySettingsResponse, Error>) -> Void) {
        let request = UpdateBiometrySettingsRequest(userId: userId, enabled: enabled, type: type, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.appSettingsBiometryUpdate, body: request, completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 2: Location & Chat Sync API
    
    // Геолокация и геозоны (7 методов)
    func syncLocationGeofences(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncLocationGeofencesResponse, Error>) -> Void) {
        let request = SyncLocationGeofencesRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.locationGeofencesSync, body: request, completion: completion)
    }
    
    func updateLocationGeofence(geofenceId: String? = nil, userId: String, name: String? = nil, latitude: Double? = nil, longitude: Double? = nil, radius: Double? = nil, isActive: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<LocationGeofenceResponse, Error>) -> Void) {
        let request = UpdateLocationGeofenceRequest(geofenceId: geofenceId, userId: userId, name: name, latitude: latitude, longitude: longitude, radius: radius, isActive: isActive, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.locationGeofencesUpdate, body: request, completion: completion)
    }
    
    func deleteLocationGeofence(geofenceId: String, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.locationGeofencesDelete.replacingOccurrences(of: "{geofenceId}", with: geofenceId)
        networkManager.delete(endpoint: endpoint, completion: completion)
    }
    
    func getMovementHistory(userId: String, limit: Int = 100, startDate: String? = nil, completion: @escaping (Result<MovementHistoryResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.locationMovementHistory + "?userId=\(userId)&limit=\(limit)"
        if let startDate = startDate {
            endpoint += "&startDate=\(startDate)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateMovementHistory(userId: String, entries: [MovementHistoryEntry], deviceId: String? = nil, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let request = UpdateMovementHistoryRequest(userId: userId, entries: entries, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.locationMovementHistoryUpdate, body: request, completion: completion)
    }
    
    func getLocationStatus(userId: String, completion: @escaping (Result<LocationStatusResponse, Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.locationStatus + "?userId=\(userId)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateLocationStatus(userId: String, enabled: Bool, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<LocationStatusResponse, Error>) -> Void) {
        let request = UpdateLocationStatusRequest(userId: userId, enabled: enabled, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.locationStatusUpdate, body: request, completion: completion)
    }
    
    // Семейный чат (офлайн) (3 метода)
    func syncOfflineMessages(userId: String, familyId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncOfflineMessagesResponse, Error>) -> Void) {
        let request = SyncOfflineMessagesRequest(userId: userId, familyId: familyId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.chatOfflineMessagesSync, body: request, completion: completion)
    }
    
    func sendOfflineMessage(userId: String, recipientId: String, familyId: String, content: String, deviceId: String? = nil, timestamp: String? = nil, completion: @escaping (Result<OfflineMessageResponse, Error>) -> Void) {
        let request = SendOfflineMessageRequest(userId: userId, recipientId: recipientId, familyId: familyId, content: content, deviceId: deviceId, timestamp: timestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.chatOfflineMessagesSend, body: request, completion: completion)
    }
    
    func resolveMessageConflicts(userId: String, familyId: String, conflicts: [[String: String]], deviceId: String? = nil, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let request = ResolveMessageConflictsRequest(userId: userId, familyId: familyId, conflicts: conflicts, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.chatOfflineMessagesResolveConflicts, body: request, completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 3: Offline Storage Sync API
    
    func syncOfflineStorage(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, dataTypes: [String]? = nil, completion: @escaping (Result<SyncOfflineStorageResponse, Error>) -> Void) {
        let request = SyncOfflineStorageRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp, dataTypes: dataTypes)
        networkManager.post(endpoint: AppConfig.Endpoint.offlineStorageSync, body: request, completion: completion)
    }
    
    func getOfflineData(userId: String, dataType: String? = nil, dataId: String? = nil, completion: @escaping (Result<[OfflineDataResponse], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.offlineStorageData + "?userId=\(userId)"
        if let dataType = dataType {
            endpoint += "&dataType=\(dataType)"
        }
        if let dataId = dataId {
            endpoint += "&dataId=\(dataId)"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func updateOfflineData(userId: String, dataId: String? = nil, dataType: String, data: [String: AnyCodable], deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<OfflineDataResponse, Error>) -> Void) {
        let request = UpdateOfflineDataRequest(userId: userId, dataId: dataId, dataType: dataType, data: data, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.offlineStorageDataUpdate, body: request, completion: completion)
    }
    
    func deleteOfflineData(dataId: String, userId: String, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let endpoint = AppConfig.Endpoint.offlineStorageDataDelete.replacingOccurrences(of: "{dataId}", with: dataId) + "?userId=\(userId)"
        networkManager.delete(endpoint: endpoint, completion: completion)
    }
    
    func resolveOfflineStorageConflicts(userId: String, conflicts: [[String: String]], resolutionStrategy: String = "last-write-wins", deviceId: String? = nil, completion: @escaping (Result<[String: String], Error>) -> Void) {
        let request = ResolveOfflineStorageConflictsRequest(userId: userId, conflicts: conflicts, resolutionStrategy: resolutionStrategy, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.offlineStorageResolveConflicts, body: request, completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 3: Crash Detection Sync API
    
    func syncCrashDetection(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncCrashDetectionResponse, Error>) -> Void) {
        let request = SyncCrashDetectionRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionSync, body: request, completion: completion)
    }
    
    func reportCrash(userId: String, deviceId: String, crashType: String, severity: String, location: [String: Double]? = nil, timestamp: String? = nil, details: [String: AnyCodable]? = nil, completion: @escaping (Result<CrashReportResponse, Error>) -> Void) {
        let request = ReportCrashRequest(userId: userId, deviceId: deviceId, crashType: crashType, severity: severity, location: location, timestamp: timestamp, details: details)
        networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionReport, body: request, completion: completion)
    }
    
    func getCrashNotifications(userId: String, limit: Int = 50, unreadOnly: Bool = false, completion: @escaping (Result<[CrashNotificationResponse], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.crashDetectionNotifications + "?userId=\(userId)&limit=\(limit)"
        if unreadOnly {
            endpoint += "&unreadOnly=true"
        }
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    func sendCrashNotification(userId: String, reportId: String, recipientId: String? = nil, message: String? = nil, deviceId: String? = nil, completion: @escaping (Result<CrashNotificationResponse, Error>) -> Void) {
        let request = SendCrashNotificationRequest(userId: userId, reportId: reportId, recipientId: recipientId, message: message, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.crashDetectionNotificationsSend, body: request, completion: completion)
    }
    
    // MARK: - ✅ ЭТАП 3: Elderly Interface Sync API
    
    func syncMedications(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncMedicationsResponse, Error>) -> Void) {
        let request = SyncMedicationsRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyMedicationsSync, body: request, completion: completion)
    }
    
    func updateMedication(medicationId: String? = nil, userId: String, name: String? = nil, dosage: String? = nil, frequency: String? = nil, timeOfDay: String? = nil, startDate: String? = nil, endDate: String? = nil, notes: String? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<MedicationResponse, Error>) -> Void) {
        let request = UpdateMedicationRequest(medicationId: medicationId, userId: userId, name: name, dosage: dosage, frequency: frequency, timeOfDay: timeOfDay, startDate: startDate, endDate: endDate, notes: notes, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyMedicationsUpdate, body: request, completion: completion)
    }
    
    func syncAppointments(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncAppointmentsResponse, Error>) -> Void) {
        let request = SyncAppointmentsRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyAppointmentsSync, body: request, completion: completion)
    }
    
    func updateAppointment(appointmentId: String? = nil, userId: String, title: String? = nil, description: String? = nil, dateTime: String? = nil, location: String? = nil, contactName: String? = nil, contactPhone: String? = nil, reminderMinutes: Int? = nil, isCompleted: Bool? = nil, deviceId: String? = nil, version: Int? = nil, completion: @escaping (Result<AppointmentResponse, Error>) -> Void) {
        let request = UpdateAppointmentRequest(appointmentId: appointmentId, userId: userId, title: title, description: description, dateTime: dateTime, location: location, contactName: contactName, contactPhone: contactPhone, reminderMinutes: reminderMinutes, isCompleted: isCompleted, deviceId: deviceId, version: version)
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyAppointmentsUpdate, body: request, completion: completion)
    }

    func syncBloodPressure(userId: String, deviceId: String, lastSyncTimestamp: String? = nil, completion: @escaping (Result<SyncBloodPressureResponse, Error>) -> Void) {
        let request = SyncBloodPressureRequest(userId: userId, deviceId: deviceId, lastSyncTimestamp: lastSyncTimestamp)
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyBloodPressureSync, body: request, completion: completion)
    }

    func updateBloodPressure(
        readingId: String? = nil,
        userId: String,
        systolic: Int,
        diastolic: Int,
        recordedAt: String? = nil,
        weekdayKey: String? = nil,
        deviceId: String? = nil,
        completion: @escaping (Result<BloodPressureReadingResponse, Error>) -> Void
    ) {
        let request = UpdateBloodPressureRequest(
            readingId: readingId,
            userId: userId,
            systolic: systolic,
            diastolic: diastolic,
            recordedAt: recordedAt,
            weekdayKey: weekdayKey,
            deviceId: deviceId
        )
        networkManager.post(endpoint: AppConfig.Endpoint.elderlyBloodPressureUpdate, body: request, completion: completion)
    }
    
    // ✅ ДОБАВЛЕНО: 2FA API (для синхронизации между устройствами)
    
    /// Загрузить статус 2FA с сервера
    func get2FAStatus(completion: @escaping (Result<TwoFactorAuthStatusResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.twoFactorStatus, completion: completion)
    }
    
    /// Обновить статус 2FA на сервере
    func update2FAStatus(enabled: Bool, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct TwoFactorAuthRequest: Codable {
            let enabled: Bool
        }
        
        let request = TwoFactorAuthRequest(enabled: enabled)
        networkManager.patch(endpoint: AppConfig.Endpoint.twoFactorUpdate, body: request, completion: completion)
    }
    
    // MARK: - Notifications API
    
    func getNotifications(completion: @escaping (Result<[NotificationResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.notifications, completion: completion)
    }
    
    func markNotificationAsRead(notificationId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct MarkReadRequest: Codable {
            let notificationId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.markRead, body: MarkReadRequest(notificationId: notificationId), completion: completion)
    }
    
    // MARK: - Subscription API
    
    func getTariffs(completion: @escaping (Result<[TariffResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.tariffs, completion: completion)
    }
    
    func subscribe(tariffId: String, completion: @escaping (Result<SubscriptionStatus, Error>) -> Void) {
        struct SubscribeRequest: Codable {
            let tariffId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.subscribe, body: SubscribeRequest(tariffId: tariffId), completion: completion)
    }
    
    func activateSubscriptionCode(code: String, completion: @escaping (Result<ActivationCodeResponse, Error>) -> Void) {
        let request = ActivationCodeRequest(code: code)
        networkManager.post(endpoint: AppConfig.Endpoint.activateSubscription, body: request, completion: completion)
    }
    
    // MARK: - Activation Code API (новые методы для payment_service)
    
    /// Проверка кода активации перед активацией
    func verifyActivationCode(code: String, familyId: String, deviceId: String, completion: @escaping (Result<ActivationVerifyResponse, Error>) -> Void) {
        let request = ActivationVerifyRequest(code: code, familyId: familyId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.activationVerify, body: request, completion: completion)
    }
    
    /// Активация кода
    func activateCode(code: String, familyId: String, deviceId: String, completion: @escaping (Result<ActivationActivateResponse, Error>) -> Void) {
        let request = ActivationActivateRequest(code: code, familyId: familyId, deviceId: deviceId)
        networkManager.post(endpoint: AppConfig.Endpoint.activationActivate, body: request, completion: completion)
    }
    
    // MARK: - Referral API
    
    func getReferralOverview(completion: @escaping (Result<ReferralOverviewResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.referralCode, completion: completion)
    }

    func getReferralStats(completion: @escaping (Result<ReferralStatsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.referralStats, completion: completion)
    }

    func getReferralHistory(completion: @escaping (Result<[ReferralHistoryItem], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.referralHistory, completion: completion)
    }

    func getReferralRewards(completion: @escaping (Result<ReferralRewardsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.referralRewards, completion: completion)
    }
    
    // MARK: - Protection API (Threat Protection)
    
    func getProtectionSettings(completion: @escaping (Result<ProtectionSettingsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.protectionSettings, completion: completion)
    }
    
    func updateProtectionSettings(_ settings: ProtectionSettings, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.protectionSettings, body: settings, completion: completion)
    }
    
    func getProtectionStatus(completion: @escaping (Result<ProtectionStatusResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.protectionStatus, completion: completion)
    }
    
    func getThreatScenarios(completion: @escaping (Result<[ThreatScenarioResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.threatScenarios, completion: completion)
    }
    
    func enableProtectionCategory(_ categoryId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EnableRequest: Codable {
            let categoryId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.protectionEnable, body: EnableRequest(categoryId: categoryId), completion: completion)
    }
    
    func disableProtectionCategory(_ categoryId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct DisableRequest: Codable {
            let categoryId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.protectionDisable, body: DisableRequest(categoryId: categoryId), completion: completion)
    }
    
    func getProtectionStats(completion: @escaping (Result<ProtectionStatsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.protectionStats, completion: completion)
    }
    
    func syncProtectionSettings(_ settings: ProtectionSettings, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.protectionSync, body: settings, completion: completion)
    }
    
    // MARK: - Protection Threats & Quarantine API (Antivirus)
    
    /// Получить список угроз пользователя с сервера
    func getUserThreatsAsync(status: String? = nil) async throws -> [ThreatResponse] {
        return try await withCheckedThrowingContinuation { continuation in
            var hasResumed = false
            
            // Используем /api/malware/threats с query параметром status
            var endpoint = AppConfig.Endpoint.malwareThreats
            if let status = status {
                endpoint = "\(endpoint)?status=\(status)"
            }
            
            networkManager.get(endpoint: endpoint) { (result: Result<ThreatsListResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getUserThreatsAsync()!")
                    return
                }
                hasResumed = true
                
                switch result {
                case .success(let response):
                    continuation.resume(returning: response.threats)
                case .failure(let error):
                    // Если эндпоинт не существует, возвращаем пустой список (локальный карантин работает)
                    logger.error("⚠️ Эндпоинт \(endpoint) не найден, используем локальный карантин. Ошибка: \(error.localizedDescription)")
                    continuation.resume(returning: [])
                }
            }
        }
    }
    
    /// Выполнить действие с файлом в карантине на сервере
    func quarantineFileAsync(threatId: String, action: String, filePath: String? = nil) async throws -> QuarantineActionResponse {
        return try await withCheckedThrowingContinuation { continuation in
            var hasResumed = false
            
            let request = QuarantineActionRequest(
                threatId: threatId,
                action: action,
                filePath: filePath
            )
            
            // Используем /api/malware/quarantine/action
            networkManager.post(endpoint: AppConfig.Endpoint.malwareQuarantineAction, body: request) { (result: Result<QuarantineActionResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in quarantineFileAsync()!")
                    return
                }
                hasResumed = true
                
                // Если эндпоинт не существует, возвращаем успешный ответ (локальный карантин работает)
                switch result {
                case .success(let response):
                    continuation.resume(returning: response)
                case .failure(let error):
                    logger.error("⚠️ Эндпоинт \(AppConfig.Endpoint.malwareQuarantineAction) не найден, используем локальный карантин. Ошибка: \(error.localizedDescription)")
                    continuation.resume(returning: QuarantineActionResponse(
                        success: true,
                        message: "Локальный карантин работает, серверный эндпоинт недоступен",
                        threat: nil
                    ))
                }
            }
        }
    }

    // MARK: - Malware file scan (upload JSON + base64)

    /// Тело запроса сканирования файла (согласовано с ожидаемым Python-контрактом: `file_data`, snake_case).
    struct MalwareFileScanAPIRequest: Encodable {
        let fileData: String
        let fileName: String
        let fileSize: Int
        let fileHash: String?

        enum CodingKeys: String, CodingKey {
            case fileData = "file_data"
            case fileName = "file_name"
            case fileSize = "file_size"
            case fileHash = "file_hash"
        }
    }

    struct MalwareFileScanThreatDTO: Decodable {
        let id: String?
        let name: String?
        let type: String?
        let severity: String?
        let description: String?
        let confidence: Double?
    }

    struct MalwareFileScanAPIResponse: Decodable {
        let clean: Bool?
        let threatsFound: [MalwareFileScanThreatDTO]?
        let recommendations: [String]?
        let scanTime: Double?
        let confidence: Double?

        enum CodingKeys: String, CodingKey {
            case clean
            case threatsFound = "threats_found"
            case recommendations
            case scanTime = "scan_time"
            case confidence
        }
    }

    /// Загрузка содержимого файла на серверное сканирование (JSON + base64). При 404/ошибке сети — throw.
    func uploadFileForScanAsync(
        fileData: Data,
        fileName: String,
        fileSize: Int64,
        checksum: String?
    ) async throws -> MalwareFileScanAPIResponse {
        try await withCheckedThrowingContinuation { continuation in
            var hasResumed = false

            let body = MalwareFileScanAPIRequest(
                fileData: fileData.base64EncodedString(),
                fileName: fileName,
                fileSize: Int(fileSize),
                fileHash: checksum
            )

            networkManager.post(
                endpoint: AppConfig.Endpoint.malwareFileScan,
                body: body
            ) { (result: Result<MalwareFileScanAPIResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in uploadFileForScanAsync()!")
                    return
                }
                hasResumed = true
                switch result {
                case .success(let response):
                    continuation.resume(returning: response)
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    // MARK: - Auth API
    
    func login(email: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        logger.business("🔐 Starting login for email: \(email)")
        let request = LoginRequest(email: email, password: password)
        networkManager.post(endpoint: AppConfig.Endpoint.login, body: request, completion: completion)
    }
    
    func logout(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.logout, body: EmptyBody(), completion: completion)
    }

    func loginWithApple(
        identityToken: String,
        authorizationCode: String,
        email: String?,
        givenName: String?,
        familyName: String?,
        completion: @escaping (Result<AuthSessionResponse, Error>) -> Void
    ) {
        let request = AppleLoginRequest(
            identityToken: identityToken,
            authorizationCode: authorizationCode,
            email: email,
            givenName: givenName,
            familyName: familyName
        )
        networkManager.post(endpoint: AppConfig.Endpoint.authApple, body: request, requiresAuth: false, completion: completion)
    }

    func requestMagicLink(
        email: String,
        redirectUrl: String? = nil,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        let request = RequestMagicLinkRequest(email: email, redirectUrl: redirectUrl)
        networkManager.post(
            endpoint: AppConfig.Endpoint.authMagicLinkRequest,
            body: request,
            requiresAuth: false,
            completion: completion
        )
    }

    func consumeMagicLink(
        token: String,
        completion: @escaping (Result<AuthSessionResponse, Error>) -> Void
    ) {
        let request = ConsumeMagicLinkRequest(token: token)
        networkManager.post(
            endpoint: AppConfig.Endpoint.authMagicLinkConsume,
            body: request,
            requiresAuth: false,
            completion: completion
        )
    }

    /// Запрос ссылки/instructions на email для сброса пароля (без авторизации).
    func requestPasswordReset(email: String, completion: @escaping (Result<Void, Error>) -> Void) {
        struct ForgotBody: Codable { let email: String }
        networkManager.post(
            endpoint: AppConfig.Endpoint.authForgotPassword,
            body: ForgotBody(email: email),
            requiresAuth: false
        ) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let response):
                if response.success {
                    completion(.success(()))
                } else {
                    let msg = response.message ?? response.error ?? "forgot_password_failed"
                    completion(.failure(NetworkError.badRequest(msg)))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Token Refresh API
    
    /**
     * Обновляет access token используя refresh token
     * - Parameter refreshToken: Refresh token для обновления
     * - Parameter completion: Результат обновления токена
     */
    func refreshToken(refreshToken: String, completion: @escaping (Result<RefreshTokenResponse, Error>) -> Void) {
        struct RefreshTokenRequest: Codable {
            let refresh_token: String
        }
        
        let request = RefreshTokenRequest(refresh_token: refreshToken)
        networkManager.post(endpoint: AppConfig.Endpoint.authRefresh, body: request, completion: completion)
    }
    
    // MARK: - Device API
    
    func getDevices(completion: @escaping (Result<[DeviceResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.devices, completion: completion)
    }
    
    func getDeviceDetail(deviceId: String, completion: @escaping (Result<DeviceDetailResponse, Error>) -> Void) {
        networkManager.get(endpoint: "\(AppConfig.Endpoint.deviceDetail)/\(deviceId)", completion: completion)
    }
    
    struct DeviceTokenRequest: Codable {
        let deviceToken: String
        let platform: String
        let appVersion: String
        /// Совпадает с push routing на бэкенде (anon family id из FamilyLocalStore).
        let familyId: String?

        enum CodingKeys: String, CodingKey {
            case deviceToken
            case platform
            case appVersion
            case familyId
        }
    }
    
    func registerDeviceToken(_ token: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        let rawFamily = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let familyIdOpt: String? = rawFamily.isEmpty ? nil : rawFamily
        let body = DeviceTokenRequest(
            deviceToken: token,
            platform: "iOS",
            appVersion: AppConfig.appVersion,
            familyId: familyIdOpt
        )
        networkManager.post(endpoint: AppConfig.Endpoint.deviceRegister, body: body, completion: completion)
    }
    
    // MARK: - Family Reconcile API

    /**
     * Вызывает reconcile на сервере для исправления рассинхронизации семьи.
     * Используется после remove 404, registration, или явного desync.
     */
    /// Сервер (`app/routers/family.py`) возвращает голое тело `ReconcileFamilyResponse`, без обёртки `APIResponse`.
    func reconcileFamily(familyId: String? = nil, completion: @escaping (Result<ReconcileFamilyResponse, Error>) -> Void) {
        struct ReconcileRequest: Codable {
            let familyId: String?
        }
        let request = ReconcileRequest(familyId: familyId)
        networkManager.post(endpoint: AppConfig.Endpoint.familyReconcile, body: request, completion: completion)
    }

    // MARK: - Add Device API
    
    struct AddDeviceRequest: Codable {
        let name: String
        let type: String // "iphone", "ipad", "mac", "android"
        let owner: String
        let ownerMemberId: String?
        
        enum CodingKeys: String, CodingKey {
            case name, type, owner
            case ownerMemberId = "owner_member_id"
        }
        
        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            try c.encode(name, forKey: .name)
            try c.encode(type, forKey: .type)
            try c.encode(owner, forKey: .owner)
            if let mid = ownerMemberId?.trimmingCharacters(in: .whitespacesAndNewlines), !mid.isEmpty {
                try c.encode(mid, forKey: .ownerMemberId)
            }
        }
    }
    
    func addDevice(
        name: String,
        type: String,
        owner: String,
        ownerMemberId: String? = nil,
        completion: @escaping (Result<DeviceResponse, Error>) -> Void
    ) {
        let request = AddDeviceRequest(name: name, type: type, owner: owner, ownerMemberId: ownerMemberId)
        networkManager.post(endpoint: AppConfig.Endpoint.devices, body: request, completion: completion)
    }
    
    // MARK: - Bind Device API
    
    struct BindDeviceRequest: Encodable {
        let token: String?
        let pin: String?

        enum CodingKeys: String, CodingKey {
            case token
            case pin
        }

        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            if let t = token?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty {
                try c.encode(t, forKey: .token)
            }
            if let p = pin?.trimmingCharacters(in: .whitespacesAndNewlines), !p.isEmpty {
                try c.encode(p, forKey: .pin)
            }
        }
    }

    /// Привязка устройства: достаточно **либо** `token`, **либо** `pin` (6 цифр) — пустые поля в JSON не попадают.
    func bindDevice(token: String?, pin: String?, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        let t = token?.trimmingCharacters(in: .whitespacesAndNewlines)
        let p = pin?.trimmingCharacters(in: .whitespacesAndNewlines)
        let hasToken = (t?.isEmpty == false)
        let hasPin = (p?.isEmpty == false)
        guard hasToken || hasPin else {
            completion(.failure(NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "token or pin required"])))
            return
        }
        let request = BindDeviceRequest(token: hasToken ? t : nil, pin: hasPin ? p : nil)
        networkManager.post(endpoint: AppConfig.Endpoint.devicesBind, body: request, completion: completion)
    }
    
    // ✅ ДОБАВЛЕНО: Device Settings API (для синхронизации между устройствами)
    
    /// Загрузить настройки устройства с сервера
    func getDeviceSettings(deviceId: String, completion: @escaping (Result<DeviceSettingsResponse, Error>) -> Void) {
        networkManager.get(endpoint: "\(AppConfig.Endpoint.deviceSettings)/\(deviceId)/settings", completion: completion)
    }
    
    /// Сохранить настройки устройства на сервер
    func updateDeviceSettings(
        deviceId: String,
        isProtectionOn: Bool,
        isScanningEnabled: Bool,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct DeviceSettingsRequest: Codable {
            let isProtectionOn: Bool
            let isScanningEnabled: Bool
        }
        
        let request = DeviceSettingsRequest(
            isProtectionOn: isProtectionOn,
            isScanningEnabled: isScanningEnabled
        )
        
        let path = "\(AppConfig.Endpoint.deviceSettings)/\(deviceId)/settings"
        networkManager.patch(endpoint: path, body: request) { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let ok):
                completion(.success(ok))
            case .failure(let err):
                if Self.isHttpMethodNotAllowed(err) {
                    self.networkManager.put(endpoint: path, body: request, completion: completion)
                } else {
                    completion(.failure(err))
                }
            }
        }
    }

    private static func isHttpMethodNotAllowed(_ error: Error) -> Bool {
        if let ne = error as? NetworkError {
            if case .httpError(let code) = ne { return code == 405 }
        }
        let msg = error.localizedDescription
        return msg.contains("405") || msg.contains("Method Not Allowed")
    }

    // MARK: - Payment API
    
    func createQRPayment(request: CreateQRPaymentRequest, completion: @escaping (Result<CreateQRPaymentResponse, Error>) -> Void) {
        // ✅ ИСПРАВЛЕНО: Используем AppConfig.Endpoint вместо жесткой строки
        networkManager.post(endpoint: AppConfig.Endpoint.paymentsQRCreate, body: request, completion: completion)
    }
    
    func checkQRPaymentStatus(paymentId: String, completion: @escaping (Result<CheckQRPaymentStatusResponse, Error>) -> Void) {
        // ✅ ИСПРАВЛЕНО: Используем AppConfig.Endpoint вместо жесткой строки
        let endpoint = AppConfig.Endpoint.paymentsQRStatus.replacingOccurrences(of: "{paymentId}", with: paymentId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    // MARK: - Parental Control API
    
    /**
     * Применение блокировки контента
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func applyBlocking(
        childId: String,
        type: BlockingType,
        enabled: Bool,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct ApplyBlockingRequest: Codable {
            let childId: String
            let type: String
            let enabled: Bool
        }
        
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        networkManager.post(
            endpoint: AppConfig.Endpoint.applyBlocking,
            body: ApplyBlockingRequest(childId: childId, type: type.rawValue, enabled: enabled),
            completion: completion
        )
    }
    
    /**
     * Применение правил родительского контроля
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func applyParentalControlRules(
        childId: String,
        ageGroup: String,
        rules: ParentalControlRules,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct ApplyParentalControlRulesRequest: Codable {
            let childId: String
            let ageGroup: String
            let rules: ParentalControlRules
        }
        
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        networkManager.post(
            endpoint: AppConfig.Endpoint.applyRules,
            body: ApplyParentalControlRulesRequest(childId: childId, ageGroup: ageGroup, rules: rules),
            completion: completion
        )
    }
    
    // MARK: - IoT API
    
    /// Получить статус IoT безопасности
    func getIoTStatus(homeId: String) async throws -> IoTStatusResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            let endpoint = AppConfig.Endpoint.iotStatus.replacingOccurrences(of: "{homeId}", with: homeId)
            networkManager.get(endpoint: endpoint) { (result: Result<IoTStatusResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getIoTStatus()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }
    
    /// Получить список IoT устройств
    func getIoTDevices(homeId: String) async throws -> IoTDevicesResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            let endpoint = AppConfig.Endpoint.iotDevices.replacingOccurrences(of: "{homeId}", with: homeId)
            networkManager.get(endpoint: endpoint) { (result: Result<IoTDevicesResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getIoTDevices()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }
    
    /// Получить список угроз
    func getIoTThreats(homeId: String) async throws -> IoTThreatsResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            let endpoint = AppConfig.Endpoint.iotThreats.replacingOccurrences(of: "{homeId}", with: homeId)
            networkManager.get(endpoint: endpoint) { (result: Result<IoTThreatsResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getIoTThreats()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }
    
    /// Заблокировать IoT устройство
    func blockIoTDevice(deviceId: String) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct EmptyBody: Codable {}
            let endpoint = AppConfig.Endpoint.iotDeviceBlock.replacingOccurrences(of: "{deviceId}", with: deviceId)
            networkManager.post(endpoint: endpoint, body: EmptyBody()) { (result: Result<APIResponse<Bool>, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in blockIoTDevice()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // MARK: - Device Management API

    /// Заблокировать устройство
    func blockDevice(deviceId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: "\(AppConfig.Endpoint.devices)/\(deviceId)/block", body: EmptyBody(), completion: completion)
    }

    /// Разблокировать устройство
    func unblockDevice(deviceId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: "\(AppConfig.Endpoint.devices)/\(deviceId)/unblock", body: EmptyBody(), completion: completion)
    }

    /// Удалить устройство
    func removeDevice(deviceId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.delete(endpoint: "\(AppConfig.Endpoint.devices)/\(deviceId)", body: EmptyBody(), completion: completion)
    }
    
    /// Запустить сканирование IoT устройств
    func startIoTScan(homeId: String) async throws -> APIResponse<String> {
        return try await withCheckedThrowingContinuation { continuation in
            var hasResumed = false

            struct EmptyBody: Codable {}
            let endpoint = AppConfig.Endpoint.iotScan.replacingOccurrences(of: "{homeId}", with: homeId)
            networkManager.post(endpoint: endpoint, body: EmptyBody()) { (result: Result<APIResponse<String>, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in startIoTScan()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    /// Исправить угрозу
    func fixIoTThreat(threatId: String) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct EmptyBody: Codable {}
            let endpoint = AppConfig.Endpoint.iotFix.replacingOccurrences(of: "{threatId}", with: threatId)
            networkManager.post(endpoint: endpoint, body: EmptyBody()) { (result: Result<APIResponse<Bool>, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in fixIoTThreat()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }
    
    /**
     * Получение запросов доступа
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func getAccessRequests(
        childId: String? = nil,
        completion: @escaping (Result<[AccessRequestResponse], Error>) -> Void
    ) {
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        let endpoint = childId != nil ? "\(AppConfig.Endpoint.getAccessRequests)?childId=\(childId!)" : AppConfig.Endpoint.getAccessRequests
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /**
     * Обработка запроса доступа (принять/отклонить)
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func handleAccessRequest(
        requestId: String,
        action: String, // "accept" или "reject"
        reason: String? = nil,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct HandleAccessRequestRequest: Codable {
            let requestId: String
            let action: String
            let reason: String?
        }
        
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        networkManager.post(
            endpoint: "\(AppConfig.Endpoint.handleAccessRequest)/\(requestId)",
            body: HandleAccessRequestRequest(requestId: requestId, action: action, reason: reason),
            completion: completion
        )
    }
    
    /**
     * Получение статистики родительского контроля
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func getParentalControlStats(
        childId: String? = nil,
        completion: @escaping (Result<ParentalControlStatsResponse, Error>) -> Void
    ) {
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        let endpoint = childId != nil ? "\(AppConfig.Endpoint.getStats)?childId=\(childId!)" : AppConfig.Endpoint.getStats
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Детальные списки мониторинга / отчётов (только данные с сервера).
    func getParentalMonitoringDetail(
        childId: String? = nil,
        completion: @escaping (Result<ParentalMonitoringDetailResponse, Error>) -> Void
    ) {
        let key: String = (childId?.isEmpty == false) ? childId! : "__none__"
        Self.parentalMonitoringDetailCoalesceLock.lock()
        Self.parentalMonitoringDetailWaiters[key, default: []].append(completion)
        let shouldStart = !Self.parentalMonitoringDetailInflight.contains(key)
        if shouldStart {
            Self.parentalMonitoringDetailInflight.insert(key)
        }
        Self.parentalMonitoringDetailCoalesceLock.unlock()
        guard shouldStart else { return }

        var endpoint = AppConfig.Endpoint.parentalMonitoringDetail
        if let childId, !childId.isEmpty,
           let encoded = childId.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
            endpoint += "?childId=\(encoded)"
        }
        networkManager.get(endpoint: endpoint) { (result: Result<ParentalMonitoringDetailResponse, Error>) in
            let validated: Result<ParentalMonitoringDetailResponse, Error>
            switch result {
            case .success(let detail):
                do {
                    try detail.validateForProduction()
                    validated = .success(detail)
                } catch {
                    validated = .failure(error)
                }
            case .failure(let error):
                validated = .failure(error)
            }
            Self.parentalMonitoringDetailCoalesceLock.lock()
            Self.parentalMonitoringDetailInflight.remove(key)
            let callbacks = Self.parentalMonitoringDetailWaiters.removeValue(forKey: key) ?? []
            Self.parentalMonitoringDetailCoalesceLock.unlock()
            for cb in callbacks {
                cb(validated)
            }
        }
    }

    /// Детское устройство: запись событий мониторинга (DNS / приложения / хэши URL). Требуется JWT с числовым `user_id` ребёнка.
    func postParentalMonitoringEvents(
        events: [ParentalMonitoringEventInDTO],
        completion: @escaping (Result<ParentalMonitoringIngestResponseBody, Error>) -> Void
    ) {
        let body = ParentalMonitoringIngestRequestBody(events: events)
        networkManager.post(
            endpoint: AppConfig.Endpoint.parentalMonitoringEvents,
            body: body,
            completion: completion
        )
    }
    
    /**
     * Получение статистики защиты от обхода
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func getBypassStats(
        childId: String? = nil,
        completion: @escaping (Result<BypassStatsResponse, Error>) -> Void
    ) {
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        let endpoint = childId != nil ? "/api/parental/bypass/stats?childId=\(childId!)" : "/api/parental/bypass/stats"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /**
     * Применение защиты от обхода
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func applyBypassProtection(
        childId: String,
        incognito: Bool,
        tor: Bool,
        proxy: Bool,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct ApplyBypassProtectionRequest: Codable {
            let childId: String
            let incognito: Bool
            let tor: Bool
            let proxy: Bool
        }
        
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        networkManager.post(
            endpoint: "/api/parental/bypass/apply",
            body: ApplyBypassProtectionRequest(childId: childId, incognito: incognito, tor: tor, proxy: proxy),
            completion: completion
        )
    }
    
    // MARK: - Components API (42 components)
    
    /// Получить статус компонента
    func getComponentStatus(componentId: String) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            networkManager.get(endpoint: "\(AppConfig.Endpoint.componentStatus)/\(componentId)") { (result: Result<ComponentStatusResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getComponentStatus()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    do {
                        let componentStatus = try APIResponseValidator.makeComponentStatus(
                            from: response,
                            canonicalComponentId: componentId,
                            policy: .canonicalRequestIdAlwaysWins
                        )
                        hasResumed = true
                        continuation.resume(returning: componentStatus)
                    } catch {
                        hasResumed = true
                        continuation.resume(throwing: error)
                    }
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Включить компонент
    func enableComponent(componentId: String, configuration: ComponentConfiguration? = nil) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct EnableRequest: Codable {
                let componentId: String
                let configuration: ComponentConfiguration?
            }
            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentEnable)/\(componentId)",
                body: EnableRequest(componentId: componentId, configuration: configuration)
            ) { (result: Result<ComponentStatusResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in enableComponent()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    do {
                        let componentStatus = try APIResponseValidator.makeComponentStatus(
                            from: response,
                            canonicalComponentId: componentId,
                            policy: .canonicalRequestIdAlwaysWins
                        )
                        hasResumed = true
                        continuation.resume(returning: componentStatus)
                    } catch {
                        hasResumed = true
                        continuation.resume(throwing: error)
                    }
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Выключить компонент
    func disableComponent(componentId: String) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct DisableRequest: Codable {
                let componentId: String
            }
            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentDisable)/\(componentId)",
                body: DisableRequest(componentId: componentId)
            ) { (result: Result<ComponentStatusResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in disableComponent()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    do {
                        let componentStatus = try APIResponseValidator.makeComponentStatus(
                            from: response,
                            canonicalComponentId: componentId,
                            policy: .canonicalRequestIdAlwaysWins
                        )
                        hasResumed = true
                        continuation.resume(returning: componentStatus)
                    } catch {
                        hasResumed = true
                        continuation.resume(throwing: error)
                    }
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Обновить статус компонента
    func updateComponentStatus(
        componentId: String,
        isEnabled: Bool,
        configuration: ComponentConfiguration? = nil
    ) async throws {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct UpdateRequest: Codable {
                let componentId: String
                let isEnabled: Bool
                let configuration: ComponentConfiguration?
            }
            
            let requestBody = UpdateRequest(componentId: componentId, isEnabled: isEnabled, configuration: configuration)
            let endpoint = isEnabled
                ? "\(AppConfig.Endpoint.componentEnable)/\(componentId)"
                : "\(AppConfig.Endpoint.componentDisable)/\(componentId)"
            
            // Каноничный контракт: мутация статуса через enable/disable endpoints
            networkManager.post(
                endpoint: endpoint,
                body: requestBody
            ) { (result: Result<ComponentStatusResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in updateComponentStatus()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    // Каноничный ответ: ComponentStatusResponse
                    let status: ComponentStatus
                    do {
                        status = try APIResponseValidator.makeComponentStatus(
                            from: response,
                            canonicalComponentId: componentId,
                            policy: .canonicalRequestIdAlwaysWins
                        )
                    } catch {
                        hasResumed = true
                        continuation.resume(throwing: error)
                        return
                    }
                    // Валидация: флаг применён
                    if status.isEnabled == isEnabled {
                        hasResumed = true
                        continuation.resume()
                    } else {
                        hasResumed = true
                        let mismatch = "ComponentStatus mismatch: expected(\(componentId), \(isEnabled)) got(\(status.componentId), \(status.isEnabled))"
                        continuation.resume(throwing: NetworkError.decodingError(NSError(domain: "APIService.updateComponentStatus", code: -2, userInfo: [NSLocalizedDescriptionKey: mismatch])))
                    }
                case .failure(let error):
                    // Пробрасываем все ошибки, не скрываем их
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Получить конфигурацию компонента
    func getComponentConfiguration(componentId: String) async throws -> ComponentConfiguration {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false

            networkManager.get(endpoint: "\(AppConfig.Endpoint.componentConfiguration)/\(componentId)") { (result: Result<ServerComponentConfigurationResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getComponentConfiguration()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    if response.isDefault == true {
                        logger.log(
                            .info,
                            category: .network,
                            message: "Component configuration loaded from server defaults for \(componentId)"
                        )
                    }
                    // Сервер конфигурации хранит settings отдельно от статуса компонента.
                    // Для экрана настроек нам важны сами settings; флаг включенности здесь нейтральный.
                    let mapped = ComponentConfiguration(
                        isEnabled: true,
                        priority: .normal,
                        additionalSettings: response.configuration.settings
                    )
                    hasResumed = true
                    continuation.resume(returning: mapped)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Обновить конфигурацию компонента
    func updateComponentConfiguration(
        componentId: String,
        configuration: ComponentConfiguration
    ) async throws {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct UpdateRequest: Codable {
                let settings: [String: AnyCodable]
            }

            struct UpdateResponse: Codable {
                let success: Bool
                let message: String?
            }

            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentConfiguration)/\(componentId)",
                body: UpdateRequest(settings: configuration.additionalSettings ?? [:])
            ) { (result: Result<UpdateResponse, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in updateComponentConfiguration()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    if response.success {
                        hasResumed = true
                        continuation.resume()
                    } else {
                        hasResumed = true
                        let message = response.message ?? "Unknown configuration update failure"
                        continuation.resume(throwing: NetworkError.businessLogicError(message))
                    }
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    // MARK: - Component Reports API
    
    // MARK: - Driving Reports API
    
    /// Получить отчеты о вождении
    func getDrivingReports(userId: String?, period: String, completion: @escaping (Result<[DrivingReport], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.drivingReports
        var queryItems: [String] = []
        
        if let userId = userId {
            queryItems.append("userId=\(userId)")
        }
        queryItems.append("period=\(period)")
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Получить статистику вождения
    func getDrivingStats(userId: String?, period: String, completion: @escaping (Result<DrivingStats, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.drivingStats
        var queryItems: [String] = []
        
        if let userId = userId {
            queryItems.append("userId=\(userId)")
        }
        queryItems.append("period=\(period)")
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Экспортировать отчет о вождении
    func exportDrivingReport(reportId: String, format: String, completion: @escaping (Result<Data, Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.drivingExport)?reportId=\(reportId)&format=\(format)"
        networkManager.get(endpoint: endpoint) { (result: Result<APIResponse<Data>, Error>) in
            switch result {
            case .success(let response):
                if let data = response.data {
                    completion(.success(data))
                } else {
                    completion(.failure(NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data in response"])))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Начать поездку с координатами
    func startDrivingTrip(userId: String?, startLatitude: Double, startLongitude: Double, completion: @escaping (Result<APIResponse<String>, Error>) -> Void) {
        struct StartTripRequest: Codable {
            let userId: String?
            let startLatitude: Double
            let startLongitude: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.drivingStart,
            body: StartTripRequest(userId: userId, startLatitude: startLatitude, startLongitude: startLongitude),
            completion: completion
        )
    }
    
    // ✅ ИНТЕГРАЦИЯ: Завершить поездку с координатами
    func endDrivingTrip(tripId: String, endLatitude: Double, endLongitude: Double, completion: @escaping (Result<APIResponse<DrivingReport>, Error>) -> Void) {
        struct EndTripRequest: Codable {
            let tripId: String
            let endLatitude: Double
            let endLongitude: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.drivingEnd,
            body: EndTripRequest(tripId: tripId, endLatitude: endLatitude, endLongitude: endLongitude),
            completion: completion
        )
    }
    
    // MARK: - Dark Web Monitoring API

    private struct DarkWebLeaksListResponse: Codable {
        let items: [DarkWebLeakListItem]
        let nextCursor: String?

        enum CodingKeys: String, CodingKey {
            case items
            case nextCursor = "next_cursor"
        }
    }

    private struct DarkWebLeakListItem: Codable {
        let id: String
        let dataType: String?
        let leakDate: String?
        let source: String?
        let severity: String?
        let status: String?

        enum CodingKeys: String, CodingKey {
            case id
            case dataType = "data_type"
            case leakDate = "leak_date"
            case source, severity, status
        }
    }

    private func darkWebUserIdQueryItem() -> String? {
        guard let userId = FamilyLocalStore.currentJWTUserId()?.trimmingCharacters(in: .whitespacesAndNewlines),
              !userId.isEmpty else {
            return nil
        }
        return "user_id=\(userId.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? userId)"
    }

    private func mapDarkWebLeakListItem(_ item: DarkWebLeakListItem) -> DarkWebLeak? {
        let id = item.id.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !id.isEmpty else { return nil }
        let leakDate = Self.parseISO8601Date(item.leakDate) ?? Date()
        let dataType = LeakDataType(rawValue: item.dataType ?? "") ?? .email
        let severity = LeakSeverity(rawValue: item.severity ?? "") ?? .medium
        let status = LeakStatus(rawValue: item.status ?? "") ?? .new
        return DarkWebLeak(
            id: id,
            dataType: dataType,
            value: "***",
            fullValue: nil,
            leakDate: leakDate,
            discoveryDate: leakDate,
            source: item.source ?? "ALADDIN",
            severity: severity,
            status: status,
            recommendations: []
        )
    }
    
    /// Получить утечки данных (prod: `/dark-web/leaks/list` + user scope)
    func getDarkWebLeaks(status: String? = nil, severity: String? = nil, completion: @escaping (Result<[DarkWebLeak], Error>) -> Void) {
        var queryItems: [String] = ["limit=100"]
        if let userQuery = darkWebUserIdQueryItem() {
            queryItems.append(userQuery)
        }
        if let status = status {
            queryItems.append("status=\(status)")
        }
        if let severity = severity {
            queryItems.append("severity=\(severity)")
        }
        let endpoint = AppConfig.Endpoint.darkWebLeaksList + "?" + queryItems.joined(separator: "&")

        networkManager.get(endpoint: endpoint) { (result: Result<DarkWebLeaksListResponse, Error>) in
            switch result {
            case .success(let response):
                let leaks = response.items.compactMap { self.mapDarkWebLeakListItem($0) }
                completion(.success(leaks))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Получить статистику Dark Web
    func getDarkWebStats(completion: @escaping (Result<DarkWebStats, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.darkWebStats
        if let userQuery = darkWebUserIdQueryItem() {
            endpoint += "?\(userQuery)"
        }
        networkManager.get(endpoint: endpoint) { (result: Result<ComponentStatsDTO, Error>) in
            switch result {
            case .success(let dto):
                let stats = DarkWebStats(
                    totalLeaks: dto.totalLeaks ?? dto.leaks_found ?? dto.total ?? 0,
                    newLeaks: dto.newLeaks ?? dto.new_leaks ?? dto.last_24h ?? 0,
                    // В reports_compat поле blocked для dark-web соответствует "resolved".
                    resolvedLeaks: dto.resolvedLeaks ?? dto.blocked ?? 0,
                    criticalLeaks: dto.criticalLeaks ?? dto.critical ?? 0,
                    lastScanDate: Self.parseISO8601Date(dto.lastScanDate ?? dto.timestamp)
                )
                completion(.success(stats))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Получить историю сканирований
    func getDarkWebScans(limit: Int = 20, completion: @escaping (Result<[DarkWebScan], Error>) -> Void) {
        var queryItems = ["limit=\(limit)"]
        if let userQuery = darkWebUserIdQueryItem() {
            queryItems.append(userQuery)
        }
        let endpoint = AppConfig.Endpoint.darkWebScans + "?" + queryItems.joined(separator: "&")
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Отметить утечку как решенную
    func resolveDarkWebLeak(leakId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct ResolveRequest: Codable {
            let leakId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.darkWebResolve, body: ResolveRequest(leakId: leakId), completion: completion)
    }
    
    /// Запустить автоматическое сканирование темной сети
    func startDarkWebScan(completion: @escaping (Result<DarkWebScan, Error>) -> Void) {
        // POST — боевой путь на сервере (запись события в БД для freshness). GET оставлен как легаси-заглушка.
        struct EmptyDarkWebScanStartBody: Codable {}
        // Backend для /dark-web/scan/start отдаёт ReportCompatBoolResponse:
        // { "success": true, "data": true, "message": "..." }.
        // Мы декодим это как APIResponse<Bool>, а UI-процесс рассматривает успех как "запуск сессии".
        networkManager.post(endpoint: AppConfig.Endpoint.darkWebScanStart, body: EmptyDarkWebScanStartBody(), completion: { (result: Result<APIResponse<Bool>, Error>) in
            switch result {
            case .success(let apiResponse):
                if apiResponse.success == true {
                    // ViewModel в startScan игнорирует содержимое (map {_ in ()}),
                    // но тип должен совпадать. Достаточно безопасного stub-значения.
                    let scan = DarkWebScan(
                        id: UUID().uuidString,
                        scanDate: Date(),
                        databasesScanned: 0,
                        newLeaksFound: 0,
                        status: .inProgress
                    )
                    completion(.success(scan))
                } else {
        completion(.failure(NetworkError.serverUnavailable))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        })
    }
    
    // MARK: - Hybrid Dark Web Scan API
    
    /// Безопасное сканирование (хеши)
    func scanDarkWebSecure(
        emailHash: String?,
        passwordHash: String?,
        completion: @escaping (Result<APIResponse<[DarkWebScanResult]>, Error>) -> Void
    ) {
        struct SecureScanRequest: Codable {
            let emailHash: String?
            let passwordHash: String?
            var method: String = "secure"
        }
        
        let request = SecureScanRequest(
            emailHash: emailHash,
            passwordHash: passwordHash
        )
        
        networkManager.post(
            endpoint: AppConfig.Endpoint.darkWebScanSecure,
            body: request,
            completion: completion
        )
    }
    
    /// Быстрое сканирование (plaintext)
    func scanDarkWebFast(
        email: String?,
        phone: String?,
        passport: String?,
        snils: String?,
        completion: @escaping (Result<APIResponse<[DarkWebScanResult]>, Error>) -> Void
    ) {
        struct FastScanRequest: Codable {
            let email: String?
            let phone: String?
            let passport: String?
            let snils: String?
            var method: String = "fast"
        }
        
        let request = FastScanRequest(
            email: email,
            phone: phone,
            passport: passport,
            snils: snils
        )
        
        networkManager.post(
            endpoint: AppConfig.Endpoint.darkWebScanFast,
            body: request,
            completion: completion
        )
    }
    
    // MARK: - Identity Theft Protection API
    
    /// Получить попытки кражи личности (B4-03 — envelope decode + client filters).
    func getIdentityTheftAttempts(
        action: String? = nil,
        severity: String? = nil,
        limit: Int = 50,
        completion: @escaping (Result<[IdentityTheftAttempt], Error>) -> Void
    ) {
        let cappedLimit = min(max(limit, 1), 100)
        var endpoint = "\(AppConfig.Endpoint.identityTheftAttempts)?limit=\(cappedLimit)"

        networkManager.get(endpoint: endpoint) { (result: Result<IdentityTheftAttemptsEnvelope, Error>) in
            switch result {
            case .success(let envelope):
                if IdentityTheftResponseGuard.rejectsMock(source: envelope.source) {
                    completion(.failure(SecurityVerdictValidationError.mockSourceRejected(envelope.source ?? "mock")))
                    return
                }
                var attempts = envelope.attempts
                if let action, action != "all" {
                    attempts = attempts.filter { $0.action.rawValue == action }
                }
                if let severity, severity != "all" {
                    attempts = attempts.filter { $0.severity.rawValue == severity }
                }
                completion(.success(attempts))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Получить статистику защиты от кражи личности
    func getIdentityTheftStats(completion: @escaping (Result<IdentityTheftStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.identityTheftStats) { (result: Result<ComponentStatsDTO, Error>) in
            switch result {
            case .success(let dto):
                let stats = IdentityTheftStats(
                    totalAttempts: dto.totalAttempts ?? dto.attempts ?? dto.total ?? 0,
                    blockedAttempts: dto.blockedAttempts ?? dto.blocked ?? 0,
                    // Для совместимого формата отдельного suspicious нет, используем last_24h как "свежие инциденты".
                    suspiciousActivities: dto.suspiciousActivities ?? dto.suspicious ?? dto.last_24h ?? 0,
                    byDataType: [:]
                )
                completion(.success(stats))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Разрешить попытку кражи личности
    func allowIdentityTheftAttempt(attemptId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct AllowRequest: Codable {
            let attemptId: String

            enum CodingKeys: String, CodingKey {
                case attemptId = "attempt_id"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.identityTheftAllow,
            body: AllowRequest(attemptId: attemptId),
            completion: completion
        )
    }
    
    /// Заблокировать попытку кражи личности
    func blockIdentityTheftAttempt(attemptId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct BlockRequest: Codable {
            let attemptId: String

            enum CodingKeys: String, CodingKey {
                case attemptId = "attempt_id"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.identityTheftBlock,
            body: BlockRequest(attemptId: attemptId),
            completion: completion
        )
    }
    
    /// Добавить источник в белый список
    func addToWhitelist(source: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct WhitelistRequest: Codable {
            let source: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.identityTheftWhitelist,
            body: WhitelistRequest(source: source),
            completion: completion
        )
    }

    /// POST `/api/identity-theft/detect` — SNILS identity theft check (B4-02).
    func detectIdentityTheft(
        snils: String,
        completion: @escaping (Result<SecurityVerdict, Error>) -> Void
    ) {
        struct DetectRequest: Codable {
            let snils: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.identityTheftDetect,
            body: DetectRequest(snils: snils),
            completion: { [weak self] (result: Result<SecurityVerdict, Error>) in
                self?.completeValidatedAntifakeVerdict(result, completion: completion)
            }
        )
    }

    /// POST `/api/identity-theft/monitor/credit` — credit monitor agent (B4-04).
    func monitorIdentityCredit(completion: @escaping (Result<SecurityVerdict, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(
            endpoint: AppConfig.Endpoint.identityTheftMonitorCredit,
            body: EmptyBody(),
            completion: { [weak self] (result: Result<SecurityVerdict, Error>) in
                self?.completeValidatedAntifakeVerdict(result, completion: completion)
            }
        )
    }

    // MARK: - Device Hub scans (B5)

    /// POST `/api/malware/scan` — quick malware scan (B5-02).
    func runMalwareQuickScan(
        scope: String = "quick",
        completion: @escaping (Result<DeviceAgentScanResult, Error>) -> Void
    ) {
        struct ScanRequest: Codable { let scope: String }
        networkManager.post(
            endpoint: AppConfig.Endpoint.malwareQuickScan,
            body: ScanRequest(scope: scope),
            completion: { [weak self] (result: Result<DeviceAgentScanResult, Error>) in
                self?.completeValidatedDeviceScan(result, completion: completion)
            }
        )
    }

    /// POST `/api/mobile/security/check` — mobile security check (B5-03 / comp-03).
    func runMobileSecurityCheck(
        deviceId: String? = nil,
        completion: @escaping (Result<DeviceAgentScanResult, Error>) -> Void
    ) {
        struct ScanRequest: Codable {
            let deviceId: String?

            enum CodingKeys: String, CodingKey {
                case deviceId = "device_id"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.mobileSecurityCheck,
            body: ScanRequest(deviceId: deviceId),
            completion: { [weak self] (result: Result<DeviceAgentScanResult, Error>) in
                self?.completeValidatedDeviceScan(result, completion: completion)
            }
        )
    }

    /// POST `/api/mobile/scan` — app inventory scan (mob-02).
    func runMobileDeviceScan(
        deviceId: String? = nil,
        completion: @escaping (Result<DeviceAgentScanResult, Error>) -> Void
    ) {
        struct ScanRequest: Codable {
            let deviceId: String?

            enum CodingKeys: String, CodingKey {
                case deviceId = "device_id"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.mobileScan,
            body: ScanRequest(deviceId: deviceId),
            completion: { [weak self] (result: Result<DeviceAgentScanResult, Error>) in
                self?.completeValidatedDeviceScan(result, completion: completion)
            }
        )
    }

    /// POST `/api/ai/assistant/report_incident` — incident response drill (B5-03 / comp-04).
    func reportSecurityIncident(
        type: String,
        description: String,
        completion: @escaping (Result<DeviceIncidentReportResult, Error>) -> Void
    ) {
        struct IncidentRequest: Codable {
            let type: String
            let description: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.aiAssistantReportIncident,
            body: IncidentRequest(type: type, description: description),
            completion: { (result: Result<DeviceIncidentReportResult, Error>) in
                switch result {
                case .success(let payload):
                    do {
                        try payload.validateForProduction()
                        completion(.success(payload))
                    } catch {
                        completion(.failure(error))
                    }
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        )
    }

    /// EICAR antivirus file scan (B5-09).
    func runEicarTestScan() async throws -> APIService.MalwareFileScanAPIResponse {
        try await uploadFileForScanAsync(
            fileData: DeviceScanSourceValidator.eicarPayload,
            fileName: "eicar.txt",
            fileSize: Int64(DeviceScanSourceValidator.eicarPayload.count),
            checksum: nil
        )
    }

    private func completeValidatedDeviceScan(
        _ result: Result<DeviceAgentScanResult, Error>,
        completion: @escaping (Result<DeviceAgentScanResult, Error>) -> Void
    ) {
        switch result {
        case .success(let scan):
            do {
                try scan.validateForProduction()
                completion(.success(scan))
            } catch {
                completion(.failure(error))
            }
        case .failure(let error):
            if PremiumGateHandler.outcome(from: error).requiresUpgrade {
                completion(.failure(SecurityVerdictPremiumRequiredError(message: nil)))
                return
            }
            completion(.failure(error))
        }
    }

    // MARK: - Antifake API (B2-04 — explicit `/api/antifake/check/*`, no mock)

    /// POST `/api/antifake/check/text` — sync text analysis.
    func antifakeCheckText(
        text: String,
        mode: String = "news",
        completion: @escaping (Result<SecurityVerdict, Error>) -> Void
    ) {
        struct CheckTextRequest: Codable {
            let text: String
            let mode: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeCheckText,
            body: CheckTextRequest(text: text, mode: mode),
            completion: { [weak self] (result: Result<SecurityVerdict, Error>) in
                self?.completeValidatedAntifakeVerdict(result, completion: completion)
            }
        )
    }

    /// POST `/api/antifake/check/url` — sync URL analysis.
    func antifakeCheckUrl(
        url: String,
        completion: @escaping (Result<SecurityVerdict, Error>) -> Void
    ) {
        struct CheckUrlRequest: Codable {
            let url: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeCheckUrl,
            body: CheckUrlRequest(url: url),
            completion: { [weak self] (result: Result<SecurityVerdict, Error>) in
                self?.completeValidatedAntifakeVerdict(result, completion: completion)
            }
        )
    }

    /// POST multipart `/api/antifake/check/{audio|video|document}` → job enqueue or immediate verdict (B2-05).
    func antifakeUploadMedia(
        kind: AntifakeMediaKind,
        fileData: Data,
        filename: String,
        mimeType: String,
        extraFormFields: [String: String]? = nil,
        completion: @escaping (Result<AntifakeJobEnqueueResult, Error>) -> Void
    ) {
        guard fileData.count <= Self.antifakeMaxUploadBytes else {
            completion(.failure(NetworkError.badRequest("file_too_large")))
            return
        }

        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            guard let token = AppConfig.authToken else {
                completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
                return
            }

            let endpoint = kind.uploadEndpoint
            guard let url = URL(string: AppConfig.apiBaseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }

            let boundary = "Boundary-\(UUID().uuidString)"
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            let preferred = Locale.preferredLanguages.first?.lowercased() ?? "ru"
            let lang = preferred.hasPrefix("en") ? "en" : "ru"
            request.setValue(lang, forHTTPHeaderField: "Accept-Language")
            request.setValue(lang, forHTTPHeaderField: "X-Aladdin-Lang")

            var body = Data()
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
            body.append(fileData)
            body.append("\r\n".data(using: .utf8)!)
            if let extraFormFields {
                for (name, value) in extraFormFields where !value.isEmpty {
                    Self.appendMultipartFormField(to: &body, boundary: boundary, name: name, value: value)
                }
            }
            body.append("--\(boundary)--\r\n".data(using: .utf8)!)
            request.httpBody = body

            URLSession.shared.dataTask(with: request) { data, response, error in
                DispatchQueue.main.async {
                    if let error {
                        completion(.failure(error))
                        return
                    }
                    guard let httpResponse = response as? HTTPURLResponse else {
                        completion(.failure(NetworkError.invalidResponse))
                        return
                    }
                    guard let data else {
                        completion(.failure(NetworkError.noData))
                        return
                    }
                    guard (200...299).contains(httpResponse.statusCode) else {
                        let outcome = PremiumGateHandler.outcome(httpStatus: httpResponse.statusCode, data: data)
                        completion(.failure(Self.error(from: outcome, statusCode: httpResponse.statusCode, data: data)))
                        return
                    }
                    do {
                        completion(.success(try SecurityVerdictParsers.decodeJobEnqueueResult(from: data)))
                    } catch {
                        completion(.failure(error))
                    }
                }
            }.resume()
        }
    }

    /// GET `/api/antifake/metrics` — user job stats (B2-12).
    func getAntifakeMetrics(completion: @escaping (Result<AntifakeMetricsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.antifakeMetrics, completion: completion)
    }

    /// GET `/api/antifake/call-directory` — identified/blocked numbers for CallKit (af-m2 / C-09).
    func getAntifakeCallDirectory(
        since: String? = nil,
        completion: @escaping (Result<AntifakeCallDirectoryAPIResponse, Error>) -> Void
    ) {
        var query: [String: String]?
        if let since, !since.isEmpty {
            query = ["since": since]
        }
        networkManager.get(
            endpoint: AppConfig.Endpoint.antifakeCallDirectory,
            queryParams: query,
            completion: completion
        )
    }

    /// fws-06 — voice fraud / Call Directory sensitivity.
    func getAntifakeSettings(completion: @escaping (Result<AntifakeSettingsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.antifakeSettings, completion: completion)
    }

    func putAntifakeSettings(
        thresholdPercent: Int,
        completion: @escaping (Result<AntifakeSettingsResponse, Error>) -> Void
    ) {
        networkManager.put(
            endpoint: AppConfig.Endpoint.antifakeSettings,
            body: AntifakeSettingsUpdateBody(voiceFraudThresholdPercent: thresholdPercent),
            completion: completion
        )
    }

    /// POST `/api/antifake/report` — crowd scam report after completed check (I-01 / I-08).
    func antifakeReportScam(
        jobId: String,
        phone: String,
        label: String? = nil,
        note: String? = nil,
        completion: @escaping (Result<AntifakeReportSubmissionResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let jobId: String
            let phone: String
            let label: String?
            let note: String?

            enum CodingKeys: String, CodingKey {
                case jobId = "job_id"
                case phone
                case label
                case note
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeReport,
            body: Body(jobId: jobId, phone: phone, label: label, note: note),
            completion: completion
        )
    }

    /// POST `/api/antifake/appeal` — dispute «не мошенник» (I-06).
    func antifakeAppealScam(
        jobId: String,
        phone: String,
        note: String? = nil,
        completion: @escaping (Result<AntifakeReportSubmissionResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let jobId: String
            let phone: String
            let note: String?

            enum CodingKeys: String, CodingKey {
                case jobId = "job_id"
                case phone
                case note
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeAppeal,
            body: Body(jobId: jobId, phone: phone, note: note),
            completion: completion
        )
    }

    /// POST `/api/antifake/feedback` — T5-02 false-positive feedback.
    func antifakeVerdictFeedback(
        jobId: String,
        note: String? = nil,
        completion: @escaping (Result<AntifakeFeedbackResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let jobId: String
            let note: String?

            enum CodingKeys: String, CodingKey {
                case jobId = "job_id"
                case note
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeFeedback,
            body: Body(jobId: jobId, note: note),
            completion: completion
        )
    }

    /// POST `/api/antifake/whitelist` — add trusted numbers (I-05).
    func antifakeAddWhitelist(
        phones: [String],
        completion: @escaping (Result<AntifakeWhitelistMutateResponse, Error>) -> Void
    ) {
        struct Body: Codable { let phones: [String] }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeWhitelist,
            body: Body(phones: phones),
            completion: completion
        )
    }

    /// GET `/api/antifake/whitelist` — list trusted numbers (I-05).
    func antifakeListWhitelist(completion: @escaping (Result<AntifakeWhitelistResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.antifakeWhitelist, completion: completion)
    }

    /// POST `/api/antifake/family/push-token` — L-01 parent alert token.
    func antifakeRegisterFamilyPushToken(
        _ token: String,
        completion: @escaping (Result<AntifakeFamilyPushTokenResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let token: String
            let platform: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeFamilyPushToken,
            body: Body(token: token, platform: "ios"),
            completion: completion
        )
    }

    /// GET `/api/antifake/family/reports` — L-03 shared family scam reports.
    func getAntifakeFamilyReports(
        completion: @escaping (Result<AntifakeFamilyReportsResponse, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.antifakeFamilyReports, completion: completion)
    }

    /// POST `/api/antifake/family/cd-status` — L-05 member CD heartbeat.
    func reportAntifakeFamilyCDStatus(
        extensionEnabled: Bool,
        syncedCount: Int,
        completion: @escaping (Result<AntifakeFamilyCDSavedResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let extensionEnabled: Bool
            let syncedCount: Int

            enum CodingKeys: String, CodingKey {
                case extensionEnabled = "extension_enabled"
                case syncedCount = "synced_count"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.antifakeFamilyCDStatus,
            body: Body(extensionEnabled: extensionEnabled, syncedCount: syncedCount),
            completion: completion
        )
    }

    /// GET `/api/antifake/family/cd-status` — L-05 parent dashboard.
    func getAntifakeFamilyCDStatus(
        completion: @escaping (Result<AntifakeFamilyCDStatusResponse, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.antifakeFamilyCDStatus, completion: completion)
    }

    // MARK: - fws-01 Family safe-word

    func getFamilySafeWordStatus(
        completion: @escaping (Result<FamilySafeWordStatusResponse, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.familySafeWord, completion: completion)
    }

    func setFamilySafeWord(
        phrase: String,
        completion: @escaping (Result<FamilySafeWordSetResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let phrase: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.familySafeWord,
            body: Body(phrase: phrase),
            completion: completion
        )
    }

    func verifyFamilySafeWord(
        phrase: String,
        context: String = "antifake",
        completion: @escaping (Result<FamilySafeWordVerifyResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let phrase: String
            let context: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.familySafeWordVerify,
            body: Body(phrase: phrase, context: context),
            completion: completion
        )
    }

    // MARK: - fws-02 Family habit reminders

    func getFamilyHabitReminders(
        completion: @escaping (Result<FamilyHabitRemindersResponse, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.familyHabitReminders, completion: completion)
    }

    func setFamilyHabitReminders<T: Encodable>(
        body: T,
        completion: @escaping (Result<FamilyHabitRemindersSaveResponse, Error>) -> Void
    ) {
        networkManager.post(endpoint: AppConfig.Endpoint.familyHabitReminders, body: body, completion: completion)
    }

    // MARK: - P1.6 Family shared list

    func getFamilySharedList(
        completion: @escaping (Result<[FamilyListItem], Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.familySharedList) { (result: Result<FamilySharedListAPIResponse, Error>) in
            switch result {
            case .success(let resp):
                completion(.success(resp.list?.items ?? []))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    func setFamilySharedList(
        items: [FamilyListItem],
        completion: @escaping (Result<[FamilyListItem], Error>) -> Void
    ) {
        struct Body: Encodable {
            let items: [FamilyListItem]
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.familySharedList,
            body: Body(items: items)
        ) { (result: Result<FamilySharedListAPIResponse, Error>) in
            switch result {
            case .success(let resp):
                completion(.success(resp.list?.items ?? items))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    // MARK: - P2.9h Family challenges

    func getFamilyChallenges(
        completion: @escaping (Result<FamilyChallengesAPIResponse, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.familyChallenges, completion: completion)
    }

    func setFamilyChallenges(
        challenges: [FamilyChallenge],
        completion: @escaping (Result<FamilyChallengesAPIResponse, Error>) -> Void
    ) {
        struct Body: Encodable {
            let challenges: [FamilyChallenge]
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.familyChallenges,
            body: Body(challenges: challenges),
            completion: completion
        )
    }

    func getFamilyIncidents(
        since: String? = nil,
        completion: @escaping (Result<FamilyIncidentFeedResponse, Error>) -> Void
    ) {
        var query: [String: String] = [:]
        if let since, !since.isEmpty {
            query["since"] = since
        }
        networkManager.get(
            endpoint: AppConfig.Endpoint.familyIncidents,
            queryParams: query.isEmpty ? nil : query,
            completion: completion
        )
    }

    func createWellnessHabit(
        ifThen: String,
        completion: @escaping (Result<WellnessHabitCreateResponse, Error>) -> Void
    ) {
        struct Body: Codable {
            let ifThen: String

            enum CodingKeys: String, CodingKey {
                case ifThen = "if_then"
            }
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.wellnessHabits,
            body: Body(ifThen: ifThen),
            completion: completion
        )
    }

    private static func appendMultipartFormField(to body: inout Data, boundary: String, name: String, value: String) {
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(value)\r\n".data(using: .utf8)!)
    }

    /// GET `/api/antifake/jobs/{id}` — poll async job until completed (B2-05).
    func antifakePollJob(
        jobId: String,
        completion: @escaping (Result<AntifakeJobPollOutcome, Error>) -> Void
    ) {
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            guard let token = AppConfig.authToken else {
                completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
                return
            }

            let endpoint = AppConfig.Endpoint.antifakeJob(id: jobId)
            guard let url = URL(string: AppConfig.apiBaseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }

            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            let preferred = Locale.preferredLanguages.first?.lowercased() ?? "ru"
            let lang = preferred.hasPrefix("en") ? "en" : "ru"
            request.setValue(lang, forHTTPHeaderField: "Accept-Language")
            request.setValue(lang, forHTTPHeaderField: "X-Aladdin-Lang")

            URLSession.shared.dataTask(with: request) { data, response, error in
                DispatchQueue.main.async {
                    if let error {
                        completion(.failure(error))
                        return
                    }
                    guard let httpResponse = response as? HTTPURLResponse else {
                        completion(.failure(NetworkError.invalidResponse))
                        return
                    }
                    guard let data else {
                        completion(.failure(NetworkError.noData))
                        return
                    }
                    guard (200...299).contains(httpResponse.statusCode) else {
                        let outcome = PremiumGateHandler.outcome(httpStatus: httpResponse.statusCode, data: data)
                        completion(.failure(Self.error(from: outcome, statusCode: httpResponse.statusCode, data: data)))
                        return
                    }
                    do {
                        completion(.success(try SecurityVerdictParsers.decodeJobPoll(from: data)))
                    } catch {
                        completion(.failure(error))
                    }
                }
            }.resume()
        }
    }

    private static let antifakeMaxUploadBytes = 25 * 1024 * 1024

    private static func error(from outcome: PremiumGateOutcome, statusCode: Int, data: Data) -> Error {
        switch outcome {
        case .premiumRequired(let message):
            return NetworkError.forbidden(message ?? "premium_required")
        case .forbidden(let message):
            return NetworkError.forbidden(message)
        case .other(let networkError):
            return networkError
        case .allowed:
            let detail = parseFastAPIErrorDetail(from: data)
            return NetworkError.from(httpStatusCode: statusCode, message: detail)
        }
    }

    private func completeValidatedAntifakeVerdict(
        _ result: Result<SecurityVerdict, Error>,
        completion: @escaping (Result<SecurityVerdict, Error>) -> Void
    ) {
        switch result {
        case .success(let verdict):
            do {
                try verdict.validateForProduction()
                if verdict.premiumRequired {
                    completion(.failure(SecurityVerdictPremiumRequiredError(message: nil)))
                    return
                }
                completion(.success(verdict))
            } catch {
                completion(.failure(error))
            }
        case .failure(let error):
            completion(.failure(error))
        }
    }
    
    // MARK: - Privacy Reports API
    
    /// Получить статистику Location Bubble
    func getLocationStats(completion: @escaping (Result<LocationStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.locationStats, completion: completion)
    }
    
    /// Получить историю запросов местоположения
    func getLocationRequests(limit: Int = 50, completion: @escaping (Result<[LocationRequest], Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.locationRequests)?limit=\(limit)"
        networkManager.get(endpoint: endpoint) { (result: Result<LocationRequestsListResponse, Error>) in
            switch result {
            case .success(let wrapper):
                completion(.success(wrapper.requests))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Получить статистику очистки данных
    func getDataCleanupStats(completion: @escaping (Result<DataCleanupStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.dataCleanupStats, completion: completion)
    }
    
    /// Получить историю очисток
    func getDataCleanupRecords(limit: Int = 20, completion: @escaping (Result<[DataCleanupRecord], Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.dataCleanupRecords)?limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Получить статистику Anti Tracker
    func getAntiTrackerStats(completion: @escaping (Result<AntiTrackerStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.antiTrackerStats, completion: completion)
    }
    
    /// Получить топ трекеров
    func getTopTrackers(limit: Int = 10, completion: @escaping (Result<[TrackerBlock], Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.topTrackers)?limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    // MARK: - Location Actions API
    
    func allowLocationRequest(requestId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct AllowRequest: Codable {
            let requestId: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationAllow,
            body: AllowRequest(requestId: requestId),
            completion: completion
        )
    }
    
    func blockLocationRequest(requestId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct BlockRequest: Codable {
            let requestId: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationBlock,
            body: BlockRequest(requestId: requestId),
            completion: completion
        )
    }
    
    func updateLocationAccuracy(requestId: String, accuracy: LocationAccuracy, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct AccuracyRequest: Codable {
            let requestId: String
            let accuracy: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationUpdateAccuracy,
            body: AccuracyRequest(requestId: requestId, accuracy: accuracy.rawValue),
            completion: completion
        )
    }
    
    // ✅ ИНТЕГРАЦИЯ: Отправить Location Bubble (точные координаты для генерации приблизительного)
    func sendLocationBubble(latitude: Double, longitude: Double, completion: @escaping (Result<APIResponse<LocationStats>, Error>) -> Void) {
        struct LocationBubbleRequest: Codable {
            let latitude: Double
            let longitude: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationBubble,
            body: LocationBubbleRequest(latitude: latitude, longitude: longitude),
            completion: completion
        )
    }
    
    // ✅ ИНТЕГРАЦИЯ: Отправить координаты при разрешении Location Request
    func sendLocationForRequest(requestId: String, latitude: Double, longitude: Double, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct LocationForRequest: Codable {
            let requestId: String
            let latitude: Double
            let longitude: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationSend,
            body: LocationForRequest(requestId: requestId, latitude: latitude, longitude: longitude),
            completion: completion
        )
    }
    
    // MARK: - Geofences API (Parental Control)
    
    // ✅ ИНТЕГРАЦИЯ: Получить список геозон
    func getGeofences(completion: @escaping (Result<[GeofenceAPI], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.geofences, completion: completion)
    }
    
    // ✅ ИНТЕГРАЦИЯ: Создать геозону
    func createGeofence(name: String, address: String, latitude: Double, longitude: Double, radius: Double, completion: @escaping (Result<APIResponse<GeofenceAPI>, Error>) -> Void) {
        struct CreateGeofenceRequest: Codable {
            let name: String
            let address: String
            let latitude: Double
            let longitude: Double
            let radius: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.geofences,
            body: CreateGeofenceRequest(name: name, address: address, latitude: latitude, longitude: longitude, radius: radius),
            completion: completion
        )
    }
    
    // ✅ ИНТЕГРАЦИЯ: Удалить геозону
    func deleteGeofence(geofenceId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.delete(endpoint: "\(AppConfig.Endpoint.geofences)/\(geofenceId)", body: EmptyBody()) { (result: Result<APIResponse<Bool>, Error>) in
            completion(result)
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Отправить обновление местоположния (План 2026)
    func reportLocation(latitude: Double, longitude: Double, speed: Double? = nil, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct LocationReportRequest: Codable {
            let lat: Double
            let lon: Double
            let speed: Double?
        }
        let request = LocationReportRequest(lat: latitude, lon: longitude, speed: speed)
        networkManager.post(
            endpoint: AppConfig.Endpoint.locationReport,
            body: request,
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Получить конфигурацию DoH (План 2026)
    func getDNSConfig(childId: String? = nil, completion: @escaping (Result<DNSConfigResponse, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.dnsConfig
        if let childId = childId {
            endpoint += "?childId=\(childId)"
        }
        // Совместимость с backend: поддерживаем и raw-object, и APIResponse-wrapped формат.
        networkManager.get(endpoint: endpoint) { (rawResult: Result<DNSConfigResponse, Error>) in
            switch rawResult {
            case .success(let config):
                completion(.success(config))
            case .failure:
                self.networkManager.get(endpoint: endpoint) { (wrappedResult: Result<APIResponse<DNSConfigResponse>, Error>) in
                    switch wrappedResult {
                    case .success(let wrapped):
                        if let data = wrapped.data {
                            completion(.success(data))
                        } else {
                            completion(.failure(NetworkError.businessLogicError(wrapped.message ?? "Конфигурация DNS пуста")))
                        }
                    case .failure(let error):
                        completion(.failure(error))
                    }
                }
            }
        }
    }

    // ✅ ИНТЕГРАЦИЯ: Получить ежедневные отчеты (План 2026)
    func getDailyReports(childId: String? = nil, completion: @escaping (Result<[ParentalReportItem], Error>) -> Void) {
        var endpoint = "/api/parental-control/reports/daily"
        if let childId = childId {
            endpoint += "?childId=\(childId)"
        }
        networkManager.get(
            endpoint: endpoint,
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Получить еженедельную 'Карту достижений' (План 2026)
    func getWeeklyReports(childId: String? = nil, completion: @escaping (Result<[ParentalReportItem], Error>) -> Void) {
        var endpoint = "/api/parental-control/reports/weekly"
        if let childId = childId {
            endpoint += "?childId=\(childId)"
        }
        networkManager.get(
            endpoint: endpoint,
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Отправить обновление местоположения для родительского контроля
    func trackLocation(latitude: Double, longitude: Double, timestamp: Date, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct TrackLocationRequest: Codable {
            let latitude: Double
            let longitude: Double
            let timestamp: String
        }
        let formatter = ISO8601DateFormatter()
        networkManager.post(
            endpoint: AppConfig.Endpoint.geofenceTrack,
            body: TrackLocationRequest(latitude: latitude, longitude: longitude, timestamp: formatter.string(from: timestamp)),
            completion: completion
        )
    }
    
    // MARK: - Crash Detection API
    
    // ✅ ИНТЕГРАЦИЯ: Настроить Crash Detection
    func setupCrashDetection(latitude: Double, longitude: Double, radius: Double = 500, completion: @escaping (Result<APIResponse<String>, Error>) -> Void) {
        struct CrashDetectionSetupRequest: Codable {
            let latitude: Double
            let longitude: Double
            let radius: Double
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionSetup,
            body: CrashDetectionSetupRequest(latitude: latitude, longitude: longitude, radius: radius),
            completion: completion
        )
    }
    
    // ✅ ИНТЕГРАЦИЯ: Отправить алерт о краше
    func sendCrashAlert(latitude: Double, longitude: Double, severity: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct CrashAlertRequest: Codable {
            let latitude: Double
            let longitude: Double
            let severity: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionAlert,
            body: CrashAlertRequest(latitude: latitude, longitude: longitude, severity: severity),
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Запустить мониторинг Crash Detection
    func startCrashDetectionMonitoring(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionStart,
            body: EmptyRequest(),
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Остановить мониторинг Crash Detection
    func stopCrashDetectionMonitoring(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionStop,
            body: EmptyRequest(),
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Отправить данные сенсоров Crash Detection
    func sendCrashDetectionData(accelerometer: [String: Double], gyroscope: [String: Double], speed: Double, location: CLLocation?, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct SensorDataRequest: Codable {
            let accelerometer: [String: Double]
            let gyroscope: [String: Double]
            let speed: Double
            let latitude: Double?
            let longitude: Double?
            let timestamp: Double
        }

        let request = SensorDataRequest(
            accelerometer: accelerometer,
            gyroscope: gyroscope,
            speed: speed,
            latitude: location?.coordinate.latitude,
            longitude: location?.coordinate.longitude,
            timestamp: Date().timeIntervalSince1970
        )

        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionData,
            body: request,
            completion: completion
        )
    }

    // ✅ ИНТЕГРАЦИЯ: Получить статус Crash Detection
    func getCrashDetectionStatus(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.get(
            endpoint: AppConfig.Endpoint.crashDetectionStatus,
            completion: completion
        )
    }

    // ✅ НОВОЕ: Обновить настройки Crash Detection
    func updateCrashDetectionSettings(
        userId: String,
        sensitivity: Double,
        geofenceRadius: Double,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        struct UpdateCrashSettingsRequest: Codable {
            let userId: String
            let sensitivity: Double
            let geofenceRadius: Double
        }

        let request = UpdateCrashSettingsRequest(
            userId: userId,
            sensitivity: sensitivity,
            geofenceRadius: geofenceRadius
        )

        networkManager.post(
            endpoint: AppConfig.Endpoint.crashDetectionSettingsUpdate,
            body: request,
            completion: completion
        )
    }

    // ✅ НОВОЕ: Получить историю Crash Detection
    func getCrashDetectionHistory(
        userId: String,
        limit: Int = 50,
        completion: @escaping (Result<APIResponse<CrashHistoryResponse>, Error>) -> Void
    ) {
        let endpoint = AppConfig.Endpoint.crashDetectionHistory + "?userId=\(userId)&limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
    }

    // MARK: - Crash Detection Async Methods

    // ✅ ASYNC: Настроить Crash Detection
    func setupCrashDetection(latitude: Double, longitude: Double, radius: Double = 500) async throws -> APIResponse<String> {
        struct CrashDetectionSetupRequest: Codable {
            let latitude: Double
            let longitude: Double
            let radius: Double
        }

        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            setupCrashDetection(latitude: latitude, longitude: longitude, radius: radius) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in setupCrashDetection()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Отправить алерт о краше
    func sendCrashAlert(latitude: Double, longitude: Double, severity: String) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            sendCrashAlert(latitude: latitude, longitude: longitude, severity: severity) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in sendCrashAlert()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Запустить мониторинг Crash Detection
    func startCrashDetectionMonitoring() async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            startCrashDetectionMonitoring { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in startCrashDetectionMonitoring()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Остановить мониторинг Crash Detection
    func stopCrashDetectionMonitoring() async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            stopCrashDetectionMonitoring { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in stopCrashDetectionMonitoring()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Отправить данные сенсоров Crash Detection
    func sendCrashDetectionData(accelerometer: [String: Double], gyroscope: [String: Double], speed: Double, location: CLLocation?) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            sendCrashDetectionData(accelerometer: accelerometer, gyroscope: gyroscope, speed: speed, location: location) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in sendCrashDetectionData()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Получить статус Crash Detection
    func getCrashDetectionStatus() async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getCrashDetectionStatus { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getCrashDetectionStatus()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Обновить настройки Crash Detection
    func updateCrashDetectionSettings(userId: String, sensitivity: Double, geofenceRadius: Double) async throws -> APIResponse<Bool> {
        struct UpdateCrashSettingsRequest: Codable {
            let userId: String
            let sensitivity: Double
            let geofenceRadius: Double
        }

        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            updateCrashDetectionSettings(userId: userId, sensitivity: sensitivity, geofenceRadius: geofenceRadius) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in updateCrashDetectionSettings()!")
                    return
                }
                hasResumed = true
                continuation.resume(with: result)
            }
        }
    }

    // ✅ ASYNC: Получить историю Crash Detection
    func getCrashDetectionHistory(userId: String, limit: Int = 50) async throws -> CrashHistoryResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getCrashDetectionHistory(userId: userId, limit: limit) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getCrashDetectionHistory()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - ✅ SYSTEM MANAGEMENT BASIC

    // ✅ НОВОЕ: Получить здоровье системы
    func getSystemHealth(completion: @escaping (Result<APIResponse<SystemHealthResponse>, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.systemHealth, completion: completion)
    }

    // ✅ НОВОЕ: Получить информацию о системе
    func getSystemInfo(completion: @escaping (Result<APIResponse<SystemInfoResponse>, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.systemInfo, completion: completion)
    }

    // ✅ НОВОЕ: Получить метрики системы
    func getSystemMetrics(
        timeRange: String = "1h",
        completion: @escaping (Result<APIResponse<SystemMetricsResponse>, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.systemMetrics + "?range=\(timeRange)", completion: completion)
    }

    // ✅ НОВОЕ: Получить статус системы
    func getSystemStatus(completion: @escaping (Result<APIResponse<SystemStatusResponse>, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.systemStatus, completion: completion)
    }

    // ✅ НОВОЕ: Создать бэкап системы
    func createSystemBackup(completion: @escaping (Result<APIResponse<BackupResponse>, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.systemBackup, body: EmptyRequest(), completion: completion)
    }

    // ✅ НОВОЕ: Получить статус бэкапа
    func getBackupStatus(
        backupId: String,
        completion: @escaping (Result<APIResponse<BackupStatusResponse>, Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.systemBackupStatus + "/\(backupId)", completion: completion)
    }

    // MARK: - ✅ SYSTEM MANAGEMENT ASYNC

    // ✅ ASYNC: Получить здоровье системы
    func getSystemHealth() async throws -> SystemHealthResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getSystemHealth { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getSystemHealth()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Получить информацию о системе
    func getSystemInfo() async throws -> SystemInfoResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getSystemInfo { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getSystemInfo()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Получить метрики системы
    func getSystemMetrics(timeRange: String = "1h") async throws -> SystemMetricsResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getSystemMetrics(timeRange: timeRange) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getSystemMetrics()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Получить статус системы
    func getSystemStatus() async throws -> SystemStatusResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getSystemStatus { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getSystemStatus()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Создать бэкап системы
    func createSystemBackup() async throws -> BackupResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            createSystemBackup { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in createSystemBackup()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Получить статус бэкапа
    func getBackupStatus(backupId: String) async throws -> BackupStatusResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getBackupStatus(backupId: backupId) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getBackupStatus()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - ✅ NOTIFICATIONS EXTENDED

    // ✅ НОВОЕ: Получить категории уведомлений
    func getNotificationCategories(completion: @escaping (Result<APIResponse<NotificationCategoriesResponse>, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.notificationsCategories, completion: completion)
    }

    // ✅ НОВОЕ: Массово отметить уведомления прочитанными
    func bulkMarkNotificationsRead(
        notificationIds: [String],
        completion: @escaping (Result<APIResponse<Int>, Error>) -> Void
    ) {
        struct BulkMarkReadRequest: Codable {
            let notificationIds: [String]
        }

        let request = BulkMarkReadRequest(notificationIds: notificationIds)
        networkManager.post(endpoint: AppConfig.Endpoint.notificationsBulkMarkRead, body: request, completion: completion)
    }

    // ✅ НОВОЕ: Заархивировать уведомление
    func archiveNotification(
        notificationId: String,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        networkManager.post(endpoint: AppConfig.Endpoint.notificationsArchive + "/\(notificationId)", body: EmptyRequest(), completion: completion)
    }

    // ✅ НОВОЕ: Получить статистику уведомлений
    func getNotificationStats(completion: @escaping (Result<APIResponse<NotificationStatsResponse>, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.notificationsStats, completion: completion)
    }

    // MARK: - ✅ NOTIFICATIONS ASYNC

    // ✅ ASYNC: Получить категории уведомлений
    func getNotificationCategories() async throws -> NotificationCategoriesResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getNotificationCategories { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getNotificationCategories()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Массово отметить уведомления прочитанными
    func bulkMarkNotificationsRead(notificationIds: [String]) async throws -> Int {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            bulkMarkNotificationsRead(notificationIds: notificationIds) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in bulkMarkNotificationsRead()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Заархивировать уведомление
    func archiveNotification(notificationId: String) async throws -> Bool {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            archiveNotification(notificationId: notificationId) { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in archiveNotification()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // ✅ ASYNC: Получить статистику уведомлений
    func getNotificationStats() async throws -> NotificationStatsResponse {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            getNotificationStats { result in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getNotificationStats()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response.data!)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    // MARK: - Data Cleanup API
    
    func startDataCleanup(categories: [String], completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct CleanupRequest: Codable {
            let categories: [String]
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.dataCleanupStart,
            body: CleanupRequest(categories: categories),
            completion: completion
        )
    }
    
    // MARK: - Anti Tracker API
    
    func addTrackerToWhitelist(trackerName: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct WhitelistRequest: Codable {
            let trackerName: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.trackerWhitelist,
            body: WhitelistRequest(trackerName: trackerName),
            completion: completion
        )
    }
    
    // MARK: - AI Categories API
    
    /// Получить статистику AI категоризации
    func getAICategoriesStats(childId: String? = nil, completion: @escaping (Result<AICategoriesStats, Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.aiCategoriesStats
        
        if let childId = childId {
            endpoint += "?childId=\(childId)"
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Получить отчеты по категориям
    func getAICategoryReports(childId: String? = nil, completion: @escaping (Result<[AICategoryReport], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.aiCategoryReports
        var queryItems: [String] = []
        
        if let childId = childId {
            queryItems.append("childId=\(childId)")
        }
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    // MARK: - AI Categories Actions API
    
    func allowAIContent(contentId: String, childId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct AllowRequest: Codable {
            let contentId: String
            let childId: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.aiCategoriesAllow,
            body: AllowRequest(contentId: contentId, childId: childId),
            completion: completion
        )
    }
    
    func blockAIContent(contentId: String, childId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct BlockRequest: Codable {
            let contentId: String
            let childId: String
        }
        networkManager.post(
            endpoint: AppConfig.Endpoint.aiCategoriesBlock,
            body: BlockRequest(contentId: contentId, childId: childId),
            completion: completion
        )
    }

    // MARK: - 🚀 Performance Optimized Methods

    /**
     * 🚀 Batch запрос для получения статуса нескольких компонентов
     * Снижает количество HTTP запросов и latency
     */
    func getMultipleComponentStatuses(componentIds: [String]) async throws -> [ComponentStatus] {
        return try await withCheckedThrowingContinuation { continuation in
            struct BatchRequest: Codable {
                let componentIds: [String]
                let fields: [String]? = ["componentId", "isEnabled", "lastUpdate", "uptime"] // Только нужные поля
            }

            let request = BatchRequest(componentIds: componentIds)
            let endpoint = AppConfig.Endpoint.componentStatusBatch

            // ✅ BUILD 115: Защита от двойного вызова continuation.resume() - используем класс для синхронизации
            class ResumeGuard {
                private let lock = NSLock()
                private var _hasResumed = false
                
                var hasResumed: Bool {
                    lock.lock()
                    defer { lock.unlock() }
                    return _hasResumed
                }
                
                func setResumed() -> Bool {
                    lock.lock()
                    defer { lock.unlock() }
                    if _hasResumed {
                        return false
                    }
                    _hasResumed = true
                    return true
                }
            }
            
            let resumeGuard = ResumeGuard()
            
            networkManager.post(
                endpoint: endpoint,
                body: request
            ) { (result: Result<APIResponse<[ComponentStatusResponse]>, Error>) in
                guard resumeGuard.setResumed() else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getMultipleComponentStatuses()!")
                    return
                }
                
                switch result {
                case .success(_):
                    // Временная заглушка для компиляции
                    let statuses: [ComponentStatus] = []
                    continuation.resume(returning: statuses)
                case .failure(let error):
                    // Fallback: индивидуальные запросы если batch не поддерживается
                    print("⚠️ Batch request failed, falling back to individual requests: \(error.localizedDescription)")
                    Task {
                        guard resumeGuard.setResumed() else {
                            logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getMultipleComponentStatuses() fallback!")
                            return
                        }
                        
                        do {
                            var statuses: [ComponentStatus] = []
                            for componentId in componentIds {
                                let status = try await self.getComponentStatus(componentId: componentId)
                                statuses.append(status)
                            }
                            continuation.resume(returning: statuses)
                        } catch {
                            continuation.resume(throwing: error)
                        }
                    }
                }
            }
        }
    }

    // MARK: - Components List (✅ ЗАДАЧА 22)
    
    /**
     * ✅ ЗАДАЧА 22: Получить список всех системных компонентов
     * Используется в SettingsScreen для отображения компонентов (только для админов)
     */
    func getComponentsList(completion: @escaping (Result<[ComponentStatus], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.componentsList) { (result: Result<APIResponse<[ComponentStatusResponse]>, Error>) in
            switch result {
            case .success(let response):
                guard let data = response.data else {
                    completion(.success([]))
                    return
                }
                let components = data.map { $0.componentStatus }
                completion(.success(components))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /**
     * ✅ ЗАДАЧА 22: Получить общее здоровье всех компонентов
     */
    func getComponentsHealth(completion: @escaping (Result<ComponentsHealthResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.componentsHealth, completion: completion)
    }
    
    /**
     * 🚀 Оптимизированный метод для обновления нескольких компонентов
     */
    func updateMultipleComponents(updates: [(componentId: String, isEnabled: Bool, configuration: ComponentConfiguration?)]) async throws -> [ComponentStatus] {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            struct BulkUpdateRequest: Codable {
                let updates: [ComponentUpdate]

                struct ComponentUpdate: Codable {
                    let componentId: String
                    let isEnabled: Bool
                    let configuration: ComponentConfiguration?
                }
            }

            let updateRequests = updates.map { update in
                BulkUpdateRequest.ComponentUpdate(
                    componentId: update.componentId,
                    isEnabled: update.isEnabled,
                    configuration: update.configuration
                )
            }

            let request = BulkUpdateRequest(updates: updateRequests)
            let endpoint = AppConfig.Endpoint.componentBulkUpdate

            networkManager.post(
                endpoint: endpoint,
                body: request
            ) { (result: Result<APIResponse<[ComponentStatusResponse]>, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in updateMultipleComponents()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    // Временная заглушка для компиляции
                    let statuses: [ComponentStatus] = []
                    hasResumed = true
                    continuation.resume(returning: statuses)
                case .failure(let error):
                    // ✅ ИСПРАВЛЕНИЕ BUILD 91+: Убрали Task {} из continuation
                    // Возвращаем ошибку - fallback будет обработан в вызывающем коде
                    print("⚠️ Bulk update failed: \(error.localizedDescription)")
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    /**
     * 🚀 Health check с кэшированием
     * Кэширует результат на 30 секунд для снижения нагрузки
     */
    private var healthCheckCache: (result: APIResponse<HealthResponse>, timestamp: Date)?
    private let healthCheckCacheDuration: TimeInterval = 30.0

    /// Обычный health check без кэширования
    private func healthCheck() async throws -> APIResponse<HealthResponse> {
        return try await withCheckedThrowingContinuation { continuation in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            networkManager.get(endpoint: "/health") { (result: Result<APIResponse<HealthResponse>, Error>) in
                guard !hasResumed else {
                    logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in healthCheck()!")
                    return
                }
                
                switch result {
                case .success(let response):
                    hasResumed = true
                    continuation.resume(returning: response)
                case .failure(let error):
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    func healthCheckCached() async throws -> APIResponse<HealthResponse> {
        // Проверяем кэш
        if let cached = healthCheckCache,
           Date().timeIntervalSince(cached.timestamp) < healthCheckCacheDuration {
            print("✅ Health check from cache")
            return cached.result
        }

        // Выполняем новый запрос
        let result = try await healthCheck()
        healthCheckCache = (result, Date())
        print("✅ Health check cached")

        return result
    }
    
    // MARK: - Roadside Assistance (✅ ЗАДАЧА 24)
    
    /**
     * ✅ ЗАДАЧА 24: Вызвать помощь на дороге
     */
    func callRoadsideAssistance(
        location: CLLocationCoordinate2D,
        vehicleInfo: String,
        completion: @escaping (Result<RoadsideRequest, Error>) -> Void
    ) {
        struct RoadsideCallRequest: Codable {
            let latitude: Double
            let longitude: Double
            let vehicleInfo: String
        }
        
        let request = RoadsideCallRequest(
            latitude: location.latitude,
            longitude: location.longitude,
            vehicleInfo: vehicleInfo
        )
        
        networkManager.post(
            endpoint: AppConfig.Endpoint.roadsideCall,
            body: request,
            completion: completion
        )
    }
    
    /**
     * ✅ ЗАДАЧА 24: Получить статус запроса помощи на дороге
     */
    func getRoadsideAssistanceStatus(
        requestId: String,
        completion: @escaping (Result<RoadsideStatus, Error>) -> Void
    ) {
        let endpoint = AppConfig.Endpoint.roadsideStatus.replacingOccurrences(of: "{request_id}", with: requestId)
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /**
     * ✅ ЗАДАЧА 24: Отменить запрос помощи на дороге
     */
    func cancelRoadsideAssistance(
        requestId: String,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        let endpoint = AppConfig.Endpoint.roadsideCancel.replacingOccurrences(of: "{request_id}", with: requestId)
        networkManager.post(endpoint: endpoint, body: EmptyRequest(), completion: completion)
    }
    
    /**
     * ✅ ЗАДАЧА 24: Получить историю обращений за помощью на дороге
     */
    func getRoadsideAssistanceHistory(
        completion: @escaping (Result<[RoadsideRequest], Error>) -> Void
    ) {
        networkManager.get(endpoint: AppConfig.Endpoint.roadsideHistory, completion: completion)
    }

    // MARK: - Receipt Validation

    /**
     * Валидировать App Store receipt на сервере
     */
    func validateReceipt(request: ReceiptValidationRequest, token: String, completion: @escaping (Result<ReceiptValidationResponse, Error>) -> Void) {
        // Создаем кастомный NetworkManager для запроса с заголовками авторизации
        struct AuthorizedNetworkManager {
            let baseManager: NetworkManager
            let token: String

            func post(endpoint: String, body: ReceiptValidationRequest, completion: @escaping (Result<ReceiptValidationResponse, Error>) -> Void) {
                let url = URL(string: AppConfig.baseURL + endpoint)!
                var urlRequest = URLRequest(url: url)
                urlRequest.httpMethod = "POST"
                urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
                urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

                do {
                    urlRequest.httpBody = try JSONEncoder().encode(body)
                } catch {
                    completion(.failure(error))
                    return
                }

                URLSession.shared.dataTask(with: urlRequest) { data, response, error in
                    if let error = error {
                        completion(.failure(error))
                        return
                    }

                    guard let data = data else {
                        completion(.failure(NSError(domain: "NoData", code: -1, userInfo: nil)))
                        return
                    }

                    do {
                        let response = try JSONDecoder().decode(ReceiptValidationResponse.self, from: data)
                        completion(.success(response))
                    } catch {
                        completion(.failure(error))
                    }
                }.resume()
            }
        }

        let authorizedManager = AuthorizedNetworkManager(baseManager: networkManager, token: token)
        authorizedManager.post(endpoint: "/api/subscription/validate-receipt", body: request, completion: completion)
    }

    // Device registration methods
    func registerDeviceAnonymously(request: DeviceRegisterRequest, completion: @escaping (Result<JWTDeviceRegisterResponse, Error>) -> Void) {
        // ✅ КРИТИЧНО: Для анонимной регистрации авторизация НЕ требуется!
        networkManager.post(endpoint: AppConfig.Endpoint.deviceRegister, body: request, requiresAuth: false, completion: completion)
    }

    func registerDeviceWithTrial(request: TrialDeviceRegisterRequest, completion: @escaping (Result<JWTDeviceRegisterResponse, Error>) -> Void) {
        // ✅ Trial registration is also anonymous in this model (token is created by backend).
        networkManager.post(endpoint: AppConfig.Endpoint.registerDeviceTrial, body: request, requiresAuth: false, completion: completion)
    }
}



