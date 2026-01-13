import SwiftUI

/**
 * 📱 Mobile Security Settings Modal
 * Модальное окно для настройки мобильной безопасности
 */

struct MobileSecuritySettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var deviceEncryption: Bool = true
    @State private var appLock: Bool = true
    @State private var screenLock: Bool = true
    @State private var biometricAuth: Bool = true
    @State private var remoteWipe: Bool = false
    @State private var trackDevice: Bool = true
    
    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.mobile_security_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                // Основные настройки
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("mobile_security.settings"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.device_encryption"),
                        isOn: $deviceEncryption
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.app_lock"),
                        isOn: $appLock
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.screen_lock"),
                        isOn: $screenLock
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.biometric_auth"),
                        isOn: $biometricAuth
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.remote_wipe"),
                        isOn: $remoteWipe
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("mobile_security.track_device"),
                        isOn: $trackDevice
                    )
                }
            }
        }
    }
    
    private func saveSettings() {
        // TODO: Сохранить настройки через ComponentConfigurationService
        print("💾 Сохранение настроек мобильной безопасности: \(componentId)")
    }
}

