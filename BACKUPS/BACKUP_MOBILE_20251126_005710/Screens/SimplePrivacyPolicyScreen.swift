import SwiftUI

/**
 * 📋 Simple Privacy Policy Screen
 * Простая политика конфиденциальности без WebKit
 */

struct SimplePrivacyPolicyScreen: View {
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Header
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .font(.title2)
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    Text("Политика конфиденциальности")
                        .font(.h2)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Color.clear.frame(width: 30)
                }
                .padding(.horizontal, Spacing.m)
                .padding(.top, Spacing.s)
                
                // Content
                ScrollView {
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ")
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                        
                        Text("Последнее обновление: 29 октября 2024")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            policySection(
                                title: "1. Сбор информации",
                                content: "Мы собираем только необходимую информацию для обеспечения безопасности вашей семьи. Никакие личные данные не передаются третьим лицам."
                            )
                            
                            policySection(
                                title: "2. Использование данных",
                                content: "Ваши данные используются исключительно для обеспечения защиты от киберугроз и улучшения работы приложения."
                            )
                            
                            policySection(
                                title: "3. Безопасность",
                                content: "Все данные шифруются и хранятся на защищенных серверах. Мы используем современные методы защиты информации."
                            )
                            
                            policySection(
                                title: "4. Ваши права",
                                content: "Вы можете в любое время запросить удаление ваших данных или изменить настройки конфиденциальности."
                            )
                            
                            policySection(
                                title: "5. Контакты",
                                content: "По вопросам конфиденциальности обращайтесь: privacy@aladdin.family"
                            )
                        }
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    private func policySection(title: String, content: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(title)
                .font(.bodyBold)
                .foregroundColor(.primaryBlue)
            
            Text(content)
                .font(.body)
                .foregroundColor(.textPrimary)
                .lineSpacing(4)
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}

// MARK: - Preview

struct SimplePrivacyPolicyScreen_Previews: PreviewProvider {
    static var previews: some View {
        SimplePrivacyPolicyScreen()
    }
}
