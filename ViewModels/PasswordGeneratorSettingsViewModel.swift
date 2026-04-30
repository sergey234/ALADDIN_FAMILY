import Foundation
import SwiftUI
import Combine

/// ViewModel для настроек генератора паролей
/// Реализует draft/save/rollback паттерн для надежного сохранения
@MainActor
class PasswordGeneratorSettingsViewModel: ObservableObject {

    // MARK: - Settings State

    struct SettingsState: Equatable {
        var passwordLength: Int = 16
        var includeUppercase: Bool = true
        var includeLowercase: Bool = true
        var includeNumbers: Bool = true
        var includeSpecial: Bool = true
    }

    // MARK: - Published Properties

    @Published var state = SettingsState()
    @Published var lastSavedState: SettingsState?
    @Published var hasChanges = false
    @Published var isApplyingState = false
    @Published var isLoading = false

    @Published var generatedPassword: String = ""
    @Published var isGenerating: Bool = false

    // MARK: - Dependencies

    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentId = "password_security_agent"

    // MARK: - Initialization

    init() {
        loadSettings()
        generatePassword()
    }

    // MARK: - Public Methods

    /// Загрузка настроек с fallback на дефолты
    func loadSettings() {
        isLoading = true
        SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_load_start", state: .syncing)

        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newState = SettingsState(
                        passwordLength: settings["passwordLength"]?.value as? Int ?? 16,
                        includeUppercase: settings["includeUppercase"]?.value as? Bool ?? true,
                        includeLowercase: settings["includeLowercase"]?.value as? Bool ?? true,
                        includeNumbers: settings["includeNumbers"]?.value as? Bool ?? true,
                        includeSpecial: settings["includeSpecial"]?.value as? Bool ?? true
                    )

                    await MainActor.run {
                        self.state = newState
                        self.lastSavedState = newState
                        self.hasChanges = false
                        self.isLoading = false
                    }

                    log("✅ Настройки password generator загружены из API")
                    SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_load_complete", state: .synced)
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                await MainActor.run {
                    self.lastSavedState = self.state
                    self.hasChanges = false
                    self.isLoading = false
                }

                log("⚠️ Настройки password generator не найдены (404), используются дефолты: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_load_local", state: .local)
            }
        }
    }

    /// Обработка изменения настройки
    func handleChange(_ keyPath: WritableKeyPath<SettingsState, Bool>, newValue: Bool) {
        guard !isApplyingState else {
            log("⚠️ Изменение игнорировано - идет применение состояния")
            return
        }

        let oldValue = state[keyPath: keyPath]
        if oldValue == newValue {
            return // Нет изменений
        }

        // Обновляем состояние
        state[keyPath: keyPath] = newValue
        hasChanges = true
        SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_change_pending", state: .pending)

        log("🔄 Password generator setting изменен: \(keyPath) = \(newValue)")

        // Генерируем новый пароль
        generatePassword()

        // Сохраняем изменения
        performSave()
    }

    /// Обработка изменения длины пароля
    func handlePasswordLengthChange(_ newValue: Int) {
        guard !isApplyingState else {
            log("⚠️ Изменение длины пароля игнорировано - идет применение состояния")
            return
        }

        if state.passwordLength == newValue {
            return // Нет изменений
        }

        // Обновляем состояние
        state.passwordLength = newValue
        hasChanges = true
        SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_change_pending", state: .pending)

        log("🔄 Длина пароля изменена: \(newValue)")

        // Генерируем новый пароль
        generatePassword()

        // Сохраняем изменения
        performSave()
    }

    /// Генерация нового пароля
    func generatePassword() {
        guard !isGenerating else { return }

        isGenerating = true

        Task {
            let password = await generateSecurePassword(
                length: state.passwordLength,
                includeUppercase: state.includeUppercase,
                includeLowercase: state.includeLowercase,
                includeNumbers: state.includeNumbers,
                includeSpecial: state.includeSpecial
            )

            await MainActor.run {
                generatedPassword = password
                isGenerating = false
            }
        }
    }

    /// Выполнение сохранения
    func performSave() {
        guard hasChanges else {
            log("⚠️ Сохранение пропущено - нет изменений")
            return
        }

        guard !isApplyingState else {
            log("⚠️ Сохранение пропущено - уже идет сохранение")
            return
        }

        isApplyingState = true
        SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_save_start", state: .syncing)

        Task {
            do {
                // Получаем статус компонента
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                // Создаем конфигурацию
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "passwordLength": AnyCodable(state.passwordLength),
                        "includeUppercase": AnyCodable(state.includeUppercase),
                        "includeLowercase": AnyCodable(state.includeLowercase),
                        "includeNumbers": AnyCodable(state.includeNumbers),
                        "includeSpecial": AnyCodable(state.includeSpecial)
                    ]
                )

                // Сохраняем
                try await configurationService.saveConfiguration(
                    componentId: componentId,
                    configuration: config
                )

                await MainActor.run {
                    lastSavedState = state
                    hasChanges = false
                    isApplyingState = false
                    toastManager.showSuccess("Настройки сохранены")
                }

                log("✅ Настройки password generator успешно сохранены")
                SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_save_complete", state: .synced)

            } catch {
                log("❌ Ошибка сохранения настроек password generator: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .settings, operation: "password_generator_vm_save_error", state: .error(error.localizedDescription))

                // Rollback к последнему сохраненному состоянию
                if let lastSaved = lastSavedState {
                    await MainActor.run {
                        state = lastSaved
                        hasChanges = false
                        isApplyingState = false
                        toastManager.showError("Ошибка сохранения. Изменения отменены.")
                    }
                    log("🔄 Rollback выполнен - возвращены последние сохраненные настройки")
                } else {
                    await MainActor.run {
                        isApplyingState = false
                        toastManager.showError("Ошибка сохранения настроек")
                    }
                }
            }
        }
    }

    /// Сохранение при выходе (если есть несохраненные изменения)
    func saveOnExit() {
        guard hasChanges && !isApplyingState else {
            return
        }

        log("💾 Save on exit - сохраняем несохраненные изменения")
        performSave()
    }

    // MARK: - Private Methods

    private func generateSecurePassword(
        length: Int,
        includeUppercase: Bool,
        includeLowercase: Bool,
        includeNumbers: Bool,
        includeSpecial: Bool
    ) async -> String {
        var charset = ""
        var mandatoryChars = [String]()

        if includeLowercase {
            charset += "abcdefghijklmnopqrstuvwxyz"
            mandatoryChars.append("abcdefghijklmnopqrstuvwxyz.randomElement()!")
        }

        if includeUppercase {
            charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            mandatoryChars.append("ABCDEFGHIJKLMNOPQRSTUVWXYZ.randomElement()!")
        }

        if includeNumbers {
            charset += "0123456789"
            mandatoryChars.append("0123456789.randomElement()!")
        }

        if includeSpecial {
            charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
            mandatoryChars.append("!@#$%^&*()-_=+[]{}|;:,.<>?/~.randomElement()!")
        }

        guard !charset.isEmpty else {
            return "Configure password rules first"
        }

        var password = ""

        // Добавляем обязательные символы из каждой категории
        for char in mandatoryChars {
            if char.count > 0, let firstChar = char.first {
                password += String(firstChar)
            }
        }

        // Заполняем оставшуюся длину случайными символами
        let remainingLength = max(0, length - password.count)
        for _ in 0..<remainingLength {
            if let randomChar = charset.randomElement() {
                password += String(randomChar)
            }
        }

        // Перемешиваем пароль
        let shuffledPassword = String(password.shuffled())

        return String(shuffledPassword.prefix(length))
    }

    private func log(_ message: String) {
        print("[PasswordGeneratorSettingsViewModel] \(message)")
    }
}