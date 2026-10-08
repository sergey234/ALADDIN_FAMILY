import Foundation

/// Maps 403 / Premium API denials to paywall copy (not “network error”).
enum PrivacyPremiumErrorMapper {
    static func isPremiumRequired(_ error: Error) -> Bool {
        let network = NetworkError.from(error)
        switch network {
        case .forbidden(let detail):
            return looksLikePremium(detail)
        case .httpError(let code) where code == 403:
            return true
        case .apiError(let message, let code):
            if code == 403 { return true }
            return looksLikePremium(message)
        default:
            return looksLikePremium(error.localizedDescription)
        }
    }

    static func paywallMessage(localization: LocalizationManager) -> String {
        localization.localized("privacy_premium_required_body")
    }

    private static func looksLikePremium(_ raw: String?) -> Bool {
        let s = (raw ?? "").lowercased()
        return s.contains("premium")
            || s.contains("subscription")
            || s.contains("подписк")
            || s.contains("requires premium")
            || s.contains("dark web monitoring requires")
            || s.contains("location bubble requires")
    }
}
