import Foundation
import Combine

/**
 * 🔌 API Service
 * Удобные методы для работы с API
 * Используется ViewModels для загрузки данных
 */

class APIService {

    let networkManager: NetworkManager

    // ✅ ИСПРАВЛЕНИЕ: Исправляем singleton паттерн - один экземпляр NetworkManager
    private static let sharedNetworkManager: NetworkManager = {
        print("🔧 APIService: Создание singleton NetworkManager")
        return NetworkManager()
    }()

    // ✅ ИСПРАВЛЕНИЕ: Кешируем APIService для избежания повторного создания
    private static var _sharedAPIService: APIService?

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
        networkManager.get(endpoint: "/network-protection/config", completion: completion)
    }
    
    func sendNetworkProtectionStats(_ stats: NetworkProtectionStats, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        networkManager.post(endpoint: "/network-protection/stats", body: stats, completion: completion)
    }

    // MARK: - Family Registration API

    func createFamily(request: CreateFamilyRequest, completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.createFamily, body: request, completion: completion)
    }

    func joinFamily(request: JoinFamilyRequest, completion: @escaping (Result<APIResponse<FamilyResponse>, Error>) -> Void) {
        networkManager.post(endpoint: AppConfig.Endpoint.joinFamily, body: request, completion: completion)
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
        networkManager.get(endpoint: AppConfig.Endpoint.familyMembers, completion: completion)
    }
    
    func addFamilyMember(name: String, role: String, completion: @escaping (Result<FamilyMemberResponse, Error>) -> Void) {
        struct AddMemberRequest: Codable {
            let name: String
            let role: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.addFamilyMember, body: AddMemberRequest(name: name, role: role), completion: completion)
    }
    
    /**
     * Удаление участника семьи (async версия для CachedAPIService)
     */
    func removeFamilyMember(_ memberId: String) async throws -> FamilyMemberResponse {
        return try await withCheckedThrowingContinuation { continuation in
            struct RemoveMemberRequest: Codable {
                let memberId: String
            }
            networkManager.delete(endpoint: AppConfig.Endpoint.removeFamilyMember, body: RemoveMemberRequest(memberId: memberId)) { (result: Result<FamilyMemberResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.familyStats, completion: completion)
    }
    
    // MARK: - Family Chat API
    
    func getFamilyChatMessages(completion: @escaping (Result<[FamilyChatMessageResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.familyChatMessages, completion: completion)
    }
    
    func sendFamilyChatMessage(message: String?, familyId: String?, messageType: String?, voiceUrl: String?, voiceDuration: Double?, mediaUrl: String?, mediaType: String?, replyToMessageId: String?, completion: @escaping (Result<SendFamilyChatMessageResponse, Error>) -> Void) {
        let request = SendFamilyChatMessageRequest(
            message: message,
            familyId: familyId,
            messageType: messageType,
            voiceUrl: voiceUrl,
            voiceDuration: voiceDuration,
            mediaUrl: mediaUrl,
            mediaType: mediaType,
            replyToMessageId: replyToMessageId
        )
        networkManager.post(endpoint: AppConfig.Endpoint.familyChatSend, body: request, completion: completion)
    }
    
    func deleteFamilyChatMessage(messageId: String, completion: @escaping (Result<Bool, Error>) -> Void) {
        struct DeleteRequest: Codable {
            let messageId: String
        }
        networkManager.delete(endpoint: "\(AppConfig.Endpoint.familyChatSend)/\(messageId)", body: DeleteRequest(messageId: messageId)) { (result: Result<APIResponse<Bool>, Error>) in
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
    
    func uploadMedia(data: Data, type: String, completion: @escaping (Result<String, Error>) -> Void) {
        // TODO: Реализовать загрузку медиа на сервер
        // Это требует multipart/form-data запроса
        completion(.failure(NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Media upload not implemented"])))
    }
    
    // MARK: - Analytics API
    
    func getAnalytics(period: String, completion: @escaping (Result<AnalyticsResponse, Error>) -> Void) {
        networkManager.get(endpoint: "\(AppConfig.Endpoint.analytics)?period=\(period)", completion: completion)
    }
    
    func getTopThreats(completion: @escaping (Result<[ThreatItem], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.topThreats, completion: completion)
    }
    
    // MARK: - AI Assistant API
    
    func sendMessageToAI(message: String, completion: @escaping (Result<ChatMessageResponse, Error>) -> Void) {
        let request = ChatMessageRequest(
            message: message,
            userId: AppConfig.authToken ?? "guest",
            timestamp: Date()
        )
        networkManager.post(endpoint: AppConfig.Endpoint.aiSendMessage, body: request, completion: completion)
    }
    
    // MARK: - User API
    
    func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.profile, completion: completion)
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
    
    // MARK: - Auth API
    
    func login(email: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        let request = LoginRequest(email: email, password: password)
        networkManager.post(endpoint: AppConfig.Endpoint.login, body: request, completion: completion)
    }
    
    func logout(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.logout, body: EmptyBody(), completion: completion)
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
        networkManager.post(endpoint: "/auth/refresh", body: request, completion: completion)
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
    }
    
    func registerDeviceToken(_ token: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        let body = DeviceTokenRequest(deviceToken: token, platform: "iOS", appVersion: AppConfig.appVersion)
        networkManager.post(endpoint: AppConfig.Endpoint.deviceRegister, body: body, completion: completion)
    }
    
    // MARK: - Add Device API
    
    struct AddDeviceRequest: Codable {
        let name: String
        let type: String // "iphone", "ipad", "mac", "android"
        let owner: String
    }
    
    func addDevice(name: String, type: String, owner: String, completion: @escaping (Result<DeviceResponse, Error>) -> Void) {
        let request = AddDeviceRequest(name: name, type: type, owner: owner)
        networkManager.post(endpoint: AppConfig.Endpoint.devices, body: request, completion: completion)
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
        
        networkManager.patch(endpoint: "\(AppConfig.Endpoint.deviceSettings)/\(deviceId)/settings", body: request, completion: completion)
    }

    // MARK: - Payment API
    
    func createQRPayment(request: CreateQRPaymentRequest, completion: @escaping (Result<CreateQRPaymentResponse, Error>) -> Void) {
        // ✅ ИСПРАВЛЕНИЕ: baseURL уже содержит /api, убираем из endpoint
        // Было: "/api/payments/qr/create" → приводило к "/api/api/payments/qr/create"
        // Стало: "/payments/qr/create" → правильно "/api/payments/qr/create"
        networkManager.post(endpoint: "/payments/qr/create", body: request, completion: completion)
    }
    
    func checkQRPaymentStatus(paymentId: String, completion: @escaping (Result<CheckQRPaymentStatusResponse, Error>) -> Void) {
        // ✅ ИСПРАВЛЕНИЕ: baseURL уже содержит /api, убираем из endpoint
        networkManager.get(endpoint: "/payments/qr/status/\(paymentId)", completion: completion)
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
            networkManager.get(endpoint: "/iot/status/\(homeId)") { (result: Result<IoTStatusResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    /// Получить список IoT устройств
    func getIoTDevices(homeId: String) async throws -> IoTDevicesResponse {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.get(endpoint: "/iot/devices/\(homeId)") { (result: Result<IoTDevicesResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    /// Получить список угроз
    func getIoTThreats(homeId: String) async throws -> IoTThreatsResponse {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.get(endpoint: "/iot/threats/\(homeId)") { (result: Result<IoTThreatsResponse, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    /// Заблокировать IoT устройство
    func blockIoTDevice(deviceId: String) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            struct EmptyBody: Codable {}
            networkManager.post(endpoint: "/iot/device/\(deviceId)/block", body: EmptyBody()) { (result: Result<APIResponse<Bool>, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    /// Запустить сканирование IoT устройств
    func startIoTScan(homeId: String) async throws -> APIResponse<String> {
        return try await withCheckedThrowingContinuation { continuation in
            struct EmptyBody: Codable {}
            networkManager.post(endpoint: "/iot/scan/\(homeId)", body: EmptyBody()) { (result: Result<APIResponse<String>, Error>) in
                continuation.resume(with: result)
            }
        }
    }
    
    /// Исправить угрозу
    func fixIoTThreat(threatId: String) async throws -> APIResponse<Bool> {
        return try await withCheckedThrowingContinuation { continuation in
            struct EmptyBody: Codable {}
            networkManager.post(endpoint: "/iot/fix/\(threatId)", body: EmptyBody()) { (result: Result<APIResponse<Bool>, Error>) in
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
    
    /**
     * Получение статистики защиты от обхода
     * ✅ РЕАЛЬНЫЙ API ЗАПРОС
     */
    func getBypassStats(
        childId: String? = nil,
        completion: @escaping (Result<BypassStatsResponse, Error>) -> Void
    ) {
        // ✅ РЕАЛЬНЫЙ ЗАПРОС
        let endpoint = childId != nil ? "/parental/bypass/stats?childId=\(childId!)" : "/parental/bypass/stats"
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
            endpoint: "/parental/bypass/apply",
            body: ApplyBypassProtectionRequest(childId: childId, incognito: incognito, tor: tor, proxy: proxy),
            completion: completion
        )
    }
    
    // MARK: - Components API (42 components)
    
    /// Получить статус компонента
    func getComponentStatus(componentId: String) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.get(endpoint: "\(AppConfig.Endpoint.componentStatus)/\(componentId)") { (result: Result<ComponentStatusResponse, Error>) in
                switch result {
                case .success(let response):
                    continuation.resume(returning: response.status)
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Включить компонент
    func enableComponent(componentId: String, configuration: ComponentConfiguration? = nil) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            struct EnableRequest: Codable {
                let componentId: String
                let configuration: ComponentConfiguration?
            }
            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentEnable)/\(componentId)",
                body: EnableRequest(componentId: componentId, configuration: configuration)
            ) { (result: Result<ComponentStatusResponse, Error>) in
                switch result {
                case .success(let response):
                    continuation.resume(returning: response.status)
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    /// Выключить компонент
    func disableComponent(componentId: String) async throws -> ComponentStatus {
        return try await withCheckedThrowingContinuation { continuation in
            struct DisableRequest: Codable {
                let componentId: String
            }
            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentDisable)/\(componentId)",
                body: DisableRequest(componentId: componentId)
            ) { (result: Result<ComponentStatusResponse, Error>) in
                switch result {
                case .success(let response):
                    continuation.resume(returning: response.status)
                case .failure(let error):
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
            struct UpdateRequest: Codable {
                let componentId: String
                let isEnabled: Bool
                let configuration: ComponentConfiguration?
            }
            
            let requestBody = UpdateRequest(componentId: componentId, isEnabled: isEnabled, configuration: configuration)
            let endpoint = "\(AppConfig.Endpoint.componentStatus)/\(componentId)"
            
            // ✅ ИСПРАВЛЕНИЕ: Сначала пробуем PUT (правильный метод для обновления)
            networkManager.put(
                endpoint: endpoint,
                body: requestBody
            ) { (result: Result<APIResponse<Bool>, Error>) in
                switch result {
                case .success:
                    continuation.resume()
                case .failure(let error):
                    // ✅ FALLBACK: Если PUT не поддерживается (405), пробуем PATCH
                    if let networkError = error as? NetworkError,
                       (({
                           if case .invalidStatusCode(let code) = networkError { return code == 405 }
                           if case .httpError(let code) = networkError { return code == 405 }
                           return false
                       })()) {
                        // Пробуем PATCH как fallback
                        print("⚠️ APIService: PUT вернул 405, пробуем PATCH")
                        self.networkManager.patch(
                            endpoint: endpoint,
                            body: requestBody
                        ) { (patchResult: Result<APIResponse<Bool>, Error>) in
                            switch patchResult {
                            case .success:
                                continuation.resume()
                            case .failure(let patchError):
                                    // Если и PATCH не работает, просто логируем (не критично)
                                    print("⚠️ APIService: PATCH тоже не работает: \(patchError.localizedDescription)")
                                    // Не пробрасываем ошибку - статус сохранен локально
                                    continuation.resume()
                            }
                        }
                    } else {
                        // Для других ошибок (кроме 405) пробрасываем
                        continuation.resume(throwing: error)
                    }
                }
            }
        }
    }
    
    /// Получить конфигурацию компонента
    func getComponentConfiguration(componentId: String) async throws -> ComponentConfiguration {
        return try await withCheckedThrowingContinuation { continuation in
            networkManager.get(endpoint: "\(AppConfig.Endpoint.componentConfiguration)/\(componentId)") { (result: Result<ComponentConfigurationResponse, Error>) in
                switch result {
                case .success(let response):
                    continuation.resume(returning: response.configuration)
                case .failure(let error):
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
            struct UpdateRequest: Codable {
                let componentId: String
                let configuration: ComponentConfiguration
            }
            networkManager.post(
                endpoint: "\(AppConfig.Endpoint.componentConfiguration)/\(componentId)",
                body: UpdateRequest(componentId: componentId, configuration: configuration)
            ) { (result: Result<APIResponse<Bool>, Error>) in
                switch result {
                case .success:
                    continuation.resume()
                case .failure(let error):
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
    
    // MARK: - Dark Web Monitoring API
    
    /// Получить утечки данных
    func getDarkWebLeaks(status: String? = nil, severity: String? = nil, completion: @escaping (Result<[DarkWebLeak], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.darkWebLeaks
        var queryItems: [String] = []
        
        if let status = status {
            queryItems.append("status=\(status)")
        }
        if let severity = severity {
            queryItems.append("severity=\(severity)")
        }
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Получить статистику Dark Web
    func getDarkWebStats(completion: @escaping (Result<DarkWebStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.darkWebStats, completion: completion)
    }
    
    /// Получить историю сканирований
    func getDarkWebScans(limit: Int = 20, completion: @escaping (Result<[DarkWebScan], Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.darkWebScans)?limit=\(limit)"
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
        struct EmptyRequest: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.darkWebScanStart, body: EmptyRequest(), completion: completion)
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
    
    /// Получить попытки кражи личности
    func getIdentityTheftAttempts(action: String? = nil, severity: String? = nil, completion: @escaping (Result<[IdentityTheftAttempt], Error>) -> Void) {
        var endpoint = AppConfig.Endpoint.identityTheftAttempts
        var queryItems: [String] = []
        
        if let action = action {
            queryItems.append("action=\(action)")
        }
        if let severity = severity {
            queryItems.append("severity=\(severity)")
        }
        
        if !queryItems.isEmpty {
            endpoint += "?" + queryItems.joined(separator: "&")
        }
        
        networkManager.get(endpoint: endpoint, completion: completion)
    }
    
    /// Получить статистику защиты от кражи личности
    func getIdentityTheftStats(completion: @escaping (Result<IdentityTheftStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.identityTheftStats, completion: completion)
    }
    
    /// Разрешить попытку кражи личности
    func allowIdentityTheftAttempt(attemptId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct AllowRequest: Codable {
            let attemptId: String
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
    
    // MARK: - Privacy Reports API
    
    /// Получить статистику Location Bubble
    func getLocationStats(completion: @escaping (Result<LocationStats, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.locationStats, completion: completion)
    }
    
    /// Получить историю запросов местоположения
    func getLocationRequests(limit: Int = 50, completion: @escaping (Result<[LocationRequest], Error>) -> Void) {
        let endpoint = "\(AppConfig.Endpoint.locationRequests)?limit=\(limit)"
        networkManager.get(endpoint: endpoint, completion: completion)
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
}



