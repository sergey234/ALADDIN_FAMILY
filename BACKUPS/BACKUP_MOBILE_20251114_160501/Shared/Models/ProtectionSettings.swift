import Foundation

/// Настройки защиты от угроз
/// ✅ ГИБКАЯ АРХИТЕКТУРА: Использует Dictionary для легкого расширения
/// При добавлении новой категории не нужно менять структуру!
struct ProtectionSettings: Codable {
    // ✅ ГИБКАЯ АРХИТЕКТУРА: Dictionary для легкого расширения
    // При добавлении новой категории не нужно менять структуру!
    private var enabledCategories: [String: Bool] = [:]
    
    // MARK: - Обратная совместимость (для существующих категорий)
    
    var cyberThreatsEnabled: Bool {
        get { enabledCategories["cyberThreats"] ?? false }
        set { enabledCategories["cyberThreats"] = newValue }
    }
    
    var fraudEnabled: Bool {
        get { enabledCategories["fraud"] ?? false }
        set { enabledCategories["fraud"] = newValue }
    }
    
    var childThreatsEnabled: Bool {
        get { enabledCategories["childThreats"] ?? false }
        set { enabledCategories["childThreats"] = newValue }
    }
    
    var dataLeaksEnabled: Bool {
        get { enabledCategories["dataLeaks"] ?? false }
        set { enabledCategories["dataLeaks"] = newValue }
    }
    
    var deepfakesEnabled: Bool {
        get { enabledCategories["deepfakes"] ?? false }
        set { enabledCategories["deepfakes"] = newValue }
    }
    
    var internetThreatsEnabled: Bool {
        get { enabledCategories["internetThreats"] ?? false }
        set { enabledCategories["internetThreats"] = newValue }
    }
    
    var mobileThreatsEnabled: Bool {
        get { enabledCategories["mobileThreats"] ?? false }
        set { enabledCategories["mobileThreats"] = newValue }
    }
    
    var familyThreatsEnabled: Bool {
        get { enabledCategories["familyThreats"] ?? false }
        set { enabledCategories["familyThreats"] = newValue }
    }
    
    var iotThreatsEnabled: Bool {
        get { enabledCategories["iotThreats"] ?? false }
        set { enabledCategories["iotThreats"] = newValue }
    }
    
    // MARK: - Универсальные методы (работают для любых категорий)
    
    /// Проверить, включена ли категория
    func isEnabled(_ category: ThreatProtectionCategory) -> Bool {
        return enabledCategories[category.rawValue] ?? false
    }
    
    /// Установить состояние категории
    mutating func setEnabled(_ category: ThreatProtectionCategory, _ enabled: Bool) {
        enabledCategories[category.rawValue] = enabled
    }
    
    /// Получить все включенные категории
    func enabledCategoriesList() -> [ThreatProtectionCategory] {
        return ThreatProtectionCategory.allCases.filter { isEnabled($0) }
    }
    
    /// Получить все выключенные категории
    func disabledCategoriesList() -> [ThreatProtectionCategory] {
        return ThreatProtectionCategory.allCases.filter { !isEnabled($0) }
    }
    
    // MARK: - Вычисляемые свойства для групп
    
    var deviceProtectionEnabled: Bool {
        let deviceCategories: [ThreatProtectionCategory] = [.cyberThreats, .mobileThreats, .dataLeaks]
        return deviceCategories.allSatisfy { isEnabled($0) }
    }
    
    var internetProtectionEnabled: Bool {
        return isEnabled(.internetThreats)
    }
    
    var familyProtectionEnabled: Bool {
        let familyCategories: [ThreatProtectionCategory] = [.childThreats, .familyThreats, .iotThreats]
        return familyCategories.allSatisfy { isEnabled($0) }
    }
    
    var financeProtectionEnabled: Bool {
        return isEnabled(.fraud)
    }
    
    var premiumProtectionEnabled: Bool {
        return isEnabled(.deepfakes)
    }
    
    // MARK: - Инициализация
    
    /// ✅ АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ: Все категории по умолчанию false
    init() {
        // Инициализируем все существующие категории
        ThreatProtectionCategory.allCases.forEach { category in
            enabledCategories[category.rawValue] = false
        }
    }
    
    /// Инициализация из Dictionary (для загрузки из UserDefaults)
    init(enabledCategories: [String: Bool]) {
        self.enabledCategories = enabledCategories
        // Убеждаемся, что все категории инициализированы
        ThreatProtectionCategory.allCases.forEach { category in
            if self.enabledCategories[category.rawValue] == nil {
                self.enabledCategories[category.rawValue] = false
            }
        }
    }
    
    // MARK: - Codable
    
    enum CodingKeys: String, CodingKey {
        case enabledCategories
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        enabledCategories = try container.decode([String: Bool].self, forKey: .enabledCategories)
        // Убеждаемся, что все категории инициализированы
        ThreatProtectionCategory.allCases.forEach { category in
            if enabledCategories[category.rawValue] == nil {
                enabledCategories[category.rawValue] = false
            }
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(enabledCategories, forKey: .enabledCategories)
    }
}

