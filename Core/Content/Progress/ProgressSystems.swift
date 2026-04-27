import Foundation

struct ParentDashboardSnapshot {
    let totalOpens: Int
    let totalCompletions: Int
    let completionRate: Double
    let currentStreakDays: Int
    let remainingTimeSecToday: Int
    let unlockedAchievements: [String]
}

/// One calendar day of activity for parent dashboard charts (opens, completions, screen time).
struct ParentDashboardDayPoint: Identifiable, Equatable {
    let id: String
    let dayStart: Date
    let opens: Int
    let completions: Int
    let usedSeconds: Int
}

/// Persists per-day opens/completions and closed-day screen time for week/month trends.
final class ParentActivityDailyAggregator {
    static let shared = ParentActivityDailyAggregator()

    private let defaults: UserDefaults
    private let calendar: Calendar
    private let storageKey = "content.parentActivityDaily.v1"
    private var days: [String: StoredDay] = [:]

    private struct StoredDay: Codable, Equatable {
        var dayKey: String
        var opens: Int
        var completions: Int
        /// Set when the calendar day ended (midnight rollover). Today reads live from `TimeTracker`.
        var closedUsedSeconds: Int?
    }

    init(defaults: UserDefaults = .standard, calendar: Calendar = .current) {
        self.defaults = defaults
        self.calendar = calendar
        load()
    }

    func recordOpen(at date: Date = Date()) {
        mutate(dayKey(for: date)) { $0.opens += 1 }
    }

    func recordCompletion(at date: Date = Date()) {
        mutate(dayKey(for: date)) { $0.completions += 1 }
    }

    /// Called from `TimeTracker` when the stored usage date is no longer "today".
    func closeDay(atStartOfDay dayStart: Date, totalUsedSeconds: Int) {
        let key = dayKey(for: dayStart)
        var row = days[key] ?? StoredDay(dayKey: key, opens: 0, completions: 0, closedUsedSeconds: nil)
        row.closedUsedSeconds = max(0, totalUsedSeconds)
        days[key] = row
        persist()
    }

    /// Oldest → newest; `lastCalendarDays` is 7 (week) or 30 (month).
    func trendPoints(lastCalendarDays: Int, now: Date = Date()) -> [ParentDashboardDayPoint] {
        buildTrendPoints(lastDays: lastCalendarDays, now: now, todayUsedSeconds: TimeTracker.shared.usedSecondsToday)
    }

    func buildTrendPoints(lastDays: Int, now: Date, todayUsedSeconds: Int) -> [ParentDashboardDayPoint] {
        let n = max(1, min(lastDays, 120))
        let todayStart = calendar.startOfDay(for: now)
        var result: [ParentDashboardDayPoint] = []
        result.reserveCapacity(n)
        for offset in stride(from: n - 1, through: 0, by: -1) {
            guard let dayStart = calendar.date(byAdding: .day, value: -offset, to: todayStart) else { continue }
            let key = dayKey(for: dayStart)
            let row = days[key]
            let opens = row?.opens ?? 0
            let completions = row?.completions ?? 0
            let used: Int
            if calendar.isDate(dayStart, inSameDayAs: now) {
                used = max(0, todayUsedSeconds)
            } else {
                used = max(0, row?.closedUsedSeconds ?? 0)
            }
            result.append(
                ParentDashboardDayPoint(
                    id: key,
                    dayStart: dayStart,
                    opens: opens,
                    completions: completions,
                    usedSeconds: used
                )
            )
        }
        return result
    }

    private func mutate(_ key: String, _ body: (inout StoredDay) -> Void) {
        var row = days[key] ?? StoredDay(dayKey: key, opens: 0, completions: 0, closedUsedSeconds: nil)
        body(&row)
        days[key] = row
        persist()
    }

    private func dayKey(for date: Date) -> String {
        let start = calendar.startOfDay(for: date)
        let c = calendar.dateComponents([.year, .month, .day], from: start)
        guard let y = c.year, let m = c.month, let d = c.day else { return "" }
        return String(format: "%04d-%02d-%02d", y, m, d)
    }

    private func load() {
        guard let data = defaults.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([StoredDay].self, from: data)
        else {
            days = [:]
            return
        }
        days = Dictionary(uniqueKeysWithValues: decoded.map { ($0.dayKey, $0) })
    }

    private func persist() {
        prune()
        let rows = days.values.sorted { $0.dayKey < $1.dayKey }
        if let data = try? JSONEncoder().encode(rows) {
            defaults.set(data, forKey: storageKey)
        }
    }

    private func prune(keepingLastDays: Int = 120) {
        guard let cutoffDate = calendar.date(byAdding: .day, value: -keepingLastDays, to: calendar.startOfDay(for: Date())) else {
            return
        }
        let cutoffKey = dayKey(for: cutoffDate)
        days = days.filter { $0.key >= cutoffKey }
    }
}

final class ProgressTracker {
    static let shared = ProgressTracker()

    private let defaults = UserDefaults.standard
    private let opensKey = "content.progress.opens.total"
    private let completionsKey = "content.progress.completions.total"

    private init() {}

    func recordOpen(contentId: String) {
        defaults.set(totalOpens + 1, forKey: opensKey)
        ParentActivityDailyAggregator.shared.recordOpen()
        StreakTracker.shared.recordActivity()
    }

    func recordCompletion(contentId: String) {
        defaults.set(totalCompletions + 1, forKey: completionsKey)
        ParentActivityDailyAggregator.shared.recordCompletion()
        StreakTracker.shared.recordActivity()
    }

    var totalOpens: Int {
        defaults.integer(forKey: opensKey)
    }

    var totalCompletions: Int {
        defaults.integer(forKey: completionsKey)
    }

    var completionRate: Double {
        guard totalOpens > 0 else { return 0 }
        return Double(totalCompletions) / Double(totalOpens)
    }
}

final class AchievementSystem {
    static let shared = AchievementSystem()

    private init() {}

    func unlockedAchievements() -> [String] {
        var result: [String] = []
        let opens = ProgressTracker.shared.totalOpens
        let completions = ProgressTracker.shared.totalCompletions
        let streak = StreakTracker.shared.currentStreakDays

        if opens >= 10 { result.append("first_10_opens") }
        if completions >= 5 { result.append("first_5_completions") }
        if streak >= 3 { result.append("streak_3_days") }
        return result
    }
}

final class StreakTracker {
    static let shared = StreakTracker()

    private let defaults = UserDefaults.standard
    private let lastActivityDateKey = "content.streak.lastActivityDate"
    private let streakDaysKey = "content.streak.days"
    private let calendar = Calendar.current

    private init() {}

    func recordActivity(now: Date = Date()) {
        if let last = defaults.object(forKey: lastActivityDateKey) as? Date {
            if calendar.isDate(last, inSameDayAs: now) {
                return
            }
            if let yesterday = calendar.date(byAdding: .day, value: -1, to: now),
               calendar.isDate(last, inSameDayAs: yesterday) {
                defaults.set(currentStreakDays + 1, forKey: streakDaysKey)
            } else {
                defaults.set(1, forKey: streakDaysKey)
            }
        } else {
            defaults.set(1, forKey: streakDaysKey)
        }
        defaults.set(now, forKey: lastActivityDateKey)
    }

    var currentStreakDays: Int {
        max(0, defaults.integer(forKey: streakDaysKey))
    }
}

final class TimeTracker {
    static let shared = TimeTracker()

    private let defaults = UserDefaults.standard
    private let usedSecondsKey = "content.time.usedSeconds.today"
    private let usedDateKey = "content.time.usedDate"
    private let dailyLimitSecKey = "content.time.dailyLimitSec"
    private let calendar = Calendar.current

    private init() {
        if defaults.object(forKey: dailyLimitSecKey) == nil {
            defaults.set(3600, forKey: dailyLimitSecKey)
        }
    }

    func addUsage(seconds: Int, now: Date = Date()) {
        rotateDayIfNeeded(now: now)
        let updated = usedSecondsToday + max(0, seconds)
        defaults.set(updated, forKey: usedSecondsKey)
    }

    func canStartSession(now: Date = Date()) -> Bool {
        rotateDayIfNeeded(now: now)
        return usedSecondsToday < dailyLimitSec
    }

    var dailyLimitSec: Int {
        max(300, defaults.integer(forKey: dailyLimitSecKey))
    }

    var usedSecondsToday: Int {
        defaults.integer(forKey: usedSecondsKey)
    }

    var remainingSecondsToday: Int {
        max(0, dailyLimitSec - usedSecondsToday)
    }

    /// Updates the daily cap used by `ChildContentScreen` / parent summary (stored in seconds, minimum 5 minutes).
    func setDailyLimitMinutes(_ minutes: Int, now: Date = Date()) {
        rotateDayIfNeeded(now: now)
        let clampedMin = max(5, min(minutes, 24 * 60))
        defaults.set(clampedMin * 60, forKey: dailyLimitSecKey)
    }

    private func rotateDayIfNeeded(now: Date) {
        guard let saved = defaults.object(forKey: usedDateKey) as? Date else {
            defaults.set(now, forKey: usedDateKey)
            defaults.set(0, forKey: usedSecondsKey)
            return
        }
        if !calendar.isDate(saved, inSameDayAs: now) {
            let usedBeforeReset = defaults.integer(forKey: usedSecondsKey)
            let previousDayStart = calendar.startOfDay(for: saved)
            ParentActivityDailyAggregator.shared.closeDay(atStartOfDay: previousDayStart, totalUsedSeconds: usedBeforeReset)
            defaults.set(now, forKey: usedDateKey)
            defaults.set(0, forKey: usedSecondsKey)
        }
    }
}

