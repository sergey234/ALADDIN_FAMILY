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
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(isEnabled ? Color.successGreen.opacity(0.1) : Color.clear)
        )
        .contentShape(Rectangle())
        .onTapGesture {
            if isAvailable {
                // Переключение только для доступных категорий
                withAnimation {
                    isEnabled.toggle()
                }
                HapticFeedback.selection()
            } else {
                // Для недоступных - переход на тарифы
                onDetailsTap()
            }
        }
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

