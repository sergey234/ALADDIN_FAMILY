import Foundation

/// Gate for Calls memory hub: trial 14d + Family/Premium (not a separate MTS-style 30d trial).
@MainActor
enum CallsAccessPolicy {
    static var bypassPremiumGate: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    static func isAvailable(subscriptionManager: SubscriptionManager? = nil) -> Bool {
        if bypassPremiumGate { return true }
        let subs = subscriptionManager ?? SubscriptionManager.shared
        if subs.trialStatus?.isActive == true { return true }
        switch subs.getCurrentLevel() {
        case .trial, .family, .premium:
            return true
        case .free, .personal:
            return false
        }
    }
}
