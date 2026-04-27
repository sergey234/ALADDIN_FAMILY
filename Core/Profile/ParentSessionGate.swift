import Foundation
import CryptoKit

// MARK: - Phase 7.2 — подтверждение взрослого перед чувствительными действиями с ростером

/// Дополняет `FamilyRosterAccess` (роль в семье) биометрией устройства, если она доступна.
@MainActor
enum ParentSessionGate {
    private static let lastSuccessfulAuthTimestampKey = "parent_session_gate_last_success_ts_v1"
    private static let lastSuccessfulPinAuthTimestampKey = "parent_session_gate_last_pin_auth_ts_v1"
    private static let pinHashSecureKey = "parent_session_gate.pin.sha256"
    private static let pinFailCountKey = "parent_session_gate.pin.fail_count.v1"
    private static let pinBlockedUntilKey = "parent_session_gate.pin.blocked_until.v1"
    private static let pinMaxAttempts = 5
    private static let pinBlockDuration: TimeInterval = 15 * 60
    /// TTL взрослой сессии для чувствительных операций (Phase 7.2).
    static let sessionTimeout: TimeInterval = 10 * 60

    /// Возвращает `true`, если биометрия недоступна или пользователь успешно прошёл проверку.
    static func confirmBiometricIfAvailable() async -> Bool {
        let sm = SecurityManager.shared
        guard sm.biometricAuthAvailable else { return true }
        return await sm.authenticateWithBiometrics()
    }

    /// Единая точка проверки для чувствительных действий.
    /// - Если есть валидная взрослая сессия в пределах TTL, повторная биометрия не требуется.
    /// - Иначе запрашивается биометрическое подтверждение (когда доступно).
    static func confirmSensitiveAction(forceReauth: Bool = false) async -> Bool {
        if !forceReauth, hasActiveSession() {
            return true
        }

        if SecurityManager.shared.biometricAuthAvailable {
            let ok = await confirmBiometricIfAvailable()
            if ok {
                markSessionConfirmed()
            }
            return ok
        }

        // Mandatory secure fallback when biometrics unavailable.
        // We intentionally require either active PIN session or explicit PIN verification via `verifyParentalPIN`.
        if hasActivePinSession() {
            markSessionConfirmed()
            return true
        }

        let ok = false
        if ok {
            markSessionConfirmed()
        }
        return ok
    }

    static func hasActiveSession(now: Date = Date()) -> Bool {
        let ts = UserDefaults.standard.double(forKey: lastSuccessfulAuthTimestampKey)
        guard ts > 0 else { return false }
        return (now.timeIntervalSince1970 - ts) <= sessionTimeout
    }

    static func markSessionConfirmed(at date: Date = Date()) {
        UserDefaults.standard.set(date.timeIntervalSince1970, forKey: lastSuccessfulAuthTimestampKey)
    }

    static func invalidateSession() {
        UserDefaults.standard.removeObject(forKey: lastSuccessfulAuthTimestampKey)
        UserDefaults.standard.removeObject(forKey: lastSuccessfulPinAuthTimestampKey)
    }

    // MARK: - Secure parental PIN fallback (threat model: no plaintext, rate limiting)

    static func setParentalPIN(_ pin: String) -> Bool {
        let normalized = pin.trimmingCharacters(in: .whitespacesAndNewlines)
        guard normalized.count >= 4, normalized.count <= 12 else { return false }
        let hash = sha256(normalized)
        guard let data = hash.data(using: .utf8) else { return false }
        let ok = SecurityManager.shared.storeSecureData(data, forKey: pinHashSecureKey)
        if ok {
            resetPinRateLimitState()
        }
        return ok
    }

    static func hasConfiguredParentalPIN() -> Bool {
        guard let data = SecurityManager.shared.retrieveSecureData(forKey: pinHashSecureKey),
              let hash = String(data: data, encoding: .utf8) else {
            return false
        }
        return !hash.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    static func verifyParentalPIN(_ pin: String, now: Date = Date()) -> Bool {
        guard !isPinTemporarilyBlocked(now: now) else { return false }
        guard let data = SecurityManager.shared.retrieveSecureData(forKey: pinHashSecureKey),
              let storedHash = String(data: data, encoding: .utf8) else {
            return false
        }
        let enteredHash = sha256(pin.trimmingCharacters(in: .whitespacesAndNewlines))
        if enteredHash == storedHash {
            resetPinRateLimitState()
            UserDefaults.standard.set(now.timeIntervalSince1970, forKey: lastSuccessfulPinAuthTimestampKey)
            markSessionConfirmed(at: now)
            return true
        }
        registerFailedPinAttempt(now: now)
        return false
    }

    private static func hasActivePinSession(now: Date = Date()) -> Bool {
        let ts = UserDefaults.standard.double(forKey: lastSuccessfulPinAuthTimestampKey)
        guard ts > 0 else { return false }
        return (now.timeIntervalSince1970 - ts) <= sessionTimeout
    }

    private static func isPinTemporarilyBlocked(now: Date) -> Bool {
        let blockedUntil = UserDefaults.standard.double(forKey: pinBlockedUntilKey)
        return blockedUntil > now.timeIntervalSince1970
    }

    private static func registerFailedPinAttempt(now: Date) {
        let attempts = UserDefaults.standard.integer(forKey: pinFailCountKey) + 1
        UserDefaults.standard.set(attempts, forKey: pinFailCountKey)
        if attempts >= pinMaxAttempts {
            UserDefaults.standard.set(now.timeIntervalSince1970 + pinBlockDuration, forKey: pinBlockedUntilKey)
            UserDefaults.standard.set(0, forKey: pinFailCountKey)
        }
    }

    private static func resetPinRateLimitState() {
        UserDefaults.standard.set(0, forKey: pinFailCountKey)
        UserDefaults.standard.removeObject(forKey: pinBlockedUntilKey)
    }

    private static func sha256(_ value: String) -> String {
        let digest = SHA256.hash(data: Data(value.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }
}
