import Foundation
import SwiftUI
import Combine

/// ViewModel для настроек мобильной безопасности
/// Реализует draft/save/rollback паттерн для надежного сохранения
@MainActor
class MobileSecuritySettingsViewModel: ObservableObject {

    // MARK: - Settings State

    struct SettingsState: Equatable {
        var deviceEncryption: Bool = true
        var appLock: Bool = true
        var screenLock: Bool = true
        var biometricAuth: Bool = true
        var remoteWipe: Bool = false
        var trackDevice: Bool = true
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
    private let componentId = "mobile_security_agent"

    // MARK: - Initialization

    init() {
        loadSettings()
    }

    // MARK: - Public Methods

    /// Загрузка настроек с fallback на дефолты
    func loadSettings() {
        isLoading = true
        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_load_start", state: .syncing)

        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newState = SettingsState(
                        deviceEncryption: settings["deviceEncryption"]?.value as? Bool ?? true,
                        appLock: settings["appLock"]?.value as? Bool ?? true,
                        screenLock: settings["screenLock"]?.value as? Bool ?? true,
                        biometricAuth: settings["biometricAuth"]?.value as? Bool ?? true,
                        remoteWipe: settings["remoteWipe"]?.value as? Bool ?? false,
                        trackDevice: settings["trackDevice"]?.value as? Bool ?? true
                    )

                    await MainActor.run {
                        self.state = newState
                        self.lastSavedState = newState
                        self.hasChanges = false
                        self.isLoading = false
                    }

                    log("✅ Настройки mobile security загружены из API")
                    SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_load_complete", state: .synced)
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                await MainActor.run {
                    self.lastSavedState = self.state
                    self.hasChanges = false
                    self.isLoading = false
                }

                log("⚠️ Настройки mobile security не найдены (404), используются дефолты: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_load_local", state: .local)
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
        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_change_pending", state: .pending)

        log("🔄 Mobile security setting изменен: \(keyPath) = \(newValue)")

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
        SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_save_start", state: .syncing)

        Task {
            do {
                // Получаем статус компонента
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                // Создаем конфигурацию
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "deviceEncryption": AnyCodable(state.deviceEncryption),
                        "appLock": AnyCodable(state.appLock),
                        "screenLock": AnyCodable(state.screenLock),
                        "biometricAuth": AnyCodable(state.biometricAuth),
                        "remoteWipe": AnyCodable(state.remoteWipe),
                        "trackDevice": AnyCodable(state.trackDevice)
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

                log("✅ Настройки mobile security успешно сохранены")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_save_complete", state: .synced)

            } catch {
                log("❌ Ошибка сохранения настроек mobile security: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "mobile_security_save_error", state: .error(error.localizedDescription))

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
        print("[MobileSecuritySettingsViewModel] \(message)")
    }
}