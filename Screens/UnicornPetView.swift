import SwiftUI
import UIKit

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
    
    // ✅ ГЕЙМИФИКАЦИЯ: Баланс единорогов с синхронизацией
    @State private var unicornBalance: Int = 0
    @State private var isLoadingBalance: Bool = false
    @State private var balanceError: String? = nil
    
    @AppStorage("companion_selected_character_id") private var companionCharacterId: String = "unicorn"
    
    // Кэшированный баланс для офлайн режима
    @AppStorage("child_unicorn_balance") private var cachedBalance: Int = 0
    
    private let apiService = APIService.shared
    
    // Получаем userId для API вызовов
    private var userId: String {
        let defaults = UserDefaults.standard
        if let id = defaults.string(forKey: "user_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !id.isEmpty {
            return id
        }
        if let memberId = defaults.string(forKey: "your_member_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !memberId.isEmpty {
            return memberId
        }
        if let childId = defaults.string(forKey: "parental_selected_child_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !childId.isEmpty {
            return childId
        }
        return "guest"
    }

    private var rewardsScopeChildId: String? {
        let defaults = UserDefaults.standard
        if let childId = defaults.string(forKey: "parental_selected_child_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !childId.isEmpty {
            return childId
        }
        return UnicornRewardsStore.resolveActiveChildId()
    }

    private func mergedBalanceWithLocal(_ serverBalance: Int) -> Int {
        let localBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        if serverBalance <= 0 && localBalance > 0 {
            return localBalance
        }
        return max(serverBalance, 0)
    }
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .growWarm)
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
            loadBalance()
        }
        .refreshable {
            await refreshBalance()
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
        .stormGlassCard(cornerRadius: CornerRadius.xl)
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
        VStack(spacing: Spacing.m) {
            // Показываем баланс единорогов
            if isLoadingBalance {
                HStack {
                    ProgressView()
                        .scaleEffect(0.8)
                    Text(localizationManager.localized("loading_balance"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.horizontal, Spacing.screenPadding)
            } else if let error = balanceError {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
                    .padding(.horizontal, Spacing.screenPadding)
            } else {
                Text(String(format: localizationManager.localized("unicorn_balance_display"), unicornBalance))
                    .font(.bodyBold)
                    .foregroundColor(.primaryBlue)
                    .padding(.horizontal, Spacing.screenPadding)
            }
            
            HStack(spacing: Spacing.m) {
                actionButton(icon: "🍎", title: localizationManager.localized("unicorn_pet_feed"), cost: String(format: localizationManager.localized("unicorn_pet_cost_unicorns"), 10)) {
                    feedPet()
                }
                
                actionButton(icon: "🎮", title: localizationManager.localized("unicorn_pet_play"), cost: String(format: localizationManager.localized("unicorn_pet_cost_unicorns"), 5)) {
                    playWithPet()
                }
                
                actionButton(icon: "💕", title: localizationManager.localized("unicorn_pet_pet"), cost: localizationManager.localized("unicorn_pet_cost_free")) {
                    petPet()
                }
            }
            .padding(.horizontal, Spacing.screenPadding)

            Button(action: {
                HapticFeedback.impact(.medium)
                companionCharacterId = "unicorn"
                navigationManager.navigateToCompanionHome(returnTo: .unicornPet)
            }) {
                HStack(spacing: Spacing.s) {
                    Text("🦄")
                        .font(.system(size: 28))
                    Text(localizationManager.localized("companion_pet_talk_button"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                    Spacer()
                    Image(systemName: "mic.fill")
                        .foregroundColor(.white.opacity(0.9))
                }
                .padding(Spacing.m)
                .background(
                    LinearGradient(
                        colors: [Color(hex: "6366F1"), Color(hex: "A855F7")],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .cornerRadius(CornerRadius.large)
            }
            .buttonStyle(PlainButtonStyle())
            .padding(.horizontal, Spacing.screenPadding)
            .accessibilityIdentifier("unicorn_pet_companion_talk_button")
            .accessibilityLabel(localizationManager.localized("companion_pet_talk_button"))
        }
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
            .stormGlassCard(cornerRadius: 8)
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
    
    // MARK: - ✅ ГЕЙМИФИКАЦИЯ: API методы для синхронизации баланса
    
    /// Загрузить баланс единорогов с сервера
    private func loadBalance() {
        isLoadingBalance = true
        balanceError = nil
        
        // Используем кэшированное значение для быстрого отображения
        unicornBalance = cachedBalance
        
        apiService.getGamificationBalance(userId: userId) { [self] result in
            isLoadingBalance = false
            switch result {
            case .success(let response):
                let safeBalance = mergedBalanceWithLocal(response.balance)
                unicornBalance = safeBalance
                cachedBalance = safeBalance
                UnicornRewardsStore.writeBalance(safeBalance, for: rewardsScopeChildId)
                balanceError = nil
            case .failure(let error):
                balanceError = error.localizedDescription
                // Используем кэшированное значение при ошибке
                if cachedBalance > 0 {
                    unicornBalance = cachedBalance
                }
            }
        }
    }
    
    /// Обновить баланс (pull-to-refresh)
    @MainActor
    private func refreshBalance() async {
        loadBalance()
        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 секунды
    }
    
    /// Покормить питомца (списать 10 единорогов)
    private func feedPet() {
        guard unicornBalance >= 10 else {
            balanceError = localizationManager.localized("unicorn_insufficient_balance")
            return
        }
        
        apiService.subtractGamificationBalance(
            userId: userId,
            amount: 10,
            reason: "Feed pet",
            deviceId: UIDevice.current.identifierForVendor?.uuidString
        ) { [self] result in
            switch result {
            case .success(let response):
                unicornBalance = response.balance
                cachedBalance = response.balance
                hunger = min(1.0, hunger + 0.2)
                HapticFeedback.impact(.medium)
            case .failure(let error):
                balanceError = error.localizedDescription
                HapticFeedback.notification(.error)
            }
        }
    }
    
    /// Поиграть с питомцем (списать 5 единорогов)
    private func playWithPet() {
        guard unicornBalance >= 5 else {
            balanceError = localizationManager.localized("unicorn_insufficient_balance")
            return
        }
        
        apiService.subtractGamificationBalance(
            userId: userId,
            amount: 5,
            reason: "Play with pet",
            deviceId: UIDevice.current.identifierForVendor?.uuidString
        ) { [self] result in
            switch result {
            case .success(let response):
                unicornBalance = response.balance
                cachedBalance = response.balance
                energy = min(1.0, energy + 0.15)
                HapticFeedback.impact(.medium)
            case .failure(let error):
                balanceError = error.localizedDescription
                HapticFeedback.notification(.error)
            }
        }
    }
    
    /// Погладить питомца (бесплатно)
    private func petPet() {
        love = min(1.0, love + 0.1)
        HapticFeedback.impact(.light)
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



