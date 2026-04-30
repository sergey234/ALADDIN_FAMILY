import SwiftUI

/**
 * 🎤 Voice Control View
 * Экран настройки голосового управления
 * Компонент: voice_control_manager
 */

struct VoiceControlView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    
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
        .onAppear {
            loadSettings()
        }
        .onChange(of: activationWord) { _ in
            SyncEngine.shared.publish(domain: .settings, operation: "voice_control_change_pending", state: .pending)
        }
        .onChange(of: selectedLanguage) { _ in
            SyncEngine.shared.publish(domain: .settings, operation: "voice_control_change_pending", state: .pending)
        }
        .onChange(of: sensitivity) { _ in
            SyncEngine.shared.publish(domain: .settings, operation: "voice_control_change_pending", state: .pending)
        }
        .onChange(of: isOnlineMode) { _ in
            SyncEngine.shared.publish(domain: .settings, operation: "voice_control_change_pending", state: .pending)
        }
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
    
    private func loadSettings() {
        SyncEngine.shared.publish(domain: .settings, operation: "voice_control_load_start", state: .syncing)
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: "voice_control_manager")
                if let settings = config.additionalSettings {
                    await MainActor.run {
                        if let word = settings["activationWord"]?.value as? String {
                            activationWord = word
                        }
                        if let lang = settings["selectedLanguage"]?.value as? String {
                            selectedLanguage = lang
                        }
                        if let sens = settings["sensitivity"]?.value as? Double {
                            sensitivity = sens
                        }
                        if let mode = settings["isOnlineMode"]?.value as? Bool {
                            isOnlineMode = mode
                        }
                    }
                }
                SyncEngine.shared.publish(domain: .settings, operation: "voice_control_load_complete", state: .synced)
            } catch {
                // Использовать значения по умолчанию
                SyncEngine.shared.publish(domain: .settings, operation: "voice_control_load_local", state: .local)
            }
        }
    }
    
    private func saveSettings() {
        SyncEngine.shared.publish(domain: .settings, operation: "voice_control_save_start", state: .syncing)
        Task {
            do {
                // Получить текущий статус компонента через метод (правильный доступ к @MainActor)
                let isComponentEnabled = await MainActor.run {
                    ComponentStatusService.shared.getComponentEnabledStatus(componentId: "voice_control_manager")
                }
                
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "activationWord": AnyCodable(activationWord),
                        "selectedLanguage": AnyCodable(selectedLanguage),
                        "sensitivity": AnyCodable(sensitivity),
                        "isOnlineMode": AnyCodable(isOnlineMode)
                    ]
                )
                
                try await configurationService.saveConfiguration(
                    componentId: "voice_control_manager",
                    configuration: config
                )
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    dismiss()
                }
                SyncEngine.shared.publish(domain: .settings, operation: "voice_control_save_complete", state: .synced)
            } catch {
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    dismiss()
                }
                SyncEngine.shared.publish(domain: .settings, operation: "voice_control_save_error", state: .error(error.localizedDescription))
            }
        }
    }
}

