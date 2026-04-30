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
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "deviceEncryption",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 deviceEncryption = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.app_lock"),
                        isOn: $appLock
                    )
                    .onChange(of: appLock) { newValue in
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "appLock",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 appLock = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.screen_lock"),
                        isOn: $screenLock
                    )
                    .onChange(of: screenLock) { newValue in
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "screenLock",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 screenLock = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.biometric_auth"),
                        isOn: $biometricAuth
                    )
                    .onChange(of: biometricAuth) { newValue in
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "biometricAuth",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 biometricAuth = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.remote_wipe"),
                        isOn: $remoteWipe
                    )
                    .onChange(of: remoteWipe) { newValue in
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "remoteWipe",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 remoteWipe = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("mobile_security.track_device"),
                        isOn: $trackDevice
                    )
                    .onChange(of: trackDevice) { newValue in
                        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_change_pending", state: .pending)
                        DispatchQueue.main.async { [componentAnalytics, componentId] in
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "trackDevice",
                                enabled: newValue
                            )
                        }
                        vLog("🔄 trackDevice = \(newValue)")
                    }
                }
            }
        }
        .onAppear {
            vLog("🛠️ Open settings modal")
            loadSettings()
        }
        .withVisualLogger()
    }
    
    // ✅ Загрузка настроек при открытии через API
    // ✅ BUILD 103: Task { @MainActor in } для гарантии выполнения на main thread
    private func loadSettings() {
        isLoading = true
        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_load_start", state: .syncing)
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

                    vLog("✅ Settings loaded from API", level: .success)
                    SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_load_complete", state: .synced)
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                vLog("⚠️ Load failed, defaults are used: \(error.localizedDescription)", level: .warning)
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_load_local", state: .local)
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
        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_save_start", state: .syncing)
        vLog("💾 Save requested")
        
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
                vLog("✅ Settings saved via API", level: .success)
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_save_complete", state: .synced)
            } catch {
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                vLog("⚠️ Save failed, local cache kept: \(error.localizedDescription)", level: .warning)
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_modal_save_error", state: .error(error.localizedDescription))
            }
        }
    }

    private func vLog(_ message: String, level: VisualLogger.LogLevel = .info) {
        VisualLogger.shared.log(
            message,
            level: level,
            category: "GEAR.\(componentId)"
        )
    }
}

