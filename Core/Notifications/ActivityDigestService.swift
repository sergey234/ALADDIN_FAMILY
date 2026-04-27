import Foundation

/// W3-4 v1: in-app activity digest text from local progress (`ContentManager` snapshot + today bucket).
enum ActivityDigestService {
    /// Builds short lines for the parent dashboard (push deferred to v2).
    static func buildDigestLines(
        snapshot: ParentDashboardSnapshot,
        todayPoint: ParentDashboardDayPoint?,
        localizationManager: LocalizationManager
    ) -> [String] {
        let opens = todayPoint?.opens ?? 0
        let completions = todayPoint?.completions ?? 0
        let usedMin = todayPoint.map { max($0.usedSeconds / 60, 0) } ?? 0
        let streak = snapshot.currentStreakDays
        let line1 = localizationManager.localized(
            "activity_digest_line_usage_fmt",
            opens,
            completions,
            usedMin
        )
        let line2 = localizationManager.localized("activity_digest_line_streak_fmt", streak)
        return [line1, line2]
    }

    @MainActor
    static func buildLiveDigestLines(localizationManager: LocalizationManager) -> [String] {
        let snap = ContentManager.shared.parentDashboardSnapshot()
        let today = ParentActivityDailyAggregator.shared.trendPoints(lastCalendarDays: 1).last
        return buildDigestLines(snapshot: snap, todayPoint: today, localizationManager: localizationManager)
    }
}
