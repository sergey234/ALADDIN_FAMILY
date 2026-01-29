import SwiftUI

/// ⚙️ Экран детальных настроек защиты от фишинга
/// Использует PhishingSettingsViewModel с draft/save/rollback паттерном
struct PhishingProtectionSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = PhishingSettingsViewModel()

    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()

            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("threat_category_phishing_protection"),
                    subtitle: localizationManager.localized("settings_subtitle"),
                    showBackButton: true,
                    onBack: {
                        navigationManager.goBack()
                    }
                )

                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Основные настройки
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("phishing_protection.settings"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            ToggleRow(
                                title: localizationManager.localized("phishing_protection.block_suspicious_links"),
                                isOn: Binding(
                                    get: { viewModel.state.blockSuspiciousLinks },
                                    set: { viewModel.handleChange(\.blockSuspiciousLinks, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("phishing_protection.warn_before_opening"),
                                isOn: Binding(
                                    get: { viewModel.state.warnBeforeOpening },
                                    set: { viewModel.handleChange(\.warnBeforeOpening, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("phishing_protection.check_email_links"),
                                isOn: Binding(
                                    get: { viewModel.state.checkEmailLinks },
                                    set: { viewModel.handleChange(\.checkEmailLinks, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("phishing_protection.check_sms_links"),
                                isOn: Binding(
                                    get: { viewModel.state.checkSMSLinks },
                                    set: { viewModel.handleChange(\.checkSMSLinks, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("phishing_protection.block_known_domains"),
                                isOn: Binding(
                                    get: { viewModel.state.blockKnownPhishingDomains },
                                    set: { viewModel.handleChange(\.blockKnownPhishingDomains, newValue: $0) }
                                )
                            )
                        }

                        // Уровень чувствительности
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("phishing_protection.sensitivity_level"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            Picker("", selection: Binding(
                                get: { viewModel.state.sensitivityLevel },
                                set: { viewModel.handleSensitivityLevelChange($0) }
                            )) {
                                Text(localizationManager.localized("phishing_protection.sensitivity_low")).tag("low")
                                Text(localizationManager.localized("phishing_protection.sensitivity_medium")).tag("medium")
                                Text(localizationManager.localized("phishing_protection.sensitivity_high")).tag("high")
                            }
                            .pickerStyle(SegmentedPickerStyle())
                        }

                        // Кнопка быстрого сканирования
                        PrimaryButton(
                            title: localizationManager.localized("phishing_protection.quick_scan"),
                            icon: "magnifyingglass",
                            isLoading: false
                        ) {
                            // TODO: Интегрировать с антифишинговым сканером
                            print("🎣 Запуск быстрого сканирования на фишинг...")
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
        .onDisappear {
            viewModel.saveOnExit()
        }
        .id("phishing_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct PhishingProtectionSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        PhishingProtectionSettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


