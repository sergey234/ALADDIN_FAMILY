import SwiftUI

/// 🛡️ Security Education Screen
/// Экран обучения безопасности для детей
/// Приветствие, уровень безопасности, уроки и прогресс
struct SecurityEducationScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss
    
    @State private var selectedLesson: SecurityLesson? = nil
    @State private var securityLevel: Int = 5
    @State private var securityXP: Int = 1247
    @State private var totalLessonsCompleted: Int = 12
    @State private var unicornsEarned: Int = 0
    @State private var showRewardAlert: Bool = false
    
    // MARK: - Security Lessons
    
    struct SecurityLesson: Identifiable {
        let id = UUID()
        let icon: String
        let title: String
        let description: String
        let isCompleted: Bool
        let xpReward: Int
    }
    
    private var lessons: [SecurityLesson] = [
        SecurityLesson(icon: "🛡️", title: "Киберзащита", description: "Стань экспертом по безопасности", isCompleted: true, xpReward: 100),
        SecurityLesson(icon: "🎣", title: "Фишинг", description: "Распознай опасные письма", isCompleted: true, xpReward: 80),
        SecurityLesson(icon: "🕵️", title: "Соц. инженерия", description: "Защитись от манипуляций", isCompleted: false, xpReward: 90),
        SecurityLesson(icon: "🔐", title: "Пароли", description: "Создай надёжный пароль", isCompleted: false, xpReward: 70)
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient(
                colors: [
                    Color.blue,
                    Color.blue.opacity(0.8),
                    Color.blue.opacity(0.6)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Заголовок
                header
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 20) {
                        // Приветствие
                        greetingCard
                        
                        // Уровень безопасности
                        securityLevelCard
                        
                        // Список уроков
                        lessonsList
                        
                        // Простые правила
                        simpleRulesCard
                        
                        // Продвинутые советы
                        advancedTipsCard
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                    .padding(.bottom, 32)
                }
            }
        }
        .sheet(item: $selectedLesson) { lesson in
            LessonDetailView(lesson: lesson)
        }
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack(spacing: 16) {
            Button(action: {
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.white.opacity(0.2))
                    )
            }
            .accessibilityLabel("Назад")
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Безопасность")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                Text("Обучение защите")
                    .font(.system(size: 14, weight: .regular))
                    .foregroundColor(.white.opacity(0.8))
            }
            
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.top, 16)
        .padding(.bottom, 12)
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        VStack(spacing: 12) {
            Text("👋")
                .font(.system(size: 50))
            Text("Привет, Алексей!")
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.primary)
            Text("Ты молодец! Продолжай изучать безопасность!")
                .font(.system(size: 16))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
    
    // MARK: - Security Level Card
    
    private var securityLevelCard: some View {
        VStack(spacing: 12) {
            HStack {
                Text("🛡️")
                    .font(.system(size: 32))
                VStack(alignment: .leading, spacing: 4) {
                    Text("Уровень \(securityLevel)")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.primary)
                    Text("Защитник семьи")
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                }
                Spacer()
            }
            
            // Прогресс-бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 12)
                    
                    RoundedRectangle(cornerRadius: 8)
                        .fill(LinearGradient(
                            colors: [Color.blue, Color.blue.opacity(0.8)],
                            startPoint: .leading,
                            endPoint: .trailing
                        ))
                        .frame(width: geometry.size.width * 0.75, height: 12)
                }
            }
            .frame(height: 12)
            
            HStack {
                Text("\(securityXP) XP")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(totalLessonsCompleted) уроков пройдено")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
    
    // MARK: - Lessons List
    
    private var lessonsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Уроки безопасности")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 4)
            
            ForEach(lessons) { lesson in
                LessonCard(lesson: lesson) {
                    selectedLesson = lesson
                }
            }
        }
    }
    
    // MARK: - Simple Rules Card
    
    private var simpleRulesCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("✅ Простые правила")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
            
            VStack(alignment: .leading, spacing: 8) {
                RuleRow(text: "Не разговаривай с незнакомцами")
                RuleRow(text: "Не открывай странные письма")
                RuleRow(text: "Позови маму или папу если страшно")
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
    
    // MARK: - Advanced Tips Card
    
    private var advancedTipsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("💡 Продвинутые советы")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.primary)
            
            VStack(alignment: .leading, spacing: 8) {
                TipRow(text: "Используй двухфакторную аутентификацию (2FA)")
                TipRow(text: "Проверяй URL перед переходом по ссылкам")
                TipRow(text: "Не публикуй личную информацию в соц. сетях")
                TipRow(text: "Используй VPN в общественных Wi-Fi")
                TipRow(text: "Обновляй приложения регулярно")
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
}

// MARK: - Lesson Card

struct LessonCard: View {
    let lesson: SecurityEducationScreen.SecurityLesson
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: 16) {
                Text(lesson.icon)
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        Circle()
                            .fill(Color.blue.opacity(0.1))
                    )
                
                VStack(alignment: .leading, spacing: 6) {
                    Text(lesson.title)
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.primary)
                        .lineLimit(1)
                    
                    Text(lesson.description)
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                Spacer()
                
                VStack(spacing: 4) {
                    if lesson.isCompleted {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.green)
                    } else {
                        Image(systemName: "play.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.blue)
                    }
                    
                    Text("+\(lesson.xpReward) XP")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.secondary)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white)
                    .shadow(color: .black.opacity(0.1), radius: 8, x: 0, y: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Rule Row

struct RuleRow: View {
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color.blue)
                .frame(width: 8, height: 8)
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.primary)
        }
    }
}

// MARK: - Tip Row

struct TipRow: View {
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("•")
                .font(.system(size: 20))
                .foregroundColor(.blue)
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(.primary)
        }
    }
}

// MARK: - Lesson Detail View

struct LessonDetailView: View {
    let lesson: SecurityEducationScreen.SecurityLesson
    @Environment(\.dismiss) private var dismiss
    @State private var hasLearned: Bool = false
    
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color.blue,
                    Color.blue.opacity(0.8),
                    Color.blue.opacity(0.6)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 20) {
                Text(lesson.icon)
                    .font(.system(size: 80))
                
                Text(lesson.title)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                
                Text(lesson.description)
                    .font(.system(size: 16))
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
                
                Spacer()
                
                if !hasLearned {
                    Button(action: {
                        // Изучаем урок
                        hasLearned = true
                        
                        // Haptic feedback
                        let generator = UIImpactFeedbackGenerator(style: .heavy)
                        generator.impactOccurred()
                        
                        // Сохраняем в UserDefaults
                        UserDefaults.standard.set(true, forKey: "lesson_\(lesson.id.uuidString)_completed")
                        
                        // Закрываем через 1 секунду
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                            dismiss()
                        }
                    }) {
                        VStack(spacing: 8) {
                            Text("🎓 Изучить урок")
                                .font(.system(size: 16, weight: .semibold))
                            Text("+\(lesson.xpReward) XP +10 🦄")
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(.green)
                        }
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.white)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal, 40)
                    .padding(.bottom, 40)
                } else {
                    VStack(spacing: 12) {
                        Text("✅ Урок изучен!")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(.white)
                        
                        Text("+\(lesson.xpReward) XP • +10 🦄")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.green)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 10)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.white.opacity(0.2))
                            )
                    }
                    
                    Button(action: {
                        dismiss()
                    }) {
                        Text("Продолжить")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.blue)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(Color.white)
                            .cornerRadius(12)
                    }
                    .padding(.horizontal, 40)
                    .padding(.bottom, 40)
                }
            }
        }
    }
}

// MARK: - Preview

struct SecurityEducationScreen_Previews: PreviewProvider {
    static var previews: some View {
        SecurityEducationScreen()
            .environmentObject(NavigationManager())
    }
}
