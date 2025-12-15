import XCTest
@testable import ALADDIN

/**
 * 🔔 NotificationManager Unit Tests
 * Тестирование менеджера уведомлений
 */

final class NotificationManagerTests: XCTestCase {
    
    private var notificationManager: NotificationManager!
    private var originalSettings: NotificationSettings!
    
    override func setUpWithError() throws {
        notificationManager = NotificationManager.shared
        originalSettings = notificationManager.notificationSettings
    }
    
    override func tearDownWithError() throws {
        if let originalSettings = originalSettings {
            notificationManager.updateNotificationSettings(originalSettings)
        }
        notificationManager = nil
        originalSettings = nil
    }
    
    func testDefaultNotificationSettingsMatchStructDefaults() {
        let defaults = NotificationSettings()
        notificationManager.updateNotificationSettings(defaults)
        XCTAssertEqual(notificationManager.notificationSettings, defaults, "Настройки по умолчанию должны совпадать с NotificationSettings()")
    }
    
    func testUpdateNotificationSettingsPersistsChanges() {
        var updatedSettings = notificationManager.notificationSettings
        updatedSettings.securityEnabled.toggle()
        updatedSettings.soundEnabled.toggle()
        updatedSettings.badgeEnabled.toggle()
        
        notificationManager.updateNotificationSettings(updatedSettings)
        
        XCTAssertEqual(notificationManager.notificationSettings, updatedSettings, "Обновленные настройки должны сохраняться в менеджере")
    }
    
    func testSendLocalNotificationDoesNotThrow() {
        XCTAssertNoThrow(
            notificationManager.sendLocalNotification(
                title: "Test Title",
                body: "Test Body",
                category: .security,
                userInfo: ["type": "security_test"],
                delay: 0.1
            )
        )
    }
    
    func testSetupNotificationCategoriesDoesNotThrow() {
        XCTAssertNoThrow(notificationManager.setupNotificationCategories())
    }
}
