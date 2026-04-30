import SwiftUI

/// ⚙️ Экран детальных настроек реагирования на инциденты
/// Использует IncidentResponseSettingsViewModel с draft/save/rollback паттерном
struct IncidentResponseSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var syncEngine = SyncEngine.shared
    @StateObject private var viewModel = IncidentResponseSettingsViewModel()

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
                    title: localizationManager.localized("threat_category_incident_response"),
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
                            Text(localizationManager.localized("incident_response.settings"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            ToggleRow(
                                title: localizationManager.localized("incident_response.auto_actions"),
                                isOn: Binding(
                                    get: { viewModel.state.autoActions },
                                    set: { viewModel.handleChange(\.autoActions, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("incident_response.escalation_thresholds"),
                                isOn: Binding(
                                    get: { viewModel.state.escalationThresholds },
                                    set: { viewModel.handleChange(\.escalationThresholds, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("incident_response.contact_roles"),
                                isOn: Binding(
                                    get: { viewModel.state.contactRoles },
                                    set: { viewModel.handleChange(\.contactRoles, newValue: $0) }
                                )
                            )
                        }

                        // SLA время реагирования
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("incident_response.sla_time"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            Picker("", selection: Binding(
                                get: { viewModel.state.slaTime },
                                set: { viewModel.handleSLATimeChange($0) }
                            )) {
                                Text("1 \(localizationManager.localized("incident_response.hour"))").tag("1h")
                                Text("2 \(localizationManager.localized("incident_response.hours"))").tag("2h")
                                Text("4 \(localizationManager.localized("incident_response.hours"))").tag("4h")
                                Text("8 \(localizationManager.localized("incident_response.hours"))").tag("8h")
                                Text("24 \(localizationManager.localized("incident_response.hours"))").tag("24h")
                            }
                            .pickerStyle(SegmentedPickerStyle())
                        }

                        // Кнопка тестирования реагирования
                        PrimaryButton(
                            title: localizationManager.localized("incident_response.test_response"),
                            icon: "exclamationmark.triangle",
                            isLoading: false
                        ) {
                            // TODO: Запустить тест системы реагирования
                            print("🚨 Запуск тестирования системы реагирования...")
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
        .id("incident_response_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

#if DEBUG
struct IncidentResponseSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        IncidentResponseSettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


