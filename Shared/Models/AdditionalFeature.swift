import Foundation

// MARK: - Дополнительная функция тарифа

/// Модель дополнительной функции тарифа (Защита сети, устройства, реклама, AI и т.д.)
struct AdditionalFeature: Identifiable {
    let id: String
    let titleKey: String
    let descriptionKey: String?
    let requiredTariff: TariffType
    let icon: String?
    
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

// MARK: - Конфигурация дополнительных функций

extension TariffType {
    /// ✅ ГИБКАЯ КОНФИГУРАЦИЯ: Все дополнительные функции по тарифам
    static var additionalFeatures: [TariffType: [AdditionalFeature]] {
        [
            .free: [
                AdditionalFeature(
                    id: "network_protection_free",
                    titleKey: "tariff_additional_network_protection_free",
                    descriptionKey: nil,
                    requiredTariff: .free,
                    icon: "🛡️"
                ),
                AdditionalFeature(
                    id: "ads_free",
                    titleKey: "tariff_additional_ads_free",
                    descriptionKey: nil,
                    requiredTariff: .free,
                    icon: "📢"
                )
            ],
            .personal: [
                AdditionalFeature(
                    id: "network_protection_personal",
                    titleKey: "tariff_additional_network_protection_personal",
                    descriptionKey: nil,
                    requiredTariff: .personal,
                    icon: "🛡️"
                ),
                AdditionalFeature(
                    id: "ai_assistant_personal",
                    titleKey: "tariff_additional_ai_assistant_personal",
                    descriptionKey: nil,
                    requiredTariff: .personal,
                    icon: "🤖"
                )
            ],
            .family: [
                AdditionalFeature(
                    id: "network_protection_family",
                    titleKey: "tariff_additional_network_protection_family",
                    descriptionKey: nil,
                    requiredTariff: .family,
                    icon: "🛡️"
                ),
                AdditionalFeature(
                    id: "elderly_protection_family",
                    titleKey: "tariff_additional_elderly_protection_family",
                    descriptionKey: nil,
                    requiredTariff: .family,
                    icon: "👴"
                ),
                AdditionalFeature(
                    id: "voice_control_family",
                    titleKey: "tariff_additional_voice_control_family",
                    descriptionKey: nil,
                    requiredTariff: .family,
                    icon: "🎤"
                ),
                AdditionalFeature(
                    id: "gamification_family",
                    titleKey: "tariff_additional_gamification_family",
                    descriptionKey: nil,
                    requiredTariff: .family,
                    icon: "🎮"
                )
            ],
            .premium: [
                AdditionalFeature(
                    id: "network_protection_premium",
                    titleKey: "tariff_additional_network_protection_premium",
                    descriptionKey: nil,
                    requiredTariff: .premium,
                    icon: "🛡️"
                ),
                AdditionalFeature(
                    id: "anonymity_premium",
                    titleKey: "tariff_additional_anonymity_premium",
                    descriptionKey: nil,
                    requiredTariff: .premium,
                    icon: "👻"
                )
            ]
        ]
    }
    
    /// Получить все дополнительные функции для тарифа
    func allAdditionalFeatures() -> [AdditionalFeature] {
        var features: [AdditionalFeature] = []
        
        switch self {
        case .free:
            // Free: только свои функции
            features = Self.additionalFeatures[.free] ?? []
        case .personal:
            // Personal: только свои функции (без Free, чтобы не дублировать защиту сети)
            features = Self.additionalFeatures[.personal] ?? []
        case .family:
            // Family: только свои функции (без предыдущих, чтобы не дублировать защиту сети)
            features = Self.additionalFeatures[.family] ?? []
        case .premium:
            // Premium: ВСЕ функции из всех тарифов (но защита сети только Premium версия)
            // Собираем все уникальные функции, исключая дубликаты защиты сети
            var allFeatures: [AdditionalFeature] = []
            
            // Добавляем функции из всех тарифов
            if let freeFeatures = Self.additionalFeatures[.free] {
                // Исключаем защиту сети и рекламу из Free (защита сети будет Premium версия, реклама не нужна)
                allFeatures.append(contentsOf: freeFeatures.filter { $0.id != "network_protection_free" && $0.id != "ads_free" })
            }
            if let personalFeatures = Self.additionalFeatures[.personal] {
                // Исключаем защиту сети из Personal (будет Premium версия)
                allFeatures.append(contentsOf: personalFeatures.filter { $0.id != "network_protection_personal" })
            }
            if let familyFeatures = Self.additionalFeatures[.family] {
                // Исключаем защиту сети из Family (будет Premium версия)
                allFeatures.append(contentsOf: familyFeatures.filter { $0.id != "network_protection_family" })
            }
            if let premiumFeatures = Self.additionalFeatures[.premium] {
                allFeatures.append(contentsOf: premiumFeatures)
            }
            
            features = allFeatures
        }
        
        return features
    }
}

