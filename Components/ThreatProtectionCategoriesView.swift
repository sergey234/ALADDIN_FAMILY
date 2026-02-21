import SwiftUI

struct ThreatProtectionCategoriesView: View {
    @Binding var expandedCategory: ThreatProtectionCategory?
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            ForEach(ThreatProtectionCategory.allCases) { category in
                categorySection(for: category)
            }
        }
    }
    
    private func categorySection(for category: ThreatProtectionCategory) -> some View {
        let isEnabled = settingsManager.settings.isEnabled(category)
        let isAvailable = tariffManager.isCategoryAvailable(category)
        
        // Определяем статус и цвет
        let (statusIndicator, statusColor): (String, Color) = {
            if !isAvailable {
                return ("🔴", .dangerRed)
            } else if isEnabled {
                return ("🟢", .successGreen)
            } else {
                return ("🟡", .warningOrange)
            }
        }()
        
        return VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.2, dampingFraction: 0.8)) {
                    if expandedCategory == category {
                        expandedCategory = nil
                    } else {
                        expandedCategory = category
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.s) {
                    Text(category.emoji)
                        .font(.system(size: 20))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(category.localizedTitle(localizationManager))
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        
                        HStack(spacing: Spacing.xs) {
                            Text("\(category.count) \(localizationManager.localized("protection_threats_count"))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            // Бейдж тарифа
                            tariffBadge(for: category.requiredTariff)
                        }
                    }
                    
                    // Статус-индикатор с плавной анимацией
                    VStack(spacing: Spacing.xxs) {
                        Text(statusIndicator)
                            .font(.system(size: 14))
                        
                        Circle()
                            .fill(statusColor)
                            .frame(width: 8, height: 8)
                            .animation(.easeInOut(duration: 0.25), value: statusColor) // ✅ Плавная анимация изменения цвета
                    }
                    
                    Image(systemName: expandedCategory == category ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.s)
            }
            
            if expandedCategory == category {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    ForEach(Array(category.localizedThreats(localizationManager).enumerated()), id: \.element) { index, threat in
                        // ✅ УЛУЧШЕННАЯ ВИЗУАЛИЗАЦИЯ: Каждая угроза с цветной полоской и бейджем тарифа
                        ThreatTariffRow(
                            threat: threat,
                            tariff: category.requiredTariff
                        )
                    }
                }
                .padding(.leading, Spacing.m)
                .padding(.top, Spacing.xs)
                .padding(.bottom, Spacing.s)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(.vertical, Spacing.xs)
    }
    
    // MARK: - Tariff Badge
    
    @ViewBuilder
    private func tariffBadge(for tariff: TariffType) -> some View {
        let (badgeText, badgeColor): (String, Color) = {
            switch tariff {
            case .free:
                return (localizationManager.localized("tariffs_free"), .gray)
            case .personal:
                return (localizationManager.localized("tariffs_personal"), .blue)
            case .family:
                return (localizationManager.localized("tariffs_family"), .orange)
            case .premium:
                return (localizationManager.localized("tariffs_premium"), .purple)
            case .ultimate:
                return (localizationManager.localized("tariffs_ultimate"), .red)
            }
        }()
        
        Text(badgeText)
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
