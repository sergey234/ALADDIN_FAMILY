import SwiftUI

/// 🛡️ Расширенная карточка категории защиты
/// Включает: статус-индикатор, блок "Что это даёт", кнопку "Подробнее", мотивационный баннер
struct EnhancedThreatCategoryCard: View {
    let category: ThreatProtectionCategory
    @Binding var isExpanded: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var settingsManager = ProtectionSettingsManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    
    // MARK: - Computed Properties
    
    var isEnabled: Bool {
        settingsManager.settings.isEnabled(category)
    }
    
    var isAvailable: Bool {
        tariffManager.isCategoryAvailable(category)
    }
    
    var statusColor: Color {
        if !isAvailable {
            return .dangerRed
        } else if isEnabled {
            return .successGreen
        } else {
            return .warningOrange
        }
    }
    
    var statusIndicator: String {
        if !isAvailable {
            return "🔴"
        } else if isEnabled {
            return "🟢"
        } else {
            return "🟡"
        }
    }
    
    var statusText: String {
        if !isAvailable {
            return localizationManager.localized("protection_status_unavailable")
        } else if isEnabled {
            return localizationManager.localized("protection_status_available")
        } else {
            return localizationManager.localized("protection_status_partial")
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с статусом
            headerView
            
            if isExpanded {
                expandedContent
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(backgroundColor)
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(borderColor, lineWidth: 1)
                )
        )
        .cardShadow()
    }
    
    // MARK: - Header View
    
    private var headerView: some View {
        Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                isExpanded.toggle()
            }
            HapticFeedback.selection()
        }) {
            HStack(spacing: Spacing.m) {
                Text(category.emoji)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(category.localizedTitle(localizationManager))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    HStack(spacing: Spacing.xs) {
                        Text("\(category.count) \(localizationManager.localized("protection_threats_count"))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Text("•")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Text(statusText)
                            .font(.caption)
                            .foregroundColor(statusColor)
                    }
                }
                
                Spacer()
                
                // Статус-индикатор
                VStack(spacing: Spacing.xxs) {
                    Text(statusIndicator)
                        .font(.system(size: 16))
                    
                    Circle()
                        .fill(statusColor)
                        .frame(width: 8, height: 8)
                }
                
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .foregroundColor(.secondaryGold)
                    .font(.caption)
            }
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Expanded Content
    
    @ViewBuilder
    private var expandedContent: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Блок "Что это даёт"
            benefitView
            
            // Мотивационный баннер (если недоступно)
            if !isAvailable {
                MotivationBanner(
                    category: category,
                    requiredTariff: category.requiredTariff
                )
            }
            
            // Кнопка "Подробнее"
            detailsButton
        }
        .padding(.top, Spacing.xs)
    }
    
    // MARK: - Benefit View
    
    private var benefitView: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(localizationManager.localized("protection_what_this_gives"))
                .font(.captionBold)
                .foregroundColor(.textSecondary)
            
            Text(category.benefit)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, Spacing.xs)
    }
    
    // MARK: - Details Button
    
    private var detailsButton: some View {
        Button(action: {
            handleDetailsTap()
        }) {
            HStack {
                Text(localizationManager.localized("protection_details_button"))
                    .font(.body)
                    .fontWeight(.medium)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
            }
            .foregroundColor(.secondaryGold)
            .padding(.vertical, Spacing.xs)
        }
    }
    
    // MARK: - Background & Border
    
    private var backgroundColor: Color {
        if isEnabled {
            return Color.successGreen.opacity(0.1)
        } else {
            return Color.backgroundMedium.opacity(0.5)
        }
    }
    
    private var borderColor: Color {
        if isEnabled {
            return Color.successGreen.opacity(0.3)
        } else if !isAvailable {
            return Color.dangerRed.opacity(0.3)
        } else {
            return Color.secondaryGold.opacity(0.3)
        }
    }
    
    // MARK: - Navigation
    
    private func handleDetailsTap() {
        HapticFeedback.selection()
        
        // ✅ ПРАВИЛЬНАЯ ЛОГИКА: Если функция недоступна → ВСЕГДА на Тарифы
        if isAvailable {
            // Функция доступна → переход на экран настроек
            if let settingsScreen = category.settingsScreen {
                navigationManager.navigateTo(settingsScreen)
            } else {
                // Если нет специфичного экрана → общий экран настроек защиты
                navigationManager.navigateTo(.threatProtectionSettings)
            }
        } else {
            // ✅ Функция недоступна → ВСЕГДА на Тарифы (не на VPN или другие экраны!)
            navigationManager.navigateTo(.tariffs)
        }
    }
}

#if DEBUG
struct EnhancedThreatCategoryCard_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.m) {
            EnhancedThreatCategoryCard(
                category: .cyberThreats,
                isExpanded: .constant(true)
            )
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
            
            EnhancedThreatCategoryCard(
                category: .deepfakes,
                isExpanded: .constant(true)
            )
            .environmentObject(LocalizationManager())
            .environmentObject(NavigationManager())
        }
        .padding()
        .background(Color.backgroundDark)
    }
}
#endif

