import Foundation
import BackgroundTasks

// Master Logger for subscription monitoring
private let logger = MasterLogger.shared

/**
 * 📊 Subscription Monitor Service
 * Мониторинг подписок и планирование уведомлений об истечении
 * Background task для периодической проверки состояния подписки
 */
class SubscriptionMonitor: ObservableObject {

    // MARK: - Singleton

    static let shared = SubscriptionMonitor()

    // MARK: - Properties

    @Published private(set) var isMonitoring: Bool = false
    private let subscriptionManager = SubscriptionManager.shared
    private let notificationManager = NotificationManager.shared
    private let userDefaults = UserDefaults.standard

    // Keys for UserDefaults
    private let lastCheckKey = "subscriptionLastCheckDate"
    private let monitoringEnabledKey = "subscriptionMonitoringEnabled"

    // Background task identifier
    private let backgroundTaskIdentifier = "com.aladdin.subscription.monitor"

    // MARK: - Init

    private init() {
        logger.business("Initializing SubscriptionMonitor")

        // Register background task
        registerBackgroundTask()

        // Start monitoring if enabled
        if isMonitoringEnabled {
            startMonitoring()
        }
    }

    // MARK: - Public Methods

    /**
     * Запустить мониторинг подписки
     */
    func startMonitoring() {
        logger.business("Starting subscription monitoring")

        guard !isMonitoring else {
            logger.business("Monitoring already active")
            return
        }

        isMonitoring = true
        monitoringEnabled = true

        // Немедленная проверка при запуске
        checkSubscriptionStatus()

        // Запланировать background task
        scheduleBackgroundTask()

        logger.business("Subscription monitoring started")
    }

    /**
     * Остановить мониторинг подписки
     */
    func stopMonitoring() {
        logger.business("Stopping subscription monitoring")

        isMonitoring = false
        monitoringEnabled = false

        // Отменить background task
        BGTaskScheduler.shared.cancel(taskRequestWithIdentifier: backgroundTaskIdentifier)

        // Отменить все запланированные уведомления
        notificationManager.cancelRenewalNotifications()
        notificationManager.cancelTrialNotifications()

        logger.business("Subscription monitoring stopped")
    }

    /**
     * Принудительная проверка статуса подписки
     */
    func checkSubscriptionStatus() {
        logger.business("Performing subscription status check")

        Task { @MainActor in
            performSubscriptionCheck()
        }

        // Обновить время последней проверки
        lastCheckDate = Date()
    }

    /**
     * Получить время до истечения подписки
     */
    @MainActor var timeUntilExpiration: TimeInterval? {
        guard let subscription = subscriptionManager.currentSubscription,
              let expiresDate = subscription.expiresAt else {
            return nil
        }

        return expiresDate.timeIntervalSince(Date())
    }

    /**
     * Проверить, истекает ли подписка скоро
     */
    @MainActor var isExpiringSoon: Bool {
        guard let timeUntilExpiration = timeUntilExpiration else {
            return false
        }

        // Считаем "скоро" - менее 7 дней
        return timeUntilExpiration < (7 * 24 * 60 * 60) && timeUntilExpiration > 0
    }

    /**
     * Проверить, истекла ли подписка
     */
    @MainActor var isExpired: Bool {
        guard let timeUntilExpiration = timeUntilExpiration else {
            return false
        }

        return timeUntilExpiration <= 0
    }

    // MARK: - Private Methods

    /**
     * Выполнить проверку подписки
     */
    @MainActor private func performSubscriptionCheck() {
        logger.business("🔍 Checking subscription status...")

        do {
            // Получить текущую подписку
            let subscription = subscriptionManager.currentSubscription

            if let subscription = subscription {
                logger.business("📊 Current subscription: \(subscription.level.displayName)")

                if let expiresDate = subscription.expiresAt {
                    let daysUntilExpiration = Int(expiresDate.timeIntervalSince(Date()) / (24 * 60 * 60))

                    if daysUntilExpiration > 0 {
                        logger.business("⏰ Subscription expires in \(daysUntilExpiration) days")

                        // Запланировать уведомления об истечении
                        scheduleExpirationNotifications(for: subscription)
                    } else {
                        logger.business("⚠️ Subscription has expired")

                        // Отправить уведомление об истечении
                        sendExpirationNotification(for: subscription)
                    }
                } else {
                    logger.business("♾️ Subscription is lifetime or free")
                }
            } else {
                logger.business("❌ No active subscription found")
            }

        } catch {
            logger.error("❌ Error checking subscription status: \(error)")
        }
    }

    /**
     * Запланировать уведомления об истечении подписки
     */
    private func scheduleExpirationNotifications(for subscription: SubscriptionStatus) {
        guard let expiresDate = subscription.expiresAt else { return }

        logger.business("📅 Scheduling expiration notifications for subscription ending on: \(expiresDate)")

        notificationManager.scheduleRenewalNotifications(subscriptionEndDate: expiresDate)
    }

    /**
     * Отправить немедленное уведомление об истечении подписки
     */
    private func sendExpirationNotification(for subscription: SubscriptionStatus) {
        logger.business("🚨 Sending immediate expiration notification")

        // Отправляем локальное уведомление об истечении подписки
        notificationManager.sendLocalNotification(
            title: "Подписка истекла",
            body: "Ваша подписка \(subscription.level.displayName) истекла",
            category: .subscription,
            userInfo: ["type": "subscription_expired"]
        )
    }

    // MARK: - Background Tasks

    /**
     * Зарегистрировать background task
     */
    private func registerBackgroundTask() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: backgroundTaskIdentifier,
            using: nil
        ) { task in
            self.handleBackgroundTask(task as! BGAppRefreshTask)
        }
    }

    /**
     * Запланировать background task
     */
    private func scheduleBackgroundTask() {
        let request = BGAppRefreshTaskRequest(identifier: backgroundTaskIdentifier)

        // Запускать каждые 24 часа
        request.earliestBeginDate = Date(timeIntervalSinceNow: 24 * 60 * 60)

        do {
            try BGTaskScheduler.shared.submit(request)
            logger.business("✅ Background task scheduled for 24 hours from now")
        } catch {
            logger.error("❌ Failed to schedule background task: \(error)")
        }
    }

    /**
     * Обработать background task
     */
    private func handleBackgroundTask(_ task: BGAppRefreshTask) {
        logger.business("🔄 Executing background subscription check")

        // Установить обработчик завершения
        task.expirationHandler = {
            logger.business("⏰ Background task expired")
            task.setTaskCompleted(success: false)
        }

        // Выполнить проверку
        Task { @MainActor in
            performSubscriptionCheck()

            // Запланировать следующий task
            scheduleBackgroundTask()

            // Завершить task
            task.setTaskCompleted(success: true)
            logger.business("✅ Background subscription check completed")
        }
    }

    // MARK: - Persistence

    private var monitoringEnabled: Bool {
        get { userDefaults.bool(forKey: monitoringEnabledKey) }
        set { userDefaults.set(newValue, forKey: monitoringEnabledKey) }
    }

    private var lastCheckDate: Date? {
        get { userDefaults.object(forKey: lastCheckKey) as? Date }
        set { userDefaults.set(newValue, forKey: lastCheckKey) }
    }

    private var isMonitoringEnabled: Bool {
        userDefaults.bool(forKey: monitoringEnabledKey)
    }
}