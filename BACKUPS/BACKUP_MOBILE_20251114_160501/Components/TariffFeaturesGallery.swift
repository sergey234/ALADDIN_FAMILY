import SwiftUI

// MARK: - Галерея карточек тарифов

/// Галерея из 4 карточек тарифов с полным функционалом
/// Заменяет ThreatScenariosGallery
struct TariffFeaturesGallery: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    
    // Карточки тарифов
    private var tariffCards: [TariffCard] {
        [
            TariffType.free.createCard(localizationManager: localizationManager),
            TariffType.personal.createCard(localizationManager: localizationManager),
            TariffType.family.createCard(localizationManager: localizationManager),
            TariffType.premium.createCard(localizationManager: localizationManager)
        ]
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок
            Text(localizationManager.localized("protection_scenarios_title"))
                .font(.title2)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            // Вертикальный список карточек тарифов
            VStack(spacing: Spacing.l) {
                ForEach(tariffCards) { card in
                    TariffCardView(card: card)
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(.vertical, Spacing.m)
    }
}

// MARK: - Preview

#if DEBUG
struct TariffFeaturesGallery_Previews: PreviewProvider {
    static var previews: some View {
        ScrollView {
            TariffFeaturesGallery()
                .environmentObject(LocalizationManager())
                .environmentObject(NavigationManager())
        }
        .background(LinearGradient.backgroundGradient)
    }
}
#endif

