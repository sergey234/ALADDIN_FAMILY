import SwiftUI

/**
 * 🔐 Password Generator Modal
 * Модальное окно для генерации безопасных паролей
 */

struct PasswordGeneratorModal: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var passwordLength: Double = 16
    @State private var includeUppercase: Bool = true
    @State private var includeLowercase: Bool = true
    @State private var includeNumbers: Bool = true
    @State private var includeSpecial: Bool = true
    @State private var generatedPassword: String = ""
    @State private var isGenerating: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
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
                    .padding(Spacing.m)
                }
            }
            .navigationTitle(localizationManager.localized("component.password_security_agent.title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("common.close")) {
                        dismiss()
                    }
                }
            }
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
}


