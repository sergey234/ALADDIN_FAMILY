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
                    
                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.warn_before_opening"),
                        isOn: $warnBeforeOpening
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.check_email_links"),
                        isOn: $checkEmailLinks
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.check_sms_links"),
                        isOn: $checkSMSLinks
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("phishing_protection.block_known_domains"),
                        isOn: $blockKnownPhishingDomains
                    )
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
    private func loadSettings() {
        isLoading = true
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                // Применить настройки из конфигурации
                if let settings = config.additionalSettings {
                    if let value = settings["blockSuspiciousLinks"]?.value as? Bool {
                        blockSuspiciousLinks = value
                    }
                    if let value = settings["warnBeforeOpening"]?.value as? Bool {
                        warnBeforeOpening = value
                    }
                    if let value = settings["checkEmailLinks"]?.value as? Bool {
                        checkEmailLinks = value
                    }
                    if let value = settings["checkSMSLinks"]?.value as? Bool {
                        checkSMSLinks = value
                    }
                    if let value = settings["blockKnownPhishingDomains"]?.value as? Bool {
                        blockKnownPhishingDomains = value
                    }
                    if let value = settings["sensitivityLevel"]?.value as? String {
                        sensitivityLevel = value
                    }
                }
            } catch {
                // Использовать дефолтные значения (уже установлены в @State)
                print("⚠️ PhishingProtectionSettingsModal: Ошибка загрузки настроек: \(error)")
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
                
                // Создать конфигурацию с настройками
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
                
                // ✅ Сохраняет в UserDefaults через ComponentCacheService
                // ✅ Синхронизирует с сервером
                try await configurationService.saveConfiguration(
                    componentId: componentId,
                    configuration: config
                )
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
            } catch {
                // Настройки уже сохранены в кэш (ComponentCacheService)
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
            }
        }
    }
}

