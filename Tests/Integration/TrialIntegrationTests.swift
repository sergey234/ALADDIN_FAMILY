import XCTest
import SwiftUI
@testable import ALADDIN

/**
 * 🧪 Trial Integration Tests
 * Комплексное тестирование trial flow от первого запуска до истечения
 */
@MainActor
class TrialIntegrationTests: XCTestCase {

    var subscriptionManager: SubscriptionManager!
    var notificationManager: NotificationManager!
    var subscriptionMonitor: SubscriptionMonitor!

    // MARK: - Setup

    override func setUp() {
        super.setUp()

        // Инициализация менеджеров
        subscriptionManager = SubscriptionManager.shared
        notificationManager = NotificationManager.shared
        subscriptionMonitor = SubscriptionMonitor.shared

        // Очистка состояния перед каждым тестом
        clearAppState()
    }

    override func tearDown() {
        // Очистка после каждого теста
        clearAppState()
        super.tearDown()
    }

    // MARK: - Test Cases

    /**
     * ✅ Test 4.1: Trial activation flow from first launch to expiration
     * Проверяет полный цикл trial: активация → использование → истечение → переход на free
     */
    func testTrialActivationFlow() async throws {
        print("🧪 [TrialIntegrationTests] Starting trial activation flow test")

        // ШАГ 1: Первый запуск приложения (симуляция)
        // Проверяем что trial не активирован
        XCTAssertFalse(subscriptionManager.hasTrialBeenActivated, "Trial should not be activated initially")

        // ШАГ 2: Активация trial при первом запуске
        await subscriptionManager.activateTrialIfNeeded()

        // Проверяем что trial активирован
        XCTAssertTrue(subscriptionManager.hasTrialBeenActivated, "Trial should be activated after first launch")

        // Проверяем что есть активная подписка
        XCTAssertNotNil(subscriptionManager.currentSubscription, "Should have active subscription after trial activation")

        if let subscription = subscriptionManager.currentSubscription {
            XCTAssertEqual(subscription.level, .trial, "Subscription level should be trial")
            XCTAssertTrue(subscription.isActive, "Trial subscription should be active")
            XCTAssertNotNil(subscription.expiresDate, "Trial should have expiration date")
            XCTAssertNotNil(subscription.trialInfo, "Trial should have trial info")
        }

        // ШАГ 3: Проверяем уведомления trial
        // Проверяем что уведомления запланированы
        let pendingNotifications = await getPendingNotifications()
        let trialNotifications = pendingNotifications.filter { notification in
            notification.content.categoryIdentifier == NotificationCategory.trial.rawValue
        }
        XCTAssertFalse(trialNotifications.isEmpty, "Trial notifications should be scheduled")

        // ШАГ 4: Симуляция использования функций во время trial
        // Проверяем что все premium функции доступны
        await testPremiumFeaturesAccess(duringTrial: true)

        // ШАГ 5: Симуляция истечения trial
        await simulateTrialExpiration()

        // Проверяем что trial истек
        XCTAssertTrue(subscriptionMonitor.isExpired, "Trial should be expired after simulation")

        // Проверяем что подписка перешла на free
        if let subscription = subscriptionManager.currentSubscription {
            XCTAssertEqual(subscription.level, .free, "Should downgrade to free after trial expiration")
            XCTAssertTrue(subscription.isActive, "Free subscription should be active")
        }

        // ШАГ 6: Проверяем уведомления об истечении
        let expiredNotifications = await getPendingNotifications().filter { notification in
            notification.content.categoryIdentifier == NotificationCategory.subscription.rawValue &&
            notification.content.userInfo["type"] as? String == "subscription_expired"
        }
        XCTAssertFalse(expiredNotifications.isEmpty, "Expired subscription notifications should be scheduled")

        // ШАГ 7: Проверяем блокировку premium функций после истечения
        await testPremiumFeaturesAccess(duringTrial: false)

        print("✅ [TrialIntegrationTests] Trial activation flow test completed successfully")
    }

    /**
     * Тест повторной активации trial (должен быть заблокирован)
     */
    func testTrialReusePrevention() async throws {
        print("🧪 [TrialIntegrationTests] Testing trial reuse prevention")

        // Первая активация
        await subscriptionManager.activateTrialIfNeeded()
        XCTAssertTrue(subscriptionManager.hasTrialBeenActivated, "Trial should be activated")

        // Попытка повторной активации
        await subscriptionManager.activateTrialIfNeeded()

        // Проверяем что trial все еще активен, но не продлен
        if let subscription = subscriptionManager.currentSubscription {
            XCTAssertEqual(subscription.level, .trial, "Should remain on trial level")
            // Проверяем что дата истечения не изменилась (сложно без mock времени)
        }

        print("✅ [TrialIntegrationTests] Trial reuse prevention test completed")
    }

    /**
     * Тест background мониторинга trial
     */
    func testTrialBackgroundMonitoring() async throws {
        print("🧪 [TrialIntegrationTests] Testing trial background monitoring")

        // Активация trial
        await subscriptionManager.activateTrialIfNeeded()

        // Запуск мониторинга
        subscriptionMonitor.startMonitoring()
        XCTAssertTrue(subscriptionMonitor.isMonitoring, "Monitor should be active")

        // Имитация background task
        await subscriptionMonitor.checkSubscriptionStatus()

        // Проверяем что мониторинг работает
        XCTAssertNotNil(subscriptionMonitor.timeUntilExpiration, "Should track time until expiration")

        // Остановка мониторинга
        subscriptionMonitor.stopMonitoring()
        XCTAssertFalse(subscriptionMonitor.isMonitoring, "Monitor should be stopped")

        print("✅ [TrialIntegrationTests] Background monitoring test completed")
    }

    // MARK: - Helper Methods

    private func clearAppState() {
        // Очистка UserDefaults для тестов
        UserDefaults.standard.removeObject(forKey: "has_trial_been_activated")
        UserDefaults.standard.removeObject(forKey: SubscriptionManager.trialEndDateKey)
        UserDefaults.standard.removeObject(forKey: SubscriptionManager.currentSubscriptionKey)

        // Очистка уведомлений
        notificationCenter.removeAllPendingNotificationRequests()
        notificationCenter.removeAllDeliveredNotifications()
    }

    private func testPremiumFeaturesAccess(duringTrial: Bool) async {
        // Здесь можно добавить проверки доступа к premium функциям
        // Для интеграционных тестов это может быть сложно без UI

        print("🔍 [TrialIntegrationTests] Testing premium features access (trial: \(duringTrial))")

        // Проверяем что SubscriptionManager правильно определяет уровень доступа
        let hasTrialAccess = subscriptionManager.currentSubscription?.level == .trial
        let hasFreeAccess = subscriptionManager.currentSubscription?.level == .free

        if duringTrial {
            XCTAssertTrue(hasTrialAccess, "Should have trial access during trial period")
        } else {
            XCTAssertTrue(hasFreeAccess, "Should have free access after trial expiration")
        }
    }

    private func simulateTrialExpiration() async {
        // В реальном тесте можно использовать mock время или dependency injection
        // Для интеграционного теста просто устанавливаем прошедшую дату

        print("⏰ [TrialIntegrationTests] Simulating trial expiration")

        // Устанавливаем прошедшую дату истечения
        let expiredDate = Date().addingTimeInterval(-24 * 60 * 60) // 1 день назад
        UserDefaults.standard.set(expiredDate, forKey: SubscriptionManager.trialEndDateKey)

        // Обновляем subscription manager
        await subscriptionManager.loadCurrentSubscription()
    }

    private func getPendingNotifications() async -> [UNNotificationRequest] {
        return await withCheckedContinuation { continuation in
            notificationCenter.getPendingNotificationRequests { requests in
                continuation.resume(returning: requests)
            }
        }
    }

    private var notificationCenter: UNUserNotificationCenter {
        UNUserNotificationCenter.current()
    }
}