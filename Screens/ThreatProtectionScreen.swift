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
                        
                        AntifakeQuickAccessCard()
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
}

// MARK: - Antifake quick access (ux-1-06 — Защита + каталог)

struct AntifakeQuickAccessCard: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var tariffManager = TariffManager.shared
    @State private var showAppleLimits = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Button {
                openHub()
            } label: {
                HStack(spacing: Spacing.m) {
                    Text("🎭")
                        .font(.system(size: 32))
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(localizationManager.localized("protection_antifake_card_title"))
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                            .accessibilityAddTraits(.isHeader)
                        AntifakeQuickAccessCopyLines()
                            .environmentObject(localizationManager)
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
            .accessibilityIdentifier("antifake_quick_access_card")
            .accessibilityLabel(AntifakeQuickAccessCopy.accessibilityLabel(localizationManager: localizationManager))
            .accessibilityHint(localizationManager.localized("protection_open_check_button"))

            Button {
                showAppleLimits = true
            } label: {
                Label(localizationManager.localized("antifake_how_it_works"), systemImage: "info.circle")
                    .font(.caption.weight(.medium))
                    .foregroundColor(.primaryBlue)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("antifake_apple_limits_link")
        }
        .sheet(isPresented: $showAppleLimits) {
            AntifakeAppleLimitsSheet()
                .environmentObject(localizationManager)
        }
    }

    private func openHub() {
        HapticFeedback.selection()
        AntifakeAccessPolicy.openHubOrPaywall(using: navigationManager)
    }
}

// MARK: - Apple limits (af-8-07)

struct AntifakeAppleLimitsSheet: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .shield)
                ScrollView {
                    VStack(alignment: .leading, spacing: Spacing.l) {
                        Text(localizationManager.localized("antifake_apple_limits_intro"))
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))

                        limitsSection(
                            titleKey: "antifake_apple_limits_can_title",
                            bulletKeys: [
                                "antifake_apple_limits_can_1",
                                "antifake_apple_limits_can_2",
                                "antifake_apple_limits_can_3",
                                "antifake_apple_limits_can_4",
                                "antifake_apple_limits_can_5"
                            ],
                            accent: .successGreen
                        )

                        limitsSection(
                            titleKey: "antifake_apple_limits_cannot_title",
                            bulletKeys: [
                                "antifake_apple_limits_cannot_1",
                                "antifake_apple_limits_cannot_2",
                                "antifake_apple_limits_cannot_3",
                                "antifake_apple_limits_cannot_4",
                                "antifake_apple_limits_cannot_5"
                            ],
                            accent: .warningOrange
                        )

                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("antifake_apple_limits_calls_title"))
                                .font(.headline)
                                .foregroundColor(.white)
                            Text(localizationManager.localized("antifake_apple_limits_calls_body"))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.88))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(Spacing.m)
                        .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .primaryBlue)

                        Text(localizationManager.localized("antifake_apple_limits_disclaimer"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.75))

                        limitsSection(
                            titleKey: "antifake_family_faq_title",
                            bulletKeys: [
                                "antifake_family_faq_1",
                                "antifake_family_faq_2",
                                "antifake_family_faq_3",
                                "antifake_family_faq_4"
                            ],
                            accent: .secondaryGold
                        )
                    }
                    .padding(Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .navigationTitle(localizationManager.localized("antifake_apple_limits_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(localizationManager.localized("antifake_close")) {
                        dismiss()
                    }
                }
            }
        }
        .navigationViewStyle(.stack)
        .accessibilityIdentifier("antifake_apple_limits_sheet")
    }

    private func limitsSection(titleKey: String, bulletKeys: [String], accent: Color) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized(titleKey))
                .font(.headline)
                .foregroundColor(.white)
            ForEach(bulletKeys, id: \.self) { key in
                HStack(alignment: .top, spacing: Spacing.xs) {
                    Circle()
                        .fill(accent)
                        .frame(width: 6, height: 6)
                        .padding(.top, 6)
                    Text(localizationManager.localized(key))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.88))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: accent)
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
