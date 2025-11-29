import SwiftUI

/// 📊 Analytics Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var selectedPeriod: TimePeriod = .week
    @State private var showDetailsModal: Bool = false
    @State private var selectedStatsType: StatsType = .security
    @State private var showFilters: Bool = false
    
    enum TimePeriod: String, CaseIterable {
        case day = "День"
        case week = "Неделя"
        case month = "Месяц"
        
        var stats: (threats: Int, blocked: Int, scanned: Int) {
            switch self {
            case .day: return (12, 12, 847)
            case .week: return (47, 45, 5_234)
            case .month: return (189, 185, 21_890)
            }
        }
    }
    
    enum StatsType: String, CaseIterable {
        case security = "Безопасность"
        case family = "Семья"
        case usage = "Использование"
        case devices = "Устройства"
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
        .sheet(isPresented: $showDetailsModal) {
            DetailedStatsModal(selectedType: $selectedStatsType)
        }
        .sheet(isPresented: $showFilters) {
            AnalyticsFiltersSheet(isPresented: $showFilters)
        }
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
                value: "\(selectedPeriod.stats.blocked)",
                label: "Заблок."
            )
            
            compactStatCard(
                icon: "magnifyingglass",
                value: "\(selectedPeriod.stats.scanned)",
                label: "Проска."
            )
            
            compactStatCard(
                icon: "exclamationmark.triangle.fill",
                value: "\(selectedPeriod.stats.threats)",
                label: "Обнаруж."
            )
            
            compactStatCard(
                icon: "percent",
                value: "\(Int(Double(selectedPeriod.stats.blocked) / Double(selectedPeriod.stats.threats) * 100))%",
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
            Text("ПЕРИОД")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.s) {
                ForEach(TimePeriod.allCases, id: \.self) { period in
                    Button(action: {
                        selectedPeriod = period
                    }) {
                        Text(period.rawValue)
                            .font(.body)
                            .foregroundColor(selectedPeriod == period ? .white : .textPrimary)
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(selectedPeriod == period ? Color.primaryBlue : Color.backgroundMedium)
                            )
                    }
                    .accessibilityLabel("Период: \(period.rawValue)")
                    .accessibilityAddTraits(selectedPeriod == period ? .isSelected : [])
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
                Text("📊 Подробная статистика")
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
            Text("ДЕТАЛЬНАЯ СТАТИСТИКА")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                detailRow(
                    icon: "globe",
                    title: "Веб-угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.4))",
                    color: .dangerRed
                )
                
                detailRow(
                    icon: "doc",
                    title: "Файловые угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.3))",
                    color: .warningOrange
                )
                
                detailRow(
                    icon: "network",
                    title: "Сетевые угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.2))",
                    color: .primaryBlue
                )
                
                detailRow(
                    icon: "app",
                    title: "Угрозы приложений",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.1))",
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

// MARK: - Preview

// MARK: - Detailed Stats Modal

struct DetailedStatsModal: View {
    @Binding var selectedType: AnalyticsScreen.StatsType
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                ALADDINNavigationBar(
                    title: "ПОДРОБНАЯ СТАТИСТИКА",
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
                        Text(type.rawValue)
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
                .accessibilityLabel("Таб \(type.rawValue)")
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
            Text("🛡️ ЗАБЛОКИРОВАННЫЕ УГРОЗЫ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            statRow(title: "Фишинговые сайты", value: "542", icon: "🌐")
            statRow(title: "Вредоносные файлы", value: "318", icon: "📁")
            statRow(title: "Подозрительные приложения", value: "187", icon: "📱")
            statRow(title: "Опасные ссылки", value: "200", icon: "🔗")
        }
    }
    
    private var securityRecentThreats: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("ПОСЛЕДНИЕ УГРОЗЫ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            recentThreatRow(emoji: "✅", text: "Фишинговый сайт", time: "2 мин назад")
            recentThreatRow(emoji: "⚠️", text: "Подозрительное приложение", time: "15 мин")
            recentThreatRow(emoji: "🚫", text: "Вредоносный файл", time: "1 час назад")
        }
    }
    
    private var securityVPNStats: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📈 ТРАФИК ЧЕРЕЗ VPN")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            statRow(title: "Сегодня", value: "2.3 GB", icon: "📊")
            statRow(title: "За неделю", value: "15.8 GB", icon: "📊")
            statRow(title: "Защищено", value: "100%", icon: "✅")
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
            Text("👨‍👩‍👧‍👦 АКТИВНОСТЬ ПО ЧЛЕНАМ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            familyMemberRow(emoji: "👨", name: "Александр", time: "4ч 15м", percent: 35)
            familyMemberRow(emoji: "👩", name: "Елена", time: "3ч 42м", percent: 31)
            familyMemberRow(emoji: "👦", name: "Алексей", time: "2ч 27м", percent: 20)
            familyMemberRow(emoji: "👵", name: "Бабушка", time: "1ч 40м", percent: 14)
        }
    }
    
    private var familyThreatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🛡️ ЗАБЛОКИРОВАНО УГРОЗ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            familyThreatRow(emoji: "👨", name: "Александр", count: "245")
            familyThreatRow(emoji: "👩", name: "Елена", count: "189")
            familyThreatRow(emoji: "👦", name: "Алексей", count: "342", warning: "⚠️")
            familyThreatRow(emoji: "👵", name: "Бабушка", count: "80")
        }
    }
    
    private var familyRecentActivity: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("ПОСЛЕДНЯЯ АКТИВНОСТЬ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            recentActivityRow(emoji: "👦", member: "Алексей", activity: "безопасная игра", time: "5 мин")
            recentActivityRow(emoji: "👧", member: "Мария", activity: "урок безопасности", time: "30 мин")
            recentActivityRow(emoji: "👩", member: "Мама", activity: "родительский контроль", time: "2ч")
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
            Text("⏱️ АКТИВНОСТЬ ПО ЧАСАМ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            usageTimeRow(emoji: "🌅", period: "Утро (6-12)", time: "2ч 15м", percent: 27)
            usageTimeRow(emoji: "☀️", period: "День (12-18)", time: "3ч 42м", percent: 44)
            usageTimeRow(emoji: "🌙", period: "Вечер (18-24)", time: "2ч 27м", percent: 29)
        }
    }
    
    private var usageTopAppsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📱 TOP-5 ПРИЛОЖЕНИЙ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            topAppRow(rank: "1", name: "Instagram", time: "2ч 15м")
            topAppRow(rank: "2", name: "YouTube", time: "1ч 48м")
            topAppRow(rank: "3", name: "WhatsApp", time: "1ч 12м")
            topAppRow(rank: "4", name: "Safari", time: "58мин")
            topAppRow(rank: "5", name: "TikTok", time: "45мин")
        }
    }
    
    private var usageTopSitesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🌐 TOP-5 САЙТОВ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            topSiteRow(rank: "1", url: "youtube.com", visits: "142 визита")
            topSiteRow(rank: "2", url: "vk.com", visits: "89 визитов")
            topSiteRow(rank: "3", url: "google.com", visits: "67 визитов")
            topSiteRow(rank: "4", url: "yandex.ru", visits: "54 визита")
            topSiteRow(rank: "5", url: "mail.ru", visits: "42 визита")
        }
    }
    
    private var usageTotalTraffic: some View {
        HStack {
            Text("📊 Всего трафика:")
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Spacer()
            Text("2.3 GB")
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
            Text("📱 АКТИВНОСТЬ ПО УСТРОЙСТВАМ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            deviceRow(emoji: "📱", name: "iPhone 13 Pro", time: "4ч 15м", percent: 35)
            deviceRow(emoji: "💻", name: "MacBook Pro", time: "3ч 42м", percent: 31)
            deviceRow(emoji: "📱", name: "iPhone 12", time: "2ч 27м", percent: 20)
            deviceRow(emoji: "🖥️", name: "iMac 27\"", time: "1ч 40м", percent: 14)
            deviceRow(emoji: "📲", name: "iPad Air", time: "45мин", percent: 6)
            deviceRow(emoji: "⌚", name: "Apple Watch", time: "15мин", percent: 2)
        }
    }
    
    private var devicesThreatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🛡️ УГРОЗЫ ПО УСТРОЙСТВАМ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            deviceThreatRow(emoji: "📱", name: "iPhone 13 Pro", count: "245 блок.")
            deviceThreatRow(emoji: "💻", name: "MacBook Pro", count: "189 блок.")
            deviceThreatRow(emoji: "📱", name: "iPhone 12", count: "142 блок.")
            deviceThreatRow(emoji: "🖥️", name: "iMac 27\"", count: "198 блок.")
            deviceThreatRow(emoji: "📲", name: "iPad Air", count: "82 блок.")
            deviceThreatRow(emoji: "⌚", name: "Apple Watch", count: "5 блок.")
        }
    }
    
    private var devicesStatusSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("📊 СТАТУС")
                .font(.h3)
                .foregroundColor(.textPrimary)
            HStack {
                Text("✅ Онлайн:")
                    .foregroundColor(.successGreen)
                Spacer()
                Text("4 устройства")
            }
            HStack {
                Text("⭕ Офлайн:")
                    .foregroundColor(.textSecondary)
                Spacer()
                Text("2 устройства")
            }
            HStack {
                Text("🛡️ Защита:")
                    .foregroundColor(.primaryBlue)
                Spacer()
                Text("100%")
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
    @State private var selectedPeriod: Int = 1 // 0: День, 1: Неделя, 2: Месяц
    @State private var showOnlyBlocked: Bool = true
    @State private var includeFamily: Bool = true
    @State private var includeDevices: Bool = true
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Период")) {
                    Picker("Период", selection: $selectedPeriod) {
                        Text("День").tag(0)
                        Text("Неделя").tag(1)
                        Text("Месяц").tag(2)
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }
                Section(header: Text("Фильтры")) {
                    Toggle("Только заблокированные", isOn: $showOnlyBlocked)
                    Toggle("Учитывать семью", isOn: $includeFamily)
                    Toggle("Учитывать устройства", isOn: $includeDevices)
                }
            }
            .navigationTitle("Фильтры")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") { isPresented = false }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Применить") { isPresented = false }
                }
            }
        }
    }
}
