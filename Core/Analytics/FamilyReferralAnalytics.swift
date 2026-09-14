import Foundation

/// Funnel analytics for Family Invite Pro (Вариант A).
/// Events: invite_tap → link_open → signup_attach → qualify → grant
enum FamilyReferralAnalytics {
    static func track(_ stage: Stage, parameters: [String: Any] = [:]) {
        var params = parameters
        params["program"] = "family_invite_pro_a"
        AnalyticsManager.shared.trackEvent(stage.rawValue, parameters: params)
    }

    enum Stage: String {
        case inviteTap = "referral_a_invite_tap"
        case linkOpen = "referral_a_link_open"
        case signupAttach = "referral_a_signup_attach"
        case qualify = "referral_a_qualify"
        case grant = "referral_a_grant"
        case screenOpen = "referral_a_screen_open"
        case caregiverBlocked = "referral_a_caregiver_blocked"
        case levelUp = "referral_a_level_up"
    }
}
