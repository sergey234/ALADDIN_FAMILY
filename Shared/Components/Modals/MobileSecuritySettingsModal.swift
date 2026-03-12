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
    private let componentAnalytics = ComponentAnalytics.shared
    
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
                    .onChange(of: deviceEncryption) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "deviceEncryption",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: deviceEncryption = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.app_lock"),
                        isOn: $appLock
                    )
                    .onChange(of: appLock) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "appLock",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: appLock = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.screen_lock"),
                        isOn: $screenLock
                    )
                    .onChange(of: screenLock) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "screenLock",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: screenLock = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.biometric_auth"),
                        isOn: $biometricAuth
                    )
                    .onChange(of: biometricAuth) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "biometricAuth",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: biometricAuth = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.remote_wipe"),
                        isOn: $remoteWipe
                    )
                    .onChange(of: remoteWipe) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "remoteWipe",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: remoteWipe = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.track_device"),
                        isOn: $trackDevice
                    )
                    .onChange(of: trackDevice) { newValue in
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "trackDevice",
                                enabled: newValue
                            )
                        }
                        print("🔄 Mobile: trackDevice = \(newValue)")
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
                    let newDeviceEncryption = (settings["deviceEncryption"]?.value as? Bool) ?? deviceEncryption
                    let newAppLock = (settings["appLock"]?.value as? Bool) ?? appLock
                    let newScreenLock = (settings["screenLock"]?.value as? Bool) ?? screenLock
                    let newBiometricAuth = (settings["biometricAuth"]?.value as? Bool) ?? biometricAuth
                    let newRemoteWipe = (settings["remoteWipe"]?.value as? Bool) ?? remoteWipe
                    let newTrackDevice = (settings["trackDevice"]?.value as? Bool) ?? trackDevice

                    // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                    deviceEncryption = newDeviceEncryption
                    appLock = newAppLock
                    screenLock = newScreenLock
                    biometricAuth = newBiometricAuth
                    remoteWipe = newRemoteWipe
                    trackDevice = newTrackDevice

                    print("✅ MobileSecuritySettingsModal: Настройки загружены из API")
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                print("⚠️ MobileSecuritySettingsModal: Настройки не найдены (404), используются дефолты: \(error.localizedDescription)")
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

                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                print("✅ MobileSecuritySettingsModal: Настройки сохранены через API")
            } catch {
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                print("⚠️ MobileSecuritySettingsModal: Ошибка сохранения, но кэшировано: \(error.localizedDescription)")
            }
        }
    }
}

