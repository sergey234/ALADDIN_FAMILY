import SwiftUI

/// ⚙️ Экран детальных настроек защиты от фишинга
/// Использует PhishingSettingsViewModel с draft/save/rollback паттерном
struct PhishingProtectionSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var syncEngine = SyncEngine.shared
    @StateObject private var viewModel = PhishingSettingsViewModel()

    private var syncState: SyncState {
        syncEngine.latestStateByDomain[.networkProtection] ?? .idle
    }

    private var syncStatusTitle: String {
        switch syncState {
        case .idle: return "Idle"
        case .local: return "Local"
        case .pending: return "Pending"
        case .syncing: return "Syncing"
        case .synced: return "Synced"
        case .conflict: return "Conflict"
        case .error: return "Error"
        }
    }

    private var syncStatusColor: Color {
        switch syncState {
        case .idle, .local: return .gray
        case .pending: return .orange
        case .syncing: return .blue
        case .synced: return .green
        case .conflict, .error: return .red
        }
    }

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

                HStack {
                    Spacer()
                    Text(syncStatusTitle)
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(syncStatusColor)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(syncStatusColor.opacity(0.15))
                        .clipShape(Capsule())
                }
                .padding(.horizontal, Spacing.screenPadding)
                .padding(.top, Spacing.xs)

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


