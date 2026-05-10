import XCTest

/**
 * 🔔 Notification Settings UI Tests
 * Тестирование экрана настроек уведомлений
 */

@MainActor
final class NotificationSettingsUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    // MARK: - Notification Settings Tests
    
    func testNotificationSettingsScreenDisplay() throws {
        navigateToNotificationSettings()
        
        // Проверяем заголовок экрана
        let title = app.staticTexts["notification.settings"]
        XCTAssertTrue(title.exists, "Заголовок экрана настроек уведомлений должен отображаться")
        
        // Проверяем наличие всех переключателей
        let securityToggle = app.switches["notification.security"]
        let familyToggle = app.switches["notification.family"]
        let vpnToggle = app.switches["notification.vpn"]
        let aiToggle = app.switches["notification.ai"]
        
        XCTAssertTrue(securityToggle.exists, "Переключатель уведомлений безопасности должен быть доступен")
        XCTAssertTrue(familyToggle.exists, "Переключатель семейных уведомлений должен быть доступен")
        XCTAssertTrue(vpnToggle.exists, "Переключатель VPN уведомлений должен быть доступен")
        XCTAssertTrue(aiToggle.exists, "Переключатель AI уведомлений должен быть доступен")
    }
    
    func testNotificationToggles() throws {
        navigateToNotificationSettings()
        
        // Тестируем переключатель безопасности
        let securityToggle = app.switches["notification.security"]
        let initialValue = securityToggle.value as? String
        
        securityToggle.tap()
        
        // Проверяем, что значение изменилось
        let newValue = securityToggle.value as? String
        XCTAssertNotEqual(initialValue, newValue, "Значение переключателя должно измениться")
    }
    
    func testSoundAndBadgeSettings() throws {
        navigateToNotificationSettings()
        
        // Проверяем настройки звука и бейджа
        let soundToggle = app.switches["notification.sound"]
        let badgeToggle = app.switches["notification.badge"]
        
        XCTAssertTrue(soundToggle.exists, "Переключатель звука должен быть доступен")
        XCTAssertTrue(badgeToggle.exists, "Переключатель бейджа должен быть доступен")
        
        // Тестируем переключение
        soundToggle.tap()
        badgeToggle.tap()
    }
    
    func testQuietHoursSettings() throws {
        navigateToNotificationSettings()
        
        // Проверяем настройки тихих часов
        let quietHoursToggle = app.switches["notification.quiet_hours"]
        XCTAssertTrue(quietHoursToggle.exists, "Переключатель тихих часов должен быть доступен")
        
        // Включаем тихие часы
        quietHoursToggle.tap()
        
        // Проверяем, что появились настройки времени
        let startTimePicker = app.datePickers["quiet_hours_start"]
        let endTimePicker = app.datePickers["quiet_hours_end"]
        
        if quietHoursToggle.value as? String == "1" {
            XCTAssertTrue(startTimePicker.exists, "Пикер времени начала должен появиться")
            XCTAssertTrue(endTimePicker.exists, "Пикер времени окончания должен появиться")
        }
    }
    
    func testTestNotificationButtons() throws {
        navigateToNotificationSettings()
        
        // Проверяем кнопки тестовых уведомлений
        let securityTestButton = app.buttons["notification.test_security"]
        let familyTestButton = app.buttons["notification.test_family"]
        let vpnTestButton = app.buttons["notification.test_vpn"]
        let aiTestButton = app.buttons["notification.test_ai"]
        
        XCTAssertTrue(securityTestButton.exists, "Кнопка тестового уведомления безопасности должна быть доступна")
        XCTAssertTrue(familyTestButton.exists, "Кнопка тестового семейного уведомления должна быть доступна")
        XCTAssertTrue(vpnTestButton.exists, "Кнопка тестового VPN уведомления должна быть доступна")
        XCTAssertTrue(aiTestButton.exists, "Кнопка тестового AI уведомления должна быть доступна")
        
        // Тестируем отправку уведомления
        securityTestButton.tap()
        
        // Проверяем, что появилось подтверждение
        let alert = app.alerts.firstMatch
        if alert.exists {
            XCTAssertTrue(alert.staticTexts["notification.sent"].exists, "Должно появиться подтверждение отправки")
            alert.buttons["OK"].tap()
        }
    }
    
    func testNotificationPermissionRequest() throws {
        navigateToNotificationSettings()
        
        // Ищем кнопку запроса разрешений
        let permissionButton = app.buttons["notification.request_permission"]
        if permissionButton.exists {
            permissionButton.tap()
            
            // Проверяем, что появился системный диалог разрешений
            let allowButton = app.buttons["Allow"]
            let dontAllowButton = app.buttons["Don't Allow"]
            
            if allowButton.exists {
                allowButton.tap()
            } else if dontAllowButton.exists {
                dontAllowButton.tap()
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func navigateToNotificationSettings() {
        // Находим кнопку настроек
        let settingsButton = app.buttons["settings"]
        if settingsButton.exists {
            settingsButton.tap()
        }
        
        // Ищем кнопку настроек уведомлений
        let notificationButton = app.buttons["notification.settings"]
        if notificationButton.exists {
            notificationButton.tap()
        }
    }
}
