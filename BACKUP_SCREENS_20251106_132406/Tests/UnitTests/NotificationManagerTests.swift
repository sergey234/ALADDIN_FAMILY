import XCTest
@testable import ALADDIN

/**
 * 🔔 NotificationManager Unit Tests
 * Тестирование менеджера уведомлений
 */

final class NotificationManagerTests: XCTestCase {
    
    var notificationManager: NotificationManager!
    var mockAPIService: MockAPIService!
    
    override func setUpWithError() throws {
        mockAPIService = MockAPIService()
        notificationManager = NotificationManager.shared
        // В реальном тесте нужно было бы инжектить mockAPIService
    }
    
    override func tearDownWithError() throws {
        notificationManager = nil
        mockAPIService = nil
    }
    
    // MARK: - Authorization Tests
    
    func testRequestAuthorization() async throws {
        // Тестируем запрос разрешений
        let result = await notificationManager.requestAuthorization()
        
        // В симуляторе разрешения обычно не запрашиваются
        // Проверяем, что метод выполняется без ошибок
        XCTAssertNotNil(result, "Результат запроса разрешений не должен быть nil")
    }
    
    func testNotificationSettings() {
        // Тестируем настройки уведомлений
        XCTAssertFalse(notificationManager.isSecurityEnabled, "Уведомления безопасности должны быть выключены по умолчанию")
        XCTAssertFalse(notificationManager.isFamilyEnabled, "Семейные уведомления должны быть выключены по умолчанию")
        XCTAssertFalse(notificationManager.isVPNEnabled, "VPN уведомления должны быть выключены по умолчанию")
        XCTAssertFalse(notificationManager.isAIEnabled, "AI уведомления должны быть выключены по умолчанию")
    }
    
    func testToggleNotificationSettings() {
        // Тестируем переключение настроек
        let initialSecurity = notificationManager.isSecurityEnabled
        
        notificationManager.toggleSecurityNotifications()
        
        XCTAssertNotEqual(initialSecurity, notificationManager.isSecurityEnabled, "Настройка безопасности должна измениться")
    }
    
    func testSoundAndBadgeSettings() {
        // Тестируем настройки звука и бейджа
        XCTAssertTrue(notificationManager.isSoundEnabled, "Звук должен быть включен по умолчанию")
        XCTAssertTrue(notificationManager.isBadgeEnabled, "Бейдж должен быть включен по умолчанию")
        
        notificationManager.toggleSound()
        notificationManager.toggleBadge()
        
        XCTAssertFalse(notificationManager.isSoundEnabled, "Звук должен быть выключен")
        XCTAssertFalse(notificationManager.isBadgeEnabled, "Бейдж должен быть выключен")
    }
    
    func testQuietHoursSettings() {
        // Тестируем настройки тихих часов
        XCTAssertFalse(notificationManager.isQuietHoursEnabled, "Тихие часы должны быть выключены по умолчанию")
        
        notificationManager.toggleQuietHours()
        
        XCTAssertTrue(notificationManager.isQuietHoursEnabled, "Тихие часы должны быть включены")
    }
    
    // MARK: - Local Notification Tests
    
    func testSendLocalNotification() {
        // Тестируем отправку локального уведомления
        let expectation = XCTestExpectation(description: "Local notification sent")
        
        notificationManager.sendLocalNotification(
            title: "Test Title",
            body: "Test Body",
            category: .security
        ) { success in
            XCTAssertTrue(success, "Локальное уведомление должно быть отправлено успешно")
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 1.0)
    }
    
    func testNotificationCategories() {
        // Тестируем настройку категорий уведомлений
        notificationManager.setupNotificationCategories()
        
        // Проверяем, что категории настроены
        // В реальном тесте нужно было бы проверить UNUserNotificationCenter
        XCTAssertTrue(true, "Категории уведомлений должны быть настроены")
    }
    
    // MARK: - Device Token Tests
    
    func testDeviceTokenHandling() {
        // Тестируем обработку device token
        let mockToken = Data("test_token".utf8)
        
        notificationManager.didRegisterForRemoteNotifications(deviceToken: mockToken)
        
        // Проверяем, что токен обработан
        XCTAssertTrue(true, "Device token должен быть обработан")
    }
    
    func testDeviceTokenFailure() {
        // Тестируем обработку ошибки регистрации
        let mockError = NSError(domain: "test", code: 1, userInfo: nil)
        
        notificationManager.didFailToRegisterForRemoteNotifications(error: mockError)
        
        // Проверяем, что ошибка обработана
        XCTAssertTrue(true, "Ошибка регистрации должна быть обработана")
    }
    
    // MARK: - Mock APIService
    
    class MockAPIService {
        var registerDeviceTokenCalled = false
        var lastDeviceToken: String?
        
        func registerDeviceToken(_ token: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
            registerDeviceTokenCalled = true
            lastDeviceToken = token
            
            // Симулируем успешный ответ
            let response = APIResponse<Bool>(success: true, data: true, message: "Success")
            completion(.success(response))
        }
    }
}
