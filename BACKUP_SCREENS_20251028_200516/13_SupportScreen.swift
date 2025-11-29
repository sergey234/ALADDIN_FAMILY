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
            LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel("Фон экрана поддержки")
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel("Назад")
                    .accessibilityHint("Нажмите для возврата к предыдущему экрану")
                    
                    Spacer()
                    
                    VStack {
                        Text("ПОДДЕРЖКА")
                            .font(.headline)
                            .foregroundColor(.white)
                            .accessibilityLabel("ПОДДЕРЖКА")
                            .accessibilityAddTraits(.isHeader)
                        
                        Text("Мы всегда рядом")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .accessibilityLabel("Мы всегда рядом")
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Заголовок поддержки")
                    
                    Spacer()
                    
                    Color.clear
                        .frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Навигационная панель поддержки")
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 16) {
                        // Поиск
                        searchBar
                        
                        // Способы связи
                        contactMethods
                        
                        // FAQ
                        faqSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: 32)
                    }
                    .padding(.top, 12)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое поддержки")
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: 12)
        }
        .task {
            print("🚨 SupportScreen загружен!")
        }
    }
    
    // MARK: - Search Bar
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
                .accessibilityLabel("Поиск")
            
            TextField("Поиск по вопросам...", text: $searchText)
                .textFieldStyle(PlainTextFieldStyle())
                .accessibilityLabel("Поле поиска по вопросам")
                .accessibilityHint("Введите текст для поиска в часто задаваемых вопросах")
        }
        .padding()
        .background(Color.gray.opacity(0.3))
        .cornerRadius(8)
        .padding(.horizontal, 20)
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Поиск по вопросам")
    }
    
    // MARK: - Contact Methods
    
    private var contactMethods: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("СВЯЗАТЬСЯ С НАМИ")
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel("СВЯЗАТЬСЯ С НАМИ")
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 8) {
                contactButton(icon: "💬", title: "Чат с поддержкой", subtitle: "Ответим за 5 минут", color: .blue)
                contactButton(icon: "📧", title: "Email", subtitle: "support@aladdin.family", color: .green)
                contactButton(icon: "📱", title: "Телефон", subtitle: "+7 (800) 555-35-35", color: .orange)
            }
            .padding(.horizontal, 20)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Способы связи с поддержкой")
    }
    
    private func contactButton(icon: String, title: String, subtitle: String, color: Color) -> some View {
        Button(action: {
            print(title)
        }) {
            HStack(spacing: 12) {
                Text(icon)
                    .font(.system(size: 32))
                    .accessibilityLabel("Иконка \(title)")
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.body.bold())
                        .foregroundColor(.primary)
                        .accessibilityLabel("Название: \(title)")
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .accessibilityLabel("Описание: \(subtitle)")
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(title): \(subtitle)")
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(color)
                    .accessibilityLabel("Перейти")
            }
            .padding(12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
        .appGlassmorphism()
        .accessibilityLabel("\(title): \(subtitle)")
        .accessibilityHint("Нажмите для \(title.lowercased())")
    }
    
    // MARK: - FAQ Section
    
    private var faqSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("ЧАСТЫЕ ВОПРОСЫ")
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel("ЧАСТЫЕ ВОПРОСЫ")
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 8) {
                ForEach($faqItems) { $item in
                    faqCard(item: $item)
                }
            }
            .padding(.horizontal, 20)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Часто задаваемые вопросы")
    }
    
    private func faqCard(item: Binding<FAQItem>) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            // Вопрос
            Button(action: {
                withAnimation(.spring()) {
                    item.wrappedValue.isExpanded.toggle()
                }
            }) {
                HStack(spacing: 12) {
                    Text(item.wrappedValue.icon)
                        .font(.system(size: 24))
                        .accessibilityLabel("Иконка вопроса")
                    
                    Text(item.wrappedValue.question)
                        .font(.body.bold())
                        .foregroundColor(.primary)
                        .accessibilityLabel("Вопрос: \(item.wrappedValue.question)")
                    
                    Spacer()
                    
                    Image(systemName: item.wrappedValue.isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.blue)
                        .accessibilityLabel(item.wrappedValue.isExpanded ? "Свернуть ответ" : "Развернуть ответ")
                }
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel(item.wrappedValue.isExpanded ? "Свернуть: \(item.wrappedValue.question)" : "Развернуть: \(item.wrappedValue.question)")
            .accessibilityHint("Нажмите для \(item.wrappedValue.isExpanded ? "сворачивания" : "разворачивания") ответа")
            
            // Ответ (раскрывается)
            if item.wrappedValue.isExpanded {
                Text(item.wrappedValue.answer)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .padding(.leading, 36)
                    .transition(.opacity)
                    .accessibilityLabel("Ответ: \(item.wrappedValue.answer)")
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.3))
        )
        .cardShadow()
        .accessibilityElement(children: .contain)
        .accessibilityLabel("FAQ: \(item.wrappedValue.question)")
    }
}

// MARK: - Preview

struct SupportScreen_Previews: PreviewProvider {
    static var previews: some View {
        SupportScreen()
    }
}



