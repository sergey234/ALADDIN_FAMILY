import SwiftUI

/// 📋 Строка категории защиты (для экрана настроек)
/// Используется в ThreatProtectionSettingsScreen для отображения категории с переключателем
struct ProtectionCategoryRow: View {
    let category: ThreatProtectionCategory
    @Binding var isEnabled: Bool
    let isAvailable: Bool
    let onDetailsTap: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(category.emoji)
                .font(.system(size: 24))
            
            // Название и описание
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(category.localizedTitle(localizationManager))
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("\(category.count) \(localizationManager.localized("protection_threats_count"))")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            if isAvailable, category.settingsScreen != nil {
                Button(action: onDetailsTap) {
                    openHubLabel
                }
                .buttonStyle(.plain)
            }
            
            // Переключатель или баннер
            if isAvailable {
                ALADDINToggle(isOn: $isEnabled)
            } else {
                // Компактный баннер для недоступных функций
                HStack(spacing: Spacing.xs) {
                    Image(systemName: "lock.fill")
                        .font(.caption2)
                        .foregroundColor(.warningOrange)
                    
                    Text(category.requiredTariff.title(localizationManager: localizationManager))
                        .font(.caption)
                        .foregroundColor(.warningOrange)
                }
                .padding(.horizontal, Spacing.xs)
                .padding(.vertical, Spacing.xxs)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.warningOrange.opacity(0.1))
                )
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(
            cornerRadius: CornerRadius.medium,
            accentStripColor: isEnabled ? .statusProtected : nil
        )
        .contentShape(Rectangle())
        .onTapGesture {
            guard !isAvailable else { return }
            onDetailsTap()
        }
    }
    
    @ViewBuilder
    private var openHubLabel: some View {
        let titleKey = category == .deepfakes
            ? "protection_open_check_button"
            : "protection_open_hub_button"
        HStack(spacing: 4) {
            Text(localizationManager.localized(titleKey))
                .font(.caption.weight(.semibold))
            Image(systemName: "chevron.right")
                .font(.caption2.weight(.semibold))
        }
        .foregroundColor(.primaryBlue)
        .padding(.horizontal, Spacing.xs)
        .padding(.vertical, Spacing.xxs)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.primaryBlue.opacity(0.12))
        )
        .accessibilityLabel(localizationManager.localized(titleKey))
    }
}

#if DEBUG
struct ProtectionCategoryRow_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.m) {
            ProtectionCategoryRow(
                category: .cyberThreats,
                isEnabled: .constant(true),
                isAvailable: true,
                onDetailsTap: {}
            )
            .environmentObject(LocalizationManager())
            
            ProtectionCategoryRow(
                category: .deepfakes,
                isEnabled: .constant(false),
                isAvailable: false,
                onDetailsTap: {}
            )
            .environmentObject(LocalizationManager())
        }
        .padding()
        .background(Color.backgroundDark)
    }
}
#endif

