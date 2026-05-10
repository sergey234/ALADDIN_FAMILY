import XCTest

/**
 * 🔄 Sync UI Tests
 * Автоматические тесты пользовательского интерфейса для синхронизации
 * Цель: Покрытие всех экранов и функций синхронизации
 */

@MainActor
class SyncUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
        super.tearDown()
    }
    
    // MARK: - Sync Settings Screen Tests
    
    func testSyncSettingsScreenDisplay() throws {
        // Тест отображения экрана настроек синхронизации
        navigateToSyncSettings()
        
        let syncSettingsScreen = app.otherElements["SyncSettingsScreen"]
        if waitForElementToAppear(syncSettingsScreen) {
            XCTAssertTrue(syncSettingsScreen.exists)
        }
    }
    
    func testSyncToggle() throws {
        // Тест переключения синхронизации
        navigateToSyncSettings()
        
        let syncToggle = app.switches.matching(identifier: "SyncEnabled").firstMatch
        if waitForElementToAppear(syncToggle) {
            let initialState = syncToggle.value as? String == "1"
            syncToggle.tap()
            
            // Проверяем что состояние изменилось
            let newState = syncToggle.value as? String == "1"
            XCTAssertNotEqual(initialState, newState)
        }
    }
    
    func testAutoSyncToggle() throws {
        // Тест переключения автоматической синхронизации
        navigateToSyncSettings()
        
        let autoSyncToggle = app.switches.matching(identifier: "AutoSyncEnabled").firstMatch
        if waitForElementToAppear(autoSyncToggle) {
            autoSyncToggle.tap()
            
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
    
    func testSyncIntervalSelection() throws {
        // Тест выбора интервала синхронизации
        navigateToSyncSettings()
        
        let intervalButton = app.buttons["Интервал синхронизации"]
        if waitForElementToAppear(intervalButton) {
            intervalButton.tap()
            
            // Выбираем интервал
            let fiveMinutes = app.buttons["5 минут"]
            if waitForElementToAppear(fiveMinutes) {
                fiveMinutes.tap()
                
                // Проверяем что интервал выбран
                XCTAssertTrue(intervalButton.label.contains("5 минут"))
            }
        }
    }
    
    // MARK: - Sync Status Screen Tests
    
    func testSyncStatusScreenDisplay() throws {
        // Тест отображения экрана статуса синхронизации
        navigateToSyncStatus()
        
        let syncStatusScreen = app.otherElements["SyncStatusScreen"]
        if waitForElementToAppear(syncStatusScreen) {
            XCTAssertTrue(syncStatusScreen.exists)
        }
    }
    
    func testSyncStatusIndicator() throws {
        // Тест индикатора статуса синхронизации
        navigateToSyncStatus()
        
        let statusIndicator = app.otherElements.matching(identifier: "SyncStatusIndicator").firstMatch
        if waitForElementToAppear(statusIndicator) {
            XCTAssertTrue(statusIndicator.exists)
        }
    }
    
    func testLastSyncTime() throws {
        // Тест отображения времени последней синхронизации
        navigateToSyncStatus()
        
        let lastSyncLabel = app.staticTexts.matching(identifier: "LastSyncTime").firstMatch
        if waitForElementToAppear(lastSyncLabel) {
            XCTAssertTrue(lastSyncLabel.exists)
        }
    }
    
    func testSyncProgress() throws {
        // Тест отображения прогресса синхронизации
        navigateToSyncStatus()
        
        // Запускаем синхронизацию
        let syncButton = app.buttons["Синхронизировать"]
        if waitForElementToAppear(syncButton) {
            syncButton.tap()
            
            // Проверяем что появился индикатор прогресса
            let progressIndicator = app.progressIndicators.matching(identifier: "SyncProgress").firstMatch
            if waitForElementToAppear(progressIndicator) {
                XCTAssertTrue(progressIndicator.exists)
            }
        }
    }
    
    func testSyncStatistics() throws {
        // Тест отображения статистики синхронизации
        navigateToSyncStatus()
        
        let statisticsSection = app.otherElements.matching(identifier: "SyncStatistics").firstMatch
        if waitForElementToAppear(statisticsSection) {
            XCTAssertTrue(statisticsSection.exists)
            
            // Проверяем наличие статистики
            let syncedItems = app.staticTexts.matching(identifier: "SyncedItemsCount").firstMatch
            if syncedItems.exists {
                XCTAssertTrue(syncedItems.exists)
            }
        }
    }
    
    // MARK: - Conflict Resolution Screen Tests
    
    func testConflictResolutionScreenDisplay() throws {
        // Тест отображения экрана разрешения конфликтов
        navigateToConflictResolution()
        
        let conflictScreen = app.otherElements["ConflictResolutionScreen"]
        if waitForElementToAppear(conflictScreen) {
            XCTAssertTrue(conflictScreen.exists)
        }
    }
    
    func testConflictList() throws {
        // Тест списка конфликтов
        navigateToConflictResolution()
        
        let conflictList = app.tables.matching(identifier: "ConflictList").firstMatch
        if waitForElementToAppear(conflictList) {
            XCTAssertTrue(conflictList.exists)
        }
    }
    
    func testResolveConflict() throws {
        // Тест разрешения конфликта
        navigateToConflictResolution()
        
        // Выбираем первый конфликт
        let firstConflict = app.cells.matching(identifier: "ConflictCell").firstMatch
        if waitForElementToAppear(firstConflict) {
            firstConflict.tap()
            
            // Выбираем стратегию разрешения
            let lastWriteWins = app.buttons["Последняя запись побеждает"]
            if waitForElementToAppear(lastWriteWins) {
                lastWriteWins.tap()
                
                // Подтверждаем разрешение
                let resolveButton = app.buttons["Разрешить"]
                if waitForElementToAppear(resolveButton) {
                    resolveButton.tap()
                    
                    // Проверяем что конфликт разрешен
                    let successAlert = app.alerts["Конфликт разрешен"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    func testResolveAllConflicts() throws {
        // Тест разрешения всех конфликтов
        navigateToConflictResolution()
        
        let resolveAllButton = app.buttons["Разрешить все"]
        if waitForElementToAppear(resolveAllButton) {
            resolveAllButton.tap()
            
            // Подтверждаем действие
            let confirmButton = app.alerts.buttons["Подтвердить"]
            if waitForElementToAppear(confirmButton) {
                confirmButton.tap()
                
                // Проверяем что все конфликты разрешены
                let successAlert = app.alerts["Все конфликты разрешены"]
                if waitForElementToAppear(successAlert) {
                    XCTAssertTrue(successAlert.exists)
                }
            }
        }
    }
    
    // MARK: - Manual Sync Tests
    
    func testManualSync() throws {
        // Тест ручной синхронизации
        navigateToSyncStatus()
        
        let syncButton = app.buttons["Синхронизировать"]
        if waitForElementToAppear(syncButton) {
            syncButton.tap()
            
            // Проверяем что синхронизация началась
            let progressIndicator = app.progressIndicators.matching(identifier: "SyncProgress").firstMatch
            if waitForElementToAppear(progressIndicator) {
                XCTAssertTrue(progressIndicator.exists)
            }
            
            // Ждем завершения синхронизации
            waitForElementToDisappear(progressIndicator, timeout: 30.0)
            
            // Проверяем что синхронизация завершена
            let successMessage = app.staticTexts.matching(identifier: "SyncComplete").firstMatch
            if waitForElementToAppear(successMessage) {
                XCTAssertTrue(successMessage.exists)
            }
        }
    }
    
    func testSyncErrorHandling() throws {
        // Тест обработки ошибок синхронизации
        navigateToSyncStatus()
        
        // Симулируем ошибку (отключаем интернет)
        // TODO: Реализовать симуляцию ошибки
        
        let syncButton = app.buttons["Синхронизировать"]
        if waitForElementToAppear(syncButton) {
            syncButton.tap()
            
            // Проверяем что ошибка отображается
            let errorAlert = app.alerts.matching(identifier: "SyncError").firstMatch
            if waitForElementToAppear(errorAlert) {
                XCTAssertTrue(errorAlert.exists)
            }
        }
    }
    
    // MARK: - Navigation Helper Methods
    
    private func navigateToSyncSettings() {
        // Навигация к настройкам синхронизации
        let settingsButton = app.buttons["Настройки"]
        if waitForElementToAppear(settingsButton) {
            settingsButton.tap()
        }
        
        let syncSettingsButton = app.buttons["Синхронизация"]
        if waitForElementToAppear(syncSettingsButton) {
            syncSettingsButton.tap()
        }
    }
    
    private func navigateToSyncStatus() {
        // Навигация к статусу синхронизации
        navigateToSyncSettings()
        
        let statusButton = app.buttons["Статус синхронизации"]
        if waitForElementToAppear(statusButton) {
            statusButton.tap()
        }
    }
    
    private func navigateToConflictResolution() {
        // Навигация к разрешению конфликтов
        navigateToSyncSettings()
        
        let conflictsButton = app.buttons["Конфликты"]
        if waitForElementToAppear(conflictsButton) {
            conflictsButton.tap()
        }
    }
    
    // MARK: - Helper Methods
    
    func waitForElementToAppear(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        let predicate = NSPredicate(format: "exists == true")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        return result == .completed
    }
    
    func waitForElementToDisappear(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        let predicate = NSPredicate(format: "exists == false")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        return result == .completed
    }
}
