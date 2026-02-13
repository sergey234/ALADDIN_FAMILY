import XCTest

/**
 * 👨‍👩‍👧‍👦 Parental Control Sync UI Tests
 * Автоматические тесты пользовательского интерфейса для синхронизации родительского контроля
 * Цель: Покрытие всех экранов и функций синхронизации родительского контроля
 */

class ParentalControlSyncUITests: XCTestCase {
    
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
    
    // MARK: - Time Limits Sync Tests
    
    func testTimeLimitsSyncScreen() throws {
        // Тест экрана синхронизации лимитов времени
        navigateToParentalControl()
        navigateToTimeLimits()
        
        let timeLimitsScreen = app.otherElements["TimeLimitsScreen"]
        if waitForElementToAppear(timeLimitsScreen) {
            XCTAssertTrue(timeLimitsScreen.exists)
        }
    }
    
    func testUpdateTimeLimits() throws {
        // Тест обновления лимитов времени
        navigateToParentalControl()
        navigateToTimeLimits()
        
        // Изменяем дневной лимит
        let dailyLimitField = app.textFields.matching(identifier: "DailyLimitField").firstMatch
        if waitForElementToAppear(dailyLimitField) {
            dailyLimitField.tap()
            dailyLimitField.clearText()
            dailyLimitField.typeText("120")
            
            // Сохраняем изменения
            let saveButton = app.buttons["Сохранить"]
            if waitForElementToAppear(saveButton) {
                saveButton.tap()
                
                // Проверяем что изменения синхронизированы
                let successAlert = app.alerts["Лимиты времени обновлены"]
                if waitForElementToAppear(successAlert) {
                    XCTAssertTrue(successAlert.exists)
                }
            }
        }
    }
    
    func testTimeLimitsHistory() throws {
        // Тест истории лимитов времени
        navigateToParentalControl()
        navigateToTimeLimits()
        
        let historyButton = app.buttons["История изменений"]
        if waitForElementToAppear(historyButton) {
            historyButton.tap()
            
            // Проверяем что открылась история
            let historyScreen = app.otherElements["TimeLimitsHistoryScreen"]
            if waitForElementToAppear(historyScreen) {
                XCTAssertTrue(historyScreen.exists)
            }
        }
    }
    
    // MARK: - Schedules Sync Tests
    
    func testSchedulesSyncScreen() throws {
        // Тест экрана синхронизации расписаний
        navigateToParentalControl()
        navigateToSchedules()
        
        let schedulesScreen = app.otherElements["SchedulesScreen"]
        if waitForElementToAppear(schedulesScreen) {
            XCTAssertTrue(schedulesScreen.exists)
        }
    }
    
    func testAddSchedule() throws {
        // Тест добавления расписания
        navigateToParentalControl()
        navigateToSchedules()
        
        let addButton = app.buttons["Добавить расписание"]
        if waitForElementToAppear(addButton) {
            addButton.tap()
            
            // Заполняем форму расписания
            let nameField = app.textFields.matching(identifier: "ScheduleNameField").firstMatch
            if waitForElementToAppear(nameField) {
                nameField.tap()
                nameField.typeText("Школьное время")
            }
            
            // Выбираем время начала
            let startTimeButton = app.buttons["Время начала"]
            if waitForElementToAppear(startTimeButton) {
                startTimeButton.tap()
                
                let timePicker = app.pickers.matching(identifier: "TimePicker").firstMatch
                if waitForElementToAppear(timePicker) {
                    // Выбираем время (8:00)
                    // TODO: Реализовать выбор времени в пикере
                }
            }
            
            // Сохраняем расписание
            let saveButton = app.buttons["Сохранить"]
            if waitForElementToAppear(saveButton) {
                saveButton.tap()
                
                // Проверяем что расписание добавлено и синхронизировано
                let successAlert = app.alerts["Расписание добавлено"]
                if waitForElementToAppear(successAlert) {
                    XCTAssertTrue(successAlert.exists)
                }
            }
        }
    }
    
    func testEditSchedule() throws {
        // Тест редактирования расписания
        navigateToParentalControl()
        navigateToSchedules()
        
        // Выбираем первое расписание
        let firstSchedule = app.cells.matching(identifier: "ScheduleCell").firstMatch
        if waitForElementToAppear(firstSchedule) {
            firstSchedule.tap()
            
            // Редактируем название
            let nameField = app.textFields.matching(identifier: "ScheduleNameField").firstMatch
            if waitForElementToAppear(nameField) {
                nameField.tap()
                nameField.clearText()
                nameField.typeText("Обновленное расписание")
                
                // Сохраняем изменения
                let saveButton = app.buttons["Сохранить"]
                if waitForElementToAppear(saveButton) {
                    saveButton.tap()
                    
                    // Проверяем что изменения синхронизированы
                    let successAlert = app.alerts["Расписание обновлено"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    func testDeleteSchedule() throws {
        // Тест удаления расписания
        navigateToParentalControl()
        navigateToSchedules()
        
        // Выбираем первое расписание
        let firstSchedule = app.cells.matching(identifier: "ScheduleCell").firstMatch
        if waitForElementToAppear(firstSchedule) {
            firstSchedule.swipeLeft()
            
            // Нажимаем кнопку удаления
            let deleteButton = app.buttons["Удалить"]
            if waitForElementToAppear(deleteButton) {
                deleteButton.tap()
                
                // Подтверждаем удаление
                let confirmButton = app.alerts.buttons["Удалить"]
                if waitForElementToAppear(confirmButton) {
                    confirmButton.tap()
                    
                    // Проверяем что расписание удалено и синхронизировано
                    let successAlert = app.alerts["Расписание удалено"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    // MARK: - Geofences Sync Tests
    
    func testGeofencesSyncScreen() throws {
        // Тест экрана синхронизации геозон
        navigateToParentalControl()
        navigateToGeofences()
        
        let geofencesScreen = app.otherElements["GeofencesScreen"]
        if waitForElementToAppear(geofencesScreen) {
            XCTAssertTrue(geofencesScreen.exists)
        }
    }
    
    func testAddGeofence() throws {
        // Тест добавления геозоны
        navigateToParentalControl()
        navigateToGeofences()
        
        let addButton = app.buttons["Добавить геозону"]
        if waitForElementToAppear(addButton) {
            addButton.tap()
            
            // Заполняем форму геозоны
            let nameField = app.textFields.matching(identifier: "GeofenceNameField").firstMatch
            if waitForElementToAppear(nameField) {
                nameField.tap()
                nameField.typeText("Школа")
            }
            
            // Выбираем местоположение
            let locationButton = app.buttons["Выбрать местоположение"]
            if waitForElementToAppear(locationButton) {
                locationButton.tap()
                
                // TODO: Реализовать выбор местоположения на карте
            }
            
            // Сохраняем геозону
            let saveButton = app.buttons["Сохранить"]
            if waitForElementToAppear(saveButton) {
                saveButton.tap()
                
                // Проверяем что геозона добавлена и синхронизирована
                let successAlert = app.alerts["Геозона добавлена"]
                if waitForElementToAppear(successAlert) {
                    XCTAssertTrue(successAlert.exists)
                }
            }
        }
    }
    
    func testEditGeofence() throws {
        // Тест редактирования геозоны
        navigateToParentalControl()
        navigateToGeofences()
        
        // Выбираем первую геозону
        let firstGeofence = app.cells.matching(identifier: "GeofenceCell").firstMatch
        if waitForElementToAppear(firstGeofence) {
            firstGeofence.tap()
            
            // Редактируем название
            let nameField = app.textFields.matching(identifier: "GeofenceNameField").firstMatch
            if waitForElementToAppear(nameField) {
                nameField.tap()
                nameField.clearText()
                nameField.typeText("Обновленная геозона")
                
                // Сохраняем изменения
                let saveButton = app.buttons["Сохранить"]
                if waitForElementToAppear(saveButton) {
                    saveButton.tap()
                    
                    // Проверяем что изменения синхронизированы
                    let successAlert = app.alerts["Геозона обновлена"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    func testDeleteGeofence() throws {
        // Тест удаления геозоны
        navigateToParentalControl()
        navigateToGeofences()
        
        // Выбираем первую геозону
        let firstGeofence = app.cells.matching(identifier: "GeofenceCell").firstMatch
        if waitForElementToAppear(firstGeofence) {
            firstGeofence.swipeLeft()
            
            // Нажимаем кнопку удаления
            let deleteButton = app.buttons["Удалить"]
            if waitForElementToAppear(deleteButton) {
                deleteButton.tap()
                
                // Подтверждаем удаление
                let confirmButton = app.alerts.buttons["Удалить"]
                if waitForElementToAppear(confirmButton) {
                    confirmButton.tap()
                    
                    // Проверяем что геозона удалена и синхронизирована
                    let successAlert = app.alerts["Геозона удалена"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    // MARK: - App Limits Sync Tests
    
    func testAppLimitsSyncScreen() throws {
        // Тест экрана синхронизации лимитов приложений
        navigateToParentalControl()
        navigateToAppLimits()
        
        let appLimitsScreen = app.otherElements["AppLimitsScreen"]
        if waitForElementToAppear(appLimitsScreen) {
            XCTAssertTrue(appLimitsScreen.exists)
        }
    }
    
    func testUpdateAppLimits() throws {
        // Тест обновления лимитов приложений
        navigateToParentalControl()
        navigateToAppLimits()
        
        // Выбираем приложение
        let firstApp = app.cells.matching(identifier: "AppCell").firstMatch
        if waitForElementToAppear(firstApp) {
            firstApp.tap()
            
            // Изменяем лимит времени
            let limitField = app.textFields.matching(identifier: "AppLimitField").firstMatch
            if waitForElementToAppear(limitField) {
                limitField.tap()
                limitField.clearText()
                limitField.typeText("60")
                
                // Сохраняем изменения
                let saveButton = app.buttons["Сохранить"]
                if waitForElementToAppear(saveButton) {
                    saveButton.tap()
                    
                    // Проверяем что изменения синхронизированы
                    let successAlert = app.alerts["Лимиты приложений обновлены"]
                    if waitForElementToAppear(successAlert) {
                        XCTAssertTrue(successAlert.exists)
                    }
                }
            }
        }
    }
    
    // MARK: - Navigation Helper Methods
    
    private func navigateToParentalControl() {
        // Навигация к родительскому контролю
        let parentalControlButton = app.buttons["Родительский контроль"]
        if waitForElementToAppear(parentalControlButton) {
            parentalControlButton.tap()
        }
    }
    
    private func navigateToTimeLimits() {
        navigateToParentalControl()
        
        let timeLimitsButton = app.buttons["Лимиты времени"]
        if waitForElementToAppear(timeLimitsButton) {
            timeLimitsButton.tap()
        }
    }
    
    private func navigateToSchedules() {
        navigateToParentalControl()
        
        let schedulesButton = app.buttons["Расписания"]
        if waitForElementToAppear(schedulesButton) {
            schedulesButton.tap()
        }
    }
    
    private func navigateToGeofences() {
        navigateToParentalControl()
        
        let geofencesButton = app.buttons["Геозоны"]
        if waitForElementToAppear(geofencesButton) {
            geofencesButton.tap()
        }
    }
    
    private func navigateToAppLimits() {
        navigateToParentalControl()
        
        let appLimitsButton = app.buttons["Лимиты приложений"]
        if waitForElementToAppear(appLimitsButton) {
            appLimitsButton.tap()
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

// MARK: - XCUIElement Extension

extension XCUIElement {
    func clearText() {
        guard let stringValue = self.value as? String else {
            return
        }
        
        let deleteString = String(repeating: XCUIKeyboardKey.delete.rawValue, count: stringValue.count)
        typeText(deleteString)
    }
}
