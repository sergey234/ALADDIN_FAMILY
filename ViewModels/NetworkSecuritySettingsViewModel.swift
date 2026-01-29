import Foundation
import SwiftUI
import Combine

/// ViewModel для настроек сетевой безопасности
/// Реализует draft/save/rollback паттерн для надежного сохранения
@MainActor
class NetworkSecuritySettingsViewModel: ObservableObject {

    // MARK: - Settings State

    struct SettingsState: Equatable {
        var blockUnsafeNetworks: Bool = true
        var warnOnPublicWiFi: Bool = true
        var autoConnectVPN: Bool = false
        var blockTracking: Bool = true
        var encryptTraffic: Bool = true
        var firewallEnabled: Bool = true
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
    private let componentId = "network_security_agent"

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
                        blockUnsafeNetworks: settings["blockUnsafeNetworks"]?.value as? Bool ?? true,
                        warnOnPublicWiFi: settings["warnOnPublicWiFi"]?.value as? Bool ?? true,
                        autoConnectVPN: settings["autoConnectVPN"]?.value as? Bool ?? false,
                        blockTracking: settings["blockTracking"]?.value as? Bool ?? true,
                        encryptTraffic: settings["encryptTraffic"]?.value as? Bool ?? true,
                        firewallEnabled: settings["firewallEnabled"]?.value as? Bool ?? true
                    )

                    await MainActor.run {
                        self.state = newState
                        self.lastSavedState = newState
                        self.hasChanges = false
                        self.isLoading = false
                    }

                    log("✅ Настройки network security загружены из API")
                }
            } catch {
                // 404 или ошибка сети - используем дефолты
                await MainActor.run {
                    self.lastSavedState = self.state
                    self.hasChanges = false
                    self.isLoading = false
                }

                log("⚠️ Настройки network security не найдены (404), используются дефолты: \(error.localizedDescription)")
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

        log("🔄 Network security setting изменен: \(keyPath) = \(newValue)")

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
                        "blockUnsafeNetworks": AnyCodable(state.blockUnsafeNetworks),
                        "warnOnPublicWiFi": AnyCodable(state.warnOnPublicWiFi),
                        "autoConnectVPN": AnyCodable(state.autoConnectVPN),
                        "blockTracking": AnyCodable(state.blockTracking),
                        "encryptTraffic": AnyCodable(state.encryptTraffic),
                        "firewallEnabled": AnyCodable(state.firewallEnabled)
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

                log("✅ Настройки network security успешно сохранены")

            } catch {
                log("❌ Ошибка сохранения настроек network security: \(error.localizedDescription)")

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
        print("[NetworkSecuritySettingsViewModel] \(message)")
    }
}