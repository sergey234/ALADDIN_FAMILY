import SwiftUI

/**
 * 🎤 Voice Control View
 * Экран настройки голосового управления
 * Компонент: voice_control_manager
 */

struct VoiceControlView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var configurationService = ComponentConfigurationService.shared
    @StateObject private var toastManager = ToastManager.shared
    
    @State private var activationWord: String = "Аладдин"
    @State private var selectedLanguage: String = "ru"
    @State private var sensitivity: Double = 0.5
    @State private var isOnlineMode: Bool = true
    
    let activationWords = ["Аладдин", "Aladdin", "Защита", "Protection"]
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("component_voice_control_manager_title"),
                    subtitle: localizationManager.localized("component_voice_control_manager_description"),
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Activation Word
                        activationWordSection
                        
                        // Language
                        languageSection
                        
                        // Sensitivity
                        sensitivitySection
                        
                        // Mode
                        modeSection
                        
                        // Save Button
                        saveButton
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Sections
    
    private var activationWordSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("voice_control_activation_title"))
                .font(.h4)
                .foregroundColor(.textPrimary)
            
            Picker(
                localizationManager.localized("voice_control_activation_word"),
                selection: $activationWord
            ) {
                ForEach(activationWords, id: \.self) { word in
                    Text(word).tag(word)
                }
            }
            .pickerStyle(.menu)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var languageSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("voice_control_language_title"))
                .font(.h4)
                .foregroundColor(.textPrimary)
            
            Picker(
                localizationManager.localized("voice_control_language"),
                selection: $selectedLanguage
            ) {
                Text(localizationManager.localized("language_russian")).tag("ru")
                Text(localizationManager.localized("language_english")).tag("en")
            }
            .pickerStyle(.menu)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var sensitivitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("voice_control_sensitivity_title"))
                .font(.h4)
                .foregroundColor(.textPrimary)
            
            HStack {
                Text(localizationManager.localized("voice_control_sensitivity_low"))
                Spacer()
                Text(localizationManager.localized("voice_control_sensitivity_high"))
            }
            .font(.caption)
            .foregroundColor(.textSecondary)
            
            Slider(value: $sensitivity, in: 0...1)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var modeSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("voice_control_mode_title"))
                .font(.h4)
                .foregroundColor(.textPrimary)
            
            Toggle(
                localizationManager.localized("voice_control_mode_online"),
                isOn: $isOnlineMode
            )
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var saveButton: some View {
        Button(action: saveSettings) {
            Text(localizationManager.localized("common_save"))
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primaryBlue)
                .cornerRadius(CornerRadius.medium)
        }
    }
    
    // MARK: - Methods
    
    private func saveSettings() {
        Task {
            // TODO: Сохранить настройки через API
            toastManager.showSuccess(localizationManager.localized("settings_saved"))
        }
    }
}

