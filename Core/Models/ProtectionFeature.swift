import Foundation

/// 🛡️ Protection Feature Model
/// Модель функции защиты с настройками

struct ProtectionFeature: Identifiable, Codable {
    let id: String
    let name: String
    let icon: String
    let description: String
    let defaultLevels: [Int] // На каких уровнях включено по умолчанию
    var isEnabled: Bool
    
    /// Определяет, включена ли функция на данном уровне
    func isEnabledAtLevel(_ level: Int) -> Bool {
        return defaultLevels.contains(level)
    }
    
    /// Получает минимальный уровень для включения функции
    var minLevel: Int {
        return defaultLevels.min() ?? 0
    }
}

/// 🔒 Protection Features Manager
/// Менеджер для управления функциями защиты

class ProtectionFeaturesManager: ObservableObject {
    static let shared = ProtectionFeaturesManager()
    
    @Published var features: [ProtectionFeature] = []
    
    private init() {
        loadDefaultFeatures()
        loadSavedStates()
    }
    
    // MARK: - Default Features
    
    private func loadDefaultFeatures() {
        features = [
            ProtectionFeature(
                id: "website_filter",
                name: "Фильтрация сайтов",
                icon: "globe.badge.chevron.backward",
                description: "Блокировка опасных и нежелательных сайтов",
                defaultLevels: [50, 75, 100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "parental_control",
                name: "Родительский контроль",
                icon: "hand.raised.fill",
                description: "Контроль времени и доступа детей к интернету",
                defaultLevels: [50, 75, 100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "activity_monitoring",
                name: "Мониторинг активности",
                icon: "chart.line.uptrend.xyaxis",
                description: "Отслеживание активности детей в сети",
                defaultLevels: [75, 100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "threat_blocking",
                name: "Блокировка угроз",
                icon: "exclamationmark.triangle.fill",
                description: "Автоматическая блокировка вирусов и фишинга",
                defaultLevels: [75, 100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "app_blocking",
                name: "Блокировка приложений",
                icon: "app.badge",
                description: "Контроль доступа к нежелательным приложениям",
                defaultLevels: [75, 100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "emergency_alerts",
                name: "Экстренные уведомления",
                icon: "bell.badge.fill",
                description: "Мгновенные уведомления о серьезных угрозах",
                defaultLevels: [100],
                isEnabled: false
            ),
            ProtectionFeature(
                id: "ad_blocking",
                name: "Блокировка рекламы",
                icon: "eye.slash.fill",
                description: "Защита от навязчивой рекламы и трекеров",
                defaultLevels: [50, 75, 100],
                isEnabled: false
            )
        ]
    }
    
    // MARK: - Apply Protection Level
    
    /// Применяет уровень защиты, включая соответствующие функции
    func applyProtectionLevel(_ level: Int) {
        for i in 0..<features.count {
            features[i].isEnabled = features[i].isEnabledAtLevel(level)
        }
        saveStates()
    }
    
    // MARK: - Toggle Feature
    
    func toggleFeature(id: String) {
        if let index = features.firstIndex(where: { $0.id == id }) {
            features[index].isEnabled.toggle()
            saveStates()
        }
    }
    
    // MARK: - Get Features for Level
    
    func getFeaturesForLevel(_ level: Int) -> [ProtectionFeature] {
        return features.filter { $0.isEnabledAtLevel(level) }
    }
    
    // MARK: - Get Level Description
    
    func getLevelDescription(_ level: Int) -> (nameKey: String, descriptionKey: String, features: [ProtectionFeature]) {
        let levelFeatures = getFeaturesForLevel(level)
        
        switch level {
        case 0...25:
            return (
                nameKey: "protection_level_low_name",
                descriptionKey: "protection_level_low_desc",
                features: levelFeatures
            )
        case 26...50:
            return (
                nameKey: "protection_level_medium_name",
                descriptionKey: "protection_level_medium_desc",
                features: levelFeatures
            )
        case 51...75:
            return (
                nameKey: "protection_level_high_name",
                descriptionKey: "protection_level_high_desc",
                features: levelFeatures
            )
        case 76...100:
            return (
                nameKey: "protection_level_max_name",
                descriptionKey: "protection_level_max_desc",
                features: levelFeatures
            )
        default:
            return (
                nameKey: "protection_level_medium_name",
                descriptionKey: "protection_level_medium_desc",
                features: []
            )
        }
    }
    
    // MARK: - Save/Load States
    
    private func saveStates() {
        let enabledIds = features.filter { $0.isEnabled }.map { $0.id }
        UserDefaults.standard.set(enabledIds, forKey: "protection_features_enabled")
    }
    
    private func loadSavedStates() {
        guard let enabledIds = UserDefaults.standard.array(forKey: "protection_features_enabled") as? [String] else {
            return
        }
        
        for i in 0..<features.count {
            features[i].isEnabled = enabledIds.contains(features[i].id)
        }
    }
}
