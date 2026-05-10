import Foundation

/// Единая логика подписей «дата регистрации» и «окончание подписки» для Profile и семейной карточки MainScreen.
@MainActor
enum SubscriptionProfileCaption {

    private static let registrationDateFormatterRU: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "d MMMM yyyy"
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()

    private static let registrationDateFormatterEN: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "d MMMM yyyy"
        formatter.locale = Locale(identifier: "en_US")
        return formatter
    }()

    /// Дата создания аккаунта из `registration_date`; если нет — сегодня (как в Profile).
    static func registrationDateDisplay(isRussian: Bool) -> String {
        let formatter = isRussian ? registrationDateFormatterRU : registrationDateFormatterEN
        if let savedDate = UserDefaults.standard.object(forKey: "registration_date") as? Date {
            return formatter.string(from: savedDate)
        }
        return formatter.string(from: Date())
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
