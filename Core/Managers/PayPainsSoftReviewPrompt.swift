import Foundation

extension Notification.Name {
    /// Soft review modal should present (pay-pains R / D1.4).
    static let payPainsSoftReviewPending = Notification.Name("aladdin.payPains.softReview.pending")
}

/// Soft in-app review ask (§25 / R / D1.4).
///
/// Conditions (all): ≥2 distinct open days · real benefit this install session · never shown before.
/// Not after add-member. Not same calendar day as a system SKStoreReview attempt.
@MainActor
enum PayPainsSoftReviewPrompt {
    private static let shownKey = "aladdin.payPains.softReview.shown"
    private static let pendingKey = "aladdin.payPains.softReview.pending"

    static var hasShownOnce: Bool {
        UserDefaults.standard.bool(forKey: shownKey)
    }

    static var isPending: Bool {
        get { UserDefaults.standard.bool(forKey: pendingKey) }
        set { UserDefaults.standard.set(newValue, forKey: pendingKey) }
    }

    /// Call from home `onAppear` so day counter grows even without MainScreen.
    static func recordUsageDay(now: Date = Date()) {
        let defaults = UserDefaults.standard
        if defaults.object(forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt) == nil {
            defaults.set(now.timeIntervalSince1970, forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt)
        }
        var days = Set(defaults.stringArray(forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays) ?? [])
        days.insert(AppStoreReviewPolicy.dayKey(now, calendar: .current))
        defaults.set(Array(days.sorted().suffix(40)), forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays)
    }

    /// Successful check / pause / map / habit. Does nothing if gates fail.
    static func noteBenefitCompleted(now: Date = Date()) {
        guard PayPainsUIFlags.usesNewPayPainsHome else { return }
        guard !hasShownOnce else { return }
        recordUsageDay(now: now)
        guard distinctUsageDayCount() >= 2 else { return }
        guard !hadSystemReviewAttemptToday(now: now) else { return }
        isPending = true
        NotificationCenter.default.post(name: .payPainsSoftReviewPending, object: nil)
    }

    static var shouldPresent: Bool {
        guard PayPainsUIFlags.usesNewPayPainsHome else { return false }
        guard isPending, !hasShownOnce else { return false }
        guard distinctUsageDayCount() >= 2 else { return false }
        guard !hadSystemReviewAttemptToday() else { return false }
        return true
    }

    static func markHandled() {
        UserDefaults.standard.set(true, forKey: shownKey)
        isPending = false
    }

    static func distinctUsageDayCount() -> Int {
        Set(UserDefaults.standard.stringArray(forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays) ?? []).count
    }

    private static func hadSystemReviewAttemptToday(now: Date = Date()) -> Bool {
        let today = AppStoreReviewPolicy.dayKey(now, calendar: .current)
        let raw = UserDefaults.standard.array(forKey: AppConfig.UserDefaultsKeys.appStoreReviewAttemptDates) ?? []
        for value in raw {
            guard let n = value as? NSNumber else { continue }
            let day = AppStoreReviewPolicy.dayKey(Date(timeIntervalSince1970: n.doubleValue), calendar: .current)
            if day == today { return true }
        }
        return false
    }
}
