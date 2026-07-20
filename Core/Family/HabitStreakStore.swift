import Foundation

/// p2-9d — streak stamps per (sourceId, memberId); milestones 3/7/14/30.
final class HabitStreakStore {
    static let shared = HabitStreakStore()

    static let milestones = [3, 7, 14, 30]
    private let defaults: UserDefaults
    private let prefix = "habit_streak_v1_"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    private func dayStamp(_ date: Date = Date()) -> String {
        let f = DateFormatter()
        f.calendar = Calendar.current
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: date)
    }

    private func key(sourceId: String, memberId: String) -> String {
        "\(prefix)\(sourceId)_\(memberId)"
    }

    private func medalKey(sourceId: String, memberId: String, milestone: Int) -> String {
        "\(prefix)medal_\(sourceId)_\(memberId)_\(milestone)"
    }

    /// Record Done for today. Returns current streak length and any new milestone hit.
    @discardableResult
    func recordDone(
        sourceId: String,
        memberId: String? = nil,
        date: Date = Date()
    ) -> (streak: Int, newMilestone: Int?) {
        let member = (memberId ?? UnicornRewardsStore.resolveActiveChildId() ?? "guest")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let source = sourceId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !source.isEmpty else { return (0, nil) }

        let today = dayStamp(date)
        let k = key(sourceId: source, memberId: member)
        var days = defaults.stringArray(forKey: k) ?? []
        if days.contains(today) {
            return (currentStreak(days: days, endingOn: today), nil)
        }
        // p2-9f — respect medal source toggles (still track streak for enabled sources only)
        guard HabitMedalSourcesSettings.isSourceEnabled(source) else {
            return (0, nil)
        }
        days.append(today)
        days = Array(Set(days)).sorted()
        defaults.set(days, forKey: k)

        let streak = currentStreak(days: days, endingOn: today)
        var hit: Int?
        for m in Self.milestones where streak >= m {
            let mk = medalKey(sourceId: source, memberId: member, milestone: m)
            if !defaults.bool(forKey: mk) {
                defaults.set(true, forKey: mk)
                hit = m
                _ = UnicornCareReward.grant(
                    reason: .streakMedal,
                    sourceId: "\(source)_\(m)",
                    childId: memberId
                )
                // p2-9e lite — local Moment until Moments API
                let isRU = Locale.preferredLanguages.first?.hasPrefix("ru") == true
                let title = "🏅 \(m) " + (isRU ? "дней" : "days")
                _ = FamilyMomentsLocalStore.append(
                    text: "\(title): \(source)",
                    childId: memberId,
                    kind: "streakMedal",
                    defaults: defaults
                )
                break
            }
        }
        return (streak, hit)
    }

    func streak(sourceId: String, memberId: String? = nil) -> Int {
        let member = (memberId ?? UnicornRewardsStore.resolveActiveChildId() ?? "guest")
        let days = defaults.stringArray(forKey: key(sourceId: sourceId, memberId: member)) ?? []
        return currentStreak(days: days, endingOn: dayStamp())
    }

    private func currentStreak(days: [String], endingOn end: String) -> Int {
        let sorted = days.sorted()
        guard sorted.contains(end) else { return 0 }
        var count = 0
        var cursor = end
        let cal = Calendar.current
        let fmt = DateFormatter()
        fmt.calendar = cal
        fmt.locale = Locale(identifier: "en_US_POSIX")
        fmt.dateFormat = "yyyy-MM-dd"
        while sorted.contains(cursor) {
            count += 1
            guard let d = fmt.date(from: cursor),
                  let prev = cal.date(byAdding: .day, value: -1, to: d) else { break }
            cursor = fmt.string(from: prev)
        }
        return count
    }
}
