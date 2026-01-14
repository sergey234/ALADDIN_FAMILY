import SwiftUI
import Foundation

/// 📊 Analytics Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = AnalyticsScreen.makeViewModel()
    @State private var showAnalyticsSettings: Bool = false
    
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
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
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
        .task { await viewModel.load() }
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
                    action: { showAnalyticsSettings = true }
                )
            ],
            onBack: {
                navigationManager.goBack()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("analytics_accessibility_navbar"))
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
                if viewModel.threatCategories.isEmpty {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
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
    
    // MARK: - Components Reports Section (НОВОЕ)
    
    private var componentsReportsSection: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_components_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                // Отчеты о вождении
                componentReportCard(
                    componentId: "driving_reports_agent",
                    icon: "🚗",
                    titleKey: "component_driving_reports_title",
                    metrics: [
                        (localizationManager.localized("component_driving_reports_metric_trips"), "12"),
                        (localizationManager.localized("component_driving_reports_metric_safety"), "8.5/10")
                    ],
                    color: .primaryBlue,
                    badgeCount: 3,
                    onTap: { showDrivingReportsModal = true }
                )
                
                // Мониторинг Дарк вэб
                componentReportCard(
                    componentId: "dark_web_monitoring_agent",
                    icon: "🌑",
                    titleKey: "component_dark_web_title",
                    metrics: [
                        (localizationManager.localized("component_dark_web_metric_leaks"), "3"),
                        (localizationManager.localized("component_dark_web_metric_new"), "0")
                    ],
                    color: .dangerRed,
                    badgeCount: 1,
                    onTap: { showDarkWebMonitoringModal = true }
                )
                
                // Защита кражи личности
                componentReportCard(
                    componentId: "russian_identity_theft_protection_agent",
                    icon: "🛡️",
                    titleKey: "component_identity_theft_title",
                    metrics: [
                        (localizationManager.localized("component_identity_theft_metric_attempts"), "0"),
                        (localizationManager.localized("component_identity_theft_metric_blocked"), "47")
                    ],
                    color: .primaryBlue,
                    badgeCount: nil,
                    onTap: { showIdentityTheftModal = true }
                )
                
                // Пузырь местоположения
                componentReportCard(
                    componentId: "location_bubble_agent",
                    icon: "📍",
                    titleKey: "component_location_bubble_title",
                    metrics: [
                        (localizationManager.localized("component_location_bubble_metric_blocked"), "47"),
                        (localizationManager.localized("component_location_bubble_metric_accuracy"), "Средняя")
                    ],
                    color: .primaryBlue,
                    badgeCount: nil,
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // Очистка данных
                componentReportCard(
                    componentId: "personal_data_cleanup_agent",
                    icon: "🧹",
                    titleKey: "component_data_cleanup_title",
                    metrics: [
                        (localizationManager.localized("component_data_cleanup_metric_freed"), "2.3 ГБ"),
                        (localizationManager.localized("component_data_cleanup_metric_last"), "2ч назад")
                    ],
                    color: .primaryBlue,
                    badgeCount: nil,
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // Блокировка трекеров
                componentReportCard(
                    componentId: "anti_tracker_agent",
                    icon: "🚫",
                    titleKey: "component_anti_tracker_title",
                    metrics: [
                        (localizationManager.localized("component_anti_tracker_metric_blocked"), "1,247"),
                        (localizationManager.localized("component_anti_tracker_metric_week"), "+234")
                    ],
                    color: .primaryBlue,
                    badgeCount: nil,
                    onTap: { showPrivacyReportsModal = true }
                )
                
                // AI категоризация
                componentReportCard(
                    componentId: "ai_categories_agent",
                    icon: "🤖",
                    titleKey: "component_ai_categories_title",
                    metrics: [
                        (localizationManager.localized("component_ai_categories_metric_categorized"), "342"),
                        (localizationManager.localized("component_ai_categories_metric_blocked"), "12")
                    ],
                    color: .primaryBlue,
                    badgeCount: nil,
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

private extension AnalyticsScreen {
    static func makeViewModel() -> AnalyticsViewModel {
        let service = RemoteAnalyticsService()
        return AnalyticsViewModel(service: service)
    }
}

// MARK: - Preview

