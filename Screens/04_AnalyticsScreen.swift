import SwiftUI
import Foundation

// Master Logger for UI logging
private let logger = MasterLogger.shared

/// 📊 Analytics Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {

    // MARK: - State

    init() {
        logger.screenLoad("AnalyticsScreen")
    }
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = AnalyticsScreen.makeViewModel()
    @State private var showAnalyticsSettings: Bool = false
    @State private var didStartInitialLoad: Bool = false
    
    // MARK: - Component Reports Modals
    
    @State private var showDrivingReportsModal: Bool = false
    @State private var showDarkWebMonitoringModal: Bool = false
    @State private var showIdentityTheftModal: Bool = false
    @State private var showPrivacyReportsModal: Bool = false
    @State private var showAICategoriesModal: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("analytics_accessibility_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // ✅ ВАРИАНТ 4: Индикатор источника данных (с дебаунсом)
                DebouncedDataSourceIndicator(dataSource: viewModel.dataSource, localizationManager: localizationManager)
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.s)
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // ✅ ЗАДАЧА 64: Индикатор офлайн режима
                        if viewModel.isOfflineMode {
                            HStack(spacing: Spacing.s) {
                                Image(systemName: "wifi.slash")
                                    .foregroundColor(.orange)
                                Text(localizationManager.localized("analytics_offline_mode"))
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.orange)
                                Spacer()
                            }
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.s)
                            .background(Color.orange.opacity(0.1))
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        // Компактные карточки в 1 строку
                        mainStats
                        
                        // Разбивка по типам угроз
                        threatBreakdown

                        // Уровень защиты
                        protectionBlock
                        
                        // Компоненты защиты (НОВОЕ)
                        componentsReportsSection
                        
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("analytics_accessibility_summary"))
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("analytics_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showAnalyticsSettings) {
            AnalyticsSettingsModal()
                .environmentObject(localizationManager)
        }
        // Модальные окна отчетов компонентов
        .sheet(isPresented: $showDrivingReportsModal) {
            DrivingReportsModal(isPresented: $showDrivingReportsModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDarkWebMonitoringModal) {
            DarkWebMonitoringModal(isPresented: $showDarkWebMonitoringModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showIdentityTheftModal) {
            IdentityTheftModal(isPresented: $showIdentityTheftModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPrivacyReportsModal) {
            PrivacyReportsModal(isPresented: $showPrivacyReportsModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAICategoriesModal) {
            AICategoriesModal(isPresented: $showAICategoriesModal)
                .environmentObject(localizationManager)
        }
        .overlay(alignment: .center) {
            if viewModel.isLoading {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                    .padding()
                    .background(Color.backgroundMedium.opacity(0.85))
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
            }
        }
        .overlay(alignment: .bottom) {
            if let error = viewModel.errorMessage {
                errorBanner(message: error)
                    .padding(.bottom, Spacing.l)
            }
        }
        .withVisualLogger()
        .onAppear {
            VisualLogger.shared.log("👀 AnalyticsScreen onAppear", level: .info, category: "ANALYTICS.UI")
            guard !didStartInitialLoad else { return }
            didStartInitialLoad = true
            Task { await viewModel.load() }
        }
        .onDisappear {
            VisualLogger.shared.log("👋 AnalyticsScreen onDisappear", level: .info, category: "ANALYTICS.UI")
            Task { @MainActor in
                viewModel.cancelAll(reason: "screen_disappear")
            }
        }
        .onChange(of: viewModel.isLoading) { isLoading in
            VisualLogger.shared.log("⏳ analytics_loading = \(isLoading)", level: .info, category: "ANALYTICS.UI")
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("analytics_title"),
            subtitle: localizationManager.localized("analytics_subtitle"),
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [
                NavigationActionButton(
                    icon: "slider.horizontal.3",
                    accessibilityLabel: localizationManager.localized("analytics_settings_button"),
                    action: {
                        logger.buttonTap("Analytics Settings", screen: "Analytics")
                        showAnalyticsSettings = true
                    }
                )
            ],
            onBack: {
                logger.buttonTap("Back", screen: "Analytics")
                navigationManager.goBack()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("analytics_accessibility_navbar"))
    }
    
    // MARK: - Data Source Indicator
    
    /// ✅ ВАРИАНТ 4: Индикатор источника данных
    @ViewBuilder
    private var dataSourceIndicator: some View {
        HStack(spacing: Spacing.xs) {
            switch viewModel.dataSource {
            case .api:
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
                Text(localizationManager.localized("analytics_data_source_api") ?? "Реальные данные")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .cache:
                Image(systemName: "clock.fill")
                    .foregroundColor(.orange)
                Text(localizationManager.localized("analytics_data_source_cache") ?? "Данные из кэша")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .empty:
                Image(systemName: "circle")
                    .foregroundColor(.gray)
                Text(localizationManager.localized("analytics_data_source_empty") ?? "Нет данных")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .error:
                Image(systemName: "exclamationmark.triangle.fill")
                    .foregroundColor(.red)
                Text(localizationManager.localized("analytics_data_source_error") ?? "Ошибка загрузки")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(.horizontal, Spacing.m)
        .padding(.vertical, Spacing.xs)
        .background(Color.backgroundMedium.opacity(0.5))
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
    }
    
    // MARK: - Main Stats (компактные карточки в 1 строку)
    
    private var mainStats: some View {
        HStack(spacing: Spacing.s) {
            compactStatCard(
                icon: "shield.fill",
                value: "\(viewModel.threatsBlocked)",
                label: localizationManager.localized("analytics_blocked_short")
            )
            
            compactStatCard(
                icon: "magnifyingglass",
                value: "\(viewModel.itemsScanned)",
                label: localizationManager.localized("analytics_scanned_short")
            )
            
            compactStatCard(
                icon: "exclamationmark.triangle.fill",
                value: "\(viewModel.threatsDetected)",
                label: localizationManager.localized("analytics_detected_short")
            )
            
            compactStatCard(
                icon: "percent",
                value: effectivenessText,
                label: localizationManager.localized("analytics_effectiveness_short")
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Threat Breakdown
    
    private var threatBreakdown: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_detailed_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                if viewModel.isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, Spacing.l)
                } else if viewModel.threatCategories.isEmpty {
                    // ✅ ВАРИАНТ 4: Показываем сообщение "Нет данных" вместо бесконечной загрузки
                    Text(localizationManager.localized("analytics_no_threats") ?? "Нет данных об угрозах")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, Spacing.l)
                } else {
                    ForEach(Array(viewModel.threatCategories.enumerated()), id: \.element.id) { index, category in
                        threatRow(for: category, color: colorForThreat(at: index))
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Protection Block

    private var protectionBlock: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_protection"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)

            VStack(alignment: .leading, spacing: Spacing.s) {
                ProgressView(value: min(max(viewModel.protectionLevel / 100.0, 0), 1))
                    .progressViewStyle(.linear)
                    .tint(.primaryBlue)

                HStack {
                    Text(localizationManager.localized("analytics_protected"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("\(Int(viewModel.protectionLevel))%")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }

    // MARK: - Helper Views
    private func threatRow(for category: ThreatTypeCount, color: Color) -> some View {
        detailRow(
            icon: category.icon ?? iconName(for: category.type),
            title: localizedThreatTitle(for: category.type),
            value: "\(category.count)",
            color: color
        )
    }
    
    private func iconName(for type: String) -> String {
        switch type.lowercased() {
        case "web": return "globe"
        case "file": return "doc"
        case "app": return "iphone"
        case "network": return "shield"
        default: return "shield"
        }
    }
    
    private func localizedThreatTitle(for type: String) -> String {
        switch type.lowercased() {
        case "web": return localizationManager.localized("analytics_web_threats")
        case "file": return localizationManager.localized("analytics_file_threats")
        case "network": return localizationManager.localized("analytics_network_threats")
        case "app": return localizationManager.localized("analytics_app_threats")
        default: return type.capitalized
        }
    }
    
    private func colorForThreat(at index: Int) -> Color {
        let palette: [Color] = [.dangerRed, .warningOrange, .primaryBlue, .successGreen]
        return index < palette.count ? palette[index] : .primaryBlue
    }
    
    private func compactStatCard(icon: String, value: String, label: String) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 18))
                .foregroundColor(.primaryBlue)
            
            Text(value)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.textPrimary)
                .lineLimit(1)
            
            Text(label)
                .font(.system(size: 10))
                .foregroundColor(.textSecondary)
                .lineLimit(1)
                .minimumScaleFactor(0.7)  // ✅ ПУНКТ 1,2: Автоматическое уменьшение шрифта для предотвращения обрезания
                .fixedSize(horizontal: false, vertical: true)  // ✅ ПУНКТ 1,2: Предотвращение обрезания текста
                .frame(maxWidth: .infinity)  // ✅ ПУНКТ 2: Выравнивание по ширине
                .multilineTextAlignment(.center)  // ✅ ПУНКТ 2: Центрирование текста
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: localizationManager.localized("analytics_accessibility_stat_value"),
                label,
                value
            )
        )
    }
    
    private func detailRow(icon: String, title: String, value: String, color: Color) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(color)
                .frame(width: 24)
            
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            
            Spacer()
            
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: localizationManager.localized("analytics_accessibility_stat_value"),
                title,
                value
            )
        )
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    private var effectivenessText: String {
        guard viewModel.threatsDetected > 0 else { return "0%" }
        let ratio = Double(viewModel.threatsBlocked) / Double(viewModel.threatsDetected)
        let percent = Int(max(0, min(100, round(ratio * 100))))
        return "\(percent)%"
    }
    
    private func errorBanner(message: String) -> some View {
        Text(message)
            .font(.footnote)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(Color.dangerRed.opacity(0.9))
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .shadow(radius: 6)
    }
    
    // MARK: - Component Real Data Helpers
    
    /// ✅ ВАРИАНТ 4: Получить реальные метрики компонента
    private func getRealMetrics(for componentId: String) -> [(String, String)] {
        guard let components = viewModel.componentsAnalytics,
              let stats = components.getStats(for: componentId) else {
            // Fallback на пустые данные
            return getEmptyMetrics(for: componentId)
        }
        
        // Преобразуем метрики компонента в формат для UI
        switch componentId {
        case "driving_reports_agent":
            return [
                (localizationManager.localized("component_driving_reports_metric_trips"), stats.getMetric(key: "trips")),
                (localizationManager.localized("component_driving_reports_metric_safety"), "\(stats.getMetric(key: "safety_score"))/10")
            ]
        case "dark_web_monitoring_agent":
            return [
                (localizationManager.localized("component_dark_web_metric_leaks"), stats.getMetric(key: "leaks_found")),
                (localizationManager.localized("component_dark_web_metric_new"), stats.getMetric(key: "new_leaks"))
            ]
        case "russian_identity_theft_protection_agent":
            return [
                (localizationManager.localized("component_identity_theft_metric_attempts"), stats.getMetric(key: "attempts")),
                (localizationManager.localized("component_identity_theft_metric_blocked"), stats.getMetric(key: "blocked"))
            ]
        case "location_bubble_agent":
            return [
                (localizationManager.localized("component_location_bubble_metric_blocked"), stats.getMetric(key: "blocked")),
                (localizationManager.localized("component_location_bubble_metric_accuracy"), stats.getMetric(key: "accuracy"))
            ]
        case "personal_data_cleanup_agent":
            let freedGB = stats.getMetric(key: "freed_space_gb")
            let hoursAgo = stats.getIntMetric(key: "last_cleanup_hours_ago")
            let timeAgo = hoursAgo > 0 ? "\(hoursAgo)ч назад" : "Недавно"
            return [
                (localizationManager.localized("component_data_cleanup_metric_freed"), "\(freedGB) ГБ"),
                (localizationManager.localized("component_data_cleanup_metric_last"), timeAgo)
            ]
        case "anti_tracker_agent":
            let total = stats.getIntMetric(key: "blocked_total")
            let week = stats.getIntMetric(key: "blocked_this_week")
            return [
                (localizationManager.localized("component_anti_tracker_metric_blocked"), formatNumber(total)),
                (localizationManager.localized("component_anti_tracker_metric_week"), "+\(week)")
            ]
        case "ai_categories_agent":
            return [
                (localizationManager.localized("component_ai_categories_metric_categorized"), stats.getMetric(key: "categorized")),
                (localizationManager.localized("component_ai_categories_metric_blocked"), stats.getMetric(key: "blocked"))
            ]
        default:
            return getEmptyMetrics(for: componentId)
        }
    }
    
    /// ✅ ВАРИАНТ 4: Получить реальный badgeCount компонента
    private func getRealBadgeCount(for componentId: String) -> Int? {
        guard let components = viewModel.componentsAnalytics,
              let stats = components.getStats(for: componentId) else {
            return nil
        }
        
        // Возвращаем количество новых событий как badgeCount
        switch componentId {
        case "driving_reports_agent":
            let count = stats.getIntMetric(key: "new_events")
            return count > 0 ? count : nil
        case "dark_web_monitoring_agent":
            let count = stats.getIntMetric(key: "new_events")
            return count > 0 ? count : nil
        default:
            return nil
        }
    }
    
    /// Получить пустые метрики для компонента (fallback)
    private func getEmptyMetrics(for componentId: String) -> [(String, String)] {
        switch componentId {
        case "driving_reports_agent":
            return [
                (localizationManager.localized("component_driving_reports_metric_trips"), "0"),
                (localizationManager.localized("component_driving_reports_metric_safety"), "0.0/10")
            ]
        case "dark_web_monitoring_agent":
            return [
                (localizationManager.localized("component_dark_web_metric_leaks"), "0"),
                (localizationManager.localized("component_dark_web_metric_new"), "0")
            ]
        case "russian_identity_theft_protection_agent":
            return [
                (localizationManager.localized("component_identity_theft_metric_attempts"), "0"),
                (localizationManager.localized("component_identity_theft_metric_blocked"), "0")
            ]
        case "location_bubble_agent":
            return [
                (localizationManager.localized("component_location_bubble_metric_blocked"), "0"),
                (localizationManager.localized("component_location_bubble_metric_accuracy"), "Нет данных")
            ]
        case "personal_data_cleanup_agent":
            return [
                (localizationManager.localized("component_data_cleanup_metric_freed"), "0.0 ГБ"),
                (localizationManager.localized("component_data_cleanup_metric_last"), "Нет данных")
            ]
        case "anti_tracker_agent":
            return [
                (localizationManager.localized("component_anti_tracker_metric_blocked"), "0"),
                (localizationManager.localized("component_anti_tracker_metric_week"), "0")
            ]
        case "ai_categories_agent":
            return [
                (localizationManager.localized("component_ai_categories_metric_categorized"), "0"),
                (localizationManager.localized("component_ai_categories_metric_blocked"), "0")
            ]
        default:
            return []
        }
    }
    
    /// Форматировать число с разделителями тысяч
    private func formatNumber(_ number: Int) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.groupingSeparator = ","
        return formatter.string(from: NSNumber(value: number)) ?? "\(number)"
    }
    
    // MARK: - Components Reports Section (НОВОЕ)
    
    private var componentsReportsSection: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_components_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                // ✅ ВАРИАНТ 4: Отчеты о вождении (реальные данные)
                componentReportCard(
                    componentId: "driving_reports_agent",
                    icon: "🚗",
                    titleKey: "component_driving_reports_title",
                    metrics: getRealMetrics(for: "driving_reports_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "driving_reports_agent"),
                    onTap: { showDrivingReportsModal = true }
                )
                
                // ✅ ВАРИАНТ 4: Мониторинг Дарк вэб (реальные данные)
                componentReportCard(
                    componentId: "dark_web_monitoring_agent",
                    icon: "🌑",
                    titleKey: "component_dark_web_title",
                    metrics: getRealMetrics(for: "dark_web_monitoring_agent"),
                    color: .dangerRed,
                    badgeCount: getRealBadgeCount(for: "dark_web_monitoring_agent"),
                    onTap: { showDarkWebMonitoringModal = true }
                )
                
                // ✅ ВАРИАНТ 4: Защита кражи личности (реальные данные)
                componentReportCard(
                    componentId: "russian_identity_theft_protection_agent",
                    icon: "🛡️",
                    titleKey: "component_identity_theft_title",
                    metrics: getRealMetrics(for: "russian_identity_theft_protection_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "russian_identity_theft_protection_agent"),
                    onTap: { showIdentityTheftModal = true }
                )
                
                // ✅ ВАРИАНТ 4: Пузырь местоположения (реальные данные)
                componentReportCard(
                    componentId: "location_bubble_agent",
                    icon: "📍",
                    titleKey: "component_location_bubble_title",
                    metrics: getRealMetrics(for: "location_bubble_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "location_bubble_agent"),
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // ✅ ВАРИАНТ 4: Очистка данных (реальные данные)
                componentReportCard(
                    componentId: "personal_data_cleanup_agent",
                    icon: "🧹",
                    titleKey: "component_data_cleanup_title",
                    metrics: getRealMetrics(for: "personal_data_cleanup_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "personal_data_cleanup_agent"),
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // ✅ ВАРИАНТ 4: Блокировка трекеров (реальные данные)
                componentReportCard(
                    componentId: "anti_tracker_agent",
                    icon: "🚫",
                    titleKey: "component_anti_tracker_title",
                    metrics: getRealMetrics(for: "anti_tracker_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "anti_tracker_agent"),
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // ✅ ВАРИАНТ 4: AI категоризация (реальные данные)
                componentReportCard(
                    componentId: "ai_categories_agent",
                    icon: "🤖",
                    titleKey: "component_ai_categories_title",
                    metrics: getRealMetrics(for: "ai_categories_agent"),
                    color: .primaryBlue,
                    badgeCount: getRealBadgeCount(for: "ai_categories_agent"),
                    onTap: { showAICategoriesModal = true }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Component Report Cards
    
    private func componentReportCard(
        componentId: String,
        icon: String,
        titleKey: String,
        metrics: [(String, String)],
        color: Color,
        badgeCount: Int?,
        onTap: @escaping () -> Void
    ) -> some View {
        ComponentReportCard(
            componentId: componentId,
            icon: icon,
            title: localizationManager.localized(titleKey),
            metrics: metrics,
            color: color,
            badgeCount: badgeCount,
            onTap: onTap
        )
    }
}

// MARK: - Debounced Indicator
private struct DebouncedDataSourceIndicator: View {
    let dataSource: DataSource
    @ObservedObject var localizationManager: LocalizationManager
    @State private var displayed: DataSource = .empty
    @State private var pendingTask: Task<Void, Never>?
    
    var body: some View {
        HStack(spacing: Spacing.xs) {
            switch displayed {
            case .api:
                Image(systemName: "checkmark.circle.fill").foregroundColor(.green)
                Text(localizationManager.localized("analytics_data_source_api") ?? "Реальные данные")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .cache:
                Image(systemName: "clock.fill").foregroundColor(.orange)
                Text(localizationManager.localized("analytics_data_source_cache") ?? "Кэш")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .empty:
                Image(systemName: "circle").foregroundColor(.gray)
                Text(localizationManager.localized("analytics_data_source_empty") ?? "Нет данных")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            case .error:
                Image(systemName: "exclamationmark.triangle.fill").foregroundColor(.red)
                Text(localizationManager.localized("analytics_data_source_error") ?? "Ошибка загрузки")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(.horizontal, Spacing.m)
        .padding(.vertical, Spacing.xs)
        .background(Color.backgroundMedium.opacity(0.5))
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        .onAppear { displayed = dataSource }
        .onChange(of: dataSource) { newValue in
            pendingTask?.cancel()
            // Дебаунс 0.5s
            pendingTask = Task { @MainActor in
                try? await Task.sleep(nanoseconds: 500_000_000)
                displayed = newValue
            }
        }
    }
}

private extension AnalyticsScreen {
    /// ✅ ИСПРАВЛЕНО: Всегда используем RemoteAnalyticsService для реальных данных
    static func makeViewModel() -> AnalyticsViewModel {
        // ✅ ИСПРАВЛЕНО: Всегда используем RemoteAnalyticsService, даже в DEBUG режиме
        // Это гарантирует, что мы используем реальный API и видим ошибки вместо MOCK данных
        let service: AnalyticsService = RemoteAnalyticsService()
        
        #if DEBUG
        print("📊 AnalyticsScreen: Используется RemoteAnalyticsService (всегда реальный API)")
        #endif
        
        return AnalyticsViewModel(service: service)
    }
}

// MARK: - Preview

