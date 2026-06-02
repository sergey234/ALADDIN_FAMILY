import Foundation
import UIKit

/// Maps backend `suggested_actions` to navigation, tel: links, or sheets (p18-06).
enum AIActionCardMapper {
    static func screen(for actionId: String) -> NavigationManager.ALADDINScreen? {
        switch actionId {
        case "wellness_open_checkin", "wellness_action_open_checkin":
            return .wellnessCheckin
        case "wellness_open_hub":
            return .wellnessHub
        case "wellness_open_assessment", "wellness_action_open_assessment", "wellness_open_phq_lite":
            return .wellnessAssessmentsHub
        case "wellness_open_exercise", "wellness_action_start_breathing", "wellness_action_start_grounding":
            return .wellnessExercise
        case "wellness_open_deep", "wellness_action_open_deep":
            return .wellnessReflective
        case "wellness_open_dreams":
            return .wellnessDreamJournal
        default:
            guard let id = AIActionId(rawValue: actionId) else { return nil }
            switch id {
            case .openMain: return .main
            case .openAnalytics: return .analytics
            case .openFamily: return .family
            case .openParental: return .parentalControl
            case .openNetwork: return .networkProtection
            case .openTariffs: return .tariffs
            case .openFamilyChat: return .familyChat
            case .openThreats: return .threatProtection
            case .openSettings: return .settings
            }
        }
    }

    /// Returns a `tel:` URL string for call actions, if applicable.
    static func phoneURL(for actionId: String) -> URL? {
        switch actionId {
        case "wellness_referral_112", "wellness_call_112":
            return URL(string: "tel:112")
        case "wellness_referral_helpline_ru":
            return URL(string: "tel:88002000122")
        default:
            return nil
        }
    }

    static func opensReferralSheet(_ actionId: String) -> Bool {
        actionId == "wellness_open_referral"
    }
}

enum AIActionId: String {
    case openMain = "open_main"
    case openAnalytics = "open_analytics"
    case openFamily = "open_family"
    case openParental = "open_parental"
    case openNetwork = "open_network"
    case openTariffs = "open_tariffs"
    case openFamilyChat = "open_family_chat"
    case openThreats = "open_threats"
    case openSettings = "open_settings"
}
