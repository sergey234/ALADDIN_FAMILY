# 🏗️ ДЕТАЛЬНАЯ АРХИТЕКТУРА: Система защиты от 100 видов угроз

**Дата:** 2025-11-12  
**Автор:** Senior Mobile Architect (15+ лет опыта)  
**Цель:** Создать лучшее приложение для защиты семьи от киберугроз

---

## 📊 EXECUTIVE SUMMARY

### Проблема
9 категорий угроз → нужно ли создавать 9 отдельных экранов?

### Решение
**Единая система управления защитой:**
- 1 экран каталога (ThreatProtectionScreen) — просмотр всех угроз
- 1 экран настроек (ThreatProtectionSettingsScreen) — управление всеми категориями
- Автоматическая активация при покупке тарифа
- Умная навигация на детальные экраны

### Принципы
1. **Простота** — минимум экранов, максимум функциональности
2. **Понятность** — интуитивная навигация, понятные статусы
3. **Красота** — современный дизайн, плавные анимации
4. **Функциональность** — всё работает, ничего лишнего

---

## 🎯 АРХИТЕКТУРНАЯ ДИАГРАММА

```
┌─────────────────────────────────────────────────────────────┐
│                    ПОЛЬЗОВАТЕЛЬСКИЙ FLOW                      │
└─────────────────────────────────────────────────────────────┘

MainScreen
    │
    ├─→ [Защита] → ThreatProtectionScreen (Каталог)
    │                    │
    │                    ├─→ Просмотр 9 категорий
    │                    ├─→ Расширенные карточки (статус, совет, кнопка)
    │                    ├─→ Галерея сценариев
    │                    │
    │                    └─→ [Подробнее] → ThreatProtectionSettingsScreen
    │                                         │
    │                                         ├─→ Группа 1: Устройства (3)
    │                                         ├─→ Группа 2: Интернет (1)
    │                                         ├─→ Группа 3: Семья (3)
    │                                         ├─→ Группа 4: Финансы (1)
    │                                         ├─→ Группа 5: Премиум (1)
    │                                         │
    │                                         └─→ [Подробнее] → Детальные экраны
    │                                                              │
    │                                                              ├─→ ParentalControlScreen
    │                                                              ├─→ IoTSecurityScreen
    │                                                              ├─→ VPNScreen
    │                                                              ├─→ DeviceDetailScreen
    │                                                              └─→ ProfileScreen
    │
    └─→ [Тарифы] → TariffsScreen
                        │
                        ├─→ Выбор тарифа
                        ├─→ Покупка (QR/IAP)
                        │
                        └─→ [После покупки] → Автоматическая активация
                                                │
                                                └─→ ProtectionSettingsManager
                                                    .enableForTariff()
```

---

## 🧩 КОМПОНЕНТЫ СИСТЕМЫ

### 1. Модель данных

```swift
// Shared/Models/ThreatProtectionCategory.swift
enum ThreatProtectionCategory: String, CaseIterable, Identifiable {
    case cyberThreats      // 🛡️ Киберугрозы
    case fraud             // 💰 Мошенничество
    case childThreats      // 👶 Угрозы для детей
    case dataLeaks         // 🔒 Утечки данных
    case deepfakes         // 🎭 Deepfakes
    case internetThreats   // 🌐 Интернет-угрозы
    case mobileThreats     // 📱 Мобильные угрозы
    case familyThreats     // 🏠 Семейные угрозы
    case iotThreats        // 🏡 IoT угрозы
    
    // ✅ ГИБКАЯ АРХИТЕКТУРА: Конфигурация через Dictionary
    // При добавлении новой категории просто добавляем запись в configurations!
    static var configurations: [ThreatProtectionCategory: CategoryConfiguration] {
        [
            .cyberThreats: CategoryConfiguration(
                requiredTariff: .free,
                benefit: "Блокирует вирусы, трояны, фишинг",
                settingsScreen: .deviceDetail,
                group: .devices
            ),
            .fraud: CategoryConfiguration(
                requiredTariff: .personal,
                benefit: "Предотвращает финансовое мошенничество",
                settingsScreen: .profile,
                group: .finance
            ),
            .childThreats: CategoryConfiguration(
                requiredTariff: .family,
                benefit: "Защищает детей от опасного контента",
                settingsScreen: .parentalControl,
                group: .family
            ),
            .dataLeaks: CategoryConfiguration(
                requiredTariff: .personal,
                benefit: "Предупреждает об утечках данных",
                settingsScreen: .deviceDetail,
                group: .devices
            ),
            .deepfakes: CategoryConfiguration(
                requiredTariff: .premium,
                benefit: "Обнаруживает поддельные видео и аудио",
                settingsScreen: .advancedProtection,
                group: .premium
            ),
            .internetThreats: CategoryConfiguration(
                requiredTariff: .free,
                benefit: "Защищает от вредоносных сайтов",
                settingsScreen: .vpn,
                group: .internet
            ),
            .mobileThreats: CategoryConfiguration(
                requiredTariff: .personal,
                benefit: "Блокирует вредные приложения",
                settingsScreen: .deviceDetail,
                group: .devices
            ),
            .familyThreats: CategoryConfiguration(
                requiredTariff: .family,
                benefit: "Защищает всю семью",
                settingsScreen: .parentalControl,
                group: .family
            ),
            .iotThreats: CategoryConfiguration(
                requiredTariff: .family,
                benefit: "Защищает умные устройства",
                settingsScreen: .iotSecurity,
                group: .family
            )
        ]
    }
    
    // ✅ СВОЙСТВА ЧЕРЕЗ КОНФИГУРАЦИЮ: Автоматически работают для новых категорий
    var config: CategoryConfiguration {
        return Self.configurations[self] ?? CategoryConfiguration.default
    }
    
    var requiredTariff: TariffType { config.requiredTariff }
    var benefit: String { config.benefit }
    var settingsScreen: NavigationManager.ALADDINScreen? { config.settingsScreen }
    var group: ProtectionGroup { config.group }
}

// ✅ КОНФИГУРАЦИЯ КАТЕГОРИИ: Вся информация в одном месте
struct CategoryConfiguration {
    let requiredTariff: TariffType
    let benefit: String
    let settingsScreen: NavigationManager.ALADDINScreen?
    let group: ProtectionGroup
    
    static var `default`: CategoryConfiguration {
        CategoryConfiguration(
            requiredTariff: .free,
            benefit: "",
            settingsScreen: nil,
            group: .devices
        )
    }
}

enum ProtectionGroup: String, CaseIterable {
    case devices = "УСТРОЙСТВА"
    case internet = "ИНТЕРНЕТ"
    case family = "СЕМЬЯ"
    case finance = "ФИНАНСЫ"
    case premium = "ПРЕМИУМ"
    
    // ✅ ГИБКАЯ АРХИТЕКТУРА: Автоматически собирает категории из конфигурации
    var categories: [ThreatProtectionCategory] {
        return ThreatProtectionCategory.allCases.filter { category in
            category.group == self
        }
    }
    
    // Альтернатива: можно использовать switch для явного контроля
    // var categories: [ThreatProtectionCategory] {
    //     switch self {
    //     case .devices: return [.cyberThreats, .mobileThreats, .dataLeaks]
    //     case .internet: return [.internetThreats]
    //     case .family: return [.childThreats, .familyThreats, .iotThreats]
    //     case .finance: return [.fraud]
    //     case .premium: return [.deepfakes]
    //     }
    // }
    
    var icon: String {
        switch self {
        case .devices: return "📱"
        case .internet: return "🌐"
        case .family: return "👨‍👩‍👧‍👦"
        case .finance: return "💰"
        case .premium: return "💎"
        }
    }
}
```

---

### 2. Модель настроек защиты (ГИБКАЯ АРХИТЕКТУРА)

```swift
// Shared/Models/ProtectionSettings.swift
struct ProtectionSettings: Codable {
    // ✅ ГИБКАЯ АРХИТЕКТУРА: Dictionary для легкого расширения
    // При добавлении новой категории не нужно менять структуру!
    private var enabledCategories: [String: Bool] = [:]
    
    // Обратная совместимость (для существующих категорий)
    var cyberThreatsEnabled: Bool {
        get { enabledCategories["cyberThreats"] ?? false }
        set { enabledCategories["cyberThreats"] = newValue }
    }
    var fraudEnabled: Bool {
        get { enabledCategories["fraud"] ?? false }
        set { enabledCategories["fraud"] = newValue }
    }
    // ... остальные для обратной совместимости
    
    // ✅ УНИВЕРСАЛЬНЫЕ МЕТОДЫ: Работают для любых категорий
    func isEnabled(_ category: ThreatProtectionCategory) -> Bool {
        return enabledCategories[category.rawValue] ?? false
    }
    
    mutating func setEnabled(_ category: ThreatProtectionCategory, _ enabled: Bool) {
        enabledCategories[category.rawValue] = enabled
    }
    
    // ✅ АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ: Все категории по умолчанию false
    init() {
        // Инициализируем все существующие категории
        ThreatProtectionCategory.allCases.forEach { category in
            enabledCategories[category.rawValue] = false
        }
    }
    
    // Вычисляемые свойства для групп
    var deviceProtectionEnabled: Bool {
        cyberThreatsEnabled && mobileThreatsEnabled && dataLeaksEnabled
    }
    
    var internetProtectionEnabled: Bool {
        internetThreatsEnabled
    }
    
    var familyProtectionEnabled: Bool {
        childThreatsEnabled && familyThreatsEnabled && iotThreatsEnabled
    }
    
    var financeProtectionEnabled: Bool {
        fraudEnabled
    }
    
    var premiumProtectionEnabled: Bool {
        deepfakesEnabled
    }
}
```

---

### 3. Менеджер настроек защиты

```swift
// Managers/ProtectionSettingsManager.swift
@MainActor
class ProtectionSettingsManager: ObservableObject {
    static let shared = ProtectionSettingsManager()
    
    @Published var settings: ProtectionSettings = ProtectionSettings()
    
    private let userDefaults = UserDefaults.standard
    private let settingsKey = "protection_settings"
    
    private init() {
        loadSettings()
    }
    
    // MARK: - Load & Save
    
    func loadSettings() {
        if let data = userDefaults.data(forKey: settingsKey),
           let decoded = try? JSONDecoder().decode(ProtectionSettings.self, from: data) {
            settings = decoded
        }
    }
    
    func saveSettings() {
        if let encoded = try? JSONEncoder().encode(settings) {
            userDefaults.set(encoded, forKey: settingsKey)
        }
    }
    
    // MARK: - Enable/Disable Category
    
    func toggleCategory(_ category: ThreatProtectionCategory) {
        let currentState = settings.isEnabled(category)
        settings.setEnabled(category, !currentState)
        saveSettings()
    }
    
    func enableCategory(_ category: ThreatProtectionCategory) {
        settings.setEnabled(category, true)
        saveSettings()
    }
    
    func disableCategory(_ category: ThreatProtectionCategory) {
        settings.setEnabled(category, false)
        saveSettings()
    }
    
    // MARK: - Tariff Integration
    
    func enableForTariff(_ tariff: TariffType) {
        switch tariff {
        case .free:
            enableCategory(.cyberThreats)
            enableCategory(.internetThreats)
            
        case .personal:
            enableCategory(.cyberThreats)
            enableCategory(.internetThreats)
            enableCategory(.fraud)
            enableCategory(.mobileThreats)
            enableCategory(.dataLeaks)
            
        case .family:
            enableCategory(.cyberThreats)
            enableCategory(.internetThreats)
            enableCategory(.fraud)
            enableCategory(.mobileThreats)
            enableCategory(.dataLeaks)
            enableCategory(.childThreats)
            enableCategory(.familyThreats)
            enableCategory(.iotThreats)
            
        case .premium:
            // Включаем всё
            ThreatProtectionCategory.allCases.forEach { category in
                enableCategory(category)
            }
        }
    }
    
    // MARK: - Availability Check
    
    func isCategoryAvailable(_ category: ThreatProtectionCategory, 
                            in tariff: TariffType) -> Bool {
        return category.requiredTariff.level <= tariff.level
    }
}
```

---

### 4. Менеджер тарифов

```swift
// Managers/TariffManager.swift
@MainActor
class TariffManager: ObservableObject {
    static let shared = TariffManager()
    
    @Published var currentTariff: TariffType = .free
    
    private let userDefaults = UserDefaults.standard
    private let tariffKey = "current_tariff"
    
    private init() {
        loadTariff()
        observeTariffChanges()
    }
    
    // MARK: - Load & Save
    
    func loadTariff() {
        if let tariffString = userDefaults.string(forKey: tariffKey),
           let tariff = TariffType(rawValue: tariffString) {
            currentTariff = tariff
        }
    }
    
    func saveTariff(_ tariff: TariffType) {
        currentTariff = tariff
        userDefaults.set(tariff.rawValue, forKey: tariffKey)
        
        // Автоматически включаем функции для тарифа
        ProtectionSettingsManager.shared.enableForTariff(tariff)
    }
    
    // MARK: - Tariff Level
    
    extension TariffType {
        var level: Int {
            switch self {
            case .free: return 0
            case .personal: return 1
            case .family: return 2
            case .premium: return 3
            }
        }
    }
    
    // MARK: - Observers
    
    private func observeTariffChanges() {
        // Подписка на изменения в StoreManager
        NotificationCenter.default.addObserver(
            forName: .tariffPurchased,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            if let tariff = notification.userInfo?["tariff"] as? TariffType {
                self?.saveTariff(tariff)
            }
        }
    }
}
```

---

## 🎨 UI КОМПОНЕНТЫ

### 1. Расширенная карточка категории

```swift
// Components/EnhancedThreatCategoryCard.swift
struct EnhancedThreatCategoryCard: View {
    let category: ThreatProtectionCategory
    @Binding var isExpanded: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    var isEnabled: Bool {
        settingsManager.settings.isEnabled(category)
    }
    
    var isAvailable: Bool {
        settingsManager.isCategoryAvailable(category, in: tariffManager.currentTariff)
    }
    
    var statusColor: Color {
        if !isAvailable {
            return .red
        } else if isEnabled {
            return .green
        } else {
            return .yellow
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с статусом
            HStack(spacing: Spacing.m) {
                Text(category.emoji)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(category.localizedTitle(localizationManager))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    Text("\(category.count) видов защиты")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                // Статус-индикатор
                Circle()
                    .fill(statusColor)
                    .frame(width: 12, height: 12)
            }
            
            if isExpanded {
                // Блок "Что это даёт"
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("💡 Что это даёт:")
                        .font(.captionBold)
                        .foregroundColor(.textSecondary)
                    
                    Text(category.benefit)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.xs)
                
                // Мотивационный баннер (если недоступно)
                if !isAvailable {
                    MotivationBanner(
                        category: category,
                        requiredTariff: category.requiredTariff
                    )
                }
                
                // Кнопка "Подробнее"
                Button(action: {
                    handleDetailsTap()
                }) {
                    HStack {
                        Text("Подробнее")
                            .font(.body)
                        Image(systemName: "chevron.right")
                            .font(.caption)
                    }
                    .foregroundColor(.secondaryGold)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(isEnabled ? Color.green.opacity(0.1) : Color.backgroundMedium)
        )
    }
    
    private func handleDetailsTap() {
        if isAvailable {
            // Переход на экран настроек или детальный экран
            if let settingsScreen = category.settingsScreen {
                navigationManager.navigateTo(settingsScreen)
            } else {
                // Переход на единый экран настроек защиты
                navigationManager.navigateTo(.threatProtectionSettings)
            }
        } else {
            // Переход на тарифы с подсветкой нужного тарифа
            navigationManager.navigateTo(.tariffs)
            // TODO: Подсветить нужный тариф
        }
    }
}
```

---

### 2. Мотивационный баннер

```swift
// Components/MotivationBanner.swift
struct MotivationBanner: View {
    let category: ThreatProtectionCategory
    let requiredTariff: TariffType
    @EnvironmentObject private var navigationManager: NavigationManager
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "lock.fill")
                .foregroundColor(.orange)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text("Требует тариф \(requiredTariff.title)")
                    .font(.captionBold)
                    .foregroundColor(.orange)
                
                Text("Обновите тариф для полной защиты")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Button(action: {
                navigationManager.navigateTo(.tariffs)
            }) {
                Text("Обновить")
                    .font(.captionBold)
                    .foregroundColor(.orange)
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.orange.opacity(0.1))
        )
    }
}
```

---

### 3. Галерея сценариев

```swift
// Components/ThreatScenariosGallery.swift
struct ThreatScenariosGallery: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var tariffManager = TariffManager.shared
    
    let scenarios: [ThreatScenario] = [
        ThreatScenario(
            id: "fraud",
            title: "Угрозы мошенничества",
            description: "Мошенники могут украсть ваши деньги через поддельные сайты и звонки",
            icon: "💰",
            requiredTariff: .family,
            protectionSteps: ["Включить защиту от мошенничества", "Настроить уведомления"]
        ),
        ThreatScenario(
            id: "phishing",
            title: "Фишинговые письма",
            description: "Поддельные письма и сайты для кражи паролей",
            icon: "📧",
            requiredTariff: .personal,
            protectionSteps: ["Включить антифишинг", "Проверить настройки почты"]
        ),
        ThreatScenario(
            id: "malware",
            title: "Вредные приложения",
            description: "Вирусы и трояны в приложениях",
            icon: "📱",
            requiredTariff: .personal,
            protectionSteps: ["Включить сканирование приложений", "Обновить базу угроз"]
        )
    ]
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📖 Реальные сценарии угроз")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.m) {
                    ForEach(scenarios) { scenario in
                        ThreatScenarioCard(scenario: scenario)
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
        }
    }
}

struct ThreatScenario: Identifiable {
    let id: String
    let title: String
    let description: String
    let icon: String
    let requiredTariff: TariffType
    let protectionSteps: [String]
}

struct ThreatScenarioCard: View {
    let scenario: ThreatScenario
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var tariffManager = TariffManager.shared
    
    var isAvailable: Bool {
        scenario.requiredTariff.level <= tariffManager.currentTariff.level
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(scenario.icon)
                .font(.system(size: 32))
            
            Text(scenario.title)
                .font(.h4)
                .foregroundColor(.textPrimary)
            
            Text(scenario.description)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .lineLimit(3)
            
            if !isAvailable {
                HStack {
                    Image(systemName: "lock.fill")
                    Text("Требует: \(scenario.requiredTariff.title)")
                }
                .font(.caption)
                .foregroundColor(.orange)
            }
            
            Button(action: {
                if isAvailable {
                    // Переход на настройки
                    navigationManager.navigateTo(.threatProtectionSettings)
                } else {
                    // Переход на тарифы
                    navigationManager.navigateTo(.tariffs)
                }
            }) {
                Text(isAvailable ? "Как защититься" : "Получить защиту")
                    .font(.captionBold)
                    .foregroundColor(.white)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(isAvailable ? Color.secondaryGold : Color.orange)
                    )
            }
        }
        .padding(Spacing.m)
        .frame(width: 280)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium)
        )
    }
}
```

---

### 4. Единый экран настроек защиты

```swift
// Screens/ThreatProtectionSettingsScreen.swift
struct ThreatProtectionSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: "Настройки защиты",
                    subtitle: "Управление всеми категориями",
                    showBackButton: true,
                    onBack: {
                        navigationManager.goBack()
                    }
                )
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Группы категорий
                        ForEach(ProtectionGroup.allCases, id: \.self) { group in
                            ProtectionGroupSection(
                                group: group,
                                settingsManager: settingsManager,
                                tariffManager: tariffManager
                            )
                        }
                    }
                    .padding(Spacing.screenPadding)
                }
            }
        }
    }
}

struct ProtectionGroupSection: View {
    let group: ProtectionGroup
    @ObservedObject var settingsManager: ProtectionSettingsManager
    @ObservedObject var tariffManager: TariffManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок группы
            HStack {
                Text(group.icon)
                    .font(.system(size: 20))
                Text(group.rawValue)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            
            // Категории в группе
            ForEach(group.categories, id: \.id) { category in
                ProtectionCategoryRow(
                    category: category,
                    isEnabled: Binding(
                        get: { settingsManager.settings.isEnabled(category) },
                        set: { newValue in
                            if newValue {
                                settingsManager.enableCategory(category)
                            } else {
                                settingsManager.disableCategory(category)
                            }
                        }
                    ),
                    isAvailable: settingsManager.isCategoryAvailable(
                        category,
                        in: tariffManager.currentTariff
                    ),
                    onDetailsTap: {
                        navigateToCategoryDetails(category)
                    }
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium)
        )
    }
    
    private func navigateToCategoryDetails(_ category: ThreatProtectionCategory) {
        if let settingsScreen = category.settingsScreen {
            navigationManager.navigateTo(settingsScreen)
        }
    }
}

struct ProtectionCategoryRow: View {
    let category: ThreatProtectionCategory
    @Binding var isEnabled: Bool
    let isAvailable: Bool
    let onDetailsTap: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(category.emoji)
                .font(.system(size: 24))
            
            // Название и описание
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(category.localizedTitle(localizationManager))
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("\(category.count) видов защиты")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            // Переключатель или баннер
            if isAvailable {
                ALADDINToggle(isOn: $isEnabled)
            } else {
                MotivationBanner(
                    category: category,
                    requiredTariff: category.requiredTariff
                )
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(isEnabled ? Color.green.opacity(0.1) : Color.clear)
        )
    }
}
```

---

## 🔄 FLOW ДИАГРАММЫ

### Flow 1: Просмотр каталога угроз

```
User → MainScreen → [Защита] → ThreatProtectionScreen
                                    │
                                    ├─→ Просмотр 9 категорий
                                    ├─→ Раскрытие категории → Расширенная карточка
                                    │   ├─→ Статус (🟢🟡🔴)
                                    │   ├─→ Совет "Что это даёт"
                                    │   └─→ Кнопка "Подробнее"
                                    │
                                    └─→ Галерея сценариев
                                        └─→ Карточка сценария → [Как защититься]
```

### Flow 2: Настройка защиты

```
User → ThreatProtectionScreen → [Подробнее] → ThreatProtectionSettingsScreen
                                                      │
                                                      ├─→ Группа 1: Устройства
                                                      │   ├─→ Киберугрозы [ON/OFF]
                                                      │   ├─→ Мобильные [ON/OFF]
                                                      │   └─→ Утечки [ON/OFF]
                                                      │
                                                      ├─→ Группа 2: Интернет
                                                      │   └─→ Интернет-угрозы [ON/OFF]
                                                      │
                                                      ├─→ Группа 3: Семья
                                                      │   ├─→ Дети [ON/OFF] → ParentalControl
                                                      │   ├─→ Семья [ON/OFF] → FamilyScreen
                                                      │   └─→ IoT [ON/OFF] → IoTSecurity
                                                      │
                                                      ├─→ Группа 4: Финансы
                                                      │   └─→ Мошенничество [ON/OFF] → Profile
                                                      │
                                                      └─→ Группа 5: Премиум
                                                          └─→ Deepfakes [ON/OFF] → AdvancedProtection
```

### Flow 3: Покупка тарифа и активация

```
User → TariffsScreen → Выбор тарифа → Покупка (QR/IAP)
                                                    │
                                                    └─→ Успешная покупка
                                                        │
                                                        ├─→ TariffManager.saveTariff()
                                                        │
                                                        └─→ ProtectionSettingsManager
                                                            .enableForTariff()
                                                            │
                                                            └─→ Автоматическое включение
                                                                категорий по тарифу
```

---

## 📱 НАВИГАЦИЯ

### Добавление новых экранов в NavigationManager

```swift
// Core/Navigation/NavigationManager.swift
enum ALADDINScreen: String, CaseIterable {
    // ... существующие экраны ...
    
    // НОВЫЕ ЭКРАНЫ
    case threatProtection = "ThreatProtectionScreen"
    case threatProtectionSettings = "ThreatProtectionSettingsScreen"
    case iotSecurity = "IoTSecurityScreen"
    case advancedProtection = "AdvancedProtectionSettingsScreen"
    
    var displayName: String {
        switch self {
        // ... существующие ...
        case .threatProtection: return "Защита"
        case .threatProtectionSettings: return "Настройки защиты"
        case .iotSecurity: return "IoT защита"
        case .advancedProtection: return "Расширенная защита"
        }
    }
    
    var icon: String {
        switch self {
        // ... существующие ...
        case .threatProtection: return "shield.lefthalf.filled"
        case .threatProtectionSettings: return "gearshape.2.fill"
        case .iotSecurity: return "house.fill"
        case .advancedProtection: return "lock.shield.fill"
        }
    }
}
```

---

## 💾 ХРАНЕНИЕ ДАННЫХ

### UserDefaults Keys

```swift
// Core/Storage/StorageKeys.swift
enum ProtectionStorageKeys {
    static let protectionSettings = "protection_settings"
    static let currentTariff = "current_tariff"
    static let lastTariffUpdate = "last_tariff_update"
}
```

### Структура хранения

```swift
// ProtectionSettings хранится как JSON в UserDefaults
{
    "cyberThreatsEnabled": true,
    "fraudEnabled": false,
    "childThreatsEnabled": true,
    // ... остальные категории
}

// Tariff хранится как String
"current_tariff" = "family"
```

---

## 🔗 ИНТЕГРАЦИЯ С ТАРИФАМИ

### Обработка покупки тарифа

```swift
// ViewModels/TariffsViewModel.swift
func purchaseTariff(_ tariff: Tariff) async {
    // ... существующая логика покупки ...
    
    // После успешной покупки
    if transaction != nil {
        // Определяем тип тарифа
        let tariffType: TariffType = {
            switch tariff.id {
            case "free": return .free
            case "personal": return .personal
            case "family": return .family
            case "premium": return .premium
            default: return .free
            }
        }()
        
        // Сохраняем тариф
        TariffManager.shared.saveTariff(tariffType)
        
        // Уведомление о покупке
        NotificationCenter.default.post(
            name: .tariffPurchased,
            object: nil,
            userInfo: ["tariff": tariffType]
        )
    }
}
```

---

## 🎯 ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### Этап 1: Базовая инфраструктура (КРИТИЧНО)
1. ✅ Модель данных (ProtectionSettings, ThreatProtectionCategory extensions)
2. ✅ ProtectionSettingsManager
3. ✅ TariffManager
4. ✅ Добавить навигацию в NavigationManager

### Этап 2: UI компоненты
1. ✅ EnhancedThreatCategoryCard
2. ✅ MotivationBanner
3. ✅ ThreatScenariosGallery
4. ✅ ProtectionCategoryRow

### Этап 3: Экраны
1. ✅ Обновить ThreatProtectionScreen (расширенные карточки)
2. ✅ Создать ThreatProtectionSettingsScreen
3. ✅ Добавить галерею сценариев

### Этап 4: Интеграция
1. ✅ Интеграция с тарифами (автоматическая активация)
2. ✅ Навигация на детальные экраны
3. ✅ Мотивационные баннеры

---

## ✅ КРИТЕРИИ УСПЕХА

1. **Простота**: Пользователь понимает, что делать без инструкций
2. **Понятность**: Все статусы и действия очевидны
3. **Красота**: Современный дизайн, плавные анимации
4. **Функциональность**: Всё работает, ничего не ломается
5. **Производительность**: Быстрая загрузка, плавная анимация
6. **Масштабируемость**: Легко добавить новые категории

---

**Дата создания:** 2025-11-12  
**Статус:** Готово к реализации  
**Следующий шаг:** Начать с Этапа 1 (базовая инфраструктура)

