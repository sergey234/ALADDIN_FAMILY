import Foundation

// MARK: - TariffType для совместимости

/// Тип тарифа (для совместимости с TariffsScreen)
typealias TariffType = TariffsScreen.TariffType

extension TariffType {
    /// Согласованный маппинг с `SubscriptionLevel` (единые rawValue: trial, free, personal, family, premium).
    static func fromSubscriptionLevel(_ level: SubscriptionLevel) -> TariffType {
        TariffType(rawValue: level.rawValue) ?? .free
    }
}

/// Модель категории угроз для каталога «100 видов защиты».
/// Используется на экранах тарифов и защите.
enum ThreatProtectionCategory: String, CaseIterable, Identifiable {
    case cyberThreats
    case fraud
    case childThreats
    case dataLeaks
    case deepfakes
    case internetThreats
    case mobileThreats
    case familyThreats
    case iotThreats
    
    var id: String { rawValue }
    
    var emoji: String {
        switch self {
        case .cyberThreats: return "🛡️"
        case .fraud: return "💰"
        case .childThreats: return "👶"
        case .dataLeaks: return "🔒"
        case .deepfakes: return "🎭"
        case .internetThreats: return "🌐"
        case .mobileThreats: return "📱"
        case .familyThreats: return "🏠"
        case .iotThreats: return "🏡"
        }
    }
    
    var count: Int {
        switch self {
        case .cyberThreats: return 10
        case .fraud: return 12
        case .childThreats: return 17
        case .dataLeaks: return 12
        case .deepfakes: return 8
        case .internetThreats: return 6
        case .mobileThreats: return 10
        case .familyThreats: return 15
        case .iotThreats: return 10
        }
    }
}

extension ThreatProtectionCategory {
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .cyberThreats: return localizationManager.localized("tariffs_threat_category_cyber")
        case .fraud: return localizationManager.localized("tariffs_threat_category_fraud")
        case .childThreats: return localizationManager.localized("tariffs_threat_category_child")
        case .dataLeaks: return localizationManager.localized("tariffs_threat_category_data")
        case .deepfakes: return localizationManager.localized("tariffs_threat_category_deepfakes")
        case .internetThreats: return localizationManager.localized("tariffs_threat_category_internet")
        case .mobileThreats: return localizationManager.localized("tariffs_threat_category_mobile")
        case .familyThreats: return localizationManager.localized("tariffs_threat_category_family")
        case .iotThreats: return localizationManager.localized("tariffs_threat_category_iot")
        }
    }
    
    // MARK: - Гибкая конфигурация категорий
    
    /// ✅ ГИБКАЯ АРХИТЕКТУРА: Конфигурация через Dictionary
    /// При добавлении новой категории просто добавляем запись в configurations!
    static var configurations: [ThreatProtectionCategory: CategoryConfiguration] {
        [
            .cyberThreats: CategoryConfiguration(
                requiredTariff: TariffType.free,
                benefit: "Блокирует вирусы, трояны, фишинг",
                settingsScreen: NavigationManager.ALADDINScreen.deviceHub,
                group: ProtectionGroup.devices
            ),
            .fraud: CategoryConfiguration(
                requiredTariff: TariffType.personal,
                benefit: "Предотвращает финансовое мошенничество",
                settingsScreen: NavigationManager.ALADDINScreen.identityHub,
                group: ProtectionGroup.finance
            ),
            .childThreats: CategoryConfiguration(
                requiredTariff: TariffType.family,
                benefit: "Защищает детей от опасного контента",
                settingsScreen: NavigationManager.ALADDINScreen.parentalControl,
                group: ProtectionGroup.family
            ),
            .dataLeaks: CategoryConfiguration(
                requiredTariff: TariffType.personal,
                benefit: "Предупреждает об утечках данных",
                settingsScreen: NavigationManager.ALADDINScreen.privacyHub,
                group: ProtectionGroup.devices
            ),
            .deepfakes: CategoryConfiguration(
                requiredTariff: TariffType.premium,
                benefit: "Обнаруживает поддельные видео и аудио",
                settingsScreen: NavigationManager.ALADDINScreen.antifakeHub,
                group: ProtectionGroup.premium
            ),
            .internetThreats: CategoryConfiguration(
                requiredTariff: TariffType.free,
                benefit: "Защищает от вредоносных сайтов",
                settingsScreen: NavigationManager.ALADDINScreen.networkProtection,
                group: ProtectionGroup.internet
            ),
            .mobileThreats: CategoryConfiguration(
                requiredTariff: TariffType.personal,
                benefit: "Блокирует вредные приложения",
                settingsScreen: NavigationManager.ALADDINScreen.deviceHub,
                group: ProtectionGroup.devices
            ),
            .familyThreats: CategoryConfiguration(
                requiredTariff: TariffType.family,
                benefit: "Защищает всю семью",
                settingsScreen: NavigationManager.ALADDINScreen.parentalControl,
                group: ProtectionGroup.family
            ),
            .iotThreats: CategoryConfiguration(
                requiredTariff: TariffType.family,
                benefit: "Защищает умные устройства",
                settingsScreen: NavigationManager.ALADDINScreen.deviceHub,
                group: ProtectionGroup.family
            )
        ]
    }
    
    /// ✅ СВОЙСТВА ЧЕРЕЗ КОНФИГУРАЦИЮ: Автоматически работают для новых категорий
    var config: CategoryConfiguration {
        return Self.configurations[self] ?? CategoryConfiguration.default
    }
    
    /// Минимальный тариф для категории
    var requiredTariff: TariffType { config.requiredTariff }
    
    /// Короткий совет "Что это даёт"
    var benefit: String { config.benefit }
    
    /// Экран настроек для категории
    var settingsScreen: NavigationManager.ALADDINScreen? { config.settingsScreen }
    
    /// Группа категории
    var group: ProtectionGroup { config.group }
}

// MARK: - Конфигурация категории

/// ✅ КОНФИГУРАЦИЯ КАТЕГОРИИ: Вся информация в одном месте
struct CategoryConfiguration {
    let requiredTariff: TariffType
    let benefit: String
    let settingsScreen: NavigationManager.ALADDINScreen?
    let group: ProtectionGroup
    
    static var `default`: CategoryConfiguration {
        CategoryConfiguration(
            requiredTariff: TariffType.free,
            benefit: "",
            settingsScreen: nil,
            group: ProtectionGroup.devices
        )
    }
}

extension ThreatProtectionCategory {
    func localizedThreats(_ localizationManager: LocalizationManager) -> [String] {
        switch self {
        case .cyberThreats:
            return [
                localizationManager.localized("tariffs_threat_cyber_1"),
                localizationManager.localized("tariffs_threat_cyber_2"),
                localizationManager.localized("tariffs_threat_cyber_3"),
                localizationManager.localized("tariffs_threat_cyber_4"),
                localizationManager.localized("tariffs_threat_cyber_5"),
                localizationManager.localized("tariffs_threat_cyber_6"),
                localizationManager.localized("tariffs_threat_cyber_7"),
                localizationManager.localized("tariffs_threat_cyber_8"),
                localizationManager.localized("tariffs_threat_cyber_9"),
                localizationManager.localized("tariffs_threat_cyber_10")
            ]
        case .fraud:
            return [
                localizationManager.localized("tariffs_threat_fraud_1"),
                localizationManager.localized("tariffs_threat_fraud_2"),
                localizationManager.localized("tariffs_threat_fraud_3"),
                localizationManager.localized("tariffs_threat_fraud_4"),
                localizationManager.localized("tariffs_threat_fraud_5"),
                localizationManager.localized("tariffs_threat_fraud_6"),
                localizationManager.localized("tariffs_threat_fraud_7"),
                localizationManager.localized("tariffs_threat_fraud_8"),
                localizationManager.localized("tariffs_threat_fraud_9"),
                localizationManager.localized("tariffs_threat_fraud_10"),
                localizationManager.localized("tariffs_threat_fraud_11"),
                localizationManager.localized("tariffs_threat_fraud_12")
            ]
        case .childThreats:
            return [
                localizationManager.localized("tariffs_threat_child_1"),
                localizationManager.localized("tariffs_threat_child_2"),
                localizationManager.localized("tariffs_threat_child_3"),
                localizationManager.localized("tariffs_threat_child_4"),
                localizationManager.localized("tariffs_threat_child_5"),
                localizationManager.localized("tariffs_threat_child_6"),
                localizationManager.localized("tariffs_threat_child_7"),
                localizationManager.localized("tariffs_threat_child_8"),
                localizationManager.localized("tariffs_threat_child_9"),
                localizationManager.localized("tariffs_threat_child_10"),
                localizationManager.localized("tariffs_threat_child_11"),
                localizationManager.localized("tariffs_threat_child_12"),
                localizationManager.localized("tariffs_threat_child_13"),
                localizationManager.localized("tariffs_threat_child_14"),
                localizationManager.localized("tariffs_threat_child_15"),
                localizationManager.localized("tariffs_threat_child_16"),
                localizationManager.localized("tariffs_threat_child_17")
            ]
        case .dataLeaks:
            return [
                localizationManager.localized("tariffs_threat_data_1"),
                localizationManager.localized("tariffs_threat_data_2"),
                localizationManager.localized("tariffs_threat_data_3"),
                localizationManager.localized("tariffs_threat_data_4"),
                localizationManager.localized("tariffs_threat_data_5"),
                localizationManager.localized("tariffs_threat_data_6"),
                localizationManager.localized("tariffs_threat_data_7"),
                localizationManager.localized("tariffs_threat_data_8"),
                localizationManager.localized("tariffs_threat_data_9"),
                localizationManager.localized("tariffs_threat_data_10"),
                localizationManager.localized("tariffs_threat_data_11"),
                localizationManager.localized("tariffs_threat_data_12")
            ]
        case .deepfakes:
            return [
                localizationManager.localized("tariffs_threat_deepfake_1"),
                localizationManager.localized("tariffs_threat_deepfake_2"),
                localizationManager.localized("tariffs_threat_deepfake_3"),
                localizationManager.localized("tariffs_threat_deepfake_4"),
                localizationManager.localized("tariffs_threat_deepfake_5"),
                localizationManager.localized("tariffs_threat_deepfake_6"),
                localizationManager.localized("tariffs_threat_deepfake_7"),
                localizationManager.localized("tariffs_threat_deepfake_8")
            ]
        case .internetThreats:
            return [
                localizationManager.localized("tariffs_threat_internet_1"),
                localizationManager.localized("tariffs_threat_internet_2"),
                localizationManager.localized("tariffs_threat_internet_3"),
                localizationManager.localized("tariffs_threat_internet_4"),
                localizationManager.localized("tariffs_threat_internet_5"),
                localizationManager.localized("tariffs_threat_internet_6")
            ]
        case .mobileThreats:
            return [
                localizationManager.localized("tariffs_threat_mobile_1"),
                localizationManager.localized("tariffs_threat_mobile_2"),
                localizationManager.localized("tariffs_threat_mobile_3"),
                localizationManager.localized("tariffs_threat_mobile_4"),
                localizationManager.localized("tariffs_threat_mobile_5"),
                localizationManager.localized("tariffs_threat_mobile_6"),
                localizationManager.localized("tariffs_threat_mobile_7"),
                localizationManager.localized("tariffs_threat_mobile_8"),
                localizationManager.localized("tariffs_threat_mobile_9"),
                localizationManager.localized("tariffs_threat_mobile_10")
            ]
        case .familyThreats:
            return [
                localizationManager.localized("tariffs_threat_family_1"),
                localizationManager.localized("tariffs_threat_family_2"),
                localizationManager.localized("tariffs_threat_family_3"),
                localizationManager.localized("tariffs_threat_family_4"),
                localizationManager.localized("tariffs_threat_family_5"),
                localizationManager.localized("tariffs_threat_family_6"),
                localizationManager.localized("tariffs_threat_family_7"),
                localizationManager.localized("tariffs_threat_family_8"),
                localizationManager.localized("tariffs_threat_family_9"),
                localizationManager.localized("tariffs_threat_family_10"),
                localizationManager.localized("tariffs_threat_family_11"),
                localizationManager.localized("tariffs_threat_family_12"),
                localizationManager.localized("tariffs_threat_family_13"),
                localizationManager.localized("tariffs_threat_family_14"),
                localizationManager.localized("tariffs_threat_family_15")
            ]
        case .iotThreats:
            return [
                localizationManager.localized("tariffs_threat_iot_1"),
                localizationManager.localized("tariffs_threat_iot_2"),
                localizationManager.localized("tariffs_threat_iot_3"),
                localizationManager.localized("tariffs_threat_iot_4"),
                localizationManager.localized("tariffs_threat_iot_5"),
                localizationManager.localized("tariffs_threat_iot_6"),
                localizationManager.localized("tariffs_threat_iot_7"),
                localizationManager.localized("tariffs_threat_iot_8"),
                localizationManager.localized("tariffs_threat_iot_9"),
                localizationManager.localized("tariffs_threat_iot_10")
            ]
        }
    }

    /// ux-2-04: единый маршрут «Открыть хаб» (IoT → Device Hub /iot).
    @MainActor
    func openDetails(using navigationManager: NavigationManager, tariffManager: TariffManager) {
        guard tariffManager.isCategoryAvailable(self) else {
            navigationManager.navigateTo(.tariffs)
            return
        }
        if self == .iotThreats {
            navigationManager.navigateToDeviceHub(tab: .iot)
            return
        }
        if self == .deepfakes {
            AntifakeAccessPolicy.openHubOrPaywall(using: navigationManager)
            return
        }
        if let settingsScreen {
            navigationManager.navigateTo(settingsScreen)
        } else {
            navigationManager.navigateTo(.threatProtectionSettings)
        }
    }
}
