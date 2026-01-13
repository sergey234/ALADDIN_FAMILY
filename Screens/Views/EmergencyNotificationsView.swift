import SwiftUI

/**
 * 🔔 Emergency Notifications View
 * Экран настройки экстренных уведомлений
 * Компонент: emergency_notification_manager
 */

struct EmergencyNotificationsView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    
    @State private var messageTemplates: [String: String] = [:]
    @State private var deliveryChannels: [String: Bool] = ["push": true, "sms": true, "email": false, "call": false]
    @State private var repeatFrequency: Int = 1 // раз в минуту
    @State private var timeWindows: [(start: Date, end: Date)] = []
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("component_emergency_notification_manager_title"),
                    subtitle: localizationManager.localized("component_emergency_notification_manager_description"),
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Message Templates
                        messageTemplatesSection
                        
                        // Delivery Channels
                        deliveryChannelsSection
                        
                        // Repeat Frequency
                        repeatFrequencySection
                        
                        // Save Button
                        saveButton
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            loadSettings()
        }
    }
    
    // MARK: - Sections
    
    private var messageTemplatesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("emergency_notifications_templates_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(["crash", "medical", "security"], id: \.self) { type in
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("emergency_notifications_template_\(type)"))
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        TextField(
                            localizationManager.localized("emergency_notifications_template_placeholder"),
                            text: Binding(
                                get: { messageTemplates[type] ?? "" },
                                set: { messageTemplates[type] = $0 }
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
    
    private var deliveryChannelsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("emergency_notifications_channels_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(["push", "sms", "email", "call"], id: \.self) { channel in
                    Toggle(
                        localizationManager.localized("emergency_notifications_channel_\(channel)"),
                        isOn: Binding(
                            get: { deliveryChannels[channel] ?? false },
                            set: { deliveryChannels[channel] = $0 }
                        )
                    )
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var repeatFrequencySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("emergency_notifications_repeat_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            HStack {
                Text("\(repeatFrequency)")
                    .font(.headline)
                Text(localizationManager.localized("emergency_notifications_repeat_minutes"))
                    .font(.body)
                Spacer()
            }
            
            Slider(value: Binding(
                get: { Double(repeatFrequency) },
                set: { repeatFrequency = Int($0) }
            ), in: 1...60, step: 1)
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
    
    // ✅ Загрузка настроек при открытии
    private func loadSettings() {
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: "emergency_notification_manager")
                if let settings = config.additionalSettings {
                    if let templates = settings["messageTemplates"]?.value as? [String: String] {
                        messageTemplates = templates
                    }
                    if let channels = settings["deliveryChannels"]?.value as? [String: Bool] {
                        deliveryChannels = channels
                    }
                    if let frequency = settings["repeatFrequency"]?.value as? Int {
                        repeatFrequency = frequency
                    }
                }
            } catch {
                print("⚠️ EmergencyNotificationsView: Ошибка загрузки настроек: \(error)")
            }
        }
    }
    
    // ✅ Сохранение настроек через ComponentConfigurationService
    private func saveSettings() {
        Task {
            do {
                // Получить текущий статус компонента через метод (правильный доступ к @MainActor)
                let isComponentEnabled = await MainActor.run {
                    ComponentStatusService.shared.getComponentEnabledStatus(componentId: "emergency_notification_manager")
                }
                
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "messageTemplates": AnyCodable(messageTemplates),
                        "deliveryChannels": AnyCodable(deliveryChannels),
                        "repeatFrequency": AnyCodable(repeatFrequency)
                    ]
                )
                
                try await configurationService.saveConfiguration(
                    componentId: "emergency_notification_manager",
                    configuration: config
                )
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    dismiss()
                }
            }
        }
    }
}

