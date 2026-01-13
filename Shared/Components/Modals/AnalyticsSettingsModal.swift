import SwiftUI

/**
 * 📊 Analytics Settings Modal
 * Модальное окно для настроек аналитики
 * Компонент: analytics_manager
 */

struct AnalyticsSettingsModal: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var configurationService = ComponentConfigurationService.shared
    @StateObject private var toastManager = ToastManager.shared
    
    @State private var selectedPeriod: String = "day" // day, week, month, year
    @State private var enabledMetrics: Set<String> = ["threats", "scans", "blocks", "devices"]
    @State private var reportFrequency: String = "weekly" // daily, weekly, monthly
    @State private var autoReportsEnabled: Bool = true
    
    let metrics = ["threats", "scans", "blocks", "devices", "family", "network"]
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Period Selection
                        periodSection
                        
                        // Enabled Metrics
                        metricsSection
                        
                        // Report Schedule
                        reportScheduleSection
                        
                        // Save Button
                        saveButton
                    }
                    .padding(Spacing.m)
                }
            }
            .navigationTitle(localizationManager.localized("component_analytics_manager_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common.cancel")) {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Sections
    
    private var periodSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_settings_period_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            Picker("", selection: $selectedPeriod) {
                Text(localizationManager.localized("analytics_settings_period_day")).tag("day")
                Text(localizationManager.localized("analytics_settings_period_week")).tag("week")
                Text(localizationManager.localized("analytics_settings_period_month")).tag("month")
                Text(localizationManager.localized("analytics_settings_period_year")).tag("year")
            }
            .pickerStyle(.segmented)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private var metricsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_settings_metrics_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            VStack(spacing: Spacing.s) {
                ForEach(metrics, id: \.self) { metric in
                    Toggle(
                        localizationManager.localized("analytics_settings_metric_\(metric)"),
                        isOn: Binding(
                            get: { enabledMetrics.contains(metric) },
                            set: { isOn in
                                if isOn {
                                    enabledMetrics.insert(metric)
                                } else {
                                    enabledMetrics.remove(metric)
                                }
                            }
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
    
    private var reportScheduleSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_settings_reports_title"))
                    .font(.title3)
                .foregroundColor(.textPrimary)
            
            Toggle(
                localizationManager.localized("analytics_settings_auto_reports"),
                isOn: $autoReportsEnabled
            )
            
            if autoReportsEnabled {
                Picker("", selection: $reportFrequency) {
                    Text(localizationManager.localized("analytics_settings_frequency_daily")).tag("daily")
                    Text(localizationManager.localized("analytics_settings_frequency_weekly")).tag("weekly")
                    Text(localizationManager.localized("analytics_settings_frequency_monthly")).tag("monthly")
                }
                .pickerStyle(.segmented)
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
            Text(localizationManager.localized("common.save"))
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

