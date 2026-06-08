import SwiftUI

/// ➕ Add More Member Card
/// Карточка "Добавить ещё участника" (Вариант 1)
struct AddMoreMemberCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text("➕")
                    .font(.system(size: 32))
                    .foregroundColor(.secondaryGold.opacity(0.8))
                
                Text(localizationManager.localized("family_add_more_member"))
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.secondaryGold)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                
                Spacer()
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(Spacing.s)
            .stormGlassCard(cornerRadius: 10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .strokeBorder(
                        Color.secondaryGold.opacity(0.35),
                        style: StrokeStyle(lineWidth: 1, dash: [3, 3])
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

