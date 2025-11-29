import SwiftUI

/// 🛡️ Young Defender View
/// Образовательная игра: уроки безопасности для детей
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct YoungDefenderView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
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
        let title: String
        let description: String
        let content: [String]  // Параграфы урока
        let quizQuestions: [QuizQuestion]
    }
    
    struct QuizQuestion {
        let question: String
        let options: [String]
        let correctAnswer: Int
    }
    
    let lessons: [Lesson] = [
        Lesson(
            id: 1,
            icon: "🔐",
            title: "Безопасные пароли",
            description: "Как создать надёжный пароль",
            content: [
                "Пароль должен быть длинным (минимум 8 символов)",
                "Используй буквы, цифры и символы",
                "Не используй своё имя или дату рождения",
                "Не сообщай пароль никому, даже друзьям",
                "Используй разные пароли для разных сайтов"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Пароль должен быть:",
                    options: ["Коротким", "Длинным (8+ символов)", "Только цифрами", "Твоим именем"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что НЕЛЬЗЯ использовать в пароле?",
                    options: ["Буквы", "Дату рождения", "Цифры", "Символы"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли сообщать пароль друзьям?",
                    options: ["Да, друзьям можно", "Нет, никому нельзя", "Только родителям", "Только в экстренном случае"],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 2,
            icon: "🎣",
            title: "Фишинг",
            description: "Как распознать обман в интернете",
            content: [
                "Фишинг - это обман, когда тебя пытаются обмануть",
                "Подозрительные письма могут быть опасными",
                "Не переходи по ссылкам от незнакомцев",
                "Если что-то кажется слишком хорошим - это может быть обман",
                "Всегда спрашивай родителей, если сомневаешься"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Что такое фишинг?",
                    options: ["Рыбалка", "Обман в интернете", "Игра", "Социальная сеть"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что делать с подозрительным письмом?",
                    options: ["Открыть сразу", "Показать родителям", "Переслать друзьям", "Удалить не читая"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли переходить по ссылкам от незнакомцев?",
                    options: ["Да, всегда", "Нет, это опасно", "Только если интересно", "Только днём"],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 3,
            icon: "📱",
            title: "Социальные сети",
            description: "Безопасное общение в соцсетях",
            content: [
                "Не публикуй личную информацию (адрес, телефон)",
                "Не дружи с незнакомыми людьми",
                "Показывай родителям сообщения от незнакомцев",
                "Не публикуй фото без разрешения родителей",
                "Помни: всё, что публикуешь, остаётся в интернете"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Можно ли публиковать свой адрес?",
                    options: ["Да, всем", "Нет, это опасно", "Только друзьям", "Только в профиле"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что делать с сообщениями от незнакомцев?",
                    options: ["Отвечать сразу", "Показать родителям", "Игнорировать всегда", "Блокировать автоматически"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли публиковать фото без разрешения родителей?",
                    options: ["Да, всегда", "Нет, нужно спросить", "Только свои", "Только в закрытых группах"],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 4,
            icon: "🌐",
            title: "Wi‑Fi",
            description: "Безопасное подключение к интернету",
            content: [
                "Подключайся только к известным Wi‑Fi сетям",
                "Не используй публичные Wi‑Fi без пароля",
                "Всегда спрашивай родителей перед подключением",
                "Пароль Wi‑Fi должен быть сложным",
                "Не дели паролем Wi‑Fi с незнакомцами"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Можно ли подключаться к незнакомым Wi‑Fi?",
                    options: ["Да, всегда", "Нет, это опасно", "Только бесплатным", "Только быстрым"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что делать перед подключением к новой сети?",
                    options: ["Подключаться сразу", "Спросить родителей", "Спросить друзей", "Попробовать подключиться"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли делиться паролем Wi‑Fi?",
                    options: ["Да, с друзьями", "Нет, только с родителями", "Да, всем", "Только днём"],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 5,
            icon: "📧",
            title: "Спам",
            description: "Как защититься от спама",
            content: [
                "Спам - это ненужные письма и сообщения",
                "Не отвечай на спам-сообщения",
                "Не переходи по ссылкам из спама",
                "Сообщи родителям о спаме",
                "Используй фильтры от спама"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Что такое спам?",
                    options: ["Еда", "Ненужные письма", "Игра", "Социальная сеть"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что делать со спам-сообщениями?",
                    options: ["Отвечать", "Удалять и показать родителям", "Переслать друзьям", "Игнорировать"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли переходить по ссылкам из спама?",
                    options: ["Да, иногда", "Нет, это опасно", "Только если интересно", "Только в приложениях"],
                    correctAnswer: 1
                )
            ]
        ),
        Lesson(
            id: 6,
            icon: "⚠️",
            title: "Вирусы",
            description: "Защита от вирусов и вредоносных программ",
            content: [
                "Вирусы могут повредить твой компьютер или телефон",
                "Не открывай файлы от незнакомцев",
                "Используй антивирус",
                "Не устанавливай программы из неизвестных источников",
                "Сообщи родителям, если устройство ведёт себя странно"
            ],
            quizQuestions: [
                QuizQuestion(
                    question: "Что такое вирус?",
                    options: ["Болезнь", "Вредоносная программа", "Игра", "Приложение"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Можно ли открывать файлы от незнакомцев?",
                    options: ["Да, всегда", "Нет, это опасно", "Только изображения", "Только текстовые"],
                    correctAnswer: 1
                ),
                QuizQuestion(
                    question: "Что делать, если устройство ведёт себя странно?",
                    options: ["Ничего", "Сообщить родителям", "Перезагрузить", "Удалить приложения"],
                    correctAnswer: 1
                )
            ]
        )
    ]
    
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
            
            Text("🛡️ Юный защитник")
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
                    Text("из \(lessons.count)\nуроков")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(totalScore)")
                        .font(.h1)
                        .foregroundColor(.successGreen)
                    Text("очков\nнабрано")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack {
                    Text("\(calculateBonuses())")
                        .font(.h1)
                        .foregroundColor(.secondaryGold)
                    Text("🦄\nбонусов")
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
            Text("📚 Уроки безопасности")
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
                        Text(lesson.title)
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
                    
                    Text(lesson.description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                    
                    if isCompleted {
                        Text("+\(settingsManager.lessonReward) 🦄 получено")
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
                    Text("Вопрос \(currentQuestion + 1) из \(lesson.quizQuestions.count)")
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
                        Text(selectedAnswer == nil ? "Выбери ответ" : 
                             currentQuestion == lesson.quizQuestions.count - 1 ? "Завершить" : "Далее")
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
                    Button("Закрыть") {
                        HapticFeedback.impact(.light)
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func quizCard(question: YoungDefenderView.QuizQuestion) -> some View {
        VStack(spacing: Spacing.l) {
            Text(question.question)
                .font(.h3)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            
            VStack(spacing: Spacing.s) {
                ForEach(0..<question.options.count, id: \.self) { index in
                    Button(action: {
                        HapticFeedback.impact(.light)
                        selectedAnswer = index
                    }) {
                        HStack {
                            Text(question.options[index])
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
    }
}
#endif

