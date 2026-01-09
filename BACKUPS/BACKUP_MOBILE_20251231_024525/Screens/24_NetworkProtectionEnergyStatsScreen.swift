import SwiftUI

/**
 * 🔋 Network Protection Energy Stats Screen
 * Статистика энергопотребления защиты сети
 * 18_network_protection_energy_stats из HTML
 */

struct NetworkProtectionEnergyStatsScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var networkProtectionManager = NetworkProtectionManager.shared
    @State private var selectedPeriod: String = "today"
    @State private var batteryUsage: Double = 12.5 // %
    @State private var dataUsage: String = "0 GB"
    @State private var sessionTime: String = "0:00:00"
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: localizationManager.localized("network_protection_energy_title"),
                    subtitle: localizationManager.localized("network_protection_energy_subtitle"),
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: {
                        // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                        // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                        dismiss()
                        
                        // Дополнительно синхронизируем NavigationManager для корректной работы стека
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack()
                            }
                        }
                    }
                )
                .padding(.bottom, Spacing.m)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(localizationManager.localized("network_protection_energy_nav_accessibility"))
                
                // Battery Impact Card
                VStack(spacing: Spacing.m) {
                    Text("🔋")
                        .font(.system(size: Size.iconXLarge * 1.5))
                        .accessibilityLabel(localizationManager.localized("network_protection_energy_battery"))
                    
                    Text("\(batteryUsage, specifier: "%.1f")%")
                        .font(.largeTitle)
                        .foregroundColor(.secondaryGold)
                        .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_battery_usage"), batteryUsage))
                    
                    Text(localizationManager.localized("network_protection_energy_battery_today"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel(localizationManager.localized("network_protection_energy_battery_today"))
                    
                    ProgressView(value: batteryUsage / 100)
                        .progressViewStyle(LinearProgressViewStyle(tint: .secondaryGold))
                        .scaleEffect(x: 1, y: 2, anchor: .center)
                        .padding(.horizontal, Spacing.l)
                        .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_battery_progress"), batteryUsage))
                    
                    Text(localizationManager.localized("network_protection_energy_battery_efficient"))
                        .font(.caption)
                        .foregroundColor(.successGreen)
                        .accessibilityLabel(localizationManager.localized("network_protection_energy_battery_efficient"))
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
                    PeriodButton(title: localizationManager.localized("network_protection_energy_period_today"), isSelected: selectedPeriod == "today") {
                        selectedPeriod = "today"
                    }
                    PeriodButton(title: localizationManager.localized("network_protection_energy_period_week"), isSelected: selectedPeriod == "week") {
                        selectedPeriod = "week"
                    }
                    PeriodButton(title: localizationManager.localized("network_protection_energy_period_month"), isSelected: selectedPeriod == "month") {
                        selectedPeriod = "month"
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .accessibilityElement(children: .contain)
                .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_period_selector"), selectedPeriod))
                
                // Energy Stats
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("network_protection_energy_stats_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                    
                    EnergyStatRow(icon: "⚡", label: localizationManager.localized("network_protection_energy_stats_consumed"), value: "245 mAh", color: .warningOrange)
                    EnergyStatRow(icon: "⏱️", label: localizationManager.localized("network_protection_energy_stats_time"), value: sessionTime, color: .infoBlue)
                    EnergyStatRow(icon: "📊", label: localizationManager.localized("network_protection_energy_stats_average"), value: "53 mAh/час", color: .successGreen)
                    EnergyStatRow(icon: "🌐", label: localizationManager.localized("network_protection_energy_stats_traffic"), value: dataUsage, color: .infoBlue)
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Comparison Card
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("network_protection_energy_comparison_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                    
                    VStack(spacing: Spacing.s) {
                        ComparisonRow(name: "ALADDIN", usage: 12.5, color: .successGreen)
                        ComparisonRow(name: "Решение A", usage: 18.3, color: .warningOrange)
                        ComparisonRow(name: "Решение B", usage: 22.1, color: .dangerRed)
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
                    Text(localizationManager.localized("network_protection_energy_tips_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                    
                    TipCard(tip: localizationManager.localized("network_protection_energy_tip_wifi"))
                    TipCard(tip: localizationManager.localized("network_protection_energy_tip_disable"))
                    TipCard(tip: localizationManager.localized("network_protection_energy_tip_server"))
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localizationManager.localized("network_protection_energy_accessibility"))
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 NetworkProtectionEnergyStatsScreen загружен!")
            loadEnergyStats()
        }
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
                .accessibilityLabel(icon)
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
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(label): \(value)")
    }
}

// MARK: - Comparison Row

struct ComparisonRow: View {
    let name: String
    let usage: Double
    let color: Color
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(name): \(usage, specifier: "%.1f") \(localizationManager.localized("network_protection_energy_comparison_percent"))")
            
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
            .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_comparison_chart"), usage))
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_comparison_row"), name, usage))
    }
}

// MARK: - Tip Card

struct TipCard: View {
    let tip: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.secondaryGold)
                .accessibilityLabel(localizationManager.localized("network_protection_energy_tip_icon"))
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
        .accessibilityElement(children: .combine)
        .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_tip_format"), tip))
    }
}

// MARK: - Functions

extension NetworkProtectionEnergyStatsScreen {
    private func loadEnergyStats() {
        // Загружаем данные из NetworkProtectionManager
        let dataUsage = networkProtectionManager.getDataUsage()
        
        // Форматируем данные
        self.dataUsage = formatBytes(dataUsage.today)
        self.sessionTime = formatSessionTime()
        
        // Battery usage - локальная оценка (можно расширить)
        self.batteryUsage = 12.5
    }
    
    private func formatBytes(_ bytes: Int64) -> String {
        let gb = Double(bytes) / (1024.0 * 1024.0 * 1024.0)
        if gb >= 1.0 {
            return String(format: "%.2f GB", gb)
        } else {
            let mb = Double(bytes) / (1024.0 * 1024.0)
            return String(format: "%.2f MB", mb)
        }
    }
    
    private func formatSessionTime() -> String {
        // TODO: Получить реальное время сессии защиты сети
        return "4:37:21"
    }
}

// MARK: - Period Button

struct PeriodButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
        .accessibilityLabel(String(format: localizationManager.localized("network_protection_energy_period_accessibility"), title))
        .accessibilityHint(isSelected ? String(format: localizationManager.localized("network_protection_energy_period_selected_hint"), title) : String(format: localizationManager.localized("network_protection_energy_period_switch_hint"), title))
    }
}

// MARK: - Preview

struct NetworkProtectionEnergyStatsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NetworkProtectionEnergyStatsScreen()
    }
}



