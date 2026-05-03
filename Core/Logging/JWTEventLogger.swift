//
//  JWTEventLogger.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2026 ALADDIN. All rights reserved.
//
//  🛡️ DEFENSIVE JWT ARCHITECTURE - Stage 2
//  Comprehensive event logging for JWT token lifecycle
//  Enables debugging and monitoring of token-related operations
//

import Foundation
import UIKit

/// 🛡️ JWTEventLogger - Comprehensive JWT Event Logging
///
/// Logs all JWT-related events for debugging and analytics.
/// Part of DEFENSIVE JWT Architecture for visibility into token lifecycle.
///
/// Events logged:
/// - Token validation results
/// - Device registration success/failure
/// - Token refresh operations
/// - Emergency re-registrations
/// - Offline mode activations
///
struct JWTEventLogger {

    /// Остаток до истечения токена для логов (секунды из `timeIntervalSinceNow`).
    static func describeTimeLeft(seconds: TimeInterval) -> String {
        let s = seconds
        guard s > 0 else { return "expired" }
        if s >= 86_400 {
            let d = Int(s / 86_400)
            let h = Int((s.truncatingRemainder(dividingBy: 86_400)) / 3600)
            return "\(d)d \(h)h"
        }
        if s >= 3600 {
            let h = Int(s / 3600)
            let m = Int((s.truncatingRemainder(dividingBy: 3600)) / 60)
            return "\(h)h \(m)m"
        }
        return "\(max(1, Int(s / 60)))m"
    }

    // MARK: - JWT Events

    /// 📊 JWT Event Types
    ///
    /// Comprehensive enumeration of all JWT-related events
    /// Used for logging, analytics, and debugging
    ///
    enum JWTEvent {
        // Token Validation Events
        case tokenValidated(isValid: Bool, timeToExpiry: TimeInterval, tokenStatus: String)

        // Device Registration Events
        case deviceRegistered(success: Bool, error: String?, deviceId: String)

        // Token Refresh Events
        case tokenRefreshAttempted(reason: String)
        case tokenRefreshed(success: Bool, error: String?, newExpiry: Date?)

        // Emergency Recovery Events
        case emergencyReRegistration(success: Bool, error: String?, reason: String)

        // Monitoring Events
        case healthCheckPerformed(tokenExists: Bool, timeToExpiry: TimeInterval?, nextCheckIn: TimeInterval)

        // Offline Mode Events
        case offlineModeActivated(reason: String, willRetry: Bool)

        // Circuit Breaker Events
        case circuitBreakerStateChanged(state: String, reason: String)

        // Error Recovery Events
        case errorRecoveryAttempted(strategy: String, success: Bool, error: String?)
    }

    // MARK: - Public Logging Methods

    /// 📝 Log JWT Event
    ///
    /// Logs JWT event with comprehensive context information.
    /// Includes device info, timestamp, and structured data for analysis.
    ///
    /// - Parameter event: The JWT event to log
    ///
    static func logEvent(_ event: JWTEvent) {
        let timestamp = Date()
        let deviceInfo = getDeviceInfo()
        let sessionId = getSessionId()

        // Create base log entry
        var logEntry = """
        📊 JWT EVENT [\(timestamp)]
        Device: \(deviceInfo)
        Session: \(sessionId)
        """

        // Add event-specific details
        switch event {
        case .tokenValidated(let isValid, let timeToExpiry, let tokenStatus):
            logEntry += """
            \n🔍 TOKEN VALIDATION
            Valid: \(isValid)
            Time to Expiry: \(Self.describeTimeLeft(seconds: timeToExpiry)) (~\(Int(timeToExpiry))s)
            Status: \(tokenStatus)
            """

        case .deviceRegistered(let success, let error, let deviceId):
            logEntry += """
            \n📱 DEVICE REGISTRATION
            Success: \(success)
            Device ID: \(deviceId)
            """
            if let error = error {
                logEntry += "Error: \(error)\n"
            }

        case .tokenRefreshAttempted(let reason):
            logEntry += """
            \n🔄 TOKEN REFRESH ATTEMPT
            Reason: \(reason)
            """

        case .tokenRefreshed(let success, let error, let newExpiry):
            logEntry += """
            \n✅ TOKEN REFRESH RESULT
            Success: \(success)
            """
            if let newExpiry = newExpiry {
                logEntry += "New Expiry: \(newExpiry)\n"
            }
            if let error = error {
                logEntry += "Error: \(error)\n"
            }

        case .emergencyReRegistration(let success, let error, let reason):
            logEntry += """
            \n🚨 EMERGENCY RE-REGISTRATION
            Success: \(success)
            Reason: \(reason)
            """
            if let error = error {
                logEntry += "Error: \(error)\n"
            }

        case .healthCheckPerformed(let tokenExists, let timeToExpiry, let nextCheckIn):
            logEntry += """
            \n🏥 HEALTH CHECK
            Token Exists: \(tokenExists)
            Next Check: \(Int(nextCheckIn)) seconds
            """
            if let timeToExpiry = timeToExpiry {
                logEntry += "\nTime to Expiry: \(Self.describeTimeLeft(seconds: timeToExpiry)) (~\(Int(timeToExpiry))s)\n"
            }

        case .offlineModeActivated(let reason, let willRetry):
            logEntry += """
            \n📴 OFFLINE MODE
            Reason: \(reason)
            Will Retry: \(willRetry)
            """

        case .circuitBreakerStateChanged(let state, let reason):
            logEntry += """
            \n🔌 CIRCUIT BREAKER
            New State: \(state)
            Reason: \(reason)
            """

        case .errorRecoveryAttempted(let strategy, let success, let error):
            logEntry += """
            \n🛠️ ERROR RECOVERY
            Strategy: \(strategy)
            Success: \(success)
            """
            if let error = error {
                logEntry += "Error: \(error)\n"
            }
        }

        // Log to different destinations
        logToConsole(logEntry)
        logToAnalytics(event)
        persistLogEntry(logEntry)
    }

    // MARK: - Convenience Methods

    /// 🔍 Log Token Validation Result
    static func logTokenValidation(isValid: Bool, timeToExpiry: TimeInterval, status: TokenValidator.TokenStatus) {
        logEvent(.tokenValidated(isValid: isValid, timeToExpiry: timeToExpiry, tokenStatus: status.description))
    }

    /// 📱 Log Device Registration
    static func logDeviceRegistration(success: Bool, error: String? = nil, deviceId: String) {
        logEvent(.deviceRegistered(success: success, error: error, deviceId: deviceId))
    }

    /// 🔄 Log Token Refresh
    static func logTokenRefresh(success: Bool, error: String? = nil, newExpiry: Date? = nil) {
        logEvent(.tokenRefreshed(success: success, error: error, newExpiry: newExpiry))
    }

    /// 🚨 Log Emergency Re-registration
    static func logEmergencyReRegistration(success: Bool, error: String? = nil, reason: String) {
        logEvent(.emergencyReRegistration(success: success, error: error, reason: reason))
    }

    /// 🏥 Log Health Check
    static func logHealthCheck(tokenExists: Bool, timeToExpiry: TimeInterval? = nil) {
        let nextCheckIn: TimeInterval = 60 // TokenHealthMonitor monitoring interval
        if let timeToExpiry = timeToExpiry {
            let minutes = Int(timeToExpiry / 60)
            // jwt_ttl_anomaly_count: detect obviously abnormal future expiry windows (clock/payload drift).
            if minutes > 60 * 24 * 370 {
                incrementCounter("jwt_ttl_anomaly_count")
            }
        }
        logEvent(.healthCheckPerformed(tokenExists: tokenExists, timeToExpiry: timeToExpiry, nextCheckIn: nextCheckIn))
    }

    /// 📴 Log Offline Mode
    static func logOfflineMode(reason: String, willRetry: Bool = true) {
        logEvent(.offlineModeActivated(reason: reason, willRetry: willRetry))
    }

    // MARK: - Private Helper Methods

    /// 📱 Get Device Information
    private static func getDeviceInfo() -> String {
        let device = UIDevice.current
        return "\(device.model) (\(device.systemVersion))"
    }

    /// 🔢 Get Session ID
    private static func getSessionId() -> String {
        // Generate or retrieve session ID
        if let sessionId = UserDefaults.standard.string(forKey: "jwt_session_id") {
            return sessionId
        } else {
            let newSessionId = UUID().uuidString
            UserDefaults.standard.set(newSessionId, forKey: "jwt_session_id")
            return newSessionId
        }
    }

    /// 📝 Log to Console
    private static func logToConsole(_ entry: String) {
        let logger = MasterLogger.shared
        logger.business(entry)
    }

    /// 📊 Log to Analytics
    private static func logToAnalytics(_ event: JWTEvent) {
        // TODO: Integrate with analytics service when available
        // For now, just log that analytics integration is pending
        let logger = MasterLogger.shared
        logger.business("📊 JWT Event sent to analytics: \(event)")
    }

    /// 💾 Persist Log Entry
    private static func persistLogEntry(_ entry: String) {
        // TODO: Implement persistent logging to file/database when needed
        // For now, entries are kept in memory via MasterLogger
    }

    // MARK: - Observability Counters

    /// Increments lightweight local counter for operational anomaly signals.
    static func incrementCounter(_ key: String) {
        let storageKey = "obs_\(key)"
        let current = UserDefaults.standard.integer(forKey: storageKey)
        UserDefaults.standard.set(current + 1, forKey: storageKey)
        let logger = MasterLogger.shared
        logger.business("📈 OBS Counter \(key)=\(current + 1)")

        // Emit operational alert into analytics/metrics pipeline for observability.
        let alert = Alert(
            id: "jwt_obs_\(key)_\(Int(Date().timeIntervalSince1970))",
            type: .security,
            message: "OBS counter '\(key)' incremented to \(current + 1)",
            severity: .warning,
            timestamp: Date()
        )
        let analytics = RemoteAnalyticsService()
        analytics.trackAlert(alert: alert)
    }
}
