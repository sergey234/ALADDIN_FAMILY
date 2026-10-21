import Foundation
import StoreKit
import UIKit

/// Когда можно вызвать системное окно оценки.
///
/// Первый вызов — через 21 день после первого открытия этой сборки,
/// если онбординг пройден и приложение открывали минимум в 3 разных дня.
/// Следующие вызовы — не раньше чем через 21 день, и только если человек
/// открыл приложение в более поздний день. Своих вызовов не больше 3 за 365 дней.
/// Покажет ли окно на самом деле, решает Apple.
enum AppStoreReviewPolicy {
    static let gap: TimeInterval = 21 * 24 * 60 * 60
    static let minimumDistinctDays = 3
    static let maxAttemptsPerYear = 3
    static let year: TimeInterval = 365 * 24 * 60 * 60

    struct Snapshot: Equatable {
        var onboardingCompleted: Bool
        var firstOpenAt: Date?
        var usageDayKeys: Set<String>
        var attemptDates: [Date]
    }

    enum Decision: Equatable {
        case request
        case skip
    }

    static func dayKey(_ date: Date, calendar: Calendar) -> String {
        let parts = calendar.dateComponents([.year, .month, .day], from: date)
        return String(format: "%04d-%02d-%02d", parts.year ?? 0, parts.month ?? 0, parts.day ?? 0)
    }

    static func decision(snapshot: Snapshot, now: Date, calendar: Calendar) -> Decision {
        guard snapshot.onboardingCompleted, let firstOpen = snapshot.firstOpenAt else {
            return .skip
        }
        guard snapshot.usageDayKeys.count >= minimumDistinctDays else {
            return .skip
        }

        let windowStart = now.addingTimeInterval(-year)
        let attemptsThisYear = snapshot.attemptDates.filter { $0 > windowStart }
        guard attemptsThisYear.count < maxAttemptsPerYear else {
            return .skip
        }

        if let lastAttempt = snapshot.attemptDates.max() {
            guard now.timeIntervalSince(lastAttempt) >= gap else {
                return .skip
            }
            let lastDay = dayKey(lastAttempt, calendar: calendar)
            guard snapshot.usageDayKeys.contains(where: { $0 > lastDay }) else {
                return .skip
            }
        } else {
            guard now.timeIntervalSince(firstOpen) >= gap else {
                return .skip
            }
        }

        return .request
    }
}

/// Системное окно оценки и ссылка «написать отзыв» в настройках.
@MainActor
enum AppStoreReviewPrompt {
    private static var didConsiderThisProcess = false

    /// Тихий главный экран. Один раз за запуск приложения.
    static func considerSystemPromptFromQuietScreen() async {
        guard !didConsiderThisProcess else { return }
        didConsiderThisProcess = true

        let now = Date()
        retireLegacyOnboardingPrompt()
        recordUsage(now: now)
        guard currentDecision(now: now) == .request else { return }

        try? await Task.sleep(nanoseconds: 2_000_000_000)
        guard !Task.isCancelled else { return }
        guard currentDecision(now: Date()) == .request else { return }
        guard let scene = foregroundWindowScene() else { return }

        recordAttempt(now: Date())
        SKStoreReviewController.requestReview(in: scene)
    }

    static func openWriteReviewPage() {
        let primary = AppConfig.appStoreWriteReviewURL
        UIApplication.shared.open(primary, options: [:]) { opened in
            guard !opened else { return }
            UIApplication.shared.open(AppConfig.appStoreWriteReviewHTTPSURL, options: [:], completionHandler: nil)
        }
    }

    /// DEBUG / `-RESET_ONBOARDING`.
    static func resetForQA() {
        didConsiderThisProcess = false
        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt)
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays)
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.appStoreReviewAttemptDates)
        retireLegacyOnboardingPrompt()
    }

    private static func recordUsage(now: Date) {
        let defaults = UserDefaults.standard
        if defaults.object(forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt) == nil {
            defaults.set(now.timeIntervalSince1970, forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt)
        }
        var days = Set(defaults.stringArray(forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays) ?? [])
        days.insert(AppStoreReviewPolicy.dayKey(now, calendar: .current))
        let trimmed = Array(days.sorted().suffix(40))
        defaults.set(trimmed, forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays)
    }

    private static func recordAttempt(now: Date) {
        let defaults = UserDefaults.standard
        var dates = attemptDates(defaults)
        dates.append(now)
        let cutoff = now.addingTimeInterval(-(AppStoreReviewPolicy.year + AppStoreReviewPolicy.gap))
        let kept = dates.filter { $0 > cutoff }.map(\.timeIntervalSince1970)
        defaults.set(kept, forKey: AppConfig.UserDefaultsKeys.appStoreReviewAttemptDates)
    }

    private static func currentDecision(now: Date) -> AppStoreReviewPolicy.Decision {
        let defaults = UserDefaults.standard
        let firstOpen = (defaults.object(forKey: AppConfig.UserDefaultsKeys.appStoreReviewFirstOpenAt) as? NSNumber)?.doubleValue
        let snapshot = AppStoreReviewPolicy.Snapshot(
            onboardingCompleted: defaults.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding),
            firstOpenAt: firstOpen.map { Date(timeIntervalSince1970: $0) },
            usageDayKeys: Set(defaults.stringArray(forKey: AppConfig.UserDefaultsKeys.appStoreReviewUsageDays) ?? []),
            attemptDates: attemptDates(defaults)
        )
        return AppStoreReviewPolicy.decision(snapshot: snapshot, now: now, calendar: .current)
    }

    private static func attemptDates(_ defaults: UserDefaults) -> [Date] {
        let raw = defaults.array(forKey: AppConfig.UserDefaultsKeys.appStoreReviewAttemptDates) ?? []
        return raw.compactMap { value in
            (value as? NSNumber).map { Date(timeIntervalSince1970: $0.doubleValue) }
        }
    }

    private static func foregroundWindowScene() -> UIWindowScene? {
        let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        return scenes.first { $0.activationState == .foregroundActive } ?? scenes.first
    }

    /// Старый флаг карточки после онбординга больше не читается.
    private static func retireLegacyOnboardingPrompt() {
        let defaults = UserDefaults.standard
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.pendingAppStoreReviewPrompt)
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.hasAskedAppStoreReviewAfterOnboarding)
    }
}
