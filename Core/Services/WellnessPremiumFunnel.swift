import Foundation

/// r100-1-16 — единая точка premium gate (Hub → Timeline / PDF / assessments).
enum WellnessPremiumFunnel {
    /// `true` = доступ разрешён; `false` = показать paywall (вызвавший UI выставляет `showPaywall`).
    @MainActor
    static func ensurePremiumAccess(showPaywall: inout Bool) async -> Bool {
        if let gate = try? await WellnessAPIService.shared.fetchPremiumEligibility(),
           gate.isPremiumAllowed {
            return true
        }
        showPaywall = true
        return false
    }

    static func paywallMessageKey(from gate: WellnessPremiumEligibilityResponse?) -> String {
        gate?.messageKey ?? "wellness_error_premium_subscription"
    }
}
