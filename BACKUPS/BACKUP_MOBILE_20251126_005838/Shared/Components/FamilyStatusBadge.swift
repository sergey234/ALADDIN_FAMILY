import SwiftUI

/// 🏷️ Family Status Badge
/// Капсула статуса семейной защиты для карточки "Семья" на главном экране
struct FamilyStatusBadge: View {
    let status: FamilyProtectionStatus
    let localizationManager: LocalizationManager
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                // Иконка
                Image(systemName: status.iconName)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(status.iconColor)
                
                // Текст статуса
                Text(localizationManager.localized(status.titleLocalizationKey))
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(status.iconColor)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(status.color.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - FamilyProtectionStatus Extension

extension FamilyProtectionStatus {
    var iconColor: Color {
        switch self {
        case .active: return Color(red: 0.04, green: 0.55, blue: 0.28) // #0A8C47
        case .paused: return Color(red: 0.43, green: 0.45, blue: 0.52) // #6E7484
        case .attention: return Color(red: 0.88, green: 0.55, blue: 0.16) // #E08F29
        case .critical: return Color(red: 0.88, green: 0.26, blue: 0.27) // #E04345
        }
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyStatusBadge_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            FamilyStatusBadge(
                status: .active,
                localizationManager: LocalizationManager(),
                action: {}
            )
            
            FamilyStatusBadge(
                status: .paused,
                localizationManager: LocalizationManager(),
                action: {}
            )
            
            FamilyStatusBadge(
                status: .attention,
                localizationManager: LocalizationManager(),
                action: {}
            )
            
            FamilyStatusBadge(
                status: .critical,
                localizationManager: LocalizationManager(),
                action: {}
            )
        }
        .padding()
        .background(Color.gray.opacity(0.1))
    }
}
#endif


