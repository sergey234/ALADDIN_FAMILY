import SwiftUI

/// 🛡️ Young Defender View
/// Образовательная игра: уроки безопасности для детей
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct YoungDefenderView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var settingsManager = GamesSettingsManager.shared
    
    // Прогресс урока (сохраняется в AppStorage)
    @AppStorage("young_defender_current_lesson") private var storedCurrentLesson: Int = 0
    @State private var currentLesson: Int = 0 {
        didSet { storedCurrentLesson = currentLesson }
    }
    
    @AppStorage("young_defender_completed_lessons") private var storedCompletedLessons: Int = 0
    @State private var completedLessons: Int = 0 {
        didSet { storedCompletedLessons = completedLessons }
    }
    
    @AppStorage("young_defender_total_score") private var storedTotalScore: Int = 0
    @State private var totalScore: Int = 0 {
        didSet { storedTotalScore = totalScore }
    }
    
    @State private var showQuiz: Bool = false
    
    // MARK: - Lessons Data
    
    struct Lesson {
        let id: Int
        let icon: String
        let titleKey: String
        let descriptionKey: String
        let contentKeys: [String]  // Ключи локализации для параграфов урока
        let quizQuestions: [QuizQuestion]
    }
    
    struct QuizQuestion {
        let questionKey: String
        let optionKeys: [String]
        let correctAnswer: Int
    }
    
    // Computed property для локализованных уроков
    private var lessons: [Lesson] {
        [
        Lesson(
            id: 1,
            icon: "🔐",
            titleKey: "young_defender_lesson_1_title",
            descriptionKey: "young_defender_lesson_1_desc",
            contentKeys: [
                "young_defender_lesson_1_content_1",
                "young_defender_lesson_1_content_2",
                "young_defender_lesson_1_content_3",
                "young_defender_lesson_1_content_4",
                "young_defender_lesson_1_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_1_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_1_quiz_1_a1",
                        "young_defender_lesson_1_quiz_1_a2",
                        "young_defender_lesson_1_quiz_1_a3",
                        "young_defender_lesson_1_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_1_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_1_quiz_2_a1",
                        "young_defender_lesson_1_quiz_2_a2",
                        "young_defender_lesson_1_quiz_2_a3",
                        "young_defender_lesson_1_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_1_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_1_quiz_3_a1",
                        "young_defender_lesson_1_quiz_3_a2",
                        "young_defender_lesson_1_quiz_3_a3",
                        "young_defender_lesson_1_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 2,
            icon: "🎣",
            titleKey: "young_defender_lesson_2_title",
            descriptionKey: "young_defender_lesson_2_desc",
            contentKeys: [
                "young_defender_lesson_2_content_1",
                "young_defender_lesson_2_content_2",
                "young_defender_lesson_2_content_3",
                "young_defender_lesson_2_content_4",
                "young_defender_lesson_2_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_2_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_2_quiz_1_a1",
                        "young_defender_lesson_2_quiz_1_a2",
                        "young_defender_lesson_2_quiz_1_a3",
                        "young_defender_lesson_2_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_2_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_2_quiz_2_a1",
                        "young_defender_lesson_2_quiz_2_a2",
                        "young_defender_lesson_2_quiz_2_a3",
                        "young_defender_lesson_2_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_2_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_2_quiz_3_a1",
                        "young_defender_lesson_2_quiz_3_a2",
                        "young_defender_lesson_2_quiz_3_a3",
                        "young_defender_lesson_2_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 3,
            icon: "📱",
            titleKey: "young_defender_lesson_3_title",
            descriptionKey: "young_defender_lesson_3_desc",
            contentKeys: [
                "young_defender_lesson_3_content_1",
                "young_defender_lesson_3_content_2",
                "young_defender_lesson_3_content_3",
                "young_defender_lesson_3_content_4",
                "young_defender_lesson_3_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_3_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_3_quiz_1_a1",
                        "young_defender_lesson_3_quiz_1_a2",
                        "young_defender_lesson_3_quiz_1_a3",
                        "young_defender_lesson_3_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_3_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_3_quiz_2_a1",
                        "young_defender_lesson_3_quiz_2_a2",
                        "young_defender_lesson_3_quiz_2_a3",
                        "young_defender_lesson_3_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_3_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_3_quiz_3_a1",
                        "young_defender_lesson_3_quiz_3_a2",
                        "young_defender_lesson_3_quiz_3_a3",
                        "young_defender_lesson_3_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 4,
            icon: "🌐",
            titleKey: "young_defender_lesson_4_title",
            descriptionKey: "young_defender_lesson_4_desc",
            contentKeys: [
                "young_defender_lesson_4_content_1",
                "young_defender_lesson_4_content_2",
                "young_defender_lesson_4_content_3",
                "young_defender_lesson_4_content_4",
                "young_defender_lesson_4_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_4_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_4_quiz_1_a1",
                        "young_defender_lesson_4_quiz_1_a2",
                        "young_defender_lesson_4_quiz_1_a3",
                        "young_defender_lesson_4_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_4_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_4_quiz_2_a1",
                        "young_defender_lesson_4_quiz_2_a2",
                        "young_defender_lesson_4_quiz_2_a3",
                        "young_defender_lesson_4_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_4_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_4_quiz_3_a1",
                        "young_defender_lesson_4_quiz_3_a2",
                        "young_defender_lesson_4_quiz_3_a3",
                        "young_defender_lesson_4_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 5,
            icon: "📧",
            titleKey: "young_defender_lesson_5_title",
            descriptionKey: "young_defender_lesson_5_desc",
            contentKeys: [
                "young_defender_lesson_5_content_1",
                "young_defender_lesson_5_content_2",
                "young_defender_lesson_5_content_3",
                "young_defender_lesson_5_content_4",
                "young_defender_lesson_5_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_5_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_5_quiz_1_a1",
                        "young_defender_lesson_5_quiz_1_a2",
                        "young_defender_lesson_5_quiz_1_a3",
                        "young_defender_lesson_5_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_5_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_5_quiz_2_a1",
                        "young_defender_lesson_5_quiz_2_a2",
                        "young_defender_lesson_5_quiz_2_a3",
                        "young_defender_lesson_5_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_5_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_5_quiz_3_a1",
                        "young_defender_lesson_5_quiz_3_a2",
                        "young_defender_lesson_5_quiz_3_a3",
                        "young_defender_lesson_5_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 6,
            icon: "⚠️",
            titleKey: "young_defender_lesson_6_title",
            descriptionKey: "young_defender_lesson_6_desc",
            contentKeys: [
                "young_defender_lesson_6_content_1",
                "young_defender_lesson_6_content_2",
                "young_defender_lesson_6_content_3",
                "young_defender_lesson_6_content_4",
                "young_defender_lesson_6_content_5"
            ],
            quizQuestions: [
                QuizQuestion(
                    questionKey: "young_defender_lesson_6_quiz_1_q",
                    optionKeys: [
                        "young_defender_lesson_6_quiz_1_a1",
                        "young_defender_lesson_6_quiz_1_a2",
                        "young_defender_lesson_6_quiz_1_a3",
                        "young_defender_lesson_6_quiz_1_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_6_quiz_2_q",
                    optionKeys: [
                        "young_defender_lesson_6_quiz_2_a1",
                        "young_defender_lesson_6_quiz_2_a2",
                        "young_defender_lesson_6_quiz_2_a3",
                        "young_defender_lesson_6_quiz_2_a4"
                    ],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    questionKey: "young_defender_lesson_6_quiz_3_q",
                    optionKeys: [
                        "young_defender_lesson_6_quiz_3_a1",
                        "young_defender_lesson_6_quiz_3_a2",
                        "young_defender_lesson_6_quiz_3_a3",
                        "young_defender_lesson_6_quiz_3_a4"
                    ],
                    correctAnswer: 1
                )
            ]
        )
        ]
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
                        // Прогресс-бар
                        progressCard
                        
                        // Список уроков
                        lessonsList
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showQuiz) {
            if currentLesson < lessons.count {
                QuizView(
                    lesson: lessons[currentLesson],
                    onComplete: { score in
                        completeLesson(score: score)
                    }
                )
            }
        }
        .onAppear {
            // Восстанавливаем сохранённый прогресс из AppStorage
            completedLessons = storedCompletedLessons
            totalScore = storedTotalScore
            currentLesson = storedCurrentLesson
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
            
            Text(localizationManager.localized("young_defender_title"))
                .font(.h2)
                .foregroundColor(.primaryBlue)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Progress Card
    
    private var progressCard: some View {
        VStack(spacing: Spacing.m) {
            // Иконка
            Text("🛡️")
                .font(.system(size: 56))
            
            // Статистика
            HStack(spacing: Spacing.l) {
                VStack {
                    Text("\(completedLessons)")
                        .font(.h1)
                        .foregroundColor(.primaryBlue)
                    Text(String(format: localizationManager.localized("young_defender_progress_from"), lessons.count))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(totalScore)")
                        .font(.h1)
                        .foregroundColor(.successGreen)
                    Text(localizationManager.localized("young_defender_progress_points"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(calculateBonuses())")
                        .font(.h1)
                        .foregroundColor(.secondaryGold)
                    Text(localizationManager.localized("young_defender_progress_bonuses"))
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
                                colors: [.primaryBlue, .secondaryBlue],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: geometry.size.width * progress, height: 20)
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
    
    // MARK: - Lessons List
    
    private var lessonsList: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("young_defender_lessons_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            ForEach(0..<lessons.count, id: \.self) { index in
                lessonCard(lesson: lessons[index], index: index)
            }
        }
    }
    
    private func lessonCard(lesson: Lesson, index: Int) -> some View {
        let isCompleted = index < completedLessons
        let isLocked = index > completedLessons
        
        return Button(action: {
            if !isLocked {
                HapticFeedback.impact(.medium)
                currentLesson = index
                showQuiz = true
            }
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка урока
                Text(lesson.icon)
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(isCompleted ? Color.successGreen.opacity(0.2) : 
                                  isLocked ? Color.textSecondary.opacity(0.1) : 
                                  Color.primaryBlue.opacity(0.2))
                    )
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(localizationManager.localized(lesson.titleKey))
                            .font(.bodyBold)
                            .foregroundColor(isCompleted ? .successGreen : .textPrimary)
                        
                        Spacer()
                        
                        // Статус
                        if isCompleted {
                            Text("✅")
                                .font(.system(size: 20))
                        } else if isLocked {
                            Text("🔒")
                                .font(.system(size: 20))
                        } else {
                            Text("▶️")
                                .font(.system(size: 20))
                        }
                    }
                    
                    Text(localizationManager.localized(lesson.descriptionKey))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                    
                    if isCompleted {
                        Text(String(format: localizationManager.localized("young_defender_lesson_reward_earned"), settingsManager.lessonReward))
                            .font(.captionSmall)
                            .foregroundColor(.successGreen)
                    }
                }
                
                Spacer()
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(isLocked ? Color.backgroundMedium.opacity(0.3) : Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(
                                isCompleted ? Color.successGreen.opacity(0.5) :
                                isLocked ? Color.textSecondary.opacity(0.2) :
                                Color.primaryBlue.opacity(0.3),
                                lineWidth: isCompleted ? 2 : 1
                            )
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(isLocked)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Computed Properties
    
    private var progress: Double {
        Double(completedLessons) / Double(lessons.count)
    }
    
    // MARK: - Methods
    
    private func completeLesson(score: Int) {
        totalScore += score
        
        if !lessons[currentLesson].quizQuestions.isEmpty {
            // Добавляем награду за урок
            let lessonReward = settingsManager.lessonReward
            totalScore += lessonReward
            
            // Обновляем баланс единорогов ребёнка
            if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                let newBalance = storedBalance + lessonReward
                UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
            }
            
            completedLessons += 1
            
            // Проверяем бонусы за серию
            if completedLessons == 5 {
                let bonus5 = settingsManager.bonus5Lessons
                totalScore += bonus5
                if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                    let newBalance = storedBalance + bonus5
                    UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
                }
            } else if completedLessons == lessons.count {
                let bonusAll = settingsManager.bonusAll6
                totalScore += bonusAll
                if let storedBalance = UserDefaults.standard.object(forKey: "child_unicorn_balance") as? Int {
                    let newBalance = storedBalance + bonusAll
                    UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
                }
            }
            
            HapticFeedback.notification(.success)
        }
    }
    
    private func calculateBonuses() -> Int {
        var bonus = completedLessons * settingsManager.lessonReward
        if completedLessons >= 5 {
            bonus += settingsManager.bonus5Lessons
        }
        if completedLessons == lessons.count {
            bonus += settingsManager.bonusAll6
        }
        return bonus
    }
}

// MARK: - Quiz View

struct QuizView: View {
    let lesson: YoungDefenderView.Lesson
    let onComplete: (Int) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var currentQuestion = 0
    @State private var score = 0
    @State private var selectedAnswer: Int? = nil
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: Spacing.l) {
                    // Прогресс вопросов
                    Text(String(format: localizationManager.localized("young_defender_quiz_question"), currentQuestion + 1, lesson.quizQuestions.count))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    // Текущий вопрос
                    if currentQuestion < lesson.quizQuestions.count {
                        quizCard(question: lesson.quizQuestions[currentQuestion])
                    }
                    
                    // Кнопка продолжить
                    Button(action: {
                        if selectedAnswer != nil {
                            HapticFeedback.impact(.medium)
                            goToNextQuestion()
                        }
                    }) {
                        Text(selectedAnswer == nil ? localizationManager.localized("young_defender_quiz_select") : 
                             currentQuestion == lesson.quizQuestions.count - 1 ? localizationManager.localized("young_defender_quiz_finish") : localizationManager.localized("young_defender_quiz_next"))
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(selectedAnswer != nil ? Color.primaryBlue : Color.textSecondary)
                            )
                    }
                    .disabled(selectedAnswer == nil)
                    .padding(.horizontal, Spacing.screenPadding)
                    
                    Spacer()
                }
                .padding(.top, Spacing.l)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("young_defender_quiz_close")) {
                        HapticFeedback.impact(.light)
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func quizCard(question: YoungDefenderView.QuizQuestion) -> some View {
        VStack(spacing: Spacing.l) {
            Text(localizationManager.localized(question.questionKey))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            
            VStack(spacing: Spacing.s) {
                ForEach(0..<question.optionKeys.count, id: \.self) { index in
                    Button(action: {
                        HapticFeedback.impact(.light)
                        selectedAnswer = index
                    }) {
                        HStack {
                            Text(localizationManager.localized(question.optionKeys[index]))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            Spacer()
                            
                            if selectedAnswer == index {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.primaryBlue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(selectedAnswer == index ? 
                                      Color.primaryBlue.opacity(0.2) : 
                                      Color.backgroundMedium.opacity(0.5))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(
                                            selectedAnswer == index ? Color.primaryBlue : Color.clear,
                                            lineWidth: 2
                                        )
                                )
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
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
    
    private func goToNextQuestion() {
        if let answer = selectedAnswer {
            if answer == lesson.quizQuestions[currentQuestion].correctAnswer {
                score += 1
                HapticFeedback.notification(.success)
            } else {
                HapticFeedback.notification(.error)
            }
        }
        
        if currentQuestion < lesson.quizQuestions.count - 1 {
            currentQuestion += 1
            selectedAnswer = nil
        } else {
            // Квиз завершён
            onComplete(score)
            dismiss()
        }
    }
}

// MARK: - Preview

#if DEBUG
struct YoungDefenderView_Previews: PreviewProvider {
    static var previews: some View {
        YoungDefenderView()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
#endif

