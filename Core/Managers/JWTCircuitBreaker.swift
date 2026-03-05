//
//  JWTCircuitBreaker.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2026 ALADDIN. All rights reserved.
//
//  🛡️ DEFENSIVE JWT ARCHITECTURE - Stage 3
//  Circuit breaker pattern for JWT-protected endpoints
//  Prevents cascade failures and ensures system resilience
//

import Foundation

/// 🛡️ JWTCircuitBreaker - DEFENSIVE JWT Circuit Breaker
///
/// Implements Circuit Breaker pattern for JWT-protected API endpoints.
/// Prevents cascade failures when server is experiencing issues.
/// Part of DEFENSIVE JWT Architecture for high availability.
///
/// States:
/// - Closed: Normal operation, requests allowed
/// - Open: Failure threshold exceeded, requests blocked
/// - Half-Open: Testing recovery, limited requests allowed
///
class JWTCircuitBreaker {

    // MARK: - Circuit States

    /// 🔄 Circuit Breaker States
    ///
    /// Defines the three states of circuit breaker operation
    ///
    enum CircuitState: String {
        case closed      // Всё работает нормально - запросы разрешены
        case open        // Срабатывает защита - блокируем запросы
        case halfOpen    // Проверяем восстановление - пробуем запросы

        /// 📊 Human-readable description
        var description: String {
            switch self {
            case .closed: return "CLOSED (normal operation)"
            case .open: return "OPEN (protecting from failures)"
            case .halfOpen: return "HALF-OPEN (testing recovery)"
            }
        }
    }

    // MARK: - Properties

    /// Current circuit state
    private var state: CircuitState = .closed

    /// Number of consecutive failures
    private var failureCount = 0

    /// Timestamp of last failure
    private var lastFailureTime: Date?

    /// Number of failures before opening circuit
    private let failureThreshold = 3

    /// Time to wait before attempting recovery (5 minutes)
    private let timeout: TimeInterval = 300

    /// Number of successes needed to close circuit from half-open
    private let successThreshold = 2

    /// Success count in half-open state
    private var halfOpenSuccessCount = 0

    /// Logger instance
    private let logger = MasterLogger.shared

    /// Singleton instance
    static let shared = JWTCircuitBreaker()

    // MARK: - Initialization

    /// Private initializer for singleton
    private init() {
        logger.business("🔌 DEFENSIVE JWT: JWTCircuitBreaker initialized - \(state.description)")
    }

    // MARK: - Public Methods

    /// 🔍 Should Allow Request - Core Circuit Breaker Logic
    ///
    /// Determines if API request should be allowed based on circuit state.
    /// Implements the circuit breaker pattern to prevent cascade failures.
    ///
    /// - Returns: true if request should proceed, false if blocked
    ///
    func shouldAllowRequest() -> Bool {
        switch state {
        case .closed:
            // Normal operation - allow all requests
            return true

        case .open:
            // Check if timeout has passed - attempt recovery
            if let lastFailure = lastFailureTime,
               Date().timeIntervalSince(lastFailure) > timeout {

                // Transition to half-open for testing
                state = .halfOpen
                halfOpenSuccessCount = 0
                logger.business("🔄 DEFENSIVE JWT: Circuit Breaker → HALF-OPEN (testing recovery after \(Int(timeout/60))min)")

                // Log state change
                JWTEventLogger.logEvent(.circuitBreakerStateChanged(
                    state: CircuitState.halfOpen.rawValue,
                    reason: "Timeout expired, testing recovery"
                ))

                return true
            }

            // Still in open state - block requests
            logger.business("🚫 DEFENSIVE JWT: Circuit Breaker OPEN - blocking request")
            return false

        case .halfOpen:
            // Allow limited requests for testing
            return true
        }
    }

    /// ✅ Record Success - Update circuit state on successful request
    ///
    /// Records successful API request and updates circuit breaker state.
    /// Transitions from half-open to closed when success threshold is reached.
    ///
    func recordSuccess() {
        failureCount = 0  // Reset failure count

        switch state {
        case .halfOpen:
            halfOpenSuccessCount += 1
            logger.business("✅ DEFENSIVE JWT: Success in HALF-OPEN state (\(halfOpenSuccessCount)/\(successThreshold))")

            if halfOpenSuccessCount >= successThreshold {
                // Recovery successful - close circuit
                state = .closed
                logger.business("🎉 DEFENSIVE JWT: Circuit Breaker → CLOSED (system recovered)")

                // Log state change
                JWTEventLogger.logEvent(.circuitBreakerStateChanged(
                    state: CircuitState.closed.rawValue,
                    reason: "Recovery successful"
                ))
            }

        case .closed:
            // Normal operation - stay closed
            break

        case .open:
            // Unexpected success in open state - log but don't change
            logger.business("⚠️ DEFENSIVE JWT: Unexpected success in OPEN state")
            break
        }
    }

    /// ❌ Record Failure - Update circuit state on failed request
    ///
    /// Records failed API request and updates circuit breaker state.
    /// Transitions to open state when failure threshold is exceeded.
    ///
    func recordFailure() {
        failureCount += 1
        lastFailureTime = Date()

        logger.business("❌ DEFENSIVE JWT: Circuit Breaker failure #\(failureCount)")

        if failureCount >= failureThreshold {
            // Too many failures - open circuit
            state = .open
            logger.error("🚨 DEFENSIVE JWT: Circuit Breaker → OPEN (too many failures: \(failureCount))")

            // Log state change
            JWTEventLogger.logEvent(.circuitBreakerStateChanged(
                state: CircuitState.open.rawValue,
                reason: "Failure threshold exceeded: \(failureCount) failures"
            ))
        }
    }

    /// 📊 Get State Description - For debugging and monitoring
    ///
    /// Returns detailed description of current circuit breaker state.
    /// Includes failure counts, timeouts, and recovery status.
    ///
    /// - Returns: Human-readable status description
    ///
    func getStateDescription() -> String {
        var description = "Circuit Breaker: \(state.description.uppercased())"

        switch state {
        case .closed:
            description += " | Failures: \(failureCount)/\(failureThreshold)"

        case .open:
            if let lastFailure = lastFailureTime {
                let timeLeft = timeout - Date().timeIntervalSince(lastFailure)
                let timeLeftFormatted = timeLeft > 0 ? "\(Int(timeLeft/60))min" : "ready for recovery"
                description += " | Next recovery check: \(timeLeftFormatted)"
            }

        case .halfOpen:
            description += " | Recovery progress: \(halfOpenSuccessCount)/\(successThreshold)"
        }

        return description
    }

    // MARK: - Status Reporting

    /// 📈 Get Status for Analytics
    ///
    /// Returns circuit breaker status for analytics and monitoring.
    ///
    /// - Returns: Dictionary with status information
    ///
    func getStatus() -> [String: Any] {
        return [
            "state": state.rawValue,
            "failureCount": failureCount,
            "failureThreshold": failureThreshold,
            "lastFailureTime": lastFailureTime?.description ?? "never",
            "timeout": timeout,
            "halfOpenSuccessCount": halfOpenSuccessCount,
            "successThreshold": successThreshold,
            "timeSinceLastFailure": lastFailureTime.map { Date().timeIntervalSince($0) } ?? 0
        ]
    }

    // MARK: - Manual Control (for testing/debugging)

    /// 🔧 Force State Change (for testing)
    ///
    /// Manually changes circuit breaker state for testing purposes.
    /// Should not be used in production code.
    ///
    /// - Parameter newState: New state to force
    ///
    func forceState(_ newState: CircuitState) {
        logger.business("🔧 DEFENSIVE JWT: Manual state change to \(newState.rawValue) (testing only)")
        state = newState
        failureCount = 0
        halfOpenSuccessCount = 0
        lastFailureTime = newState == .open ? Date() : nil
    }
}