import Foundation

/// Central gate for Antifake Hub / deepfakes category (af-2-08, G-03).
@MainActor
enum AntifakeAccessPolicy {
    /// Build 238: production premium gate enforced. UITest uses `-UITestAntifakeHubSmoke`.
    static let bypassPremiumGate: Bool = false

    private static var uiTestHubUnlock: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestAntifakeHubSmoke")
    }

    static func isHubAvailable(
        tariffManager: TariffManager? = nil,
        subscriptionManager: SubscriptionManager? = nil
    ) -> Bool {
        if uiTestHubUnlock { return true }
        if bypassPremiumGate { return true }

        let subs = subscriptionManager ?? SubscriptionManager.shared
        if subs.trialStatus?.isActive == true { return true }
        if subs.getCurrentLevel() == .trial { return true }

        let manager = tariffManager ?? TariffManager.shared
        if manager.currentTariff == .premium { return true }
        return manager.isCategoryAvailable(.deepfakes)
    }

    static func openHubOrPaywall(using navigationManager: NavigationManager) {
        if isHubAvailable() {
            navigationManager.navigateToAntifakeHub()
        } else {
            navigationManager.navigateTo(.tariffs)
        }
    }
}
