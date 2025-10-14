import SwiftUI

/**
 * 🔋 VPN Energy Stats Screen
 * Статистика энергопотребления VPN
 * 18_vpn_energy_stats из HTML
 */

struct VPNEnergyStatsScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var selectedPeriod: String = "Сегодня"
    @State private var batteryUsage: Double = 12.5 // %
    @State private var dataUsage: String = "2.4 GB"
    @State private var sessionTime: String = "4:37:21"
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: "ЭНЕРГОПОТРЕБЛЕНИЕ VPN",
                    subtitle: "Статистика использования",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                .padding(.bottom, Spacing.m)
                
                // Battery Impact Card
                VStack(spacing: Spacing.m) {
                    Text("🔋")
                        .font(.system(size: Size.iconXLarge * 1.5))
                    
                    Text("\(batteryUsage, specifier: "%.1f")%")
                        .font(.largeTitle)
                        .foregroundColor(.secondaryGold)
                    
                    Text("Расход батареи за сегодня")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    ProgressView(value: batteryUsage / 100)
                        .progressViewStyle(LinearProgressViewStyle(tint: .secondaryGold))
                        .scaleEffect(x: 1, y: 2, anchor: .center)
                        .padding(.horizontal, Spacing.xl)
                    
                    Text("Это ниже среднего! VPN работает эффективно")
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                .padding(Spacing.cardPadding)
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
                .padding(.horizontal, Spacing.screenPadding)
                
                // Period Selector
                HStack(spacing: Spacing.s) {
                    PeriodButton(title: "Сегодня", isSelected: selectedPeriod == "Сегодня") {
                        selectedPeriod = "Сегодня"
                    }
                    PeriodButton(title: "Неделя", isSelected: selectedPeriod == "Неделя") {
                        selectedPeriod = "Неделя"
                    }
                    PeriodButton(title: "Месяц", isSelected: selectedPeriod == "Месяц") {
                        selectedPeriod = "Месяц"
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Energy Stats
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("СТАТИСТИКА")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    EnergyStatRow(icon: "⚡", label: "Потреблено энергии", value: "245 mAh", color: .warningOrange)
                    EnergyStatRow(icon: "⏱️", label: "Время работы VPN", value: sessionTime, color: .infoBlue)
                    EnergyStatRow(icon: "📊", label: "Средний расход", value: "53 mAh/час", color: .successGreen)
                    EnergyStatRow(icon: "🌐", label: "Трафик обработан", value: dataUsage, color: .infoBlue)
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Comparison Card
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("СРАВНЕНИЕ С ДРУГИМИ VPN")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    VStack(spacing: Spacing.s) {
                        ComparisonRow(name: "ALADDIN VPN", usage: 12.5, color: .successGreen)
                        ComparisonRow(name: "NordVPN", usage: 18.3, color: .warningOrange)
                        ComparisonRow(name: "ExpressVPN", usage: 22.1, color: .dangerRed)
                    }
                    .padding(Spacing.m)
                    .background(
                        LinearGradient.cardGradient.appGlassmorphism()
                    )
                    .cornerRadius(CornerRadius.large)
                    .cardShadow()
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Tips Card
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("💡 СОВЕТЫ ПО ЭКОНОМИИ")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    TipCard(tip: "Используйте Wi-Fi вместо сотовой сети")
                    TipCard(tip: "Отключайте VPN когда не нужен")
                    TipCard(tip: "Выбирайте ближайший сервер")
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .navigationBarHidden(true)
    }
}

// MARK: - Energy Stat Row

struct EnergyStatRow: View {
    let icon: String
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack {
            Text(icon)
                .font(.system(size: Size.iconMedium))
            Text(label)
                .font(.body)
                .foregroundColor(.textSecondary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(color)
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient.appGlassmorphism()
        )
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Comparison Row

struct ComparisonRow: View {
    let name: String
    let usage: Double
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xxs) {
            HStack {
                Text(name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Spacer()
                Text("\(usage, specifier: "%.1f")%")
                    .font(.bodyBold)
                    .foregroundColor(color)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.backgroundMedium)
                        .frame(height: 8)
                    
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(usage / 25.0), height: 8)
                }
            }
            .frame(height: 8)
        }
    }
}

// MARK: - Tip Card

struct TipCard: View {
    let tip: String
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.secondaryGold)
            Text(tip)
                .font(.body)
                .foregroundColor(.textPrimary)
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient.appGlassmorphism()
        )
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Period Button

struct PeriodButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            action()
            HapticFeedback.selection()
        }) {
            Text(title)
                .font(.bodyBold)
                .foregroundColor(isSelected ? .backgroundDark : .textPrimary)
                .padding(.vertical, Spacing.s)
                .padding(.horizontal, Spacing.m)
                .frame(maxWidth: .infinity)
                .background(isSelected ? Color.secondaryGold : Color.surfaceDark.opacity(0.6))
                .cornerRadius(CornerRadius.medium)
        }
    }
}

// MARK: - Preview

struct VPNEnergyStatsScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNEnergyStatsScreen()
    }
}



