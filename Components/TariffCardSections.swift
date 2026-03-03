import SwiftUI

// MARK: - Секция дополнительных функций

struct AdditionalFeaturesSection: View {
    let card: TariffCard
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            ForEach(card.additionalFeatures) { feature in
                HStack(spacing: Spacing.s) {
                    if let icon = feature.icon {
                        Text(icon)
                            .font(.system(size: 20))
                    }
                    
                    Text(feature.localizedTitle(localizationManager))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    // Индикатор доступности
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.successGreen)
                        .font(.system(size: 16))
                        .accessibilityLabel("Доступно")
                }
                .padding(.vertical, Spacing.xxs)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(feature.localizedTitle(localizationManager) + ", доступно")
            }
        }
    }
}

// MARK: - Секция защиты от угроз

struct ProtectionFeaturesSection: View {
    let card: TariffCard
    @Binding var expandedCategory: ThreatProtectionCategory?
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Доступные категории
            ForEach(card.protectionFeatures) { category in
                categoryView(category: category)
            }
            
            // Заблокированные категории
            ForEach(ThreatProtectionCategory.allCases.filter { !card.protectionFeatures.contains($0) }) { category in
                lockedCategoryView(category: category)
            }
        }
    }
    
    // MARK: - Карточка категории (доступна)
    
    private func categoryView(category: ThreatProtectionCategory) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Button(action: {
                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                    if expandedCategory == category {
                        expandedCategory = nil
                    } else {
                        expandedCategory = category
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack {
                    Text(category.emoji)
                        .font(.system(size: 20))
                    
                    Text(category.localizedTitle(localizationManager))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                        .fixedSize(horizontal: true, vertical: false)
                    
                    Text(String(format: localizationManager.localized("tariff_protection_category_count"), category.count))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(1)
                    
                    Spacer()
                    
                    Image(systemName: expandedCategory == category ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.xs)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(category.localizedTitle(localizationManager)), \(category.count) ф.")
                .accessibilityHint(expandedCategory == category ? "Нажмите, чтобы свернуть список угроз" : "Нажмите, чтобы развернуть список угроз")
            }
            .buttonStyle(PlainButtonStyle())
            
            // Список угроз (раскрывается)
            if expandedCategory == category {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    ForEach(Array(category.localizedThreats(localizationManager).enumerated()), id: \.offset) { index, threat in
                        HStack(spacing: Spacing.xs) {
                            Text("•")
                                .foregroundColor(.textSecondary)
                            
                            Text(threat)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(.leading, Spacing.m)
                    }
                }
                .padding(.top, Spacing.xs)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.successGreen.opacity(0.1))
        )
    }
    
    // MARK: - Карточка категории (заблокирована)
    
    private func lockedCategoryView(category: ThreatProtectionCategory) -> some View {
        HStack {
            Text(category.emoji)
                .font(.system(size: 20))
            
            Text(category.localizedTitle(localizationManager))
                .font(.body)
                .foregroundColor(.textSecondary)
                .lineLimit(1)
                .fixedSize(horizontal: true, vertical: false)
            
            Text(String(format: localizationManager.localized("tariff_protection_category_count"), category.count))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .lineLimit(1)
            
            Spacer()
            
            // Badge с требуемым тарифом
            tariffBadge(for: category.requiredTariff)
            
            Image(systemName: "lock.fill")
                .font(.caption)
                .foregroundColor(.warningOrange)
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.warningOrange.opacity(0.1))
        )
    }
    
    // MARK: - Badge тарифа
    
    private func tariffBadge(for tariff: TariffType) -> some View {
        let (badgeText, badgeColor): (String, Color) = {
            switch tariff {
            case .trial:
                return (localizationManager.localized("tariffs_trial"), .green)
            case .free:
                return (localizationManager.localized("tariffs_free"), .gray)
            case .personal:
                return (localizationManager.localized("tariffs_personal"), .blue)
            case .family:
                return (localizationManager.localized("tariffs_family"), .orange)
            case .premium:
                return (localizationManager.localized("tariffs_premium"), .purple)
            }
        }()
        
        return Text(badgeText)
            .font(.system(size: 10, weight: .semibold))
            .foregroundColor(.white)
            .lineLimit(1)
            .fixedSize(horizontal: true, vertical: false)
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .frame(minWidth: 50, maxWidth: 70, minHeight: 18, maxHeight: 18)
            .background(
                Capsule()
                    .fill(badgeColor.opacity(0.9))
            )
    }
}

// MARK: - Секция родительского контроля

struct ParentalControlSection: View {
    let card: TariffCard
    @Binding var expandedModule: ParentalControlModule?
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Доступные модули
            ForEach(ParentalControlModule.allCases) { module in
                let moduleFeatures = module.features(for: card.tariffType)
                let allModuleFeatures = module.allFeatures
                
                if !moduleFeatures.isEmpty {
                    // Модуль с доступными функциями
                    moduleView(module: module, availableFeatures: moduleFeatures, allFeatures: allModuleFeatures)
                } else {
                    // Модуль полностью заблокирован
                    lockedModuleView(module: module, allFeatures: allModuleFeatures)
                }
            }
        }
    }
    
    // MARK: - Карточка модуля (есть доступные функции)
    
    private func moduleView(
        module: ParentalControlModule,
        availableFeatures: [ParentalControlFeature],
        allFeatures: [ParentalControlFeature]
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Button(action: {
                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                    if expandedModule == module {
                        expandedModule = nil
                    } else {
                        expandedModule = module
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack {
                    Text(module.emoji)
                        .font(.system(size: 20))
                    
                    Text(module.localizedTitle(localizationManager))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                        .fixedSize(horizontal: true, vertical: false)
                    
                    Text("(\(availableFeatures.count)/\(allFeatures.count))")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(1)
                    
                    Spacer()
                    
                    Image(systemName: expandedModule == module ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.xs)
            }
            .buttonStyle(PlainButtonStyle())
            
            // Список функций (раскрывается)
            if expandedModule == module {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    // Доступные функции
                    ForEach(availableFeatures) { feature in
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.successGreen)
                                .font(.system(size: 14))
                            
                            Text(feature.localizedTitle(localizationManager))
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        .padding(.leading, Spacing.m)
                    }
                    
                    // Заблокированные функции
                    ForEach(allFeatures.filter { feature in
                        !availableFeatures.contains { $0.id == feature.id }
                    }) { feature in
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "lock.fill")
                                .foregroundColor(.warningOrange)
                                .font(.system(size: 14))
                            
                            Text(feature.localizedTitle(localizationManager))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            tariffBadge(for: feature.requiredTariff)
                        }
                        .padding(.leading, Spacing.m)
                    }
                }
                .padding(.top, Spacing.xs)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.successGreen.opacity(0.1))
        )
    }
    
    // MARK: - Карточка модуля (полностью заблокирована)
    
    private func lockedModuleView(module: ParentalControlModule, allFeatures: [ParentalControlFeature]) -> some View {
        let requiredTariff = allFeatures.first?.requiredTariff ?? .personal
        
        return HStack {
            Text(module.emoji)
                .font(.system(size: 20))
            
            Text(module.localizedTitle(localizationManager))
                .font(.body)
                .foregroundColor(.textSecondary)
                .lineLimit(1)
                .fixedSize(horizontal: true, vertical: false)
            
            Text("(\(allFeatures.count) ф.)")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .lineLimit(1)
            
            Spacer()
            
            tariffBadge(for: requiredTariff)
            
            Image(systemName: "lock.fill")
                .font(.caption)
                .foregroundColor(.warningOrange)
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.warningOrange.opacity(0.1))
        )
    }
    
    // MARK: - Badge тарифа
    
    private func tariffBadge(for tariff: TariffType) -> some View {
        let (badgeText, badgeColor): (String, Color) = {
            switch tariff {
            case .trial:
                return (localizationManager.localized("tariffs_trial"), .green)
            case .free:
                return (localizationManager.localized("tariffs_free"), .gray)
            case .personal:
                return (localizationManager.localized("tariffs_personal"), .blue)
            case .family:
                return (localizationManager.localized("tariffs_family"), .orange)
            case .premium:
                return (localizationManager.localized("tariffs_premium"), .purple)
            }
        }()
        
        return Text(badgeText)
            .font(.system(size: 10, weight: .semibold))
            .foregroundColor(.white)
            .lineLimit(1)
            .fixedSize(horizontal: true, vertical: false)
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .frame(minWidth: 50, maxWidth: 70, minHeight: 18, maxHeight: 18)
            .background(
                Capsule()
                    .fill(badgeColor.opacity(0.9))
            )
    }
}

