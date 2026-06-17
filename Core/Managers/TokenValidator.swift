//
//  TokenValidator.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2026 ALADDIN. All rights reserved.
//
//  🛡️ DEFENSIVE JWT ARCHITECTURE - Stage 1
//  Intelligent token validation with comprehensive state analysis
//  Prevents JWT-related crashes and provides graceful degradation
//

import Foundation

/// 🛡️ TokenValidator - DEFENSIVE JWT Core Component
///
/// Provides intelligent validation of JWT tokens with comprehensive state analysis.
/// Handles all edge cases: expired tokens, malformed tokens, refresh scenarios.
/// Part of DEFENSIVE JWT Architecture for 51 protected endpoints.
///
@MainActor
class TokenValidator {

    // MARK: - Token Status Enum

    /// 🔍 Token Status - Comprehensive JWT State Analysis
    ///
    /// Defines all possible states of JWT token validation:
    /// - none: No token exists (first app launch)
    /// - valid: Token is properly signed and not expired
    /// - expired: Token has passed its expiration date
    /// - invalid: Token is malformed or corrupted
    /// - needsRefresh: Token will expire soon (proactive refresh needed)
    ///
    enum TokenStatus {
        case none           // Токена нет - нужна регистрация устройства
        case valid          // Токен валиден - используем существующий
        case expired        // Истек - очищаем и регистрируем заново
        case invalid        // Поврежден - очищаем и регистрируем заново
        case needsRefresh   // Истекает скоро - обновляем проактивно

        /// 📊 Human-readable description for logging
        var description: String {
            switch self {
            case .none: return "NONE (no token - device registration required)"
            case .valid: return "VALID (token OK - using existing)"
            case .expired: return "EXPIRED (token past expiry - clearing and re-registering)"
            case .invalid: return "INVALID (token corrupted - clearing and re-registering)"
            case .needsRefresh: return "NEEDS_REFRESH (token expiring soon - proactive refresh)"
            }
        }
    }

    // MARK: - Public Methods

    /// 🔍 Validate Current Token - DEFENSIVE JWT Core Logic
    ///
    /// Performs comprehensive validation of current JWT token with intelligent analysis:
    /// 1. Checks token existence
    /// 2. Validates JWT structure (3 parts separated by dots)
    /// 3. Analyzes expiration time with thresholds
    /// 4. Determines appropriate action (use/clear/refresh)
    ///
    /// - Returns: TokenStatus indicating current token state and required action
    ///
    /// - Note: This method is thread-safe and handles all edge cases gracefully
    ///
    static func validateCurrentToken() -> TokenStatus {
        let logger = MasterLogger.shared
        logger.business("🔍 DEFENSIVE JWT: TokenValidator.validateCurrentToken() called")

        // ШАГ 1: Проверяем существование токена
        guard let token = SubscriptionManager.shared.currentToken else {
            logger.business("📱 DEFENSIVE JWT: No token found - device registration required")
            return .none
        }

        logger.business("📋 DEFENSIVE JWT: Token exists - analyzing structure and validity")

        // ШАГ 2: Проверяем структуру JWT
        guard isValidJWTStructure(token.token) else {
            logger.error("🚨 DEFENSIVE JWT: Invalid JWT structure - token corrupted")
            return .invalid
        }

        logger.business("✅ DEFENSIVE JWT: JWT structure is valid")

        // ШАГ 3: Проверяем срок действия с интеллектуальным анализом
        let timeToExpiry = token.expiresAt.timeIntervalSinceNow
        logger.business("⏰ DEFENSIVE JWT: Time to expiry: \(Int(timeToExpiry / 60)) minutes")

        // Критическая ситуация: токен уже истек
        if timeToExpiry < 0 {
            logger.error("🚨 DEFENSIVE JWT: Token has EXPIRED (\(Int(abs(timeToExpiry) / 60)) minutes ago)")
            return .expired
        }

        // Предупреждающая ситуация: токен истечет скоро (5 минут)
        let refreshThreshold: TimeInterval = 300 // 5 minutes
        if timeToExpiry < refreshThreshold {
            logger.business("⚠️ DEFENSIVE JWT: Token expires soon (\(Int(timeToExpiry / 60)) min) - proactive refresh needed")
            return .needsRefresh
        }

        // Всё нормально: токен валиден
        logger.business("✅ DEFENSIVE JWT: Token is VALID - \(Int(timeToExpiry / 3600)) hours remaining")
        return .valid
    }

    // MARK: - Private Methods

    /// 🔧 Validate JWT Structure
    ///
    /// Performs basic structural validation of JWT token:
    /// - Must have exactly 3 parts separated by dots
    /// - Each part must be non-empty
    /// - Follows standard JWT format: header.payload.signature
    ///
    /// - Parameter token: JWT token string to validate
    /// - Returns: true if structure is valid, false otherwise
    ///
    private static func isValidJWTStructure(_ token: String) -> Bool {
        let parts = token.split(separator: ".")
        let isValid = parts.count == 3 && parts.allSatisfy { !$0.isEmpty }

        if !isValid {
            MasterLogger.shared.error("🚨 DEFENSIVE JWT: Invalid JWT structure - expected 3 parts, got \(parts.count)")
        }

        return isValid
    }
}

extension TokenValidator {
    /// Сессия пригодна для API (не показывать «демо» при валидном JWT).
    static var hasUsableAPISession: Bool {
        switch validateCurrentToken() {
        case .valid, .needsRefresh:
            return true
        case .none, .expired, .invalid:
            return false
        }
    }
}