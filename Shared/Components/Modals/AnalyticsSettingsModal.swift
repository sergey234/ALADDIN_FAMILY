import SwiftUI

/**
 * 📊 Analytics Settings Modal
 * Модальное окно для настроек аналитики
 * Компонент: analytics_manager
 */

struct AnalyticsSettingsModal: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let configurationService = ComponentConfigurationService.shared
    private let toastManager = ToastManager.shared
    
    @State private var selectedPeriod: String = "day" // day, week, month, year
    @State private var enabledMetrics: Set<String> = ["threats", "scans", "blocks", "devices"]
    @State private var reportFrequency: String = "weekly" // daily, weekly, monthly
    @State private var autoReportsEnabled: Bool = true
    @State private var isSaving: Bool = false
    
    let metrics = ["threats", "scans", "blocks", "devices", "family", "network"]
    
    // Ключи для UserDefaults
    private let periodKey = "analytics_last_period"
    private let metricsKey = "analytics_last_enabled_metrics"
    private let frequencyKey = "analytics_last_report_frequency"
    private let autoReportsKey = "analytics_last_auto_reports"
    
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
                    Button(localizationManager.localized("common_cancel")) {
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            loadSettings()
        }
        .withVisualLogger()
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
                                VisualLogger.shared.log("🔄 analytics_metric_\(metric)_enabled = \(isOn)", level: .info, category: "ANALYTICS.UI")
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
                isOn: Binding(
                    get: { autoReportsEnabled },
                    set: { newValue in
                        autoReportsEnabled = newValue
                        VisualLogger.shared.log("🔄 analytics_auto_reports_enabled = \(newValue)", level: .info, category: "ANALYTICS.UI")
                    }
                )
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
            HStack(spacing: 8) {
                if isSaving {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                }
                Text(localizationManager.localized("common_save"))
                    .font(.bodyBold)
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(isSaving ? Color.primaryBlue.opacity(0.6) : Color.primaryBlue)
            .cornerRadius(CornerRadius.medium)
        }
        .disabled(isSaving)
    }
    
    // MARK: - Methods
    
    private func loadSettings() {
        SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_load_start", state: .syncing)
        // Загрузить из UserDefaults
        if let savedPeriod = UserDefaults.standard.string(forKey: periodKey) {
            selectedPeriod = savedPeriod
        }
        
        if let savedMetrics = UserDefaults.standard.array(forKey: metricsKey) as? [String] {
            enabledMetrics = Set(savedMetrics)
        }
        
        if let savedFrequency = UserDefaults.standard.string(forKey: frequencyKey) {
            reportFrequency = savedFrequency
        }
        
        autoReportsEnabled = UserDefaults.standard.bool(forKey: autoReportsKey)
        
        // Также попробовать загрузить из ComponentConfigurationService
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: "analytics_manager")
                await MainActor.run {
                    if let additionalSettings = config.additionalSettings {
                        if let periodCodable = additionalSettings["selectedPeriod"],
                           let period = periodCodable.value as? String {
                            selectedPeriod = period
                        }
                        if let metricsCodable = additionalSettings["enabledMetrics"],
                           let metricsArray = metricsCodable.value as? [Any],
                           let metrics = metricsArray.compactMap({ $0 as? String }) as [String]? {
                            enabledMetrics = Set(metrics)
                        }
                        if let frequencyCodable = additionalSettings["reportFrequency"],
                           let frequency = frequencyCodable.value as? String {
                            reportFrequency = frequency
                        }
                        if let autoReportsCodable = additionalSettings["autoReportsEnabled"],
                           let autoReports = autoReportsCodable.value as? Bool {
                            autoReportsEnabled = autoReports
                        }
                    }
                }
                SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_load_complete", state: .synced)
            } catch {
                // Игнорируем ошибку, используем значения из UserDefaults
                SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_load_local", state: .local)
            }
        }
    }
    
    private func saveSettings() {
        VisualLogger.shared.log("💾 analytics_settings_save tapped", level: .info, category: "ANALYTICS.UI")
        isSaving = true
        SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_save_start", state: .syncing)
        
        // Сохранить в UserDefaults
        UserDefaults.standard.set(selectedPeriod, forKey: periodKey)
        UserDefaults.standard.set(Array(enabledMetrics), forKey: metricsKey)
        UserDefaults.standard.set(reportFrequency, forKey: frequencyKey)
        UserDefaults.standard.set(autoReportsEnabled, forKey: autoReportsKey)
        
        Task {
            do {
                // Получить текущий статус компонента через метод (правильный доступ к @MainActor)
                let isComponentEnabled = await MainActor.run {
                    ComponentStatusService.shared.getComponentEnabledStatus(componentId: "analytics_manager")
                }
                
                let config = ComponentConfiguration(
                    isEnabled: isComponentEnabled,
                    priority: .normal,
                    additionalSettings: [
                        "selectedPeriod": AnyCodable(selectedPeriod),
                        "enabledMetrics": AnyCodable(Array(enabledMetrics)),
                        "reportFrequency": AnyCodable(reportFrequency),
                        "autoReportsEnabled": AnyCodable(autoReportsEnabled)
                    ]
                )
                
                try await configurationService.saveConfiguration(
                    componentId: "analytics_manager",
                    configuration: config
                )
                
                await MainActor.run {
                    VisualLogger.shared.log("✅ analytics_settings_save success", level: .success, category: "ANALYTICS.UI")
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isSaving = false
                    dismiss()
                }
                SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_save_complete", state: .synced)
            } catch {
                // Даже при ошибке сохранили в UserDefaults, показываем успех
                await MainActor.run {
                    VisualLogger.shared.log("⚠️ analytics_settings_save fallback local only", level: .warning, category: "ANALYTICS.UI")
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                    isSaving = false
                    dismiss()
                }
                SyncEngine.shared.publish(domain: .settings, operation: "analytics_modal_save_error", state: .error(error.localizedDescription))
            }
        }
    }
}

