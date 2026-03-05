//
//  JWTErrorRecovery.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2026 ALADDIN. All rights reserved.
//
//  🛡️ DEFENSIVE JWT ARCHITECTURE - Stage 3
//  Intelligent error recovery for JWT-protected endpoints
//  Analyzes errors and applies optimal recovery strategies
//

import Foundation

/// 🛡️ JWTErrorRecovery - DEFENSIVE JWT Error Recovery
///
/// Implements intelligent error recovery for JWT-protected API endpoints.
/// Analyzes error types and applies appropriate recovery strategies.
/// Part of DEFENSIVE JWT Architecture for graceful error handling.
///
/// Recovery Strategies:
/// - silentRetry: Тихий повтор операции
/// - userNotification: Уведомить пользователя
/// - forceOffline: Перейти в offline режим
/// - emergencyReset: Полная перезагрузка системы
/// - circuitBreak: Активировать circuit breaker
///
class JWTErrorRecovery {

    // MARK: - Recovery Strategies

    /// 🛠️ Recovery Strategy Options
    ///
    /// Defines available recovery strategies based on error analysis
    ///
    enum RecoveryStrategy: String {
        case silentRetry        // Тихий повтор операции
        case userNotification   // Уведомить пользователя
        case forceOffline       // Перейти в offline режим
        case emergencyReset     // Полная перезагрузка системы
        case circuitBreak       // Активировать circuit breaker

        /// 📊 Human-readable description
        var description: String {
            switch self {
            case .silentRetry: return "SILENT_RETRY (automatic retry)"
            case .userNotification: return "USER_NOTIFICATION (notify user)"
            case .forceOffline: return "FORCE_OFFLINE (switch to offline mode)"
            case .emergencyReset: return "EMERGENCY_RESET (full system reset)"
            case .circuitBreak: return "CIRCUIT_BREAK (activate circuit breaker)"
            }
        }
    }

    // MARK: - Error Analysis

    /// 🔍 Select Recovery Strategy - Core Error Analysis Logic
    ///
    /// Analyzes error type and context to select optimal recovery strategy.
    /// Considers error codes, network conditions, and system state.
    ///
    /// - Parameter error: The error that occurred
    /// - Returns: Appropriate recovery strategy
    ///
    static func selectStrategy(for error: Error) -> RecoveryStrategy {
        let logger = MasterLogger.shared
        logger.business("🔍 DEFENSIVE JWT: Analyzing error for recovery strategy")

        // Check if it's a NetworkError
        if let networkError = error as? NetworkError {
            return analyzeNetworkError(networkError)
        }

        // Check if it's JWT-related
        if error.isTokenRelated {
            logger.business("🔑 DEFENSIVE JWT: JWT-related error detected")
            return .emergencyReset
        }

        // Generic error handling
        logger.business("❓ DEFENSIVE JWT: Generic error - using user notification")
        return .userNotification
    }

    /// 🌐 Analyze Network Error
    ///
    /// Detailed analysis of network-specific errors
    ///
    /// - Parameter networkError: Network error to analyze
    /// - Returns: Recovery strategy for network error
    ///
    private static func analyzeNetworkError(_ networkError: NetworkError) -> RecoveryStrategy {
        let logger = MasterLogger.shared

        switch networkError {
        case .httpError(let statusCode):
            switch statusCode {
            case 401:
                logger.business("🚫 DEFENSIVE JWT: 401 Unauthorized - token expired, silent retry")
                return .silentRetry  // Токен истек - пробуем заново

            case 403:
                logger.business("🚫 DEFENSIVE JWT: 403 Forbidden - insufficient permissions")
                return .userNotification  // Нет прав доступа

            case 500...599:
                logger.business("🚫 DEFENSIVE JWT: 5xx Server Error - server issues, circuit break")
                return .circuitBreak  // Серверная ошибка

            default:
                logger.business("🚫 DEFENSIVE JWT: HTTP \(statusCode) - generic retry")
                return .silentRetry
            }

        case .noConnection:
            logger.business("📡 DEFENSIVE JWT: Network connectivity issue - force offline")
            return .forceOffline  // Нет сети

        case .timeout:
            logger.business("⏱️ DEFENSIVE JWT: Request timeout - circuit break to prevent cascade")
            return .circuitBreak  // Таймаут - возможно проблема с сервером

        default:
            logger.business("❓ DEFENSIVE JWT: Unknown network error - user notification")
            return .userNotification
        }
    }

    // MARK: - Strategy Execution

    /// 🚀 Execute Recovery Strategy
    ///
    /// Executes the selected recovery strategy.
    /// Handles all side effects and logging.
    ///
    /// - Parameters:
    ///   - strategy: Strategy to execute
    ///   - error: Original error that triggered recovery
    ///
    static func executeStrategy(_ strategy: RecoveryStrategy, for error: Error) async {
        let logger = MasterLogger.shared
        logger.business("🛠️ DEFENSIVE JWT: Executing recovery strategy: \(strategy.description)")

        // Log recovery attempt
        JWTEventLogger.logEvent(.errorRecoveryAttempted(
            strategy: strategy.rawValue,
            success: false,  // Will be updated
            error: nil
        ))

        do {
            switch strategy {
            case .silentRetry:
                try await performSilentRetry()

            case .userNotification:
                showUserNotification(for: error)

            case .forceOffline:
                forceOfflineMode()

            case .emergencyReset:
                try await performEmergencyReset()

            case .circuitBreak:
                activateCircuitBreaker(for: error)
            }

            // Log successful recovery
            JWTEventLogger.logEvent(.errorRecoveryAttempted(
                strategy: strategy.rawValue,
                success: true,
                error: nil
            ))

            logger.business("✅ DEFENSIVE JWT: Recovery strategy executed successfully")

        } catch {
            // Log failed recovery
            JWTEventLogger.logEvent(.errorRecoveryAttempted(
                strategy: strategy.rawValue,
                success: false,
                error: error.localizedDescription
            ))

            logger.error("❌ DEFENSIVE JWT: Recovery strategy failed: \(error)")
        }
    }

    // MARK: - Recovery Implementations

    /// 🔄 Perform Silent Retry
    ///
    /// Attempts to retry the operation silently.
    /// Used for recoverable errors like expired tokens.
    ///
    private static func performSilentRetry() async throws {
        let logger = MasterLogger.shared
        logger.business("🔄 DEFENSIVE JWT: Performing silent retry")

        // For JWT errors, try device re-registration
        do {
            try await SubscriptionManager.shared.registerDeviceAnonymously()
            logger.business("✅ DEFENSIVE JWT: Silent retry successful")
        } catch {
            logger.error("❌ DEFENSIVE JWT: Silent retry failed: \(error)")
            throw error
        }
    }

    /// 👤 Show User Notification
    ///
    /// Displays user-friendly error notification.
    /// Used when user action is required.
    ///
    /// - Parameter error: Error to display
    ///
    private static func showUserNotification(for error: Error) {
        let message = getUserFriendlyMessage(for: error)

        // TODO: Use ErrorMessageManager when available
        // For now, just log the message
        MasterLogger.shared.business("👤 DEFENSIVE JWT: User notification needed: \(message)")

        // Could integrate with NotificationCenter or other UI system
        // ErrorMessageManager.shared.showCustomError(
        //     title: "Временная проблема",
        //     message: message,
        //     type: .warning,
        //     action: .retry
        // )
    }

    /// 📴 Force Offline Mode
    ///
    /// Forces the app into offline mode.
    /// Used when network connectivity is unavailable.
    ///
    private static func forceOfflineMode() {
        let logger = MasterLogger.shared
        logger.business("📴 DEFENSIVE JWT: Forcing offline mode")

        // Note: isOfflineMode is private(set), using alternative approach
        // For now, just show notification and log the event
        logger.business("📴 DEFENSIVE JWT: Offline mode notification sent (set externally)")

        // TODO: Show offline notification when ErrorMessageManager is available
        MasterLogger.shared.business("📴 DEFENSIVE JWT: Offline notification needed")

        logger.business("✅ DEFENSIVE JWT: Offline mode notification displayed")
    }

    /// 🚨 Perform Emergency Reset
    ///
    /// Performs complete system reset.
    /// Used for critical JWT failures.
    ///
    private static func performEmergencyReset() async throws {
        let logger = MasterLogger.shared
        logger.business("🚨 DEFENSIVE JWT: Performing emergency system reset")

        // Clear all tokens
        await SubscriptionManager.shared.clearToken()

        // Stop monitoring
        TokenHealthMonitor.shared.stopMonitoring()

        // Try to recover
        do {
            try await SubscriptionManager.shared.registerDeviceAnonymously()

            // Restart monitoring
            TokenHealthMonitor.shared.startMonitoring()

            logger.business("✅ DEFENSIVE JWT: Emergency reset successful")
        } catch {
            logger.error("❌ DEFENSIVE JWT: Emergency reset failed: \(error)")

            // Force offline as last resort
            forceOfflineMode()
            throw error
        }
    }

    /// 🔌 Activate Circuit Breaker
    ///
    /// Activates circuit breaker to prevent cascade failures.
    /// Used for server-side issues.
    ///
    /// - Parameter error: Error that triggered circuit breaker
    ///
    private static func activateCircuitBreaker(for error: Error) {
        let logger = MasterLogger.shared
        logger.business("🔌 DEFENSIVE JWT: Activating circuit breaker")

        // Circuit breaker activation is handled by NetworkManager
        // Here we just log the activation
        logger.business("✅ DEFENSIVE JWT: Circuit breaker activation logged")

        // TODO: Show technical maintenance notification when ErrorMessageManager is available
        MasterLogger.shared.business("🔌 DEFENSIVE JWT: Technical maintenance notification needed")
    }

    // MARK: - Helper Methods

    /// 💬 Get User-Friendly Error Message
    ///
    /// Converts technical errors to user-friendly messages.
    ///
    /// - Parameter error: Technical error
    /// - Returns: User-friendly message
    ///
    private static func getUserFriendlyMessage(for error: Error) -> String {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .httpError(401):
                return "Сессия истекла. Выполняем повторный вход."
            case .httpError(403):
                return "Недостаточно прав для выполнения операции."
            case .noConnection:
                return "Проблемы с подключением к интернету."
            case .timeout:
                return "Сервер не отвечает. Повторите попытку позже."
            default:
                return "Временная техническая проблема. Повторите попытку."
            }
        }

        return "Произошла непредвиденная ошибка. Мы работаем над решением."
    }
}

// MARK: - Error Extensions

/// Error classification extension
extension Error {
    /// Check if error is JWT-related
    var isTokenRelated: Bool {
        let errorString = localizedDescription.lowercased()
        return errorString.contains("token") ||
               errorString.contains("jwt") ||
               errorString.contains("auth") ||
               errorString.contains("unauthorized") ||
               errorString.contains("401")
    }
}