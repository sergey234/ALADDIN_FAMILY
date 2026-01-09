import SwiftUI

/// 🕵️ Family Protector View
/// Интерактивные квесты по безопасности
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct FamilyProtectorView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
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
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .phishing: return localizationManager.localized("family_protector_quest_phishing_title")
            case .device: return localizationManager.localized("family_protector_quest_device_title")
            case .communication: return localizationManager.localized("family_protector_quest_communication_title")
            case .weeklyTest: return localizationManager.localized("family_protector_quest_weekly_title")
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
        
        func description(localizationManager: LocalizationManager) -> String {
            switch self {
            case .phishing: return localizationManager.localized("family_protector_quest_phishing_desc")
            case .device: return localizationManager.localized("family_protector_quest_device_desc")
            case .communication: return localizationManager.localized("family_protector_quest_communication_desc")
            case .weeklyTest: return localizationManager.localized("family_protector_quest_weekly_desc")
            }
        }
    }
    
    // MARK: - Quest Scenarios
    
    struct QuestScenario {
        let id: Int
        let type: QuestType
        let titleKey: String
        let scenarioKey: String
        let optionKeys: [String]
        let correctAnswer: Int
        let explanationKey: String
    }
    
    // Computed properties для локализованных сценариев
    private var phishingScenarios: [QuestScenario] {
        [
        QuestScenario(
            id: 1,
            type: .phishing,
            titleKey: "family_protector_scenario_suspicious_email",
            scenarioKey: "family_protector_scenario_suspicious_email_text",
            optionKeys: [
                "family_protector_scenario_suspicious_email_option_1",
                "family_protector_scenario_suspicious_email_option_2",
                "family_protector_scenario_suspicious_email_option_3",
                "family_protector_scenario_suspicious_email_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_suspicious_email_explanation"
        ),
        QuestScenario(
            id: 2,
            type: .phishing,
            titleKey: "family_protector_scenario_contest_win",
            scenarioKey: "family_protector_scenario_contest_win_text",
            optionKeys: [
                "family_protector_scenario_contest_win_option_1",
                "family_protector_scenario_contest_win_option_2",
                "family_protector_scenario_contest_win_option_3",
                "family_protector_scenario_contest_win_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_contest_win_explanation"
        ),
        QuestScenario(
            id: 3,
            type: .phishing,
            titleKey: "family_protector_scenario_strange_site",
            scenarioKey: "family_protector_scenario_strange_site_text",
            optionKeys: [
                "family_protector_scenario_strange_site_option_1",
                "family_protector_scenario_strange_site_option_2",
                "family_protector_scenario_strange_site_option_3",
                "family_protector_scenario_strange_site_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_strange_site_explanation"
        )
        ]
    }
    
    private var deviceScenarios: [QuestScenario] {
        [
        QuestScenario(
            id: 4,
            type: .device,
            titleKey: "family_protector_scenario_virus_attack",
            scenarioKey: "family_protector_scenario_virus_attack_text",
            optionKeys: [
                "family_protector_scenario_virus_attack_option_1",
                "family_protector_scenario_virus_attack_option_2",
                "family_protector_scenario_virus_attack_option_3",
                "family_protector_scenario_virus_attack_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_virus_attack_explanation"
        ),
        QuestScenario(
            id: 5,
            type: .device,
            titleKey: "family_protector_scenario_unknown_file",
            scenarioKey: "family_protector_scenario_unknown_file_text",
            optionKeys: [
                "family_protector_scenario_unknown_file_option_1",
                "family_protector_scenario_unknown_file_option_2",
                "family_protector_scenario_unknown_file_option_3",
                "family_protector_scenario_unknown_file_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_unknown_file_explanation"
        ),
        QuestScenario(
            id: 6,
            type: .device,
            titleKey: "family_protector_scenario_system_update",
            scenarioKey: "family_protector_scenario_system_update_text",
            optionKeys: [
                "family_protector_scenario_system_update_option_1",
                "family_protector_scenario_system_update_option_2",
                "family_protector_scenario_system_update_option_3",
                "family_protector_scenario_system_update_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_system_update_explanation"
        )
        ]
    }
    
    private var communicationScenarios: [QuestScenario] {
        [
        QuestScenario(
            id: 7,
            type: .communication,
            titleKey: "family_protector_scenario_stranger_online",
            scenarioKey: "family_protector_scenario_stranger_online_text",
            optionKeys: [
                "family_protector_scenario_stranger_online_option_1",
                "family_protector_scenario_stranger_online_option_2",
                "family_protector_scenario_stranger_online_option_3",
                "family_protector_scenario_stranger_online_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_stranger_online_explanation"
        ),
        QuestScenario(
            id: 8,
            type: .communication,
            titleKey: "family_protector_scenario_photo_request",
            scenarioKey: "family_protector_scenario_photo_request_text",
            optionKeys: [
                "family_protector_scenario_photo_request_option_1",
                "family_protector_scenario_photo_request_option_2",
                "family_protector_scenario_photo_request_option_3",
                "family_protector_scenario_photo_request_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_photo_request_explanation"
        ),
        QuestScenario(
            id: 9,
            type: .communication,
            titleKey: "family_protector_scenario_secret_from_parents",
            scenarioKey: "family_protector_scenario_secret_from_parents_text",
            optionKeys: [
                "family_protector_scenario_secret_from_parents_option_1",
                "family_protector_scenario_secret_from_parents_option_2",
                "family_protector_scenario_secret_from_parents_option_3",
                "family_protector_scenario_secret_from_parents_option_4"
            ],
            correctAnswer: 1,
            explanationKey: "family_protector_scenario_secret_from_parents_explanation"
        )
        ]
    }
    
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
            
            Text(localizationManager.localized("family_protector_title"))
                .font(.h2)
                .foregroundColor(.pink)
            
            Spacer()
            
            // Прогресс
            Text(String(format: localizationManager.localized("family_protector_quests_completed"), completedQuests))
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
                    Text(localizationManager.localized("family_protector_progress_quests"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(phishingScore + deviceScore + communicationScore)")
                        .font(.h1)
                        .foregroundColor(.successGreen)
                    Text(localizationManager.localized("family_protector_progress_points"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text(weeklyTestCompleted ? "✅" : "⏳")
                        .font(.system(size: 32))
                    Text(localizationManager.localized("family_protector_weekly_check"))
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
            Text(localizationManager.localized("family_protector_quests_title"))
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
                        Text(questType.title(localizationManager: localizationManager))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("▶️")
                            .font(.system(size: 20))
                    }
                    
                    Text(questType.description(localizationManager: localizationManager))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                    
                    if score > 0 {
                        Text(String(format: localizationManager.localized("family_protector_quest_reward_earned"), score))
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
                        Text(localizationManager.localized("family_protector_quest_weekly_title"))
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
                    
                    Text(localizationManager.localized("family_protector_quest_weekly_desc"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    if weeklyTestCompleted {
                        Text(String(format: localizationManager.localized("family_protector_quest_reward_earned"), settingsManager.weeklyTestBonus))
                            .font(.captionSmall)
                            .foregroundColor(.successGreen)
                    } else {
                        Text(String(format: localizationManager.localized("family_protector_quest_weekly_reward"), settingsManager.weeklyTestBonus))
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
    @EnvironmentObject private var localizationManager: LocalizationManager
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
                        Text(String(format: localizationManager.localized("family_protector_scenario_progress"), currentScenario + 1, scenarios.count))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    } else {
                        Text(String(format: localizationManager.localized("family_protector_question_progress"), currentScenario + 1, scenarios.count))
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
                    Button(localizationManager.localized("family_protector_close")) {
                        HapticFeedback.impact(.light)
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func scenarioCard(scenario: FamilyProtectorView.QuestScenario) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized(scenario.titleKey))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Text(localizationManager.localized(scenario.scenarioKey))
                .font(.body)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            
            Text(localizationManager.localized("family_protector_scenario_what_do"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
                .padding(.top, Spacing.s)
            
            VStack(spacing: Spacing.s) {
                ForEach(0..<scenario.optionKeys.count, id: \.self) { index in
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
                            Text(localizationManager.localized(scenario.optionKeys[index]))
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
                Text(selectedAnswer == scenario.correctAnswer ? localizationManager.localized("family_protector_correct") : localizationManager.localized("family_protector_incorrect"))
                    .font(.bodyBold)
                    .foregroundColor(selectedAnswer == scenario.correctAnswer ? .successGreen : .dangerRed)
                
                Spacer()
            }
            
            Text(localizationManager.localized(scenario.explanationKey))
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
            return localizationManager.localized("family_protector_select_answer")
        } else if showExplanation {
            return currentScenario == scenarios.count - 1 ? localizationManager.localized("family_protector_finish") : localizationManager.localized("family_protector_next")
        } else {
            return localizationManager.localized("family_protector_continue")
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
            .environmentObject(LocalizationManager())
    }
}
#endif

