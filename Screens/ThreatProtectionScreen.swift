import SwiftUI

struct ThreatProtectionScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .shield)
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("protection_catalog_title"),
                    subtitle: localizationManager.localized("protection_catalog_subtitle"),
                    showBackButton: true, // Всегда показываем кнопку "Назад" для возврата на главный экран
                    showProfileButton: false, // Убираем кнопку профиля
                    showListButton: false, // Убираем кнопку списка экранов
                    onBack: {
                        // ✅ ИСПРАВЛЕНИЕ: Используем NavigationManager для возврата
                        // Это гарантирует правильную навигацию на реальном устройстве
                        if navigationManager.canGoBack {
                            navigationManager.goBack(reason: "ThreatProtection.onBack")
                        } else {
                            // Если стек пуст, возвращаемся на главную
                            navigationManager.currentScreen = .main
                        }
                    }
                )
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Галерея тарифов и краткое резюме
                        TariffFeaturesGallery()
                            .padding(.top, Spacing.m)
                        
                        protectionSummaryCard
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        antifakeQuickAccessCard
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        // Группы функций защиты (включая IoT‑защиту внутри семейной группы)
                        VStack(spacing: Spacing.l) {
                            ForEach(ProtectionGroup.allCases) { group in
                                ProtectionGroupSection(
                                    group: group,
                                    settingsManager: settingsManager,
                                    tariffManager: tariffManager
                                )
                            }
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.bottom, Spacing.xxl)
                    }
                }
            }
        }
        .navigationBarHidden(true)
        .id("protection_catalog_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    private var protectionSummaryCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("protection_settings_title"))
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Text(localizationManager.localized("protection_settings_subtitle"))
                .font(.body)
                .foregroundColor(.textSecondary)
            
            Divider()
                .background(Color.white.opacity(0.2))
            
            Text(localizationManager.localized("protection_what_this_gives"))
                .font(.footnote.weight(.semibold))
                .foregroundColor(.textSecondary)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                ForEach(protectionHighlights, id: \.self) { key in
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Text("•")
                            .font(.body.weight(.bold))
                            .foregroundColor(.primaryBlue)
                        Text(localizationManager.localized(key))
                            .font(.footnote)
                            .foregroundColor(.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
            
            Button {
                navigationManager.navigateTo(.tariffs)
            } label: {
                Text(localizationManager.localized("tariffs_compare_all"))
                    .font(.buttonText)
                    .frame(maxWidth: .infinity)
                    .frame(height: Size.buttonHeight)
                    .background(Color.primaryBlue)
                    .foregroundColor(.white)
                    .cornerRadius(CornerRadius.medium)
            }
            .padding(.top, Spacing.s)
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
    }
    
    private var protectionHighlights: [String] {
        [
            "protection_benefit_cyber",
            "protection_benefit_fraud",
            "protection_benefit_child",
            "protection_benefit_data",
            "protection_benefit_iot"
        ]
    }
    
    private var antifakeQuickAccessCard: some View {
        Button {
            HapticFeedback.selection()
            if tariffManager.isCategoryAvailable(.deepfakes) {
                navigationManager.navigateTo(.antifakeHub)
            } else {
                navigationManager.navigateTo(.tariffs)
            }
        } label: {
            HStack(spacing: Spacing.m) {
                Text("🎭")
                    .font(.system(size: 32))
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("protection_antifake_card_title"))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("protection_antifake_card_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.leading)
                }
                Spacer()
                Text(localizationManager.localized("protection_open_check_button"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(localizationManager.localized("protection_antifake_card_title"))
    }
}

#if DEBUG
struct ThreatProtectionScreen_Previews: PreviewProvider {
    static var previews: some View {
        ThreatProtectionScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif
