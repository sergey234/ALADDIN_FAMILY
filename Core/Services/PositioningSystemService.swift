import Foundation
import CoreLocation

/**
 * 🛰️ Positioning System Service
 * Управление выбором системы позиционирования (GPS/ГЛОНАСС/Galileo/BeiDou)
 * Автоматический выбор на основе региона пользователя
 */

enum PositioningSystem: String, CaseIterable, Codable {
    case gps = "GPS"
    case glonass = "GLONASS"
    case galileo = "Galileo"
    case beidou = "BeiDou"
    case auto = "Auto"
    
    var displayName: String {
        switch self {
        case .gps: return "GPS"
        case .glonass: return "ГЛОНАСС"
        case .galileo: return "Galileo"
        case .beidou: return "BeiDou"
        case .auto: return "Автоматически"
        }
    }
    
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .gps: return "GPS"
        case .glonass: return "ГЛОНАСС"
        case .galileo: return "Galileo"
        case .beidou: return "BeiDou"
        case .auto: return localizationManager.localized("positioning_system_auto")
        }
    }
    
    var description: String {
        switch self {
        case .gps:
            return "Global Positioning System (США)"
        case .glonass:
            return "Глобальная навигационная спутниковая система (Россия)"
        case .galileo:
            return "Европейская система спутниковой навигации"
        case .beidou:
            return "Китайская система спутниковой навигации"
        case .auto:
            return "Автоматический выбор на основе региона"
        }
    }
    
    func localizedDescription(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .gps:
            return localizationManager.localized("positioning_system_gps_description")
        case .glonass:
            return localizationManager.localized("positioning_system_glonass_description")
        case .galileo:
            return localizationManager.localized("positioning_system_galileo_description")
        case .beidou:
            return localizationManager.localized("positioning_system_beidou_description")
        case .auto:
            return localizationManager.localized("positioning_system_auto_description")
        }
    }
    
    var icon: String {
        switch self {
        case .gps: return "location.fill"
        case .glonass: return "location.circle.fill"
        case .galileo: return "location.north.line.fill"
        case .beidou: return "location.square.fill"
        case .auto: return "location.magnifyingglass"
        }
    }
}

@MainActor
class PositioningSystemService: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = PositioningSystemService()
    
    // MARK: - Published Properties
    
    @Published var selectedSystem: PositioningSystem = .auto
    @Published var currentSystem: PositioningSystem = .auto
    
    // MARK: - Private Properties
    
    private let userDefaultsKey = "positioning_system_selected"
    
    // MARK: - Initialization
    
    private init() {
        loadSelectedSystem()
        updateCurrentSystem()
    }
    
    // MARK: - Public Methods
    
    /// Загрузить сохраненный выбор пользователя
    func loadSelectedSystem() {
        if let saved = UserDefaults.standard.string(forKey: userDefaultsKey),
           let system = PositioningSystem(rawValue: saved) {
            selectedSystem = system
        } else {
            selectedSystem = .auto
        }
    }
    
    /// Сохранить выбор пользователя
    func saveSelectedSystem(_ system: PositioningSystem) {
        selectedSystem = system
        UserDefaults.standard.set(system.rawValue, forKey: userDefaultsKey)
        updateCurrentSystem()
    }
    
    /// Обновить текущую систему на основе выбора
    func updateCurrentSystem() {
        if selectedSystem == .auto {
            currentSystem = determineSystemByRegion()
        } else {
            currentSystem = selectedSystem
        }
    }
    
    /// Определить систему позиционирования на основе региона
    func determineSystemByRegion() -> PositioningSystem {
        // Получаем регион из Locale
        let regionCode = Locale.current.regionCode ?? ""
        let timeZoneIdentifier = TimeZone.current.identifier
        
        // Маппинг регионов на системы позиционирования
        switch regionCode {
        case "RU", "BY", "KZ", "AM", "AZ", "GE", "KG", "MD", "TJ", "TM", "UZ":
            // Россия и страны СНГ → ГЛОНАСС
            return .glonass
            
        case "CN", "HK", "MO", "TW":
            // Китай и регионы → BeiDou
            return .beidou
            
        case "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE":
            // Европейский союз → Galileo
            return .galileo
            
        default:
            // Остальные регионы → GPS
            return .gps
        }
    }
    
    /// Получить рекомендуемую систему для региона
    func getRecommendedSystem(for regionCode: String) -> PositioningSystem {
        switch regionCode {
        case "RU", "BY", "KZ", "AM", "AZ", "GE", "KG", "MD", "TJ", "TM", "UZ":
            return .glonass
        case "CN", "HK", "MO", "TW":
            return .beidou
        case "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE":
            return .galileo
        default:
            return .gps
        }
    }
    
    /// Получить текущий регион пользователя
    var currentRegion: String {
        Locale.current.regionCode ?? "Unknown"
    }
    
    /// Получить название текущего региона
    var currentRegionName: String {
        Locale.current.localizedString(forRegionCode: currentRegion) ?? currentRegion
    }
}

