import Foundation

// MARK: - Модуль родительского контроля

/// Модули родительского контроля
enum ParentalControlModule: String, CaseIterable, Identifiable {
    case contentBlock = "content_block"
    case timeControl = "time_control"
    case monitoring = "monitoring"
    case location = "location"
    case reports = "reports"
    case additional = "additional"
    case bypassProtection = "bypass_protection"
    case rewards = "rewards"
    
    var id: String { rawValue }
    
    var emoji: String {
        switch self {
        case .contentBlock: return "🔒"
        case .timeControl: return "⏰"
        case .monitoring: return "👀"
        case .location: return "📍"
        case .reports: return "📊"
        case .additional: return "⚙️"
        case .bypassProtection: return "🛡️"
        case .rewards: return "🦄"
        }
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        let key = "tariff_parental_module_\(rawValue)_title"
        return localizationManager.localized(key)
    }
}

// MARK: - Функция родительского контроля

/// Модель функции родительского контроля
struct ParentalControlFeature: Identifiable {
    let id: String
    let titleKey: String
    let descriptionKey: String?
    let module: ParentalControlModule
    let requiredTariff: TariffType
    
    /// Локализованное название функции
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        return localizationManager.localized(titleKey)
    }
    
    /// Локализованное описание функции (если есть)
    func localizedDescription(_ localizationManager: LocalizationManager) -> String? {
        guard let descKey = descriptionKey else { return nil }
        return localizationManager.localized(descKey)
    }
    
    /// Проверка доступности функции для тарифа
    func isAvailable(for tariff: TariffType) -> Bool {
        let currentLevel = getTariffLevel(tariff)
        let requiredLevel = getTariffLevel(requiredTariff)
        return currentLevel >= requiredLevel
    }
    
    /// Уровень тарифа (для сравнения)
    private func getTariffLevel(_ tariff: TariffType) -> Int {
        switch tariff {
        case .free: return 0
        case .personal: return 1
        case .family: return 2
        case .premium: return 3
        }
    }
}

// MARK: - Конфигурация функций родительского контроля

extension ParentalControlModule {
    /// ✅ ГИБКАЯ КОНФИГУРАЦИЯ: Все функции родительского контроля в одном месте
    static var features: [ParentalControlModule: [ParentalControlFeature]] {
        [
            .contentBlock: [
                // Free (3 функции)
                ParentalControlFeature(
                    id: "content_site_block",
                    titleKey: "tariff_parental_content_site_block_free",
                    descriptionKey: nil,
                    module: .contentBlock,
                    requiredTariff: .free
                ),
                ParentalControlFeature(
                    id: "content_app_block",
                    titleKey: "tariff_parental_content_app_block_free",
                    descriptionKey: nil,
                    module: .contentBlock,
                    requiredTariff: .free
                ),
                ParentalControlFeature(
                    id: "content_search_block",
                    titleKey: "tariff_parental_content_search_block_free",
                    descriptionKey: nil,
                    module: .contentBlock,
                    requiredTariff: .free
                ),
                // Personal (2 функции)
                ParentalControlFeature(
                    id: "content_whitelist",
                    titleKey: "tariff_parental_content_whitelist_personal",
                    descriptionKey: nil,
                    module: .contentBlock,
                    requiredTariff: .personal
                ),
                ParentalControlFeature(
                    id: "content_auto_block",
                    titleKey: "tariff_parental_content_auto_block_personal",
                    descriptionKey: nil,
                    module: .contentBlock,
                    requiredTariff: .personal
                )
            ],
            .timeControl: [
                // Free (2 функции)
                ParentalControlFeature(
                    id: "time_screen_limit",
                    titleKey: "tariff_parental_time_screen_limit_free",
                    descriptionKey: nil,
                    module: .timeControl,
                    requiredTariff: .free
                ),
                ParentalControlFeature(
                    id: "time_bedtime",
                    titleKey: "tariff_parental_time_bedtime_free",
                    descriptionKey: nil,
                    module: .timeControl,
                    requiredTariff: .free
                ),
                // Personal (2 функции)
                ParentalControlFeature(
                    id: "time_schedule",
                    titleKey: "tariff_parental_time_schedule_personal",
                    descriptionKey: nil,
                    module: .timeControl,
                    requiredTariff: .personal
                ),
                ParentalControlFeature(
                    id: "time_app_limits",
                    titleKey: "tariff_parental_time_app_limits_personal",
                    descriptionKey: nil,
                    module: .timeControl,
                    requiredTariff: .personal
                )
            ],
            .monitoring: [
                // Free (2 функции)
                ParentalControlFeature(
                    id: "monitoring_browser_24h",
                    titleKey: "tariff_parental_monitoring_browser_24h_free",
                    descriptionKey: nil,
                    module: .monitoring,
                    requiredTariff: .free
                ),
                ParentalControlFeature(
                    id: "monitoring_apps_24h",
                    titleKey: "tariff_parental_monitoring_apps_24h_free",
                    descriptionKey: nil,
                    module: .monitoring,
                    requiredTariff: .free
                ),
                // Personal (2 функции)
                ParentalControlFeature(
                    id: "monitoring_browser_7d",
                    titleKey: "tariff_parental_monitoring_browser_7d_personal",
                    descriptionKey: nil,
                    module: .monitoring,
                    requiredTariff: .personal
                ),
                ParentalControlFeature(
                    id: "monitoring_apps_7d",
                    titleKey: "tariff_parental_monitoring_apps_7d_personal",
                    descriptionKey: nil,
                    module: .monitoring,
                    requiredTariff: .personal
                ),
                ParentalControlFeature(
                    id: "monitoring_contacts",
                    titleKey: "tariff_parental_monitoring_contacts_personal",
                    descriptionKey: nil,
                    module: .monitoring,
                    requiredTariff: .personal
                )
            ],
            .location: [
                // Family (4 функции)
                ParentalControlFeature(
                    id: "location_realtime",
                    titleKey: "tariff_parental_location_realtime_family",
                    descriptionKey: nil,
                    module: .location,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "location_geofences",
                    titleKey: "tariff_parental_location_geofences_family",
                    descriptionKey: nil,
                    module: .location,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "location_history_24h",
                    titleKey: "tariff_parental_location_history_24h_family",
                    descriptionKey: nil,
                    module: .location,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "location_sos",
                    titleKey: "tariff_parental_location_sos_family",
                    descriptionKey: nil,
                    module: .location,
                    requiredTariff: .family
                ),
                // Premium (1 функция)
                ParentalControlFeature(
                    id: "location_history_7d",
                    titleKey: "tariff_parental_location_history_7d_premium",
                    descriptionKey: nil,
                    module: .location,
                    requiredTariff: .premium
                )
            ],
            .reports: [
                // Personal (1 функция)
                ParentalControlFeature(
                    id: "reports_weekly_basic",
                    titleKey: "tariff_parental_reports_weekly_basic_personal",
                    descriptionKey: nil,
                    module: .reports,
                    requiredTariff: .personal
                ),
                // Family (1 функция)
                ParentalControlFeature(
                    id: "reports_weekly_advanced",
                    titleKey: "tariff_parental_reports_weekly_advanced_family",
                    descriptionKey: nil,
                    module: .reports,
                    requiredTariff: .family
                ),
                // Premium (1 функция)
                ParentalControlFeature(
                    id: "reports_monthly_premium",
                    titleKey: "tariff_parental_reports_monthly_premium_premium",
                    descriptionKey: nil,
                    module: .reports,
                    requiredTariff: .premium
                )
            ],
            .additional: [
                // Personal (1 функция)
                ParentalControlFeature(
                    id: "additional_access_requests",
                    titleKey: "tariff_parental_additional_access_requests_personal",
                    descriptionKey: nil,
                    module: .additional,
                    requiredTariff: .personal
                ),
                // Family (2 функции)
                ParentalControlFeature(
                    id: "additional_homework_mode",
                    titleKey: "tariff_parental_additional_homework_mode_family",
                    descriptionKey: nil,
                    module: .additional,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "additional_youtube_safe",
                    titleKey: "tariff_parental_additional_youtube_safe_family",
                    descriptionKey: nil,
                    module: .additional,
                    requiredTariff: .family
                ),
                // Premium (1 функция)
                ParentalControlFeature(
                    id: "additional_ai_insights",
                    titleKey: "tariff_parental_additional_ai_insights_premium",
                    descriptionKey: nil,
                    module: .additional,
                    requiredTariff: .premium
                )
            ],
            .bypassProtection: [
                // Family (3 функции)
                ParentalControlFeature(
                    id: "bypass_incognito",
                    titleKey: "tariff_parental_bypass_incognito_family",
                    descriptionKey: nil,
                    module: .bypassProtection,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "bypass_network_protection_tor",
                    titleKey: "tariff_parental_bypass_network_protection_tor_family",
                    descriptionKey: nil,
                    module: .bypassProtection,
                    requiredTariff: .family
                ),
                ParentalControlFeature(
                    id: "bypass_proxy",
                    titleKey: "tariff_parental_bypass_proxy_family",
                    descriptionKey: nil,
                    module: .bypassProtection,
                    requiredTariff: .family
                )
            ],
            .rewards: [
                // Free (1 функция)
                ParentalControlFeature(
                    id: "rewards_basic",
                    titleKey: "tariff_parental_rewards_basic_free",
                    descriptionKey: nil,
                    module: .rewards,
                    requiredTariff: .free
                ),
                // Family (1 функция)
                ParentalControlFeature(
                    id: "rewards_auto",
                    titleKey: "tariff_parental_rewards_auto_family",
                    descriptionKey: nil,
                    module: .rewards,
                    requiredTariff: .family
                ),
                // Premium (1 функция)
                ParentalControlFeature(
                    id: "rewards_premium",
                    titleKey: "tariff_parental_rewards_premium_premium",
                    descriptionKey: nil,
                    module: .rewards,
                    requiredTariff: .premium
                )
            ]
        ]
    }
    
    /// Получить все функции модуля для тарифа
    func features(for tariff: TariffType) -> [ParentalControlFeature] {
        let allFeatures = Self.features[self] ?? []
        return allFeatures.filter { $0.isAvailable(for: tariff) }
    }
    
    /// Получить все функции модуля (все тарифы)
    var allFeatures: [ParentalControlFeature] {
        return Self.features[self] ?? []
    }
}

