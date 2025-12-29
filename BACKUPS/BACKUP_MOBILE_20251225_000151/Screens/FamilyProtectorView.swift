import SwiftUI

/// 🕵️ Family Protector View
/// Интерактивные квесты по безопасности
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct FamilyProtectorView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var settingsManager = GamesSettingsManager.shared
    
    // Прогресс квестов (AppStorage)
    @AppStorage("family_protector_completed_quests") private var storedCompletedQuests: Int = 0
    @State private var completedQuests: Int = 0 {
        didSet { storedCompletedQuests = completedQuests }
    }
    
    @AppStorage("family_protector_phishing_score") private var storedPhishingScore: Int = 0
    @State private var phishingScore: Int = 0 {
        didSet { storedPhishingScore = phishingScore }
    }
    
    @AppStorage("family_protector_device_score") private var storedDeviceScore: Int = 0
    @State private var deviceScore: Int = 0 {
        didSet { storedDeviceScore = deviceScore }
    }
    
    @AppStorage("family_protector_communication_score") private var storedCommunicationScore: Int = 0
    @State private var communicationScore: Int = 0 {
        didSet { storedCommunicationScore = communicationScore }
    }
    
    @AppStorage("family_protector_weekly_test_completed") private var storedWeeklyTestCompleted: Bool = false
    @State private var weeklyTestCompleted: Bool = false {
        didSet { storedWeeklyTestCompleted = weeklyTestCompleted }
    }
    
    @State private var selectedQuestType: QuestType? = nil
    @State private var showQuestDetail: Bool = false
    
    // MARK: - Quest Types
    
    enum QuestType {
        case phishing, device, communication, weeklyTest
        
        var title: String {
            switch self {
            case .phishing: return "🔍 Детектив фишинга"
            case .device: return "🛡️ Защитник устройства"
            case .communication: return "🎭 Сценарий общения"
            case .weeklyTest: return "📋 Еженедельная проверка"
            }
        }
        
        var icon: String {
            switch self {
            case .phishing: return "🔍"
            case .device: return "🛡️"
            case .communication: return "🎭"
            case .weeklyTest: return "📋"
            }
        }
        
        var description: String {
            switch self {
            case .phishing: return "Распознай опасные письма и сайты"
            case .device: return "Защити устройство от вирусов"
            case .communication: return "Правильно общайся в интернете"
            case .weeklyTest: return "10 случайных сценариев безопасности"
            }
        }
    }
    
    // MARK: - Quest Scenarios
    
    struct QuestScenario {
        let id: Int
        let type: QuestType
        let title: String
        let scenario: String
        let options: [String]
        let correctAnswer: Int
        let explanation: String
    }
    
    let phishingScenarios: [QuestScenario] = [
        QuestScenario(
            id: 1,
            type: .phishing,
            title: "Подозрительное письмо",
            scenario: "Ты получил письмо от 'Банк Онлайн' с текстом: 'СРОЧНО! Твой аккаунт заблокирован. Перейди по ссылке и введи пароль, иначе счёт закроют!'",
            options: [
                "Перейти по ссылке и ввести пароль",
                "Показать родителям и не переходить",
                "Переслать друзьям",
                "Удалить письмо"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Банки никогда не просят пароль по ссылке. Всегда показывай такие письма родителям."
        ),
        QuestScenario(
            id: 2,
            type: .phishing,
            title: "Выигрыш в конкурсе",
            scenario: "Пришло письмо: 'Поздравляем! Ты выиграл новый iPhone! Отправь свои данные (имя, адрес, телефон) чтобы получить приз!'",
            options: [
                "Отправить данные сразу",
                "Показать родителям",
                "Рассказать друзьям",
                "Игнорировать"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Если ты не участвовал в конкурсе, это обман. Всегда проверяй с родителями."
        ),
        QuestScenario(
            id: 3,
            type: .phishing,
            title: "Сайт выглядит странно",
            scenario: "Ты зашёл на сайт, который должен быть от популярной игры. Но адрес выглядит странно: 'game-premium.free.ru' вместо 'game-official.com'",
            options: [
                "Зарегистрироваться на сайте",
                "Закрыть сайт и рассказать родителям",
                "Попробовать скачать что-то",
                "Продолжить использование"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Поддельные сайты часто имеют похожие адреса. Всегда проверяй настоящий адрес сайта."
        )
    ]
    
    let deviceScenarios: [QuestScenario] = [
        QuestScenario(
            id: 4,
            type: .device,
            title: "Вирусная атака",
            scenario: "Твоё устройство показывает сообщение: 'Вирус обнаружен! Срочно установи антивирус по ссылке!'",
            options: [
                "Установить антивирус по ссылке",
                "Показать родителям и не устанавливать",
                "Перезагрузить устройство",
                "Игнорировать"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Настоящие антивирусы не просят устанавливаться через сомнительные ссылки. Покажи родителям."
        ),
        QuestScenario(
            id: 5,
            type: .device,
            title: "Незнакомый файл",
            scenario: "Друг прислал файл 'cool_game.exe' и просит его открыть. Ты не знаешь, что это за файл.",
            options: [
                "Открыть сразу",
                "Спросить у родителей",
                "Переслать другим друзьям",
                "Открыть на другом устройстве"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Не открывай файлы от незнакомцев или подозрительные файлы. Спроси родителей."
        ),
        QuestScenario(
            id: 6,
            type: .device,
            title: "Обновление системы",
            scenario: "Появилось сообщение: 'Твоя система устарела! Обновись здесь [ссылка] или потеряешь доступ!'",
            options: [
                "Обновиться по ссылке",
                "Проверить в настройках устройства",
                "Игнорировать",
                "Спросить у друзей"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Обновления системы делаются через настройки устройства, не по ссылкам в сообщениях."
        )
    ]
    
    let communicationScenarios: [QuestScenario] = [
        QuestScenario(
            id: 7,
            type: .communication,
            title: "Незнакомец в интернете",
            scenario: "Незнакомый человек пишет: 'Привет! Ты классный! Давай встретимся? Где ты живёшь?'",
            options: [
                "Рассказать, где живёшь",
                "Не отвечать и показать родителям",
                "Попробовать узнать, кто это",
                "Добавить в друзья"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Не рассказывай незнакомцам личную информацию. Всегда говори родителям о таких сообщениях."
        ),
        QuestScenario(
            id: 8,
            type: .communication,
            title: "Просьба о фото",
            scenario: "Незнакомец просит: 'Отправь своё фото и я отправлю тебе подарок!'",
            options: [
                "Отправить фото",
                "Отказать и заблокировать",
                "Попросить подарок сначала",
                "Посоветоваться с друзьями"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Никогда не отправляй свои фото незнакомцам. Сразу блокируй таких людей."
        ),
        QuestScenario(
            id: 9,
            type: .communication,
            title: "Секрет от родителей",
            scenario: "Кто-то пишет: 'Давай это будет наш секрет! Не говори родителям!'",
            options: [
                "Согласиться на секрет",
                "Всегда говорить родителям",
                "Рассказать друзьям",
                "Забыть об этом"
            ],
            correctAnswer: 1,
            explanation: "Правильно! Взрослые, которые просят скрывать что-то от родителей, могут быть опасны. Всегда рассказывай родителям."
        )
    ]
    
    // Еженедельная проверка: 10 случайных сценариев
    var weeklyTestScenarios: [QuestScenario] {
        var allScenarios = phishingScenarios + deviceScenarios + communicationScenarios
        allScenarios.shuffle()
        return Array(allScenarios.prefix(10))
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header с кнопкой "← Назад"
                navigationHeader
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Прогресс-карточка
                        progressCard
                        
                        // Список квестов
                        questsList
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showQuestDetail) {
            if let questType = selectedQuestType {
                QuestDetailView(
                    questType: questType,
                    scenarios: getScenarios(for: questType),
                    onComplete: { score in
                        completeQuest(questType: questType, score: score)
                    }
                )
            }
        }
        .onAppear {
            // Восстанавливаем сохранённый прогресс из AppStorage
            completedQuests = storedCompletedQuests
            phishingScore = storedPhishingScore
            deviceScore = storedDeviceScore
            communicationScore = storedCommunicationScore
            weeklyTestCompleted = storedWeeklyTestCompleted
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
            
            Text("🕵️ Я защитник")
                .font(.h2)
                .foregroundColor(.pink)
            
            Spacer()
            
            // Прогресс
            Text("\(completedQuests)/10 квестов")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(Color.primaryBlue.opacity(0.3))
                )
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Progress Card
    
    private var progressCard: some View {
        VStack(spacing: Spacing.m) {
            // Иконка
            Text("🕵️")
                .font(.system(size: 56))
            
            // Статистика
            HStack(spacing: Spacing.l) {
                VStack {
                    Text("\(completedQuests)")
                        .font(.h1)
                        .foregroundColor(.pink)
                    Text("квестов\nпройдено")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(phishingScore + deviceScore + communicationScore)")
                        .font(.h1)
                        .foregroundColor(.successGreen)
                    Text("очков\nнабрано")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text(weeklyTestCompleted ? "✅" : "⏳")
                        .font(.system(size: 32))
                    Text("Еженедельная\nпроверка")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
            }
            
            // Прогресс-бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 20)
                    
                    RoundedRectangle(cornerRadius: 10)
                        .fill(
                            LinearGradient(
                                colors: [.pink, Color(hex: "EC4899")],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: geometry.size.width * questProgress, height: 20)
                }
            }
            .frame(height: 20)
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Quests List
    
    private var questsList: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🎯 Квесты безопасности")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            // Квест 1: Детектив фишинга
            questCard(questType: .phishing, score: phishingScore)
            
            // Квест 2: Защитник устройства
            questCard(questType: .device, score: deviceScore)
            
            // Квест 3: Сценарий общения
            questCard(questType: .communication, score: communicationScore)
            
            // Еженедельная проверка
            weeklyTestCard
        }
    }
    
    private func questCard(questType: QuestType, score: Int) -> some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            selectedQuestType = questType
            showQuestDetail = true
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка квеста
                Text(questType.icon)
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.pink.opacity(0.2))
                    )
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(questType.title)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("▶️")
                            .font(.system(size: 20))
                    }
                    
                    Text(questType.description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                    
                    if score > 0 {
                        Text("+\(score) 🦄 получено")
                            .font(.captionSmall)
                            .foregroundColor(.successGreen)
                    }
                }
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(Color.pink.opacity(0.3), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var weeklyTestCard: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            selectedQuestType = .weeklyTest
            showQuestDetail = true
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Text("📋")
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(weeklyTestCompleted ? Color.successGreen.opacity(0.2) : Color.primaryBlue.opacity(0.2))
                    )
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text("📋 Еженедельная проверка")
                            .font(.bodyBold)
                            .foregroundColor(weeklyTestCompleted ? .successGreen : .textPrimary)
                        
                        Spacer()
                        
                        if weeklyTestCompleted {
                            Text("✅")
                                .font(.system(size: 20))
                        } else {
                            Text("▶️")
                                .font(.system(size: 20))
                        }
                    }
                    
                    Text("10 случайных сценариев безопасности")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    if weeklyTestCompleted {
                        Text("+\(settingsManager.weeklyTestBonus) 🦄 получено")
                            .font(.captionSmall)
                            .foregroundColor(.successGreen)
                    } else {
                        Text("Награда: \(settingsManager.weeklyTestBonus) 🦄")
                            .font(.captionSmall)
                            .foregroundColor(.secondaryGold)
                    }
                }
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(weeklyTestCompleted ? Color.successGreen.opacity(0.1) : Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(weeklyTestCompleted ? Color.successGreen.opacity(0.5) : Color.primaryBlue.opacity(0.3), lineWidth: weeklyTestCompleted ? 2 : 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Computed Properties
    
    private var questProgress: Double {
        Double(completedQuests) / 10.0
    }
    
    // MARK: - Methods
    
    private func getScenarios(for questType: QuestType) -> [QuestScenario] {
        switch questType {
        case .phishing:
            return phishingScenarios
        case .device:
            return deviceScenarios
        case .communication:
            return communicationScenarios
        case .weeklyTest:
            return weeklyTestScenarios
        }
    }
    
    private func completeQuest(questType: QuestType, score: Int) {
        let reward: Int
        
        switch questType {
        case .phishing:
            phishingScore += score
            reward = settingsManager.phishingReward
            if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                let newBalance = storedBalance + reward
                UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
            }
        case .device:
            deviceScore += score
            reward = settingsManager.deviceReward
            if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                let newBalance = storedBalance + reward
                UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
            }
        case .communication:
            communicationScore += score
            reward = settingsManager.communicationReward
            if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                let newBalance = storedBalance + reward
                UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
            }
        case .weeklyTest:
            if !weeklyTestCompleted {
                weeklyTestCompleted = true
                reward = settingsManager.weeklyTestBonus
                if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                    let newBalance = storedBalance + reward
                    UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
                }
                // Еженедельная проверка = 10 квестов
                completedQuests += 10
            } else {
                reward = 0
            }
        }
        
        // Обновляем прогресс квестов (для обычных квестов)
        if questType != .weeklyTest {
            completedQuests += 1
        }
        
        HapticFeedback.notification(.success)
    }
}

// MARK: - Quest Detail View

struct QuestDetailView: View {
    let questType: FamilyProtectorView.QuestType
    let scenarios: [FamilyProtectorView.QuestScenario]
    let onComplete: (Int) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var currentScenario = 0
    @State private var score = 0
    @State private var selectedAnswer: Int? = nil
    @State private var showExplanation = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: Spacing.l) {
                    // Прогресс сценариев
                    if questType != .weeklyTest {
                        Text("Сценарий \(currentScenario + 1) из \(scenarios.count)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    } else {
                        Text("Вопрос \(currentScenario + 1) из \(scenarios.count)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    // Текущий сценарий
                    if currentScenario < scenarios.count {
                        scenarioCard(scenario: scenarios[currentScenario])
                    }
                    
                    // Объяснение (показывается после ответа)
                    if showExplanation && currentScenario < scenarios.count {
                        explanationCard(scenario: scenarios[currentScenario])
                    }
                    
                    // Кнопка продолжить
                    Button(action: {
                        if selectedAnswer != nil || showExplanation {
                            HapticFeedback.impact(.medium)
                            goToNextScenario()
                        }
                    }) {
                        Text(getButtonText())
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(canProceed() ? Color.pink : Color.textSecondary)
                            )
                    }
                    .disabled(!canProceed())
                    .padding(.horizontal, Spacing.screenPadding)
                    
                    Spacer()
                }
                .padding(.top, Spacing.l)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Закрыть") {
                        HapticFeedback.impact(.light)
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func scenarioCard(scenario: FamilyProtectorView.QuestScenario) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(scenario.title)
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Text(scenario.scenario)
                .font(.body)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            Text("Что ты сделаешь?")
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
                .padding(.top, Spacing.s)
            
            VStack(spacing: Spacing.s) {
                ForEach(0..<scenario.options.count, id: \.self) { index in
                    Button(action: {
                        if !showExplanation {
                            HapticFeedback.impact(.light)
                            selectedAnswer = index
                            
                            // Проверяем ответ
                            if index == scenario.correctAnswer {
                                score += 1
                                HapticFeedback.notification(.success)
                            } else {
                                HapticFeedback.notification(.error)
                            }
                            
                            showExplanation = true
                        }
                    }) {
                        HStack {
                            Text(scenario.options[index])
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            Spacer()
                            
                            if selectedAnswer == index {
                                Image(systemName: index == scenario.correctAnswer ? "checkmark.circle.fill" : "xmark.circle.fill")
                                    .foregroundColor(index == scenario.correctAnswer ? .successGreen : .dangerRed)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(getOptionBackgroundColor(index: index))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(
                                            getOptionBorderColor(index: index),
                                            lineWidth: showExplanation && selectedAnswer == index ? 2 : 0
                                        )
                                )
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
                    .disabled(showExplanation)
                }
            }
        }
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func explanationCard(scenario: FamilyProtectorView.QuestScenario) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(selectedAnswer == scenario.correctAnswer ? "✅ Правильно!" : "❌ Неправильно")
                    .font(.bodyBold)
                    .foregroundColor(selectedAnswer == scenario.correctAnswer ? .successGreen : .dangerRed)
                
                Spacer()
            }
            
            Text(scenario.explanation)
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(selectedAnswer == scenario.correctAnswer ? Color.successGreen.opacity(0.1) : Color.dangerRed.opacity(0.1))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func getOptionBackgroundColor(index: Int) -> Color {
        if showExplanation {
            if selectedAnswer == index {
                return index == scenarios[currentScenario].correctAnswer ? Color.successGreen.opacity(0.2) : Color.dangerRed.opacity(0.2)
            } else if index == scenarios[currentScenario].correctAnswer {
                return Color.successGreen.opacity(0.15)
            }
        }
        return selectedAnswer == index ? Color.pink.opacity(0.2) : Color.backgroundMedium.opacity(0.5)
    }
    
    private func getOptionBorderColor(index: Int) -> Color {
        if showExplanation {
            if selectedAnswer == index {
                return index == scenarios[currentScenario].correctAnswer ? .successGreen : .dangerRed
            } else if index == scenarios[currentScenario].correctAnswer {
                return .successGreen
            }
        }
        return selectedAnswer == index ? .pink : .clear
    }
    
    private func getButtonText() -> String {
        if selectedAnswer == nil {
            return "Выбери ответ"
        } else if showExplanation {
            return currentScenario == scenarios.count - 1 ? "Завершить" : "Далее"
        } else {
            return "Продолжить"
        }
    }
    
    private func canProceed() -> Bool {
        selectedAnswer != nil && showExplanation
    }
    
    private func goToNextScenario() {
        if currentScenario < scenarios.count - 1 {
            currentScenario += 1
            selectedAnswer = nil
            showExplanation = false
        } else {
            // Все сценарии завершены
            onComplete(score)
            dismiss()
        }
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyProtectorView_Previews: PreviewProvider {
    static var previews: some View {
        FamilyProtectorView()
            .environmentObject(NavigationManager())
    }
}
#endif

