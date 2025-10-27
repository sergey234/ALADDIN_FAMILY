import SwiftUI

/// 📊 Analytics Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedPeriod: TimePeriod = .week
    @State private var selectedChart: ChartType = .threats
    
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
    
    enum ChartType: String, CaseIterable {
        case threats = "Угрозы"
        case devices = "Устройства"
        case family = "Семья"
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
                        // Общая статистика
                        overallStats
                        
                        // Селектор периода
                        periodSelector
                        
                        // Графики
                        chartsSection
                        
                        // Детальная статистика
                        detailedStats
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Статистика защиты и угроз")
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "АНАЛИТИКА",
            subtitle: "Статистика защиты",
            showBackButton: true,
            rightButtons: [
                .init(icon: "line.3.horizontal.decrease.circle", accessibilityLabel: "Фильтры") {
                    print("Фильтры")
                }
            ],
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель аналитики")
    }
    
    // MARK: - Overall Stats
    
    private var overallStats: some View {
        VStack(spacing: Spacing.m) {
            Text("📊 ОБЩАЯ СТАТИСТИКА")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.m) {
                statCard(
                    icon: "shield.fill",
                    title: "Заблокировано",
                    value: "\(selectedPeriod.stats.blocked)",
                    subtitle: "угроз",
                    color: .successGreen
                )
                
                statCard(
                    icon: "magnifyingglass",
                    title: "Просканировано",
                    value: "\(selectedPeriod.stats.scanned)",
                    subtitle: "файлов",
                    color: .primaryBlue
                )
            }
            
            HStack(spacing: Spacing.m) {
                statCard(
                    icon: "exclamationmark.triangle.fill",
                    title: "Обнаружено",
                    value: "\(selectedPeriod.stats.threats)",
                    subtitle: "угроз",
                    color: .warningOrange
                )
                
                statCard(
                    icon: "percent",
                    title: "Эффективность",
                    value: "\(Int(Double(selectedPeriod.stats.blocked) / Double(selectedPeriod.stats.threats) * 100))",
                    subtitle: "%",
                    color: .successGreen
                )
            }
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
    
    // MARK: - Charts Section
    
    private var chartsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ГРАФИКИ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Picker("Тип графика", selection: $selectedChart) {
                    ForEach(ChartType.allCases, id: \.self) { chart in
                        Text(chart.rawValue).tag(chart)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .accessibilityLabel("Выбор типа графика")
            }
            
            // График
            chartView
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
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
    
    private func statCard(icon: String, title: String, value: String, subtitle: String, color: Color) -> some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.h1)
                .foregroundColor(.textPrimary)
            
            Text(title)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(color.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value) \(subtitle)")
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
    
    private var chartView: some View {
        VStack(spacing: Spacing.m) {
            Text("График \(selectedChart.rawValue.lowercased())")
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            // Простой график (заглушка)
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(LinearGradient(
                    colors: [.primaryBlue.opacity(0.3), .secondaryBlue.opacity(0.1)],
                    startPoint: .top,
                    endPoint: .bottom
                ))
                .frame(height: 200)
                .overlay(
                    VStack {
                        Image(systemName: "chart.bar.fill")
                            .font(.system(size: 48))
                            .foregroundColor(.primaryBlue.opacity(0.5))
                        
                        Text("График \(selectedChart.rawValue.lowercased())")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                )
                .accessibilityLabel("График \(selectedChart.rawValue.lowercased())")
        }
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

struct AnalyticsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsScreen()
    }
}
