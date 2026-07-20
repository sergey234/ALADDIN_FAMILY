import Foundation

/// P0.1a — single currency care reward for the Unicorn (not a second pet).
/// Idempotent per calendar day + reason + childId (anti-farm).
enum UnicornCareReward {
    enum Reason: String {
        case habitDone = "habit_done"
        case checkin = "checkin"
        case checkinStreak = "checkin_streak"
        case focusSuccess = "focus_success"
        case goblinStep = "goblin_step"
        case listChecked = "list_checked"
        case voiceStructure = "voice_structure"
        case dayRecap = "day_recap"
        case breath = "breath"
        case streakMedal = "streak_medal"
        case challengeDone = "challenge_done"
    }

    struct GrantResult: Equatable {
        let applied: Bool
        let balance: Int
        let love: Double
        let hunger: Double
        let amount: Int
    }

    private static let loveKey = "pet_love"
    private static let hungerKey = "pet_hunger"
    private static let grantedPrefix = "unicorn_care_granted_"

    private static let defaultAmounts: [Reason: Int] = [
        .habitDone: 5,
        .checkin: 3,
        .checkinStreak: 8,
        .focusSuccess: 6,
        .goblinStep: 2,
        .listChecked: 2,
        .voiceStructure: 2,
        .dayRecap: 3,
        .breath: 4,
        .streakMedal: 10,
        .challengeDone: 4,
    ]

    @discardableResult
    static func grant(
        reason: Reason,
        amount: Int? = nil,
        sourceId: String? = nil,
        childId: String? = nil,
        defaults: UserDefaults = .standard
    ) -> GrantResult {
        let scopeChild = childId ?? UnicornRewardsStore.resolveActiveChildId(from: defaults)
        let day = Self.dayStamp(defaults: defaults)
        let source = (sourceId ?? reason.rawValue)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let grantKey = "\(grantedPrefix)\(day)_\(reason.rawValue)_\(source)_\(scopeChild ?? "guest")"

        let love = clamp01(defaults.object(forKey: loveKey) as? Double ?? 0.75)
        let hunger = clamp01(defaults.object(forKey: hungerKey) as? Double ?? 0.6)
        let balance = UnicornRewardsStore.readBalance(for: scopeChild, defaults: defaults)

        if defaults.bool(forKey: grantKey) {
            return GrantResult(applied: false, balance: balance, love: love, hunger: hunger, amount: 0)
        }

        let delta = max(0, amount ?? defaultAmounts[reason] ?? 3)
        let newBalance = balance + delta
        UnicornRewardsStore.writeBalance(newBalance, for: scopeChild, defaults: defaults)

        let weekly = UnicornRewardsStore.readWeeklyEarned(for: scopeChild, defaults: defaults)
        UnicornRewardsStore.writeWeeklyEarned(weekly + delta, for: scopeChild, defaults: defaults)

        let newLove = clamp01(love + 0.04)
        let newHunger = clamp01(hunger - 0.05)
        defaults.set(newLove, forKey: loveKey)
        defaults.set(newHunger, forKey: hungerKey)
        defaults.set(true, forKey: grantKey)

        return GrantResult(
            applied: true,
            balance: newBalance,
            love: newLove,
            hunger: newHunger,
            amount: delta
        )
    }

    /// Clear pending habit pings for a preset for today (used by P0.1d / scheduler).
    static func markHabitDoneIdempotentKey(preset: String, childId: String?) -> String {
        let day = dayStamp()
        let scope = childId ?? UnicornRewardsStore.resolveActiveChildId() ?? "guest"
        return "\(grantedPrefix)\(day)_habit_done_\(preset)_\(scope)"
    }

    private static func dayStamp(defaults: UserDefaults = .standard) -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar.current
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: Date())
    }

    private static func clamp01(_ value: Double) -> Double {
        min(1, max(0, value))
    }
}
