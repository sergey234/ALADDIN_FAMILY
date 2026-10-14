import Foundation

/// Единая логика подписей «дата регистрации» и «окончание подписки» для Profile и семейной карточки MainScreen.
@MainActor
enum SubscriptionProfileCaption {

    /// «Вы с нами с …» / pending sync — never invents today's date.
    static func registrationDateDisplay(isRussian: Bool) -> String {
        if let formatted = AccountRegistrationDateStore.displayString(isRussian: isRussian) {
            return formatted
        }
        return LocalizationManager.shared.localized("profile_registration_pending_sync")
    }

    /// Member-since line for capsule (clear whose date).
    static func memberSinceLine(isRussian: Bool) -> String {
        let dateText = registrationDateDisplay(isRussian: isRussian)
        let pending = LocalizationManager.shared.localized("profile_registration_pending_sync")
        if dateText == pending {
            return pending
        }
        return String(
            format: LocalizationManager.shared.localized("profile_member_since_fmt"),
            dateText
        )
    }

    /// Окончание trial или платной подписки. `nil` для free и когда даты ещё нет (показываем placeholder).
    static func subscriptionExpiryFormatted(
        tier: TariffType,
        trialStatus: TrialInfo?,
        subscriptionExpiresAtIso: String,
        currentSubscriptionExpiresAt: Date?,
        dates: DateFormatterService = .shared
    ) -> String? {
        guard tier != .free else { return nil }

        if tier == .trial {
            if let trial = trialStatus, trial.isActive {
                return dates.formatDisplayDate(trial.endDate)
            }
        }

        if !subscriptionExpiresAtIso.isEmpty,
           let fromIso = dates.formatExpirationDate(from: subscriptionExpiresAtIso) {
            return fromIso
        }

        if let exp = currentSubscriptionExpiresAt {
            return dates.formatDisplayDate(exp)
        }

        return nil
    }

    static func subscriptionExpiryPlaceholderKey(tier: TariffType) -> String {
        switch tier {
        case .free:
            return "profile_subscription_free_no_expiry"
        default:
            return "profile_subscription_end_pending_sync"
        }
    }
}
