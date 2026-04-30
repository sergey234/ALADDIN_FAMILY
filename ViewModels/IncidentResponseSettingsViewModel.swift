import Foundation
import SwiftUI
import Combine

/// ViewModel для настроек реагирования на инциденты
/// Реализует draft/save/rollback паттерн для надежного сохранения
@MainActor
class IncidentResponseSettingsViewModel: ObservableObject {

    // MARK: - Settings State

    struct SettingsState: Equatable {
        var autoActions: Bool = true
        var escalationThresholds: Bool = true
        var slaTime: String = "4h"
        var contactRoles: Bool = true
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
    private let componentId = "incident_response_agent"

    // MARK: - Initialization

    init() {
        loadSettings()
    }

    // MARK: - Public Methods

    /// Загрузка настроек с fallback на дефолты
    func loadSettings() {
        isLoading = true
        SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_load_start", state: .syncing)

        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    let newState = SettingsState(
                        autoActions: settings["autoActions"]?.value as? Bool ?? true,
                        escalationThresholds: settings["escalationThresholds"]?.value as? Bool ?? true,
                        slaTime: settings["slaTime"]?.value as? String ?? "4h",
                        contactRoles: settings["contactRoles"]?.value as? Bool ?? true
                    )

                    await MainActor.run {
                        self.state = newState
                        self.lastSavedState = newState
                        self.hasChanges = false
                        self.isLoading = false
                    }

                    log("✅ Настройки incident response загружены из API")
                    SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_load_complete", state: .synced)
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                await MainActor.run {
                    self.lastSavedState = self.state
                    self.hasChanges = false
                    self.isLoading = false
                }

                log("⚠️ Настройки incident response не найдены (404), используются дефолты: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_load_local", state: .local)
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
        SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_change_pending", state: .pending)

        log("🔄 Incident response setting изменен: \(keyPath) = \(newValue)")

        // Сохраняем изменения
        performSave()
    }

    /// Обработка изменения SLA времени
    func handleSLATimeChange(_ newValue: String) {
        guard !isApplyingState else {
            log("⚠️ Изменение SLA времени игнорировано - идет применение состояния")
            return
        }

        if state.slaTime == newValue {
            return // Нет изменений
        }

        // Обновляем состояние
        state.slaTime = newValue
        hasChanges = true
        SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_change_pending", state: .pending)

        log("🔄 SLA время изменено: \(newValue)")

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
        SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_save_start", state: .syncing)

        Task {
            do {
                // Получаем статус компонента
                let isComponentEnabled = ComponentStatusService.shared.getComponentEnabledStatus(componentId: componentId)

                // Создаем конфигурацию
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .critical, // Incident Response is critical
                    additionalSettings: [
                        "autoActions": AnyCodable(state.autoActions),
                        "escalationThresholds": AnyCodable(state.escalationThresholds),
                        "slaTime": AnyCodable(state.slaTime),
                        "contactRoles": AnyCodable(state.contactRoles)
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

                log("✅ Настройки incident response успешно сохранены")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_save_complete", state: .synced)

            } catch {
                log("❌ Ошибка сохранения настроек incident response: \(error.localizedDescription)")
                SyncEngine.shared.publish(domain: .networkProtection, operation: "incident_response_save_error", state: .error(error.localizedDescription))

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
        print("[IncidentResponseSettingsViewModel] \(message)")
    }
}