import SwiftUI
import Combine

/**
 * 🎯 SERVICES PROTOCOLS
 * Протоколы для dependency injection в MVVM архитектуре
 * Используются в SettingsViewModel для изоляции зависимостей
 */

// MARK: - Navigation Service
protocol NavigationService {
    func navigateTo(_ screen: ALADDINScreen)
    func navigateToRoot(_ screen: ALADDINScreen)
    func navigateToDevice(_ deviceId: String)
    func navigateToProfile(_ userId: String)
    func navigateToNotificationSettings()
    func navigateToLanguageSettings()
}

// MARK: - Localization Service
protocol LocalizationService {
    var currentLanguage: Language { get }
    func localized(_ key: String) -> String
    func localized(_ key: String, _ arguments: CVarArg...) -> String
    func changeLanguage(to language: Language)
    var locale: Locale { get }
}

// MARK: - Notification Service
protocol NotificationService {
    var notificationSettings: NotificationSettings { get set }
    func requestAuthorization() async -> Bool
    func saveSettings()
    func sendLocalNotification(title: String, body: String, userInfo: [AnyHashable: Any]?)
    func sendThreatBlockedNotification(threatType: String, url: String)
}

// MARK: - Security Service
protocol SecurityService {
    var biometricAuthAvailable: Bool { get }
    func authenticateWithBiometrics() async -> Bool
}

// MARK: - Tariff Service
protocol TariffService {
    var currentTariff: Tariff { get }
    func createCard(localizationService: LocalizationService) -> TariffCard
}

// MARK: - API Service
protocol APIService {
    func getComponentsList(completion: @escaping (Result<[ComponentStatus], Error>) -> Void)
    func enableComponent(componentId: String) async throws
    func disableComponent(componentId: String) async throws
}

// MARK: - Positioning Service
protocol PositioningService {
    var currentSystem: PositioningSystem { get }
    var selectedSystem: PositioningSystem { get set }
    var currentRegionName: String { get }
    func saveSelectedSystem(_ system: PositioningSystem)
}

// MARK: - Protection Features Service
protocol ProtectionFeaturesService {
    var features: [ProtectionFeature] { get set }
    func loadFeatures()
    func toggleFeature(_ featureId: String, enabled: Bool)
    func getFeaturesForLevel(_ level: Int) -> [ProtectionFeature]
}

// MARK: - Toast Service
protocol ToastService {
    func showToast(message: String, type: ToastType, duration: TimeInterval)
    func hideToast()
}

// MARK: - Protection History Service
protocol ProtectionHistoryService {
    var history: [ProtectionLevelRecord] { get }
    func addRecord(level: Int, reason: String, timestamp: Date)
    func getRecentRecords(limit: Int) -> [ProtectionLevelRecord]
    func clearHistory()
}

// MARK: - Toast Type (for ToastService)
enum ToastType {
    case success, warning, error, info
}

// MARK: - Type Definitions (forwards from existing models)
typealias ALADDINScreen = NavigationManager.ALADDINScreen
typealias Language = LocalizationManager.Language
typealias NotificationSettings = NotificationManager.NotificationSettings
typealias Tariff = TariffManager.TariffType
typealias TariffCard = TariffManager.TariffCard
typealias ComponentStatus = ComponentStatus // Already defined in ComponentStatus.swift
typealias PositioningSystem = PositioningSystemService.PositioningSystem
typealias ProtectionFeature = ProtectionFeaturesManager.ProtectionFeature
typealias ProtectionLevelRecord = ProtectionLevelHistoryManager.ProtectionLevelRecord