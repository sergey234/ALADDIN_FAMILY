import Foundation

/// Central gate for Antifake Hub / deepfakes category (af-2-08, TEMP QA bypass).
@MainActor
enum AntifakeAccessPolicy {
    /// TEMP QA: set `false` before App Store — restores Premium-only Hub access.
    static let bypassPremiumGate: Bool = true

    static func isHubAvailable(tariffManager: TariffManager? = nil) -> Bool {
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
