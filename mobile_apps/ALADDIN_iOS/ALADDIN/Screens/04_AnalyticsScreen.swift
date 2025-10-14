import SwiftUI

/// 📊 Analytics Screen
/// Экран аналитики - статистика защиты и угроз
/// Источник дизайна: /mobile/wireframes/04_analytics_screen.html
struct AnalyticsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedPeriod: TimePeriod = .week
    
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
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "АНАЛИТИКА",
                    subtitle: "Статистика защиты",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    },
                    rightButtons: [
                        .init(icon: "line.3.horizontal.decrease.circle") {
                            print("Фильтры")
                        }
                    ]
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Выбор периода
                        periodSelector
                        
                        // Основная статистика
                        mainStatsCard
                        
                        // График защиты (заглушка)
                        protectionChart
                        
                        // Топ угроз
                        topThreatsSection
                        
                        // Типы угроз
                        threatTypesSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Period Selector
    
    private var periodSelector: some View {
        HStack(spacing: Spacing.s) {
            ForEach(TimePeriod.allCases, id: \.self) { period in
                Button(action: {
                    let generator = UIImpactFeedbackGenerator(style: .light)
                    generator.impactOccurred()
                    
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedPeriod = period
                    }
                }) {
                    Text(period.rawValue)
                        .font(.body)
                        .foregroundColor(selectedPeriod == period ? .white : .textSecondary)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(
                                    selectedPeriod == period ?
                                    Color.primaryBlue :
                                    Color.backgroundMedium.opacity(0.3)
                                )
                        )
                }
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Main Stats Card
    
    private var mainStatsCard: some View {
        VStack(spacing: Spacing.m) {
            // Заголовок
            HStack {
                Text("ОБЩАЯ СТАТИСТИКА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text(selectedPeriod.rawValue.uppercased())
                    .font(.caption)
                    .foregroundColor(.primaryBlue)
            }
            
            // Статистика в 3 колонки
            HStack(spacing: Spacing.m) {
                statColumn(
                    icon: "🛡️",
                    value: "\(selectedPeriod.stats.threats)",
                    label: "Угроз\nобнаружено",
                    color: .dangerRed
                )
                
                Rectangle()
                    .fill(Color.white.opacity(0.1))
                    .frame(width: 1)
                
                statColumn(
                    icon: "✅",
                    value: "\(selectedPeriod.stats.blocked)",
                    label: "Успешно\nзаблокировано",
                    color: .successGreen
                )
                
                Rectangle()
                    .fill(Color.white.opacity(0.1))
                    .frame(width: 1)
                
                statColumn(
                    icon: "📱",
                    value: "\(selectedPeriod.stats.scanned)",
                    label: "Проверено\nэлементов",
                    color: .primaryBlue
                )
            }
            .frame(height: 80)
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func statColumn(icon: String, value: String, label: String, color: Color) -> some View {
        VStack(spacing: Spacing.xs) {
            Text(icon)
                .font(.system(size: 28))
            
            Text(value)
                .font(.h2)
                .foregroundColor(color)
            
            Text(label)
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Protection Chart
    
    private var protectionChart: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("УРОВЕНЬ ЗАЩИТЫ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // График (простая визуализация)
            VStack(spacing: Spacing.m) {
                // Процент защиты
                VStack(spacing: Spacing.s) {
                    Text("96%")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.successGreen)
                    
                    Text("Эффективность защиты")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.m)
                
                // Прогресс бар
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text("Заблокировано")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Spacer()
                        
                        Text("96%")
                            .font(.captionBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    GeometryReader { geometry in
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.backgroundMedium)
                                .frame(height: 8)
                            
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(
                                    LinearGradient(
                                        colors: [Color.successGreen, Color(hex: "#16A34A")],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .frame(width: geometry.size.width * 0.96, height: 8)
                        }
                    }
                    .frame(height: 8)
                }
            }
            .padding(Spacing.cardPadding)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Top Threats Section
    
    private var topThreatsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("ТОП УГРОЗ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Список угроз
            VStack(spacing: Spacing.s) {
                threatItem(rank: 1, name: "Вредоносные сайты", count: 23, icon: "🌐")
                threatItem(rank: 2, name: "Фишинг", count: 12, icon: "🎣")
                threatItem(rank: 3, name: "Трекеры", count: 8, icon: "👁️")
                threatItem(rank: 4, name: "Вирусы", count: 4, icon: "🦠")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func threatItem(rank: Int, name: String, count: Int, icon: String) -> some View {
        HStack(spacing: Spacing.m) {
            // Ранг
            Text("\(rank)")
                .font(.h3)
                .foregroundColor(.primaryBlue)
                .frame(width: 30)
            
            // Иконка
            Text(icon)
                .font(.system(size: 24))
            
            // Текст
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("\(count) заблокировано")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            // Стрелка
            Image(systemName: "chevron.right")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Threat Types Section
    
    private var threatTypesSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("ТИПЫ УГРОЗ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Типы угроз
            VStack(spacing: Spacing.s) {
                typeProgressBar(
                    label: "Веб-угрозы",
                    count: 23,
                    total: 47,
                    color: .dangerRed
                )
                
                typeProgressBar(
                    label: "Приложения",
                    count: 12,
                    total: 47,
                    color: .warningOrange
                )
                
                typeProgressBar(
                    label: "Сеть",
                    count: 8,
                    total: 47,
                    color: .primaryBlue
                )
                
                typeProgressBar(
                    label: "Файлы",
                    count: 4,
                    total: 47,
                    color: .successGreen
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func typeProgressBar(label: String, count: Int, total: Int, color: Color) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Text(label)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text("\(count)")
                    .font(.bodyBold)
                    .foregroundColor(color)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.backgroundMedium)
                        .frame(height: 6)
                    
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(count) / CGFloat(total), height: 6)
                }
            }
            .frame(height: 6)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.2))
        )
    }
}

// MARK: - Preview

#Preview {
    AnalyticsScreen()
}




