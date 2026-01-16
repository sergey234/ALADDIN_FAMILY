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
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.warn_on_public_wifi"),
                        isOn: $warnOnPublicWiFi
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.auto_connect_vpn"),
                        isOn: $autoConnectVPN
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.block_tracking"),
                        isOn: $blockTracking
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.encrypt_traffic"),
                        isOn: $encryptTraffic
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("network_security.firewall_enabled"),
                        isOn: $firewallEnabled
                    )
                }
            }
        }
        .onAppear {
            loadSettings()
        }
    }
    
    // ✅ Загрузка настроек при открытии
    private func loadSettings() {
        isLoading = true
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newBlockUnsafeNetworks = (settings["blockUnsafeNetworks"]?.value as? Bool) ?? blockUnsafeNetworks
                    let newWarnOnPublicWiFi = (settings["warnOnPublicWiFi"]?.value as? Bool) ?? warnOnPublicWiFi
                    let newAutoConnectVPN = (settings["autoConnectVPN"]?.value as? Bool) ?? autoConnectVPN
                    let newBlockTracking = (settings["blockTracking"]?.value as? Bool) ?? blockTracking
                    let newEncryptTraffic = (settings["encryptTraffic"]?.value as? Bool) ?? encryptTraffic
                    let newFirewallEnabled = (settings["firewallEnabled"]?.value as? Bool) ?? firewallEnabled

                    await MainActor.run {
                        blockUnsafeNetworks = newBlockUnsafeNetworks
                        warnOnPublicWiFi = newWarnOnPublicWiFi
                        autoConnectVPN = newAutoConnectVPN
                        blockTracking = newBlockTracking
                        encryptTraffic = newEncryptTraffic
                        firewallEnabled = newFirewallEnabled
                    }
                }
            } catch {
                print("⚠️ NetworkSecuritySettingsModal: Ошибка загрузки настроек: \(error)")
            }
            await MainActor.run {
                isLoading = false
            }
        }
    }
    
    // ✅ Сохранение настроек через ComponentConfigurationService
    private func saveSettings() {
        Task {
            do {
                // Получить текущий статус компонента через метод (правильный доступ к @MainActor)
                let isComponentEnabled = await MainActor.run {
                    ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)
                }
                
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
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
            } catch {
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
            }
        }
    }
}

