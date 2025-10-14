import SwiftUI

/// 🦄 Unicorn Pet View
/// Единорог-питомец (тамагочи)
/// Источник дизайна: /mobile/wireframes/unicorn_pet_component.html
struct UnicornPetView: View {
    
    @State private var petLevel = 2
    @State private var love: Double = 0.75
    @State private var hunger: Double = 0.6
    @State private var energy: Double = 0.8
    @State private var mood: Double = 0.7
    @State private var evolutionStage = "Teen"
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🦄 МОЙ ПИТОМЕЦ")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    // Питомец
                    petView
                    
                    // Индикаторы
                    indicatorsView
                    
                    // Действия
                    actionsView
                    
                    Spacer()
                }
                .padding(.top, Spacing.xxl)
            }
        }
    }
    
    private var petView: some View {
        VStack(spacing: Spacing.m) {
            Text("🦄")
                .font(.system(size: 100))
            
            Text("Уровень \(petLevel)")
                .font(.h2)
                .foregroundColor(.primaryBlue)
            
            Text("Стадия: \(evolutionStage)")
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.xlarge)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var indicatorsView: some View {
        VStack(spacing: Spacing.s) {
            indicatorRow(icon: "❤️", label: "Любовь", value: love, color: .dangerRed)
            indicatorRow(icon: "🍎", label: "Сытость", value: hunger, color: .successGreen)
            indicatorRow(icon: "⭐", label: "Энергия", value: energy, color: .warningOrange)
            indicatorRow(icon: "😊", label: "Настроение", value: mood, color: .primaryBlue)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func indicatorRow(icon: String, label: String, value: Double, color: Color) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
            
            Text(label)
                .font(.body)
                .foregroundColor(.textPrimary)
                .frame(width: 100, alignment: .leading)
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 5)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 10)
                    
                    RoundedRectangle(cornerRadius: 5)
                        .fill(color)
                        .frame(width: geometry.size.width * value, height: 10)
                }
            }
            .frame(height: 10)
            
            Text("\(Int(value * 100))%")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .frame(width: 40, alignment: .trailing)
        }
    }
    
    private var actionsView: some View {
        HStack(spacing: Spacing.m) {
            actionButton(icon: "🍎", title: "Покормить", cost: "10 🦄") {
                hunger = min(1.0, hunger + 0.2)
            }
            
            actionButton(icon: "🎮", title: "Поиграть", cost: "5 🦄") {
                energy = min(1.0, energy + 0.15)
            }
            
            actionButton(icon: "💕", title: "Погладить", cost: "FREE") {
                love = min(1.0, love + 0.1)
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func actionButton(icon: String, title: String, cost: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text(icon)
                    .font(.system(size: 32))
                Text(title)
                    .font(.caption)
                    .foregroundColor(.textPrimary)
                Text(cost)
                    .font(.captionSmall)
                    .foregroundColor(.successGreen)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    UnicornPetView()
}




