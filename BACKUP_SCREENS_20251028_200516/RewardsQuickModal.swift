import SwiftUI

/// 🦄 Rewards Quick Modal
/// Упрощённое модальное окно для быстрых действий с вознаграждениями
/// Источник дизайна: /mobile/wireframes/03_family_screen.html (модальное окно)
struct RewardsQuickModal: View {
    
    @Environment(\.dismiss) private var dismiss
    @Binding var unicornBalance: Int
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: Spacing.l) {
                    // Баланс
                    VStack(spacing: Spacing.m) {
                        Text("🦄")
                            .font(.system(size: 48))
                        
                        Text("\(unicornBalance)")
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(Color(hex: "C084FC"))
                        
                        Text("Единорогов на счету")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.l)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(Color(hex: "A855F7").opacity(0.15))
                    )
                    .padding(.horizontal, Spacing.screenPadding)
                    
                    // Быстрые действия
                    HStack(spacing: Spacing.m) {
                        quickActionButton(icon: "✅", title: "Вознаградить", color: .successGreen) {
                            rewardChild()
                        }
                        
                        quickActionButton(icon: "❌", title: "Наказать", color: .dangerRed) {
                            punishChild()
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    
                    Spacer()
                }
                .padding(.top, Spacing.l)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    HStack(spacing: Spacing.xs) {
                        Text("🦄")
                            .font(.system(size: 20))
                        Text("Вознаграждение ребёнка")
                            .font(.h3)
                            .foregroundColor(Color(hex: "C084FC"))
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    private func quickActionButton(icon: String, title: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text(icon)
                    .font(.system(size: 32))
                Text(title)
                    .font(.caption)
                    .foregroundColor(color)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(color.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(color, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func rewardChild() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        unicornBalance += 10
        dismiss()
    }
    
    private func punishChild() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        unicornBalance -= 10
        dismiss()
    }
}

#if DEBUG
struct RewardsQuickModal_Previews: PreviewProvider {
    static var previews: some View {
        RewardsQuickModal(unicornBalance: .constant(245))
    }
}
#endif



