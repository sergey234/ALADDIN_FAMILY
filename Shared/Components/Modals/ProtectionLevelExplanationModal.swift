import SwiftUI

/// 📋 Protection Level Explanation Modal
/// Модальное окно с объяснением уровней защиты по тарифам

struct ProtectionLevelExplanationModal: View {
    
    @Binding var isPresented: Bool
    let currentTariff: TariffType
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    VStack(spacing: Spacing.s) {
                        Text(localizationManager.localized("settings_levels_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("settings_levels_subtitle"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, Spacing.m)
                    
                    // Карточки тарифов
                    VStack(spacing: Spacing.m) {
                        tariffCard(tariff: .free)
                        tariffCard(tariff: .personal)
                        tariffCard(tariff: .family)
                        tariffCard(tariff: .premium)
                    }
                }
                .padding(Spacing.m)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        .navigationTitle(localizationManager.localized("settings_levels_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                Button(localizationManager.localized("settings_levels_done")) {
                        isPresented = false
                    }
                    .foregroundColor(.primaryBlue)
                }
            }
        }
    }
    
    // MARK: - Tariff Card
    
    private func tariffCard(tariff: TariffType) -> some View {
        let card = tariff.createCard(localizationManager: localizationManager)
        let isCurrentTariff = tariff == currentTariff
        let totalPercentage = Int((Double(card.totalFeatures) / 142.0) * 100)
        
        return VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок карточки
            HStack {
                Text(card.emoji)
                    .font(.system(size: 28))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    HStack {
                        Text(card.tariffType.title(localizationManager: localizationManager))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        if isCurrentTariff {
                            Text(localizationManager.localized("settings_levels_current"))
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                                .padding(.horizontal, Spacing.xs)
                                .padding(.vertical, 2)
                                .background(
                                    Capsule()
                                        .fill(Color.primaryBlue.opacity(0.1))
                                )
                        }
                    }
                    
                    Text("\(totalPercentage)%")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if isCurrentTariff {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                        .font(.system(size: 20))
                }
            }
            
            // Описание тарифа
            Text(tariffDescription(tariff))
                .font(.body)
                .foregroundColor(.textSecondary)
            
            Divider()
            
            // Статистика функций
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("settings_levels_includes"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                // Защита от угроз
                HStack(spacing: Spacing.s) {
                    Image(systemName: "shield.fill")
                        .font(.system(size: 16))
                        .foregroundColor(card.color)
                        .frame(width: 20)
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(String(format: localizationManager.localized("tariff_card_protection_count"), card.protectionCount, card.protectionPercentage))
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("tariff_protection_description"))
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                }
                .padding(.vertical, Spacing.xs)
                
                // Родительский контроль
                HStack(spacing: Spacing.s) {
                    Image(systemName: "person.2.fill")
                        .font(.system(size: 16))
                        .foregroundColor(card.color)
                        .frame(width: 20)
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(String(format: localizationManager.localized("tariff_card_parental_count"), card.parentalControlCount, card.parentalControlPercentage))
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("tariff_parental_description"))
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                }
                .padding(.vertical, Spacing.xs)
                
                // Дополнительные функции
                HStack(spacing: Spacing.s) {
                    Image(systemName: "star.fill")
                        .font(.system(size: 16))
                        .foregroundColor(card.color)
                        .frame(width: 20)
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(String(format: localizationManager.localized("tariff_additional_count"), card.additionalFeatures.count, Int((Double(card.additionalFeatures.count) / 6.0) * 100)))
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("tariff_additional_description"))
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                }
                .padding(.vertical, Spacing.xs)
                
                // Общее количество
                Divider()
                    .padding(.vertical, Spacing.xs)
                
                HStack {
                    Text(localizationManager.localized("tariff_total_functions"))
                        .font(.captionBold)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Text(String(format: localizationManager.localized("tariff_total_count"), card.totalFeatures, totalPercentage))
                        .font(.captionBold)
                        .foregroundColor(card.color)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(isCurrentTariff ? 0.6 : 0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(isCurrentTariff ? card.color.opacity(0.5) : Color.clear, lineWidth: 2)
                )
        )
    }
    
    private func tariffDescription(_ tariff: TariffType) -> String {
        switch tariff {
        case .trial:
            return localizationManager.localized("tariff_trial_description")
        case .free:
            return localizationManager.localized("tariff_free_description")
        case .personal:
            return localizationManager.localized("tariff_personal_description")
        case .family:
            return localizationManager.localized("tariff_family_description")
        case .premium:
            return localizationManager.localized("tariff_premium_description")
        }
    }
}

// MARK: - Preview

struct ProtectionLevelExplanationModal_Previews: PreviewProvider {
    static var previews: some View {
        ProtectionLevelExplanationModal(isPresented: .constant(true), currentTariff: .family)
            .environmentObject(LocalizationManager())
    }
}
