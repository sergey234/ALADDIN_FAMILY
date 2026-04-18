//
//  TokenHealthMonitor.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2026 ALADDIN. All rights reserved.
//
//  🛡️ DEFENSIVE JWT ARCHITECTURE - Stage 2
//  Proactive monitoring system for JWT token health
//  Prevents token expiry issues before they affect users
//

import Foundation
import UIKit

// ✅ Typealias для явного указания структуры JWTPayload из APIModels.swift
// Это предотвращает конфликт с private struct JWTPayload в SubscriptionManager.swift
typealias APIJWTPayload = JWTPayload

/// 🛡️ TokenHealthMonitor - DEFENSIVE JWT Proactive Monitoring
///
/// Monitors JWT token health proactively to prevent expiry-related issues.
/// Part of DEFENSIVE JWT Architecture for seamless token lifecycle management.
/// Prevents 401 errors and ensures continuous API availability.
///
/// Key Features:
/// - Continuous monitoring every 60 seconds
/// - Proactive refresh 5 minutes before expiry
/// - Emergency re-registration for expired tokens
/// - Comprehensive logging for debugging
///
class TokenHealthMonitor {

    // MARK: - Properties

    /// Timer for periodic health checks
    private var monitoringTimer: Timer?

    /// Monitoring interval: check every 60 seconds
    private let monitoringInterval: TimeInterval = 60

    /// Runtime threshold for proactive refresh: refresh when < 5 minutes remain.
    /// Note: policy-level warning/critical windows (7d/24h) are tracked via observability,
    /// while this tighter runtime threshold protects UX from token-expiry interruptions.
    private let refreshThreshold: TimeInterval = 300

    /// Logger instance
    private let logger = MasterLogger.shared

    /// Singleton instance
    static let shared = TokenHealthMonitor()

    // MARK: - Initialization

    /// Private initializer for singleton
    private init() {
        logger.business("🏥 DEFENSIVE JWT: TokenHealthMonitor singleton initialized")
    }

    /// Start proactive monitoring
    func startMonitoring() {
        logger.business("👀 DEFENSIVE JWT: Starting proactive token health monitoring")

        // Cancel existing timer if any
        stopMonitoring()

        // Create new timer on main thread
        DispatchQueue.main.async { [weak self] in
            guard let strongSelf = self else { return }

            strongSelf.monitoringTimer = Timer.scheduledTimer(
                withTimeInterval: strongSelf.monitoringInterval,
                repeats: true
            ) { [weak self] _ in
                guard let self = self else { return }
                Task { await self.checkTokenHealth() }
            }

            strongSelf.logger.business("✅ DEFENSIVE JWT: Health monitoring started - checking every \(Int(strongSelf.monitoringInterval)) seconds")
        }
    }

    /// Stop monitoring
    func stopMonitoring() {
        // Avoid noisy stop/start logs when no timer is running.
        guard monitoringTimer != nil else { return }

        logger.business("⏹️ DEFENSIVE JWT: Stopping token health monitoring")
        monitoringTimer?.invalidate()
        monitoringTimer = nil
        logger.business("✅ DEFENSIVE JWT: Health monitoring stopped")
    }

    // MARK: - Health Check Logic

    /// 🔍 Check token health - Core monitoring logic
    ///
    /// Performs comprehensive token health analysis:
    /// 1. Checks token existence
    /// 2. Analyzes time to expiry
    /// 3. Triggers appropriate actions based on token state
    /// 4. Logs all events via JWTEventLogger
    ///
    private func checkTokenHealth() async {
        logger.business("🔍 DEFENSIVE JWT: Performing token health check")

        let tokenExists = await SubscriptionManager.shared.currentToken != nil
        let timeToExpiry = await SubscriptionManager.shared.currentToken?.expiresAt.timeIntervalSinceNow

        // Log health check event
        JWTEventLogger.logHealthCheck(tokenExists: tokenExists, timeToExpiry: timeToExpiry)

        guard let token = await SubscriptionManager.shared.currentToken else {
            logger.business("📱 DEFENSIVE JWT: No token found - monitoring continues")
            return
        }

        let timeToExpiryValue = token.expiresAt.timeIntervalSinceNow
        logger.business("⏰ DEFENSIVE JWT: Token health check - \(Int(timeToExpiryValue/60)) minutes until expiry")

        // Decision tree based on token state
        if timeToExpiryValue < 0 {
            // CRITICAL: Token has expired
            logger.error("🚨 DEFENSIVE JWT: CRITICAL - Token has expired (\(Int(abs(timeToExpiryValue)/60)) minutes ago)")
            await performEmergencyReRegistration()
            return

        } else if timeToExpiryValue < refreshThreshold {
            // WARNING: Token expiring soon - proactive refresh
            logger.business("⚠️ DEFENSIVE JWT: WARNING - Token expires soon (\(Int(timeToExpiryValue/60)) min) - triggering proactive refresh")

            // Log refresh attempt
            JWTEventLogger.logEvent(.tokenRefreshAttempted(reason: "Token expiring soon"))

            await performProactiveRefresh()
            return

        } else {
            // HEALTHY: Token is fine
            logger.business("✅ DEFENSIVE JWT: Token is healthy - next check in \(Int(monitoringInterval)) seconds")
            return
        }
    }

    // MARK: - Helper Methods
    
    /// 🔍 Extract subscription information from JWT token
    ///
    /// Decodes JWT payload and extracts subscription level, trial info, limits, and components.
    /// Returns nil if JWT cannot be decoded or subscription info is missing.
    ///
    private func extractSubscriptionFromJWT(_ token: String) -> (SubscriptionLevel, TrialInfo?, SubscriptionLimits, [String])? {
        logger.business("🔍 DEFENSIVE JWT: Декодирование JWT для извлечения тарифа")
        
        // Split JWT token into parts
        let parts = token.split(separator: ".")
        guard parts.count == 3 else {
            logger.business("⚠️ DEFENSIVE JWT: Неверный формат JWT (не 3 части)")
            return nil
        }
        
        // Decode payload (base64)
        guard let payloadData = Data(base64Encoded: String(parts[1]), options: .ignoreUnknownCharacters) else {
            logger.business("⚠️ DEFENSIVE JWT: Не удалось декодировать base64 payload")
            return nil
        }
        
        // Parse JSON payload
        // ✅ Используем APIJWTPayload (typealias для JWTPayload из APIModels.swift)
        // Это предотвращает конфликт с private struct JWTPayload в SubscriptionManager.swift
        guard let payload = try? JSONDecoder().decode(APIJWTPayload.self, from: payloadData) else {
            logger.business("⚠️ DEFENSIVE JWT: Не удалось декодировать JWT payload")
            return nil
        }
        
        // Extract subscription information
        guard let subscription = payload.subscription else {
            logger.business("⚠️ DEFENSIVE JWT: Subscription информация отсутствует в JWT")
            return nil
        }
        
        let subscriptionLevel = SubscriptionLevel.fromAPIPlanString(subscription.level)
        let trialInfo = subscription.trial_info
        let limits = subscription.limits?.toSubscriptionLimits() ?? SubscriptionLimits.freeLimits
        let components = subscription.components ?? []
        
        logger.business("✅ DEFENSIVE JWT: Тариф извлечен из JWT: \(subscriptionLevel)")
        
        return (subscriptionLevel, trialInfo, limits, components)
    }
    
    /// 📡 Fetch subscription status from server
    ///
    /// Requests current subscription status from server as fallback when JWT doesn't contain subscription info.
    ///
    private func fetchSubscriptionFromServer() async {
        logger.business("🔄 DEFENSIVE JWT: Запрос тарифа с сервера")
        
        // Get current token to extract userId
        guard let currentToken = await SubscriptionManager.shared.currentToken else {
            logger.business("⚠️ DEFENSIVE JWT: Токен отсутствует, невозможно запросить тариф")
            return
        }
        
        // Extract userId from deviceId (or use deviceId as userId for device-based auth)
        let userId = currentToken.deviceId
        let merge = await MainActor.run { SubscriptionManager.shared.currentSubscription }

        return await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            APIService.shared.getSubscriptionStatus(userId: userId, merging: merge) { result in
                switch result {
                case .success(let updatedStatus):
                    Task { @MainActor in
                        await SubscriptionManager.shared.applySubscriptionPayloadFromServer(updatedStatus)
                        self.logger.business("✅ DEFENSIVE JWT: Тариф обновлен с сервера: \(updatedStatus.level), isActive: \(updatedStatus.isActive)")
                        continuation.resume()
                    }
                case .failure(let error):
                    self.logger.error("❌ DEFENSIVE JWT: Ошибка запроса тарифа: \(error)")
                    // Use current subscription from SubscriptionManager as fallback
                    self.logger.business("⚠️ DEFENSIVE JWT: Используем текущий тариф из локального хранилища")
                    continuation.resume()
                }
            }
        }
    }
    
    /// 🔄 Refresh token with retry logic
    ///
    /// Attempts to refresh token using refresh_token with error handling.
    /// Returns RefreshTokenResponse or throws error.
    ///
    private func refreshTokenWithRetry(refreshToken: String, attempt: Int) async throws -> RefreshTokenResponse {
        logger.business("🔄 DEFENSIVE JWT: Попытка \(attempt): обновление через refresh_token")
        
        return try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<RefreshTokenResponse, Error>) in
            APIService.shared.refreshToken(refreshToken: refreshToken) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    /// 💾 Save new token with subscription synchronization
    ///
    /// Saves new access token to AppConfig, Keychain, and SubscriptionManager.
    /// Extracts subscription information from JWT and synchronizes with server if needed.
    ///
    private func saveNewToken(_ response: RefreshTokenResponse) async {
        logger.business("💾 DEFENSIVE JWT: Сохранение нового токена с согласованием тарифов")
        
        // 1. Save access_token to AppConfig (for all API requests)
        AppConfig.authToken = response.access_token
        logger.business("✅ DEFENSIVE JWT: Access token сохранен в AppConfig.authToken")
        
        // 2. Save refresh_token to Keychain (if received)
        if let newRefreshToken = response.refresh_token, !newRefreshToken.isEmpty {
            KeychainManager.shared.save(newRefreshToken, forKey: .refreshToken)
            logger.business("✅ DEFENSIVE JWT: Refresh token сохранен в Keychain")
        }
        
        // 3. SUBSCRIPTION SYNC: Decode JWT and extract subscription info
        if let (subscriptionLevel, trialInfo, limits, components) = extractSubscriptionFromJWT(response.access_token) {
            // ✅ Subscription found in JWT - save it
            let expiresAt = Date().addingTimeInterval(response.expires_in ?? 86400) // 24 hours default
            let currentToken = await SubscriptionManager.shared.currentToken
            
            // ✅ ИСПРАВЛЕНО: Получаем deviceId безопасным способом
            // Приоритет 1: Используем deviceId из текущего токена
            let deviceId: String
            if let existingDeviceId = currentToken?.deviceId, !existingDeviceId.isEmpty {
                deviceId = existingDeviceId
            } else {
                // Приоритет 2: Используем identifierForVendor (требует MainActor)
                // Приоритет 3: Генерируем новый UUID
                deviceId = await MainActor.run {
                    UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
                }
            }
            
            let jwtToken = JWTToken(
                token: response.access_token,
                deviceId: deviceId,
                subscriptionLevel: subscriptionLevel,  // ✅ Save subscription level
                trialInfo: trialInfo,                  // ✅ Save trial info
                expiresAt: expiresAt,
                issuedAt: Date(),
                issuer: currentToken?.issuer ?? "aladdin_server",
                limits: limits,                        // ✅ Save limits
                components: components                 // ✅ Save components
            )
            
            await SubscriptionManager.shared.storeToken(jwtToken)
            logger.business("✅ DEFENSIVE JWT: Токен сохранен с тарифом: \(subscriptionLevel)")
        } else {
            // ⚠️ Subscription not found in JWT - request from server
            logger.business("⚠️ DEFENSIVE JWT: Тариф не найден в JWT, запрашиваем с сервера")
            await fetchSubscriptionFromServer()
        }
        
        // 4. Restart monitoring for new token
        TokenHealthMonitor.shared.startMonitoring()
        logger.business("✅ DEFENSIVE JWT: Мониторинг перезапущен")
    }

    // MARK: - Recovery Actions

    /// 🚑 Emergency re-registration for expired tokens
    ///
    /// Handles critical situation when token has already expired.
    /// Clears expired token and performs device re-registration.
    /// Preserves subscription information to prevent loss of paid plans.
    ///
    private func performEmergencyReRegistration() async {
        let reason = "Token has expired"
        logger.business("🚑 DEFENSIVE JWT: Executing emergency re-registration with subscription preservation")
        
        // 1. Save current subscription BEFORE re-registration
        let currentLevel = await SubscriptionManager.shared.getCurrentLevel()
        let currentTrial = await SubscriptionManager.shared.trialStatus
        logger.business("💾 DEFENSIVE JWT: Текущий тариф сохранен: \(currentLevel)")

        do {
            // Clear the expired token first
            await SubscriptionManager.shared.clearToken()
            logger.business("🧹 DEFENSIVE JWT: Cleared expired token")

            // Perform device re-registration
            let newToken = try await SubscriptionManager.shared.registerDeviceAnonymously()
            logger.business("✅ DEFENSIVE JWT: Emergency re-registration successful")
            
            // 2. Check if subscription was preserved
            let newLevel = await SubscriptionManager.shared.getCurrentLevel()
            
            if newLevel != currentLevel && currentLevel != .free {
                // ⚠️ Subscription changed - request from server
                logger.business("⚠️ DEFENSIVE JWT: Тариф изменился после перерегистрации (\(currentLevel) → \(newLevel))")
                logger.business("🔄 DEFENSIVE JWT: Запрашиваем тариф с сервера для восстановления")
                await fetchSubscriptionFromServer()
            } else {
                logger.business("✅ DEFENSIVE JWT: Тариф сохранен: \(currentLevel)")
            }
            
            // 3. Save token to AppConfig
            AppConfig.authToken = newToken.token
            logger.business("✅ DEFENSIVE JWT: Токен сохранен в AppConfig.authToken")
            
            // 4. Restart monitoring
            TokenHealthMonitor.shared.startMonitoring()
            logger.business("✅ DEFENSIVE JWT: Мониторинг перезапущен")

            // Log successful recovery
            JWTEventLogger.logEmergencyReRegistration(success: true, error: nil, reason: reason)

        } catch {
            logger.error("❌ DEFENSIVE JWT: Emergency re-registration failed: \(error)")
            logger.business("🔄 DEFENSIVE JWT: Entering offline mode due to registration failure")

            // Log failed recovery
            JWTEventLogger.logEmergencyReRegistration(success: false, error: error.localizedDescription, reason: reason)

            // Enter offline mode as last resort
            // Note: isOfflineMode is private(set), logging the event for external handling
            logger.business("📴 DEFENSIVE JWT: Emergency re-registration failed - offline mode recommended")
            JWTEventLogger.logOfflineMode(reason: "Emergency re-registration failed", willRetry: true)
        }
    }

    /// 🔄 Proactive token refresh before expiry
    ///
    /// Performs silent token refresh when token is close to expiry.
    /// Uses smart hybrid approach: refreshToken with retry → fallback to device re-registration.
    /// Prevents user-facing errors and maintains seamless experience.
    ///
    private func performProactiveRefresh() async {
        logger.business("🔄 DEFENSIVE JWT: Executing smart hybrid token refresh")

        // STEP 1: Try refreshToken() with retry
        if let refreshToken = KeychainManager.shared.loadString(forKey: .refreshToken),
           !refreshToken.isEmpty {
            logger.business("🔄 DEFENSIVE JWT: Refresh token найден, пробуем обновление")
            
            // Attempt 1
            do {
                let response = try await refreshTokenWithRetry(refreshToken: refreshToken, attempt: 1)
                await saveNewToken(response)
                logger.business("✅ DEFENSIVE JWT: Токен успешно обновлен через refresh_token (попытка 1)")
                return // Success!
            } catch {
                logger.business("⚠️ DEFENSIVE JWT: Попытка 1 не удалась: \(error.localizedDescription)")
                logger.business("🔄 DEFENSIVE JWT: Выполняем retry (попытка 2) через 2 секунды...")
                
                // Attempt 2 (retry with delay)
                do {
                    try await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
                    let response = try await refreshTokenWithRetry(refreshToken: refreshToken, attempt: 2)
                    await saveNewToken(response)
                    logger.business("✅ DEFENSIVE JWT: Токен успешно обновлен через refresh_token (попытка 2)")
                    return // Success!
                } catch {
                    logger.business("⚠️ DEFENSIVE JWT: Попытка 2 не удалась: \(error.localizedDescription)")
                    logger.business("🔄 DEFENSIVE JWT: Обе попытки не удались, используем fallback")
                }
            }
        } else {
            logger.business("⚠️ DEFENSIVE JWT: Refresh token не найден, используем fallback")
        }
        
        // STEP 2: Fallback - registerDeviceAnonymously()
        logger.business("🔄 DEFENSIVE JWT: Используем перерегистрацию устройства как fallback")
        await performEmergencyReRegistration()
    }

    // MARK: - Status Reporting

    /// 📊 Get monitoring status
    ///
    /// Returns current monitoring state for debugging and analytics.
    ///
    func getMonitoringStatus() async -> [String: Any] {
        let isMonitoring = monitoringTimer?.isValid ?? false
        let nextCheckIn = monitoringTimer?.fireDate.timeIntervalSinceNow ?? 0

        return [
            "isMonitoring": isMonitoring,
            "monitoringInterval": monitoringInterval,
            "refreshThreshold": refreshThreshold,
            "nextCheckIn": Int(nextCheckIn),
            "hasToken": await SubscriptionManager.shared.currentToken != nil
        ]
    }
}