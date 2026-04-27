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
                // Предупреждение о ложных срабатываниях
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

                // Настройки чувствительности
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("crash_settings_detection_title"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)

                    VStack(spacing: Spacing.m) {
                        ForEach(CrashDetectionSensitivity.allCases, id: \.self) { sensitivityOption in
                            SensitivityOptionRow(
                                sensitivity: sensitivityOption,
                                isSelected: sensitivity == sensitivityOption,
                                onSelect: {
                                    sensitivity = sensitivityOption
                                    componentAnalytics.trackSettingToggle(
                                        componentId: componentId,
                                        settingKey: "sensitivity",
                                        enabled: true
                                    )
                                    print("🔄 CrashDetection: sensitivity = \(sensitivityOption.rawValue)")
                                }
                            )
                        }
                    }
                }

                // Информация о батарее
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
        sensitivity = crashDetectionManager.getSensitivity()
    }

    private func saveSettings() {
        isLoading = true

        Task {
            do {
                // Сохранить чувствительность
                crashDetectionManager.setSensitivity(sensitivity)

                // Сохранить в конфигурацию компонента
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
                    toastManager.showSuccess("Настройки сохранены")
                    isPresented = false
                }

            } catch {
                await MainActor.run {
                    toastManager.showError("Ошибка сохранения настроек")
                }
                print("❌ CrashDetectionSettingsModal: Ошибка сохранения: \(error.localizedDescription)")
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
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(sensitivity.displayName)
                        .font(.body)
                        .foregroundColor(.textPrimary)

                    Text(getSensitivityDescription(sensitivity))
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

    private func getSensitivityDescription(_ sensitivity: CrashDetectionSensitivity) -> String {
        switch sensitivity {
        case .low:
            return "Меньше ложных срабатываний, но может пропустить аварию"
        case .medium:
            return "Оптимальный баланс между обнаружением и ложными срабатываниями"
        case .high:
            return "Максимальная чувствительность, больше ложных срабатываний"
        }
    }
}