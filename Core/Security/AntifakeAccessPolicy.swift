import Foundation

/// Central gate for Antifake Hub / deepfakes category (af-2-08, G-03).
/// Policy A: active App Trial (server SSOT `trial_end` or live trialStatus) unlocks Hub
/// the same way as Family/Premium. DEBUG bypass is ASC/local only — not proof of API access.
@MainActor
enum AntifakeAccessPolicy {
    /// Production: gate ON. DEBUG/UITest: unlock Hub for ASC screenshots & local QA.
    /// Release App Store builds keep `bypassPremiumGate == false`.
    static var bypassPremiumGate: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    private static var uiTestHubUnlock: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITestAntifakeHubSmoke")
    }

    private static var debugQALocalTrialOverrideActive: Bool {
        #if DEBUG
        UserDefaults.standard.bool(forKey: "debug_qa_local_trial_override_v1")
        #else
        false
        #endif
    }

    /// Server-backed or paid access (no DEBUG hub bypass). Use for Check submit expectations.
    static func canSubmitChecks(
        tariffManager: TariffManager? = nil,
        subscriptionManager: SubscriptionManager? = nil
    ) -> Bool {
        if uiTestHubUnlock { return true }

        let subs = subscriptionManager ?? SubscriptionManager.shared
        // Policy A: server SSOT trial window (survives JWT level=free drift).
        if let end = subs.ssotTrialEndDate, end > Date() { return true }

        // Live trialStatus — ignore DEBUG-only local override (not written to MAIN).
        if subs.trialStatus?.isActive == true, !debugQALocalTrialOverrideActive {
            return true
        }
        if subs.getCurrentLevel() == .trial, !debugQALocalTrialOverrideActive {
            return true
        }

        let manager = tariffManager ?? TariffManager.shared
        if manager.currentTariff == .premium { return true }
        return manager.isCategoryAvailable(.deepfakes)
    }

    static func isHubAvailable(
        tariffManager: TariffManager? = nil,
        subscriptionManager: SubscriptionManager? = nil
    ) -> Bool {
        if uiTestHubUnlock { return true }
        if bypassPremiumGate { return true }
        return canSubmitChecks(
            tariffManager: tariffManager,
            subscriptionManager: subscriptionManager
        )
    }

    static func openHubOrPaywall(using navigationManager: NavigationManager) {
        if isHubAvailable() {
            navigationManager.navigateToAntifakeHub()
        } else {
            navigationManager.navigateTo(.tariffs)
        }
    }
}
