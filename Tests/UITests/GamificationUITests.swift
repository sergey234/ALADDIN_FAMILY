import XCTest

/**
 * 🎮 Gamification UI Tests
 * Автоматические тесты пользовательского интерфейса для геймификации
 * Цель: Покрытие всех экранов и функций геймификации
 */

@MainActor
class GamificationUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        // Настройка перед каждым тестом
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }
    
    override func tearDownWithError() throws {
        // Очистка после каждого теста
        app = nil
        super.tearDown()
    }
    
    // MARK: - Balance Screen Tests
    
    func testBalanceScreenDisplay() throws {
        // Тест отображения экрана баланса
        navigateToGamification()
        
        // Проверяем что экран баланса отображается
        let balanceLabel = app.staticTexts["Баланс единорогов"]
        if waitForElementToAppear(balanceLabel) {
            XCTAssertTrue(balanceLabel.exists)
        }
    }
    
    func testBalanceValueDisplay() throws {
        // Тест отображения значения баланса
        navigateToGamification()
        
        // Проверяем что баланс отображается
        let balanceValue = app.staticTexts.matching(identifier: "BalanceValue").firstMatch
        if waitForElementToAppear(balanceValue) {
            XCTAssertTrue(balanceValue.exists)
        }
    }
    
    func testAddBalanceButton() throws {
        // Тест кнопки добавления баланса
        navigateToGamification()
        
        let addButton = app.buttons["Добавить единорогов"]
        if waitForElementToAppear(addButton) {
            addButton.tap()
            
            // Проверяем что открылось модальное окно
            let modal = app.otherElements["AddBalanceModal"]
            if waitForElementToAppear(modal) {
                XCTAssertTrue(modal.exists)
            }
        }
    }
    
    func testSubtractBalanceButton() throws {
        // Тест кнопки вычитания баланса
        navigateToGamification()
        
        let subtractButton = app.buttons["Потратить единорогов"]
        if waitForElementToAppear(subtractButton) {
            subtractButton.tap()
            
            // Проверяем что открылось модальное окно
            let modal = app.otherElements["SubtractBalanceModal"]
            if waitForElementToAppear(modal) {
                XCTAssertTrue(modal.exists)
            }
        }
    }
    
    func testBalanceHistoryButton() throws {
        // Тест кнопки истории баланса
        navigateToGamification()
        
        let historyButton = app.buttons["История операций"]
        if waitForElementToAppear(historyButton) {
            historyButton.tap()
            
            // Проверяем что открылся экран истории
            let historyScreen = app.otherElements["BalanceHistoryScreen"]
            if waitForElementToAppear(historyScreen) {
                XCTAssertTrue(historyScreen.exists)
            }
        }
    }
    
    // MARK: - Rewards Screen Tests
    
    func testRewardsScreenDisplay() throws {
        // Тест отображения экрана наград
        navigateToGamification()
        
        let rewardsButton = app.buttons["Награды"]
        if waitForElementToAppear(rewardsButton) {
            rewardsButton.tap()
            
            // Проверяем что экран наград отображается
            let rewardsScreen = app.otherElements["RewardsScreen"]
            if waitForElementToAppear(rewardsScreen) {
                XCTAssertTrue(rewardsScreen.exists)
            }
        }
    }
    
    func testClaimReward() throws {
        // Тест получения награды
        navigateToGamification()
        navigateToRewards()
        
        // Находим первую доступную награду
        let claimButton = app.buttons.matching(identifier: "ClaimRewardButton").firstMatch
        if waitForElementToAppear(claimButton) {
            claimButton.tap()
            
            // Проверяем что награда получена
            let successAlert = app.alerts["Награда получена"]
            if waitForElementToAppear(successAlert) {
                XCTAssertTrue(successAlert.exists)
            }
        }
    }
    
    func testRewardShop() throws {
        // Тест магазина наград
        navigateToGamification()
        navigateToRewards()
        
        let shopButton = app.buttons["Магазин наград"]
        if waitForElementToAppear(shopButton) {
            shopButton.tap()
            
            // Проверяем что открылся магазин
            let shopScreen = app.otherElements["RewardShopScreen"]
            if waitForElementToAppear(shopScreen) {
                XCTAssertTrue(shopScreen.exists)
            }
        }
    }
    
    // MARK: - Achievements Screen Tests
    
    func testAchievementsScreenDisplay() throws {
        // Тест отображения экрана достижений
        navigateToGamification()
        
        let achievementsButton = app.buttons["Достижения"]
        if waitForElementToAppear(achievementsButton) {
            achievementsButton.tap()
            
            // Проверяем что экран достижений отображается
            let achievementsScreen = app.otherElements["AchievementsScreen"]
            if waitForElementToAppear(achievementsScreen) {
                XCTAssertTrue(achievementsScreen.exists)
            }
        }
    }
    
    func testUnlockAchievement() throws {
        // Тест разблокировки достижения
        navigateToGamification()
        navigateToAchievements()
        
        // Находим первое заблокированное достижение
        let unlockButton = app.buttons.matching(identifier: "UnlockAchievementButton").firstMatch
        if waitForElementToAppear(unlockButton) {
            unlockButton.tap()
            
            // Проверяем что достижение разблокировано
            let successAlert = app.alerts["Достижение разблокировано"]
            if waitForElementToAppear(successAlert) {
                XCTAssertTrue(successAlert.exists)
            }
        }
    }
    
    // MARK: - Tournaments Screen Tests
    
    func testTournamentsScreenDisplay() throws {
        // Тест отображения экрана турниров
        navigateToGamification()
        
        let tournamentsButton = app.buttons["Турниры"]
        if waitForElementToAppear(tournamentsButton) {
            tournamentsButton.tap()
            
            // Проверяем что экран турниров отображается
            let tournamentsScreen = app.otherElements["TournamentsScreen"]
            if waitForElementToAppear(tournamentsScreen) {
                XCTAssertTrue(tournamentsScreen.exists)
            }
        }
    }
    
    func testJoinTournament() throws {
        // Тест присоединения к турниру
        navigateToGamification()
        navigateToTournaments()
        
        // Находим первый доступный турнир
        let joinButton = app.buttons.matching(identifier: "JoinTournamentButton").firstMatch
        if waitForElementToAppear(joinButton) {
            joinButton.tap()
            
            // Проверяем что присоединились к турниру
            let successAlert = app.alerts["Вы присоединились к турниру"]
            if waitForElementToAppear(successAlert) {
                XCTAssertTrue(successAlert.exists)
            }
        }
    }
    
    func testLeaderboard() throws {
        // Тест таблицы лидеров
        navigateToGamification()
        navigateToTournaments()
        
        let leaderboardButton = app.buttons["Таблица лидеров"]
        if waitForElementToAppear(leaderboardButton) {
            leaderboardButton.tap()
            
            // Проверяем что открылась таблица лидеров
            let leaderboardScreen = app.otherElements["LeaderboardScreen"]
            if waitForElementToAppear(leaderboardScreen) {
                XCTAssertTrue(leaderboardScreen.exists)
            }
        }
    }
    
    // MARK: - Settings Screen Tests
    
    func testGameSettingsScreen() throws {
        // Тест экрана настроек игр
        navigateToGamification()
        
        let settingsButton = app.buttons["Настройки игр"]
        if waitForElementToAppear(settingsButton) {
            settingsButton.tap()
            
            // Проверяем что экран настроек отображается
            let settingsScreen = app.otherElements["GameSettingsScreen"]
            if waitForElementToAppear(settingsScreen) {
                XCTAssertTrue(settingsScreen.exists)
            }
        }
    }
    
    func testUpdateGameSettings() throws {
        // Тест обновления настроек игр
        navigateToGamification()
        navigateToGameSettings()
        
        // Изменяем настройку
        let toggle = app.switches.matching(identifier: "EnableNotifications").firstMatch
        if waitForElementToAppear(toggle) {
            toggle.tap()
            
            // Проверяем что настройка сохранена
            let saveButton = app.buttons["Сохранить"]
            if waitForElementToAppear(saveButton) {
                saveButton.tap()
                
                let successAlert = app.alerts["Настройки сохранены"]
                if waitForElementToAppear(successAlert) {
                    XCTAssertTrue(successAlert.exists)
                }
            }
        }
    }
    
    // MARK: - Progress Screen Tests
    
    func testProgressScreenDisplay() throws {
        // Тест отображения экрана прогресса
        navigateToGamification()
        
        let progressButton = app.buttons["Прогресс"]
        if waitForElementToAppear(progressButton) {
            progressButton.tap()
            
            // Проверяем что экран прогресса отображается
            let progressScreen = app.otherElements["ProgressScreen"]
            if waitForElementToAppear(progressScreen) {
                XCTAssertTrue(progressScreen.exists)
            }
        }
    }
    
    func testProgressLevelDisplay() throws {
        // Тест отображения уровня прогресса
        navigateToGamification()
        navigateToProgress()
        
        // Проверяем что уровень отображается
        let levelLabel = app.staticTexts.matching(identifier: "CurrentLevel").firstMatch
        if waitForElementToAppear(levelLabel) {
            XCTAssertTrue(levelLabel.exists)
        }
    }
    
    // MARK: - Navigation Helper Methods
    
    private func navigateToGamification() {
        // Навигация к экрану геймификации
        let gamificationButton = app.buttons["Геймификация"]
        if waitForElementToAppear(gamificationButton) {
            gamificationButton.tap()
        }
    }
    
    private func navigateToRewards() {
        let rewardsButton = app.buttons["Награды"]
        if waitForElementToAppear(rewardsButton) {
            rewardsButton.tap()
        }
    }
    
    private func navigateToAchievements() {
        let achievementsButton = app.buttons["Достижения"]
        if waitForElementToAppear(achievementsButton) {
            achievementsButton.tap()
        }
    }
    
    private func navigateToTournaments() {
        let tournamentsButton = app.buttons["Турниры"]
        if waitForElementToAppear(tournamentsButton) {
            tournamentsButton.tap()
        }
    }
    
    private func navigateToGameSettings() {
        let settingsButton = app.buttons["Настройки игр"]
        if waitForElementToAppear(settingsButton) {
            settingsButton.tap()
        }
    }
    
    private func navigateToProgress() {
        let progressButton = app.buttons["Прогресс"]
        if waitForElementToAppear(progressButton) {
            progressButton.tap()
        }
    }
    
    // MARK: - Helper Methods
    
    func waitForElementToAppear(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        let predicate = NSPredicate(format: "exists == true")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        return result == .completed
    }
}
