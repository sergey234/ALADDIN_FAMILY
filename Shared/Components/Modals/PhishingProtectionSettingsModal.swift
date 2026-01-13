import SwiftUI

/**
 * 🎣 Phishing Protection Settings Modal
 * Модальное окно для настройки защиты от фишинга
 */

struct PhishingProtectionSettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var blockSuspiciousLinks: Bool = true
    @State private var warnBeforeOpening: Bool = true
    @State private var checkEmailLinks: Bool = true
    @State private var checkSMSLinks: Bool = true
    @State private var blockKnownPhishingDomains: Bool = true
    @State private var sensitivityLevel: String = "medium" // low, medium, high
    
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
    }
    
    private func saveSettings() {
        // TODO: Сохранить настройки через ComponentConfigurationService
        print("💾 Сохранение настроек защиты от фишинга: \(componentId)")
    }
}

