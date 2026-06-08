import SwiftUI

/// 🛡️ Security Education Screen
/// Экран обучения безопасности для детей
/// Приветствие, уровень безопасности, уроки и прогресс
struct SecurityEducationScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    @State private var selectedLesson: SecurityLesson? = nil
    @State private var securityLevel: Int = 5
    @State private var securityXP: Int = 1247
    @State private var totalLessonsCompleted: Int = 12
    @State private var unicornsEarned: Int = 0
    @State private var showRewardAlert: Bool = false
    
    private let cardBackgroundColor = Color(UIColor.systemBackground)
    private let primaryTextColor = Color(UIColor.label)
    private let secondaryTextColor = Color(UIColor.secondaryLabel)
    
    // MARK: - Security Lessons
    
    struct SecurityLesson: Identifiable {
        let id = UUID()
        let icon: String
        let title: String
        let description: String
        let isCompleted: Bool
        let xpReward: Int
    }
    
    private var lessons: [SecurityLesson] {
        [
            SecurityLesson(icon: "🛡️", title: localizationManager.localized("security_education_lesson_cybersecurity"), description: localizationManager.localized("security_education_lesson_cybersecurity_desc"), isCompleted: true, xpReward: 100),
            SecurityLesson(icon: "🎣", title: localizationManager.localized("security_education_lesson_phishing"), description: localizationManager.localized("security_education_lesson_phishing_desc"), isCompleted: true, xpReward: 80),
            SecurityLesson(icon: "🕵️", title: localizationManager.localized("security_education_lesson_social_engineering"), description: localizationManager.localized("security_education_lesson_social_engineering_desc"), isCompleted: false, xpReward: 90),
            SecurityLesson(icon: "🔐", title: localizationManager.localized("security_education_lesson_passwords"), description: localizationManager.localized("security_education_lesson_passwords_desc"), isCompleted: false, xpReward: 70)
        ]
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .growWarm)
            
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
                .environmentObject(localizationManager)
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
            .accessibilityLabel(localizationManager.localized("security_education_back"))
            
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("security_education_title"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                Text(localizationManager.localized("security_education_subtitle"))
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
            Text(String(format: localizationManager.localized("security_education_greeting_name"), "Алексей"))
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(primaryTextColor)
            Text(localizationManager.localized("security_education_greeting_message"))
                .font(.system(size: 16))
                .foregroundColor(secondaryTextColor)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 16)
                    .fill(cardBackgroundColor)
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
                    Text(String(format: localizationManager.localized("security_education_level"), securityLevel))
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(primaryTextColor)
                    Text(localizationManager.localized("security_education_level_title"))
                        .font(.system(size: 14))
                        .foregroundColor(secondaryTextColor)
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
                Text(String(format: localizationManager.localized("security_education_xp"), securityXP))
                    .font(.system(size: 12))
                    .foregroundColor(secondaryTextColor)
                Spacer()
                Text(String(format: localizationManager.localized("security_education_lessons_completed"), totalLessonsCompleted))
                    .font(.system(size: 12))
                    .foregroundColor(secondaryTextColor)
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(cardBackgroundColor)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
    
    // MARK: - Lessons List
    
    private var lessonsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("security_education_lessons_title"))
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 4)
            
            ForEach(lessons) { lesson in
                LessonCard(lesson: lesson) {
                    selectedLesson = lesson
                }
                .environmentObject(localizationManager)
            }
        }
    }
    
    // MARK: - Simple Rules Card
    
    private var simpleRulesCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("security_education_simple_rules_title"))
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(primaryTextColor)
            
            VStack(alignment: .leading, spacing: 8) {
                RuleRow(text: localizationManager.localized("security_education_rule_strangers"))
                RuleRow(text: localizationManager.localized("security_education_rule_emails"))
                RuleRow(text: localizationManager.localized("security_education_rule_parents"))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(cardBackgroundColor)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
    
    // MARK: - Advanced Tips Card
    
    private var advancedTipsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("security_education_advanced_tips_title"))
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(primaryTextColor)
            
            VStack(alignment: .leading, spacing: 8) {
                TipRow(text: localizationManager.localized("security_education_tip_2fa"))
                TipRow(text: localizationManager.localized("security_education_tip_url"))
                TipRow(text: localizationManager.localized("security_education_tip_social"))
                TipRow(text: localizationManager.localized("security_education_tip_wifi"))
                TipRow(text: localizationManager.localized("security_education_tip_updates"))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(cardBackgroundColor)
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 4)
        )
    }
}

// MARK: - Lesson Card

struct LessonCard: View {
    let lesson: SecurityEducationScreen.SecurityLesson
    let action: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
                        .foregroundColor(Color(UIColor.label))
                        .lineLimit(1)
                    
                    Text(lesson.description)
                        .font(.system(size: 14))
                        .foregroundColor(Color(UIColor.secondaryLabel))
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
                    
                    Text(String(format: localizationManager.localized("security_education_xp_reward"), lesson.xpReward))
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundColor(.secondary)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(UIColor.systemBackground))
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
                .foregroundColor(Color(UIColor.label))
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
                .foregroundColor(Color(UIColor.label))
        }
    }
}

// MARK: - Lesson Detail View

struct LessonDetailView: View {
    let lesson: SecurityEducationScreen.SecurityLesson
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @State private var hasLearned: Bool = false
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .growWarm)
            
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
                            Text(localizationManager.localized("security_education_lesson_study"))
                                .font(.system(size: 16, weight: .semibold))
                            Text(String(format: localizationManager.localized("security_education_lesson_reward"), lesson.xpReward))
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
                        Text(localizationManager.localized("security_education_lesson_completed"))
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(.white)
                        
                        Text(String(format: localizationManager.localized("security_education_lesson_reward"), lesson.xpReward))
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
                        Text(localizationManager.localized("security_education_lesson_continue"))
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
