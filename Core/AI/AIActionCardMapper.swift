import Foundation

/// Maps backend `suggested_actions` to `NavigationManager` screens (ai-ios-action-cards P2).
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

enum AIActionCardMapper {
    static func screen(for actionId: String) -> NavigationManager.ALADDINScreen? {
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
