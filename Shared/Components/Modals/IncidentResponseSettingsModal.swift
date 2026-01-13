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
                        isOn: Binding(
                            get: { autoActions["block"] ?? false },
                            set: { autoActions["block"] = $0 }
                        )
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("incident_response.notify"),
                        isOn: Binding(
                            get: { autoActions["notify"] ?? true },
                            set: { autoActions["notify"] = $0 }
                        )
                    )
                    
                    ToggleRow(
                        title: localizationManager.localized("incident_response.escalate"),
                        isOn: Binding(
                            get: { autoActions["escalate"] ?? true },
                            set: { autoActions["escalate"] = $0 }
                        )
                    )
                }
            }
        }
        .environmentObject(localizationManager)
    }
    
    private func saveSettings() {
        // TODO: Сохранить настройки через API
        print("💾 Сохранение настроек инцидентов: \(escalationThresholds)")
        HapticFeedback.notification(.success)
    }
}

