import Foundation

enum MnemonicRewardEvent {
    case songRecall
    case memoryGame
    case studyPass
    case streak
    case capstoneComplete
    case recallAttempt

    var unicornAmount: Int {
        switch self {
        case .songRecall: return 3
        case .memoryGame: return 5
        case .studyPass: return 5
        case .streak: return 10
        case .capstoneComplete: return 10
        case .recallAttempt: return 1
        }
    }

    var localizationKey: String {
        switch self {
        case .songRecall: return "child_mnemo_reward_song"
        case .memoryGame: return "child_mnemo_reward_memory_game"
        case .studyPass: return "child_mnemo_reward_study_pass"
        case .streak: return "child_mnemo_reward_streak"
        case .capstoneComplete: return "child_mnemo_reward_capstone"
        case .recallAttempt: return "child_mnemo_reward_micro_win"
        }
    }
}

enum MnemonicRewardBridge {
    private static let balanceKey = "child_unicorn_balance"
    private static let microWinLedgerKey = "child.mnemo.micro_win.ledger.v1"
    private static let microWinLedgerCap = 300

    /// +1 🦄 за первую попытку recall на вопрос (не только 100% pass) — B14-T09.
    @discardableResult
    static func awardRecallAttempt(itemId: String, attemptKey: String) -> Bool {
        guard !itemId.isEmpty, !attemptKey.isEmpty else { return false }
        let token = "\(itemId)|\(attemptKey)"
        var ledger = Set(UserDefaults.standard.stringArray(forKey: microWinLedgerKey) ?? [])
        guard !ledger.contains(token) else { return false }
        ledger.insert(token)
        if ledger.count > microWinLedgerCap {
            ledger = Set(Array(ledger).sorted().suffix(microWinLedgerCap))
        }
        UserDefaults.standard.set(Array(ledger), forKey: microWinLedgerKey)
        let amount = MnemonicRewardEvent.recallAttempt.unicornAmount
        let current = UserDefaults.standard.integer(forKey: balanceKey)
        UserDefaults.standard.set(current + amount, forKey: balanceKey)
        MasterLogger.shared.business("MNEMO-B14 micro-win +\(amount) item=\(itemId) key=\(attemptKey)")
        return true
    }

    static func award(_ event: MnemonicRewardEvent, itemId: String? = nil, technique: MnemonicTechnique? = nil) {
        let current = UserDefaults.standard.integer(forKey: balanceKey)
        UserDefaults.standard.set(current + event.unicornAmount, forKey: balanceKey)
        MnemonicSkillTracker.shared.recordSuccessfulRecall()
        if let itemId, !itemId.isEmpty {
            let resolvedTechnique = technique ?? MnemonicStudyTechniqueMap.technique(for: itemId)
            MnemonicTechniqueMastery.shared.recordSuccess(technique: resolvedTechnique)
        }
    }
}
