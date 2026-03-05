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

    /// Refresh threshold: refresh when < 5 minutes remain
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

    // MARK: - Recovery Actions

    /// 🚑 Emergency re-registration for expired tokens
    ///
    /// Handles critical situation when token has already expired.
    /// Clears expired token and performs device re-registration.
    ///
    private func performEmergencyReRegistration() async {
        let reason = "Token has expired"
        logger.business("🚑 DEFENSIVE JWT: Executing emergency re-registration")

        do {
            // Clear the expired token first
            await SubscriptionManager.shared.clearToken()
            logger.business("🧹 DEFENSIVE JWT: Cleared expired token")

            // Perform device re-registration
            try await await SubscriptionManager.shared.registerDeviceAnonymously()
            logger.business("✅ DEFENSIVE JWT: Emergency re-registration successful")

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
    /// Prevents user-facing errors and maintains seamless experience.
    ///
    private func performProactiveRefresh() async {
        logger.business("🔄 DEFENSIVE JWT: Executing proactive token refresh")

        // For now, use device re-registration as refresh mechanism
        // TODO: Implement proper refresh token endpoint when available
        logger.business("🔄 DEFENSIVE JWT: Using device re-registration as refresh mechanism")

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