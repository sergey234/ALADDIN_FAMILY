import Foundation
import Security

/**
 * ⚙️ App Config
 * Конфигурация приложения
 * Настройки для подключения к Python backend
 */

struct AppConfig {
    
    // MARK: - API Configuration
    
    /// Окружения API
    enum Environment {
        case development
        case staging
        case production
        
        var baseURL: String {
            switch self {
            case .development:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            case .staging:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            case .production:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            }
        }
    }
    
    /// Текущее окружение
    static let currentEnvironment: Environment = {
        #if DEBUG
        return .development
        #else
        return .production
        #endif
    }()
    
    /**
     * URL вашего Python backend
     * ВАЖНО: Измените на свой реальный URL!
     */
    static let apiBaseURL: String = currentEnvironment.baseURL
    
    /// Использовать Mock API вместо реального (только для DEBUG)
    /// ✅ ИСПРАВЛЕНО: Продакшен использует реальный API
    static let useMockAPI: Bool = {
        #if DEBUG && USE_MOCK_FOR_DEVELOPMENT
        return true  // Только для разработки с флагом USE_MOCK_FOR_DEVELOPMENT
        #else
        return false // Продакшен использует реальный API
        #endif
    }()
    
    /// Режим съёмки скриншотов (принудительно включает русский язык)
    static let screenshotMode: Bool = false
    
    /// Показывать отладочные оверлеи
    static let showDebugOverlays: Bool = false
    
    // ✅ ИСПРАВЛЕНИЕ #5: Метод для безопасной проверки доступности API
    static func isAPIURLValid() -> Bool {
        guard !apiBaseURL.isEmpty else { return false }
        // Если localhost в DEBUG режиме - всегда возвращаем true (будет ошибка при запросе, но не краш)
        #if DEBUG
        return true
        #else
        return apiBaseURL.hasPrefix("https://")
        #endif
    }
    
    // MARK: - Auth
    
    /**
     * Токен авторизации (если есть)
     * Читается из Keychain для безопасности с fallback на UserDefaults
     */
    static var authToken: String? {
        get {
            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
            // Сначала пробуем Keychain (основное хранилище)
            if let keychainToken = KeychainManager.shared.loadString(forKey: .authToken) {
                return keychainToken
            }
            // Fallback на UserDefaults для обратной совместимости
            return UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken)
        }
        set {
            if let token = newValue {
                // Сохраняем в Keychain
                KeychainManager.shared.save(token, forKey: .authToken)
                // И в UserDefaults для обратной совместимости
                UserDefaults.standard.set(token, forKey: AppConfig.UserDefaultsKeys.authToken)
            } else {
                // Удаляем из обоих мест
                KeychainManager.shared.delete(forKey: .authToken)
                UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
            }
        }
    }
    
    // MARK: - App Info
    
    static let appVersion = "1.0.0"
    static let buildNumber = "1"
    static let bundleIdentifier = "family.aladdin.ios"
    static let appName = "ALADDIN"
    static let appDisplayName = "ALADDIN - AI Защита Семьи"
    
    // MARK: - API Endpoints
    
    enum Endpoint {
        // Network Protection
        static let networkProtectionStatus = "/network-protection/status"
        static let networkProtectionConnect = "/network-protection/connect"
        static let networkProtectionDisconnect = "/network-protection/disconnect"
        static let networkProtectionServers = "/network-protection/servers"
        static let networkProtectionSettings = "/network-protection/settings"
        static let networkProtectionConfig = "/network-protection/config"
        static let networkProtectionStats = "/network-protection/stats"
        
        // Family
        static let createFamily = "/family/create"
        static let joinFamily = "/family/join"
        static let recoverFamily = "/family/recover"
        static let loginByRecoveryCode = "/auth/login-by-recovery-code"
        static let familyMembers = "/family/members"
        static let addFamilyMember = "/family/add"
        static let removeFamilyMember = "/family/remove"
        static let memberProfile = "/family/member"
        static let familyStats = "/family/stats"
        
        // Family Chat
        static let familyChatMessages = "/family/chat/messages"
        static let familyChatSend = "/family/chat/send"
        
        // Components (42 components API)
        static let componentStatus = "/components/status"
        static let componentStatusBatch = "/components/status/batch"  // 🚀 Batch endpoint для оптимизации
        static let componentEnable = "/components/enable"
        static let componentDisable = "/components/disable"
        static let componentConfiguration = "/components/config"
        static let componentBulkUpdate = "/components/bulk-update"  // Массовое обновление компонентов
        static let componentsList = "/api/components/list"  // ✅ ЗАДАЧА 22: Список всех компонентов
        static let componentsHealth = "/api/components/health"  // ✅ ЗАДАЧА 22: Общее здоровье компонентов
        
        // Analytics
        static let analytics = "/analytics"
        static let threats = "/analytics/threats"
        static let topThreats = "/analytics/top-threats"

        // ✅ ЗАДАЧА 65: Metrics upload endpoint
        static let metricsUpload = "/metrics/upload"
        
        // Component Reports
        // Driving Reports
        static let drivingReports = "/reports/driving"
        static let drivingStats = "/reports/driving/stats"
        static let drivingExport = "/reports/driving/export"
        
        // Dark Web Monitoring
        static let darkWebLeaks = "/reports/dark-web/leaks"
        static let darkWebStats = "/reports/dark-web/stats"
        static let darkWebScans = "/reports/dark-web/scans"
        static let darkWebResolve = "/reports/dark-web/resolve"
        static let darkWebScanStart = "/reports/dark-web/scan/start"
        static let darkWebScanSecure = "/reports/dark-web/scan/secure"
        static let darkWebScanFast = "/reports/dark-web/scan/fast"
        
        // Identity Theft
        static let identityTheftAttempts = "/reports/identity-theft/attempts"
        static let identityTheftStats = "/reports/identity-theft/stats"
        static let identityTheftAllow = "/reports/identity-theft/allow"
        static let identityTheftBlock = "/reports/identity-theft/block"
        static let identityTheftWhitelist = "/reports/identity-theft/whitelist"
        
        // Privacy Reports
        static let locationStats = "/reports/privacy/location/stats"
        static let locationRequests = "/reports/privacy/location/requests"
        static let locationAllow = "/reports/privacy/location/allow"
        static let locationBlock = "/reports/privacy/location/block"
        static let locationUpdateAccuracy = "/reports/privacy/location/update-accuracy"
        static let dataCleanupStats = "/reports/privacy/cleanup/stats"
        static let dataCleanupRecords = "/reports/privacy/cleanup/records"
        static let dataCleanupStart = "/reports/privacy/cleanup/start"
        static let antiTrackerStats = "/reports/privacy/tracker/stats"
        static let topTrackers = "/reports/privacy/tracker/top"
        static let trackerWhitelist = "/reports/privacy/tracker/whitelist"
        
        // AI Categories
        static let aiCategoriesStats = "/reports/ai-categories/stats"
        static let aiCategoryReports = "/reports/ai-categories/reports"
        static let aiCategoriesAllow = "/reports/ai-categories/allow"
        static let aiCategoriesBlock = "/reports/ai-categories/block"
        
        // AI Assistant
        static let aiChat = "/ai/chat"
        static let aiSendMessage = "/ai/message"
        
        // AI Assistant (новые endpoints для полной интеграции)
        static let aiAssistantChat = "/api/ai/assistant/chat"
        static let aiAssistantHistory = "/api/ai/assistant/history"
        static let aiAssistantFeedback = "/api/ai/assistant/feedback"
        static let aiAssistantCapabilities = "/api/ai/assistant/capabilities"
        static let aiAssistantAnalyzeThreat = "/api/ai/assistant/analyze_threat"
        static let aiAssistantRecommendations = "/api/ai/assistant/recommendations"
        static let aiAssistantReportIncident = "/api/ai/assistant/report_incident"
        static let aiAssistantSecurityTips = "/api/ai/assistant/security_tips"
        
        // ✅ ГЕЙМИФИКАЦИЯ: Gamification endpoints (30 endpoints)
        // Баланс единорогов (4 endpoints)
        static let gamificationBalance = "/gamification/balance"
        static let gamificationBalanceAdd = "/gamification/balance/add"
        static let gamificationBalanceSubtract = "/gamification/balance/subtract"
        static let gamificationBalanceHistory = "/gamification/balance/history"
        
        // Награды (6 endpoints)
        static let gamificationRewards = "/gamification/rewards"
        static let gamificationRewardsClaim = "/gamification/rewards/claim"
        static let gamificationRewardsHistory = "/gamification/rewards/history"
        static let gamificationRewardsGive = "/gamification/rewards/give"
        static let gamificationRewardsShop = "/gamification/rewards/shop"
        static let gamificationRewardsPurchase = "/gamification/rewards/purchase"
        
        // Достижения (5 endpoints)
        static let gamificationAchievements = "/gamification/achievements"
        static let gamificationAchievementsUnlock = "/gamification/achievements/unlock"
        static let gamificationAchievementsProgress = "/gamification/achievements/progress"
        static let gamificationAchievement = "/gamification/achievements" // /{achievementId}
        static let gamificationAchievementsClaim = "/gamification/achievements/claim"
        
        // Турниры (6 endpoints)
        static let gamificationTournaments = "/gamification/tournaments"
        static let gamificationTournamentsJoin = "/gamification/tournaments/join"
        static let gamificationTournament = "/gamification/tournaments" // /{tournamentId}
        static let gamificationTournamentsLeaderboard = "/gamification/tournaments/leaderboard"
        static let gamificationTournamentsLeave = "/gamification/tournaments/leave"
        static let gamificationTournamentsHistory = "/gamification/tournaments/history"
        
        // Настройки игр (4 endpoints)
        static let gamificationSettings = "/gamification/settings"
        static let gamificationSettingsUpdate = "/gamification/settings/update"
        static let gamificationSettingsNotifications = "/gamification/settings/notifications"
        static let gamificationSettingsNotificationsUpdate = "/gamification/settings/notifications/update"
        
        // Прогресс игр (5 endpoints)
        static let gamificationProgress = "/gamification/progress"
        static let gamificationProgressUpdate = "/gamification/progress/update"
        static let gamificationProgressStats = "/gamification/progress/stats"
        static let gamificationProgressLevel = "/gamification/progress/level"
        static let gamificationProgressReset = "/gamification/progress/reset"
        
        // ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Parental Control Sync endpoints (20 endpoints)
        // Настройки (5 endpoints)
        static let parentalControlSettings = "/api/parental-control/settings" // /{familyId}
        static let parentalControlSettingsUpdate = "/api/parental-control/settings/update"
        static let parentalControlSettingsHistory = "/api/parental-control/settings/history"
        static let parentalControlSettingsSync = "/api/parental-control/settings/sync"
        static let parentalControlSettingsConflicts = "/api/parental-control/settings/conflicts"
        
        // Лимиты времени (4 endpoints)
        static let parentalControlTimeLimits = "/api/parental-control/time-limits" // /{childId}
        static let parentalControlTimeLimitsUpdate = "/api/parental-control/time-limits/update"
        static let parentalControlTimeLimitsHistory = "/api/parental-control/time-limits/history"
        static let parentalControlTimeLimitsReset = "/api/parental-control/time-limits/reset"
        
        // Расписания (4 endpoints)
        static let parentalControlSchedules = "/api/parental-control/schedules" // /{childId}
        static let parentalControlSchedulesUpdate = "/api/parental-control/schedules/update"
        static let parentalControlSchedulesHistory = "/api/parental-control/schedules/history"
        static let parentalControlSchedulesDelete = "/api/parental-control/schedules/delete"
        
        // Геозоны (4 endpoints)
        static let parentalControlGeofences = "/api/parental-control/geofences" // /{childId}
        static let parentalControlGeofencesAdd = "/api/parental-control/geofences/add"
        static let parentalControlGeofencesUpdate = "/api/parental-control/geofences/update"
        static let parentalControlGeofencesDelete = "/api/parental-control/geofences" // /{geofenceId}
        
        // Блокировки приложений (3 endpoints)
        static let parentalControlAppBlocks = "/api/parental-control/app-blocks" // /{childId}
        static let parentalControlAppBlocksUpdate = "/api/parental-control/app-blocks/update"
        static let parentalControlAppBlocksSync = "/api/parental-control/app-blocks/sync"
        
        // Parental Control (старые endpoints - оставляем для обратной совместимости)
        // ✅ ИСПРАВЛЕНО: Убрали /api/ из начала, т.к. baseURL уже содержит /api
        static let parentalControl = "/parental/control"
        static let applyBlocking = "/v1/parental-control/blocking"
        static let applyRules = "/v1/parental-control/rules"
        static let getAccessRequests = "/v1/parental-control/access-requests"
        static let handleAccessRequest = "/v1/parental-control/access-requests"
        static let getStats = "/v1/parental-control/stats"
        static let updateLimits = "/parental/limits"
        static let blockDevice = "/parental/block"
        
        // User (старые endpoints - оставляем для обратной совместимости)
        static let profile = "/user/profile"
        static let updateProfile = "/user/update"
        static let changePassword = "/user/password"
        static let deleteAccount = "/user/delete"
        static let twoFactorStatus = "/user/2fa/status"
        static let twoFactorUpdate = "/user/2fa/update"
        
        // ✅ ЭТАП 2: Профиль пользователя (5 endpoints)
        static let userProfileSync = "/api/user/profile/sync"
        static let userProfileUpdate = "/api/user/profile/update"
        static let userProfileHistory = "/api/user/profile/history"
        static let userProfilePrivacy = "/api/user/profile/privacy"
        static let userProfilePrivacyUpdate = "/api/user/profile/privacy/update"
        
        // ✅ ЭТАП 2: Тарифы и подписки (8 endpoints)
        static let subscriptionSync = "/api/subscription/sync"
        static let subscriptionUpdate = "/api/subscription/update"
        static let subscriptionPurchaseHistory = "/api/subscription/purchase-history"
        static let subscriptionStatus = "/api/subscription/status"
        static let subscriptionStatusUpdate = "/api/subscription/status/update"
        static let subscriptionAutoRenewal = "/api/subscription/auto-renewal"
        static let subscriptionAutoRenewalUpdate = "/api/subscription/auto-renewal/update"
        static let subscriptionCancel = "/api/subscription/cancel"
        
        // ✅ ЭТАП 2: Настройки приложения (10 endpoints)
        static let appSettingsSync = "/api/settings/sync"
        static let appSettingsUpdate = "/api/settings/update"
        static let appSettingsTheme = "/api/settings/theme"
        static let appSettingsThemeUpdate = "/api/settings/theme/update"
        static let appSettingsLanguage = "/api/settings/language"
        static let appSettingsLanguageUpdate = "/api/settings/language/update"
        static let appSettingsNotifications = "/api/settings/notifications"
        static let appSettingsNotificationsUpdate = "/api/settings/notifications/update"
        static let appSettingsBiometry = "/api/settings/biometry"
        static let appSettingsBiometryUpdate = "/api/settings/biometry/update"
        
        // ✅ ЭТАП 2: Геолокация и геозоны (7 endpoints)
        static let locationGeofencesSync = "/api/location/geofences/sync"
        static let locationGeofencesUpdate = "/api/location/geofences/update"
        static let locationGeofencesDelete = "/api/location/geofences" // /{geofenceId}
        static let locationMovementHistory = "/api/location/movement-history"
        static let locationMovementHistoryUpdate = "/api/location/movement-history/update"
        static let locationStatus = "/api/location/status"
        static let locationStatusUpdate = "/api/location/status/update"
        
        // ✅ ЭТАП 2: Семейный чат (офлайн) (3 endpoints)
        static let chatOfflineMessagesSync = "/api/chat/offline-messages/sync"
        static let chatOfflineMessagesSend = "/api/chat/offline-messages/send"
        static let chatOfflineMessagesResolveConflicts = "/api/chat/offline-messages/resolve-conflicts"
        
        // ✅ ЭТАП 3: Офлайн хранилище (5 endpoints)
        static let offlineStorageSync = "/api/offline-storage/sync"
        static let offlineStorageData = "/api/offline-storage/data"
        static let offlineStorageDataUpdate = "/api/offline-storage/data/update"
        static let offlineStorageDataDelete = "/api/offline-storage/data" // /{dataId}
        static let offlineStorageResolveConflicts = "/api/offline-storage/resolve-conflicts"
        
        // ✅ ЭТАП 3: Crash Detection (4 endpoints)
        static let crashDetectionSync = "/api/crash-detection/sync"
        static let crashDetectionReport = "/api/crash-detection/report"
        static let crashDetectionNotifications = "/api/crash-detection/notifications"
        static let crashDetectionNotificationsSend = "/api/crash-detection/notifications/send"
        
        // ✅ ЭТАП 3: Интерфейс для пожилых (4 endpoints)
        static let elderlyMedicationsSync = "/api/elderly/medications/sync"
        static let elderlyMedicationsUpdate = "/api/elderly/medications/update"
        static let elderlyAppointmentsSync = "/api/elderly/appointments/sync"
        static let elderlyAppointmentsUpdate = "/api/elderly/appointments/update"
        
        // Notifications
        static let notifications = "/notifications"
        static let markRead = "/notifications/read"
        
        // Devices
        static let devices = "/devices"
        static let deviceRegister = "/devices/register-ios"
        static let deviceDetail = "/devices" // /devices/{deviceId}
        static let deviceSettings = "/devices" // /devices/{deviceId}/settings
        
        // Auth
        static let login = "/auth/login"
        static let logout = "/auth/logout"
        static let register = "/auth/register"
        static let authRefresh = "/auth/refresh"
        
        // ✅ ЗАДАЧА 25: Roadside Assistance
        static let roadsideCall = "/api/roadside-assistance/call"
        static let roadsideStatus = "/api/roadside-assistance/status/{request_id}"
        static let roadsideCancel = "/api/roadside-assistance/cancel/{request_id}"
        static let roadsideHistory = "/api/roadside-assistance/history"
        
        // Subscription
        static let tariffs = "/subscription/tariffs"
        static let subscribe = "/subscription/subscribe"
        static let cancelSubscription = "/subscription/cancel"
        static let activateSubscription = "/subscription/activate"
        static let activationVerify = "/subscription/activation/verify"
        static let activationActivate = "/subscription/activation/activate"
        
        // Protection
        static let protectionSettings = "/protection/settings"
        static let protectionStatus = "/protection/status"
        static let threatScenarios = "/protection/threat-scenarios"
        static let protectionEnable = "/protection/enable"
        static let protectionDisable = "/protection/disable"
        static let protectionStats = "/protection/stats"
        static let protectionSync = "/protection/sync"
        
        // Referral
        static let referralCode = "/referral/code"
        static let referralStats = "/referral/stats"
        static let referralHistory = "/referral/history"
        static let referralRewards = "/referral/rewards"

        // Crash Detection
        static let crashDetectionSetup = "/api/crash-detection/setup"
        static let crashDetectionAlert = "/api/crash-detection/alert"
        static let crashDetectionStart = "/api/crash-detection/start"
        static let crashDetectionStop = "/api/crash-detection/stop"
        static let crashDetectionData = "/api/crash-detection/data"
        static let crashDetectionStatus = "/api/crash-detection/status"
        static let crashDetectionSettingsUpdate = "/api/crash-detection/settings/update"
        static let crashDetectionHistory = "/api/crash-detection/history"

        // System Management
        static let systemHealth = "/api/system/health"
        static let systemInfo = "/api/system/info"
        static let systemMetrics = "/api/system/metrics"
        static let systemStatus = "/api/system/status"
        static let systemBackup = "/api/system/backup"
        static let systemBackupStatus = "/api/system/backup/status"

        // Notifications
        static let notificationsCategories = "/api/notifications/categories"
        static let notificationsBulkMarkRead = "/api/notifications/bulk-mark-read"
        static let notificationsArchive = "/api/notifications/archive"
        static let notificationsStats = "/api/notifications/stats"

        // Location & Privacy
        static let locationBubble = "/reports/privacy/location/bubble"
        static let locationSend = "/reports/privacy/location/send"
        static let geofences = "/api/v1/parental-control/location/geofences"
        static let geofenceTrack = "/api/v1/parental-control/location/track"

        // Driving Reports
        static let drivingStart = "/reports/driving/start"
        static let drivingEnd = "/reports/driving/end"
        
        // IoT Security (6 endpoints)
        static let iotStatus = "/iot/status/{homeId}"
        static let iotDevices = "/iot/devices/{homeId}"
        static let iotThreats = "/iot/threats/{homeId}"
        static let iotDeviceBlock = "/iot/device/{deviceId}/block"
        static let iotScan = "/iot/scan/{homeId}"
        static let iotFix = "/iot/fix/{threatId}"
        
        // Payments (2 endpoints)
        static let paymentsQRCreate = "/payments/qr/create"
        static let paymentsQRStatus = "/payments/qr/status/{paymentId}"
    }
    
    // MARK: - Feature Flags
    
    static let isNetworkProtectionEnabled = true
    static let isAIEnabled = true
    static let isParentalControlEnabled = true
    static let isAnalyticsEnabled = true
    
    // MARK: - Payment Configuration
    
    /**
     * Проверка региона пользователя
     * Если Россия → используем QR оплату
     * Если не Россия → используем IAP (App Store)
     */
    static var isRussianRegion: Bool {
        return Locale.current.regionCode == "RU"
    }
    
    /**
     * Включить альтернативные способы оплаты (QR-коды)
     * В России IAP недоступен → используем QR оплату
     * Для остальных стран → используем IAP (App Store)
     * 
     * ✅ ИСПРАВЛЕНО: Использовать QR оплату ТОЛЬКО для России
     * Для соответствия Guideline 3.1.1 IAP должен быть доступен для всех стран кроме России
     */
    static var useAlternativePayments: Bool {
        // Использовать QR оплату ТОЛЬКО для России
        return isRussianRegion
    }
    
    /**
     * Использовать IAP (In-App Purchase через App Store)
     */
    static var useIAP: Bool {
        return !isRussianRegion
    }
    
    /**
     * API ключ для бэкенда (замените на свой!)
     */
    static let apiKey = "YOUR_SECURE_API_KEY"
    
    /**
     * Базовый URL для backward compatibility
     */
    static var baseURL: String {
        return apiBaseURL
    }
    
    // MARK: - Debug
    
    static let isDebugMode: Bool = {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }()
    
    static let logLevel: LogLevel = isDebugMode ? .verbose : .error
    
    enum LogLevel {
        case verbose, info, warning, error, none
    }
}

// MARK: - Constants Extension

extension AppConfig {
    
    // MARK: - UserDefaults Keys
    
    /// Ключи для UserDefaults
    struct UserDefaultsKeys {
        static let authToken = "authToken"
        static let familyId = "family_id"
        static let consentAccepted = "consent_accepted"
        static let consentDate = "consent_date"
        static let consentVersion = "consent_version"
        static let appLanguage = "appLanguage"
        static let hasCompletedOnboarding = "hasCompletedOnboarding"
    }
    
    // MARK: - Network Configuration
    
    /// Настройки сети
    struct Network {
        static let requestTimeout: TimeInterval = 30.0
        static let resourceTimeout: TimeInterval = 60.0
        static let waitsForConnectivity = true
    }
    
    // MARK: - Consent & Privacy
    
    /// Настройки согласий и приватности
    struct Consent {
        static let currentVersion = "2.0"
    }
    
    // MARK: - Support Contact Information
    
    /// Контактная информация для поддержки
    struct Support {
        /// Телефон поддержки (отображаемый формат)
        static let supportPhone = "+7 (927) 005-15-77"
        
        /// URL для Telegram бота поддержки
        /// ✅ Бот уже настроен и работает: https://t.me/aladdin_support_bot
        /// При нажатии на кнопку "Чат с поддержкой" откроется Telegram с этим ботом
        static let supportTelegramURL = "https://t.me/aladdin_support_bot"
        
        /// ✅ ИЗМЕНЕНИЕ: Email заменён на AI ассистента
        /// Вместо email пользователи могут отправлять пожелания и рекомендации через AI ассистента в приложении
        /// AI ассистент открывается через NavigationManager.navigateTo(.aiAssistant)
    }
    
    /// Телефон поддержки (для удобства)
    static var supportPhone: String {
        return Support.supportPhone
    }
    
    /// URL Telegram поддержки (для удобства)
    static var supportTelegramURL: String {
        return Support.supportTelegramURL
    }
    
    /// URL сайта для подписки
    static let subscriptionWebsiteURL = "https://aladdin-ai.ru"
    
    /// URL центра помощи поддержки
    static let supportHelpCenterURL = "https://aladdin-ai.ru/help-faq.html"
    
    /// URL FAQ поддержки
    static let supportFAQURL = "https://aladdin-ai.ru/help-faq.html"
    
    /// ✅ DEPRECATED: Email больше не используется
    /// Используйте AI ассистента вместо email для отправки пожеланий и рекомендаций
    @available(*, deprecated, message: "Используйте AI ассистента вместо email")
    static var supportEmail: String {
        return "support@aladdin.family" // Оставлено для обратной совместимости
    }
    
}

