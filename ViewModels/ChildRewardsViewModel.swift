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
    private let requestTimeoutSeconds: UInt64 = 12
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    func load(childId: String?) async {
        isLoading = true
        errorMessage = nil
        VisualLogger.shared.log("🚀 load() start childId=\(childId ?? "nil")", level: .info, category: "CHILD_REWARDS.API")
        defer { isLoading = false }

        do {
            VisualLogger.shared.log("🌐 request start: parental stats", level: .info, category: "CHILD_REWARDS.API")
            async let parentalStatsTask = withTimeout(seconds: requestTimeoutSeconds) {
                try await self.fetchParentalControlStats(childId: childId)
            }

            VisualLogger.shared.log("🌐 request start: referral stats", level: .info, category: "CHILD_REWARDS.API")
            async let referralStatsTask = withTimeout(seconds: requestTimeoutSeconds) {
                try await self.fetchReferralStats()
            }

            VisualLogger.shared.log("🌐 request start: referral rewards", level: .info, category: "CHILD_REWARDS.API")
            async let referralRewardsTask = withTimeout(seconds: requestTimeoutSeconds) {
                try await self.fetchReferralRewards()
            }

            let (parentalStats, referralStats, referralRewards) = try await (
                parentalStatsTask,
                referralStatsTask,
                referralRewardsTask
            )

            VisualLogger.shared.log("✅ request ok: parental stats", level: .success, category: "CHILD_REWARDS.API")
            VisualLogger.shared.log("✅ request ok: referral stats", level: .success, category: "CHILD_REWARDS.API")
            VisualLogger.shared.log("✅ request ok: referral rewards", level: .success, category: "CHILD_REWARDS.API")
            VisualLogger.shared.log("✅ load() all requests completed", level: .success, category: "CHILD_REWARDS.API")

            dashboard = mapData(
                parentalStats: parentalStats,
                referralStats: referralStats,
                referralRewards: referralRewards
            )
        } catch {
            if let networkError = error as? NetworkError, case .timeout = networkError {
                VisualLogger.shared.log("⏱️ load() hard-timeout \(requestTimeoutSeconds)s", level: .warning, category: "CHILD_REWARDS.API")
            }
            VisualLogger.shared.log("❌ load() failed: \(error.localizedDescription)", level: .error, category: "CHILD_REWARDS.API")
            errorMessage = error.localizedDescription
        }
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

    private func withTimeout<T>(seconds: UInt64, operation: @escaping () async throws -> T) async throws -> T {
        try await withThrowingTaskGroup(of: T.self) { group in
            group.addTask {
                try await operation()
            }
            group.addTask {
                try await Task.sleep(nanoseconds: seconds * 1_000_000_000)
                throw NetworkError.timeout
            }
            let value = try await group.next() ?? {
                throw NetworkError.timeout
            }()
            group.cancelAll()
            return value
        }
    }
}
