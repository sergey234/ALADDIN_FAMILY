import SwiftUI

/**
 * 🌐 Network Security Settings Modal
 * Модальное окно для настройки сетевой безопасности
 */

struct NetworkSecuritySettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var blockUnsafeNetworks: Bool = true
    @State private var warnOnPublicWiFi: Bool = true
    @State private var autoConnectVPN: Bool = false
    @State private var blockTracking: Bool = true
    @State private var encryptTraffic: Bool = true
    @State private var firewallEnabled: Bool = true
    
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
    }
    
    private func saveSettings() {
        // TODO: Сохранить настройки через ComponentConfigurationService
        print("💾 Сохранение настроек сетевой безопасности: \(componentId)")
    }
}

