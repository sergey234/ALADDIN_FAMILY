import SwiftUI
import Foundation

// ✅ Импортируем EnvironmentConfig для переключения сервисов
// Файл находится в Core/Config/EnvironmentConfig.swift

/// 📊 Analytics Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showDetailsModal: Bool = false
    @State private var selectedStatsType: StatsType = .security
    @State private var showFilters: Bool = false
    @StateObject private var viewModel = AnalyticsScreen.makeViewModel()
    
    private func periodTitle(_ period: AnalyticsViewModel.TimePeriod) -> String {
        switch period {
        case .day: return localizationManager.localized("analytics_period_day")
        case .week: return localizationManager.localized("analytics_period_week")
        case .month: return localizationManager.localized("analytics_period_month")
        }
    }
    
    enum StatsType: String, CaseIterable {
        case security
        case family
        case usage
        case devices
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .security: return localizationManager.localized("analytics_stats_security")
            case .family: return localizationManager.localized("analytics_stats_family")
            case .usage: return localizationManager.localized("analytics_stats_usage")
            case .devices: return localizationManager.localized("analytics_stats_devices")
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана аналитики")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Компактные карточки в 1 строку
                        mainStats
                        
                        // Селектор периода
                        periodSelector
                        
                        // Детальная статистика
                        detailedStats
                        
                        // Кнопка подробной статистики
                        detailsButton
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Статистика защиты и угроз")
            }
        }
        .navigationBarHidden(true)
        .task { await viewModel.load() }
        .sheet(isPresented: $showDetailsModal) {
            DetailedStatsModal(selectedType: $selectedStatsType, viewModel: viewModel)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showFilters) {
            AnalyticsFiltersSheet(isPresented: $showFilters) { filters in
                Task { await viewModel.apply(filters: filters) }
            }
            .environmentObject(localizationManager)
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("analytics_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "АНАЛИТИКА",
            subtitle: "Статистика защиты",
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [
                .init(icon: "line.3.horizontal.decrease.circle", accessibilityLabel: "Фильтры") {
                    showFilters = true
                }
            ],
            onBack: {
                navigationManager.goBack()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель аналитики")
    }
    
    // MARK: - Main Stats (компактные карточки в 1 строку)
    
    private var mainStats: some View {
        HStack(spacing: Spacing.s) {
            compactStatCard(
                icon: "shield.fill",
                value: "\(viewModel.threatsBlocked)",
                label: "Заблок."
            )
            
            compactStatCard(
                icon: "magnifyingglass",
                value: "\(viewModel.itemsScanned)",
                label: "Проска."
            )
            
            compactStatCard(
                icon: "exclamationmark.triangle.fill",
                value: "\(viewModel.threatsDetected)",
                label: "Обнаруж."
            )
            
            compactStatCard(
                icon: "percent",
                value: "\(viewModel.threatsDetected == 0 ? 0 : Int(Double(viewModel.threatsBlocked) / Double(viewModel.threatsDetected) * 100))%",
                label: "Эффект."
            )
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Period Selector
    
    private var periodSelector: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_period"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.s) {
                ForEach(AnalyticsViewModel.TimePeriod.allCases, id: \.self) { period in
                    Button(action: {
                        Task { await viewModel.changePeriod(period) }
                    }) {
                        Text(periodTitle(period))
                            .font(.body)
                            .foregroundColor(viewModel.selectedPeriod == period ? .white : .textPrimary)
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(viewModel.selectedPeriod == period ? Color.primaryBlue : Color.backgroundMedium)
                            )
                    }
                    .accessibilityLabel("Период: \(periodTitle(period))")
                    .accessibilityAddTraits(viewModel.selectedPeriod == period ? .isSelected : [])
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Details Button
    
    private var detailsButton: some View {
        Button(action: {
            showDetailsModal = true
        }) {
            HStack {
                Text(localizationManager.localized("analytics_detailed_stats"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 16))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.cardPadding)
            .background(cardBackground)
            .cardShadow()
        }
    }
    
    // MARK: - Detailed Stats
    
    private var detailedStats: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_detailed_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                detailRow(
                    icon: "globe",
                    title: "Веб-угрозы",
                    value: "\(Int(Double(max(0, viewModel.threatsDetected)) * 0.4))",
                    color: .dangerRed
                )
                
                detailRow(
                    icon: "doc",
                    title: "Файловые угрозы",
                    value: "\(Int(Double(max(0, viewModel.threatsDetected)) * 0.3))",
                    color: .warningOrange
                )
                
                detailRow(
                    icon: "network",
                    title: "Сетевые угрозы",
                    value: "\(Int(Double(max(0, viewModel.threatsDetected)) * 0.2))",
                    color: .primaryBlue
                )
                
                detailRow(
                    icon: "app",
                    title: "Угрозы приложений",
                    value: "\(Int(Double(max(0, viewModel.threatsDetected)) * 0.1))",
                    color: .successGreen
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
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
        .accessibilityLabel("\(label): \(value)")
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
        .accessibilityLabel("\(title): \(value)")
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

private extension AnalyticsScreen {
    static func makeViewModel() -> AnalyticsViewModel {
        // ✅ Используем локальный сервис по умолчанию
        // В будущем можно добавить переключение через EnvironmentConfig
        return AnalyticsViewModel(service: LocalAnalyticsService())
    }
}

// MARK: - Preview

// MARK: - Detailed Stats Modal

struct DetailedStatsModal: View {
    @Binding var selectedType: AnalyticsScreen.StatsType
    @ObservedObject var viewModel: AnalyticsViewModel
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                ALADDINNavigationBar(
                    title: localizationManager.localized("analytics_detailed_stats_title"),
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    rightButtons: [],
                    onBack: { dismiss() }
                )
                
                // Content
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Tabs
                        tabsView
                        
                        // Content based on selected type
                        contentView
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
            }
        }
    }
    
    private var tabsView: some View {
        HStack(spacing: Spacing.xs) {
            ForEach(AnalyticsScreen.StatsType.allCases, id: \.self) { type in
                Button(action: {
                    selectedType = type
                }) {
                    VStack(spacing: 4) {
                        Text(getEmoji(for: type))
                            .font(.system(size: 18))
                        Text(type.title(localizationManager: localizationManager))
                            .font(.system(size: 10, weight: .semibold))
                            .lineLimit(1)
                            .minimumScaleFactor(0.6)
                            .allowsTightening(true)
                    }
                    .foregroundColor(selectedType == type ? .white : .textPrimary)
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, Spacing.xs)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(selectedType == type ? Color.primaryBlue : Color.backgroundMedium)
                    )
                }
                .accessibilityLabel("Таб \(type.title(localizationManager: localizationManager))")
                .accessibilityAddTraits(selectedType == type ? .isSelected : [])
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var contentView: some View {
        Group {
            switch selectedType {
            case .security:
                securityContent
            case .family:
                familyContent
            case .usage:
                usageContent
            case .devices:
                devicesContent
            }
        }
    }
    
    private var securityContent: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            securityBlockedThreats
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            securityRecentThreats
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            securityVPNStats
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var securityBlockedThreats: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_blocked_threats"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let blocked = viewModel.securityAnalytics?.blockedThreats {
                ForEach(blocked) { threat in
                    statRow(title: threat.type, value: "\(threat.count)", icon: threat.icon)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
        .task {
            if viewModel.securityAnalytics == nil {
                await viewModel.loadSecurityAnalytics()
            }
        }
    }
    
    private var securityRecentThreats: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_recent_threats"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let recent = viewModel.securityAnalytics?.recentThreats {
                ForEach(recent) { threat in
                    recentThreatRow(emoji: threat.emoji, text: threat.text, time: threat.time)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var securityVPNStats: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_vpn_traffic"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let vpn = viewModel.securityAnalytics?.vpnStats {
                statRow(title: "Сегодня", value: vpn.today, icon: "📊")
                statRow(title: "За неделю", value: vpn.week, icon: "📊")
                statRow(title: "Защищено", value: vpn.protection, icon: "✅")
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var familyContent: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            familyMembersSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            familyThreatsSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            familyRecentActivity
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var familyMembersSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_family_activity"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let members = viewModel.familyAnalytics?.membersActivity {
                ForEach(members) { member in
                    familyMemberRow(emoji: member.emoji, name: member.name, time: member.time, percent: member.percent)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
        .task {
            if viewModel.familyAnalytics == nil {
                await viewModel.loadFamilyAnalytics()
            }
        }
    }
    
    private var familyThreatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_blocked_threats_count"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let threats = viewModel.familyAnalytics?.threatsByMember {
                ForEach(threats) { threat in
                    familyThreatRow(emoji: threat.emoji, name: threat.name, count: "\(threat.count)", warning: threat.warning ?? "")
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var familyRecentActivity: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_recent_activity"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let activities = viewModel.familyAnalytics?.recentActivity {
                ForEach(activities) { activity in
                    recentActivityRow(emoji: activity.emoji, member: activity.member, activity: activity.activity, time: activity.time)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var usageContent: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            usageTimeSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            usageTopAppsSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            usageTopSitesSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            usageTotalTraffic
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var usageTimeSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_activity_by_hours"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let times = viewModel.usageAnalytics?.activityByTime {
                ForEach(times) { time in
                    usageTimeRow(emoji: time.emoji, period: time.period, time: time.time, percent: time.percent)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var usageTopAppsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_top_5_apps"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let apps = viewModel.usageAnalytics?.topApps {
                ForEach(apps) { app in
                    topAppRow(rank: "\(app.rank)", name: app.name, time: app.time)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
        .task {
            if viewModel.usageAnalytics == nil {
                await viewModel.loadUsageAnalytics()
            }
        }
    }
    
    private var usageTopSitesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_top_5_sites"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let sites = viewModel.usageAnalytics?.topSites {
                ForEach(sites) { site in
                    topSiteRow(rank: "\(site.rank)", url: site.url, visits: site.visits)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var usageTotalTraffic: some View {
        HStack {
            Text(localizationManager.localized("analytics_total_traffic"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(viewModel.usageAnalytics?.totalTraffic ?? localizationManager.localized("analytics_loading"))
                .font(.bodyBold)
                .foregroundColor(.primaryBlue)
        }
    }
    
    private var devicesContent: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            devicesActivitySection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            devicesThreatsSection
            
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.m)
            
            devicesStatusSection
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var devicesActivitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_activity_by_devices"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let devices = viewModel.devicesAnalytics?.deviceActivity {
                ForEach(devices) { device in
                    deviceRow(emoji: device.emoji, name: device.name, time: device.time, percent: device.percent)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
        .task {
            if viewModel.devicesAnalytics == nil {
                await viewModel.loadDevicesAnalytics()
            }
        }
    }
    
    private var devicesThreatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_threats_by_devices"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let threats = viewModel.devicesAnalytics?.threatsByDevice {
                ForEach(threats) { threat in
                    deviceThreatRow(emoji: threat.emoji, name: threat.name, count: "\(threat.count) блок.")
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    private var devicesStatusSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("analytics_status"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            if let status = viewModel.devicesAnalytics?.status {
                HStack {
                    Text(localizationManager.localized("analytics_online"))
                        .foregroundColor(.successGreen)
                    Spacer()
                    Text("\(status.online) \(localizationManager.localized("analytics_devices"))")
                }
                HStack {
                    Text(localizationManager.localized("analytics_offline"))
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("\(status.offline) \(localizationManager.localized("analytics_devices"))")
                }
                HStack {
                    Text(localizationManager.localized("analytics_protection"))
                        .foregroundColor(.primaryBlue)
                    Spacer()
                    Text(status.protection)
                }
            } else {
                Text(localizationManager.localized("analytics_loading"))
                    .foregroundColor(.textSecondary)
                    .padding(.vertical, Spacing.s)
            }
        }
    }
    
    // MARK: - Helper Functions
    
    private func getEmoji(for type: AnalyticsScreen.StatsType) -> String {
        switch type {
        case .security: return "🛡️"
        case .family: return "👨‍👩‍👧‍👦"
        case .usage: return "📊"
        case .devices: return "📱"
        }
    }
    
    private func statRow(title: String, value: String, icon: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(icon)
                .frame(width: 24)
            Text(title)
                .font(.system(size: 13))
                .foregroundColor(.textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.85)
                .allowsTightening(true)
            Spacer(minLength: 8)
            Text(value)
                .font(.system(size: 13, weight: .bold))
                .foregroundColor(.textPrimary)
                .monospacedDigit()
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func recentThreatRow(emoji: String, text: String, time: String) -> some View {
        HStack {
            Text(emoji)
            Text(text)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func familyMemberRow(emoji: String, name: String, time: String, percent: Int) -> some View {
        HStack {
            Text(emoji)
            Text(name)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textPrimary)
                .bold()
            Text("(\(percent)%)")
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func familyThreatRow(emoji: String, name: String, count: String, warning: String = "") -> some View {
        HStack {
            Text(emoji)
            Text(name)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(count)
                .foregroundColor(.textPrimary)
                .bold()
            if !warning.isEmpty {
                Text(warning)
            }
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func recentActivityRow(emoji: String, member: String, activity: String, time: String) -> some View {
        HStack {
            Text(emoji)
            Text("\(member) → \(activity)")
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func usageTimeRow(emoji: String, period: String, time: String, percent: Int) -> some View {
        HStack {
            Text(emoji)
            Text(period)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textPrimary)
                .bold()
            Text("(\(percent)%)")
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func topAppRow(rank: String, name: String, time: String) -> some View {
        HStack {
            Text(rank + ".")
                .foregroundColor(.primaryBlue)
                .bold()
            Text(name)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textPrimary)
                .bold()
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func topSiteRow(rank: String, url: String, visits: String) -> some View {
        HStack {
            Text(rank + ".")
                .foregroundColor(.primaryBlue)
                .bold()
            Text(url)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(visits)
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func deviceRow(emoji: String, name: String, time: String, percent: Int) -> some View {
        HStack {
            Text(emoji)
            Text(name)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(time)
                .foregroundColor(.textPrimary)
                .bold()
            Text("(\(percent)%)")
                .foregroundColor(.textSecondary)
                .font(.caption)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    private func deviceThreatRow(emoji: String, name: String, count: String) -> some View {
        HStack {
            Text(emoji)
            Text(name)
                .foregroundColor(.textPrimary)
            Spacer()
            Text(count)
                .foregroundColor(.textPrimary)
                .bold()
        }
        .padding(.vertical, Spacing.xs)
    }
}

// MARK: - Preview

struct AnalyticsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsScreen()
            .environmentObject(NavigationManager())
    }
}

// MARK: - Filters Sheet (Simple placeholder to make the button work)

struct AnalyticsFiltersSheet: View {
    @Binding var isPresented: Bool
    var onApply: (AnalyticsFilters) -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var selectedPeriod: Int = 1 // 0: День, 1: Неделя, 2: Месяц (резерв на будущее)
    @State private var showOnlyBlocked: Bool = true
    @State private var includeFamily: Bool = true
    @State private var includeDevices: Bool = true
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("analytics_period"))) {
                    Picker(localizationManager.localized("analytics_period"), selection: $selectedPeriod) {
                        Text(localizationManager.localized("analytics_period_day")).tag(0)
                        Text(localizationManager.localized("analytics_period_week")).tag(1)
                        Text(localizationManager.localized("analytics_period_month")).tag(2)
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }
                Section(header: Text(localizationManager.localized("analytics_filters"))) {
                    Toggle("Только заблокированные", isOn: $showOnlyBlocked)
                    Toggle("Учитывать семью", isOn: $includeFamily)
                    Toggle("Учитывать устройства", isOn: $includeDevices)
                }
            }
            .navigationTitle(localizationManager.localized("analytics_filters"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") { isPresented = false }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Применить") {
                        let filters = AnalyticsFilters(
                            onlyBlocked: showOnlyBlocked,
                            includeFamily: includeFamily,
                            includeDevices: includeDevices
                        )
                        onApply(filters)
                        isPresented = false
                    }
                }
            }
        }
    }
}
