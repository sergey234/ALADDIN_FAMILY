import Foundation

/// What each plan unlocks on iOS — the only place for these numbers and rules.
/// Must match MAIN: `app/services/family_roster_reconcile.py` `_DEFAULT_LEVEL_MAX`,
/// `app/services/antifake_premium.py` `PREMIUM_LEVELS`, `app/services/antifake_family_entitlement.py`.
/// `FeatureRegistry` and `ThreatProtectionCategory` are catalogs, not access rules.
enum TariffEntitlements {
    /// Owner tiers (`/api/family/stats.ownerSubscriptionTier`) that share family perks with invited members.
    /// Personal is "for yourself" and does not share.
    static let familySharingOwnerTiers: Set<String> = [
        "trial", "trial_premium", "family", "premium", "premium_3m", "premium_6m"
    ]

    /// Fallback for the Personal monthly voice/video/document/call quota; the server sends the real limit.
    static let personalMonthlyHeavyChecksDefault = 30

    static func level(for tariff: TariffType) -> SubscriptionLevel {
        SubscriptionLevel(rawValue: tariff.rawValue) ?? .free
    }

    static func familyMemberLimit(_ level: SubscriptionLevel) -> Int {
        switch level {
        case .free: return 4
        case .trial: return 6
        case .personal: return 4
        case .family: return 6
        case .premium: return 15
        }
    }

    static func maxDevices(_ level: SubscriptionLevel) -> Int {
        familyMemberLimit(level)
    }

    static func canUseAntifake(_ level: SubscriptionLevel) -> Bool {
        level != .free
    }

    /// Live family map is on every plan (growth: the map is what makes people invite the family).
    static func hasLiveMap(_ level: SubscriptionLevel) -> Bool {
        true
    }

    /// Driving insights (speeding, distraction, weekly trips) stay a paid family perk.
    static func hasDrivingInsights(_ level: SubscriptionLevel) -> Bool {
        switch level {
        case .trial, .family, .premium: return true
        case .free, .personal: return false
        }
    }

    /// Server place history window. Mirror: `app/services/family_location_history.py` `_LEVEL_HOURS`.
    static func locationHistoryHours(_ level: SubscriptionLevel) -> Int {
        switch level {
        case .free, .personal: return 24
        case .trial, .family: return 7 * 24
        case .premium: return 30 * 24
        }
    }

    /// `nil` = no monthly cap (only server anti-spam rate limits).
    static func antifakeMonthlyHeavyQuota(_ level: SubscriptionLevel) -> Int? {
        level == .personal ? personalMonthlyHeavyChecksDefault : nil
    }

    static func ownerTierSharesFamilyPerks(_ tier: String?) -> Bool {
        guard let tier = tier?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased(),
              !tier.isEmpty else { return false }
        return familySharingOwnerTiers.contains(tier)
    }
}

/// Tariff screen A/B (l360 1Б.5). `control`: Free → Personal → Family → Premium; `family_first`: Family leads.
/// Sticky per install. Decide only after ≥1000 `paywall_shown` per variant or 6 weeks (revenue per 1000 views).
/// `ABTestingService` is not in the app target, so the assignment lives here.
enum TariffShowcaseExperiment {
    static let name = "tariff_showcase_v1"
    static let control = "control"
    static let familyFirst = "family_first"
    private static let storageKey = "ab_test_tariff_showcase_v1_variant"

    static func variant(defaults: UserDefaults = .standard) -> String {
        if let saved = defaults.string(forKey: storageKey), saved == control || saved == familyFirst {
            return saved
        }
        let assigned = Bool.random() ? familyFirst : control
        defaults.set(assigned, forKey: storageKey)
        AnalyticsManager.shared.trackEvent("ab_assignment", parameters: ["experiment": name, "variant": assigned])
        return assigned
    }

    static func order(for variant: String) -> [TariffType] {
        variant == familyFirst
            ? [.family, .personal, .premium, .free]
            : [.free, .personal, .family, .premium]
    }
}
