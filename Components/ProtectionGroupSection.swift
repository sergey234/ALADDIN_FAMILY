import SwiftUI

/// 📁 Секция группы категорий защиты
/// Отображает группу (Устройства, Интернет, Семья и т.д.) с её категориями
struct ProtectionGroupSection: View {
    let group: ProtectionGroup
    @ObservedObject var settingsManager: ProtectionSettingsManager
    @ObservedObject var tariffManager: TariffManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок группы
            HStack(spacing: Spacing.s) {
                Text(group.icon)
                    .font(.system(size: 20))
                
                Text(getGroupLocalizedTitle())
                    .font(.title2)
                    .foregroundColor(.textPrimary)
            }
            .padding(.bottom, Spacing.xs)
            
            // Категории в группе
            VStack(spacing: Spacing.xs) {
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
                        isAvailable: tariffManager.isCategoryAvailable(category),
                        onDetailsTap: {
                            navigateToCategoryDetails(category)
                        }
                    )
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    // MARK: - Localization
    
    private func getGroupLocalizedTitle() -> String {
        switch group {
        case .devices:
            return localizationManager.localized("protection_group_devices")
        case .internet:
            return localizationManager.localized("protection_group_internet")
        case .family:
            return localizationManager.localized("protection_group_family")
        case .finance:
            return localizationManager.localized("protection_group_finance")
        case .premium:
            return localizationManager.localized("protection_group_premium")
        }
    }
    
    // MARK: - Navigation
    
    private func navigateToCategoryDetails(_ category: ThreatProtectionCategory) {
        HapticFeedback.selection()
        
        // Проверяем доступность категории
        let isCategoryAvailable = tariffManager.isCategoryAvailable(category)
        
        if isCategoryAvailable {
            if category == .iotThreats {
                navigationManager.navigateToDeviceHub(tab: .iot)
                return
            }
            // ✅ Функция доступна → переход на экран настроек
            if let settingsScreen = category.settingsScreen {
                navigationManager.navigateTo(settingsScreen)
            } else {
                // Если нет специфичного экрана → общий экран настроек защиты
                navigationManager.navigateTo(.threatProtectionSettings)
            }
        } else {
            // ✅ Функция недоступна → ВСЕГДА на Тарифы (не на VPN или другие экраны!)
            navigationManager.navigateTo(.tariffs)
        }
    }
}

#if DEBUG
struct ProtectionGroupSection_Previews: PreviewProvider {
    static var previews: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ProtectionGroupSection(
                    group: .devices,
                    settingsManager: ProtectionSettingsManager.shared,
                    tariffManager: TariffManager.shared
                )
                .environmentObject(LocalizationManager())
                .environmentObject(NavigationManager())
            }
            .padding()
        }
        .background(Color.backgroundDark)
    }
}
#endif

