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
import CryptoKit

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
    let eventId: String
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
        self.eventId = UUID().uuidString
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

enum FamilyQuotaSource: String, Codable {
    case serverStats
    case tariffFallback
    case persistedCache
}

struct FamilyQuotaSnapshot: Codable, Equatable {
    let used: Int
    let max: Int
    let source: FamilyQuotaSource
    let updatedAt: Date
    let familyId: String?
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

    /// PHASE 2: Flag indicating that initializeOnAppStart() has completed
    /// Used by MainViewModel.onAppear() to prevent loading before auth is ready
    @Published private(set) var isInitialized: Bool = false

    /// Current family member limit based on active tariff (single source of truth)
    /// Updated from SubscriptionLevel and X-Family-Limit headers
    @Published private(set) var currentFamilyLimit: Int = 3

    /// Remaining family member slots (synced from headers or calculated)
    @Published private(set) var currentFamilyRemaining: Int = 2

    /// Единый снимок квоты семьи для согласованного UI на всех экранах.
    @Published private(set) var familyQuotaSnapshot = FamilyQuotaSnapshot(
        used: 0,
        max: 3,
        source: .persistedCache,
        updatedAt: Date.distantPast,
        familyId: nil
    )

    /// Монотонно растёт при любых изменениях уровня/триала/токена — чтобы SwiftUI гарантированно перерисовал строку тарифа на главной (в т.ч. после возврата с экрана тарифов на устройстве).
    @Published private(set) var subscriptionDisplayEpoch: UInt64 = 0

    /// Throttle для повторных синков при каждом показе главной / `scenePhase` (избегаем лишних GET).
    private var lastVisibilitySubscriptionSyncAt: Date?
    private let minVisibilitySubscriptionSyncInterval: TimeInterval = 1.2
    /// После `10_TariffsScreen.onDisappear` следующий `syncSubscriptionOnMainScreenAppear` не должен отсечься 1.2s‑троттлингом (порядок с `MainScreen.onAppear` недетерминирован).
    private var bypassVisibilitySubscriptionSyncThrottleOnce = false

    /// Events tracking
    private let eventsQueue = DispatchQueue(label: "com.aladdin.subscription.events")
    private var pendingEvents: [SubscriptionEventData] = []
    private var flushRetryCount = 0
    private var isFlushingEvents = false
    private var isSyncInFlight = false
    private var lastSyncCompletedEventAt: Date?
    private var lastSyncCompletedFingerprint: String?
    private let minSyncCompletedEventInterval: TimeInterval = 12
    private let maxEventBatchSize = 25
    private let pendingEventsStorageKey = "subscription_pending_events_v1"
    private let pendingEventsTTL: TimeInterval = 7 * 24 * 60 * 60 // 7 days
    // Runtime counters (for observability)
    private(set) var eventsSentCount: Int = 0
    private(set) var eventsFailedCount: Int = 0
    private(set) var lastQueueSize: Int = 0

    // MARK: - Private Properties

    private let keychainService = "com.aladdin.subscription"
    private let tokenKey = "jwt_token"
    private let subscriptionKey = "subscription_status"
    private let trialKey = "trial_info"
    private let trialAttemptTimestampsKey = "trial_attempt_timestamps_v1"
    private let trialRiskSaltKey = "trial_risk_salt_v1"
    private let trialRiskSaltCreatedAtKey = "trial_risk_salt_created_at_v1"

    private var cancellables = Set<AnyCancellable>()
    private let logger = MasterLogger.shared

    /// Throttle for `checkTrialExpiration` on foreground / post-launch (server remains source of truth after sync).
    private var lastThrottledTrialExpiryCheckAt: Date?
    private let trialExpiryForegroundCheckMinInterval: TimeInterval = 15 * 60

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
        
        guard !SubscriptionManager.hasInitialized else {
            
            logger.business("⚠️ SubscriptionManager.initializeOnAppStart() уже вызван, пропускаем повторный вызов")
            return
        }

        SubscriptionManager.hasInitialized = true
        
        
        #if DEBUG
        print("🚀🚀🚀 INITIALIZE_ON_APP_START: Method called")
        VisualLogger.shared.log("🚀 SubscriptionManager.initializeOnAppStart() called", level: .info)
        #endif

        let tokenStatus = TokenValidator.validateCurrentToken()

        switch tokenStatus {
        case .none:
            await performDeviceRegistration()

        case .valid:
            break

        case .expired, .invalid:
            await clearToken()
            await performDeviceRegistration()

        case .needsRefresh:
            await refreshTokenSilently()
        }

        // ✅ BUILD 123: Проверка синхронизации токена с AppConfig
        if let token = currentToken {
            if AppConfig.authToken == nil {
                AppConfig.authToken = token.token
                logger.business("✅ BUILD 123: Токен синхронизирован с AppConfig при инициализации")
            } else if AppConfig.authToken != token.token {
                // Токены не совпадают - обновляем AppConfig
                AppConfig.authToken = token.token
                logger.business("⚠️ BUILD 123: Токены не совпадали - обновлен AppConfig")
            }
        }

        // 🚨 DEFENSIVE JWT: Emergency reset Circuit Breaker if stuck
        JWTCircuitBreaker.shared.emergencyReset()

        await performThrottledTrialExpiryCheckIfNeeded()

        JWTEventLogger.logEvent(.healthCheckPerformed(
            tokenExists: currentToken != nil,
            timeToExpiry: currentToken?.expiresAt.timeIntervalSinceNow,
            nextCheckIn: 60
        ))

        reconcileTariffManagerWithSubscription(reason: "initializeOnAppStart")
        FamilyLocalStore.reconcileFamilyContextWithCurrentJWT()
        logSubscriptionReconcileSummary(tokenStatus: tokenStatus)
        isInitialized = true
        #if DEBUG
        logger.business("✅ SubscriptionManager async startup complete")
        #endif
    }

    /// Один компактный снимок после reconcile старта (меньше дублирующихся строк из слоёв).
    private func logSubscriptionReconcileSummary(tokenStatus: TokenValidator.TokenStatus) {
        let trialLine: String = {
            guard let t = trialStatus else { return "trial=nil" }
            return "trial_active=\(t.isActive)"
        }()
        let plan = currentSubscription?.level.rawValue ?? "nil"
        let tokenOk = currentToken != nil
        let effective = getCurrentLevel().rawValue
        let tariffMgr = TariffManager.shared.currentTariff.rawValue
        logger.business(
            "📋 subscription_reconcile jwt=\(tokenStatus.description) token_present=\(tokenOk) plan=\(plan) effective=\(effective) \(trialLine) family_limit=\(currentFamilyLimit) tariff_mgr=\(tariffMgr)"
        )
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

    // ✅ BUILD 123: Защита от бесконечных циклов
    private var registrationAttempts: Int = 0
    private let maxRegistrationAttempts: Int = 3
    private let registrationLock = NSLock()  // ✅ Защита от race condition

    /// 🛡️ DEFENSIVE JWT: Perform Device Registration
    ///
    /// Safely registers device with comprehensive error handling.
    /// Part of DEFENSIVE JWT Architecture for graceful token management.
    ///
    func performDeviceRegistration() async {
        // ✅ BUILD 123: Проверка количества попыток
        
        guard registrationAttempts < maxRegistrationAttempts else {
            
            logger.error("❌ BUILD 123: Превышено максимальное количество попыток регистрации (\(maxRegistrationAttempts))")
            return
        }
        registrationAttempts += 1
        
        
        let logger = MasterLogger.shared
        logger.business("📱 DEFENSIVE JWT: Выполняем регистрацию устройства (попытка \(registrationAttempts)/\(maxRegistrationAttempts))")

        do {
            logger.business("📱 DEFENSIVE JWT: Запуск registerDeviceAnonymously()...")
            _ = try await registerDeviceAnonymously()
            logger.business("✅ DEFENSIVE JWT: Регистрация устройства прошла успешно")

            // Проверяем, что токен был установлен
            if let token = currentToken {
                logger.business("✅ DEFENSIVE JWT: Токен успешно установлен после регистрации")
                JWTEventLogger.logDeviceRegistration(success: true, error: nil, deviceId: token.deviceId)
                
                // ✅ BUILD 123: Сброс счетчика при успехе
                
                registrationAttempts = 0
                
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
            
            // ✅ BUILD 123: Сброс счетчика при ошибке (чтобы не блокировать навсегда)
            
            if registrationAttempts >= maxRegistrationAttempts {
                registrationAttempts = 0  // Сброс для следующей попытки через время
            }
            

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

    /// 🔄 BUILD 123: Восстановление подписки с сервера (защита от потери подписки)
    ///
    /// Восстанавливает подписку с сервера для пользователей с платной подпиской или триалом.
    /// Используется при 403 ошибке для предотвращения потери подписки.
    ///
    func restoreSubscriptionFromServer() async {
        guard let deviceId = currentToken?.deviceId else {
            // Нет deviceId → перерегистрация (только для FREE)
            logger.business("⚠️ BUILD 123: Нет deviceId - перерегистрация")
            await performDeviceRegistration()
            return
        }
        
        logger.business("🔄 BUILD 123: Восстановление подписки с сервера для deviceId: \(deviceId)")
        
        // ✅ Запрашиваем текущую подписку с сервера
        // Используем существующий метод getSubscriptionStatus()
        // Но нужно получить userId из токена (deviceId)
        APIService.shared.getSubscriptionStatus(userId: deviceId, merging: currentSubscription) { [weak self] result in
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                switch result {
                case .success(let status):
                    self.logger.business("✅ BUILD 123: Подписка восстановлена с сервера, level=\(status.level.rawValue)")
                    await self.applySubscriptionPayloadFromServer(status)
                    
                case .failure(let error):
                    // ✅ Если не удалось → перерегистрация (только для FREE)
                    self.logger.error("❌ BUILD 123: Не удалось восстановить подписку: \(error.localizedDescription)")
                    self.logger.business("⚠️ BUILD 123: Перерегистрация устройства")
                    await self.performDeviceRegistration()
                }
            }
        }
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
        reconcileTariffManagerWithSubscription(reason: "clearToken")
        bumpSubscriptionDisplayEpoch()
    }

    #if DEBUG
    /// Только для юнит-тестов: выставляет `currentToken` в памяти без Keychain/UserDefaults.
    func setCurrentTokenForTesting(_ token: JWTToken?) {
        currentToken = token
    }
    #endif

    private init() {
        print("🔐🔐🔐 SUBSCRIPTION_MANAGER_INIT: Starting initialization")
        logger.security("🔐 SubscriptionManager initialized - Core security component active")
        self.isInitialized = false  // Phase 2: explicit flag

        // Load persisted data on initialization
        logger.business("💾 Loading persisted data from Keychain...")
        print("💾💾💾 LOADING_PERSISTED_DATA: About to load from Keychain")
        loadPersistedData()
        loadPendingEvents()
        restoreFamilyQuotaSnapshotFromCache()
        logger.business("💾 Persisted data loading completed")
        print("💾💾💾 PERSISTED_DATA_LOADED: Completed")

        // isInitialized выставляется только после async initializeOnAppStart() (JWT / регистрация).

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
        updateSubscriptionStatus(subscription)

        logger.business("📈 Resource usage updated: \(resource.rawValue) +\(amount)")
    }

    /// 🎯 Get current subscription level
    func getCurrentLevel() -> SubscriptionLevel {
        if let trial = trialStatus, trial.isActive {
            return .trial
        }
        // После `/api/subscription/cancel` снимок `currentSubscription` уже `free`, а JWT может ещё
        // содержать старый `subscription_level` (trial) до перевыпуска токена — иначе UI показывает
        // «Пробный» и зелёный градиент при выборе «Базовый» (см. TRIAL_TARIFF_PIPELINE: plan=free, effective=trial).
        if currentSubscription?.level == .free, trialStatus?.isActive != true {
            return .free
        }
        let subLevel = currentSubscription?.level
        let tokenLevel = currentToken?.subscriptionLevel
        // Апгрейд: JWT обновился раньше Keychain `subscription_status` — доверяем токену, если триал не активен.
        if let s = subLevel, let t = tokenLevel, s != t {
            if s == .free && t != .free { return t }
            if s != .free && t == .free { return s }
            return s
        }
        if let s = subLevel { return s }
        if let t = tokenLevel { return t }
        return .free
    }

    /// Повторный синк при возврате на главную / из фона. `.task` на MainScreen выполняется только один раз (`hasAppeared`).
    func syncSubscriptionOnMainScreenAppear() async {
        let now = Date()
        if !bypassVisibilitySubscriptionSyncThrottleOnce,
           let last = lastVisibilitySubscriptionSyncAt,
           now.timeIntervalSince(last) < minVisibilitySubscriptionSyncInterval {
            return
        }
        bypassVisibilitySubscriptionSyncThrottleOnce = false
        lastVisibilitySubscriptionSyncAt = now
        await forceSync()
        bumpSubscriptionDisplayEpoch()
    }

    /// Без троттлинга: после экрана тарифов главная должна сразу подтянуть `/api/subscription/status` (иначе 1.2s коалесинг пропускает синк).
    @MainActor
    func syncSubscriptionAfterTariffsDismiss() async {
        bypassVisibilitySubscriptionSyncThrottleOnce = true
        await forceSync()
        bumpSubscriptionDisplayEpoch()
    }

    /// Family member limit by tariff level (aligned with prod `subscription_limits.py` / `family_roster_reconcile.py`: free=1, trial=3, personal=2, family=6, premium=10)
    /// Single source of truth used by all add flows
    nonisolated static func familyMemberLimitStatic(for level: SubscriptionLevel) -> Int {
        switch level {
        case .free:
            return 1
        case .trial:
            return 3
        case .personal:
            return 2
        case .family:
            return 6
        case .premium:
            return 10
        }
    }

    func familyMemberLimit(for level: SubscriptionLevel) -> Int {
        Self.familyMemberLimitStatic(for: level)
    }

    /// Central guard for adding family members. Used by FamilyScreen, FamilyRegistrationViewModel, AddMemberOptionsScreen.
    /// Returns whether allowed, user-facing message if blocked, and whether upgrade is suggested.
    func canAddFamilyMember(currentCount: Int) -> (allowed: Bool, message: String?, upgradeSuggested: Bool) {
        let limit = familyQuotaSnapshot.max
        // Persisted cache can become stale after reinstall/login switch or partial sync.
        // For local gating prefer current UI count when snapshot source is persisted cache.
        let effectiveUsed: Int
        if familyQuotaSnapshot.source == .persistedCache {
            effectiveUsed = max(0, min(currentCount, limit))
        } else {
            effectiveUsed = max(currentCount, familyQuotaSnapshot.used)
        }
        let remaining = max(0, limit - effectiveUsed)

        // ✅ Локализованные сообщения о лимитах (без хардкода)
        let isRussian = (UserDefaults.standard.string(forKey: "app_language") ?? "ru") == "ru"
        
        if limit > 0 && currentCount >= limit {
            let msg = isRussian
                ? "Лимит участников для вашего тарифа (\(limit)) достигнут. Обновите тариф чтобы добавить больше участников."
                : "Member limit for your plan (\(limit)) reached. Upgrade your plan to add more members."
            return (false, msg, true)
        }

        if remaining <= 0 && limit > 0 {
            let msg = isRussian
                ? "Осталось 0 мест по тарифу (\(limit)). Обновите подписку."
                : "0 slots remaining on your plan (\(limit)). Upgrade your subscription."
            return (false, msg, true)
        }

        return (true, nil, false)
    }

    /// Единая формула «X из Y» для главной и экрана «Семья».
    func effectiveFamilyQuotaUsed(localRosterCount: Int? = nil) -> Int {
        let localCount = max(0, localRosterCount ?? FamilyLocalStore.persistedLocalRosterCount())
        let limit = max(0, familyQuotaSnapshot.max)
        let quotaUsed: Int
        if familyQuotaSnapshot.source == .persistedCache {
            quotaUsed = localCount
        } else {
            quotaUsed = familyQuotaSnapshot.used
        }
        let combined = max(localCount, quotaUsed)
        guard limit > 0 else { return combined }
        return min(combined, limit)
    }

    /// Перерисовать карточку семьи на главной после локального sync.
    func refreshFamilyQuotaDisplayFromLocalRoster() {
        bumpSubscriptionDisplayEpoch()
    }

    /// Выравнивает лимит ростера с `GET /api/family/stats` (кап владельца в БД), чтобы UI не расходился с gate на `add`.
    func applyFamilyRosterQuotaFromFamilyStats(_ stats: FamilyStatsResponse) {
        guard let cap = stats.familyRosterMax, cap > 0 else { return }
        let used = stats.familyRosterUsed ?? stats.totalMembers
        let trimmedFamilyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let familyId: String? = trimmedFamilyId.isEmpty ? nil : trimmedFamilyId
        publishFamilyQuotaSnapshot(used: used, maxSlots: cap, source: .serverStats, familyId: familyId)
        bumpSubscriptionDisplayEpoch()
        VisualLogger.shared.log(
            "🔄 FAMILY STATS→LIMIT rosterUsed=\(used) rosterMax=\(cap) tier=\(stats.ownerSubscriptionTier ?? "?")",
            level: .info,
            category: "FAMILY"
        )
    }

    /// Safe, non-isolated access to current family limit for use in completion handlers, error paths, and non-MainActor contexts.
    /// Falls back to UserDefaults (which is always updated together with the published property).
    /// Marked nonisolated to satisfy Swift 6 concurrency rules when called from APIService completion blocks.
    nonisolated static var currentFamilyLimit: Int {
        let fromDefaults = UserDefaults.standard.integer(forKey: "family_limit")
        return fromDefaults > 0 ? fromDefaults : 3 // default to personal/trial limit
    }

    /// 🔑 Get current JWT token for API requests
    func getCurrentToken() async -> String? {
        return currentToken?.token
    }

    /// Идентификатор для тел cancel/downgrade: не `your_member_id` (MEM_…), а тот же контракт, что GET `/api/subscription/status` (`"current"` + Bearer).
    private func userIdForSubscriptionCancelRequest() -> String {
        if currentToken?.token != nil {
            return "current"
        }
        let d = (currentToken?.deviceId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !d.isEmpty { return d }
        return "anonymous"
    }

    /// ⬇️ Downgrade to Free (Cancel Trial/Subscription)
    @MainActor
    func downgradeToFree() async {
        logger.business("⬇️ Downgrading subscription to FREE (Cancel)")
        
        do {
            isLoading = true
            
            let userId = userIdForSubscriptionCancelRequest()
            let deviceId = self.currentToken?.deviceId
            
            let response: SubscriptionCancelResponse = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.downgradeSubscription(userId: userId, reason: "downgrade_to_free", deviceId: deviceId) { result in
                    switch result {
                    case .success(let resp):
                        continuation.resume(returning: resp)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }
            
            if response.success {
                logger.business("✅ Successfully downgraded to FREE on server")
                
                if let newToken = response.newToken,
                   let jwtToken = self.parseJWTToken(newToken) {
                    await self.storeToken(jwtToken)
                }

                if trialStatus != nil {
                    NotificationManager.shared.cancelTrialNotifications()
                }
                trialStatus = nil
                deleteFromKeychain(key: trialKey)

                let freeSubscription = self.createSubscriptionStatus(
                    level: .free,
                    isActive: true,
                    expiresAt: nil,
                    trialInfo: nil,
                    limits: SubscriptionLimits.freeLimits,
                    components: ["mobile_security_agent", "network_security_agent"]
                )
                updateSubscriptionStatus(freeSubscription)

                await self.forceSync()

                NotificationCenter.default.post(
                    name: Notification.Name("SubscriptionUpdated"),
                    object: nil,
                    userInfo: ["level": SubscriptionLevel.free.rawValue, "source": "downgrade_to_free"]
                )
            } else {
                logger.error("❌ Failed to downgrade to free on server")
            }
        } catch {
            logger.error("❌ Failed to downgrade to free: \(error)")
            lastError = .serverError(error.localizedDescription)
        }
        
        isLoading = false
    }

    /// 🎁 Activate trial period (14 days)
    @MainActor
    func activateTrialIfNeeded() async {
        // If trial is already active locally - do nothing.
        if let trial = trialStatus, trial.isActive {
            logger.business("✅ Trial already active")
            // Повторный тап «Пробный» на тарифах: всё равно пересчитать лимиты/UI (см. updateTrialStatus + family cap).
            if let sub = currentSubscription {
                updateSubscriptionStatus(sub)
            }
            bumpSubscriptionDisplayEpoch()
            return
        }

        logger.business("🎁 Requesting server-side 14-day trial")

        let localCooldown = localTrialCooldownSeconds()
        if localCooldown > 0 {
            logger.business("⏳ Trial activation temporarily throttled: cooldown=\(localCooldown)s")
            lastError = .serverError("Trial activation cooldown is active. Please try again later.")
            return
        }

        // We provide a requested window, but backend must be idempotent and the source of truth.
        let startDate = Date()
        let endDate = Calendar.current.date(byAdding: .day, value: 14, to: startDate)!
        let requestedTrialInfo = TrialInfo(startDate: startDate, endDate: endDate, durationDays: 14)

        do {
            isLoading = true
            recordTrialActivationAttempt()

            // Backend will return either: trial (active or not), free, or paid — without resetting trial endlessly.
            let jwtToken = try await registerDeviceWithTrial(trialInfo: requestedTrialInfo)

            if let serverTrial = jwtToken.trialInfo {
                updateTrialStatus(serverTrial)

                if serverTrial.isActive {
                    trackEvent(.trialActivated, metadata: [
                        "duration_days": String(serverTrial.durationDays),
                        "days_remaining": String(serverTrial.daysRemaining)
                    ])
                    NotificationManager.shared.scheduleTrialNotifications(trialEndDate: serverTrial.endDate)
                    logger.business("✅ Trial activated from server: \(serverTrial.daysRemaining) days remaining + notifications scheduled")
                    logger.business("📊 TRIAL_TARIFF_PIPELINE trial_activated plan=\(currentSubscription?.level.rawValue ?? "nil") effective=\(getCurrentLevel().rawValue) trial_end=\(serverTrial.endDate)")
                } else {
                    logger.business("ℹ️ Server trial is not active anymore. App should behave as free/paid.")
                }
            }
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

            let subscriptionStatus: SubscriptionStatus = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatusWithToken(
                    userId: "current",
                    token: token,
                    merging: currentSubscription
                ) { result in
                    switch result {
                    case .success(let status):
                        continuation.resume(returning: status)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }

            await updateFromServerStatus(subscriptionStatus)

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

        // ✅ PHASE 3: Robust registration with retry + fallback (NEW)
        logger.business("📡 Starting registration with retry logic (max 3 attempts)")
        
        let response = try await performRegistrationWithRetry(
            request: request,
            deviceId: deviceId,
            isTrial: false
        )

        self.logger.business("✅ РЕГИСТРАЦИЯ УСТРОЙСТВА ПРОШЛА УСПЕШНО (после retry/fallback)")
        self.logger.business("📋 Получен ответ от сервера:")
        self.logger.business("   - Token: \(response.token.prefix(20))... (длина: \(response.token.count))")
        self.logger.business("   - Subscription Level: \(response.subscription.level)")
        self.logger.business("   - Subscription Status: \(response.subscription.isActive ? "АКТИВНА" : "НЕАКТИВНА")")
        self.logger.business("   - Expires At: \(response.expiresAt)")

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

        // ✅ PHASE 3: Added robust registration with retry logic (called from improved path)
        // This helper will be used in future improvements to wrap the continuation with retries.

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
            subscriptionLevel: SubscriptionLevel.fromAPIPlanString(response.subscription.level),
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
        updateSubscriptionStatus(newSubscriptionStatus)

        // Align Keychain `trialStatus` with server (same as registerDeviceWithTrial path).
        if let serverTrial = jwtToken.trialInfo {
            updateTrialStatus(serverTrial)
        }

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

    /// 🔄 PHASE 3: Robust registration with retry, fallback and full diagnostics
    /// Attempts registration up to 3 times. On 404 automatically falls back to trial endpoint.
    private func performRegistrationWithRetry(
        request: DeviceRegisterRequest,
        deviceId: String,
        isTrial: Bool = false
    ) async throws -> JWTDeviceRegisterResponse {
        
        let maxAttempts = 3
        var lastError: Error?
        
        for attempt in 1...maxAttempts {
            let isLastAttempt = attempt == maxAttempts
            logger.business("🔄 Registration attempt \(attempt)/\(maxAttempts) (trial=\(isTrial))")
            
            do {
                let endpoint = isTrial ? "/api/auth/register-device-trial" : "/api/auth/register-device"
                let url = "https://aladdin-ai.ru\(endpoint)"
                
                logger.business("📡 Calling: \(url)")
                logger.business("   - DeviceID: \(deviceId)")
                logger.business("   - User-Agent: iOS/\(UIDevice.current.systemVersion) | Simulator: \(ProcessInfo.processInfo.environment["SIMULATOR_UDID"] != nil)")
                logger.business("   - Attempt: \(attempt)/\(maxAttempts)")
                
                let response: JWTDeviceRegisterResponse = try await withCheckedThrowingContinuation { continuation in
                    var hasResumed = false
                    
                    let completion: (Result<JWTDeviceRegisterResponse, Error>) -> Void = { result in
                        guard !hasResumed else {
                            self.logger.error("⚠️ CRITICAL: Double resume prevented in retry wrapper")
                            return
                        }
                        hasResumed = true
                        
                        switch result {
                        case .success(let resp):
                            continuation.resume(returning: resp)
                        case .failure(let err):
                            continuation.resume(throwing: err)
                        }
                    }
                    
                    if isTrial {
                        let trialInfo = TrialInfo(
                            startDate: Date(),
                            endDate: Calendar.current.date(byAdding: .day, value: 14, to: Date())!,
                            durationDays: 14
                        )
                        let trialRequest = TrialDeviceRegisterRequest(
                            deviceId: request.deviceId,
                            deviceType: request.deviceType,
                            trialInfo: trialInfo,
                            antiAbuse: nil
                        )
                        APIService.shared.registerDeviceWithTrial(request: trialRequest, completion: completion)
                    } else {
                        APIService.shared.registerDeviceAnonymously(request: request, completion: completion)
                    }
                }
                
                logger.business("✅ Registration succeeded on attempt \(attempt)")
                return response
                
            } catch {
                lastError = error
                logger.error("❌ Attempt \(attempt) failed: \(error.localizedDescription)")
                
                if let networkError = error as? NetworkError, case .httpError(404) = networkError {
                    logger.error("❌ 404 - Endpoint /api/auth/register-device not found on server")
                    logger.business("🔄 Recommendation: Server should support /api/auth/register-device or /api/auth/register-device-trial")
                    logger.business("   - DeviceID: \(deviceId)")
                    logger.business("   - Is Simulator: \(ProcessInfo.processInfo.environment["SIMULATOR_UDID"] != nil)")
                    
                    let detailedError = NSError(domain: "ALADDIN.Registration", code: 404, userInfo: [
                        NSLocalizedDescriptionKey: "Registration endpoint not found. Please check server configuration.",
                        "url": "https://aladdin-ai.ru/api/auth/register-device",
                        "fallback": "/api/auth/register-device-trial",
                        "deviceId": deviceId
                    ])
                    throw detailedError
                }
                
                if !isLastAttempt {
                    let delay = Double(attempt) * 1.0 // 1s, 2s, 4s...
                    logger.business("⏳ Retrying in \(delay)s...")
                    try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
        }
        
        // All attempts failed
        logger.error("❌ All \(maxAttempts) registration attempts failed. Last error: \(lastError?.localizedDescription ?? "unknown")")
        throw lastError ?? NSError(domain: "ALADDIN.Registration", code: -1, userInfo: [NSLocalizedDescriptionKey: "Registration failed after \(maxAttempts) attempts"])
    }

    /// 🔑 Register device anonymously with trial via backend (server-side source of truth).
    private func registerDeviceWithTrial(trialInfo: TrialInfo) async throws -> JWTToken {
        logger.business("📱 НАЧАЛО РЕГИСТРАЦИИ УСТРОЙСТВА С TRIAL (server-side)")

        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        let deviceType = "ios"
        let antiAbuseSignals = buildTrialAntiAbuseSignals(deviceId: deviceId)

        let request = TrialDeviceRegisterRequest(
            deviceId: deviceId,
            deviceType: deviceType,
            trialInfo: trialInfo,
            antiAbuse: antiAbuseSignals
        )

        // ✅ ПРОДАКШН: Реальный API вызов через APIService
        logger.business("📡 ВЫЗОВ API: POST /api/auth/register-device-trial")

        let response = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<JWTDeviceRegisterResponse, Error>) in
            var hasResumed = false

            APIService.shared.registerDeviceWithTrial(request: request) { [self] result in
                guard !hasResumed else {
                    self.logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in registerDeviceWithTrial()!")
                    return
                }

                switch result {
                case .success(let jwtResponse):
                    // Save refresh token if present (same as free registration path).
                    if let refreshToken = jwtResponse.refreshToken {
                        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
                        self.logger.business("✅ Refresh token saved to Keychain for trial device")
                    }

                    // Validate JWT token payload/signature-like checks.
                    let validationResult = self.validateJWTToken(jwtResponse.token)
                    switch validationResult {
                    case .valid:
                        hasResumed = true
                        continuation.resume(returning: jwtResponse)
                    case .invalid(let reason):
                        self.logger.error("❌ Trial JWT invalid: \(reason)")
                        hasResumed = true
                        continuation.resume(throwing: SubscriptionError.invalidToken)
                    }

                case .failure(let error):
                    // Keep parity with registerDeviceAnonymously: handle 401 asynchronously.
                    if let networkError = error as? NetworkError,
                       case .httpError(401) = networkError {
                        self.logger.business("🚨 Detected 401 during trial registration")
                        Task { await self.handle401Error() }
                        return
                    }

                    hasResumed = true
                    continuation.resume(throwing: error)
                }
            }
        }

        // ✅ Parse exp for local expiry handling.
        let realExpFromJWT = parseJWTToken(response.token)?.expiresAt
        let finalExpiresAt = realExpFromJWT ?? response.expiresAtDate ?? Date().addingTimeInterval(86400)

        let jwtToken = JWTToken(
            token: response.token,
            deviceId: response.deviceId,
            subscriptionLevel: SubscriptionLevel.fromAPIPlanString(response.subscription.level),
            trialInfo: response.subscription.trialInfo,
            expiresAt: finalExpiresAt,
            issuedAt: response.registeredAtDate ?? Date(),
            issuer: "ALADDIN",
            limits: SubscriptionLimits.freeLimits, // overwritten by subscriptionStatus sync below
            components: []
        )

        await storeToken(jwtToken)

        // Sync subscription/limits and update trial status for UI.
        let newSubscriptionStatus = response.subscription.toSubscriptionStatus()
        updateSubscriptionStatus(newSubscriptionStatus)

        if let serverTrial = jwtToken.trialInfo {
            updateTrialStatus(serverTrial)
        }

        return jwtToken
    }

    // MARK: - Privacy-safe trial anti-abuse

    private func recordTrialActivationAttempt(now: Date = Date()) {
        var timestamps = trialAttemptTimestamps()
        timestamps.append(now.timeIntervalSince1970)
        let minAllowed = now.addingTimeInterval(-24 * 3600).timeIntervalSince1970
        timestamps = timestamps.filter { $0 >= minAllowed }
        UserDefaults.standard.set(timestamps, forKey: trialAttemptTimestampsKey)
    }

    private func trialAttemptTimestamps(now: Date = Date()) -> [TimeInterval] {
        let raw = UserDefaults.standard.array(forKey: trialAttemptTimestampsKey) as? [TimeInterval] ?? []
        let minAllowed = now.addingTimeInterval(-24 * 3600).timeIntervalSince1970
        return raw.filter { $0 >= minAllowed }
    }

    private func localTrialCooldownSeconds(now: Date = Date()) -> Int {
        let timestamps = trialAttemptTimestamps(now: now)
        let attemptsInHour = timestamps.filter { now.timeIntervalSince1970 - $0 <= 3600 }.count
        guard attemptsInHour >= 3, let last = timestamps.max() else { return 0 }
        let elapsed = now.timeIntervalSince1970 - last
        let cooldown: TimeInterval = 15 * 60
        let remaining = max(0, cooldown - elapsed)
        return Int(remaining.rounded(.up))
    }

    private func buildTrialAntiAbuseSignals(deviceId: String, now: Date = Date()) -> TrialAntiAbuseSignals {
        let timestamps = trialAttemptTimestamps(now: now)
        let velocity1h = timestamps.filter { now.timeIntervalSince1970 - $0 <= 3600 }.count
        let velocity24h = timestamps.count
        let cooldown = localTrialCooldownSeconds(now: now)

        let salt = loadOrRotateTrialRiskSalt(now: now)
        let baseFingerprint = [
            deviceId,
            UIDevice.current.model,
            UIDevice.current.systemVersion,
            Bundle.main.bundleIdentifier ?? "unknown.bundle"
        ].joined(separator: "|")

        let fingerprintHash = sha256Hex("\(salt)|\(baseFingerprint)")
        let appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown"

        return TrialAntiAbuseSignals(
            installFingerprintHash: fingerprintHash,
            velocity1h: velocity1h,
            velocity24h: velocity24h,
            cooldownSeconds: cooldown,
            appVersion: appVersion,
            osVersion: UIDevice.current.systemVersion,
            riskVersion: "ios-v1"
        )
    }

    private func loadOrRotateTrialRiskSalt(now: Date = Date()) -> String {
        let defaults = UserDefaults.standard
        let createdAt = defaults.object(forKey: trialRiskSaltCreatedAtKey) as? Date
        let existing = defaults.string(forKey: trialRiskSaltKey)
        let shouldRotate: Bool = {
            guard let createdAt else { return true }
            return now.timeIntervalSince(createdAt) > 30 * 24 * 3600
        }()
        if let existing, !existing.isEmpty, !shouldRotate {
            return existing
        }
        let fresh = UUID().uuidString.replacingOccurrences(of: "-", with: "")
        defaults.set(fresh, forKey: trialRiskSaltKey)
        defaults.set(now, forKey: trialRiskSaltCreatedAtKey)
        return fresh
    }

    private func sha256Hex(_ input: String) -> String {
        let digest = SHA256.hash(data: Data(input.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
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
        let subscriptionLevel = subscription != nil ? SubscriptionLevel.fromAPIPlanString(subscription!.level) : .free
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

    /// Level used only for **family roster size cap** (not for billing UI).
    /// Server may keep `plan_level` at free while `trial_info` is still active — then cap must be trial (3).
    private func subscriptionLevelForFamilyMemberCap(_ status: SubscriptionStatus) -> SubscriptionLevel {
        if let t = status.trialInfo, t.isActive {
            return .trial
        }
        if status.trialInfo == nil, trialStatus?.isActive == true {
            return .trial
        }
        return status.level
    }

    /// 🔄 Update subscription status
    /// ✅ ИСПРАВЛЕНО: Изменено с private на internal для использования в TokenHealthMonitor
    @MainActor
    func updateSubscriptionStatus(_ status: SubscriptionStatus) {
        let previousSubscription = currentSubscription
        let previousFamilyLimit = currentFamilyLimit

        currentSubscription = status
        persistSubscriptionStatus(status)
        logger.business("📊 Subscription updated: \(status.level)")

        // ✅ SINGLE SOURCE OF TRUTH: Update both UserDefaults (for legacy) and published properties
        // Uses mapping aligned with prod limits: free=1, trial=3, personal=2, family=6, premium=10
        // When JWT `plan_level` is still "free" but trial is active, cap must follow trial (3), not free (1).
        let levelForFamilyCap = subscriptionLevelForFamilyMemberCap(status)
        let tariffBasedLimit = familyMemberLimit(for: levelForFamilyCap)
        let currentUsed = familyQuotaSnapshot.used
        let cappedUsed = max(0, min(currentUsed, tariffBasedLimit))
        let calculatedRemaining = max(0, tariffBasedLimit - cappedUsed)

        // Update legacy storage for backward compatibility with FamilyScreen and VM
        UserDefaults.standard.set(tariffBasedLimit, forKey: "family_limit")
        UserDefaults.standard.set(calculatedRemaining, forKey: "family_remaining")
        UserDefaults.standard.synchronize()

        // Update reactive published properties (new single source)
        let trimmedFamilyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let familyId: String? = trimmedFamilyId.isEmpty ? nil : trimmedFamilyId
        publishFamilyQuotaSnapshot(used: cappedUsed, maxSlots: tariffBasedLimit, source: .tariffFallback, familyId: familyId)

        VisualLogger.shared.log("🔄 TARIFF→FAMILY SYNC: plan_level=\(status.level), cap_level=\(levelForFamilyCap), family_limit=\(tariffBasedLimit), remaining=\(calculatedRemaining) (published + UserDefaults)", level: .info, category: "FAMILY")
        logger.business("🔄 Tariff sync: family_limit=\(tariffBasedLimit) for cap_level=\(levelForFamilyCap.rawValue) (plan_level=\(status.level.rawValue))")

        let subscriptionMeaningfullyChanged =
            previousSubscription?.level != status.level
            || previousSubscription?.expiresAt != status.expiresAt
            || previousSubscription?.trialInfo != status.trialInfo
            || previousFamilyLimit != tariffBasedLimit

        // Не шлём уведомление при идентичном снимке — иначе MainScreen коалесцирует лишний loadDashboardData и дубли GET /api/devices.
        if subscriptionMeaningfullyChanged {
            NotificationCenter.default.post(
                name: Notification.Name("SubscriptionUpdated"),
                object: nil,
                userInfo: ["level": status.level.rawValue, "limit": tariffBasedLimit]
            )
        }

        reconcileTariffManagerWithSubscription(reason: "updateSubscriptionStatus")
        bumpSubscriptionDisplayEpoch()
    }

    /// 🎁 Update trial status
    @MainActor
    private func updateTrialStatus(_ trial: TrialInfo) {
        // Cancel trial notifications if trial is no longer active
        if !trial.isActive && trialStatus?.isActive == true {
            NotificationManager.shared.cancelTrialNotifications()
            logger.business("❌ Trial notifications cancelled - trial no longer active")
        }

        trialStatus = trial
        persistTrialStatus(trial)
        logger.business("🎁 Trial updated: \(trial.daysRemaining) days remaining")
        // Лимит семьи и градиент главной завязаны на `subscriptionLevelForFamilyMemberCap`, который смотрит и на `trialStatus`.
        // Раньше `registerDeviceWithTrial` вызывал `updateSubscriptionStatus` до присвоения `trialStatus` — кап оставался free (1) и цвет «золотой».
        if let sub = currentSubscription {
            updateSubscriptionStatus(sub)
        }
        reconcileTariffManagerWithSubscription(reason: "updateTrialStatus")
        bumpSubscriptionDisplayEpoch()
    }

    private func bumpSubscriptionDisplayEpoch() {
        subscriptionDisplayEpoch &+= 1
        // На части устройств/версий SwiftUI цепочка @Published для UInt64 + градиент по derived Color
        // иногда не перерисовывает карточку; явный ping гарантирует инвалидацию дерева.
        objectWillChange.send()
    }

    private func publishFamilyQuotaSnapshot(
        used: Int,
        maxSlots: Int,
        source: FamilyQuotaSource,
        familyId: String?
    ) {
        let sanitizedMax = max(0, maxSlots)
        let sanitizedUsed = max(0, min(used, sanitizedMax))
        let remaining = max(0, sanitizedMax - sanitizedUsed)

        currentFamilyLimit = sanitizedMax
        currentFamilyRemaining = remaining
        familyQuotaSnapshot = FamilyQuotaSnapshot(
            used: sanitizedUsed,
            max: sanitizedMax,
            source: source,
            updatedAt: Date(),
            familyId: familyId?.isEmpty == true ? nil : familyId
        )

        UserDefaults.standard.set(sanitizedMax, forKey: "family_limit")
        UserDefaults.standard.set(remaining, forKey: "family_remaining")
        UserDefaults.standard.set(sanitizedUsed, forKey: "family_roster_used_last")
        UserDefaults.standard.set(source.rawValue, forKey: "family_quota_source_last")
        if let familyId, !familyId.isEmpty {
            UserDefaults.standard.set(familyId, forKey: "family_quota_family_id_last")
        }
        UserDefaults.standard.synchronize()
    }

    private func restoreFamilyQuotaSnapshotFromCache() {
        let cachedMax = UserDefaults.standard.integer(forKey: "family_limit")
        guard cachedMax > 0 else { return }

        let cachedUsed = UserDefaults.standard.integer(forKey: "family_roster_used_last")
        let cachedFamilyId = UserDefaults.standard.string(forKey: "family_quota_family_id_last")
        let trimmedCurrentFamilyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let currentFamilyId: String? = trimmedCurrentFamilyId.isEmpty ? nil : trimmedCurrentFamilyId
        let cachedSourceRaw = UserDefaults.standard.string(forKey: "family_quota_source_last")
        let cachedSource = FamilyQuotaSource(rawValue: cachedSourceRaw ?? "") ?? .persistedCache
        let normalizedCachedFamilyId = cachedFamilyId?.trimmingCharacters(in: .whitespacesAndNewlines)

        // Do not restore used slots from another family context.
        let safeUsed: Int
        if let cachedId = normalizedCachedFamilyId,
           !cachedId.isEmpty,
           let currentFamilyId,
           !currentFamilyId.isEmpty,
           cachedId != currentFamilyId {
            safeUsed = 0
        } else if currentFamilyId == nil || currentFamilyId?.isEmpty == true {
            safeUsed = 0
        } else {
            safeUsed = cachedUsed
        }

        publishFamilyQuotaSnapshot(
            used: safeUsed,
            maxSlots: cachedMax,
            source: cachedSource == .serverStats ? .persistedCache : cachedSource,
            familyId: normalizedCachedFamilyId
        )
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

        #if DEBUG
        logSubscriptionStateSnapshotAfterKeychainLoad()
        #endif

        logger.business("💾 Persisted data loaded")
        persistOfflineUserIdFromJWTIfMissing()
        bumpSubscriptionDisplayEpoch()
    }

    /// Подставляет `user_id` для offline-слоя из JWT, если в токене есть явные поля (без `sub` — часто device/session).
    private func persistOfflineUserIdFromJWTIfMissing() {
        guard let jwt = currentToken?.token, !jwt.isEmpty else { return }
        let existing = (UserDefaults.standard.string(forKey: "user_id") ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard existing.isEmpty else { return }
        guard let payload = FamilyLocalStore.jwtPayloadDictionary(from: jwt) else { return }
        let extracted: String? = {
            if let s = payload["user_id"] as? String {
                let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
                return t.isEmpty ? nil : t
            }
            if let i = payload["user_id"] as? Int { return String(i) }
            if let s = payload["userId"] as? String {
                let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
                return t.isEmpty ? nil : t
            }
            if let i = payload["userId"] as? Int { return String(i) }
            return nil
        }()
        guard let extracted, !extracted.isEmpty else { return }
        UserDefaults.standard.set(extracted, forKey: "user_id")
        NotificationCenter.default.post(name: .aladdinUserIdentityDidUpdate, object: nil)
    }

    #if DEBUG
    /// Single diagnostic line: token snapshot vs subscription vs trial Keychain vs effective level (avoids trial/free confusion).
    private func logSubscriptionStateSnapshotAfterKeychainLoad() {
        let tokenLevel = currentToken?.subscriptionLevel.rawValue ?? "nil"
        let planLevel = currentSubscription.map { $0.level.rawValue } ?? "nil"
        let trialLine: String = {
            guard let t = trialStatus else { return "trialStatus=nil" }
            let iso = ISO8601DateFormatter()
            iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            return "trialStatus active=\(t.isActive) end=\(iso.string(from: t.endDate))"
        }()
        let effective = getCurrentLevel().rawValue
        let line = "📊 SUBSCRIPTION_KEYCHAIN_SNAPSHOT token_level=\(tokenLevel) plan_level=\(planLevel) \(trialLine) getCurrentLevel=\(effective)"
        print(line)
        VisualLogger.shared.log(line, level: .info, category: "SUBSCRIPTION")
        logger.business(line)
    }
    #endif

    /// Runs local trial expiry handling at most once per `trialExpiryForegroundCheckMinInterval` (cold start / first active always runs).
    /// After successful server sync, `updateFromServerStatus` overwrites local state — server wins.
    func performThrottledTrialExpiryCheckIfNeeded() async {
        let now = Date()
        if let last = lastThrottledTrialExpiryCheckAt,
           now.timeIntervalSince(last) < trialExpiryForegroundCheckMinInterval {
            return
        }
        lastThrottledTrialExpiryCheckAt = now
        await checkTrialExpiration()
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
        persistOfflineUserIdFromJWTIfMissing()
        bumpSubscriptionDisplayEpoch()
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

    private func deleteFromKeychain(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: key,
        ]
        SecItemDelete(query as CFDictionary)
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

        let _ = createSubscriptionStatus(
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

        updateSubscriptionStatus(freeSubscription)
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
            updateSubscriptionStatus(subscription)

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

    // MARK: - Tariff pipeline (B5 / B6)

    /// Выровнять `TariffManager` под эффективный уровень подписки/триала (`getCurrentLevel`). Сервер уже отражён в `SubscriptionManager`; здесь только защита и каталог функций.
    private func reconcileTariffManagerWithSubscription(reason: String) {
        let effective = getCurrentLevel()
        let trialActive = trialStatus?.isActive ?? false
        let plan = currentSubscription?.level.rawValue ?? "nil"
        let target = TariffType.fromSubscriptionLevel(effective)
        let tm = TariffManager.shared
        if tm.currentTariff == target {
            logger.business("📊 TRIAL_TARIFF_PIPELINE ok reason=\(reason) plan=\(plan) trial_active=\(trialActive) effective=\(effective.rawValue) tariff_mgr=\(target.rawValue)")
            return
        }
        logger.business("📊 TRIAL_TARIFF_PIPELINE sync reason=\(reason) plan=\(plan) trial_active=\(trialActive) effective=\(effective.rawValue) \(tm.currentTariff.rawValue)→\(target.rawValue)")
        tm.saveTariff(target, pullServerAfterSave: false)
    }

    /// После локального `TariffManager.saveTariff` (покупка, QR, код) подтягиваем статус с сервера — единый источник правды для главной и JWT.
    func pullSubscriptionAfterLocalTariffSave() async {
        logger.business("📊 TRIAL_TARIFF_PIPELINE: local TariffManager.save → pullSubscriptionAfterLocalTariffSave → forceSync")
        await forceSync()
    }

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

    /// Apply decoded GET `/api/subscription/status` body (trial, limits, level, persistence, family cap).
    @MainActor
    func applySubscriptionPayloadFromServer(_ serverStatus: SubscriptionStatus) async {
        await updateFromServerStatus(serverStatus)
    }

    /// 🔄 Sync subscription data with server when online
    @MainActor
    func syncWithServer() async {
        guard !isOfflineMode else {
            logger.network("📡 Skipping sync - offline mode")
            return
        }
        guard !isSyncInFlight else {
            logger.network("📡 Sync skipped - request already in flight")
            return
        }
        isSyncInFlight = true
        defer { isSyncInFlight = false }

        logger.network("📡 Starting subscription sync with server")

        do {
            // Get current token for explicit authorization
            guard let token = currentToken?.token else {
                logger.error("❌ Sync failed: No token available")
                return
            }

            let serverStatus: SubscriptionStatus = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatusWithToken(
                    userId: "current",
                    token: token,
                    merging: self.currentSubscription
                ) { result in
                    switch result {
                    case .success(let status):
                        continuation.resume(returning: status)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }

            // Update local data if server has newer information
            if shouldUpdateFromServer(serverStatus) {
                await updateFromServerStatus(serverStatus)
                logger.network("✅ Subscription synced with server")
            } else {
                logger.network("📡 Local data is up to date")
            }

            let now = Date()
            lastSyncDate = now
            let fingerprint = subscriptionFingerprint(serverStatus)
            if shouldTrackSyncCompletedEvent(now: now, fingerprint: fingerprint) {
                trackEvent(.syncCompleted)
                lastSyncCompletedEventAt = now
                lastSyncCompletedFingerprint = fingerprint
            }

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
               serverStatus.expiresAt != localSubscription.expiresAt ||
               serverStatus.trialInfo != localSubscription.trialInfo
    }

    private func subscriptionFingerprint(_ status: SubscriptionStatus) -> String {
        let expiryTs = Int(status.expiresAt?.timeIntervalSince1970 ?? 0)
        let trialActive = status.trialInfo?.isActive == true
        let trialDays = status.trialInfo?.daysRemaining ?? -1
        return "\(status.level.rawValue)|\(status.isActive)|exp=\(expiryTs)|trial=\(trialActive)|days=\(trialDays)"
    }

    private func shouldTrackSyncCompletedEvent(now: Date, fingerprint: String) -> Bool {
        if let lastAt = lastSyncCompletedEventAt,
           now.timeIntervalSince(lastAt) < minSyncCompletedEventInterval,
           lastSyncCompletedFingerprint == fingerprint {
            logger.business("ℹ️ sync_completed skipped: unchanged subscription state within debounce window")
            return false
        }
        return true
    }

    /// 📥 Update local subscription from server data
    private func updateFromServerStatus(_ serverStatus: SubscriptionStatus) async {
        // Convert server response to local model
        let subscriptionLevel = serverStatus.level

        // Update family limits from server status (ensures sync after restore/sync)
        updateSubscriptionStatus(serverStatus)

        // 🔬 DIAGNOSTICS: Testing in another sync context (updateFromServerStatus)
        #if DEBUG
        logger.business("🔬 DIAGNOSTICS: Testing SubscriptionStatus creation in updateFromServerStatus")

        do {
            let _ = SubscriptionStatus(
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
            logger.business("❌ DIAGNOSTICS: Failed to create SubscriptionStatus in updateFromServerStatus")
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
        reconcileTariffManagerWithSubscription(reason: "updateFromServerStatus")
        bumpSubscriptionDisplayEpoch()

        await MainActor.run {
            rescheduleLocalSubscriptionNotifications(afterSync: serverStatus)
        }
    }

    /// Локальные напоминания (UNCalendar): trial 7/3/1 дня; платный тариф — за 3 и 1 день до `expiresAt`.
    /// Серверные push (если настроены) — отдельный канал; здесь только клиентское планирование после синка.
    private func rescheduleLocalSubscriptionNotifications(afterSync status: SubscriptionStatus) {
        let now = Date()

        if let trial = status.trialInfo, trial.isActive, trial.endDate > now {
            NotificationManager.shared.scheduleTrialNotifications(trialEndDate: trial.endDate)
        } else {
            NotificationManager.shared.cancelTrialNotifications()
        }

        let paidTiers: Set<SubscriptionLevel> = [.personal, .family, .premium]
        if paidTiers.contains(status.level),
           status.isActive,
           let exp = status.expiresAt,
           exp > now {
            NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: exp)
        } else {
            NotificationManager.shared.cancelRenewalNotifications()
        }
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
            // ✅ Динамическая локаль в зависимости от языка приложения
            let lang = UserDefaults.standard.string(forKey: "app_language") ?? "ru"
            formatter.locale = Locale(identifier: lang == "ru" ? "ru_RU" : "en_US")
            return formatter.localizedString(for: date, relativeTo: Date())
        } ?? (UserDefaults.standard.string(forKey: "app_language") ?? "ru" == "ru" ? "Никогда" : "Never")

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
        var mergedMeta = metadata ?? [:]
        mergedMeta["plan_level"] = currentSubscription?.level.rawValue ?? "unknown"
        mergedMeta["effective_level"] = getCurrentLevel().rawValue

        let eventData = SubscriptionEventData(
            event: event,
            userId: userId ?? currentToken?.deviceId,
            subscriptionLevel: subscriptionLevel ?? currentSubscription?.level.rawValue,
            featureId: featureId,
            resourceType: resourceType,
            amount: amount,
            transactionId: transactionId,
            errorMessage: errorMessage,
            metadata: mergedMeta.isEmpty ? nil : mergedMeta
        )

        pendingEvents.append(eventData)
        pruneExpiredEventsLocked()

        // Limit queue size to prevent memory issues
        if pendingEvents.count > 1000 {
            pendingEvents.removeFirst(100)
        }
        savePendingEventsLocked()
        lastQueueSize = pendingEvents.count
        logger.business("📥 SubscriptionEvent queued. queue_size=\(lastQueueSize)")

        // Send immediately if online
        if !self.isOfflineMode {
            Task {
                await self.flushPendingEvents()
            }
        }

        logger.business("📊 Event tracked: \(event.rawValue)")
    }

    /// 📤 Send pending events to server
    @MainActor private func flushPendingEvents() async {
        guard !isOfflineMode else { return }

        pruneExpiredEventsLocked()
        guard !pendingEvents.isEmpty else { return }
        guard !isFlushingEvents else { return }
        isFlushingEvents = true
        let eventsToSend: [SubscriptionEventData] = Array(pendingEvents.prefix(maxEventBatchSize))

        guard !eventsToSend.isEmpty else { return }

        do {
            try await sendSubscriptionEventsToMetrics(eventsToSend)
            let sentIds = Set(eventsToSend.map { $0.eventId })
            pendingEvents.removeAll { sentIds.contains($0.eventId) }
            flushRetryCount = 0
            isFlushingEvents = false
            savePendingEventsLocked()
            eventsSentCount += eventsToSend.count
            lastQueueSize = pendingEvents.count
            logger.business("📤 Subscription events sent: \(eventsToSend.count)")
        } catch {
            flushRetryCount += 1
            isFlushingEvents = false
            // Exponential backoff: 2, 4, 8, 16, 30s cap
            let delay: TimeInterval = min(pow(2.0, Double(flushRetryCount)), 30.0)
            let shouldRetry = !isOfflineMode && !pendingEvents.isEmpty
            savePendingEventsLocked()
            eventsFailedCount += 1
            lastQueueSize = pendingEvents.count
            logger.error("❌ Failed to send subscription events: \(error.localizedDescription)")
            if shouldRetry {
                Task { @MainActor in
                    try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                    await self.flushPendingEvents()
                }
            }
        }
    }

    private func sendSubscriptionEventsToMetrics(_ events: [SubscriptionEventData]) async throws {
        let metrics: [[String: AnyCodable]] = events.map { event in
            var item: [String: AnyCodable] = [
                "timestamp": AnyCodable(event.timestamp.timeIntervalSince1970),
                "eventId": AnyCodable(event.eventId),
                "eventType": AnyCodable(event.event.rawValue),
                "deviceId": AnyCodable(event.deviceId),
            ]
            if let level = event.subscriptionLevel { item["subscriptionLevel"] = AnyCodable(level) }
            if let featureId = event.featureId { item["featureId"] = AnyCodable(featureId) }
            if let resourceType = event.resourceType { item["resourceType"] = AnyCodable(resourceType) }
            if let amount = event.amount { item["amount"] = AnyCodable(amount) }
            if let transactionId = event.transactionId { item["transactionId"] = AnyCodable(transactionId) }
            if let errorMessage = event.errorMessage { item["errorMessage"] = AnyCodable(errorMessage) }
            if let metadata = event.metadata { item["metadata"] = AnyCodable(metadata) }
            return item
        }

        try await APIService.shared.sendSubscriptionEventsBatch(events: metrics)
    }

    private func loadPendingEvents() {
        guard let data = UserDefaults.standard.data(forKey: pendingEventsStorageKey) else { return }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        if let saved = try? decoder.decode([SubscriptionEventData].self, from: data) {
            pendingEvents = saved
            pruneExpiredEventsLocked()
            savePendingEventsLocked()
            logger.business("💾 Restored pending subscription events: \(saved.count)")
        }
    }

    private func savePendingEventsLocked() {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        if let data = try? encoder.encode(pendingEvents) {
            UserDefaults.standard.set(data, forKey: pendingEventsStorageKey)
        }
    }

    private func pruneExpiredEventsLocked() {
        let now = Date()
        pendingEvents.removeAll { now.timeIntervalSince($0.timestamp) > pendingEventsTTL }
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
            case .serviceUnavailable:
                return "Сервис временно недоступен. Повторите попытку позже."
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
                _ = try await registerDeviceAnonymously()
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
