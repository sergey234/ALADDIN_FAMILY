import SwiftUI

/// 🎮 Games Parental Control View
/// Панель управления геймификацией
/// Источник дизайна: /mobile/wireframes/14c_games_parental_control.html
struct GamesParentalControlView: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isWheelEnabled: Bool = true
    @State private var isTournamentEnabled: Bool = true
    @State private var isUniverseEnabled: Bool = true
    @State private var wheelFrequency: Double = 1
    @State private var prizeSector1: Double = 5
    @State private var prizeSector2: Double = 10
    @State private var prizeSector3: Double = 20
    @State private var prizeSector4: Double = 50
    @State private var prizeSector5: Double = 100
    @State private var prizeSector6: Double = 500
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "УПРАВЛЕНИЕ ИГРАМИ",
                    subtitle: "Родительский контроль",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Информация
                        infoCard
                        
                        // Колесо удачи
                        wheelGameCard
                        
                        // Семейный турнир
                        tournamentGameCard
                        
                        // Единорог-питомец (всегда ВКЛ)
                        petGameCard
                        
                        // Единорог-вселенная
                        universeGameCard
                        
                        // Быстрые действия
                        quickActions
                        
                        // Текущие настройки
                        currentSettings
                        
                        // Кнопка сохранить
                        saveButton
                        
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        HStack(spacing: Spacing.m) {
            Text("💡")
                .font(.system(size: 20))
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("Родительский контроль игр")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Text("Здесь вы можете включать/отключать игровые элементы. Единорог-питомец всегда активен - это основная мотивация! 🦄")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.primaryBlue.opacity(0.15))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Wheel Game Card
    
    private var wheelGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с переключателем
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🎰")
                        .font(.system(size: 22))
                    Text("Колесо удачи")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: $isWheelEnabled)
                    .labelsHidden()
            }
            
            // Описание
            Text("Ребёнок крутит колесо и получает случайный приз от 5 до 500 🦄. Призы: 1️⃣ 5🦄 • 2️⃣ 10🦄 • 3️⃣ 20🦄 • 4️⃣ 50🦄 • 5️⃣ 100🦄 • 6️⃣ 500🦄 ДЖЕКПОТ!")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if isWheelEnabled {
                // Частота вращений
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Частота вращений в день:")
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    Slider(value: $wheelFrequency, in: 1...7, step: 1)
                        .accentColor(.successGreen)
                    
                    HStack {
                        Text("1 раз")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(Int(wheelFrequency)) \(wheelFrequency == 1 ? "раз в день" : (wheelFrequency <= 4 ? "раза в день" : "раз в день"))")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.successGreen)
                        Spacer()
                        Text("7 раз")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                // Настройка призов
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("⚙️ Настройка призов на барабане:")
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    prizeSlider(sector: 1, chance: "40%", prize: $prizeSector1, range: 1...50)
                    prizeSlider(sector: 2, chance: "30%", prize: $prizeSector2, range: 5...100)
                    prizeSlider(sector: 3, chance: "15%", prize: $prizeSector3, range: 10...150)
                    prizeSlider(sector: 4, chance: "10%", prize: $prizeSector4, range: 20...200)
                    prizeSlider(sector: 5, chance: "4%", prize: $prizeSector5, range: 50...300)
                    prizeSlider(sector: 6, chance: "1%", prize: $prizeSector6, range: 100...1000, isJackpot: true)
                    
                    Text("💡 Совет: Начните с малых призов и постепенно увеличивайте для мотивации!")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .padding(Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .opacity(isWheelEnabled ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func prizeSlider(sector: Int, chance: String, prize: Binding<Double>, range: ClosedRange<Double>, isJackpot: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text("\(sector)️⃣ Сектор \(sector)\(isJackpot ? " ДЖЕКПОТ" : "") (\(chance) шанс):")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                Spacer()
                Text("\(Int(prize.wrappedValue)) 🦄")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(Color(hex: "FFD700"))
            }
            
            Slider(value: prize, in: range, step: 1)
                .accentColor(Color(hex: "FFD700"))
                .frame(height: 4)
        }
    }
    
    // MARK: - Tournament Game Card
    
    private var tournamentGameCard: some View {
        gameCard(
            icon: "🏆",
            title: "Семейный турнир",
            description: "Еженедельное соревнование всей семьи. 5 типов турниров: отличники 📚, помощники 🧹, без конфликтов 😊, чтение 📖, универсальный 🎯. Призы: 🥇 +50 • 🥈 +30 • 🥉 +20 🦄",
            isEnabled: $isTournamentEnabled
        )
    }
    
    // MARK: - Pet Game Card
    
    private var petGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🦄")
                        .font(.system(size: 22))
                    Text("Единорог-питомец")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Text("🔒 ВСЕГДА ВКЛ")
                    .font(.captionSmall)
                    .foregroundColor(Color(hex: "C084FC"))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(
                        Capsule()
                            .fill(Color(hex: "A855F7").opacity(0.3))
                            .overlay(
                                Capsule()
                                    .stroke(Color(hex: "C084FC"), lineWidth: 1)
                            )
                    )
            }
            
            Text("Тамагочи-питомец с индикаторами ❤️🍎⭐😊. Ребёнок кормит, играет, гладит. 4 стадии эволюции. Нельзя отключить - это основа мотивации!")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color(hex: "A855F7").opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color(hex: "C084FC"), lineWidth: 1)
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Universe Game Card
    
    private var universeGameCard: some View {
        gameCard(
            icon: "🌳",
            title: "Единорог-вселенная",
            description: "Сад единорогов, коллекция 10 видов, сторителлинг 5 глав. Чем больше единорогов, тем красивее сад!",
            isEnabled: $isUniverseEnabled
        )
    }
    
    private func gameCard(icon: String, title: String, description: String, isEnabled: Binding<Bool>) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text(icon)
                        .font(.system(size: 22))
                    Text(title)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: isEnabled)
                    .labelsHidden()
            }
            
            Text(description)
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .opacity(isEnabled.wrappedValue ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Quick Actions
    
    private var quickActions: some View {
        VStack(spacing: Spacing.s) {
            Button(action: disableAllGames) {
                Text("Отключить все (кроме 🦄)")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.dangerRed)
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.dangerRed.opacity(0.2))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .stroke(Color.dangerRed, lineWidth: 2)
                            )
                    )
            }
            .buttonStyle(PlainButtonStyle())
            
            Button(action: enableAllGames) {
                Text("Включить все")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.successGreen)
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.successGreen.opacity(0.2))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .stroke(Color.successGreen, lineWidth: 2)
                            )
                    )
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Current Settings
    
    private var currentSettings: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text("📊 Текущие настройки:")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                if isWheelEnabled {
                    Text("• Колесо удачи: ✅ Включено (\(Int(wheelFrequency)) \(wheelFrequency == 1 ? "раз в день" : "раз в день"))")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                    Text("  Призы: 1️⃣\(Int(prizeSector1)) • 2️⃣\(Int(prizeSector2)) • 3️⃣\(Int(prizeSector3)) • 4️⃣\(Int(prizeSector4)) • 5️⃣\(Int(prizeSector5)) • 6️⃣\(Int(prizeSector6)) 🦄")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                } else {
                    Text("• Колесо удачи: ❌ Отключено")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                }
                
                Text(isTournamentEnabled ? "• Семейный турнир: ✅ Включен" : "• Семейный турнир: ❌ Отключен")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                
                Text("• Единорог-питомец: 🔒 Всегда включен")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                
                Text(isUniverseEnabled ? "• Единорог-вселенная: ✅ Включена" : "• Единорог-вселенная: ❌ Отключена")
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Save Button
    
    private var saveButton: some View {
        Button(action: saveSettings) {
            Text("💾 Сохранить настройки")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    LinearGradient(
                        colors: [.successGreen, .successGreen.opacity(0.8)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Actions
    
    private func disableAllGames() {
        isWheelEnabled = false
        isTournamentEnabled = false
        isUniverseEnabled = false
        
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        print("Все игры отключены (кроме питомца)")
    }
    
    private func enableAllGames() {
        isWheelEnabled = true
        isTournamentEnabled = true
        isUniverseEnabled = true
        
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        print("Все игры включены")
    }
    
    private func saveSettings() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        print("💾 Настройки сохранены:")
        print("- Колесо: \(isWheelEnabled ? "ВКЛ" : "ВЫКЛ"), частота: \(Int(wheelFrequency))")
        print("- Призы: \(Int(prizeSector1)), \(Int(prizeSector2)), \(Int(prizeSector3)), \(Int(prizeSector4)), \(Int(prizeSector5)), \(Int(prizeSector6))")
        print("- Турнир: \(isTournamentEnabled ? "ВКЛ" : "ВЫКЛ")")
        print("- Вселенная: \(isUniverseEnabled ? "ВКЛ" : "ВЫКЛ")")
        
        dismiss()
    }
}

// MARK: - Preview

#if DEBUG
struct GamesParentalControlView_Previews: PreviewProvider {
    static var previews: some View {
        GamesParentalControlView()
    }
}
#endif




