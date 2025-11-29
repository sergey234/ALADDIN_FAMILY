import Foundation
import SwiftUI

@MainActor
final class ChildRewardsViewModel: ObservableObject {
    struct DashboardData {
        let balance: Int
        let weeklyEarned: Int
        let weeklyPunished: Int
        let goalTitleKey: String?
        let goalCost: Int
        let goalProgress: Double
        let rewards: [ShopReward]
    }
    
    @Published private(set) var dashboard: DashboardData?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private let apiService: APIService
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    func load(childId: String?) async {
        isLoading = true
        errorMessage = nil
        do {
            async let parentalStatsTask = fetchParentalControlStats(childId: childId)
            async let referralStatsTask = fetchReferralStats()
            async let referralRewardsTask = fetchReferralRewards()
            let (parentalStats, referralStats, referralRewards) = try await (parentalStatsTask, referralStatsTask, referralRewardsTask)
            dashboard = mapData(parentalStats: parentalStats, referralStats: referralStats, referralRewards: referralRewards)
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
    
    // MARK: - Mapping
    
    private func mapData(parentalStats: ParentalControlStatsResponse,
                         referralStats: ReferralStatsResponse,
                         referralRewards: ReferralRewardsResponse) -> DashboardData {
        let balance = max(Int(referralStats.totalRewards.rounded()), 0)
        let weeklyEarned = max(referralRewards.totalConverted * 50, 0)
        let weeklyPunished = max(parentalStats.contentBlocked.appsBlocked, 0)
        let nextReward = referralRewards.rewards.first { $0.status.lowercased() != "completed" } ?? referralRewards.rewards.first
        let goalCost = max(parseAmount(from: nextReward?.rewardValue) ?? nextReward?.requiredConverted ?? 0, 0)
        let progress = goalCost > 0 ? min(Double(balance) / Double(goalCost), 1.0) : 0.0
        let rewards = referralRewards.rewards.map { self.convertReward($0) }
        return DashboardData(
            balance: balance,
            weeklyEarned: weeklyEarned,
            weeklyPunished: weeklyPunished,
            goalTitleKey: nextReward?.titleKey,
            goalCost: goalCost,
            goalProgress: progress,
            rewards: rewards.isEmpty ? ShopReward.defaultRewards : rewards
        )
    }
    
    private func convertReward(_ item: ReferralRewardItem) -> ShopReward {
        let price = parseAmount(from: item.rewardValue) ?? item.requiredConverted
        return ShopReward(
            id: item.rewardId,
            icon: item.icon.isEmpty ? "🎁" : item.icon,
            titleKey: item.titleKey,
            descKey: item.subtitleKey,
            price: price,
            isEnabled: item.status.lowercased() != "locked"
        )
    }
    
    private func parseAmount(from string: String?) -> Int? {
        guard let string = string else { return nil }
        let digits = string.filter { $0.isNumber }
        return Int(digits)
    }
    
    // MARK: - API helpers
    
    private func fetchParentalControlStats(childId: String?) async throws -> ParentalControlStatsResponse {
        try await withCheckedThrowingContinuation { continuation in
            apiService.getParentalControlStats(childId: childId) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    private func fetchReferralStats() async throws -> ReferralStatsResponse {
        try await withCheckedThrowingContinuation { continuation in
            apiService.getReferralStats { result in
                continuation.resume(with: result)
            }
        }
    }
    
    private func fetchReferralRewards() async throws -> ReferralRewardsResponse {
        try await withCheckedThrowingContinuation { continuation in
            apiService.getReferralRewards { result in
                continuation.resume(with: result)
            }
        }
    }
}
