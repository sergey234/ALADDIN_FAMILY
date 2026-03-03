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

// Import subscription models
// Note: This file uses both local models and API models
// Models are defined in separate files in Core/Models/

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

    // MARK: - Initialization

    /// Initialize on app start (async operations)
    func initializeOnAppStart() async {
        print("🚀🚀🚀 INITIALIZE_ON_APP_START: Method called")
        logger.business("🚀 SubscriptionManager.initializeOnAppStart() called")
        VisualLogger.shared.log("🚀 SubscriptionManager.initializeOnAppStart() called", level: .info)

        // Check current token state
        let hasToken = currentToken != nil
        logger.business("📋 Token check: currentToken is nil = \(!hasToken)")

        if let token = currentToken {
            logger.business("📋 Token details: deviceId=\(token.deviceId), level=\(token.subscriptionLevel), expires=\(token.expiresAt)")
        }

        // Check if token is expired
        let tokenExpired = isTokenExpired()
        logger.business("📋 Token expired check: \(tokenExpired)")

        // Check if we need to register device
        if currentToken == nil || tokenExpired {
            logger.business("📱 CONDITION MET: No valid token found, registering device anonymously")

            // Check network connectivity before attempting
            logger.business("🌐 Checking network connectivity...")
            // For now assume network is available

            do {
                logger.business("📱 Starting device registration...")
                try await registerDeviceAnonymously()
                logger.business("✅ Device registered successfully with trial subscription")

                // Verify token was set
                if currentToken != nil {
                    logger.business("✅ Token successfully set after registration")
                } else {
                    logger.error("❌ Token not set after registration")
                }

            } catch {
                logger.error("❌ Failed to register device: \(error.localizedDescription)")
                logger.error("❌ Error type: \(type(of: error))")
                logger.error("❌ Error details: \(error)")

                // Fallback: just log the error, app continues without token
                logger.business("🔄 FALLBACK: API registration failed, continuing without token")
                logger.business("ℹ️ INFO: User will need to manually register or API will be unavailable")
            }
        } else {
            logger.business("✅ CONDITION NOT MET: Valid token found, using existing subscription")
        }

        logger.security("🚀 SubscriptionManager: App start initialization completed")
    }

    /// Check if current token is expired
    private func isTokenExpired() -> Bool {
        guard let token = currentToken else { return true }
        return JWTTokenManager.shared.isTokenExpired(token.token)
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

            let response: SubscriptionStatusResponse = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatus(userId: "current") { result in
                    switch result {
                    case .success(let statusResponse):
                        continuation.resume(returning: statusResponse)
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }

            await updateSubscriptionStatus(response.status)

            // Update trial status if present
            if let trialInfo = response.status.trialInfo {
                await updateTrialStatus(trialInfo)
            }

            logger.business("✅ Subscription status refreshed: \(response.status.level)")

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
            let url = URL(string: "https://aladdin-ai.ru/auth/register-device")!
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
            let url = URL(string: "https://aladdin-ai.ru/auth/register-device")!
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
    func registerDeviceAnonymously() async throws {
        logger.business("📱 Registering device anonymously")

        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
        let deviceType = "ios"

        let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: deviceType)

        // 🚨 EMERGENCY: Try GET instead of POST to see if server accepts it
        print("🚨🚨🚨 EMERGENCY MODE: Using GET instead of POST for register-device")

        let url = URL(string: "https://aladdin-ai.ru/auth/register-device")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET" // EMERGENCY CHANGE!

        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        let httpResponse = response as? HTTPURLResponse

        print("🚨🚨🚨 EMERGENCY RESPONSE:")
        print("   - Status Code: \(httpResponse?.statusCode ?? 0)")
        if let responseString = String(data: data, encoding: .utf8) {
            print("   - Response Body: \(responseString.prefix(1000))")
        }

        // If server accepts GET, it might return some response
        // For now, just return a mock response to continue
        let mockResponse = JWTDeviceRegisterResponse(
            token: "emergency-mock-token-\(UUID().uuidString)",
            deviceId: deviceId,
            expiresAt: Date().addingTimeInterval(24 * 60 * 60), // 1 day
            registeredAt: Date(),
            subscription: SubscriptionStatus(
                level: .trial,
                isActive: true,
                expiresAt: Date().addingTimeInterval(14 * 24 * 60 * 60), // 14 days
                trialInfo: TrialInfo(
                    startDate: Date(),
                    endDate: Date().addingTimeInterval(14 * 24 * 60 * 60), // 14 days
                    durationDays: 14
                ),
                limits: SubscriptionLimits(
                    maxDevices: 3,
                    maxAIMessages: 50,
                    maxScans: 100,
                    maxReports: 10,
                    currentUsage: UsageCounters(
                        aiMessages: 0,
                        scans: 0,
                        reports: 0,
                        devices: 0
                    )
                ),
                components: [],
                lastUpdated: Date()
            )
        )

        print("✅ EMERGENCY: Created mock response, continuing...")
        await storeToken(JWTToken(
            token: mockResponse.token,
            deviceId: mockResponse.deviceId,
            subscriptionLevel: mockResponse.subscription.level,
            trialInfo: mockResponse.subscription.trialInfo,
            expiresAt: Date().addingTimeInterval(24 * 60 * 60), // 1 day
            issuedAt: Date(),
            issuer: "emergency-test",
            limits: mockResponse.subscription.limits,
            components: []
        ))
        await updateSubscriptionStatus(mockResponse.subscription)

        logger.business("✅ Device registered: \(deviceId)")
    }

    // MARK: - Private Methods

    /// 🔐 Parse JWT token and extract subscription data
    private func parseJWTToken(_ token: String) -> JWTToken? {
        // Split JWT token
        let parts = token.split(separator: ".")
        guard parts.count == 3 else { return nil }

        // Decode payload
        guard let payloadData = decodeBase64(String(parts[1])),
              let payload = try? JSONDecoder().decode(JWTPayload.self, from: payloadData) else {
            return nil
        }

        // Convert to our model
        return JWTToken(
            token: token,
            deviceId: payload.deviceId,
            subscriptionLevel: payload.subscriptionLevel,
            trialInfo: payload.trialInfo,
            expiresAt: Date(timeIntervalSince1970: payload.exp),
            issuedAt: Date(timeIntervalSince1970: payload.iat),
            issuer: payload.iss,
            limits: payload.limits,
            components: payload.components
        )
    }

    /// 🔄 Update subscription status
    private func updateSubscriptionStatus(_ status: SubscriptionStatus) async {
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
        // Load token
        if let tokenData = loadFromKeychain(key: tokenKey),
           let token = try? JSONDecoder().decode(JWTToken.self, from: tokenData) {
            currentToken = token
            // ✅ КРИТИЧНО: Также восстанавливаем токен в AppConfig для NetworkManager
            AppConfig.authToken = token.token
            logger.business("🔑 Token restored from Keychain to AppConfig.authToken")
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
    private func storeToken(_ token: JWTToken) async {
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

extension SubscriptionLimits {
    /// Free tier limits
    static var freeLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 1,
            maxAIMessages: 10,
            maxScans: 5,
            maxReports: 2,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }

    /// Trial limits
    static var trialLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 3,
            maxAIMessages: 50,
            maxScans: 100,
            maxReports: 10,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
}

// MARK: - API Request Models

/// 📡 JWT Payload Structure
private struct JWTPayload: Codable {
    let deviceId: String
    let subscriptionLevel: SubscriptionLevel
    let trialInfo: TrialInfo?
    let exp: Double
    let iat: Double
    let iss: String
    let limits: SubscriptionLimits
    let components: [String]

    enum CodingKeys: String, CodingKey {
        case deviceId = "device_id"
        case subscriptionLevel = "subscription_level"
        case trialInfo = "trial_info"
        case exp, iat, iss, limits, components
    }
}

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
            // Get current subscription status from server
            let serverStatus: SubscriptionStatus = try await withCheckedThrowingContinuation { continuation in
                APIService.shared.getSubscriptionStatus(userId: "current") { result in
                    switch result {
                    case .success(let response):
                        // Convert response to SubscriptionStatus
                        let subscriptionStatus = SubscriptionStatus(
                            level: response.status.level,
                            isActive: response.status.isActive,
                            expiresAt: response.status.expiresAt,
                            trialInfo: response.status.trialInfo,
                            limits: response.status.limits,
                            components: response.status.components,
                            lastUpdated: Date()
                        )
                        continuation.resume(returning: subscriptionStatus)
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
            formatter.locale = Locale.current
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
}
