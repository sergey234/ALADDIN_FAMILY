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
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана аналитики")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        // Общая статистика
                        overallStats
                        
                        // Селектор периода
                        periodSelector
                        
                        // Графики
                        chartsSection
                        
                        // Детальная статистика
                        detailedStats
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 40)
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
        VStack(spacing: 16) {
            Text("📊 ОБЩАЯ СТАТИСТИКА")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: 16) {
                statCard(
                    icon: "shield.fill",
                    title: "Заблокировано",
                    value: "\(selectedPeriod.stats.blocked)",
                    subtitle: "угроз",
                    color: .green
                )
                
                statCard(
                    icon: "magnifyingglass",
                    title: "Просканировано",
                    value: "\(selectedPeriod.stats.scanned)",
                    subtitle: "файлов",
                    color: .blue
                )
            }
            
            HStack(spacing: 16) {
                statCard(
                    icon: "exclamationmark.triangle.fill",
                    title: "Обнаружено",
                    value: "\(selectedPeriod.stats.threats)",
                    subtitle: "угроз",
                    color: .orange
                )
                
                statCard(
                    icon: "percent",
                    title: "Эффективность",
                    value: "\(Int(Double(selectedPeriod.stats.blocked) / Double(selectedPeriod.stats.threats) * 100))",
                    subtitle: "%",
                    color: .green
                )
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Period Selector
    
    private var periodSelector: some View {
        VStack(spacing: 16) {
            Text("ПЕРИОД")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: 8) {
                ForEach(TimePeriod.allCases, id: \.self) { period in
                    Button(action: {
                        selectedPeriod = period
                    }) {
                        Text(period.rawValue)
                            .font(.body)
                            .foregroundColor(selectedPeriod == period ? .white : .primary)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(selectedPeriod == period ? Color.blue : Color.gray)
                            )
                    }
                    .accessibilityLabel("Период: \(period.rawValue)")
                    .accessibilityAddTraits(selectedPeriod == period ? .isSelected : [])
                }
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Charts Section
    
    private var chartsSection: some View {
        VStack(spacing: 16) {
            HStack {
                Text("ГРАФИКИ")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.primary)
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
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Detailed Stats
    
    private var detailedStats: some View {
        VStack(spacing: 16) {
            Text("ДЕТАЛЬНАЯ СТАТИСТИКА")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 8) {
                detailRow(
                    icon: "globe",
                    title: "Веб-угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.4))",
                    color: .red
                )
                
                detailRow(
                    icon: "doc",
                    title: "Файловые угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.3))",
                    color: .orange
                )
                
                detailRow(
                    icon: "network",
                    title: "Сетевые угрозы",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.2))",
                    color: .blue
                )
                
                detailRow(
                    icon: "app",
                    title: "Угрозы приложений",
                    value: "\(Int(Double(selectedPeriod.stats.threats) * 0.1))",
                    color: .green
                )
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func statCard(icon: String, title: String, value: String, subtitle: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(.primary)
            
            Text(title)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.primary)
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(color.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value) \(subtitle)")
    }
    
    private func detailRow(icon: String, title: String, value: String, color: Color) -> some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(color)
                .frame(width: 24)
            
            Text(title)
                .font(.body)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(value)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.primary)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
    
    private var chartView: some View {
        VStack(spacing: 16) {
            Text("График \(selectedChart.rawValue.lowercased())")
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.primary)
            
            // Простой график (заглушка)
            RoundedRectangle(cornerRadius: 8)
                .fill(LinearGradient(
                    colors: [.blue.opacity(0.3), .purple.opacity(0.1)],
                    startPoint: .top,
                    endPoint: .bottom
                ))
                .frame(height: 200)
                .overlay(
                    VStack {
                        Image(systemName: "chart.bar.fill")
                            .font(.system(size: 48))
                            .foregroundColor(.blue.opacity(0.5))
                        
                        Text("График \(selectedChart.rawValue.lowercased())")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                )
                .accessibilityLabel("График \(selectedChart.rawValue.lowercased())")
        }
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.gray.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
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
