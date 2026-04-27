import XCTest
@testable import ALADDIN

/**
 * 🔄 Sync Between Devices Tests
 * Тесты синхронизации между устройствами
 * Цель: Проверка синхронизации данных между iPhone и iPad
 */

class SyncBetweenDevicesTests: XCTestCase {
    
    var apiService: APIService!
    var userId: String = "test_user_123"
    
    override func setUpWithError() throws {
        let env = ProcessInfo.processInfo.environment
        let mode = (env["SYNC_INTEGRATION_MODE"] ?? "mock").lowercased()
        let runFlag = env["RUN_SYNC_INTEGRATION_TESTS"] ?? "0"
        guard mode == "staging", runFlag == "1" else {
            throw XCTSkip(
                "SyncBetweenDevicesTests require staging opt-in: " +
                "set SYNC_INTEGRATION_MODE=staging and RUN_SYNC_INTEGRATION_TESTS=1"
            )
        }

        // Настройка перед каждым тестом
        let networkManager = NetworkManager()
        apiService = APIService(networkManager: networkManager)
    }
    
    override func tearDownWithError() throws {
        // Очистка после каждого теста
        apiService = nil
    }
    
    // MARK: - Gamification Sync Tests
    
    func testGamificationBalanceSync() throws {
        // Тест синхронизации баланса геймификации между устройствами
        let expectation = XCTestExpectation(description: "Balance synced")
        
        // Изменяем баланс на "iPhone"
        let addBalanceRequest = AddBalanceRequest(
            userId: userId,
            amount: 50,
            reason: "Test sync"
        )
        
        apiService.addGamificationBalance(request: addBalanceRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем баланс на "iPad"
                self.apiService.getGamificationBalance(userId: self.userId) { balanceResult in
                    switch balanceResult {
                    case .success(let balance):
                        // Проверяем что баланс синхронизирован
                        XCTAssertGreaterThanOrEqual(balance.balance, 50)
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get balance: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to add balance: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    func testGamificationRewardsSync() throws {
        // Тест синхронизации наград между устройствами
        let expectation = XCTestExpectation(description: "Rewards synced")
        
        // Получаем награду на "iPhone"
        let claimRequest = ClaimRewardRequest(
            userId: userId,
            rewardId: "test_reward_1"
        )
        
        apiService.claimGamificationReward(request: claimRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем награды на "iPad"
                self.apiService.getGamificationRewardsHistory(userId: self.userId) { rewardsResult in
                    switch rewardsResult {
                    case .success(let rewards):
                        // Проверяем что награда синхронизирована
                        let claimedReward = rewards.first { $0.rewardId == "test_reward_1" }
                        XCTAssertNotNil(claimedReward)
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get rewards: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to claim reward: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - Parental Control Sync Tests
    
    func testParentalControlSettingsSync() throws {
        // Тест синхронизации настроек родительского контроля
        let expectation = XCTestExpectation(description: "Parental settings synced")
        
        // Изменяем настройки на "iPhone"
        let updateRequest = UpdateParentalControlSettingsRequest(
            familyId: "test_family_123",
            settings: [
                "screenTimeLimit": AnyCodable(120),
                "bedtime": AnyCodable("22:00")
            ]
        )
        
        apiService.updateParentalControlSettings(request: updateRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем настройки на "iPad"
                self.apiService.getParentalControlSettings(familyId: "test_family_123") { settingsResult in
                    switch settingsResult {
                    case .success(let settings):
                        // Проверяем что настройки синхронизированы
                        XCTAssertNotNil(settings.settings["screenTimeLimit"])
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get settings: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to update settings: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    func testTimeLimitsSync() throws {
        // Тест синхронизации лимитов времени
        let expectation = XCTestExpectation(description: "Time limits synced")
        
        // Изменяем лимиты на "iPhone"
        let updateRequest = UpdateTimeLimitsRequest(
            childId: "test_child_123",
            limits: [
                "daily": AnyCodable(120),
                "weekly": AnyCodable(840)
            ]
        )
        
        apiService.updateTimeLimits(request: updateRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем лимиты на "iPad"
                self.apiService.getTimeLimits(childId: "test_child_123") { limitsResult in
                    switch limitsResult {
                    case .success(let limits):
                        // Проверяем что лимиты синхронизированы
                        XCTAssertNotNil(limits.limits["daily"])
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get limits: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to update limits: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - Profile Sync Tests
    
    func testProfileSync() throws {
        // Тест синхронизации профиля пользователя
        let expectation = XCTestExpectation(description: "Profile synced")
        
        // Изменяем профиль на "iPhone"
        let updateRequest = UpdateUserProfileRequest(
            userId: userId,
            profile: [
                "displayName": AnyCodable("Test User"),
                "avatar": AnyCodable("avatar_url")
            ]
        )
        
        apiService.updateUserProfile(request: updateRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем профиль на "iPad"
                self.apiService.getUserProfile(userId: self.userId) { profileResult in
                    switch profileResult {
                    case .success(let profile):
                        // Проверяем что профиль синхронизирован
                        XCTAssertEqual(profile.profile["displayName"]?.value as? String, "Test User")
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get profile: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to update profile: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - Subscription Sync Tests
    
    func testSubscriptionSync() throws {
        // Тест синхронизации тарифа
        let expectation = XCTestExpectation(description: "Subscription synced")
        
        // Изменяем тариф на "iPhone"
        let updateRequest = UpdateSubscriptionRequest(
            userId: userId,
            subscription: [
                "plan": AnyCodable("premium"),
                "status": AnyCodable("active")
            ]
        )
        
        apiService.updateSubscription(request: updateRequest) { result in
            switch result {
            case .success:
                // Ждем синхронизации
                sleep(2)
                
                // Проверяем тариф на "iPad"
                self.apiService.getSubscription(userId: self.userId) { subscriptionResult in
                    switch subscriptionResult {
                    case .success(let subscription):
                        // Проверяем что тариф синхронизирован
                        XCTAssertEqual(subscription.subscription["plan"]?.value as? String, "premium")
                        expectation.fulfill()
                    case .failure(let error):
                        XCTFail("Failed to get subscription: \(error)")
                    }
                }
            case .failure(let error):
                XCTFail("Failed to update subscription: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    // MARK: - Conflict Resolution Tests
    
    func testSimultaneousChangesConflict() throws {
        // Тест разрешения конфликтов при одновременных изменениях
        let expectation = XCTestExpectation(description: "Conflict resolved")
        
        // Изменяем одни и те же данные на разных устройствах одновременно
        let request1 = UpdateUserProfileRequest(
            userId: userId,
            profile: ["displayName": AnyCodable("iPhone User")]
        )
        
        let request2 = UpdateUserProfileRequest(
            userId: userId,
            profile: ["displayName": AnyCodable("iPad User")]
        )
        
        // Выполняем оба запроса одновременно
        var result1: Result<UserProfileResponse, Error>?
        var result2: Result<UserProfileResponse, Error>?
        
        let group = DispatchGroup()
        
        group.enter()
        apiService.updateUserProfile(request: request1) { result in
            result1 = result
            group.leave()
        }
        
        group.enter()
        apiService.updateUserProfile(request: request2) { result in
            result2 = result
            group.leave()
        }
        
        group.wait()
        
        // Ждем синхронизации и разрешения конфликта
        sleep(3)
        
        // Проверяем что конфликт разрешен
        apiService.getUserProfile(userId: userId) { profileResult in
            switch profileResult {
            case .success(let profile):
                // Одно из значений должно быть применено (последнее по timestamp)
                XCTAssertNotNil(profile.profile["displayName"])
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Failed to get profile: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }

    func testRosterConflictResolutionStrategiesRespectVersioning() {
        let existing = ChildProfile(
            displayName: "Local Device",
            serverUserId: "srv-conflict-1",
            familyId: "fam-sync",
            avatarKey: "🙂",
            version: 4,
            updatedAt: Date().addingTimeInterval(120)
        )
        let serverMembers = [
            FamilyMemberResponse(
                id: "srv-conflict-1",
                name: "Server Device",
                role: "child",
                avatar: "🧒",
                status: "protected",
                threatsBlocked: nil,
                lastActive: nil,
                devices: nil
            )
        ]

        let keepLocal = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [existing],
            serverMembers: serverMembers,
            familyId: "fam-sync",
            removeMissingServerLinkedChildren: false,
            mergeStrategy: .localWins
        )
        XCTAssertEqual(keepLocal.profiles.first?.displayName, "Local Device")
        XCTAssertEqual(keepLocal.mergeStrategy, .localWins)
        XCTAssertEqual(keepLocal.conflicts, 1)
        XCTAssertGreaterThan((keepLocal.profiles.first?.version ?? 0), 4)

        let forceServer = ChildRosterReconcilePolicy.reconcile(
            existingProfiles: [existing],
            serverMembers: serverMembers,
            familyId: "fam-sync",
            removeMissingServerLinkedChildren: false,
            mergeStrategy: .serverWins
        )
        XCTAssertEqual(forceServer.profiles.first?.displayName, "Server Device")
        XCTAssertEqual(forceServer.mergeStrategy, .serverWins)
        XCTAssertEqual(forceServer.conflicts, 1)
    }
    
    // MARK: - Performance Tests
    
    func testSyncPerformance() throws {
        // Тест производительности синхронизации
        self.measure {
            // Синхронизируем все данные
            apiService.syncGamification(userId: userId, lastSyncTimestamp: nil) { _ in }
            apiService.syncParentalControl(userId: userId, lastSyncTimestamp: nil) { _ in }
            apiService.syncUserProfile(userId: userId, lastSyncTimestamp: nil) { _ in }
        }
    }
    
    func testBatchSyncPerformance() throws {
        // Тест производительности батчинга синхронизации
        self.measure {
            // Синхронизируем 100 элементов батчами
            for i in 0..<100 {
                apiService.getGamificationBalance(userId: "\(userId)_\(i)") { _ in }
            }
        }
    }
}
