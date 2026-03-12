import SwiftUI

/**
 * 🌐 Network Security Settings Modal
 * Модальное окно для настройки сетевой безопасности
 */

struct NetworkSecuritySettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared
    
    @State private var blockUnsafeNetworks: Bool = true
    @State private var warnOnPublicWiFi: Bool = true
    @State private var autoConnectVPN: Bool = false
    @State private var blockTracking: Bool = true
    @State private var encryptTraffic: Bool = true
    @State private var firewallEnabled: Bool = true
    @State private var isLoading: Bool = false
    
    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.network_security_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                // Основные настройки
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("network_security.settings"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.block_unsafe_networks"),
                        isOn: $blockUnsafeNetworks
                    )
                    .onChange(of: blockUnsafeNetworks) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "blockUnsafeNetworks",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: blockUnsafeNetworks = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("network_security.warn_on_public_wifi"),
                        isOn: $warnOnPublicWiFi
                    )
                    .onChange(of: warnOnPublicWiFi) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "warnOnPublicWiFi",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: warnOnPublicWiFi = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("network_security.auto_connect_vpn"),
                        isOn: $autoConnectVPN
                    )
                    .onChange(of: autoConnectVPN) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "autoConnectVPN",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: autoConnectVPN = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("network_security.block_tracking"),
                        isOn: $blockTracking
                    )
                    .onChange(of: blockTracking) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "blockTracking",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: blockTracking = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("network_security.encrypt_traffic"),
                        isOn: $encryptTraffic
                    )
                    .onChange(of: encryptTraffic) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "encryptTraffic",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: encryptTraffic = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("network_security.firewall_enabled"),
                        isOn: $firewallEnabled
                    )
                    .onChange(of: firewallEnabled) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "firewallEnabled",
                                enabled: newValue
                            )
                        }
                        print("🔄 Network: firewallEnabled = \(newValue)")
                    }
                }
            }
        }
        .onAppear {
            loadSettings()
        }
    }
    
    // ✅ Загрузка настроек при открытии через API
    // ✅ BUILD 103: Task { @MainActor in } для гарантии выполнения на main thread
    private func loadSettings() {
        isLoading = true
        Task { @MainActor in
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newBlockUnsafeNetworks = (settings["blockUnsafeNetworks"]?.value as? Bool) ?? blockUnsafeNetworks
                    let newWarnOnPublicWiFi = (settings["warnOnPublicWiFi"]?.value as? Bool) ?? warnOnPublicWiFi
                    let newAutoConnectVPN = (settings["autoConnectVPN"]?.value as? Bool) ?? autoConnectVPN
                    let newBlockTracking = (settings["blockTracking"]?.value as? Bool) ?? blockTracking
                    let newEncryptTraffic = (settings["encryptTraffic"]?.value as? Bool) ?? encryptTraffic
                    let newFirewallEnabled = (settings["firewallEnabled"]?.value as? Bool) ?? firewallEnabled

                    // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                    blockUnsafeNetworks = newBlockUnsafeNetworks
                    warnOnPublicWiFi = newWarnOnPublicWiFi
                    autoConnectVPN = newAutoConnectVPN
                    blockTracking = newBlockTracking
                    encryptTraffic = newEncryptTraffic
                    firewallEnabled = newFirewallEnabled

                    print("✅ NetworkSecuritySettingsModal: Настройки загружены из API")
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                print("⚠️ NetworkSecuritySettingsModal: Настройки не найдены (404), используются дефолты: \(error.localizedDescription)")
            }
            // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
            isLoading = false
        }
    }
    
    // ✅ Сохранение настроек через ComponentConfigurationService
    // ✅ BUILD 114: Асинхронное сохранение, закрываем окно СРАЗУ
    private func saveSettings() {
        // Сначала закрываем окно для отзывчивости UI
        isPresented = false
        
        // Затем выполняем сохранение асинхронно
        Task { @MainActor in
            do {
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "blockUnsafeNetworks": AnyCodable(blockUnsafeNetworks),
                        "warnOnPublicWiFi": AnyCodable(warnOnPublicWiFi),
                        "autoConnectVPN": AnyCodable(autoConnectVPN),
                        "blockTracking": AnyCodable(blockTracking),
                        "encryptTraffic": AnyCodable(encryptTraffic),
                        "firewallEnabled": AnyCodable(firewallEnabled)
                    ]
                )

                try await configurationService.saveConfiguration(
                    componentId: componentId,
                    configuration: config
                )

                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                print("✅ NetworkSecuritySettingsModal: Настройки сохранены через API")
            } catch {
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                print("⚠️ NetworkSecuritySettingsModal: Ошибка сохранения, но кэшировано: \(error.localizedDescription)")
            }
        }
    }
}

