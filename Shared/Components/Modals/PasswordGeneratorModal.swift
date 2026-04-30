import SwiftUI

/**
 * 🔐 Password Generator Modal
 * Модальное окно для генерации безопасных паролей
 */

struct PasswordGeneratorModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared
    
    // ✅ ИСПРАВЛЕНО: Заменено @State на @AppStorage для сохранения между сессиями
    @AppStorage("password_generator_length") private var passwordLengthInt: Int = 16
    private var passwordLength: Double {
        get { Double(passwordLengthInt) }
        set { passwordLengthInt = Int(newValue) }
    }
    
    @AppStorage("password_generator_uppercase") private var includeUppercase: Bool = true
    @AppStorage("password_generator_lowercase") private var includeLowercase: Bool = true
    @AppStorage("password_generator_numbers") private var includeNumbers: Bool = true
    @AppStorage("password_generator_special") private var includeSpecial: Bool = true
    
    @State private var generatedPassword: String = ""
    @State private var isGenerating: Bool = false
    @State private var isLoading: Bool = false
    
    init(componentId: String = "password_security_agent", isPresented: Binding<Bool>) {
        self.componentId = componentId
        self._isPresented = isPresented
    }
    
    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.password_security_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                // Настройки генератора
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("password_generator.settings"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    // Длина пароля
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(localizationManager.localized("password_generator.length"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(Int(passwordLength))")
                                .font(.headline)
                                .foregroundColor(.textPrimary)
                        }
                        
                        Slider(value: Binding(
                            get: { passwordLength },
                            set: { passwordLengthInt = Int($0) }
                        ), in: 8...64, step: 1)
                            .tint(.blue)
                            .onChange(of: passwordLengthInt) { newValue in
                                SyncEngine.shared.publish(domain: .settings, operation: "password_modal_change_pending", state: .pending)
                                componentAnalytics.trackSettingToggle(
                                    componentId: componentId,
                                    settingKey: "passwordLength",
                                    enabled: true // Для слайдера всегда true, значение в метаданных
                                )
                                vLog("🔄 passwordLength = \(newValue)")
                            }
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                    
                    // Типы символов
                    VStack(spacing: Spacing.s) {
                        ToggleRow(
                            title: localizationManager.localized("password_generator.uppercase"),
                            isOn: $includeUppercase
                        )
                        .onChange(of: includeUppercase) { newValue in
                            SyncEngine.shared.publish(domain: .settings, operation: "password_modal_change_pending", state: .pending)
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "includeUppercase",
                                enabled: newValue
                            )
                            vLog("🔄 includeUppercase = \(newValue)")
                        }

                        ToggleRow(
                            title: localizationManager.localized("password_generator.lowercase"),
                            isOn: $includeLowercase
                        )
                        .onChange(of: includeLowercase) { newValue in
                            SyncEngine.shared.publish(domain: .settings, operation: "password_modal_change_pending", state: .pending)
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "includeLowercase",
                                enabled: newValue
                            )
                            vLog("🔄 includeLowercase = \(newValue)")
                        }

                        ToggleRow(
                            title: localizationManager.localized("password_generator.numbers"),
                            isOn: $includeNumbers
                        )
                        .onChange(of: includeNumbers) { newValue in
                            SyncEngine.shared.publish(domain: .settings, operation: "password_modal_change_pending", state: .pending)
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "includeNumbers",
                                enabled: newValue
                            )
                            vLog("🔄 includeNumbers = \(newValue)")
                        }

                        ToggleRow(
                            title: localizationManager.localized("password_generator.special"),
                            isOn: $includeSpecial
                        )
                        .onChange(of: includeSpecial) { newValue in
                            SyncEngine.shared.publish(domain: .settings, operation: "password_modal_change_pending", state: .pending)
                            componentAnalytics.trackSettingToggle(
                                componentId: componentId,
                                settingKey: "includeSpecial",
                                enabled: newValue
                            )
                            vLog("🔄 includeSpecial = \(newValue)")
                        }
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                
                // Сгенерированный пароль
                if !generatedPassword.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("password_generator.generated"))
                            .font(.h4)
                            .foregroundColor(.textPrimary)
                        
                        HStack {
                            Text(generatedPassword)
                                .font(.system(.body, design: .monospaced))
                                .foregroundColor(.textPrimary)
                                .padding(Spacing.m)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                            
                            Button(action: {
                                UIPasteboard.general.string = generatedPassword
                                HapticFeedback.notification(.success)
                            }) {
                                Image(systemName: "doc.on.doc")
                                    .font(.title3)
                                    .foregroundColor(.blue)
                            }
                            .accessibilityLabel("Copy password")
                        }
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                
                // Кнопка генерации
                Button(action: {
                    generatePassword()
                }) {
                    HStack {
                        if isGenerating {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "key.fill")
                                .font(.title3)
                        }
                        
                        Text(localizationManager.localized("password_generator.generate"))
                            .font(.headline)
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(canGenerate ? Color.blue : Color.gray)
                    )
                }
                .disabled(!canGenerate || isGenerating)
            }
        }
        .onAppear {
            vLog("🛠️ Open settings modal")
            loadSettings()
        }
        .withVisualLogger()
    }
    
    private var canGenerate: Bool {
        includeUppercase || includeLowercase || includeNumbers || includeSpecial
    }
    
    private func generatePassword() {
        isGenerating = true
        vLog("🔐 Generate password requested")
        
        // Имитация генерации (в реальности будет API вызов)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            let uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            let lowercase = "abcdefghijklmnopqrstuvwxyz"
            let numbers = "0123456789"
            let special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            var characters = ""
            if includeUppercase { characters += uppercase }
            if includeLowercase { characters += lowercase }
            if includeNumbers { characters += numbers }
            if includeSpecial { characters += special }
            
            var password = ""
            for _ in 0..<Int(passwordLength) {
                if let char = characters.randomElement() {
                    password.append(char)
                }
            }
            
            generatedPassword = password
            isGenerating = false
            HapticFeedback.notification(.success)
            vLog("✅ Password generated with length \(password.count)", level: .success)
        }
    }
    
    // ✅ Загрузка настроек при открытии (синхронизация с ComponentConfigurationService)
    private func loadSettings() {
        isLoading = true
        SyncEngine.shared.publish(domain: .settings, operation: "password_modal_load_start", state: .syncing)
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    // Синхронизируем с @AppStorage только если значения есть в ComponentConfigurationService
                    if let value = settings["passwordLength"]?.value as? Int {
                        passwordLengthInt = value
                    }
                    if let value = settings["includeUppercase"]?.value as? Bool {
                        includeUppercase = value
                    }
                    if let value = settings["includeLowercase"]?.value as? Bool {
                        includeLowercase = value
                    }
                    if let value = settings["includeNumbers"]?.value as? Bool {
                        includeNumbers = value
                    }
                    if let value = settings["includeSpecial"]?.value as? Bool {
                        includeSpecial = value
                    }
                }
                SyncEngine.shared.publish(domain: .settings, operation: "password_modal_load_complete", state: .synced)
            } catch {
                vLog("⚠️ Load failed: \(error.localizedDescription)", level: .warning)
                SyncEngine.shared.publish(domain: .settings, operation: "password_modal_load_local", state: .local)
            }
            await MainActor.run {
                isLoading = false
            }
        }
    }
    
    // ✅ Сохранение настроек через ComponentConfigurationService
    private func saveSettings() {
        vLog("💾 Save requested")
        SyncEngine.shared.publish(domain: .settings, operation: "password_modal_save_start", state: .syncing)
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
                        "passwordLength": AnyCodable(passwordLengthInt),
                        "includeUppercase": AnyCodable(includeUppercase),
                        "includeLowercase": AnyCodable(includeLowercase),
                        "includeNumbers": AnyCodable(includeNumbers),
                        "includeSpecial": AnyCodable(includeSpecial)
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
                vLog("✅ Settings saved via API", level: .success)
                SyncEngine.shared.publish(domain: .settings, operation: "password_modal_save_complete", state: .synced)
            } catch {
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
                vLog("⚠️ Save failed, UI closed with cached values", level: .warning)
                SyncEngine.shared.publish(domain: .settings, operation: "password_modal_save_error", state: .error(error.localizedDescription))
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


