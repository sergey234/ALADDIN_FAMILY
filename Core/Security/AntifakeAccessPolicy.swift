import Foundation

/// Central gate for Antifake Hub / deepfakes category (af-2-08, G-03).
@MainActor
enum AntifakeAccessPolicy {
    /// G-03: must stay `false` for App Store. Q-01: `verify_antifake_bypass_off.py`
    static let bypassPremiumGate: Bool = false

    private static var uiTestHubUnlock: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestAntifakeHubSmoke")
    }

    static func isHubAvailable(tariffManager: TariffManager? = nil) -> Bool {
        if uiTestHubUnlock { return true }
        if bypassPremiumGate { return true }
        let manager = tariffManager ?? TariffManager.shared
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
