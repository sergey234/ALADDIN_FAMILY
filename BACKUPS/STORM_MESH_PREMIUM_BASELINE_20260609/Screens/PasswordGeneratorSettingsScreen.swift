import SwiftUI

/// ⚙️ Экран детальных настроек генератора паролей
/// Использует PasswordGeneratorSettingsViewModel с draft/save/rollback паттерном
struct PasswordGeneratorSettingsScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = PasswordGeneratorSettingsViewModel()
    @State private var generatedPassword: String = ""

    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()

            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("threat_category_password_generator"),
                    subtitle: localizationManager.localized("settings_subtitle"),
                    showBackButton: true,
                    onBack: {
                        navigationManager.goBack()
                    }
                )

                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Основные настройки
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("password_generator.settings"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            ToggleRow(
                                title: localizationManager.localized("password_generator.include_uppercase"),
                                isOn: Binding(
                                    get: { viewModel.state.includeUppercase },
                                    set: { viewModel.handleChange(\.includeUppercase, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("password_generator.include_lowercase"),
                                isOn: Binding(
                                    get: { viewModel.state.includeLowercase },
                                    set: { viewModel.handleChange(\.includeLowercase, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("password_generator.include_numbers"),
                                isOn: Binding(
                                    get: { viewModel.state.includeNumbers },
                                    set: { viewModel.handleChange(\.includeNumbers, newValue: $0) }
                                )
                            )

                            ToggleRow(
                                title: localizationManager.localized("password_generator.include_special"),
                                isOn: Binding(
                                    get: { viewModel.state.includeSpecial },
                                    set: { viewModel.handleChange(\.includeSpecial, newValue: $0) }
                                )
                            )
                        }

                        // Длина пароля
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            HStack {
                                Text(localizationManager.localized("password_generator.password_length"))
                                    .font(.h4)
                                    .foregroundColor(.textPrimary)

                                Spacer()

                                Text("\(Int(viewModel.state.passwordLength))")
                                    .font(.body)
                                    .foregroundColor(.secondaryGold)
                            }

                            Slider(value: Binding(
                                get: { viewModel.state.passwordLength },
                                set: { viewModel.handlePasswordLengthChange($0) }
                            ), in: 8...32, step: 1)
                            .accentColor(.secondaryGold)
                        }

                        // Сгенерированный пароль
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("password_generator.generated_password"))
                                .font(.h4)
                                .foregroundColor(.textPrimary)

                            HStack {
                                Text(generatedPassword.isEmpty ? "••••••••••••" : generatedPassword)
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                    .padding()
                                    .background(Color.backgroundMedium.opacity(0.3))
                                    .cornerRadius(CornerRadius.medium)

                                Spacer()

                                Button {
                                    generatePassword()
                                } label: {
                                    Image(systemName: "arrow.clockwise")
                                        .font(.title2)
                                        .foregroundColor(.secondaryGold)
                                        .padding(.horizontal, Spacing.s)
                                }
                            }
                        }

                        // Кнопки действий
                        VStack(spacing: Spacing.m) {
                            PrimaryButton(
                                title: localizationManager.localized("password_generator.generate_new"),
                                icon: "key",
                                isLoading: false
                            ) {
                                generatePassword()
                            }

                            SecondaryButton(
                                title: localizationManager.localized("password_generator.copy_password"),
                                icon: "doc.on.doc"
                            ) {
                                copyPassword()
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            generatePassword() // Генерируем пароль при открытии
        }
        .onDisappear {
            viewModel.saveOnExit()
        }
        .id("password_generator_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }

    private func generatePassword() {
        // Простая генерация пароля на основе настроек
        var characters = ""
        if viewModel.state.includeLowercase { characters += "abcdefghijklmnopqrstuvwxyz" }
        if viewModel.state.includeUppercase { characters += "ABCDEFGHIJKLMNOPQRSTUVWXYZ" }
        if viewModel.state.includeNumbers { characters += "0123456789" }
        if viewModel.state.includeSpecial { characters += "!@#$%^&*()_+-=[]{}|;:,.<>?" }

        if characters.isEmpty {
            generatedPassword = "Настройте параметры"
            return
        }

        let length = Int(viewModel.state.passwordLength)
        generatedPassword = String((0..<length).compactMap { _ in characters.randomElement() })

        print("🔑 Сгенерирован пароль длиной \(length) символов")
    }

    private func copyPassword() {
        if !generatedPassword.isEmpty && generatedPassword != "Настройте параметры" {
            UIPasteboard.general.string = generatedPassword
            print("📋 Пароль скопирован в буфер обмена")
            // TODO: Показать toast уведомление
        }
    }
}

#if DEBUG
struct PasswordGeneratorSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        PasswordGeneratorSettingsScreen()
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
    }
}
#endif


