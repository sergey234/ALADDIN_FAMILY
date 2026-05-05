import SwiftUI

/// 🎮 Games Parental Control Screen
/// Экран управления геймификацией
/// Источник дизайна: /mobile/wireframes/14c_games_parental_control.html
struct GamesParentalControlScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var parentAuthMessage: String?
    
    // Сохраняем настройки игр в AppStorage
    @AppStorage("games_wheel_enabled") private var isWheelEnabled: Bool = true
    @AppStorage("games_tournament_enabled") private var isTournamentEnabled: Bool = true
    @AppStorage("games_universe_enabled") private var isUniverseEnabled: Bool = true
    @AppStorage("games_wheel_frequency") private var wheelFrequency: Double = 1
    @AppStorage("games_wheel_prize_1") private var prizeSector1: Double = 5
    @AppStorage("games_wheel_prize_2") private var prizeSector2: Double = 10
    @AppStorage("games_wheel_prize_3") private var prizeSector3: Double = 20
    @AppStorage("games_wheel_prize_4") private var prizeSector4: Double = 50
    @AppStorage("games_wheel_prize_5") private var prizeSector5: Double = 100
    @AppStorage("games_wheel_prize_6") private var prizeSector6: Double = 500
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: localizationManager.localized("games_parental_nav_title"),
                    subtitle: localizationManager.localized("games_parental_nav_subtitle"),
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: {
                        navigationManager.goBack()
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
        .alert(
            localizationManager.localized("games_parental_auth_alert_title"),
            isPresented: Binding(
                get: { parentAuthMessage != nil },
                set: { if !$0 { parentAuthMessage = nil } }
            )
        ) {
            Button(localizationManager.localized("common_ok"), role: .cancel) {
                parentAuthMessage = nil
            }
        } message: {
            Text(parentAuthMessage ?? "")
        }
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        HStack(spacing: Spacing.m) {
            Text("💡")
                .font(.system(size: 20))
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(localizationManager.localized("games_parental_info_title"))
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("games_parental_info_description"))
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
                    Text(localizationManager.localized("games_parental_wheel_title"))
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: Binding(
                    get: { isWheelEnabled },
                    set: { newValue in
                        requestParentSessionForSettingChange {
                            isWheelEnabled = newValue
                        }
                    }
                ))
                    .labelsHidden()
            }
            
            // Описание
            Text(localizationManager.localized("games_parental_wheel_description"))
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if isWheelEnabled {
                // Частота вращений
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("games_parental_wheel_frequency_title"))
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    Slider(value: $wheelFrequency, in: 1...7, step: 1)
                        .accentColor(.successGreen)
                    
                    HStack {
                        Text(localizationManager.localized("games_parental_wheel_frequency_min"))
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(Int(wheelFrequency)) \(wheelFrequency == 1 ? "раз в день" : (wheelFrequency <= 4 ? "раза в день" : "раз в день"))")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.successGreen)
                        Spacer()
                        Text(localizationManager.localized("games_parental_wheel_frequency_max"))
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                // Настройка призов
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("games_parental_wheel_prizes_title"))
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    prizeSlider(sector: 1, chance: "40%", prize: $prizeSector1, range: 1...50)
                    prizeSlider(sector: 2, chance: "30%", prize: $prizeSector2, range: 5...100)
                    prizeSlider(sector: 3, chance: "15%", prize: $prizeSector3, range: 10...150)
                    prizeSlider(sector: 4, chance: "10%", prize: $prizeSector4, range: 20...200)
                    prizeSlider(sector: 5, chance: "4%", prize: $prizeSector5, range: 50...300)
                    prizeSlider(sector: 6, chance: "1%", prize: $prizeSector6, range: 100...1000, isJackpot: true)
                    
                    Text(localizationManager.localized("games_parental_wheel_tip"))
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
                Text(
                    isJackpot
                    ? localizationManager.localized("games_parental_wheel_sector_jackpot", sector, chance)
                    : localizationManager.localized("games_parental_wheel_sector", sector, chance)
                )
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
            title: localizationManager.localized("games_parental_tournament_title"),
            description: localizationManager.localized("games_parental_tournament_description"),
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
                    Text(localizationManager.localized("games_parental_pet_title"))
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Text(localizationManager.localized("games_parental_pet_always_on"))
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
            
            Text(localizationManager.localized("games_parental_pet_description"))
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
            title: localizationManager.localized("games_parental_universe_title"),
            description: localizationManager.localized("games_parental_universe_description"),
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
                
                Toggle("", isOn: Binding(
                    get: { isEnabled.wrappedValue },
                    set: { newValue in
                        requestParentSessionForSettingChange {
                            isEnabled.wrappedValue = newValue
                        }
                    }
                ))
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
            Button(action: {
                requestParentSessionForSettingChange {
                    disableAllGames()
                }
            }) {
                Text(localizationManager.localized("games_parental_disable_all"))
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
            
            Button(action: {
                requestParentSessionForSettingChange {
                    enableAllGames()
                }
            }) {
                Text(localizationManager.localized("games_parental_enable_all"))
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
            Text(localizationManager.localized("games_parental_current_settings_title"))
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                if isWheelEnabled {
                    Text(localizationManager.localized("games_parental_current_wheel_enabled", Int(wheelFrequency)))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                    Text(localizationManager.localized(
                        "games_parental_current_wheel_prizes",
                        Int(prizeSector1),
                        Int(prizeSector2),
                        Int(prizeSector3),
                        Int(prizeSector4),
                        Int(prizeSector5),
                        Int(prizeSector6)
                    ))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                } else {
                    Text(localizationManager.localized("games_parental_current_wheel_disabled"))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                }
                
                Text(
                    isTournamentEnabled
                    ? localizationManager.localized("games_parental_current_tournament_enabled")
                    : localizationManager.localized("games_parental_current_tournament_disabled")
                )
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                
                Text(localizationManager.localized("games_parental_current_pet_always_on"))
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                
                Text(
                    isUniverseEnabled
                    ? localizationManager.localized("games_parental_current_universe_enabled")
                    : localizationManager.localized("games_parental_current_universe_disabled")
                )
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
        Button(action: {
            requestParentSessionForSettingChange {
                saveSettings()
            }
        }) {
            Text(localizationManager.localized("games_parental_save"))
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
        
        navigationManager.goBack()
    }

    @MainActor
    private func requestParentSessionForSettingChange(action: @escaping () -> Void) {
        action()
    }
}

// MARK: - Preview

#if DEBUG
struct GamesParentalControlScreen_Previews: PreviewProvider {
    static var previews: some View {
        GamesParentalControlScreen()
    }
}
#endif



