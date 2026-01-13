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
    
    @State private var passwordLength: Double = 16
    @State private var includeUppercase: Bool = true
    @State private var includeLowercase: Bool = true
    @State private var includeNumbers: Bool = true
    @State private var includeSpecial: Bool = true
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
                        
                        Slider(value: $passwordLength, in: 8...64, step: 1)
                            .tint(.blue)
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
                        
                        ToggleRow(
                            title: localizationManager.localized("password_generator.lowercase"),
                            isOn: $includeLowercase
                        )
                        
                        ToggleRow(
                            title: localizationManager.localized("password_generator.numbers"),
                            isOn: $includeNumbers
                        )
                        
                        ToggleRow(
                            title: localizationManager.localized("password_generator.special"),
                            isOn: $includeSpecial
                        )
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
            loadSettings()
        }
    }
    
    private var canGenerate: Bool {
        includeUppercase || includeLowercase || includeNumbers || includeSpecial
    }
    
    private func generatePassword() {
        isGenerating = true
        
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
        }
    }
    
    // ✅ Загрузка настроек при открытии
    private func loadSettings() {
        isLoading = true
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    if let value = settings["passwordLength"]?.value as? Int {
                        passwordLength = Double(value)
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
            } catch {
                print("⚠️ PasswordGeneratorModal: Ошибка загрузки настроек: \(error)")
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
                        "passwordLength": AnyCodable(Int(passwordLength)),
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
            } catch {
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isPresented = false
                }
            }
        }
    }
}


