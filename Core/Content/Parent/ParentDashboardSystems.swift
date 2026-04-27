import Foundation

struct ActivityReportItem: Identifiable, Hashable {
    let id: String
    /// Localization key for the row title (resolved in UI via `LocalizationManager`).
    let titleKey: String
    let value: String
}

final class ActivityReports {
    static let shared = ActivityReports()

    private init() {}

    func build(from snapshot: ParentDashboardSnapshot) -> [ActivityReportItem] {
        [
            .init(id: "opens", titleKey: "parent_dashboard_metric_opens", value: "\(snapshot.totalOpens)"),
            .init(id: "completions", titleKey: "parent_dashboard_metric_completions", value: "\(snapshot.totalCompletions)"),
            .init(id: "completion_rate", titleKey: "parent_dashboard_metric_completion_rate", value: "\(Int(snapshot.completionRate * 100))%"),
            .init(id: "streak", titleKey: "parent_dashboard_metric_streak", value: "\(snapshot.currentStreakDays)"),
            .init(id: "remaining", titleKey: "parent_dashboard_metric_remaining", value: "\(snapshot.remainingTimeSecToday / 60)")
        ]
    }
}

final class TimeLimitsManager {
    static let shared = TimeLimitsManager()

    private init() {}

    func currentDailyLimitMinutes() -> Int {
        TimeTracker.shared.dailyLimitSec / 60
    }

    func currentRemainingMinutes() -> Int {
        TimeTracker.shared.remainingSecondsToday / 60
    }
}

final class ContentFilters {
    static let shared = ContentFilters()

    private init() {}

    func filtered(items: [ContentItem], allowedTypes: Set<ContentItemType>) -> [ContentItem] {
        guard !allowedTypes.isEmpty else { return items }
        return items.filter { allowedTypes.contains($0.type) }
    }
}

