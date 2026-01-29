import Foundation
import SwiftUI
import Combine

/// ViewModel для настроек защиты от фишинга
/// Реализует draft/save/rollback паттерн для надежного сохранения
@MainActor
class PhishingSettingsViewModel: ObservableObject {

    // MARK: - Settings State

    struct SettingsState: Equatable {
        var blockSuspiciousLinks: Bool = true
        var warnBeforeOpening: Bool = true
        var checkEmailLinks: Bool = true
        var checkSMSLinks: Bool = true
        var blockKnownPhishingDomains: Bool = true
        var sensitivityLevel: String = "medium"
    }

    // MARK: - Published Properties

    @Published var state = SettingsState()
    @Published var lastSavedState: SettingsState?
    @Published var hasChanges = false
    @Published var isApplyingState = false
    @Published var isLoading = false

    // MARK: - Dependencies

    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentId = "phishing_protection_agent"

    // MARK: - Initialization

    init() {
        loadSettings()
    }

    // MARK: - Public Methods

    /// Загрузка настроек с fallback на дефолты
    func loadSettings() {
        isLoading = true

        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newState = SettingsState(
                        blockSuspiciousLinks: settings["blockSuspiciousLinks"]?.value as? Bool ?? true,
                        warnBeforeOpening: settings["warnBeforeOpening"]?.value as? Bool ?? true,
                        checkEmailLinks: settings["checkEmailLinks"]?.value as? Bool ?? true,
                        checkSMSLinks: settings["checkSMSLinks"]?.value as? Bool ?? true,
                        blockKnownPhishingDomains: settings["blockKnownPhishingDomains"]?.value as? Bool ?? true,
                        sensitivityLevel: settings["sensitivityLevel"]?.value as? String ?? "medium"
                    )

                    await MainActor.run {
                        self.state = newState
                        self.lastSavedState = newState
                        self.hasChanges = false
                        self.isLoading = false
                    }

                    log("✅ Настройки phishing protection загружены из API")
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                await MainActor.run {
                    self.lastSavedState = self.state
                    self.hasChanges = false
                    self.isLoading = false
                }

                log("⚠️ Настройки phishing protection не найдены (404), используются дефолты: \(error.localizedDescription)")
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

        log("🔄 Phishing setting изменен: \(keyPath) = \(newValue)")

        // Сохраняем изменения
        performSave()
    }

    /// Обработка изменения уровня чувствительности
    func handleSensitivityLevelChange(_ newValue: String) {
        guard !isApplyingState else {
            log("⚠️ Изменение уровня чувствительности игнорировано - идет применение состояния")
            return
        }

        if state.sensitivityLevel == newValue {
            return // Нет изменений
        }

        // Обновляем состояние
        state.sensitivityLevel = newValue
        hasChanges = true

        log("🔄 Уровень чувствительности изменен: \(newValue)")

        // Сохраняем изменения
        performSave()
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

        Task {
            do {
                // Получаем статус компонента
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                // Создаем конфигурацию
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "blockSuspiciousLinks": AnyCodable(state.blockSuspiciousLinks),
                        "warnBeforeOpening": AnyCodable(state.warnBeforeOpening),
                        "checkEmailLinks": AnyCodable(state.checkEmailLinks),
                        "checkSMSLinks": AnyCodable(state.checkSMSLinks),
                        "blockKnownPhishingDomains": AnyCodable(state.blockKnownPhishingDomains),
                        "sensitivityLevel": AnyCodable(state.sensitivityLevel)
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

                log("✅ Настройки phishing protection успешно сохранены")

            } catch {
                log("❌ Ошибка сохранения настроек phishing protection: \(error.localizedDescription)")

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

    private func log(_ message: String) {
        print("[PhishingSettingsViewModel] \(message)")
    }
}