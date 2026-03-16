//
//  SubscriptionManager.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  🛡️ CRITICAL SECURITY COMPONENT - JWT Subscription Management
//  Core security layer protecting millions of families from cyber threats
//  Handles JWT tokens, subscription state, and feature access control
//

import Foundation
import Combine
import Security

// Notification system for trial expiry alerts
import UserNotifications
import SwiftUI

// ✅ Typealias для явного указания структуры JWTPayload из APIModels.swift
// Используем полное имя структуры из APIModels для избежания конфликтов
// Примечание: JWTPayload определена в Core/Models/APIModels.swift

// Import subscription models
// Note: This file uses both local models and API models
// Models are defined in separate files in Core/Models/

// MARK: - JWT Processing

// MARK: - Subscription Events Tracking

/// 📊 Subscription Events - Analytics for conversion tracking
enum SubscriptionEvent: String, Codable {
    // Trial Events
    case trialActivated = "trial_activated"
    case trialExpired = "trial_expired"
    case trialExtended = "trial_extended"

    // Upgrade Events
    case upgradeInitiated = "upgrade_initiated"
    case upgradeCompleted = "upgrade_completed"
    case upgradeFailed = "upgrade_failed"

    // Subscription Events
    case subscriptionRenewed = "subscription_renewed"
    case subscriptionCancelled = "subscription_cancelled"
    case subscriptionExpired = "subscription_expired"

    // Feature Usage Events
    case featureAccessed = "feature_accessed"
    case featureBlocked = "feature_blocked"
    case resourceUsed = "resource_used"
    case limitExceeded = "limit_exceeded"

    // Management Events
    case restorePurchases = "restore_purchases"
    case subscriptionManaged = "subscription_managed"

    // Sync Events
    case offlineMode = "offline_mode"
    case syncCompleted = "sync_completed"
    case syncFailed = "sync_failed"
}

struct SubscriptionEventData: Codable {
    let event: SubscriptionEvent
    let timestamp: Date
    let userId: String?
    let deviceId: String
    let subscriptionLevel: String?
    let featureId: String?
    let resourceType: String?
    let amount: Int?
    let transactionId: String?
    let errorMessage: String?
    let metadata: [String: String]?

    init(
        event: SubscriptionEvent,
        userId: String? = nil,
        subscriptionLevel: String? = nil,
        featureId: String? = nil,
        resourceType: String? = nil,
        amount: Int? = nil,
        transactionId: String? = nil,
        errorMessage: String? = nil,
        metadata: [String: String]? = nil
    ) {
        self.event = event
        self.timestamp = Date()
        self.userId = userId
        self.deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        self.subscriptionLevel = subscriptionLevel
        self.featureId = featureId
        self.resourceType = resourceType
        self.amount = amount
        self.transactionId = transactionId
        self.errorMessage = errorMessage
        self.metadata = metadata
    }
}

// MARK: - Subscription Manager

/// 🛡️ Subscription Manager - Core Security Component
/// Manages JWT tokens, subscription state, and feature access control
/// Critical for protecting millions of families from cyber threats
@MainActor
final class SubscriptionManager: ObservableObject {

    // MARK: - Singleton

    static let shared = SubscriptionManager()

    // MARK: - Published Properties

    /// Current JWT token
    @Published private(set) var currentToken: JWTToken?

    /// Current subscription status
    @Published private(set) var currentSubscription: SubscriptionStatus?

    /// Trial status (if active)
    @Published private(set) var trialStatus: TrialInfo?

    /// Loading state
    @Published private(set) var isLoading = false

    /// Last error
    @Published private(set) var lastError: SubscriptionError?

    /// Offline mode indicator
    @Published private(set) var isOfflineMode = false

    /// Last sync timestamp
    @Published private(set) var lastSyncDate: Date?

    /// Events tracking
    private let eventsQueue = DispatchQueue(label: "com.aladdin.subscription.events")
    private var pendingEvents: [SubscriptionEventData] = []

    // MARK: - Private Properties

    private let keychainService = "com.aladdin.subscription"
    private let tokenKey = "jwt_token"
    private let subscriptionKey = "subscription_status"
    private let trialKey = "trial_info"

    private var cancellables = Set<AnyCancellable>()
    private let logger = MasterLogger.shared

    // 🏥 DEFENSIVE JWT: Proactive Token Health Monitor
    // 🏥 DEFENSIVE JWT: Token Health Monitor работает через singleton

    // MARK: - Initialization
    
    /// ✅ BUILD 101: Защита от повторного вызова initializeOnAppStart()
    /// SwiftUI может вызывать onAppear несколько раз при пересоздании View
    private static var hasInitialized = false
    private static let initializationLock = NSLock()

    /// Initialize on app start (async operations)
    /// ✅ BUILD 101: Добавлена защита от повторного вызова для предотвращения дублирования инициализации
    func initializeOnAppStart() async {
        SubscriptionManager.initializationLock.lock()
        defer { SubscriptionManager.initializationLock.unlock() }
        
        guard !SubscriptionManager.hasInitialized else {
            logger.business("⚠️ SubscriptionManager.initializeOnAppStart() уже вызван, пропускаем повторный вызов")
            return
        }
        
        SubscriptionManager.hasInitialized = true
        
        print("🚀🚀🚀 INITIALIZE_ON_APP_START: Method called")
        logger.business("🚀 SubscriptionManager.initializeOnAppStart() called")
        VisualLogger.shared.log("🚀 SubscriptionManager.initializeOnAppStart() called", level: .info)

        // Логируем состояние приложения при запуске
        logger.business("📊 ИНИЦИАЛИЗАЦИЯ ПОДПИСКИ - ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ")
        logger.business("📱 Устройство: \(UIDevice.current.model) (\(UIDevice.current.systemVersion))")
        logger.business("🌐 Режим сети: \(isOfflineMode ? "ОФФЛАЙН" : "ОНЛАЙН")")
        logger.business("⏰ Время запуска: \(Date())")

        // 🚀🚀🚀 DEFENSIVE JWT: ИНТЕЛЛЕКТУАЛЬНАЯ ПРОВЕРКА ТОКЕНОВ 🚀🚀🚀
        logger.business("🚀 DEFENSIVE JWT: Начинаем интеллектуальную проверку токена")

        // ШАГ 1: Используем TokenValidator для комплексного анализа
        let tokenStatus = TokenValidator.validateCurrentToken()
        logger.business("🔍 DEFENSIVE JWT: Статус токена: \(tokenStatus.description)")

        // ШАГ 2: Выполняем действия в зависимости от статуса токена
        switch tokenStatus {
        case .none:
            logger.business("📱 DEFENSIVE JWT: Токена нет - запускаем первичную регистрацию")
            await performDeviceRegistration()

        case .valid:
            logger.business("✅ DEFENSIVE JWT: Токен валиден - используем существующий")
            // Ничего не делаем, токен рабочий

        case .expired, .invalid:
            logger.business("⏰ DEFENSIVE JWT: Токен истек/невалиден - очищаем и регистрируем заново")
            await clearToken()  // Очищаем проблемный токен
            await performDeviceRegistration()  // Регистрируем заново

        case .needsRefresh:
            logger.business("🔄 DEFENSIVE JWT: Токен скоро истечет - запускаем silent refresh")
            await refreshTokenSilently()
        }

        logger.business("🎉 DEFENSIVE JWT: Инициализация завершена успешно")

        // 🚨 DEFENSIVE JWT: Emergency reset Circuit Breaker if stuck
        JWTCircuitBreaker.shared.emergencyReset()

        // Log initialization completion
        JWTEventLogger.logEvent(.healthCheckPerformed(
            tokenExists: currentToken != nil,
            timeToExpiry: currentToken?.expiresAt.timeIntervalSinceNow,
            nextCheckIn: 60
        ))

        logger.security("🚀 SubscriptionManager: App start initialization completed")
    }

    /// Check if current token is expired
    private func isTokenExpired() -> Bool {
        guard let token = currentToken else { return true }
        return JWTTokenManager.shared.isTokenExpired(token.token)
    }

    /// Parse ISO 8601 date string to Date
    /// ✅ FIXED: Handles API contract mismatch (server returns ISO strings)
    private func parseISODate(_ dateString: String?) -> Date? {
        guard let dateString = dateString else { return nil }
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime] // Поддержка формата 2026-03-05T10:19:39.616795Z
        return formatter.date(from: dateString)
    }

    /// 🔧 Helper method to create SubscriptionStatus - test different contexts
    private func createSubscriptionStatus(level: SubscriptionLevel, isActive: Bool, expiresAt: Date?, trialInfo: TrialInfo?, limits: SubscriptionLimits, components: [String]) -> SubscriptionStatus {
        return SubscriptionStatus(
            level: level,
            isActive: isActive,
            expiresAt: expiresAt,
            trialInfo: trialInfo,
            limits: limits,
            components: components,
            lastUpdated: Date()
        )
    }

    // MARK: - DEFENSIVE JWT Methods

    /// 🛡️ DEFENSIVE JWT: Perform Device Registration
    ///
    /// Safely registers device with comprehensive error handling.
    /// Part of DEFENSIVE JWT Architecture for graceful token management.
    ///
    private func performDeviceRegistration() async {
        let logger = MasterLogger.shared
        logger.business("📱 DEFENSIVE JWT: Выполняем регистрацию устройства")

        do {
            logger.business("📱 DEFENSIVE JWT: Запуск registerDeviceAnonymously()...")
            try await registerDeviceAnonymously()
            logger.business("✅ DEFENSIVE JWT: Регистрация устройства прошла успешно")

            // Проверяем, что токен был установлен
            if let token = currentToken {
                logger.business("✅ DEFENSIVE JWT: Токен успешно установлен после регистрации")
                JWTEventLogger.logDeviceRegistration(success: true, error: nil, deviceId: token.deviceId)
            } else {
                logger.error("❌ DEFENSIVE JWT: Токен не был установлен после регистрации")
                JWTEventLogger.logDeviceRegistration(success: false, error: "Token not set after registration", deviceId: "unknown")
            }

        } catch {
            logger.error("❌ DEFENSIVE JWT: Регистрация устройства провалилась: \(error.localizedDescription)")
            logger.error("❌ DEFENSIVE JWT: Тип ошибки: \(type(of: error))")
            logger.error("❌ DEFENSIVE JWT: Детали ошибки: \(error)")

            // Log failed registration
            JWTEventLogger.logDeviceRegistration(success: false, error: error.localizedDescription, deviceId: "unknown")

            // ✅ ИСПРАВЛЕНИЕ BUILD 121: Различаем типы ошибок
            // 422 (Validation Error) - это ошибка формата данных, НЕ сетевая ошибка
            // Не переходим в offline режим для ошибок валидации
            if let networkError = error as? NetworkError {
                switch networkError {
                case .httpError(422):
                    // Ошибка валидации данных - это проблема формата, не сети
                    logger.error("❌ DEFENSIVE JWT: Ошибка валидации данных (422) - проверьте формат запроса")
                    logger.error("❌ DEFENSIVE JWT: НЕ переходим в offline режим для ошибки валидации")
                    // НЕ переходим в offline режим!
                    return
                case .httpError(let code) where code >= 500:
                    // Серверные ошибки - возможно временные, переходим в offline
                    logger.business("🔄 DEFENSIVE JWT: Серверная ошибка \(code) - переходим в offline режим")
                    isOfflineMode = true
                    JWTEventLogger.logOfflineMode(reason: "Server error \(code)", willRetry: true)
                case .noConnection, .timeout, .serverUnavailable:
                    // Сетевые ошибки - переходим в offline
                    logger.business("🔄 DEFENSIVE JWT: Сетевая ошибка - переходим в offline режим")
                    isOfflineMode = true
                    JWTEventLogger.logOfflineMode(reason: "Network error: \(networkError.localizedDescription)", willRetry: true)
                default:
                    // Другие ошибки - не переходим в offline для клиентских ошибок (4xx)
                    logger.business("⚠️ DEFENSIVE JWT: Клиентская ошибка - НЕ переходим в offline режим")
                }
            } else {
                // Неизвестная ошибка - переходим в offline только если это точно сетевая проблема
                logger.business("🔄 DEFENSIVE JWT: Неизвестная ошибка - переходим в offline режим")
                isOfflineMode = true
                JWTEventLogger.logOfflineMode(reason: "Unknown error: \(error.localizedDescription)", willRetry: true)
            }
        }
    }

    /// 🔄 DEFENSIVE JWT: Silent Token Refresh
    ///
    /// Performs proactive token refresh before expiration.
    /// Part of DEFENSIVE JWT Architecture for preventing token expiry issues.
    ///
    private func refreshTokenSilently() async {
        let logger = MasterLogger.shared
        logger.business("🔄 DEFENSIVE JWT: Выполняем тихое обновление токена")

        // Пока что просто перерегистрируем устройство
        // В будущем здесь будет логика refresh token endpoint
        logger.business("🔄 DEFENSIVE JWT: Используем перерегистрацию как временное решение")
        await performDeviceRegistration()
    }

    /// 🧹 DEFENSIVE JWT: Clear Token from All Storage
    ///
    /// Completely removes token from all storage locations.
    /// Critical for DEFENSIVE JWT Architecture to prevent stale token usage.
    ///
    /// Clears from:
    /// - Keychain (secure storage)
    /// - Memory (currentToken property)
    /// - UserDefaults (fallback storage)
    ///
    func clearToken() async {
        let logger = MasterLogger.shared
        logger.business("🧹 DEFENSIVE JWT: Очищаем токен из всех хранилищ")

        // Останавливаем monitoring для старого токена
        TokenHealthMonitor.shared.stopMonitoring()
        logger.business("⏹️ DEFENSIVE JWT: Остановлен monitoring старого токена")

        // Очищаем Keychain
        KeychainManager.shared.delete(forKey: .authToken)
        KeychainManager.shared.delete(forKey: .refreshToken)
        logger.business("🗝️ DEFENSIVE JWT: Очищен Keychain")

        // Очищаем память
        currentToken = nil
        currentSubscription = nil
        logger.business("🧠 DEFENSIVE JWT: Очищена память")

        // Очищаем UserDefaults (fallback)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
        // Note: refreshToken not stored in UserDefaults, only in Keychain
        logger.business("💾 DEFENSIVE JWT: Очищены UserDefaults")

        logger.business("✅ DEFENSIVE JWT: Токен полностью очищен")
    }

    private init() {
        print("🔐🔐🔐 SUBSCRIPTION_MANAGER_INIT: Starting initialization")
        logger.security("🔐 SubscriptionManager initialized - Core security component active")

        // Load persisted data on initialization
        logger.business("💾 Loading persisted data from Keychain...")
        print("💾💾💾 LOADING_PERSISTED_DATA: About to load from Keychain")
        loadPersistedData()
        logger.business("💾 Persisted data loading completed")
        print("💾💾💾 PERSISTED_DATA_LOADED: Completed")

        // Log what was loaded
        if currentToken != nil {
            logger.business("💾 Token loaded from Keychain: deviceId=\(currentToken!.deviceId)")
        } else {
            logger.business("💾 No token found in Keychain")
        }

        if currentSubscription != nil {
            logger.business("💾 Subscription loaded from Keychain: level=\(currentSubscription!.level)")
        } else {
            logger.business("💾 No subscription found in Keychain")
        }

        // Setup automatic token refresh
        setupTokenRefresh()

        // Setup trial monitoring
        setupTrialMonitoring()

        // 🏥 DEFENSIVE JWT: Initialize proactive token health monitoring
        // 🏥 DEFENSIVE JWT: Setup proactive token monitoring
        setupTokenHealthMonitoring()

        // Setup usage tracking reset
        setupMonthlyReset()

        // Setup network monitoring
        setupNetworkMonitoring()

        // Initial offline check
        updateOfflineStatus()

        logger.business("🔐 SubscriptionManager init completed")
    }

    // MARK: - Public Interface

    /// 🔑 Check if user can access specific feature (GRANULAR CONTROL)
    func canAccessFeature(_ featureId: String) -> Bool {
        // Get current effective level
        let currentLevel = getCurrentEffectiveLevel()

        // Use FeatureRegistry for granular control
        let access = FeatureRegistry.isFeatureAvailable(featureId, for: currentLevel)

        // Track access attempt
        if access {
            trackEvent(.featureAccessed, featureId: featureId)
            logger.security("✅ Feature access granted: \(featureId) for level \(currentLevel.rawValue)")
        } else {
            trackEvent(.featureBlocked, featureId: featureId)
            logger.security("🚫 Feature access denied: \(featureId) for level \(currentLevel.rawValue)")
        }

        return access
    }

    /// Get current effective subscription level
    private func getCurrentEffectiveLevel() -> SubscriptionLevel {
        // Trial takes precedence
        if let trial = trialStatus, trial.isActive {
            return .trial
        }

        // Then subscription level
        guard let subscription = currentSubscription else {
            return .free // Default to free if no subscription
        }

        return subscription.level
    }

    /// 📊 Check if user can use specific resource (with usage tracking)
    func canUseResource(_ resource: SubscriptionResource, amount: Int = 1) -> Bool {
        guard let subscription = currentSubscription else {
            trackEvent(.resourceUsed, resourceType: resource.rawValue, amount: amount, metadata: ["denied": "true", "reason": "no_subscription"])
            return false
        }

        // Check limits
        if subscription.limits.isLimitExceeded(for: resource) {
            let currentValue: Int
            switch resource {
            case .aiMessages:
                currentValue = subscription.limits.currentUsage.aiMessages
            case .scans:
                currentValue = subscription.limits.currentUsage.scans
            case .reports:
                currentValue = subscription.limits.currentUsage.reports
            case .devices:
                currentValue = subscription.limits.currentUsage.devices
            }
            logger.security("🚫 Limit exceeded for \(resource.rawValue): \(currentValue)")
            trackEvent(.limitExceeded, resourceType: resource.rawValue, metadata: ["current": String(currentValue)])
            return false
        }

        // For trial, check if resource is allowed
        if let trial = trialStatus, trial.isActive {
            let allowed = checkTrialResourceAccess(resource, amount: amount, subscription: subscription)
            if !allowed {
                trackEvent(.resourceUsed, resourceType: resource.rawValue, amount: amount, metadata: ["denied": "true", "reason": "trial_limit"])
            }
            return allowed
        }

        return true
    }

    /// 🔄 Use resource (increment usage counter)
    func useResource(_ resource: SubscriptionResource, amount: Int = 1) async {
        guard var subscription = currentSubscription else { return }

        // Increment usage
        subscription.limits.currentUsage.increment(resource, by: amount)

        // Track resource usage
        trackEvent(.resourceUsed, resourceType: resource.rawValue, amount: amount)

        // Update subscription
        await updateSubscriptionStatus(subscription)

        logger.business("📈 Resource usage updated: \(resource.rawValue) +\(amount)")
    }

    /// 🎯 Get current subscription level
    func getCurrentLevel() -> SubscriptionLevel {
        if let trial = trialStatus, trial.isActive {
            return .trial
        }
        return currentSubscription?.level ?? .free
    }

    /// 🔑 Get current JWT token for API requests
    func getCurrentToken() async -> String? {
        return currentToken?.token
    }

    /// 🎁 Activate trial period (14 days)
    func activateTrialIfNeeded() async {
        // Check if trial already used
        let hasUsedTrial = UserDefaults.standard.bool(forKey: "trial_used")
        if hasUsedTrial {
            logger.business("⏭️ Trial already used - skipping activation")
            return
        }

        // Check if already in trial
        if let trial = trialStatus, trial.isActive {
            logger.business("✅ Trial already active")
            return
        }

        logger.business("🎁 Activating 14-day trial period")

        do {
            isLoading = true

            // Calculate trial dates
            let startDate = Date()
            let endDate = Calendar.current.date(byAdding: .day, value: 14, to: startDate)!

            let trialInfo = TrialInfo(
                startDate: startDate,
                endDate: endDate,
                durationDays: 14
            )

            // First register device anonymously
            try await registerDeviceAnonymously()

            // Then update with trial info
            await updateTrialStatus(trialInfo)

            // Mark trial as used
            UserDefaults.standard.set(true, forKey: "trial_used")

            // Track trial activation
            trackEvent(.trialActivated, metadata: [
                "duration_days": "14",
                "days_remaining": String(trialInfo.daysRemaining)
            ])

            // 📅 Schedule trial expiry notifications (7, 3, 1 days before expiry)
            NotificationManager.shared.scheduleTrialNotifications(trialEndDate: endDate)

            logger.business("✅ Trial activated successfully: \(trialInfo.daysRemaining) days remaining + notifications scheduled")

        } catch {
            logger.error("❌ Failed to activate trial: \(error)")
            lastError = .serverError(error.localizedDescription)
        }

        isLoading = false
    }

    /// 🔄 Refresh subscription status from server
    func refreshSubscriptionStatus() async {
        logger.business("🔄 Refreshing subscription status from server")

        do {
            isLoading = true

            // Get current token for explicit authorization
            guard let token = currentToken?.token else {
                logger.error("❌ Refresh failed: No token available")
                lastError = .networkError
                return
            }

            let summary: SubscriptionStatusSummaryResponse = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatusWithToken(userId: "current", token: token) { result in
                    switch result {
                    case .success(let statusSummary):
                        continuation.resume(returning: statusSummary)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }

            // Convert summary to SubscriptionStatus using current subscription data
            let subscriptionStatus = summary.toSubscriptionStatus(currentSubscription: currentSubscription)

            await updateSubscriptionStatus(subscriptionStatus)

            // Update trial status if present (trial info comes from current subscription)
            if let trialInfo = currentSubscription?.trialInfo {
                await updateTrialStatus(trialInfo)
            }

            logger.business("✅ Subscription status refreshed: \(subscriptionStatus.level)")

        } catch {
            logger.error("❌ Failed to refresh subscription: \(error)")
            lastError = .networkError
        }

        isLoading = false
    }

    /// 🟡 ТЕСТИРОВАТЬ С ИЗОЛЯЦИЕЙ - проверить каждый компонент отдельно
    /// Test network connectivity without API parsing
    func testNetworkConnectivityOnly() async -> Bool {
        print("🧪🧪🧪 ISOLATED TESTING: Testing network connectivity only")

        do {
            let url = URL(string: "https://aladdin-ai.ru/api/auth/register-device")!
            print("   - Testing URL: \(url.absoluteString)")

            let (_, response) = try await URLSession.shared.data(from: url)
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0

            print("   ✅ Network test successful")
            print("   - Status Code: \(statusCode)")
            print("   - Response: \(response)")

            return statusCode == 404 || statusCode == 200 // 404 is expected for GET request to POST endpoint
        } catch let networkError {
            print("   ❌ Network test failed")
            print("   - Error: \(networkError.localizedDescription)")
            print("   - Error Type: \(type(of: networkError))")
            print("   - Error Domain: \((networkError as NSError).domain)")
            print("   - Error Code: \((networkError as NSError).code)")
            return false
        }
    }

    /// 🚨 EMERGENCY TEST: Try GET instead of POST to see if server accepts it
    func emergencyTestGET() async -> Bool {
        print("🚨🚨🚨 EMERGENCY TEST: Trying GET instead of POST")

        do {
            let url = URL(string: "https://aladdin-ai.ru/api/auth/register-device")!
            print("   - Emergency GET URL: \(url.absoluteString)")

            var request = URLRequest(url: url)
            request.httpMethod = "GET" // CHANGE TO GET!

            let (data, response) = try await URLSession.shared.data(for: request)
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0

            print("   ✅ Emergency GET successful")
            print("   - Status Code: \(statusCode)")
            if let responseString = String(data: data, encoding: .utf8) {
                print("   - Response: \(responseString.prefix(500))")
            }

            return statusCode != 0 // Any response is success
        } catch let emergencyError {
            print("   ❌ Emergency GET failed")
            print("   - Error: \(emergencyError.localizedDescription)")
            return false
        }
    }

    /// 🔑 Register device anonymously with trial
    /// Returns: JWTToken - созданный и сохраненный токен
    func registerDeviceAnonymously() async throws -> JWTToken {
        logger.business("📱 НАЧАЛО РЕГИСТРАЦИИ УСТРОЙСТВА АНОНИМНО")

        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        let deviceType = "ios"

        logger.business("📋 Параметры регистрации:")
        logger.business("   - DeviceID: \(deviceId)")
        logger.business("   - DeviceType: \(deviceType)")
        logger.business("   - Timestamp: \(Date())")

        let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: deviceType)

        // ✅ ПРОДАКШН: Реальный API вызов через APIService
        logger.business("📡 ВЫЗОВ API: POST /api/auth/register-device")
        logger.business("🔗 URL: https://aladdin-ai.ru/api/auth/register-device")
        logger.business("📤 Запрос: \(String(describing: request))")

        // ✅ FIXED BUILD 77: Убрали Task {} из continuation - возвращаем ответ сразу
        let response = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<JWTDeviceRegisterResponse, Error>) in
            // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
            var hasResumed = false
            
            APIService.shared.registerDeviceAnonymously(request: request) { [self] result in
                // ✅ BUILD 115: Проверка перед каждым вызовом continuation.resume()
                guard !hasResumed else {
                    self.logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in registerDeviceAnonymously()!")
                    return
                }
                
                switch result {
                case .success(let jwtResponse):
                    self.logger.business("✅ РЕГИСТРАЦИЯ УСТРОЙСТВА ПРОШЛА УСПЕШНО")
                    self.logger.business("📋 Получен ответ от сервера:")
                    self.logger.business("   - Token: \(jwtResponse.token.prefix(20))... (длина: \(jwtResponse.token.count))")
                    self.logger.business("   - Subscription Level: \(jwtResponse.subscription.level)")
                    self.logger.business("   - Subscription Status: \(jwtResponse.subscription.isActive ? "АКТИВНА" : "НЕАКТИВНА")")
                    self.logger.business("   - Expires At: \(jwtResponse.expiresAt)")
                    self.logger.business("   - Trial Info: \(String(describing: jwtResponse.subscription.trialInfo))")

                    // 🔍 Комплексная валидация JWT токена
                    let validationResult = self.validateJWTToken(jwtResponse.token)

                    switch validationResult {
                    case .valid:
                        self.logger.business("✅ JWT токен прошел полную валидацию")
                        // ✅ BUILD 114: Защита от повторного вызова resume
                        // ✅ BUILD 115: Продолжаем выполнение и вызываем resume только один раз ниже
                    case .invalid(let reason):
                        self.logger.error("❌ JWT токен не прошел валидацию: \(reason)")
                        let error = SubscriptionError.invalidToken
                        hasResumed = true
                        continuation.resume(throwing: error)
                        return  // ✅ Возвращаемся - resume уже вызван
                    }

                    // ✅ FIXED BUILD 77: Сразу возвращаем ответ без Task {}
                    // ✅ BUILD 114: Гарантируем, что resume вызывается только один раз
                    // ✅ BUILD 115: Защита от двойного вызова
                    hasResumed = true
                    continuation.resume(returning: jwtResponse)
                case .failure(let error):
                    self.logger.error("❌ Device registration failed", error: error)

                    // ✅ BUILD 115: Специальная обработка ошибки 401 - НЕ вызываем continuation.resume() сразу
                    if let networkError = error as? NetworkError,
                       case .httpError(401) = networkError {
                        self.logger.business("🚨 Обнаружена ошибка 401 при регистрации устройства")
                        // ✅ BUILD 115: handle401Error() обработает ошибку асинхронно
                        // НЕ вызываем continuation.resume() здесь - handle401Error() обработает
                        Task {
                            await self.handle401Error()
                        }
                        return  // ✅ Выходим, не вызывая continuation.resume()
                    } else {
                        // Показываем понятное сообщение пользователю для других ошибок
                        let userMessage = self.getUserFriendlyErrorMessage(for: error)
                        self.showUserError(message: userMessage)
                    }

                    // ✅ BUILD 115: Вызываем continuation.resume() только для не-401 ошибок
                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }

        // ✅ FIXED BUILD 77: Сохранение токена ПОСЛЕ получения ответа (последовательно, не внутри Task {})
        logger.business("💾 СОХРАНЕНИЕ ТОКЕНА В ЗАЩИЩЕННОЕ ХРАНИЛИЩЕ")

        // ✅ BUILD 121: Извлекаем реальный exp из JWT для диагностики
        let realExpFromJWT: Date?
        if let parsedToken = parseJWTToken(response.token) {
            realExpFromJWT = parsedToken.expiresAt
            logger.business("🔍 BUILD 121: Реальный exp из JWT payload:")
            logger.business("   - expiresAt из JWT: \(realExpFromJWT?.description ?? "nil")")
            logger.business("   - expiresAt из response: \(response.expiresAtDate?.description ?? "nil")")
            if let jwtExp = realExpFromJWT, let responseExp = response.expiresAtDate {
                let difference = abs(jwtExp.timeIntervalSince(responseExp))
                logger.business("   - Разница: \(Int(difference)) секунд (\(Int(difference / 3600)) часов)")
                if difference > 60 {
                    logger.business("   - ⚠️ ВНИМАНИЕ: Разница между JWT exp и response.expiresAt > 1 минуты!")
                }
            }
        } else {
            realExpFromJWT = nil
            logger.business("⚠️ BUILD 121: Не удалось распарсить JWT для извлечения exp")
        }

        // ✅ FIXED: Create JWTToken from JWTDeviceRegisterResponse with proper conversions
        // ✅ BUILD 121: Используем реальный exp из JWT, если удалось распарсить
        let finalExpiresAt: Date
        if let jwtExp = realExpFromJWT {
            finalExpiresAt = jwtExp
            logger.business("✅ BUILD 121: Используем реальный exp из JWT: \(finalExpiresAt)")
        } else {
            finalExpiresAt = response.expiresAtDate ?? Date().addingTimeInterval(86400)
            logger.business("⚠️ BUILD 121: Используем expiresAt из response или дефолт: \(finalExpiresAt)")
        }
        
        let jwtToken = JWTToken(
            token: response.token,
            deviceId: response.deviceId,
            subscriptionLevel: SubscriptionLevel(rawValue: response.subscription.level) ?? .free, // ✅ Convert String to enum
            trialInfo: response.subscription.trialInfo,
            expiresAt: finalExpiresAt, // ✅ BUILD 121: Используем реальный exp из JWT
            issuedAt: response.registeredAtDate ?? Date(),
            issuer: "ALADDIN",
            limits: SubscriptionLimits.freeLimits,      // ✅ Default limits for new user
            components: []                               // ✅ Default components for new user
        )

        await storeToken(jwtToken)

        // ✅ SOLUTION: Convert API model to internal SubscriptionStatus
        let newSubscriptionStatus = response.subscription.toSubscriptionStatus()
        await updateSubscriptionStatus(newSubscriptionStatus)

        // Логирование после сохранения токена
        logger.business("✅ Токен успешно сохранен в Keychain:")
        logger.business("   - DeviceID: \(jwtToken.deviceId)")
        logger.business("   - Уровень подписки: \(jwtToken.subscriptionLevel)")
        logger.business("   - Trial: \(jwtToken.trialInfo?.daysRemaining ?? 0) дней осталось")
        logger.business("   - Выдан: \(jwtToken.issuedAt)")
        logger.business("   - Истекает: \(jwtToken.expiresAt)")
        logger.business("   - Время жизни: \(Int(jwtToken.expiresAt.timeIntervalSince(jwtToken.issuedAt) / 3600)) часов")

        // ✅ BUILD 115: Диагностика your_member_id
        let existingMemberId = UserDefaults.standard.string(forKey: "your_member_id")
        logger.business("🔍 Проверка your_member_id после регистрации устройства:")
        logger.business("   - your_member_id в UserDefaults: \(existingMemberId ?? "НЕ НАЙДЕН")")
        if existingMemberId == nil {
            logger.business("   - ⚠️ ВНИМАНИЕ: your_member_id не сохранен!")
            logger.business("   - ℹ️ your_member_id сохраняется ТОЛЬКО при создании/присоединении к семье")
            logger.business("   - ℹ️ Для отображения ID нужно создать семью или присоединиться к существующей")
        } else {
            logger.business("   - ✅ your_member_id найден и будет отображаться на главном экране")
        }

        logger.business("🎉 РЕГИСТРАЦИЯ УСТРОЙСТВА ЗАВЕРШЕНА ПОЛНОСТЬЮ")
        logger.business("🚀 Устройство \(jwtToken.deviceId) готово к работе с реальным JWT")
        logger.business("🔐 Все защищенные API теперь доступны")

        return jwtToken
    }

    // MARK: - Private Methods


    /// 🔐 Parse JWT token and extract subscription data
    /// ✅ ИСПРАВЛЕНО: Используем структуру JWTPayload из APIModels.swift (реальная структура JWT от сервера)
    private func parseJWTToken(_ token: String) -> JWTToken? {
        // Split JWT token
        let parts = token.split(separator: ".")
        guard parts.count == 3 else { return nil }

        // Decode payload - используем структуру JWTPayload из APIModels.swift напрямую
        guard let payloadData = decodeBase64(String(parts[1])),
              let apiPayload = try? JSONDecoder().decode(JWTPayload.self, from: payloadData) else {
            return nil
        }

        // Извлекаем данные из реальной структуры JWT
        let deviceId = apiPayload.device_id ?? apiPayload.sub ?? ""
        let subscription = apiPayload.subscription
        
        // Получаем subscription level, trial info, limits, components из subscription
        let subscriptionLevel = subscription != nil ? (SubscriptionLevel(rawValue: subscription!.level) ?? .free) : .free
        let trialInfo = subscription?.trial_info
        let limits = subscription?.limits?.toSubscriptionLimits() ?? SubscriptionLimits.freeLimits
        let components = subscription?.components ?? []
        
        // Получаем exp и iat (могут быть nil, используем значения по умолчанию)
        let exp = apiPayload.exp ?? Date().addingTimeInterval(86400).timeIntervalSince1970
        let iat = apiPayload.iat ?? Date().timeIntervalSince1970
        let iss = apiPayload.iss ?? "aladdin_server"

        // Convert to our model
        return JWTToken(
            token: token,
            deviceId: deviceId,
            subscriptionLevel: subscriptionLevel,
            trialInfo: trialInfo,
            expiresAt: Date(timeIntervalSince1970: exp),
            issuedAt: Date(timeIntervalSince1970: iat),
            issuer: iss,
            limits: limits,
            components: components
        )
    }

    /// 🔄 Update subscription status
    /// ✅ ИСПРАВЛЕНО: Изменено с private на internal для использования в TokenHealthMonitor
    func updateSubscriptionStatus(_ status: SubscriptionStatus) async {
        currentSubscription = status
        persistSubscriptionStatus(status)
        logger.business("📊 Subscription updated: \(status.level)")
    }

    /// 🎁 Update trial status
    private func updateTrialStatus(_ trial: TrialInfo) async {
        // Cancel trial notifications if trial is no longer active
        if !trial.isActive && trialStatus?.isActive == true {
            NotificationManager.shared.cancelTrialNotifications()
            logger.business("❌ Trial notifications cancelled - trial no longer active")
        }

        trialStatus = trial
        persistTrialStatus(trial)
        logger.business("🎁 Trial updated: \(trial.daysRemaining) days remaining")
    }


    /// 🎯 Check trial feature access (80% of functions)
    private func checkTrialFeatureAccess(_ featureId: String, subscription: SubscriptionStatus) -> Bool {
        // Trial has access to 80% of basic functions
        // This is a simplified check - in production, would check against feature mapping
        let trialFunctions = 114 // 80% of 142
        let currentFunctions = subscription.level.maxFunctions

        // For trial, allow access if within trial limits
        return currentFunctions <= trialFunctions
    }

    /// 💳 Check subscription feature access
    private func checkSubscriptionFeatureAccess(_ featureId: String, subscription: SubscriptionStatus) -> Bool {
        // Check if feature is available for current level
        // This would check against the 142 functions mapping
        let requiredLevel = getRequiredLevelForFeature(featureId)
        return subscription.level.numericLevel >= requiredLevel.numericLevel
    }

    /// 🎯 Check trial resource access
    private func checkTrialResourceAccess(_ resource: SubscriptionResource, amount: Int, subscription: SubscriptionStatus) -> Bool {
        // Trial has limited resource access
        switch resource {
        case .aiMessages:
            return subscription.limits.currentUsage.aiMessages + amount <= 50 // Limited AI in trial
        case .scans:
            return subscription.limits.currentUsage.scans + amount <= 100 // Limited scans in trial
        case .reports:
            return subscription.limits.currentUsage.reports + amount <= 10 // Limited reports in trial
        case .devices:
            return true // Devices always allowed
        }
    }

    /// 🎯 Get required level for feature (placeholder - would be from mapping)
    private func getRequiredLevelForFeature(_ featureId: String) -> SubscriptionLevel {
        // This would be implemented with the actual feature mapping
        // For now, return free as default
        return .free
    }

    // MARK: - Persistence

    /// 💾 Load persisted data
    private func loadPersistedData() {
        #if DEBUG
        let logMessage = "💾💾💾 SubscriptionManager.loadPersistedData: Начало загрузки данных из Keychain"
        VisualLogger.shared.log(logMessage, level: .info, category: "SUBSCRIPTION")
        print(logMessage)
        #endif
        
        // Load token
        if let tokenData = loadFromKeychain(key: tokenKey),
           let token = try? JSONDecoder().decode(JWTToken.self, from: tokenData) {
            currentToken = token
            // ✅ КРИТИЧНО: Также восстанавливаем токен в AppConfig для NetworkManager
            AppConfig.authToken = token.token
            logger.business("🔑 Token restored from Keychain to AppConfig.authToken")
            #if DEBUG
            let successMessage = """
            ✅ SubscriptionManager.loadPersistedData: Токен загружен из Keychain
               - DeviceId: \(token.deviceId)
               - SubscriptionLevel: \(token.subscriptionLevel)
               - Token length: \(token.token.count)
               - AppConfig.authToken установлен: \(AppConfig.authToken != nil ? "✅ да" : "❌ нет")
            """
            VisualLogger.shared.log(successMessage, level: .success, category: "SUBSCRIPTION")
            print(successMessage)
            #endif
        } else {
            #if DEBUG
            let errorMessage = "❌ SubscriptionManager.loadPersistedData: Токен не найден в Keychain или ошибка декодирования"
            VisualLogger.shared.log(errorMessage, level: .error, category: "SUBSCRIPTION")
            print(errorMessage)
            #endif
        }

        // Load subscription
        if let subData = loadFromKeychain(key: subscriptionKey),
           let subscription = try? JSONDecoder().decode(SubscriptionStatus.self, from: subData) {
            currentSubscription = subscription
        }

        // Load trial
        if let trialData = loadFromKeychain(key: trialKey),
           let trial = try? JSONDecoder().decode(TrialInfo.self, from: trialData) {
            trialStatus = trial
        }

        logger.business("💾 Persisted data loaded")
    }

    /// 🔐 Store JWT token securely
    /// ✅ ИСПРАВЛЕНО: Изменено с private на internal для использования в TokenHealthMonitor
    func storeToken(_ token: JWTToken) async {
        print("💾💾💾 STORE_TOKEN: Starting to store token")
        print("💾💾💾 STORE_TOKEN: Token deviceId = \(token.deviceId)")
        print("💾💾💾 STORE_TOKEN: Token level = \(token.subscriptionLevel)")

        currentToken = token
        print("💾💾💾 STORE_TOKEN: Set currentToken")

        // ✅ КРИТИЧНО: Также сохраняем токен в AppConfig для NetworkManager
        AppConfig.authToken = token.token
        print("💾💾💾 STORE_TOKEN: Set AppConfig.authToken = \(token.token.prefix(20))...")
        logger.business("🔑 Token stored in AppConfig.authToken for NetworkManager")

        if let data = try? JSONEncoder().encode(token) {
            saveToKeychain(data: data, key: tokenKey)
            print("💾💾💾 STORE_TOKEN: Saved to Keychain successfully")
        } else {
            print("❌❌❌ STORE_TOKEN: Failed to encode token for Keychain")
        }

        // 🏥 DEFENSIVE JWT: Запускаем monitoring для нового токена
        TokenHealthMonitor.shared.startMonitoring()
        logger.business("🏥 DEFENSIVE JWT: Monitoring запущен для нового токена")

        print("💾💾💾 STORE_TOKEN: Completed")
    }

    /// 💾 Persist subscription status
    private func persistSubscriptionStatus(_ status: SubscriptionStatus) {
        if let data = try? JSONEncoder().encode(status) {
            saveToKeychain(data: data, key: subscriptionKey)
        }
    }

    /// 💾 Persist trial status
    private func persistTrialStatus(_ trial: TrialInfo) {
        if let data = try? JSONEncoder().encode(trial) {
            saveToKeychain(data: data, key: trialKey)
        }
    }

    // MARK: - Keychain Operations

    private func saveToKeychain(data: Data, key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]

        // Delete existing
        SecItemDelete(query as CFDictionary)

        // Add new
        let status = SecItemAdd(query as CFDictionary, nil)
        if status != errSecSuccess {
            logger.error("❌ Failed to save to keychain: \(key)")
        }
    }

    private func loadFromKeychain(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess, let data = result as? Data {
            return data
        }

        return nil
    }

    // MARK: - Monitoring & Maintenance

    /// ⏰ Setup automatic token refresh
    private func setupTokenRefresh() {
        Timer.publish(every: 3600, on: .main, in: .common) // Every hour
            .autoconnect()
            .sink { [weak self] _ in
                Task { [weak self] in
                    await self?.refreshSubscriptionStatus()
                }
            }
            .store(in: &cancellables)
    }

    /// 🎁 Setup trial monitoring
    private func setupTrialMonitoring() {
        Timer.publish(every: 86400, on: .main, in: .common) // Daily
            .autoconnect()
            .sink { [weak self] _ in
                Task { [weak self] in
                    await self?.checkTrialExpiration()
                }
            }
            .store(in: &cancellables)
    }

    /// 🏥 DEFENSIVE JWT: Setup Token Health Monitoring
    ///
    /// Initializes proactive token health monitoring system.
    /// Part of DEFENSIVE JWT Architecture for automatic token management.
    ///
    private func setupTokenHealthMonitoring() {
        logger.business("🏥 DEFENSIVE JWT: Setting up proactive token health monitoring")

        // Start monitoring via singleton - it will automatically begin health checks
        TokenHealthMonitor.shared.startMonitoring()

        logger.business("✅ DEFENSIVE JWT: Proactive token health monitoring is now ACTIVE")
    }

    /// 📅 Setup monthly usage reset
    private func setupMonthlyReset() {
        Timer.publish(every: 86400, on: .main, in: .common) // Daily check
            .autoconnect()
            .sink { [weak self] _ in
                Task { [weak self] in
                    await self?.checkMonthlyReset()
                }
            }
            .store(in: &cancellables)
    }

    /// ⏰ Check trial expiration
    private func checkTrialExpiration() async {
        guard let trial = trialStatus, !trial.isActive else { return }

        logger.business("🎁 Trial expired - switching to free tier")

        // ❌ Cancel trial notifications since trial is over
        NotificationManager.shared.cancelTrialNotifications()

        trialStatus = nil

        // 🔬 DIAGNOSTICS: Testing in sync context with helper method
        #if DEBUG
        logger.business("🔬 DIAGNOSTICS: Testing SubscriptionStatus creation in sync context")

        let testSyncSubscription = createSubscriptionStatus(
            level: .premium,  // Test with enum value
            isActive: true,
            expiresAt: Date(),  // Test with Date
            trialInfo: nil,
            limits: SubscriptionLimits.freeLimits,
            components: ["test"]
        )
        logger.business("✅ DIAGNOSTICS: SubscriptionStatus created successfully in sync context")
        #endif

        // Switch to free subscription
        let freeSubscription = SubscriptionStatus(
            level: .free,
            isActive: true,
            expiresAt: nil,
            trialInfo: nil,
            limits: SubscriptionLimits.freeLimits,
            components: [],
            lastUpdated: Date()
        )

        await updateSubscriptionStatus(freeSubscription)
    }

    /// 📅 Check monthly reset
    private func checkMonthlyReset() async {
        guard var subscription = currentSubscription else { return }

        let calendar = Calendar.current
        let now = Date()
        let currentMonth = calendar.component(.month, from: now)

        // Check if it's a new month
        let lastResetMonth = UserDefaults.standard.integer(forKey: "last_usage_reset_month")
        if currentMonth != lastResetMonth {
            subscription.limits.currentUsage.resetMonthlyCounters()
            await updateSubscriptionStatus(subscription)

            UserDefaults.standard.set(currentMonth, forKey: "last_usage_reset_month")
            logger.business("📅 Monthly usage counters reset")
        }
    }

    // MARK: - Utility

    /// 🔧 Decode base64 URL string
    private func decodeBase64(_ base64Url: String) -> Data? {
        var base64 = base64Url
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")

        // Add padding if needed
        while base64.count % 4 != 0 {
            base64 += "="
        }

        return Data(base64Encoded: base64)
    }
}

// MARK: - Helper Extensions

// ✅ УДАЛЕНО: extension SubscriptionLimits с freeLimits и trialLimits
// Эти свойства уже определены в SubscriptionModels.swift
// Используем их оттуда, чтобы избежать дублирования

// MARK: - API Request Models

// ✅ УДАЛЕНО: private struct JWTPayload больше не используется
// Теперь используется JWTPayload из APIModels.swift напрямую
// Это предотвращает конфликт имен и использует правильную структуру JWT от сервера

// MARK: - Network Monitoring & Offline Support

extension SubscriptionManager {

    /// 🌐 Setup network connectivity monitoring
    private func setupNetworkMonitoring() {
        // Monitor network changes and sync when online
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(networkStatusChanged),
            name: NSNotification.Name("NetworkStatusChanged"),
            object: nil
        )

        // Setup periodic sync when online
        setupPeriodicSync()
    }

    /// 🌐 Network status changed notification handler
    @objc private func networkStatusChanged() {
        Task { @MainActor in
            let wasOffline = isOfflineMode
            updateOfflineStatus()

            // If came back online, sync subscription data
            if wasOffline && !isOfflineMode {
                trackEvent(.offlineMode, metadata: ["back_online": "true"])
                await syncWithServer()
            } else if !wasOffline && isOfflineMode {
                trackEvent(.offlineMode, metadata: ["went_offline": "true"])
            }
        }
    }

    /// 🌐 Update offline status based on network connectivity
    private func updateOfflineStatus() {
        // Simple connectivity check - in production use proper network monitoring
        isOfflineMode = false // Assume online for now, implement proper check
    }

    /// 🔄 Sync subscription data with server when online
    func syncWithServer() async {
        guard !isOfflineMode else {
            logger.network("📡 Skipping sync - offline mode")
            return
        }

        logger.network("📡 Starting subscription sync with server")

        do {
            // Get current token for explicit authorization
            guard let token = currentToken?.token else {
                logger.error("❌ Sync failed: No token available")
                return
            }

            // Get current subscription status summary from server with explicit token
            let serverSummary: SubscriptionStatusSummaryResponse = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatusWithToken(userId: "current", token: token) { result in
                    switch result {
                    case .success(let summary):
                        continuation.resume(returning: summary)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }

            // Convert summary to SubscriptionStatus using current subscription data
            let serverStatus = serverSummary.toSubscriptionStatus(currentSubscription: currentSubscription)

            // Update local data if server has newer information
            if shouldUpdateFromServer(serverStatus) {
                await updateFromServerStatus(serverStatus)
                logger.network("✅ Subscription synced with server")
            } else {
                logger.network("📡 Local data is up to date")
            }

            lastSyncDate = Date()
            trackEvent(.syncCompleted)

        } catch {
            logger.error("❌ Failed to sync with server: \(error.localizedDescription)")
            trackEvent(.syncFailed, errorMessage: error.localizedDescription)
            // Continue with cached data - graceful degradation
        }
    }

    /// 🔍 Check if server data is newer than local
    private func shouldUpdateFromServer(_ serverStatus: SubscriptionStatus) -> Bool {
        guard let localSubscription = currentSubscription else { return true }

        // Compare subscription levels and expiration dates
        return serverStatus.level != localSubscription.level ||
               serverStatus.expiresAt != localSubscription.expiresAt
    }

    /// 📥 Update local subscription from server data
    private func updateFromServerStatus(_ serverStatus: SubscriptionStatus) async {
        // Convert server response to local model
        let subscriptionLevel = serverStatus.level

        // 🔬 DIAGNOSTICS: Testing in another sync context (updateFromServerStatus)
        #if DEBUG
        logger.business("🔬 DIAGNOSTICS: Testing SubscriptionStatus creation in updateFromServerStatus")

        do {
            let testServerSubscription = SubscriptionStatus(
                level: subscriptionLevel,  // From server
                isActive: serverStatus.isActive,  // From server
                expiresAt: serverStatus.expiresAt,  // Date? from server
                trialInfo: serverStatus.trialInfo,  // From server
                limits: serverStatus.limits,  // From server
                components: serverStatus.components,  // From server
                lastUpdated: Date()
            )
            logger.business("✅ DIAGNOSTICS: SubscriptionStatus created successfully in updateFromServerStatus")
        } catch {
            logger.business("❌ DIAGNOSTICS: Failed to create SubscriptionStatus in updateFromServerStatus: \(error)")
        }
        #endif

        let subscriptionStatus = SubscriptionStatus(
            level: subscriptionLevel,
            isActive: serverStatus.isActive,
            expiresAt: serverStatus.expiresAt,
            trialInfo: serverStatus.trialInfo,
            limits: serverStatus.limits,
            components: serverStatus.components,
            lastUpdated: Date()
        )

        // Update local state
        currentSubscription = subscriptionStatus
        trialStatus = serverStatus.trialInfo

        // Persist updated data
        persistSubscriptionStatus(subscriptionStatus)
        if let trial = serverStatus.trialInfo {
            persistTrialStatus(trial)
        }

        logger.business("📥 Updated subscription from server: \(subscriptionLevel.rawValue)")
    }

    /// ⏰ Setup periodic sync when online
    private func setupPeriodicSync() {
        Task {
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 300_000_000_000) // 5 minutes

                if !isOfflineMode {
                    await syncWithServer()
                    await flushPendingEvents() // Send pending events
                }
            }
        }
    }

    /// 🔄 Force sync now (for manual refresh)
    func forceSync() async {
        await syncWithServer()
        await flushPendingEvents()
    }

    /// 📊 Get offline status info for UI
    func getOfflineStatusInfo() -> (isOffline: Bool, lastSync: String) {
        let lastSyncText = lastSyncDate.map { date in
            let formatter = RelativeDateTimeFormatter()
            // ✅ BUILD 98: Используем статический locale вместо Locale.current для предотвращения рекурсии
            formatter.locale = Locale(identifier: "ru_RU")
            return formatter.localizedString(for: date, relativeTo: Date())
        } ?? "Never"

        return (isOffline: isOfflineMode, lastSync: lastSyncText)
    }

    // MARK: - Events Tracking

    /// 📊 Track subscription event
    func trackEvent(
        _ event: SubscriptionEvent,
        userId: String? = nil,
        subscriptionLevel: String? = nil,
        featureId: String? = nil,
        resourceType: String? = nil,
        amount: Int? = nil,
        transactionId: String? = nil,
        errorMessage: String? = nil,
        metadata: [String: String]? = nil
    ) {
        let eventData = SubscriptionEventData(
            event: event,
            userId: userId ?? currentToken?.deviceId,
            subscriptionLevel: subscriptionLevel ?? currentSubscription?.level.rawValue,
            featureId: featureId,
            resourceType: resourceType,
            amount: amount,
            transactionId: transactionId,
            errorMessage: errorMessage,
            metadata: metadata
        )

        eventsQueue.sync {
            pendingEvents.append(eventData)

            // Limit queue size to prevent memory issues
            if pendingEvents.count > 1000 {
                pendingEvents.removeFirst(100)
            }

            // Send immediately if online
            if !self.isOfflineMode {
                Task {
                    await self.flushPendingEvents()
                }
            }
        }

        logger.business("📊 Event tracked: \(event.rawValue)")
    }

    /// 📤 Send pending events to server
    @MainActor private func flushPendingEvents() async {
        guard !pendingEvents.isEmpty else { return }

        let eventsToSend = pendingEvents
        pendingEvents.removeAll()

        // TODO: Implement sendSubscriptionEvents in APIService
        logger.business("📤 Would send \(eventsToSend.count) subscription events to server (not implemented)")

        // Re-queue events for now
        pendingEvents.insert(contentsOf: eventsToSend, at: 0)
    }

    // MARK: - Error Handling

    /// 🔍 Получить понятное сообщение об ошибке для пользователя
    private func getUserFriendlyErrorMessage(for error: Error) -> String {
        switch error {
        case let networkError as NetworkError:
            switch networkError {
            case .httpError(401):
                return "Требуется авторизация. Проверьте подключение к интернету и попробуйте снова."
            case .httpError(403):
                return "Доступ запрещен. Возможно, истек срок действия подписки."
            case .httpError(404):
                return "Сервис временно недоступен. Попробуйте позже."
            case .httpError(500):
                return "Внутренняя ошибка сервера. Попробуйте через несколько минут."
            case .noConnection:
                return "Нет подключения к интернету. Проверьте соединение и попробуйте снова."
            case .timeout:
                return "Превышено время ожидания. Проверьте интернет-соединение."
            case .serverUnavailable:
                return "Сервер временно недоступен. Попробуйте позже."
            default:
                return "Произошла сетевая ошибка. Попробуйте позже."
            }

        case let subscriptionError as SubscriptionError:
            switch subscriptionError {
            case .tokenExpired:
                return "Срок действия токена истек. Обновляем авторизацию..."
            case .invalidToken:
                return "Неверный токен авторизации. Повторная регистрация устройства..."
            case .networkError:
                return "Ошибка сети. Проверьте подключение к интернету."
            case .serverError(let message):
                return "Ошибка сервера: \(message). Попробуйте позже."
            case .limitExceeded(let resource):
                return "Превышен лимит использования для \(resource.rawValue). Обновите подписку."
            case .trialExpired:
                return "Пробный период истек. Перейдите на платную подписку."
            case .subscriptionExpired:
                return "Подписка истекла. Продлите подписку для продолжения использования."
            case .unauthorized:
                return "Нет авторизации. Пожалуйста, войдите в систему."
            }

        default:
            return "Произошла неожиданная ошибка. Попробуйте позже."
        }
    }

    /// 🚨 Показать ошибку пользователю
    private func showUserError(message: String) {
        // Логируем ошибку для пользователя
        logger.business("🚨 Ошибка авторизации: \(message)")

        // Также обновляем lastError для UI компонентов
        lastError = .serverError(message)

        // TODO: В будущем заменить на ErrorMessageManager для показа UI
        print("🚨 ПОЛЬЗОВАТЕЛЬСКАЯ ОШИБКА: \(message)")
    }

    /// 🔄 Специальная обработка ошибки 401 Unauthorized с retry-механизмом
    private func handle401Error() async {
        logger.business("🔄 Обработка ошибки 401 - запуск retry-механизма")

        // Очищаем текущий токен
        await clearToken()

        // Показываем сообщение пользователю
        showUserError(message: "Авторизация истекла. Восстановление доступа...")

        // Запускаем retry-механизм
        let success = await retryDeviceRegistration(maxAttempts: 3)

        if success {
            logger.business("✅ Авторизация успешно восстановлена после 401")

            // Показываем успех
            logger.business("✅ Авторизация успешно восстановлена - все функции доступны")
            print("✅ УСПЕХ: Авторизация обновлена, устройство зарегистрировано")

        } else {
            logger.error("❌ Все попытки восстановления авторизации провалились")

            // Показываем критическую ошибку
            showUserError(message: "Не удалось восстановить авторизацию. Проверьте интернет-соединение или перезапустите приложение.")

            // Переходим в оффлайн режим
            isOfflineMode = true
            trackEvent(.offlineMode, metadata: ["reason": "auth_retry_failed"])
        }
    }

    /// 🔁 Retry-механизм для регистрации устройства
    /// - Parameter maxAttempts: Максимальное количество попыток
    /// - Returns: true если регистрация удалась
    private func retryDeviceRegistration(maxAttempts: Int) async -> Bool {
        for attempt in 1...maxAttempts {
            logger.business("🔄 Попытка \(attempt)/\(maxAttempts) регистрации устройства")

            do {
                try await registerDeviceAnonymously()
                logger.business("✅ Регистрация удалась на попытке \(attempt)")
                return true

            } catch {
                logger.error("❌ Попытка \(attempt) провалилась: \(error.localizedDescription)")

                // Если это не последняя попытка, ждем перед следующей
                if attempt < maxAttempts {
                    let delaySeconds = Double(attempt) * 2.0 // 2, 4, 6 секунд
                    logger.business("⏳ Ждем \(delaySeconds) секунд перед следующей попыткой")

                    // Показываем прогресс пользователю
                    logger.business("⏳ Восстановление доступа: попытка \(attempt)/\(maxAttempts), ожидание \(Int(delaySeconds)) сек")
                    print("⏳ ПРОГРЕСС: Попытка \(attempt)/\(maxAttempts) регистрации")

                    try? await Task.sleep(nanoseconds: UInt64(delaySeconds * 1_000_000_000))

                    // Проверяем, не отменена ли задача
                    if Task.isCancelled {
                        logger.business("🚫 Retry-механизм отменен")
                        return false
                    }
                }
            }
        }

        logger.error("❌ Все \(maxAttempts) попыток регистрации провалились")
        return false
    }


    /// 🔍 Комплексная валидация JWT токена
    private func validateJWTToken(_ token: String) -> JWTValidationResult {
        logger.business("🔍 Начинаем валидацию JWT токена")

        // 1. Базовая проверка формата
        if token.isEmpty {
            logger.error("❌ Токен пустой")
            return .invalid("Пустой токен")
        }

        if !token.contains(".") {
            logger.error("❌ Токен не содержит разделителей '.'")
            return .invalid("Неверный формат JWT")
        }

        let parts = token.split(separator: ".")
        if parts.count != 3 {
            logger.error("❌ Токен должен содержать 3 части, получено: \(parts.count)")
            return .invalid("Неверное количество частей в JWT")
        }

        // 2. Проверка base64 формата каждой части
        for (index, part) in parts.enumerated() {
            if let decodedData = Data(base64URLEncoded: String(part)) {
                logger.business("✅ Часть \(index + 1): валидный base64, длина: \(decodedData.count) байт")
            } else {
                logger.error("❌ Часть \(index + 1): невалидный base64")
                return .invalid("Невалидный base64 в части \(index + 1)")
            }
        }

        // 3. Попытка декодировать header
        if let headerData = Data(base64URLEncoded: String(parts[0])),
           let headerString = String(data: headerData, encoding: .utf8) {
            logger.business("📋 JWT Header: \(headerString)")

            // Проверка типа токена
            if !headerString.contains("\"alg\"") {
                logger.error("❌ JWT header не содержит алгоритм")
                return .invalid("Отсутствует алгоритм в header")
            }

            if !headerString.contains("\"typ\":\"JWT\"") {
                logger.error("❌ Токен не является JWT")
                return .invalid("Неверный тип токена")
            }
        }

        // 4. Попытка декодировать payload (без верификации подписи)
        if let payloadData = Data(base64URLEncoded: String(parts[1])),
           let payloadString = String(data: payloadData, encoding: .utf8) {
            logger.business("📋 JWT Payload (первые 200 символов): \(payloadString.prefix(200))")

            // ✅ BUILD 121: Проверка обязательных полей (согласно реальной структуре JWT от сервера)
            // Сервер отправляет: {"sub":"anonymous","device_id":"...","subscription":{"level":"free",...},"exp":...,"iat":...}
            // НЕТ поля subscription_level на верхнем уровне - оно внутри subscription.level
            
            // Проверка обязательных полей верхнего уровня
            let requiredTopLevelFields = ["sub", "exp", "iat"]
            for field in requiredTopLevelFields {
                if !payloadString.contains("\"\(field)\"") {
                    logger.error("❌ JWT payload не содержит обязательное поле: \(field)")
                    return .invalid("Отсутствует обязательное поле: \(field)")
                }
            }

            // ✅ BUILD 121: Проверка subscription объекта (вложенная структура)
            if !payloadString.contains("\"subscription\"") {
                logger.error("❌ JWT payload не содержит объект 'subscription'")
                return .invalid("Отсутствует объект subscription")
            }
            
            // Проверка subscription.level внутри subscription объекта
            if !payloadString.contains("\"subscription\":{") || !payloadString.contains("\"level\"") {
                logger.error("❌ JWT payload не содержит subscription.level")
                return .invalid("Отсутствует subscription.level")
            }

            // Дополнительная проверка: deviceId должен быть в поле "sub" или "device_id"
            if !payloadString.contains("\"sub\":") && !payloadString.contains("\"device_id\"") {
                logger.error("❌ JWT payload не содержит deviceId в поле 'sub' или 'device_id'")
                return .invalid("Отсутствует deviceId")
            }

            // ✅ BUILD 121: Проверка срока действия с детальным логированием
            if let expTimestamp = extractTimestamp(from: payloadString, field: "exp") {
                let expirationDate = Date(timeIntervalSince1970: TimeInterval(expTimestamp))
                let now = Date()
                
                // ✅ BUILD 121: Детальное логирование для диагностики
                logger.business("🔍 DEFENSIVE JWT: Детальная проверка exp:")
                logger.business("   - exp timestamp: \(expTimestamp)")
                logger.business("   - expirationDate: \(expirationDate)")
                logger.business("   - currentDate: \(now)")
                logger.business("   - timeDifference: \(expirationDate.timeIntervalSince(now)) секунд")
                logger.business("   - timeDifference: \(Int(expirationDate.timeIntervalSince(now) / 3600)) часов")

                if expirationDate <= now {
                    logger.error("❌ Токен уже истек: \(expirationDate)")
                    logger.error("   - Истёк \(Int(abs(expirationDate.timeIntervalSince(now) / 3600))) часов назад")
                    return .invalid("Токен истек")
                }

                let hoursUntilExpiration = Int(expirationDate.timeIntervalSince(now) / 3600)
                let minutesUntilExpiration = Int((expirationDate.timeIntervalSince(now).truncatingRemainder(dividingBy: 3600)) / 60)
                logger.business("⏰ Токен истекает через \(hoursUntilExpiration) часов \(minutesUntilExpiration) минут")
                
                // ✅ BUILD 121: Предупреждение если токен истекает скоро (менее 1 часа)
                if hoursUntilExpiration < 1 {
                    logger.business("⚠️ DEFENSIVE JWT: Токен истекает очень скоро (\(minutesUntilExpiration) минут) - требуется обновление")
                }
            } else {
                logger.business("⚠️ DEFENSIVE JWT: Не удалось извлечь exp из JWT payload")
            }
        }

        // 5. Проверка подписи (базовая)
        let signature = String(parts[2])
        if signature.isEmpty {
            logger.error("❌ Пустая подпись токена")
            return .invalid("Пустая подпись")
        }

        logger.business("✅ JWT токен прошел все проверки валидации")
        return .valid
    }

    /// 🛠️ Извлечение timestamp из JWT payload
    private func extractTimestamp(from payload: String, field: String) -> Int? {
        // Простой парсер JSON для извлечения timestamp
        let pattern = "\"\(field)\":\\s*(\\d+)"
        if let regex = try? NSRegularExpression(pattern: pattern, options: []),
           let match = regex.firstMatch(in: payload, options: [], range: NSRange(payload.startIndex..., in: payload)),
           let range = Range(match.range(at: 1), in: payload) {
            return Int(payload[range])
        }
        return nil
    }
}

/// 📋 Результат валидации JWT токена
private enum JWTValidationResult {
    case valid
    case invalid(String)
}

// MARK: - Data Extensions

extension Data {
    /// Инициализация Data из base64url-encoded строки (без padding)
    init?(base64URLEncoded base64String: String) {
        // Заменяем URL-safe символы на стандартные
        var base64 = base64String
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")

        // Добавляем padding если необходимо
        let paddingLength = (4 - (base64.count % 4)) % 4
        base64 += String(repeating: "=", count: paddingLength)

        self.init(base64Encoded: base64)
    }
}
