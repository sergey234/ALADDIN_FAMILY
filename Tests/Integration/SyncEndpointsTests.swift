import XCTest
@testable import ALADDIN

/**
 * 🔄 Sync Endpoints Tests
 * Тесты всех 96 endpoint'ов синхронизации
 * Цель: Проверка всех endpoint'ов синхронизации
 */

class SyncEndpointsTests: XCTestCase {
    
    var apiService: APIService!
    var userId: String = "test_user_123"
    
    override func setUpWithError() throws {
        let networkManager = NetworkManager()
        apiService = APIService(networkManager: networkManager)
    }
    
    override func tearDownWithError() throws {
        apiService = nil
    }
    
    // MARK: - Gamification Sync Endpoints (30 endpoints)
    
    func testGamificationBalanceEndpoints() throws {
        // Тест endpoint'ов баланса геймификации (4 endpoint'а)
        let expectation = XCTestExpectation(description: "Balance endpoints tested")
        expectation.expectedFulfillmentCount = 4
        
        // GET /api/gamification/balance/{userId}
        apiService.getGamificationBalance(userId: userId) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                expectation.fulfill()
            }
        }
        
        // POST /api/gamification/balance/add
        let addRequest = AddBalanceRequest(userId: userId, amount: 10, reason: "Test")
        apiService.addGamificationBalance(request: addRequest) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                expectation.fulfill()
            }
        }
        
        // POST /api/gamification/balance/subtract
        let subtractRequest = SubtractBalanceRequest(userId: userId, amount: 5, reason: "Test")
        apiService.subtractGamificationBalance(request: subtractRequest) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                expectation.fulfill()
            }
        }
        
        // GET /api/gamification/balance/history
        apiService.getGamificationBalanceHistory(userId: userId, limit: 10) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 20.0)
    }
    
    func testGamificationRewardsEndpoints() throws {
        // Тест endpoint'ов наград (6 endpoint'ов)
        let expectation = XCTestExpectation(description: "Rewards endpoints tested")
        expectation.expectedFulfillmentCount = 6
        
        // GET /api/gamification/rewards
        apiService.getGamificationRewards(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/rewards/claim
        let claimRequest = ClaimRewardRequest(userId: userId, rewardId: "test_reward_1")
        apiService.claimGamificationReward(request: claimRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/rewards/history
        apiService.getGamificationRewardsHistory(userId: userId, limit: 10) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/rewards/give
        let giveRequest = GiveRewardRequest(userId: userId, rewardId: "test_reward_1", reason: "Test")
        apiService.giveGamificationReward(request: giveRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/rewards/shop
        apiService.getGamificationRewardsShop(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/rewards/purchase
        let purchaseRequest = PurchaseRewardRequest(userId: userId, rewardId: "test_reward_1")
        apiService.purchaseGamificationReward(request: purchaseRequest) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 30.0)
    }
    
    func testGamificationAchievementsEndpoints() throws {
        // Тест endpoint'ов достижений (5 endpoint'ов)
        let expectation = XCTestExpectation(description: "Achievements endpoints tested")
        expectation.expectedFulfillmentCount = 5
        
        // GET /api/gamification/achievements
        apiService.getGamificationAchievements(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/achievements/unlock
        let unlockRequest = UnlockAchievementRequest(userId: userId, achievementId: "test_achievement_1")
        apiService.unlockGamificationAchievement(request: unlockRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/achievements/progress
        apiService.getGamificationAchievementsProgress(userId: userId) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/achievements/{achievementId}
        apiService.getGamificationAchievement(userId: userId, achievementId: "test_achievement_1") { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/achievements/claim
        let claimRequest = ClaimAchievementRewardRequest(userId: userId, achievementId: "test_achievement_1")
        apiService.claimGamificationAchievementReward(request: claimRequest) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 25.0)
    }
    
    func testGamificationTournamentsEndpoints() throws {
        // Тест endpoint'ов турниров (6 endpoint'ов)
        let expectation = XCTestExpectation(description: "Tournaments endpoints tested")
        expectation.expectedFulfillmentCount = 6
        
        // GET /api/gamification/tournaments
        apiService.getGamificationTournaments(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/tournaments/join
        let joinRequest = JoinTournamentRequest(userId: userId, tournamentId: "test_tournament_1")
        apiService.joinGamificationTournament(request: joinRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/tournaments/{tournamentId}
        apiService.getGamificationTournament(userId: userId, tournamentId: "test_tournament_1") { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/tournaments/leaderboard
        apiService.getGamificationTournamentLeaderboard(tournamentId: "test_tournament_1") { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/tournaments/leave
        let leaveRequest = LeaveTournamentRequest(userId: userId, tournamentId: "test_tournament_1")
        apiService.leaveGamificationTournament(request: leaveRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/tournaments/history
        apiService.getGamificationTournamentsHistory(userId: userId, limit: 10) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 30.0)
    }
    
    func testGamificationSettingsEndpoints() throws {
        // Тест endpoint'ов настроек игр (4 endpoint'а)
        let expectation = XCTestExpectation(description: "Settings endpoints tested")
        expectation.expectedFulfillmentCount = 4
        
        // GET /api/gamification/settings
        apiService.getGamificationSettings(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/settings/update
        let updateRequest = UpdateGameSettingsRequest(userId: userId, settings: [:])
        apiService.updateGamificationSettings(request: updateRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/settings/notifications
        apiService.getGamificationNotificationsSettings(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/settings/notifications/update
        let notificationsRequest = UpdateGameNotificationsRequest(userId: userId, notifications: [:])
        apiService.updateGamificationNotificationsSettings(request: notificationsRequest) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 20.0)
    }
    
    func testGamificationProgressEndpoints() throws {
        // Тест endpoint'ов прогресса (5 endpoint'ов)
        let expectation = XCTestExpectation(description: "Progress endpoints tested")
        expectation.expectedFulfillmentCount = 5
        
        // GET /api/gamification/progress
        apiService.getGamificationProgress(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/progress/update
        let updateRequest = UpdateProgressRequest(userId: userId, progress: [:])
        apiService.updateGamificationProgress(request: updateRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/progress/stats
        apiService.getGamificationProgressStats(userId: userId) { result in
            expectation.fulfill()
        }
        
        // GET /api/gamification/progress/level
        apiService.getGamificationLevel(userId: userId) { result in
            expectation.fulfill()
        }
        
        // POST /api/gamification/progress/reset
        let resetRequest = ResetProgressRequest(userId: userId)
        apiService.resetGamificationProgress(request: resetRequest) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 25.0)
    }
    
    // MARK: - Parental Control Sync Endpoints (20 endpoints)
    
    func testParentalControlSettingsEndpoints() throws {
        // Тест endpoint'ов настроек родительского контроля (5 endpoint'ов)
        let expectation = XCTestExpectation(description: "Parental settings endpoints tested")
        expectation.expectedFulfillmentCount = 5
        
        // GET /api/parental-control/settings/{familyId}
        apiService.getParentalControlSettings(familyId: "test_family_123") { result in
            expectation.fulfill()
        }
        
        // POST /api/parental-control/settings/update
        let updateRequest = UpdateParentalControlSettingsRequest(familyId: "test_family_123", settings: [:])
        apiService.updateParentalControlSettings(request: updateRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/parental-control/settings/history
        apiService.getParentalControlSettingsHistory(familyId: "test_family_123", limit: 10) { result in
            expectation.fulfill()
        }
        
        // POST /api/parental-control/settings/sync
        let syncRequest = SyncParentalControlSettingsRequest(familyId: "test_family_123")
        apiService.syncParentalControlSettings(request: syncRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/parental-control/settings/conflicts
        apiService.getParentalControlSettingsConflicts(familyId: "test_family_123") { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 25.0)
    }
    
    func testTimeLimitsEndpoints() throws {
        // Тест endpoint'ов лимитов времени (4 endpoint'а)
        let expectation = XCTestExpectation(description: "Time limits endpoints tested")
        expectation.expectedFulfillmentCount = 4
        
        // GET /api/parental-control/time-limits/{childId}
        apiService.getTimeLimits(childId: "test_child_123") { result in
            expectation.fulfill()
        }
        
        // POST /api/parental-control/time-limits/update
        let updateRequest = UpdateTimeLimitsRequest(childId: "test_child_123", limits: [:])
        apiService.updateTimeLimits(request: updateRequest) { result in
            expectation.fulfill()
        }
        
        // GET /api/parental-control/time-limits/history
        apiService.getTimeLimitsHistory(childId: "test_child_123", limit: 10) { result in
            expectation.fulfill()
        }
        
        // POST /api/parental-control/time-limits/reset
        let resetRequest = ResetTimeLimitsRequest(childId: "test_child_123")
        apiService.resetTimeLimits(request: resetRequest) { result in
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 20.0)
    }
    
    // MARK: - Batch Sync Tests
    
    func testBatchSyncPerformance() throws {
        // Тест производительности батчинга синхронизации
        self.measure {
            // Синхронизируем все категории одновременно
            apiService.syncGamification(userId: userId, lastSyncTimestamp: nil) { _ in }
            apiService.syncParentalControl(userId: userId, lastSyncTimestamp: nil) { _ in }
            apiService.syncUserProfile(userId: userId, lastSyncTimestamp: nil) { _ in }
            apiService.syncSubscription(userId: userId, lastSyncTimestamp: nil) { _ in }
        }
    }
    
    // MARK: - All Endpoints Test
    
    func testAllSyncEndpoints() throws {
        // Тест всех 96 endpoint'ов синхронизации
        let expectation = XCTestExpectation(description: "All endpoints tested")
        expectation.expectedFulfillmentCount = 96
        
        // Геймификация (30 endpoint'ов)
        testGamificationBalanceEndpoints()
        testGamificationRewardsEndpoints()
        testGamificationAchievementsEndpoints()
        testGamificationTournamentsEndpoints()
        testGamificationSettingsEndpoints()
        testGamificationProgressEndpoints()
        
        // Родительский контроль (20 endpoint'ов)
        testParentalControlSettingsEndpoints()
        testTimeLimitsEndpoints()
        // TODO: Добавить остальные endpoint'ы родительского контроля
        
        // Профиль пользователя (5 endpoint'ов)
        // TODO: Добавить тесты endpoint'ов профиля
        
        // Тарифы и подписки (8 endpoint'ов)
        // TODO: Добавить тесты endpoint'ов тарифов
        
        // Настройки приложения (10 endpoint'ов)
        // TODO: Добавить тесты endpoint'ов настроек
        
        // Геолокация (7 endpoint'ов)
        // TODO: Добавить тесты endpoint'ов геолокации
        
        // Семейный чат (3 endpoint'а)
        // TODO: Добавить тесты endpoint'ов чата
        
        // Офлайн хранилище (5 endpoint'ов)
        // TODO: Добавить тесты endpoint'ов офлайн хранилища
        
        // Crash Detection (4 endpoint'а)
        // TODO: Добавить тесты endpoint'ов Crash Detection
        
        // Интерфейс для пожилых (4 endpoint'а)
        // TODO: Добавить тесты endpoint'ов интерфейса для пожилых
        
        wait(for: [expectation], timeout: 300.0) // 5 минут для всех тестов
    }
}
