import Foundation
import UIKit

/// Одноразовое приглашение оставить отзыв **в App Store** после онбординга.
///
/// Кастомные звёзды на карточке — только декор. Реальная оценка уходит через
/// `AppConfig.appStoreWriteReviewURL` (`?action=write-review`).
enum AppStoreReviewPrompt {
    /// Вызвать в момент завершения онбординга. Существующим юзерам pending не ставится задним числом.
    static func armAfterOnboardingIfNeeded() {
        let defaults = UserDefaults.standard
        guard !defaults.bool(forKey: AppConfig.UserDefaultsKeys.hasAskedAppStoreReviewAfterOnboarding) else {
            return
        }
        defaults.set(true, forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt)
    }

    /// `true`, если нужно показать карточку сейчас. Сразу помечает «уже спрашивали» (строго 1×).
    @discardableResult
    static func consumePendingForDisplay() -> Bool {
        let defaults = UserDefaults.standard
        guard defaults.bool(forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt) else {
            return false
        }
        guard !defaults.bool(forKey: AppConfig.UserDefaultsKeys.hasAskedAppStoreReviewAfterOnboarding) else {
            defaults.set(false, forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt)
            return false
        }
        defaults.set(false, forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt)
        defaults.set(true, forKey: AppConfig.UserDefaultsKeys.hasAskedAppStoreReviewAfterOnboarding)
        return true
    }

    static func openWriteReviewPage() {
        let primary = AppConfig.appStoreWriteReviewURL
        UIApplication.shared.open(primary, options: [:]) { opened in
            guard !opened else { return }
            // Simulator / без App Store: https как запасной путь (на симе всё равно часто FAIL).
            UIApplication.shared.open(AppConfig.appStoreWriteReviewHTTPSURL, options: [:], completionHandler: nil)
        }
    }

    /// DEBUG / `-RESET_ONBOARDING`: снова можно пройти онбординг и увидеть карточку.
    static func resetForQA() {
        let defaults = UserDefaults.standard
        defaults.set(false, forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt)
        defaults.set(false, forKey: AppConfig.UserDefaultsKeys.hasAskedAppStoreReviewAfterOnboarding)
    }
}
