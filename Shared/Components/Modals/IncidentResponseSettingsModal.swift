import SwiftUI

/**
 * 🚨 Incident Response Settings Modal
 * Модальное окно для настройки реагирования на инциденты
 */

// MARK: - ToggleRow (если не импортирован)
struct ToggleRow: View {
    let title: String
    @Binding var isOn: Bool
    
    var body: some View {
        HStack {
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            Spacer()
            Toggle("", isOn: $isOn)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.white.opacity(0.05))
        )
    }
}

struct IncidentResponseSettingsModal: View {
    let componentId: String
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared
    
    @State private var escalationThresholds: [String: String] = [
        "low": "30",
        "medium": "15",
        "high": "5",
        "critical": "1"
    ]
    
    @State private var slaTime: String = "30"
    @State private var contactRoles: [String] = ["admin", "security"]
    @State private var autoActions: [String: Bool] = [
        "block": false,
        "notify": true,
        "escalate": true
    ]

    // Отдельные состояния для логирования
    @State private var blockEnabled: Bool = false
    @State private var notifyEnabled: Bool = true
    @State private var escalateEnabled: Bool = true
    @State private var isLoading: Bool = false
    
    var body: some View {
        ComponentSettingsModal(
            componentId: componentId,
            title: localizationManager.localized("component.incident_response_agent.title"),
            isPresented: $isPresented,
            onSave: {
                saveSettings()
            }
        ) {
            VStack(spacing: Spacing.l) {
                // Пороги эскалации
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("incident_response.escalation_thresholds"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    ForEach(["low", "medium", "high", "critical"], id: \.self) { level in
                        HStack {
                            Text(localizationManager.localized("incident_response.\(level)"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            TextField("", text: Binding(
                                get: { escalationThresholds[level] ?? "" },
                                set: { escalationThresholds[level] = $0 }
                            ))
                            .keyboardType(.numberPad)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .frame(width: 60)
                            
                            Text(localizationManager.localized("incident_response.minutes"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.backgroundMedium.opacity(0.2))
                        )
                    }
                }
                
                // Сроки SLA
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("incident_response.sla_time"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    HStack {
                        TextField("", text: $slaTime)
                            .keyboardType(.numberPad)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .frame(width: 60)
                        
                        Text(localizationManager.localized("incident_response.minutes"))
                            .font(.body)
                            .foregroundColor(.textPrimary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                
                // Автодействия
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("incident_response.auto_actions"))
                        .font(.h4)
                        .foregroundColor(.textPrimary)
                    
                    ToggleRow(
                        title: localizationManager.localized("incident_response.block"),
                        isOn: $blockEnabled
                    )
                    .onChange(of: blockEnabled) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "autoActions_block",
                            enabled: newValue
                        )
                        autoActions["block"] = newValue
                        print("🔄 IncidentResponse: autoActions_block = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("incident_response.notify"),
                        isOn: $notifyEnabled
                    )
                    .onChange(of: notifyEnabled) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "autoActions_notify",
                            enabled: newValue
                        )
                        autoActions["notify"] = newValue
                        print("🔄 IncidentResponse: autoActions_notify = \(newValue)")
                    }

                    ToggleRow(
                        title: localizationManager.localized("incident_response.escalate"),
                        isOn: $escalateEnabled
                    )
                    .onChange(of: escalateEnabled) { newValue in
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: "autoActions_escalate",
                            enabled: newValue
                        )
                        autoActions["escalate"] = newValue
                        print("🔄 IncidentResponse: autoActions_escalate = \(newValue)")
                    }
                }
            }
        }
        .environmentObject(localizationManager)
        .onAppear {
            loadSettings()
        }
    }
    
    // ✅ Загрузка настроек при открытии
    private func loadSettings() {
        isLoading = true
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: componentId)
                if let settings = config.additionalSettings {
                    if let value = settings["escalationThresholds"]?.value as? [String: String] {
                        escalationThresholds = value
                    }
                    if let value = settings["slaTime"]?.value as? String {
                        slaTime = value
                    }
                    if let value = settings["contactRoles"]?.value as? [String] {
                        contactRoles = value
                    }
                    if let value = settings["autoActions"]?.value as? [String: Bool] {
                        autoActions = value
                        // Синхронизировать @State переменные
                        blockEnabled = value["block"] ?? false
                        notifyEnabled = value["notify"] ?? true
                        escalateEnabled = value["escalate"] ?? true
                    }
                }
            } catch {
                print("⚠️ IncidentResponseSettingsModal: Ошибка загрузки настроек: \(error)")
                // Использовать дефолтные значения
                await MainActor.run {
                    blockEnabled = autoActions["block"] ?? false
                    notifyEnabled = autoActions["notify"] ?? true
                    escalateEnabled = autoActions["escalate"] ?? true
                }
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
                    priority: .critical, // Incident Response is critical
                    additionalSettings: [
                        "escalationThresholds": AnyCodable(escalationThresholds),
                        "slaTime": AnyCodable(slaTime),
                        "contactRoles": AnyCodable(contactRoles),
                        "autoActions": AnyCodable(autoActions)
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

