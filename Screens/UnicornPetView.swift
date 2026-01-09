import SwiftUI

/// 🦄 Unicorn Pet View
/// Единорог-питомец (тамагочи)
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct UnicornPetView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохраняем состояние питомца в AppStorage
    @AppStorage("pet_level") private var petLevel: Int = 2
    @AppStorage("pet_love") private var love: Double = 0.75
    @AppStorage("pet_hunger") private var hunger: Double = 0.6
    @AppStorage("pet_energy") private var energy: Double = 0.8
    @AppStorage("pet_mood") private var mood: Double = 0.7
    @AppStorage("pet_evolution_stage") private var evolutionStage: String = "Teen"
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана питомца-единорога")
            
            VStack(spacing: 0) {
                // Header с кнопкой "← Назад"
                header
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Питомец
                        petView
                    
                    // Индикаторы
                    indicatorsView
                    
                    // Действия
                    actionsView
                    
                        // Адаптивный отступ (Apple HIG)
                        Spacer(minLength: 0)
                    }
                    .padding(.top, Spacing.m)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое экрана питомца-единорога")
            }
        }
        .navigationBarHidden(true)
        .task {
            print("🚨 UnicornPetView загружен!")
        }
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack {
            Button(action: {
                HapticFeedback.impact(.light)
                navigationManager.goBack()
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.textPrimary)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
            }
            
            Text("🦄 \(localizationManager.localized("unicorn_pet_title"))")
                .font(.h2)
                .foregroundColor(Color(hex: "A855F7"))
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Pet View
    
    private var petView: some View {
        VStack(spacing: Spacing.m) {
            Text("🦄")
                .font(.system(size: 100))
                .accessibilityLabel("Единорог питомец")
            
            Text(String(format: localizationManager.localized("unicorn_pet_level"), petLevel))
                .font(.h2)
                .foregroundColor(.primaryBlue)
                .accessibilityLabel(String(format: localizationManager.localized("unicorn_pet_level"), petLevel))
            
            Text(String(format: localizationManager.localized("unicorn_pet_stage"), getLocalizedEvolutionStage(evolutionStage)))
                .font(.body)
                .foregroundColor(.textSecondary)
                .accessibilityLabel(String(format: localizationManager.localized("unicorn_pet_stage"), getLocalizedEvolutionStage(evolutionStage)))
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.xl)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
        .appGlassmorphism()
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Карточка питомца единорога")
    }
    
    private var indicatorsView: some View {
        VStack(spacing: Spacing.s) {
            indicatorRow(icon: "❤️", label: localizationManager.localized("unicorn_pet_love"), value: love, color: .dangerRed)
            indicatorRow(icon: "🍎", label: localizationManager.localized("unicorn_pet_hunger"), value: hunger, color: .successGreen)
            indicatorRow(icon: "⭐", label: localizationManager.localized("unicorn_pet_energy"), value: energy, color: .warningOrange)
            indicatorRow(icon: "😊", label: localizationManager.localized("unicorn_pet_mood"), value: mood, color: .primaryBlue)
        }
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Индикаторы состояния питомца")
    }
    
    private func indicatorRow(icon: String, label: String, value: Double, color: Color) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(icon)")
            
            Text(label)
                .font(.body)
                .foregroundColor(.textPrimary)
                .frame(width: 100, alignment: .leading)
                .accessibilityLabel("\(label)")
            
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
            .accessibilityLabel("Прогресс-бар \(label): \(Int(value * 100)) процентов")
            
            Text("\(Int(value * 100))%")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .frame(width: 40, alignment: .trailing)
                .accessibilityLabel("\(Int(value * 100)) процентов")
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(label): \(Int(value * 100)) процентов")
    }
    
    private var actionsView: some View {
        HStack(spacing: Spacing.m) {
            actionButton(icon: "🍎", title: localizationManager.localized("unicorn_pet_feed"), cost: String(format: localizationManager.localized("unicorn_pet_cost_unicorns"), 10)) {
                hunger = min(1.0, hunger + 0.2)
            }
            
            actionButton(icon: "🎮", title: localizationManager.localized("unicorn_pet_play"), cost: String(format: localizationManager.localized("unicorn_pet_cost_unicorns"), 5)) {
                energy = min(1.0, energy + 0.15)
            }
            
            actionButton(icon: "💕", title: localizationManager.localized("unicorn_pet_pet"), cost: localizationManager.localized("unicorn_pet_cost_free")) {
                love = min(1.0, love + 0.1)
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Действия с питомцем")
    }
    
    private func actionButton(icon: String, title: String, cost: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text(icon)
                    .font(.system(size: 32))
                    .accessibilityLabel("Иконка: \(icon)")
                Text(title)
                    .font(.caption)
                    .foregroundColor(.textPrimary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                Text(cost)
                    .font(.captionSmall)
                    .foregroundColor(.successGreen)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
            .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityLabel("\(title) - \(cost)")
        .accessibilityHint("Нажмите для \(title.lowercased()) питомца")
    }
    
    // MARK: - Helper Methods
    
    private func getLocalizedEvolutionStage(_ stage: String) -> String {
        switch stage.lowercased() {
        case "baby":
            return localizationManager.localized("unicorn_pet_evolution_baby")
        case "teen":
            return localizationManager.localized("unicorn_pet_evolution_teen")
        case "adult":
            return localizationManager.localized("unicorn_pet_evolution_adult")
        case "legendary":
            return localizationManager.localized("unicorn_pet_evolution_legendary")
        default:
            return stage
        }
    }
}

#if DEBUG
struct UnicornPetView_Previews: PreviewProvider {
    static var previews: some View {
        UnicornPetView()
            .environmentObject(LocalizationManager())
    }
}
#endif



