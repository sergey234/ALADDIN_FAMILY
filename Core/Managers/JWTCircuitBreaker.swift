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
/// Endpoint Categories:
/// - componentConfig: User settings (higher threshold)
/// - analytics: Metrics/analytics (standard threshold)
/// - criticalBusiness: Core features (lower threshold)
/// - publicApi: Public endpoints (no CB)
///
class JWTCircuitBreaker {

    // MARK: - Endpoint Categories

    /// 📊 Endpoint Categories with different CB behavior
    enum EndpointCategory {
        case componentConfig    // User settings saves (threshold: 10)
        case analytics         // Metrics/analytics (threshold: 3)
        case criticalBusiness  // Core business logic (threshold: 5)
        case publicApi        // Public endpoints (no CB)

        var failureThreshold: Int {
            switch self {
            case .componentConfig: return 10  // More tolerant for user settings
            case .analytics: return 3         // Standard for metrics
            case .criticalBusiness: return 5  // Moderate for business logic
            case .publicApi: return Int.max   // Never trigger CB
            }
        }

        var recoveryTimeout: TimeInterval {
            switch self {
            case .componentConfig: return 180  // 3 min recovery
            case .analytics: return 60         // 1 min recovery
            case .criticalBusiness: return 120 // 2 min recovery
            case .publicApi: return 0          // No recovery needed
            }
        }
    }

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

    // MARK: - Category Support

    /// 🔀 Separate CB instances for different endpoint categories
    private var categoryBreakers: [EndpointCategory: JWTCircuitBreaker] = [:]

    /// Get or create CB for specific category
    private func breaker(for category: EndpointCategory) -> JWTCircuitBreaker {
        if let breaker = categoryBreakers[category] {
            return breaker
        }

        // Create new CB with category-specific settings
        let breaker = JWTCircuitBreaker()
        breaker.failureThreshold = category.failureThreshold
        breaker.timeout = category.recoveryTimeout
        categoryBreakers[category] = breaker
        return breaker
    }

    // MARK: - Properties

    /// Current circuit state
    private var state: CircuitState = .closed

    /// Number of consecutive failures
    private var failureCount = 0

    /// Timestamp of last failure
    private var lastFailureTime: Date?

    /// Number of failures before opening circuit
    private var failureThreshold = 3

    /// Time to wait before attempting recovery (5 minutes)
    private var timeout: TimeInterval = 300

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
    /// - Parameter category: Endpoint category for granular CB behavior
    /// - Returns: true if request should proceed, false if blocked
    ///
    func shouldAllowRequest(for category: EndpointCategory = .criticalBusiness) -> Bool {
        // Skip CB for public APIs
        if category == .publicApi {
            return true
        }

        let breaker = self.breaker(for: category)
        return breaker.shouldAllowRequest()
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
    /// - Parameter category: Endpoint category for granular CB behavior
    ///
    func recordSuccess(for category: EndpointCategory = .criticalBusiness) {
        // Skip CB for public APIs
        if category == .publicApi {
            return
        }

        let breaker = self.breaker(for: category)
        breaker.recordSuccess()
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
    /// - Parameter category: Endpoint category for granular CB behavior
    ///
    func recordFailure(for category: EndpointCategory = .criticalBusiness) {
        // Skip CB for public APIs
        if category == .publicApi {
            return
        }

        let breaker = self.breaker(for: category)
        breaker.recordFailure()
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

    /// 🚨 Emergency Reset to Closed State
    ///
    /// Resets circuit breaker to CLOSED state in case of emergency.
    /// Should be called when CB gets stuck in OPEN state.
    ///
    func emergencyReset() {
        logger.business("🚨 DEFENSIVE JWT: Emergency reset to CLOSED state")
        forceState(.closed)
        JWTEventLogger.logEvent(.circuitBreakerStateChanged(state: "CLOSED", reason: "Emergency reset"))
    }
}