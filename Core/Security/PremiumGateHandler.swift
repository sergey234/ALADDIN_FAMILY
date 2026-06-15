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
        let message: String
        switch networkError {
        case .unauthorized:
            message = localizationManager.localized("antifake_error_unauthorized")
        case .badRequest(let detail) where detail?.contains("file_too_large") == true:
            message = localizationManager.localized("antifake_error_file_too_large")
        case .notFound:
            message = localizationManager.localized("antifake_error_job_not_found")
        case .timeout:
            message = localizationManager.localized("antifake_error_job_timeout")
        case .tooManyRequests:
            message = localizationManager.localized("antifake_error_rate_limit")
        case .serviceUnavailable, .badGateway, .internalServerError:
            message = localizationManager.localized("antifake_error_service_unavailable")
        default:
            message = localizationManager.localized("antifake_error_try_later")
        }
        return AntifakeCheckFailurePresentation(requiresPremiumUpgrade: false, errorMessage: message)
    }
}

/// Thrown when decoded `SecurityVerdict` has `premium_required: true` (contract edge).
struct SecurityVerdictPremiumRequiredError: Error, Equatable {
    let message: String?
}
