import SwiftUI

/// 📖 Галерея сценариев угроз
/// Горизонтальный слайдер с реальными сценариями угроз
struct ThreatScenariosGallery: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var tariffManager = TariffManager.shared
    
    // MARK: - Scenarios Data
    
    let scenarios: [ThreatScenario] = [
        ThreatScenario(
            id: "fraud",
            title: "Угрозы мошенничества",
            description: "Мошенники могут украсть ваши деньги через поддельные сайты и звонки",
            icon: "💰",
            requiredTariff: .family,
            category: .fraud,
            protectionSteps: [
                "Включить защиту от мошенничества",
                "Настроить уведомления о подозрительных операциях"
            ]
        ),
        ThreatScenario(
            id: "phishing",
            title: "Фишинговые письма",
            description: "Поддельные письма и сайты для кражи паролей и данных",
            icon: "📧",
            requiredTariff: .personal,
            category: .internetThreats,
            protectionSteps: [
                "Включить антифишинг",
                "Проверить настройки почты"
            ]
        ),
        ThreatScenario(
            id: "malware",
            title: "Вредные приложения",
            description: "Вирусы и трояны в приложениях из неофициальных источников",
            icon: "📱",
            requiredTariff: .personal,
            category: .mobileThreats,
            protectionSteps: [
                "Включить сканирование приложений",
                "Обновить базу угроз"
            ]
        ),
        ThreatScenario(
            id: "child_content",
            title: "Опасный контент для детей",
            description: "Дети могут столкнуться с нежелательным контентом в интернете",
            icon: "👶",
            requiredTariff: .family,
            category: .childThreats,
            protectionSteps: [
                "Включить родительский контроль",
                "Настроить фильтры контента"
            ]
        ),
        ThreatScenario(
            id: "iot_attack",
            title: "Угрозы IoT",
            description: "Умные устройства могут быть взломаны и использованы для атак",
            icon: "🏡",
            requiredTariff: .family,
            category: .iotThreats,
            protectionSteps: [
                "Включить защиту IoT устройств",
                "Проверить безопасность сети"
            ]
        ),
        ThreatScenario(
            id: "deepfake",
            title: "Deepfake атаки",
            description: "Поддельные видео и аудио для обмана и манипуляций",
            icon: "🎭",
            requiredTariff: .premium,
            category: .deepfakes,
            protectionSteps: [
                "Включить обнаружение deepfake",
                "Настроить проверку медиа"
            ]
        )
    ]
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок
            Text(localizationManager.localized("protection_scenarios_title"))
                .font(.title2)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            // Горизонтальный слайдер
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.m) {
                    ForEach(scenarios) { scenario in
                        ThreatScenarioCard(scenario: scenario)
                            .frame(width: 280)
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
        }
        .padding(.vertical, Spacing.m)
    }
}

// MARK: - Threat Scenario Model

struct ThreatScenario: Identifiable {
    let id: String
    let title: String
    let description: String
    let icon: String
    let requiredTariff: TariffType
    let category: ThreatProtectionCategory
    let protectionSteps: [String]
}

// MARK: - Threat Scenario Card

struct ThreatScenarioCard: View {
    let scenario: ThreatScenario
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var tariffManager = TariffManager.shared
    
    /// Проверка доступности: используем requiredTariff сценария, а не категории
    var isAvailable: Bool {
        let currentTariff = tariffManager.currentTariff
        let requiredLevel = tariffLevel(scenario.requiredTariff)
        let currentLevel = tariffLevel(currentTariff)
        return currentLevel >= requiredLevel
    }
    
    /// Получить уровень тарифа (для сравнения)
    private func tariffLevel(_ tariffType: TariffType) -> Int {
        switch tariffType {
        case .free: return 0
        case .personal: return 1
        case .family: return 2
        case .premium: return 3
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Иконка
            Text(scenario.icon)
                .font(.system(size: 32))
            
            // Заголовок
            Text(scenario.title)
                .font(.headline)
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            
            // Описание
            Text(scenario.description)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .lineLimit(3)
                .fixedSize(horizontal: false, vertical: true)
            
            Spacer()
            
            // Индикатор доступности
            if !isAvailable {
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "lock.fill")
                        .font(.caption2)
                    Text("\(localizationManager.localized("protection_requires_tariff")): \(scenario.requiredTariff.title(localizationManager: localizationManager))")
                        .font(.caption)
                        .lineLimit(1) // ✅ Размещаем на одной строке
                }
                .foregroundColor(.warningOrange)
            }
            
            // Кнопка действия
            Button(action: {
                handleActionTap()
            }) {
                HStack {
                    Text(isAvailable ? 
                         localizationManager.localized("protection_scenario_how_to_protect") :
                         localizationManager.localized("protection_scenario_get_protection"))
                        .font(.captionBold)
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .font(.caption2)
                }
                .foregroundColor(.secondaryGold)
                .padding(.vertical, Spacing.xs)
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(isAvailable ? Color.secondaryGold.opacity(0.3) : Color.warningOrange.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
    
    // MARK: - Navigation
    
    private func handleActionTap() {
        HapticFeedback.selection()
        
        // ✅ ПРАВИЛЬНАЯ ЛОГИКА: Если функция недоступна → всегда на Тарифы
        // Если доступна → на настройки (но только если есть settingsScreen, иначе на общий экран настроек)
        if isAvailable {
            // Функция доступна → переход на экран настроек
            // Используем settingsScreen категории, если он есть
            if let settingsScreen = scenario.category.settingsScreen {
                navigationManager.navigateTo(settingsScreen)
            } else {
                // Если нет специфичного экрана → общий экран настроек защиты
                navigationManager.navigateTo(.threatProtectionSettings)
            }
        } else {
            // ✅ Функция недоступна → ВСЕГДА на Тарифы (не на VPN!)
            navigationManager.navigateTo(.tariffs)
        }
    }
}

#if DEBUG
struct ThreatScenariosGallery_Previews: PreviewProvider {
    static var previews: some View {
        ThreatScenariosGallery()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
            .background(Color.backgroundDark)
    }
}
#endif

