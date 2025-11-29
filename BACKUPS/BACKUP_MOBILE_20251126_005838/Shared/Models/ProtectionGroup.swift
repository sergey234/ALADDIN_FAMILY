import Foundation

/// Группы категорий защиты от угроз
/// Используется для группировки категорий на экране защиты
enum ProtectionGroup: String, CaseIterable, Identifiable {
    case devices = "УСТРОЙСТВА"
    case internet = "ИНТЕРНЕТ"
    case family = "СЕМЬЯ"
    case finance = "ФИНАНСЫ"
    case premium = "ПРЕМИУМ"
    
    var id: String { rawValue }
    
    /// Иконка группы
    var icon: String {
        switch self {
        case .devices: return "📱"
        case .internet: return "🌐"
        case .family: return "👨‍👩‍👧‍👦"
        case .finance: return "💰"
        case .premium: return "💎"
        }
    }
    
    /// Локализованное название группы
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .devices: return localizationManager.localized("protection_group_devices")
        case .internet: return localizationManager.localized("protection_group_internet")
        case .family: return localizationManager.localized("protection_group_family")
        case .finance: return localizationManager.localized("protection_group_finance")
        case .premium: return localizationManager.localized("protection_group_premium")
        }
    }
    
    /// Получить все категории в группе
    /// ✅ ГИБКАЯ АРХИТЕКТУРА: Автоматически собирает категории из конфигурации
    var categories: [ThreatProtectionCategory] {
        return ThreatProtectionCategory.allCases.filter { category in
            category.group == self
        }
    }
}

