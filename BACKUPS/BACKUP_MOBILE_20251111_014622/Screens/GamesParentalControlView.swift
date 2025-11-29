import SwiftUI

/// 🎮 Games Parental Control View
/// Панель управления геймификацией для родителей
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct GamesParentalControlView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var settingsManager = GamesSettingsManager.shared
    @State private var showAccessDeniedAlert: Bool = false
    
    // Проверка роли пользователя
    private var isUserParent: Bool {
        let storedRole = UserDefaults.standard.string(forKey: "current_user_role") ?? ""
        print("🔍 DEBUG GamesParentalControlView.isUserParent:")
        print("   - roleString = '\(storedRole)'")
        
        guard let role = FamilyRole(storageValue: storedRole) else {
            print("   - Результат: false (роль не найдена или невалидна)")
            return false
        }
        
        let isParent = role == .parent
        print("   - role = \(role.rawValue)")
        print("   - Результат: \(isParent)")
        return isParent
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент (только для родителей)
                if isUserParent {
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: Spacing.l) {
                            // Информация
                            infoCard
                        
                        // 🛡️ ЮНЫЙ ЗАЩИТНИК
                        youngDefenderGameCard
                        
                        // 🦄 МОЙ ПИТОМЕЦ
                        petGameCard
                        
                        // 🕵️ Я ЗАЩИТНИК
                        familyProtectorGameCard
                        
                        // 🏆 ТУРНИР СЕМЬИ
                        tournamentGameCard
                        
                        // 🏪 МАГАЗИН НАГРАД
                        shopGameCard
                        
                        // ⚙️ ОБЩИЕ НАСТРОЙКИ
                        generalSettingsCard
                        
                        // Быстрые действия
                        quickActions
                        
                        // Кнопка сохранить
                        saveButton
                        
                            Spacer()
                                .frame(height: Spacing.xxl)
                        }
                        .padding(.top, Spacing.m)
                    }
                } else {
                    // Если не родитель - показываем сообщение
                    VStack(spacing: Spacing.l) {
                        Text("🔒")
                            .font(.system(size: 64))
                        
                        Text("Доступ ограничен")
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                        
                        Text("Настройки игр доступны только родителям.")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        Button(action: {
                            HapticFeedback.impact(.medium)
                            navigationManager.goBack()
                        }) {
                            Text("Назад")
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.primaryBlue)
                                .cornerRadius(CornerRadius.medium)
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                    }
                    .padding(.top, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            // Проверка доступа: только родители могут настраивать игры
            if !isUserParent {
                showAccessDeniedAlert = true
            }
        }
        .alert("🔒 Доступ запрещён", isPresented: $showAccessDeniedAlert) {
            Button("Понятно") {
                HapticFeedback.impact(.medium)
                navigationManager.goBack()
            }
        } message: {
            Text("Настройки игр доступны только родителям. Если ты родитель, убедись, что выбрана правильная роль в приложении.")
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
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
            
            Text("⚙️ Управление играми")
                .font(.h2)
                .foregroundColor(.primaryBlue)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
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
                Text("Здесь вы можете настроить все награды и параметры игр. Все настройки сохраняются автоматически! 🎮")
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
    
    // MARK: - 🛡️ ЮНЫЙ ЗАЩИТНИК Game Card
    
    private var youngDefenderGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с переключателем
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🛡️")
                        .font(.system(size: 22))
                    Text("Юный защитник")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: Binding(
                    get: { settingsManager.youngDefenderEnabled },
                    set: { settingsManager.youngDefenderEnabled = $0 }
                ))
                .labelsHidden()
            }
            
            // Описание
            Text("Образовательная игра: 6 уроков безопасности с квизами. Ребёнок проходит уроки и получает награды за правильные ответы.")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if settingsManager.youngDefenderEnabled {
                // Награда за урок
                rewardSlider(
                    title: "Награда за урок:",
                    value: Binding(
                        get: { Double(settingsManager.lessonReward) },
                        set: { settingsManager.lessonReward = Int($0) }
                    ),
                    range: 1...100,
                    unit: "🦄"
                )
                
                // Бонус за 5 уроков
                rewardSlider(
                    title: "Бонус за 5 уроков:",
                    value: Binding(
                        get: { Double(settingsManager.bonus5Lessons) },
                        set: { settingsManager.bonus5Lessons = Int($0) }
                    ),
                    range: 10...200,
                    unit: "🦄"
                )
                
                // Бонус за все 6 уроков
                rewardSlider(
                    title: "Бонус за все 6 уроков:",
                    value: Binding(
                        get: { Double(settingsManager.bonusAll6) },
                        set: { settingsManager.bonusAll6 = Int($0) }
                    ),
                    range: 20...500,
                    unit: "🦄"
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.primaryBlue.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
                )
                .opacity(settingsManager.youngDefenderEnabled ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - 🦄 МОЙ ПИТОМЕЦ Game Card
    
    private var petGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🦄")
                        .font(.system(size: 22))
                    Text("Мой питомец")
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
            
            // Цены действий
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("💰 Цены действий:")
                    .font(.caption)
                    .foregroundColor(.textPrimary)
                
                rewardSlider(
                    title: "Покормить:",
                    value: Binding(
                        get: { Double(settingsManager.petFeedCost) },
                        set: { settingsManager.petFeedCost = Int($0) }
                    ),
                    range: 1...50,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Поиграть:",
                    value: Binding(
                        get: { Double(settingsManager.petPlayCost) },
                        set: { settingsManager.petPlayCost = Int($0) }
                    ),
                    range: 1...50,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Погладить (бесплатно):",
                    value: Binding(
                        get: { Double(settingsManager.petPetCost) },
                        set: { settingsManager.petPetCost = Int($0) }
                    ),
                    range: 0...10,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Бонус за полный уход (24ч):",
                    value: Binding(
                        get: { Double(settingsManager.petCareBonus) },
                        set: { settingsManager.petCareBonus = Int($0) }
                    ),
                    range: 5...100,
                    unit: "🦄"
                )
            }
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
    
    // MARK: - 🕵️ Я ЗАЩИТНИК Game Card
    
    private var familyProtectorGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с переключателем
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🕵️")
                        .font(.system(size: 22))
                    Text("Я защитник")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: Binding(
                    get: { settingsManager.protectorEnabled },
                    set: { settingsManager.protectorEnabled = $0 }
                ))
                .labelsHidden()
            }
            
            // Описание
            Text("Интерактивные квесты безопасности: детектив фишинга, защитник устройства, сценарии общения. Еженедельная проверка из 10 случайных сценариев.")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if settingsManager.protectorEnabled {
                // Награды за квесты
                rewardSlider(
                    title: "Детектив фишинга:",
                    value: Binding(
                        get: { Double(settingsManager.phishingReward) },
                        set: { settingsManager.phishingReward = Int($0) }
                    ),
                    range: 1...50,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Защитник устройства:",
                    value: Binding(
                        get: { Double(settingsManager.deviceReward) },
                        set: { settingsManager.deviceReward = Int($0) }
                    ),
                    range: 1...100,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Сценарий общения:",
                    value: Binding(
                        get: { Double(settingsManager.communicationReward) },
                        set: { settingsManager.communicationReward = Int($0) }
                    ),
                    range: 1...100,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Еженедельная проверка (10/10):",
                    value: Binding(
                        get: { Double(settingsManager.weeklyTestBonus) },
                        set: { settingsManager.weeklyTestBonus = Int($0) }
                    ),
                    range: 10...500,
                    unit: "🦄"
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.pink.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.pink.opacity(0.3), lineWidth: 1)
                )
                .opacity(settingsManager.protectorEnabled ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - 🏆 ТУРНИР Game Card
    
    private var tournamentGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с переключателем
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🏆")
                        .font(.system(size: 22))
                    Text("Турнир семьи")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: Binding(
                    get: { settingsManager.tournamentEnabled },
                    set: { settingsManager.tournamentEnabled = $0 }
                ))
                .labelsHidden()
            }
            
            // Описание
            Text("Еженедельное соревнование всей семьи. 5 типов турниров: отличники 📚, помощники 🧹, без конфликтов 😊, чтение 📖, универсальный 🎯.")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if settingsManager.tournamentEnabled {
                // Призы за места
                rewardSlider(
                    title: "🥇 1 место:",
                    value: Binding(
                        get: { Double(settingsManager.firstPlaceReward) },
                        set: { settingsManager.firstPlaceReward = Int($0) }
                    ),
                    range: 10...500,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "🥈 2 место:",
                    value: Binding(
                        get: { Double(settingsManager.secondPlaceReward) },
                        set: { settingsManager.secondPlaceReward = Int($0) }
                    ),
                    range: 5...300,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "🥉 3 место:",
                    value: Binding(
                        get: { Double(settingsManager.thirdPlaceReward) },
                        set: { settingsManager.thirdPlaceReward = Int($0) }
                    ),
                    range: 5...200,
                    unit: "🦄"
                )
                
                rewardSlider(
                    title: "Участие:",
                    value: Binding(
                        get: { Double(settingsManager.participationReward) },
                        set: { settingsManager.participationReward = Int($0) }
                    ),
                    range: 1...100,
                    unit: "🦄"
                )
                
                // Длительность турнира
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Длительность турнира:")
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    Slider(value: Binding(
                        get: { Double(settingsManager.durationDays) },
                        set: { settingsManager.durationDays = Int($0) }
                    ), in: 1...30, step: 1)
                        .accentColor(.warningOrange)
                    
                    HStack {
                        Text("1 день")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(settingsManager.durationDays) \(settingsManager.durationDays == 1 ? "день" : (settingsManager.durationDays <= 4 ? "дня" : "дней"))")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.warningOrange)
                        Spacer()
                        Text("30 дней")
                            .font(.captionSmall)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.warningOrange.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.warningOrange.opacity(0.3), lineWidth: 1)
                )
                .opacity(settingsManager.tournamentEnabled ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - 🏪 МАГАЗИН Game Card
    
    private var shopGameCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок с переключателем
            HStack {
                HStack(spacing: Spacing.xs) {
                    Text("🏪")
                        .font(.system(size: 22))
                    Text("Магазин наград")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                Toggle("", isOn: Binding(
                    get: { settingsManager.shopEnabled },
                    set: { settingsManager.shopEnabled = $0 }
                ))
                .labelsHidden()
            }
            
            // Описание
            Text("Ребёнок тратит единороги на награды: дополнительное время игр, экранное время, пицца, кино, подарки.")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if settingsManager.shopEnabled {
                // Цены товаров
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("💰 Цены товаров:")
                        .font(.caption)
                        .foregroundColor(.textPrimary)
                    
                    rewardSlider(
                        title: "🎮 +30 минут игр:",
                        value: Binding(
                            get: { Double(settingsManager.game30minPrice) },
                            set: { settingsManager.game30minPrice = Int($0) }
                        ),
                        range: 10...200,
                        unit: "🦄"
                    )
                    
                    rewardSlider(
                        title: "📱 +1 час экрана:",
                        value: Binding(
                            get: { Double(settingsManager.screen1hourPrice) },
                            set: { settingsManager.screen1hourPrice = Int($0) }
                        ),
                        range: 20...300,
                        unit: "🦄"
                    )
                    
                    rewardSlider(
                        title: "🌙 +30 мин перед сном:",
                        value: Binding(
                            get: { Double(settingsManager.sleep30minPrice) },
                            set: { settingsManager.sleep30minPrice = Int($0) }
                    ),
                        range: 30...400,
                        unit: "🦄"
                    )
                    
                    rewardSlider(
                        title: "🍕 Пицца:",
                        value: Binding(
                            get: { Double(settingsManager.pizzaPrice) },
                            set: { settingsManager.pizzaPrice = Int($0) }
                        ),
                        range: 50...500,
                        unit: "🦄"
                    )
                    
                    rewardSlider(
                        title: "🎬 Кино:",
                        value: Binding(
                            get: { Double(settingsManager.cinemaPrice) },
                            set: { settingsManager.cinemaPrice = Int($0) }
                        ),
                        range: 100...600,
                        unit: "🦄"
                    )
                    
                    rewardSlider(
                        title: "🎁 Подарок:",
                        value: Binding(
                            get: { Double(settingsManager.giftPrice) },
                            set: { settingsManager.giftPrice = Int($0) }
                        ),
                        range: 200...1000,
                        unit: "🦄"
                    )
                    
                    // Лимит трат в день
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Лимит трат в день:")
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                        
                        Slider(value: Binding(
                            get: { Double(settingsManager.dailyLimit) },
                            set: { settingsManager.dailyLimit = Int($0) }
                        ), in: 50...500, step: 10)
                            .accentColor(.secondaryGold)
                        
                        HStack {
                            Text("50 🦄")
                                .font(.captionSmall)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(settingsManager.dailyLimit) 🦄")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(.secondaryGold)
                            Spacer()
                            Text("500 🦄")
                                .font(.captionSmall)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    // Подтверждение покупок
                    Toggle(isOn: Binding(
                        get: { settingsManager.confirmPurchases },
                        set: { settingsManager.confirmPurchases = $0 }
                    )) {
                        Text("Подтверждение покупок родителем")
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.secondaryGold.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
                .opacity(settingsManager.shopEnabled ? 1.0 : 0.6)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - ⚙️ ОБЩИЕ НАСТРОЙКИ
    
    private var generalSettingsCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("⚙️ Общие настройки")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
            
            Toggle(isOn: Binding(
                get: { settingsManager.notificationsEnabled },
                set: { settingsManager.notificationsEnabled = $0 }
            )) {
                Text("Уведомления о достижениях")
                    .font(.body)
                    .foregroundColor(.textPrimary)
            }
            
            Toggle(isOn: Binding(
                get: { settingsManager.achievementsEnabled },
                set: { settingsManager.achievementsEnabled = $0 }
            )) {
                Text("Статистика достижений")
                    .font(.body)
                    .foregroundColor(.textPrimary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Reward Slider Helper
    
    private func rewardSlider(title: String, value: Binding<Double>, range: ClosedRange<Double>, unit: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(title)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                Spacer()
                Text("\(Int(value.wrappedValue)) \(unit)")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondaryGold)
            }
            
            Slider(value: value, in: range, step: 1)
                .accentColor(.secondaryGold)
                .frame(height: 4)
        }
    }
    
    // MARK: - Quick Actions
    
    private var quickActions: some View {
        VStack(spacing: Spacing.s) {
            Button(action: {
                HapticFeedback.impact(.medium)
                resetToDefaults()
            }) {
                Text("🔄 Сброс к базовым настройкам")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.5))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .stroke(Color.textSecondary.opacity(0.3), lineWidth: 1)
                            )
                    )
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Save Button
    
    private var saveButton: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            saveSettings()
        }) {
            Text("💾 Настройки сохранены!")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.white)
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
    
    private func resetToDefaults() {
        settingsManager.resetToDefaults()
        HapticFeedback.notification(.success)
        print("🔄 Все настройки сброшены к базовым значениям")
    }
    
    private func saveSettings() {
        // Настройки сохраняются автоматически через @AppStorage в GamesSettingsManager
        HapticFeedback.notification(.success)
        print("💾 Настройки сохранены (автоматически через AppStorage)")
        
        // Небольшая задержка перед возвратом назад
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            navigationManager.goBack()
        }
    }
}

// MARK: - Preview

#if DEBUG
struct GamesParentalControlView_Previews: PreviewProvider {
    static var previews: some View {
        GamesParentalControlView()
            .environmentObject(NavigationManager())
    }
}
#endif

