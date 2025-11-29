struct RewardHistoryEntry: Codable, Identifiable {
    let id: String
    var title: RewardText
    var reason: RewardText
    let amount: Int
    let isReward: Bool
    let date: Date
    
    init(
        id: String = UUID().uuidString,
        title: RewardText,
        reason: RewardText,
        amount: Int,
        isReward: Bool,
        date: Date = Date()
    ) {
        self.id = id
        self.title = title
        self.reason = reason
        self.amount = amount
        self.isReward = isReward
        self.date = date
    }
}

/// Backward compatibility alias for legacy code working with RewardOperation.
typealias RewardOperation = RewardHistoryEntry
