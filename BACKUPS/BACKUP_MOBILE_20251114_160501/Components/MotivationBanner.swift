import SwiftUI

/// 💡 Мотивационный баннер для недоступных функций
/// Показывается рядом с недоступными категориями для объяснения, чего пользователь лишается
struct MotivationBanner: View {
    let category: ThreatProtectionCategory
    let requiredTariff: TariffType
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "lock.fill")
                .foregroundColor(.warningOrange)
                .font(.caption)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text("\(localizationManager.localized("protection_requires_tariff")): \(requiredTariff.title(localizationManager: localizationManager))")
                    .font(.captionBold)
                    .foregroundColor(.warningOrange)
                    .lineLimit(1) // ✅ Размещаем на одной строке
                
                Text(getMotivationText())
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            Spacer()
            
            Button(action: {
                handleUpgradeTap()
            }) {
                Text(localizationManager.localized("protection_upgrade_tariff"))
                    .font(.captionBold)
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xxs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.2))
                    )
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.warningOrange.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.warningOrange.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Motivation Text
    
    private func getMotivationText() -> String {
        switch category {
        case .fraud:
            return "Защитите свои финансы от мошенничества"
        case .childThreats, .familyThreats:
            return "Защитите всю семью от опасностей"
        case .deepfakes:
            return "Обнаруживайте поддельные видео и аудио"
        case .iotThreats:
            return "Защитите умные устройства от взлома"
        default:
            return "Получите полную защиту от всех угроз"
        }
    }
    
    // MARK: - Navigation
    
    private func handleUpgradeTap() {
        HapticFeedback.selection()
        navigationManager.navigateTo(.tariffs)
        // TODO: Подсветить нужный тариф при переходе
    }
}

#if DEBUG
struct MotivationBanner_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.m) {
            MotivationBanner(
                category: .deepfakes,
                requiredTariff: .premium
            )
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
            
            MotivationBanner(
                category: .fraud,
                requiredTariff: .personal
            )
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
        }
        .padding()
        .background(Color.backgroundDark)
    }
}
#endif

