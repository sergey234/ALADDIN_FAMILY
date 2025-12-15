import Foundation

/**
 * Кэшированный API сервис для ALADDIN
 * Интегрирует кэширование с существующим APIService
 */
class CachedAPIService: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    private let cacheManager: CacheManager
    private let retryManager: RetryManager
    
    // MARK: - Configuration
    
    /// Включено ли кэширование
    @Published var isCachingEnabled: Bool = true
    
    /// Включен ли офлайн режим
    @Published var isOfflineModeEnabled: Bool = true
    
    // MARK: - Initialization
    
    init(
        apiService: APIService = APIService.shared,
        cacheManager: CacheManager = CacheManager.shared,
        retryManager: RetryManager = RetryManager.balanced()
    ) {
        self.apiService = apiService
        self.cacheManager = cacheManager
        self.retryManager = retryManager
    }
    
    // MARK: - VPN API Methods
    
    /**
     * Получает статус VPN с кэшированием
     */
    func getVPNStatus() async -> Result<NetworkProtectionStatusResponse, NetworkError> {
        let cacheKey = "vpn_status"
        
        // Пытаемся получить из кэша (асинхронно)
        if isCachingEnabled, let cachedStatus: NetworkProtectionStatusResponse = await cacheManager.retrieve(NetworkProtectionStatusResponse.self, forKey: cacheKey) {
            print("💾 CachedAPI: VPN статус получен из кэша")
            return .success(cachedStatus)
        }
        
        // Получаем с сервера
        let result = await retryManager.execute {
            try await self.apiService.getVPNStatus()
        }
        
        switch result {
        case .success(let status):
            // Сохраняем в кэш (асинхронно)
            if isCachingEnabled {
                await cacheManager.store(status, forKey: cacheKey, ttl: 30, priority: .high)
            }
            return .success(status)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Подключается к VPN с кэшированием
     */
    func connectVPN() async -> Result<VPNConnectResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.connectVPN()
        }
        
        switch result {
        case .success(let response):
            // Очищаем кэш VPN статуса при изменении
            if isCachingEnabled {
                cacheManager.remove(key: "vpn_status")
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Отключается от VPN с кэшированием
     */
    func disconnectVPN() async -> Result<VPNDisconnectResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.disconnectVPN()
        }
        
        switch result {
        case .success(let response):
            // Очищаем кэш VPN статуса при изменении
            if isCachingEnabled {
                cacheManager.remove(key: "vpn_status")
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Family API Methods
    
    /**
     * Получает список членов семьи с кэшированием
     */
    func getFamilyMembers() async -> Result<FamilyMembersResponse, NetworkError> {
        let cacheKey = "family_members"
        
        // Пытаемся получить из кэша (асинхронно)
        if isCachingEnabled, let cachedMembers: FamilyMembersResponse = await cacheManager.retrieve(FamilyMembersResponse.self, forKey: cacheKey) {
            print("💾 CachedAPI: Список семьи получен из кэша")
            return .success(cachedMembers)
        }
        
        // Получаем с сервера
        let result = await retryManager.execute {
            try await self.apiService.getFamilyMembers()
        }
        
        switch result {
        case .success(let members):
            // Сохраняем в кэш (асинхронно)
            if isCachingEnabled {
                await cacheManager.store(members, forKey: cacheKey, ttl: 300, priority: .normal)
            }
            return .success(members)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Добавляет члена семьи с обновлением кэша
     */
    func addFamilyMember(_ member: FamilyMemberRequest) async -> Result<FamilyMemberResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.addFamilyMember(member)
        }
        
        switch result {
        case .success(let response):
            // Очищаем кэш списка семьи при изменении
            if isCachingEnabled {
                cacheManager.remove(key: "family_members")
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Удаляет члена семьи с обновлением кэша
     */
    func removeFamilyMember(_ memberId: String) async -> Result<FamilyMemberResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.removeFamilyMember(memberId)
        }
        
        switch result {
        case .success(let response):
            // Очищаем кэш списка семьи при изменении
            if isCachingEnabled {
                cacheManager.remove(key: "family_members")
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Analytics API Methods
    
    /**
     * Получает аналитику с кэшированием
     */
    func getAnalytics(_ request: AnalyticsRequest) async -> Result<AnalyticsResponse, NetworkError> {
        let cacheKey = "analytics_\(request.type.rawValue)_\(request.period.rawValue)"
        
        // Пытаемся получить из кэша
        if isCachingEnabled, let cachedAnalytics: AnalyticsResponse = await cacheManager.retrieve(AnalyticsResponse.self, forKey: cacheKey) {
            print("💾 CachedAPI: Аналитика получена из кэша")
            return .success(cachedAnalytics)
        }
        
        // Получаем с сервера
        let result = await retryManager.execute {
            try await self.apiService.getAnalytics(request)
        }
        
        switch result {
        case .success(let analytics):
            // Сохраняем в кэш
            if isCachingEnabled {
                await cacheManager.store(analytics, forKey: cacheKey, ttl: 600, priority: .normal)
            }
            return .success(analytics)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Notifications API Methods
    
    /**
     * Получает уведомления с кэшированием
     */
    func getNotifications() async -> Result<[NotificationResponse], NetworkError> {
        let cacheKey = "notifications"
        
        // Пытаемся получить из кэша
        if isCachingEnabled, let cachedNotifications: [NotificationResponse] = await cacheManager.retrieve([NotificationResponse].self, forKey: cacheKey) {
            print("💾 CachedAPI: Уведомления получены из кэша")
            return .success(cachedNotifications)
        }
        
        // Получаем с сервера
        let result = await withCheckedContinuation { (continuation: CheckedContinuation<Result<[NotificationResponse], NetworkError>, Never>) in
            apiService.getNotifications { apiResult in
                switch apiResult {
                case .success(let notifications):
                    continuation.resume(returning: .success(notifications))
                case .failure(let error):
                    continuation.resume(returning: .failure(NetworkError.from(error)))
                }
            }
        }
        
        switch result {
        case .success(let notifications):
            // Сохраняем в кэш
            if isCachingEnabled {
                await cacheManager.store(notifications, forKey: cacheKey, ttl: 180, priority: .high)
            }
            return .success(notifications)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Отмечает уведомление как прочитанное с обновлением кэша
     */
    func markNotificationAsRead(_ notificationId: String) async -> Result<NotificationResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.markNotificationAsRead(notificationId)
        }
        
        switch result {
        case .success(let response):
            // Очищаем кэш уведомлений при изменении
            if isCachingEnabled {
                cacheManager.remove(key: "notifications")
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Subscriptions API Methods
    
    /**
     * Получает информацию о подписке с кэшированием
     */
    func getSubscriptionInfo() async -> Result<SubscriptionResponse, NetworkError> {
        let cacheKey = "subscription_info"
        
        // Пытаемся получить из кэша
        if isCachingEnabled, let cachedSubscription: SubscriptionResponse = await cacheManager.retrieve(SubscriptionResponse.self, forKey: cacheKey) {
            print("💾 CachedAPI: Информация о подписке получена из кэша")
            return .success(cachedSubscription)
        }
        
        // Получаем с сервера
        let result = await retryManager.execute {
            try await self.apiService.getSubscriptionInfo()
        }
        
        switch result {
        case .success(let subscription):
            // Сохраняем в кэш
            if isCachingEnabled {
                await cacheManager.store(subscription, forKey: cacheKey, ttl: 1800, priority: .normal)
            }
            return .success(subscription)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Auth API Methods
    
    /**
     * Авторизуется с кэшированием токена
     */
    func login(_ request: LoginRequest) async -> Result<LoginResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.login(request)
        }
        
        switch result {
        case .success(let response):
            // Очищаем весь кэш при смене пользователя
            if isCachingEnabled {
                cacheManager.clear()
            }
            return .success(response)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    /**
     * Выходит из системы с очисткой кэша
     */
    func logout() async -> Result<LogoutResponse, NetworkError> {
        let result = await retryManager.execute {
            try await self.apiService.logout()
        }
        
        // Очищаем весь кэш при выходе
        if isCachingEnabled {
            cacheManager.clear()
        }
        
        return result
    }
    
    // MARK: - Device API Methods
    
    /**
     * Получает информацию об устройстве с кэшированием
     */
    func getDeviceInfo() async -> Result<DeviceInfoResponse, NetworkError> {
        let cacheKey = "device_info"
        
        // Пытаемся получить из кэша
        if isCachingEnabled, let cachedDeviceInfo: DeviceInfoResponse = await cacheManager.retrieve(DeviceInfoResponse.self, forKey: cacheKey) {
            print("💾 CachedAPI: Информация об устройстве получена из кэша")
            return .success(cachedDeviceInfo)
        }
        
        // Получаем с сервера
        let result = await retryManager.execute {
            try await self.apiService.getDeviceInfo()
        }
        
        switch result {
        case .success(let deviceInfo):
            // Сохраняем в кэш
            if isCachingEnabled {
                cacheManager.store(deviceInfo, forKey: cacheKey, ttl: 3600, priority: .low)
            }
            return .success(deviceInfo)
        case .failure(let error):
            return .failure(error)
        }
    }
    
    // MARK: - Cache Management
    
    /**
     * Очищает кэш для конкретного типа данных
     */
    func clearCache(for dataType: CacheDataType) {
        switch dataType {
        case .vpn:
            cacheManager.remove(key: "vpn_status")
        case .family:
            cacheManager.remove(key: "family_members")
        case .analytics:
            // Очищаем все ключи аналитики
            let keys = ["analytics_threats_daily", "analytics_threats_weekly", "analytics_threats_monthly",
                       "analytics_usage_daily", "analytics_usage_weekly", "analytics_usage_monthly"]
            for key in keys {
                cacheManager.remove(key: key)
            }
        case .notifications:
            cacheManager.remove(key: "notifications")
        case .subscription:
            cacheManager.remove(key: "subscription_info")
        case .device:
            cacheManager.remove(key: "device_info")
        case .all:
            cacheManager.clear()
        }
        
        print("💾 CachedAPI: Очищен кэш для \(dataType)")
    }
    
    /**
     * Получает статистику кэша
     */
    func getCacheStatistics() -> CacheStatistics {
        return cacheManager.statistics
    }
    
    /**
     * Получает информацию о кэше
     */
    func getCacheInfo() -> CacheInfo {
        return cacheManager.getCacheInfo()
    }
}

// MARK: - CacheDataType

/**
 * Типы данных для управления кэшем
 */
enum CacheDataType: String, CaseIterable {
    case vpn = "vpn"
    case family = "family"
    case analytics = "analytics"
    case notifications = "notifications"
    case subscription = "subscription"
    case device = "device"
    case all = "all"
    
    var displayName: String {
        switch self {
        case .vpn:
            return "VPN"
        case .family:
            return "Семья"
        case .analytics:
            return "Аналитика"
        case .notifications:
            return "Уведомления"
        case .subscription:
            return "Подписка"
        case .device:
            return "Устройство"
        case .all:
            return "Все данные"
        }
    }
}

