import SwiftUI

/**
 * 📱 Mobile Security Settings Modal
 * Модальное окно для настройки мобильной безопасности
 */

struct MobileSecuritySettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    
    @State private var deviceEncryption: Bool = true
    @State private var appLock: Bool = true
    @State private var screenLock: Bool = true
    @State private var biometricAuth: Bool = true
    @State private var remoteWipe: Bool = false
    @State private var trackDevice: Bool = true
    @State private var isLoading: Bool = false
    
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
                    let newDeviceEncryption = (settings["deviceEncryption"]?.value as? Bool) ?? deviceEncryption
                    let newAppLock = (settings["appLock"]?.value as? Bool) ?? appLock
                    let newScreenLock = (settings["screenLock"]?.value as? Bool) ?? screenLock
                    let newBiometricAuth = (settings["biometricAuth"]?.value as? Bool) ?? biometricAuth
                    let newRemoteWipe = (settings["remoteWipe"]?.value as? Bool) ?? remoteWipe
                    let newTrackDevice = (settings["trackDevice"]?.value as? Bool) ?? trackDevice

                    await MainActor.run {
                        deviceEncryption = newDeviceEncryption
                        appLock = newAppLock
                        screenLock = newScreenLock
                        biometricAuth = newBiometricAuth
                        remoteWipe = newRemoteWipe
                        trackDevice = newTrackDevice
                    }
                }
            } catch {
                print("⚠️ MobileSecuritySettingsModal: Ошибка загрузки настроек: \(error)")
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
                        "deviceEncryption": AnyCodable(deviceEncryption),
                        "appLock": AnyCodable(appLock),
                        "screenLock": AnyCodable(screenLock),
                        "biometricAuth": AnyCodable(biometricAuth),
                        "remoteWipe": AnyCodable(remoteWipe),
                        "trackDevice": AnyCodable(trackDevice)
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

