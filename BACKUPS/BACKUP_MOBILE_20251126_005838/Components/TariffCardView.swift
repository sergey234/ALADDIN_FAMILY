import SwiftUI

// MARK: - Карточка тарифа

/// Основной компонент карточки тарифа с трехуровневым раскрытием
struct TariffCardView: View {
    let card: TariffCard
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    
    @State private var isExpanded: Bool = false
    @State private var expandedSection: TariffSection? = nil
    @State private var expandedCategory: ThreatProtectionCategory? = nil
    @State private var expandedModule: ParentalControlModule? = nil
    
    enum TariffSection: String, CaseIterable {
        case additional = "additional"
        case protection = "protection"
        case parental = "parental"
        
        var titleKey: String {
            switch self {
            case .additional: return "tariff_additional_features_title"
            case .protection: return "tariff_protection_title"
            case .parental: return "tariff_parental_title"
            }
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Заголовок карточки (всегда видимый)
            cardHeader
            
            // Раскрывающийся контент
            if isExpanded {
                expandedContent
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(card.color.opacity(0.3), lineWidth: 2)
                )
        )
        .cardShadow()
    }
    
    // MARK: - Заголовок карточки
    
    private var cardHeader: some View {
        Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                isExpanded.toggle()
            }
            HapticFeedback.selection()
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка тарифа
                Text(card.emoji)
                    .font(.system(size: 32))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    // Название тарифа
                    Text(card.tariffType.title(localizationManager: localizationManager))
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.textPrimary)
                    
                    // Цена и устройства
                    HStack(spacing: Spacing.s) {
                        Text(card.price)
                            .font(.body)
                            .foregroundColor(card.color)
                        
                        if !card.price.contains("0 ₽") {
                            Text(card.tariffType.period(localizationManager: localizationManager))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Text("•")
                            .foregroundColor(.textSecondary)
                        
                        Text(card.devices == "Неограниченно" ? 
                             localizationManager.localized("tariff_devices_unlimited") :
                             String(format: localizationManager.localized("tariff_card_devices"), card.devices))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    // Счётчики функций
                    HStack(spacing: Spacing.m) {
                        Label(
                            String(format: localizationManager.localized("tariff_card_protection_count"),
                                   card.protectionCount, card.protectionPercentage),
                            systemImage: "shield.fill"
                        )
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        
                        Label(
                            String(format: localizationManager.localized("tariff_card_parental_count"),
                                   card.parentalControlCount, card.parentalControlPercentage),
                            systemImage: "person.2.fill"
                        )
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
                
                // Chevron
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(card.color)
            }
            .padding(Spacing.m)
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(card.tariffType.title(localizationManager: localizationManager)), \(card.price), \(card.devices)")
            .accessibilityHint(isExpanded ? "Нажмите, чтобы свернуть карточку тарифа" : "Нажмите, чтобы развернуть карточку тарифа")
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Раскрывающийся контент
    
    private var expandedContent: some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            // Список недоступных функций для Free
            if card.tariffType == .free {
                unavailableFeaturesList
            }
            
            // Секции
            ForEach(TariffSection.allCases, id: \.self) { section in
                sectionView(for: section)
            }
        }
        .padding(Spacing.m)
        .padding(.top, Spacing.xs)
    }
    
    // MARK: - Список недоступных функций (для Free)
    
    private var unavailableFeaturesList: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized("tariff_parental_unavailable_title"))
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.warningOrange)
            
            VStack(alignment: .leading, spacing: 4) {
                Text("🔒 \(localizationManager.localized("tariff_parental_unavailable_location"))")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                
                Text("🔒 \(localizationManager.localized("tariff_parental_unavailable_bypass"))")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                
                Text("🔒 \(localizationManager.localized("tariff_parental_unavailable_reports"))")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
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
    
    // MARK: - Секция карточки
    
    private func sectionView(for section: TariffSection) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок секции
            Button(action: {
                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                    if expandedSection == section {
                        expandedSection = nil
                    } else {
                        expandedSection = section
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack {
                    Text(localizationManager.localized(section.titleKey))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Image(systemName: expandedSection == section ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.xs)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(localizationManager.localized(section.titleKey))
                .accessibilityHint(expandedSection == section ? "Нажмите, чтобы свернуть секцию" : "Нажмите, чтобы развернуть секцию")
            }
            .buttonStyle(PlainButtonStyle())
            
            // Содержимое секции
            if expandedSection == section {
                sectionContent(for: section)
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundDark.opacity(0.3))
        )
    }
    
    // MARK: - Содержимое секции
    
    @ViewBuilder
    private func sectionContent(for section: TariffSection) -> some View {
        switch section {
        case .additional:
            AdditionalFeaturesSection(card: card)
        case .protection:
            ProtectionFeaturesSection(card: card, expandedCategory: $expandedCategory)
        case .parental:
            ParentalControlSection(card: card, expandedModule: $expandedModule)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct TariffCardView_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.l) {
            ForEach([TariffType.free, .personal, .family, .premium], id: \.self) { tariff in
                TariffCardView(card: tariff.createCard(localizationManager: LocalizationManager()))
                    .environmentObject(LocalizationManager())
                    .environmentObject(NavigationManager())
            }
        }
        .padding()
        .background(LinearGradient.backgroundGradient)
    }
}
#endif

