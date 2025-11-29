import SwiftUI

/// ➕ Add More Member Card
/// Карточка "Добавить ещё участника" (Вариант 1)
struct AddMoreMemberCard: View {
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text("➕")
                    .font(.system(size: 32))
                    .foregroundColor(.secondaryGold.opacity(0.8))
                
                Text("Добавить ещё")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.secondaryGold)
                    .lineLimit(1)
                
                Text("участника")
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(1)
                
                Spacer()
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(Spacing.s)
            .background(Color.secondaryGold.opacity(0.05))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .strokeBorder(
                        Color.secondaryGold.opacity(0.2),
                        style: StrokeStyle(lineWidth: 1, dash: [3, 3])
                    )
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

