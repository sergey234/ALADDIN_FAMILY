import SwiftUI

/**
 * 👨‍👩‍👧‍👦 Family Notification Settings Modal
 * Модальное окно для настроек семейных уведомлений
 * Компонент: family_notification_manager
 */

struct FamilyNotificationSettingsModal: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var configurationService = ComponentConfigurationService.shared
    @StateObject private var toastManager = ToastManager.shared
    
    @State private var channels: [String: Bool] = ["push": true, "email": false, "sms": false]
    @State private var frequency: String = "instant" // instant, daily, weekly
    @State private var messageTemplates: [String: String] = [:]
    @State private var topicPriorities: [String: Int] = ["security": 1, "activity": 2, "rewards": 3]
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Channels
                        channelsSection
                        
                        // Frequency
                        frequencySection
                        
                        // Message Templates
                        templatesSection
                        
                        // Topic Priorities
                        prioritiesSection
                        
                        // Save Button
                        saveButton
                    }
                    .padding(Spacing.m)
                }
            }
            .navigationTitle(localizationManager.localized("component_family_notification_manager_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_cancel")) {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Sections
    
    private var channelsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("family_notifications_channels_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                Toggle(
                    localizationManager.localized("family_notifications_channel_push"),
                    isOn: Binding(
                        get: { channels["push"] ?? false },
                        set: { channels["push"] = $0 }
                    )
                )
                Toggle(
                    localizationManager.localized("family_notifications_channel_email"),
                    isOn: Binding(
                        get: { channels["email"] ?? false },
                        set: { channels["email"] = $0 }
                    )
                )
                Toggle(
                    localizationManager.localized("family_notifications_channel_sms"),
                    isOn: Binding(
                        get: { channels["sms"] ?? false },
                        set: { channels["sms"] = $0 }
                    )
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var frequencySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("family_notifications_frequency_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            Picker("", selection: $frequency) {
                Text(localizationManager.localized("family_notifications_frequency_instant")).tag("instant")
                Text(localizationManager.localized("family_notifications_frequency_daily")).tag("daily")
                Text(localizationManager.localized("family_notifications_frequency_weekly")).tag("weekly")
            }
            .pickerStyle(.segmented)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var templatesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("family_notifications_templates_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(["security", "activity", "rewards"], id: \.self) { topic in
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("family_notifications_template_\(topic)"))
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        TextField(
                            localizationManager.localized("family_notifications_template_placeholder"),
                            text: Binding(
                                get: { messageTemplates[topic] ?? "" },
                                set: { messageTemplates[topic] = $0 }
                            )
                        )
                        .textFieldStyle(.roundedBorder)
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var prioritiesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("family_notifications_priorities_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(["security", "activity", "rewards"], id: \.self) { topic in
                    HStack {
                        Text(localizationManager.localized("family_notifications_priority_\(topic)"))
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        Spacer()
                        Stepper(
                            "",
                            value: Binding(
                                get: { topicPriorities[topic] ?? 1 },
                                set: { topicPriorities[topic] = $0 }
                            ),
                            in: 1...5
                        )
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var saveButton: some View {
        Button(action: saveSettings) {
            Text(localizationManager.localized("common_save"))
                .font(.bodyBold)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.primaryBlue)
                .cornerRadius(CornerRadius.medium)
        }
    }
    
    // MARK: - Methods
    
    private func saveSettings() {
        Task {
            // TODO: Сохранить настройки через API
            toastManager.showSuccess("Настройки сохранены")
            dismiss()
        }
    }
}

