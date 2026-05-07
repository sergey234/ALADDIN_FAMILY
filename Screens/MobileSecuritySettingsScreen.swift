import SwiftUI

/// ⚙️ Экран детальных настроек мобильной безопасности
/// Использует MobileSecuritySettingsViewModel с draft/save/rollback паттерном
struct MobileSecuritySettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var syncEngine = SyncEngine.shared
    @StateObject private var viewModel = MobileSecuritySettingsViewModel()

    private var syncState: SyncState {
        syncEngine.latestStateByDomain[.networkProtection] ?? .idle
    }

    private var syncStatusTitle: String {
        syncState.localizedTitle(using: localizationManager)
    }

    private var syncStatusColor: Color {
        syncState.statusColor
    }

    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()

            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("threat_category_mobile_security"),
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
                            Text(localizationManager.localized("mobile_security.settings"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.device_encryption"),
                                isOn: Binding(
                                    get: { viewModel.state.deviceEncryption },
                                    set: { viewModel.handleChange(\.deviceEncryption, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.app_lock"),
                                isOn: Binding(
                                    get: { viewModel.state.appLock },
                                    set: { viewModel.handleChange(\.appLock, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.screen_lock"),
                                isOn: Binding(
                                    get: { viewModel.state.screenLock },
                                    set: { viewModel.handleChange(\.screenLock, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.biometric_auth"),
                                isOn: Binding(
                                    get: { viewModel.state.biometricAuth },
                                    set: { viewModel.handleChange(\.biometricAuth, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.remote_wipe"),
                                isOn: Binding(
                                    get: { viewModel.state.remoteWipe },
                                    set: { viewModel.handleChange(\.remoteWipe, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("mobile_security.track_device"),
                                isOn: Binding(
                                    get: { viewModel.state.trackDevice },
                                    set: { viewModel.handleChange(\.trackDevice, newValue: $0) }
                                )
                            )
                        }

                        // Кнопка проверки безопасности
                        PrimaryButton(
                            title: localizationManager.localized("mobile_security.security_check"),
                            icon: "checkmark.shield",
                            isLoading: false
                        ) {
                            // TODO: Запустить проверку безопасности устройства
                            print("🔐 Запуск проверки безопасности устройства...")
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
        .id("mobile_security_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct MobileSecuritySettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        MobileSecuritySettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


