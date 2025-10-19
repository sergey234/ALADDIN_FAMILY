import SwiftUI

/// 💬 Support Screen
/// Экран поддержки - помощь и FAQ
/// Источник дизайна: комбинация из разных wireframes
struct SupportScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var searchText: String = ""
    
    struct FAQItem: Identifiable {
        let id = UUID()
        let icon: String
        let question: String
        let answer: String
        var isExpanded: Bool = false
    }
    
    @State private var faqItems: [FAQItem] = [
        FAQItem(icon: "🛡️", question: "Как работает VPN?", answer: "VPN шифрует весь ваш интернет-трафик и скрывает IP адрес."),
        FAQItem(icon: "👶", question: "Как настроить родительский контроль?", answer: "Перейдите в раздел Семья → выберите ребёнка → настройте ограничения."),
        FAQItem(icon: "💳", question: "Как отменить подписку?", answer: "Настройки → Управление подпиской → Отменить подписку."),
        FAQItem(icon: "🔐", question: "Безопасны ли мои данные?", answer: "Да! Мы используем шифрование и не храним личные данные на серверах.")
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    VStack {
                        Text("ПОДДЕРЖКА")
                            .font(.headline)
                            .foregroundColor(.white)
                        
                        Text("Мы всегда рядом")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                    
                    Color.clear
                        .frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.lg) {
                        // Поиск
                        searchBar
                        
                        // Способы связи
                        contactMethods
                        
                        // FAQ
                        faqSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Search Bar
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.textSecondary)
            
            TextField("Поиск по вопросам...", text: $searchText)
                .textFieldStyle(PlainTextFieldStyle())
        }
        .padding()
        .background(Color.backgroundMedium)
        .cornerRadius(CornerRadius.md)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Contact Methods
    
    private var contactMethods: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            Text("СВЯЗАТЬСЯ С НАМИ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.sm) {
                contactButton(icon: "💬", title: "Чат с поддержкой", subtitle: "Ответим за 5 минут", color: .primaryBlue)
                contactButton(icon: "📧", title: "Email", subtitle: "support@aladdin.family", color: .green)
                contactButton(icon: "📱", title: "Телефон", subtitle: "+7 (800) 555-35-35", color: .orange)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func contactButton(icon: String, title: String, subtitle: String, color: Color) -> some View {
        Button(action: {
            print(title)
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 32))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(title)
                        .font(.body.bold())
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(color)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.md)
                    .fill(Color.backgroundMedium.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.md)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - FAQ Section
    
    private var faqSection: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            Text("ЧАСТЫЕ ВОПРОСЫ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.sm) {
                ForEach($faqItems) { $item in
                    faqCard(item: $item)
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func faqCard(item: Binding<FAQItem>) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Вопрос
            Button(action: {
                withAnimation(.spring()) {
                    item.wrappedValue.isExpanded.toggle()
                }
            }) {
                HStack(spacing: Spacing.m) {
                    Text(item.wrappedValue.icon)
                        .font(.system(size: 24))
                    
                    Text(item.wrappedValue.question)
                        .font(.body.bold())
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Image(systemName: item.wrappedValue.isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.primaryBlue)
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Ответ (раскрывается)
            if item.wrappedValue.isExpanded {
                Text(item.wrappedValue.answer)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding(.leading, 36)
                    .transition(.opacity)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.md)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}

// MARK: - Preview

struct SupportScreen_Previews: PreviewProvider {
    static var previews: some View {
        SupportScreen()
    }
}



