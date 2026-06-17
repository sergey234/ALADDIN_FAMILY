import Foundation
import SwiftUI

// MARK: - Карточка тарифа

/// Модель карточки тарифа с полным функционалом
struct TariffCard: Identifiable {
    let id: String
    let tariffType: TariffType
    let price: String
    let devices: String
    let icon: String
    
    /// Все функции защиты от угроз для этого тарифа
    var protectionFeatures: [ThreatProtectionCategory] {
        ThreatProtectionCategory.allCases.filter { category in
            let currentLevel = getTariffLevel(tariffType)
            let requiredLevel = getTariffLevel(category.requiredTariff)
            return currentLevel >= requiredLevel
        }
    }
    
    /// Все функции родительского контроля для этого тарифа
    var parentalControlFeatures: [ParentalControlFeature] {
        var allFeatures: [ParentalControlFeature] = []
        for module in ParentalControlModule.allCases {
            allFeatures.append(contentsOf: module.features(for: tariffType))
        }
        return allFeatures
    }
    
    /// Все дополнительные функции для этого тарифа
    var additionalFeatures: [AdditionalFeature] {
        return tariffType.allAdditionalFeatures()
    }
    
    /// Количество функций защиты от угроз
    var protectionCount: Int {
        protectionFeatures.reduce(0) { $0 + $1.count }
    }
    
    /// Количество функций родительского контроля
    var parentalControlCount: Int {
        parentalControlFeatures.count
    }
    
    /// Общее количество функций
    var totalFeatures: Int {
        protectionCount + parentalControlCount + additionalFeatures.count
    }
    
    /// Процент функций защиты от угроз
    var protectionPercentage: Int {
        let total = ThreatProtectionCategory.allCases.reduce(0) { $0 + $1.count } // 100
        return Int((Double(protectionCount) / Double(total)) * 100)
    }
    
    /// Процент функций родительского контроля
    var parentalControlPercentage: Int {
        let total = ParentalControlModule.allCases.reduce(0) { $0 + $1.allFeatures.count } // 32
        return Int((Double(parentalControlCount) / Double(total)) * 100)
    }
    
    /// Цвет тарифа
    var color: Color {
        tariffType.color
    }
    
    /// Эмодзи тарифа
    var emoji: String {
        switch tariffType {
        case .trial: return "🎁"
        case .free: return "🆓"
        case .personal: return "💎"
        case .family: return "👨‍👩‍👧‍👦"
        case .premium: return "⭐"
        }
    }
    
    /// Уровень тарифа (для сравнения)
    private func getTariffLevel(_ tariff: TariffType) -> Int {
        tariff.featureAccessTier
    }
}

// MARK: - Конфигурация карточек тарифов

extension TariffType {
    /// Создать карточку тарифа
    func createCard(localizationManager: LocalizationManager) -> TariffCard {
        let devices: String = {
            switch self {
            case .trial: return "10"
            case .free: return "1"
            case .personal: return "2"
            case .family: return "6"
            case .premium: return "10"
            }
        }()

        return TariffCard(
            id: rawValue,
            tariffType: self,
            price: self.price,
            devices: devices,
            icon: {
                switch self {
                case .trial: return "🎁"
                case .free: return "🆓"
                case .personal: return "💎"
                case .family: return "👨‍👩‍👧‍👦"
                case .premium: return "⭐"
                }
            }()
        )
    }
}

