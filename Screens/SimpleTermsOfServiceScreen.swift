import SwiftUI

/**
 * 📜 Simple Terms of Service Screen
 * Простые условия использования без WebKit
 */

struct SimpleTermsOfServiceScreen: View {
    
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
                    
                    Text("Условия использования")
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
                        Text("УСЛОВИЯ ИСПОЛЬЗОВАНИЯ")
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                        
                        Text("Последнее обновление: 29 октября 2024")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            termsSection(
                                title: "1. Принятие условий",
                                content: "Используя приложение ALADDIN, вы соглашаетесь с данными условиями использования."
                            )
                            
                            termsSection(
                                title: "2. Описание сервиса",
                                content: "ALADDIN - это приложение для защиты семьи от киберугроз, включающее защиту сети, родительский контроль и мониторинг безопасности."
                            )
                            
                            termsSection(
                                title: "3. Обязанности пользователя",
                                content: "Вы обязуетесь использовать приложение только в законных целях и не нарушать права других пользователей."
                            )
                            
                            termsSection(
                                title: "4. Ограничения",
                                content: "Запрещается использование приложения для незаконной деятельности, взлома или нарушения работы сервиса."
                            )
                            
                            termsSection(
                                title: "5. Ответственность",
                                content: "Мы не несем ответственности за ущерб, причиненный неправильным использованием приложения."
                            )
                            
                            termsSection(
                                title: "6. Изменения условий",
                                content: "Мы оставляем за собой право изменять условия использования. Пользователи будут уведомлены об изменениях."
                            )
                        }
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    private func termsSection(title: String, content: String) -> some View {
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

struct SimpleTermsOfServiceScreen_Previews: PreviewProvider {
    static var previews: some View {
        SimpleTermsOfServiceScreen()
    }
}
