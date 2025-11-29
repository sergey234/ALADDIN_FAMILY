import SwiftUI

/// 🛡️ Строка угрозы с визуализацией тарифа
/// Показывает каждую угрозу с цветной полоской (цвет тарифа) и бейджем тарифа
struct ThreatTariffRow: View {
    let threat: String
    let tariff: TariffType
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            // Цветная полоска слева (цвет тарифа)
            RoundedRectangle(cornerRadius: 2)
                .fill(tariffColor)
                .frame(width: 4, height: 20)
            
            // Текст угрозы
            Text(threat)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            // Бейдж тарифа справа
            tariffBadge
        }
        .padding(.vertical, Spacing.xxs)
    }
    
    // MARK: - Tariff Badge
    
    private var tariffBadge: some View {
        Text(tariff.title(localizationManager: localizationManager))
            .font(.system(size: 10, weight: .semibold))
            .foregroundColor(.white)
            .lineLimit(1)
            .fixedSize(horizontal: true, vertical: false)
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .frame(minWidth: 50, maxWidth: 70, minHeight: 18, maxHeight: 18)
            .background(
                Capsule()
                    .fill(tariffBadgeColor)
            )
    }
    
    // MARK: - Colors
    
    /// Цвет полоски (цвет тарифа)
    private var tariffColor: Color {
        switch tariff {
        case .free:
            return Color.textSecondary.opacity(0.6)
        case .personal:
            return Color.primaryBlue.opacity(0.8)
        case .family:
            return Color.secondaryGold.opacity(0.8)
        case .premium:
            return Color(hex: "#A855F7").opacity(0.8)
        }
    }
    
    /// Цвет бейджа тарифа
    private var tariffBadgeColor: Color {
        switch tariff {
        case .free:
            return Color.textSecondary.opacity(0.8)
        case .personal:
            return Color.primaryBlue.opacity(0.9)
        case .family:
            return Color.secondaryGold.opacity(0.9)
        case .premium:
            return Color(hex: "#A855F7").opacity(0.9)
        }
    }
}

#if DEBUG
struct ThreatTariffRow_Previews: PreviewProvider {
    static var previews: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            ThreatTariffRow(threat: "Вирусы и трояны", tariff: .free)
                .environmentObject(LocalizationManager())
            
            ThreatTariffRow(threat: "Фишинговые сайты", tariff: .personal)
                .environmentObject(LocalizationManager())
            
            ThreatTariffRow(threat: "Угрозы для детей", tariff: .family)
                .environmentObject(LocalizationManager())
            
            ThreatTariffRow(threat: "Deepfake атаки", tariff: .premium)
                .environmentObject(LocalizationManager())
        }
        .padding()
        .background(Color.backgroundDark)
        .previewLayout(.sizeThatFits)
    }
}
#endif

