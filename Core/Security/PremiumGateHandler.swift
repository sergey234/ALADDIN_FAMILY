import Foundation

// MARK: - Premium gate (403) for explicit security API (B2-00b)

enum PremiumGateOutcome: Equatable, Sendable {
    case allowed
    case premiumRequired(message: String?)
    case forbidden(message: String?)
    case other(NetworkError)
}

struct PremiumGateDetail: Decodable, Equatable, Sendable {
    let error: String?
    let message: String?
    let premiumRequired: Bool?

    enum CodingKeys: String, CodingKey {
        case error
        case message
        case premiumRequired = "premium_required"
    }

    var isPremiumRequired: Bool {
        if premiumRequired == true { return true }
        if error?.lowercased() == "premium_required" { return true }
        return false
    }
}

/// Maps HTTP 403 / FastAPI `detail` and `NetworkError` → upgrade UX signal for Hub screens (B2-07).
enum PremiumGateHandler {

    static func outcome(httpStatus: Int, data: Data?) -> PremiumGateOutcome {
        if httpStatus == 429, let quota = data.flatMap(AntifakeMonthlyQuota.encodedDetail(from:)) {
            return .other(.tooManyRequests(quota))
        }
        guard httpStatus == 403 else {
            return .other(NetworkError.from(httpStatusCode: httpStatus))
        }
        if let data, let detail = parsePremiumDetail(from: data), detail.isPremiumRequired {
            return .premiumRequired(message: detail.message)
        }
        let message = data.flatMap { parseFastAPIDetailString(from: $0) }
        return .forbidden(message: message)
    }

    static func outcome(from error: Error) -> PremiumGateOutcome {
        let networkError = NetworkError.from(error)
        if networkError.isPremiumRequired {
            return .premiumRequired(message: networkError.premiumGateMessage)
        }
        switch networkError {
        case .forbidden(let message):
            return .forbidden(message: message)
        default:
            return .other(networkError)
        }
    }

    static func parsePremiumDetail(from data: Data) -> PremiumGateDetail? {
        guard let root = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        if let detail = root["detail"] as? [String: Any] {
            return decodePremiumDetail(detail)
        }
        return decodePremiumDetail(root)
    }

    private static func decodePremiumDetail(_ dict: [String: Any]) -> PremiumGateDetail? {
        let error = dict["error"] as? String
        let message = dict["message"] as? String
        let premiumRequired = dict["premium_required"] as? Bool
        if premiumRequired == true || error?.lowercased() == "premium_required" {
            return PremiumGateDetail(error: error, message: message, premiumRequired: premiumRequired)
        }
        return nil
    }

    private static func parseFastAPIDetailString(from data: Data) -> String? {
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        if let s = obj["detail"] as? String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? nil : t
        }
        if let detail = obj["detail"] as? [String: Any], let message = detail["message"] as? String {
            let t = message.trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? nil : t
        }
        if let s = obj["message"] as? String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? nil : t
        }
        return nil
    }
}

extension NetworkError {
    /// True when backend returned antifake/security premium gate (403 + premium_required).
    var isPremiumRequired: Bool {
        switch self {
        case .forbidden(let message):
            guard let message else { return false }
            let lower = message.lowercased()
            if lower.contains("premium_required") { return true }
            if lower.contains("premium subscription") { return true }
            if lower.contains("require premium") { return true }
            return false
        case .apiError(let message, let code) where code == 403:
            return message.lowercased().contains("premium")
        default:
            return false
        }
    }

    var premiumGateMessage: String? {
        switch self {
        case .forbidden(let message):
            return message
        case .apiError(let message, _):
            return message
        default:
            return nil
        }
    }
}

extension PremiumGateOutcome {
    var requiresUpgrade: Bool {
        if case .premiumRequired = self { return true }
        return false
    }

    var premiumMessage: String? {
        switch self {
        case .premiumRequired(let message):
            return message
        default:
            return nil
        }
    }
}

// MARK: - Antifake Hub unified 403 UX (B2-07)

struct AntifakeCheckFailurePresentation: Equatable, Sendable {
    let requiresPremiumUpgrade: Bool
    let errorMessage: String?
}

enum AntifakeCheckFailureHandler {

    /// Maps check errors → inline premium card or user-facing error string.
    static func present(
        error: Error,
        localizationManager: LocalizationManager
    ) -> AntifakeCheckFailurePresentation {
        let gateOutcome = PremiumGateHandler.outcome(from: error)
        if gateOutcome.requiresUpgrade {
            let message = gateOutcome.premiumMessage
                ?? localizationManager.localized("antifake_premium_required_body")
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: true,
                errorMessage: message
            )
        }

        if case .mockSourceRejected = error as? SecurityVerdictValidationError {
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: false,
                errorMessage: localizationManager.localized("antifake_error_mock_rejected")
            )
        }

        if let verdict = error as? SecurityVerdictPremiumRequiredError {
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: true,
                errorMessage: verdict.message
                    ?? localizationManager.localized("antifake_premium_required_body")
            )
        }

        let networkError = NetworkError.from(error)
        if case .tooManyRequests(let detail) = networkError,
           let limit = AntifakeMonthlyQuota.limit(fromEncoded: detail) {
            AnalyticsManager.shared.trackEvent("antifake_quota_hit", parameters: ["source": "antifake_check"])
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: true,
                errorMessage: String(format: localizationManager.localized("antifake_quota_exhausted_body"), limit)
            )
        }
        let message: String
        switch networkError {
        case .unauthorized:
            message = localizationManager.localized("antifake_error_unauthorized")
        case .badRequest(let detail) where Self.isFileTooLarge(detail):
            message = localizationManager.localized("antifake_error_file_too_large")
        case .notFound:
            message = localizationManager.localized("antifake_error_job_not_found")
        case .timeout:
            // W1 Q29: friendlier copy than raw timeout jargon
            message = localizationManager.localized("antifake_timeout_friendly")
        case .tooManyRequests:
            message = localizationManager.localized("antifake_error_rate_limit")
        case .serviceUnavailable, .badGateway, .internalServerError:
            message = localizationManager.localized("antifake_sync_fail")
        case .forbidden(let detail) where networkError.isPremiumRequired:
            // Defense in depth if outcome(from:) missed nested detail
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: true,
                errorMessage: detail
                    ?? localizationManager.localized("antifake_premium_required_body")
            )
        default:
            // URLError timedOut / network lost often lands here
            let ns = error as NSError
            if ns.domain == NSURLErrorDomain,
               ns.code == NSURLErrorTimedOut || ns.code == NSURLErrorNetworkConnectionLost {
                message = localizationManager.localized("antifake_timeout_friendly")
            } else if ns.domain == NSURLErrorDomain {
                message = localizationManager.localized("antifake_sync_fail")
            } else {
                message = localizationManager.localized("antifake_error_try_later")
            }
        }
        return AntifakeCheckFailurePresentation(requiresPremiumUpgrade: false, errorMessage: message)
    }

    /// APIService maps HTTP 413 to `badRequest("File too large")` when the server sends no detail.
    private static func isFileTooLarge(_ detail: String?) -> Bool {
        guard let lowered = detail?.lowercased() else { return false }
        return lowered.contains("file_too_large") || lowered.contains("file too large")
    }
}

/// MAIN 429 `{"detail":{"error":"monthly_quota_exceeded","limit":30,...}}` (Personal voice/video/document/call).
/// Carried through `NetworkError.tooManyRequests("monthly_quota_exceeded|<limit>")`.
enum AntifakeMonthlyQuota {
    static let errorCode = "monthly_quota_exceeded"
    private static let personalLimitKey = "antifake_personal_monthly_limit_v1"

    /// Plan limit last reported by MAIN; `nil` until the quota endpoint is live (card line stays hidden).
    static var serverPersonalLimit: Int? {
        let value = UserDefaults.standard.integer(forKey: personalLimitKey)
        return value > 0 ? value : nil
    }

    @MainActor
    static func refreshServerPersonalLimit() {
        guard AppConfig.authToken != nil else { return }
        APIService.shared.getAntifakeQuota { result in
            switch result {
            case .success(let quota):
                UserDefaults.standard.set(max(0, quota.personalMonthlyLimit), forKey: personalLimitKey)
            case .failure(let error):
                if case .notFound = NetworkError.from(error) {
                    UserDefaults.standard.removeObject(forKey: personalLimitKey)
                }
            }
        }
    }

    static func encodedDetail(from data: Data) -> String? {
        guard let root = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        return encodedDetail(fromJSON: root)
    }

    static func encodedDetail(fromJSON root: [String: Any]) -> String? {
        let detail = (root["detail"] as? [String: Any]) ?? root
        guard (detail["error"] as? String) == errorCode else { return nil }
        let limit = (detail["limit"] as? Int) ?? (detail["limit"] as? NSNumber)?.intValue
            ?? TariffEntitlements.personalMonthlyHeavyChecksDefault
        return "\(errorCode)|\(limit)"
    }

    static func limit(fromEncoded detail: String?) -> Int? {
        guard let detail, detail.hasPrefix(errorCode) else { return nil }
        let parts = detail.split(separator: "|")
        if parts.count > 1, let limit = Int(parts[1]), limit > 0 { return limit }
        return TariffEntitlements.personalMonthlyHeavyChecksDefault
    }
}

/// Thrown when decoded `SecurityVerdict` has `premium_required: true` (contract edge).
struct SecurityVerdictPremiumRequiredError: Error, Equatable {
    let message: String?
}
