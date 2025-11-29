import SwiftUI

/// 📊 Protection Level History Modal
/// Модальное окно для отображения истории уровней защиты с графиком
struct ProtectionLevelHistoryModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var historyManager = ProtectionLevelHistoryManager.shared
    @State private var selectedPeriod: HistoryPeriod = .week
    
    enum HistoryPeriod: CaseIterable {
        case week
        case month
        
        var days: Int {
            switch self {
            case .week: return 7
            case .month: return 30
            }
        }
        
        var titleKey: String {
            switch self {
            case .week: return "settings_history_period_week"
            case .month: return "settings_history_period_month"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Заголовок с периодом
                        periodSelector
                        
                        // График
                        historyChart
                        
                        // Статистика
                        statisticsSection
                        
                        // История изменений
                        historyList
                    }
                    .padding(Spacing.screenPadding)
                }
            }
            .navigationTitle(localizationManager.localized("settings_history_title"))
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("settings_history_close")) {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    // MARK: - Period Selector
    
    private var periodSelector: some View {
        Picker(localizationManager.localized("settings_history_period_label"), selection: $selectedPeriod) {
            ForEach(HistoryPeriod.allCases, id: \.self) { period in
                Text(localizationManager.localized(period.titleKey)).tag(period)
            }
        }
        .pickerStyle(.segmented)
        .padding(.horizontal, Spacing.m)
    }
    
    // MARK: - History Chart
    
    private var historyChart: some View {
        let history = historyManager.getHistoryForDays(selectedPeriod.days)
        
        return VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("settings_history_chart_title"))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            
            if history.isEmpty {
                // Пустой график
                VStack(spacing: Spacing.s) {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.system(size: 48))
                        .foregroundColor(.textSecondary.opacity(0.5))
                    Text(localizationManager.localized("settings_history_chart_empty"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                .frame(height: 200)
                .frame(maxWidth: .infinity)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
            } else {
                // Простой линейный график
                GeometryReader { geometry in
                    ZStack {
                        // Фон
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                        
                        // График
                        Path { path in
                            let width = geometry.size.width - 40
                            let height = geometry.size.height - 40
                            let maxLevel: CGFloat = 100
                            let sortedHistory = history.sorted { $0.date < $1.date }
                            
                            guard !sortedHistory.isEmpty else { return }
                            
                            // Рисуем линии графика
                            for (index, entry) in sortedHistory.enumerated() {
                                let x = CGFloat(index) / CGFloat(max(1, sortedHistory.count - 1)) * width + 20
                                let y = height - (CGFloat(entry.level) / maxLevel * height) + 20
                                
                                if index == 0 {
                                    path.move(to: CGPoint(x: x, y: y))
                                } else {
                                    path.addLine(to: CGPoint(x: x, y: y))
                                }
                            }
                        }
                        .stroke(Color.primaryBlue, style: StrokeStyle(lineWidth: 3, lineCap: .round, lineJoin: .round))
                        
                        // Точки на графике
                        ForEach(Array(history.sorted { $0.date < $1.date }.enumerated()), id: \.element.id) { index, entry in
                            let width = geometry.size.width - 40
                            let height = geometry.size.height - 40
                            let maxLevel: CGFloat = 100
                            let sortedHistory = history.sorted { $0.date < $1.date }
                            let x = CGFloat(index) / CGFloat(max(1, sortedHistory.count - 1)) * width + 20
                            let y = height - (CGFloat(entry.level) / maxLevel * height) + 20
                            
                            Circle()
                                .fill(Color.primaryBlue)
                                .frame(width: 8, height: 8)
                                .position(x: x, y: y)
                        }
                    }
                }
                .frame(height: 200)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    // MARK: - Statistics Section
    
    private var statisticsSection: some View {
        let history = historyManager.getHistoryForDays(selectedPeriod.days)
        let averageLevel = historyManager.getAverageLevel(for: selectedPeriod.days)
        let maxLevel = history.map { $0.level }.max() ?? 0
        let minLevel = history.map { $0.level }.min() ?? 0
        
        return HStack(spacing: Spacing.m) {
            StatisticCard(
                title: localizationManager.localized("settings_history_stats_average"),
                value: "\(Int(averageLevel))%",
                icon: "chart.bar.fill",
                color: .primaryBlue
            )
            
            StatisticCard(
                title: localizationManager.localized("settings_history_stats_max"),
                value: "\(maxLevel)%",
                icon: "arrow.up.circle.fill",
                color: .successGreen
            )
            
            StatisticCard(
                title: localizationManager.localized("settings_history_stats_min"),
                value: "\(minLevel)%",
                icon: "arrow.down.circle.fill",
                color: .dangerRed
            )
        }
    }
    
    // MARK: - History List
    
    private var historyList: some View {
        let history = historyManager.getHistoryForDays(selectedPeriod.days)
        
        return VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("settings_history_list_title"))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            
            if history.isEmpty {
                Text(localizationManager.localized("settings_history_list_empty"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding(Spacing.m)
                    .frame(maxWidth: .infinity)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
            } else {
                ForEach(history.sorted { $0.date > $1.date }) { entry in
                    HistoryEntryRow(entry: entry, locale: localizationManager.locale)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
}

// MARK: - Statistic Card

struct StatisticCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(color)
            
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}

// MARK: - History Entry Row

struct HistoryEntryRow: View {
    let entry: ProtectionLevelHistoryEntry
    let locale: Locale
    
    private var levelColor: Color {
        switch entry.level {
        case 0...25: return .dangerRed
        case 26...50: return .warningOrange
        case 51...75: return .successGreen
        case 76...100: return .primaryBlue
        default: return .textSecondary
        }
    }
    
    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        formatter.locale = locale
        return formatter
    }
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Уровень
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                HStack {
                    Circle()
                        .fill(levelColor)
                        .frame(width: 12, height: 12)
                    
                    Text("\(entry.level)%")
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                }
                
                Text(dateFormatter.string(from: entry.date))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            // Количество функций
            HStack(spacing: Spacing.xs) {
                Image(systemName: "checkmark.shield.fill")
                    .font(.caption)
                    .foregroundColor(.primaryBlue)
                Text("\(entry.enabledFeatures.count)")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.2))
        )
    }
}

// MARK: - Preview (для Xcode Canvas)
#if DEBUG
struct ProtectionLevelHistoryModal_Previews: PreviewProvider {
    static var previews: some View {
        ProtectionLevelHistoryModal(isPresented: .constant(true))
            .environmentObject(LocalizationManager())
    }
}
#endif
