import SwiftUI

/// ⚙️ Экран детальных настроек сетевой безопасности
/// Использует NetworkSecuritySettingsViewModel с draft/save/rollback паттерном
struct NetworkSecuritySettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var syncEngine = SyncEngine.shared
    @StateObject private var viewModel = NetworkSecuritySettingsViewModel()

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
                    title: localizationManager.localized("threat_category_network_security"),
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
                            Text(localizationManager.localized("network_security.settings"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            ToggleRow(
                                title: localizationManager.localized("network_security.block_unsafe_networks"),
                                isOn: Binding(
                                    get: { viewModel.state.blockUnsafeNetworks },
                                    set: { viewModel.handleChange(\.blockUnsafeNetworks, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("network_security.warn_public_wifi"),
                                isOn: Binding(
                                    get: { viewModel.state.warnOnPublicWiFi },
                                    set: { viewModel.handleChange(\.warnOnPublicWiFi, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("network_security.auto_connect_vpn"),
                                isOn: Binding(
                                    get: { viewModel.state.autoConnectVPN },
                                    set: { viewModel.handleChange(\.autoConnectVPN, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("network_security.block_tracking"),
                                isOn: Binding(
                                    get: { viewModel.state.blockTracking },
                                    set: { viewModel.handleChange(\.blockTracking, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("network_security.encrypt_traffic"),
                                isOn: Binding(
                                    get: { viewModel.state.encryptTraffic },
                                    set: { viewModel.handleChange(\.encryptTraffic, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("network_security.firewall_enabled"),
                                isOn: Binding(
                                    get: { viewModel.state.firewallEnabled },
                                    set: { viewModel.handleChange(\.firewallEnabled, newValue: $0) }
                                )
                            )
                        }

                        // Кнопка проверки сети
                        PrimaryButton(
                            title: localizationManager.localized("network_security.network_scan"),
                            icon: "wifi",
                            isLoading: false
                        ) {
                            // TODO: Запустить сканирование сети
                            print("🛡️ Запуск сканирования сети...")
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
        .id("network_security_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct NetworkSecuritySettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NetworkSecuritySettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


