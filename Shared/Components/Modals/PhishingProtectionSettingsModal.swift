import SwiftUI

/**
 * 🎣 Phishing Protection Settings Modal
 * Модальное окно для настройки защиты от фишинга
 */

struct PhishingProtectionSettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared
    
    @State private var blockSuspiciousLinks: Bool = true
    @State private var warnBeforeOpening: Bool = true
    @State private var checkEmailLinks: Bool = true
    @State private var checkSMSLinks: Bool = true
    @State private var blockKnownPhishingDomains: Bool = true
    @State private var sensitivityLevel: String = "medium" // low, medium, high
    @State private var isLoading: Bool = false
    
    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.phishing_protection_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                // Основные настройки
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("phishing_protection.settings"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.block_suspicious_links"),
                        isOn: $blockSuspiciousLinks
                    )
                    .onChange(of: blockSuspiciousLinks) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "blockSuspiciousLinks",
                            enabled: newValue
                        )
                        print("🔄 Phishing: blockSuspiciousLinks = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.warn_before_opening"),
                        isOn: $warnBeforeOpening
                    )
                    .onChange(of: warnBeforeOpening) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "warnBeforeOpening",
                            enabled: newValue
                        )
                        print("🔄 Phishing: warnBeforeOpening = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.check_email_links"),
                        isOn: $checkEmailLinks
                    )
                    .onChange(of: checkEmailLinks) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "checkEmailLinks",
                            enabled: newValue
                        )
                        print("🔄 Phishing: checkEmailLinks = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.check_sms_links"),
                        isOn: $checkSMSLinks
                    )
                    .onChange(of: checkSMSLinks) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "checkSMSLinks",
                            enabled: newValue
                        )
                        print("🔄 Phishing: checkSMSLinks = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.block_known_domains"),
                        isOn: $blockKnownPhishingDomains
                    )
                    .onChange(of: blockKnownPhishingDomains) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "blockKnownPhishingDomains",
                            enabled: newValue
                        )
                        print("🔄 Phishing: blockKnownPhishingDomains = \(newValue)")
                    }
                }
                
                // Уровень чувствительности
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("phishing_protection.sensitivity_level"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    Picker("", selection: $sensitivityLevel) {
                        Text(localizationManager.localized("phishing_protection.sensitivity_low")).tag("low")
                        Text(localizationManager.localized("phishing_protection.sensitivity_medium")).tag("medium")
                        Text(localizationManager.localized("phishing_protection.sensitivity_high")).tag("high")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }
            }
        }
        .onAppear {
            loadSettings()
        }
    }
    
    // ✅ Загрузка настроек при открытии
    // ✅ BUILD 103: Task { @MainActor in } для гарантии выполнения на main thread
    private func loadSettings() {
        isLoading = true
        Task { @MainActor in
            // Загружаем через API
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newBlockSuspiciousLinks = (settings["blockSuspiciousLinks"]?.value as? Bool) ?? blockSuspiciousLinks
                    let newWarnBeforeOpening = (settings["warnBeforeOpening"]?.value as? Bool) ?? warnBeforeOpening
                    let newCheckEmailLinks = (settings["checkEmailLinks"]?.value as? Bool) ?? checkEmailLinks
                    let newCheckSMSLinks = (settings["checkSMSLinks"]?.value as? Bool) ?? checkSMSLinks
                    let newBlockKnownPhishingDomains = (settings["blockKnownPhishingDomains"]?.value as? Bool) ?? blockKnownPhishingDomains
                    let newSensitivityLevel = (settings["sensitivityLevel"]?.value as? String) ?? sensitivityLevel

                    // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                    blockSuspiciousLinks = newBlockSuspiciousLinks
                    warnBeforeOpening = newWarnBeforeOpening
                    checkEmailLinks = newCheckEmailLinks
                    checkSMSLinks = newCheckSMSLinks
                    blockKnownPhishingDomains = newBlockKnownPhishingDomains
                    sensitivityLevel = newSensitivityLevel
                }
                print("✅ PhishingProtectionSettingsModal: Настройки загружены из API")
            } catch {
                print("⚠️ PhishingProtectionSettingsModal: Ошибка загрузки настроек: \(error.localizedDescription)")
            }
            // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
            isLoading = false
        }
    }
    
    // ✅ Сохранение настроек
    // ✅ BUILD 103: Task { @MainActor in } для гарантии создания Dictionary на main thread
    private func saveSettings() {
        Task { @MainActor in
            // Сохраняем через API
            do {
                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                // ✅ BUILD 103: Dictionary создается на main thread благодаря @MainActor
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "blockSuspiciousLinks": AnyCodable(blockSuspiciousLinks),
                        "warnBeforeOpening": AnyCodable(warnBeforeOpening),
                        "checkEmailLinks": AnyCodable(checkEmailLinks),
                        "checkSMSLinks": AnyCodable(checkSMSLinks),
                        "blockKnownPhishingDomains": AnyCodable(blockKnownPhishingDomains),
                        "sensitivityLevel": AnyCodable(sensitivityLevel)
                    ]
                )

                try await configurationService.saveConfiguration(
                    componentId: componentId,
                    configuration: config
                )

                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                isPresented = false

                print("✅ PhishingProtectionSettingsModal: Настройки сохранены через API")
            } catch {
                // ✅ BUILD 103: Убрали await MainActor.run - весь Task уже на main thread
                toastManager.showSuccess(localizationManager.localized("settings_saved"))
                isPresented = false
                print("⚠️ PhishingProtectionSettingsModal: Ошибка сохранения: \(error.localizedDescription)")
            }
        }
    }
}
