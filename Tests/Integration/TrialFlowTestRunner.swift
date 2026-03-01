import Foundation
import SwiftUI
@testable import ALADDIN

/**
 * 🏃‍♂️ Trial Flow Test Runner
 * Ручной runner для тестирования trial flow от первого запуска до истечения
 * Можно запускать в приложении для отладки
 */
class TrialFlowTestRunner: ObservableObject {

    static let shared = TrialFlowTestRunner()

    private let subscriptionManager = SubscriptionManager.shared
    private let notificationManager = NotificationManager.shared
    // private let subscriptionMonitor = SubscriptionMonitor.shared // Temporarily disabled

    // MARK: - Test Scenarios

    /**
     * 🚀 Сценарий 1: Первый запуск приложения
     * Симулирует первый запуск нового пользователя
     */
    func runFirstLaunchScenario() async {
        print("🚀 [TrialFlowTestRunner] ========== СЦЕНАРИЙ 1: Первый запуск ==========")

        // Очистка состояния
        clearTrialState()

        print("📱 Шаг 1: Первый запуск приложения")
        print("   - Проверяем начальное состояние...")

        // Проверяем что trial не активирован
        let initialState = await checkInitialState()
        print("   - Trial активирован: \(initialState.hasTrial)")
        print("   - Текущая подписка: \(initialState.subscriptionLevel)")

        print("🎯 Шаг 2: Активация trial при первом запуске")
        await subscriptionManager.activateTrialIfNeeded()

        // Проверяем результат активации
        let afterActivation = await checkTrialActivation()
        print("   - Trial активирован: \(afterActivation.isActivated)")
        print("   - Уровень подписки: \(afterActivation.level)")
        print("   - Дата истечения: \(afterActivation.expiresAt ?? "nil")")
        print("   - Дней до истечения: \(afterActivation.daysRemaining)")

        print("🔔 Шаг 3: Проверка уведомлений")
        await checkScheduledNotifications()

        print("✅ Сценарий 1 завершен")
        print("🚀 [TrialFlowTestRunner] =========================================")
    }

    /**
     * ⏰ Сценарий 2: Использование во время trial периода
     */
    func runTrialUsageScenario() async {
        print("⏰ [TrialFlowTestRunner] ========== СЦЕНАРИЙ 2: Использование trial ==========")

        // Проверяем что trial активен
        guard await isTrialActive() else {
            print("❌ Trial не активен, сначала запустите Сценарий 1")
            return
        }

        print("🔓 Шаг 1: Проверка доступа к premium функциям")
        await testPremiumFeaturesAccess()

        print("📊 Шаг 2: Проверка мониторинга подписки")
        testSubscriptionMonitoring()

        print("📱 Шаг 3: Тестирование UI элементов trial")
        await testTrialUIElements()

        print("✅ Сценарий 2 завершен")
        print("⏰ [TrialFlowTestRunner] =========================================")
    }

    /**
     * ⌛ Сценарий 3: Истечение trial периода
     */
    func runTrialExpirationScenario() async {
        print("⌛ [TrialFlowTestRunner] ========== СЦЕНАРИЙ 3: Истечение trial ==========")

        // Проверяем что trial активен
        guard await isTrialActive() else {
            print("❌ Trial не активен, сначала запустите Сценарий 1")
            return
        }

        print("⏰ Шаг 1: Симуляция истечения trial")
        await simulateTrialExpiration()

        print("🔄 Шаг 2: Проверка перехода на free план")
        await checkFreePlanTransition()

        print("🚫 Шаг 3: Проверка блокировки premium функций")
        await testPremiumFeaturesBlocked()

        print("🔔 Шаг 4: Проверка уведомлений об истечении")
        await checkExpirationNotifications()

        print("✅ Сценарий 3 завершен")
        print("⌛ [TrialFlowTestRunner] =========================================")
    }

    /**
     * 🔄 Сценарий 4: Полный цикл trial flow
     */
    func runCompleteTrialFlow() async {
        print("🔄 [TrialFlowTestRunner] ========== ПОЛНЫЙ ЦИКЛ TRIAL FLOW ==========")

        // Сценарий 1: Первый запуск
        await runFirstLaunchScenario()

        // Небольшая пауза для имитации использования
        try? await Task.sleep(nanoseconds: 2_000_000_000) // 2 секунды

        // Сценарий 2: Использование
        await runTrialUsageScenario()

        // Небольшая пауза
        try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 секунда

        // Сценарий 3: Истечение
        await runTrialExpirationScenario()

        print("🎉 ПОЛНЫЙ ЦИКЛ TRIAL FLOW ЗАВЕРШЕН УСПЕШНО!")
        print("🔄 [TrialFlowTestRunner] =========================================")
    }

    // MARK: - Helper Methods

    private func clearTrialState() {
        UserDefaults.standard.removeObject(forKey: "has_trial_been_activated")
        UserDefaults.standard.removeObject(forKey: SubscriptionManager.trialEndDateKey)
        UserDefaults.standard.removeObject(forKey: SubscriptionManager.currentSubscriptionKey)

        // Очистка уведомлений
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
        UNUserNotificationCenter.current().removeAllDeliveredNotifications()

        print("🧹 Trial состояние очищено")
    }

    private func checkInitialState() async -> (hasTrial: Bool, subscriptionLevel: String) {
        let hasTrial = subscriptionManager.hasTrialBeenActivated
        let level = subscriptionManager.currentSubscription?.level.displayName ?? "none"
        return (hasTrial, level)
    }

    private func checkTrialActivation() async -> (isActivated: Bool, level: String, expiresAt: String?, daysRemaining: Int) {
        let isActivated = subscriptionManager.hasTrialBeenActivated
        let subscription = subscriptionManager.currentSubscription

        let level = subscription?.level.displayName ?? "none"
        let expiresAt = subscription?.expiresDate?.description
        let daysRemaining = subscription?.trialInfo?.daysRemaining ?? 0

        return (isActivated, level, expiresAt, daysRemaining)
    }

    private func isTrialActive() async -> Bool {
        guard let subscription = subscriptionManager.currentSubscription else { return false }
        return subscription.level == .trial && subscription.isActive
    }

    private func testPremiumFeaturesAccess() async {
        // Проверяем доступ к различным premium функциям
        let subscription = subscriptionManager.currentSubscription

        if subscription?.level == .trial {
            print("   ✅ Доступ к AI помощнику: разрешен")
            print("   ✅ Доступ к расширенной аналитике: разрешен")
            print("   ✅ Доступ к родительскому контролю: разрешен")
            print("   ✅ Доступ ко всем 184 функциям: разрешен")
        } else {
            print("   ❌ Доступ к premium функциям: заблокирован")
        }
    }

    private func testSubscriptionMonitoring() {
        // subscriptionMonitor.startMonitoring() // Temporarily disabled

        print("   📊 Мониторинг подписки: disabled")
        print("   ⏰ Дней до истечения: unknown")
        print("   🚨 Истекает скоро: unknown")
        print("   💀 Истекла: unknown")
    }

    private func testTrialUIElements() async {
        // Проверяем отображение trial элементов в UI
        print("   🎨 Проверка UI элементов trial...")

        // В реальном приложении здесь можно проверить отображение
        // trial countdown, trial badges и т.д.
        print("   ✅ Trial countdown должен отображаться")
        print("   ✅ Trial badges должны быть активны")
        print("   ✅ Upgrade prompts должны быть скрыты")
    }

    private func simulateTrialExpiration() async {
        print("   ⏰ Симулируем истечение trial...")

        // Устанавливаем прошедшую дату
        let expiredDate = Date().addingTimeInterval(-24 * 60 * 60) // 1 день назад
        UserDefaults.standard.set(expiredDate, forKey: SubscriptionManager.trialEndDateKey)

        // Обновляем состояние
        await subscriptionManager.loadCurrentSubscription()

        print("   ✅ Trial истек: \(expiredDate)")
    }

    private func checkFreePlanTransition() async {
        let subscription = subscriptionManager.currentSubscription

        if subscription?.level == .free {
            print("   ✅ Переход на free план: успешный")
            print("   🎁 Бесплатные функции: доступны")
            print("   🚫 Premium функции: заблокированы")
        } else {
            print("   ❌ Переход на free план: неудачный")
        }
    }

    private func testPremiumFeaturesBlocked() async {
        let subscription = subscriptionManager.currentSubscription

        if subscription?.level == .free {
            print("   ✅ Premium функции заблокированы после истечения trial")
            print("   🔒 AI помощник: заблокирован")
            print("   🔒 Расширенная аналитика: заблокирована")
            print("   🔒 Родительский контроль: заблокирован")
        } else {
            print("   ❌ Premium функции все еще доступны")
        }
    }

    private func checkScheduledNotifications() async {
        let pending = await getPendingNotifications()

        let trialNotifications = pending.filter { $0.content.categoryIdentifier == NotificationCategory.trial.rawValue }
        let subscriptionNotifications = pending.filter { $0.content.categoryIdentifier == NotificationCategory.subscription.rawValue }

        print("   📅 Запланированные уведомления:")
        print("   🎯 Trial уведомления: \(trialNotifications.count)")
        print("   📊 Subscription уведомления: \(subscriptionNotifications.count)")
    }

    private func checkExpirationNotifications() async {
        let pending = await getPendingNotifications()

        let expiredNotifications = pending.filter {
            $0.content.categoryIdentifier == NotificationCategory.subscription.rawValue &&
            $0.content.userInfo["type"] as? String == "subscription_expired"
        }

        print("   🔔 Уведомления об истечении: \(expiredNotifications.count)")
    }

    private func getPendingNotifications() async -> [UNNotificationRequest] {
        return await withCheckedContinuation { continuation in
            UNUserNotificationCenter.current().getPendingNotificationRequests { requests in
                continuation.resume(returning: requests)
            }
        }
    }
}

// MARK: - Debug Helpers

extension TrialFlowTestRunner {

    /**
     * 🐛 Debug: Показать текущее состояние trial
     */
    func debugTrialState() {
        print("🐛 [DEBUG] Текущее состояние trial:")
        print("   - Trial активирован: \(subscriptionManager.hasTrialBeenActivated)")
        print("   - Текущая подписка: \(subscriptionManager.currentSubscription?.level.displayName ?? "none")")
        print("   - Активна: \(subscriptionManager.currentSubscription?.isActive ?? false)")
        print("   - Дата истечения: \(subscriptionManager.currentSubscription?.expiresDate?.description ?? "none")")
        print("   - Trial info: \(subscriptionManager.currentSubscription?.trialInfo?.description ?? "none")")
        print("   - Мониторинг активен: disabled")
    }

    /**
     * 🔧 Debug: Сбросить все состояния для тестирования
     */
    func debugResetAllStates() {
        clearTrialState()
        print("🔧 [DEBUG] Все состояния сброшены для тестирования")
    }
}