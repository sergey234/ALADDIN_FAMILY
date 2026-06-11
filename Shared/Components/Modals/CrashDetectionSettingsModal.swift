import SwiftUI

/**
 * 🚨 Crash Detection Settings Modal
 * Модальное окно для настройки обнаружения аварий
 */

struct CrashDetectionSettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared
    private let crashDetectionManager = CrashDetectionManager.shared
    private let apiService = APIService.shared

    @State private var sensitivity: CrashDetectionSensitivity = .medium
    @State private var isLoading: Bool = false

    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.crash_detection_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.orange)
                        Text(localizationManager.localized("crash_settings_warning_title"))
                            .font(.h4)
                            .foregroundColor(.textPrimary)
                    }

                    Text(localizationManager.localized("crash_settings_warning_message"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding()
                .background(Color.orange.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.orange.opacity(0.3), lineWidth: 1)
                )

                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("crash_settings_detection_title"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)

                    VStack(spacing: Spacing.m) {
                        ForEach(CrashDetectionSensitivity.allCases, id: \.self) { sensitivityOption in
                            SensitivityOptionRow(
                                sensitivity: sensitivityOption,
                                isSelected: sensitivity == sensitivityOption,
                                localizationManager: localizationManager,
                                onSelect: {
                                    sensitivity = sensitivityOption
                                    componentAnalytics.trackSettingToggle(
                                        componentId: componentId,
                                        settingKey: "sensitivity",
                                        enabled: true
                                    )
                                }
                            )
                        }
                    }
                }

                VStack(alignment: .leading, spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "battery.100")
                            .foregroundColor(.green)
                        Text(localizationManager.localized("crash_settings_battery_optimization_title"))
                            .font(.h4)
                            .foregroundColor(.textPrimary)
                    }

                    Text(localizationManager.localized("crash_settings_battery_optimization_message"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .onAppear {
            loadCurrentSettings()
        }
    }

    private func loadCurrentSettings() {
        SyncEngine.shared.publish(domain: .networkProtection, operation: "crash_detection_modal_load_start", state: .syncing)
        sensitivity = crashDetectionManager.getSensitivity()
        SyncEngine.shared.publish(domain: .networkProtection, operation: "crash_detection_modal_load_complete", state: .synced)
    }

    private func resolvedUserId() -> String? {
        let stored = (UserDefaults.standard.string(forKey: "user_id") ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return stored.isEmpty ? nil : stored
    }

    private func saveSettings() {
        guard let userId = resolvedUserId() else {
            toastManager.showError(localizationManager.localized("crash_settings_save_error"))
            return
        }

        isLoading = true
        SyncEngine.shared.publish(domain: .networkProtection, operation: "crash_detection_modal_save_start", state: .syncing)

        Task {
            do {
                crashDetectionManager.setSensitivity(sensitivity)

                let apiResponse = try await apiService.updateCrashDetectionSettings(
                    userId: userId,
                    sensitivity: sensitivity.gForceThreshold,
                    geofenceRadius: 1000.0
                )
                guard apiResponse.success else {
                    throw NSError(
                        domain: "CrashDetectionSettings",
                        code: -1,
                        userInfo: [NSLocalizedDescriptionKey: localizationManager.localized("crash_settings_save_error")]
                    )
                }

                _ = try await apiService.startCrashDetectionMonitoring()
                try await crashDetectionManager.startMonitoring()

                let configuration = ComponentConfiguration(
                    isEnabled: true,
                    priority: .critical,
                    additionalSettings: [
                        "sensitivity": AnyCodable(sensitivity.rawValue),
                        "gForceThreshold": AnyCodable(sensitivity.gForceThreshold),
                        "speedThreshold": AnyCodable(50.0),
                        "batteryOptimization": AnyCodable(true),
                    ]
                )
                try await configurationService.saveConfiguration(
                    componentId: componentId,
                    configuration: configuration
                )

                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("crash_settings_save_success"))
                    isPresented = false
                }
                SyncEngine.shared.publish(domain: .networkProtection, operation: "crash_detection_modal_save_complete", state: .synced)
            } catch {
                await MainActor.run {
                    toastManager.showError(localizationManager.localized("crash_settings_save_error"))
                }
                print("❌ CrashDetectionSettingsModal: Ошибка сохранения: \(error.localizedDescription)")
                SyncEngine.shared.publish(
                    domain: .networkProtection,
                    operation: "crash_detection_modal_save_error",
                    state: .error(error.localizedDescription)
                )
            }

            await MainActor.run {
                isLoading = false
            }
        }
    }
}

// MARK: - Supporting Views

struct SensitivityOptionRow: View {
    let sensitivity: CrashDetectionSensitivity
    let isSelected: Bool
    let localizationManager: LocalizationManager
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(sensitivity.localizedTitle(using: localizationManager))
                        .font(.body)
                        .foregroundColor(.textPrimary)

                    Text(sensitivity.localizedDescription(using: localizationManager))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }

                Spacer()

                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.primaryBlue)
                        .font(.title2)
                } else {
                    Circle()
                        .stroke(Color.gray.opacity(0.3), lineWidth: 2)
                        .frame(width: 24, height: 24)
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(isSelected ? Color.primaryBlue.opacity(0.1) : Color.clear)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(isSelected ? Color.primaryBlue.opacity(0.3) : Color.gray.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

extension CrashDetectionSensitivity {
    func localizedTitle(using localizationManager: LocalizationManager) -> String {
        switch self {
        case .low:
            return localizationManager.localized("crash_sensitivity_low_label")
        case .medium:
            return localizationManager.localized("crash_sensitivity_medium_label")
        case .high:
            return localizationManager.localized("crash_sensitivity_high_label")
        }
    }

    func localizedDescription(using localizationManager: LocalizationManager) -> String {
        switch self {
        case .low:
            return localizationManager.localized("crash_sensitivity_low_desc")
        case .medium:
            return localizationManager.localized("crash_sensitivity_medium_desc")
        case .high:
            return localizationManager.localized("crash_sensitivity_high_desc")
        }
    }
}
