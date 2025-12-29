import SwiftUI

/// 💬 Support Screen
/// Экран поддержки - помощь и FAQ
/// Источник дизайна: комбинация из разных wireframes
struct SupportScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var searchText: String = ""
    
    struct FAQItem: Identifiable {
        let id = UUID()
        let icon: String
        let question: String
        let answer: String
        var isExpanded: Bool = false
    }
    
    // ✅ ИСПРАВЛЕНИЕ: Используем @State массив как в бэкапе для правильной работы раскрывающихся секций
    @State private var faqItems: [FAQItem] = []
    
    // Инициализация FAQ при появлении экрана
    private func initializeFAQItems() {
        if faqItems.isEmpty {
            faqItems = [
        // ==========================================
        // 📋 ОБЩИЕ ВОПРОСЫ
        // ==========================================
        
        FAQItem(icon: "🛡️", question: localizationManager.localized("faq_what_protects"), answer: localizationManager.localized("faq_what_protects_answer")),
        
        FAQItem(icon: "👶", question: localizationManager.localized("faq_protect_children"), answer: localizationManager.localized("faq_protect_children_answer")),
        
        FAQItem(icon: "👴", question: localizationManager.localized("faq_protect_elderly"), answer: localizationManager.localized("faq_protect_elderly_answer")),
        
        FAQItem(icon: "🔐", question: localizationManager.localized("faq_data_safe"), answer: localizationManager.localized("faq_data_safe_answer")),
        
        // ==========================================
        // 🛡️ КИБЕРУГРОЗЫ (6 вопросов)
        // ==========================================
        
        FAQItem(icon: "🦠", question: localizationManager.localized("faq_viruses_trojans"), answer: localizationManager.localized("faq_viruses_trojans_answer")),
        
        FAQItem(icon: "🔒", question: localizationManager.localized("faq_ransomware"), answer: localizationManager.localized("faq_ransomware_answer")),
        
        FAQItem(icon: "🕵️", question: localizationManager.localized("faq_spyware"), answer: localizationManager.localized("faq_spyware_answer")),
        
        FAQItem(icon: "🌐", question: localizationManager.localized("faq_phishing_sites"), answer: localizationManager.localized("faq_phishing_sites_answer")),
        
        FAQItem(icon: "📱", question: localizationManager.localized("faq_fake_apps"), answer: localizationManager.localized("faq_fake_apps_answer")),
        
        FAQItem(icon: "🔗", question: localizationManager.localized("faq_malicious_links"), answer: localizationManager.localized("faq_malicious_links_answer")),
        
        // ==========================================
        // 💰 МОШЕННИЧЕСТВО (5 вопросов)
        // ==========================================
        
        FAQItem(icon: "📞", question: localizationManager.localized("faq_phone_scam"), answer: localizationManager.localized("faq_phone_scam_answer")),
        
        FAQItem(icon: "💳", question: localizationManager.localized("faq_financial_scam"), answer: localizationManager.localized("faq_financial_scam_answer")),
        
        FAQItem(icon: "🎭", question: localizationManager.localized("faq_social_engineering"), answer: localizationManager.localized("faq_social_engineering_answer")),
        
        FAQItem(icon: "🏦", question: localizationManager.localized("faq_fake_banks"), answer: localizationManager.localized("faq_fake_banks_answer")),
        
        FAQItem(icon: "📧", question: localizationManager.localized("faq_phishing_emails"), answer: localizationManager.localized("faq_phishing_emails_answer")),
        
        // ==========================================
        // 👶 ДЕТСКИЕ УГРОЗЫ (5 вопросов)
        // ==========================================
        
        FAQItem(icon: "🚫", question: localizationManager.localized("faq_inappropriate_content"), answer: localizationManager.localized("faq_inappropriate_content_answer")),
        
        FAQItem(icon: "😢", question: localizationManager.localized("faq_cyberbullying"), answer: localizationManager.localized("faq_cyberbullying_answer")),
        
        FAQItem(icon: "👥", question: localizationManager.localized("faq_dangerous_contacts"), answer: localizationManager.localized("faq_dangerous_contacts_answer")),
        
        FAQItem(icon: "🎮", question: localizationManager.localized("faq_gaming_addiction"), answer: localizationManager.localized("faq_gaming_addiction_answer")),
        
        FAQItem(icon: "💸", question: localizationManager.localized("faq_accidental_purchases"), answer: localizationManager.localized("faq_accidental_purchases_answer")),
        
        // ==========================================
        // 🔒 УТЕЧКИ ДАННЫХ (2 вопроса)
        // ==========================================
        
        FAQItem(icon: "🔑", question: localizationManager.localized("faq_password_theft"), answer: localizationManager.localized("faq_password_theft_answer")),
        
        FAQItem(icon: "👁️", question: localizationManager.localized("faq_privacy_violation"), answer: localizationManager.localized("faq_privacy_violation_answer")),
        
        // ==========================================
        // 🎭 ПОДДЕЛКИ (3 вопроса)
        // ==========================================
        
        FAQItem(icon: "🎬", question: localizationManager.localized("faq_deepfake"), answer: localizationManager.localized("faq_deepfake_answer")),
        
        FAQItem(icon: "🎤", question: localizationManager.localized("faq_fake_voices"), answer: localizationManager.localized("faq_fake_voices_answer")),
        
        FAQItem(icon: "📰", question: localizationManager.localized("faq_fake_news"), answer: localizationManager.localized("faq_fake_news_answer")),
        
        // ==========================================
        // 🌐 ИНТЕРНЕТ-УГРОЗЫ (4 вопроса)
        // ==========================================
        
        FAQItem(icon: "⚠️", question: localizationManager.localized("faq_dangerous_sites"), answer: localizationManager.localized("faq_dangerous_sites_answer")),
        
        FAQItem(icon: "📥", question: localizationManager.localized("faq_suspicious_downloads"), answer: localizationManager.localized("faq_suspicious_downloads_answer")),
        
        FAQItem(icon: "📡", question: localizationManager.localized("faq_unsafe_wifi"), answer: localizationManager.localized("faq_unsafe_wifi_answer")),
        
        FAQItem(icon: "🕵️", question: localizationManager.localized("faq_mitm_attacks"), answer: localizationManager.localized("faq_mitm_attacks_answer")),
        
        // ==========================================
        // 📱 МОБИЛЬНЫЕ УГРОЗЫ (3 вопроса)
        // ==========================================
        
        FAQItem(icon: "📱", question: localizationManager.localized("faq_malicious_apps"), answer: localizationManager.localized("faq_malicious_apps_answer")),
        
        FAQItem(icon: "💬", question: localizationManager.localized("faq_sms_scam"), answer: localizationManager.localized("faq_sms_scam_answer")),
        
        FAQItem(icon: "📍", question: localizationManager.localized("faq_location_threats"), answer: localizationManager.localized("faq_location_threats_answer")),
        
        // ==========================================
        // 🏠 СЕМЕЙНЫЕ УГРОЗЫ (2 вопроса)
        // ==========================================
        
        FAQItem(icon: "💔", question: localizationManager.localized("faq_domestic_violence"), answer: localizationManager.localized("faq_domestic_violence_answer")),
        
        FAQItem(icon: "😟", question: localizationManager.localized("faq_emotional_problems"), answer: localizationManager.localized("faq_emotional_problems_answer")),
        
        // ==========================================
        // 🔐 ВОЕННАЯ ЗАЩИТА (3 вопроса)
        // ==========================================
        
        FAQItem(icon: "🔐", question: localizationManager.localized("faq_aes256"), answer: localizationManager.localized("faq_aes256_answer")),
        
        FAQItem(icon: "👻", question: localizationManager.localized("faq_anonymity"), answer: localizationManager.localized("faq_anonymity_answer")),
        
        FAQItem(icon: "🏛️", question: localizationManager.localized("faq_critical_infrastructure"), answer: localizationManager.localized("faq_critical_infrastructure_answer")),
        
        // ==========================================
        // 💻 ТЕХНИЧЕСКИЕ ВОПРОСЫ (3 вопроса)
        // ==========================================
        
        FAQItem(icon: "💻", question: localizationManager.localized("faq_how_network_protection_works"), answer: localizationManager.localized("faq_how_network_protection_works_answer")),
        
        FAQItem(icon: "👨‍👩‍👧‍👦", question: localizationManager.localized("faq_parental_control_setup"), answer: localizationManager.localized("faq_parental_control_setup_answer")),
        
        FAQItem(icon: "💳", question: localizationManager.localized("faq_cancel_subscription"), answer: localizationManager.localized("faq_cancel_subscription_answer"))
            ]
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel(localizationManager.localized("support_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: {
                        // ✅ ИСПРАВЛЕНИЕ: Просто dismiss() - возвращаемся к Settings
                        // SupportScreen открывается как .sheet() из SettingsScreen,
                        // поэтому dismiss() вернет нас обратно на Settings
                        dismiss()
                    }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel(localizationManager.localized("support_back"))
                    .accessibilityHint(localizationManager.localized("support_back_hint"))
                    
                    Spacer()
                    
                    VStack {
                        Text(localizationManager.localized("support_title"))
                            .font(.headline)
                            .foregroundColor(.white)
                            .accessibilityLabel(localizationManager.localized("support_title"))
                            .accessibilityAddTraits(.isHeader)
                        
                        Text(localizationManager.localized("support_subtitle"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .accessibilityLabel(localizationManager.localized("support_subtitle"))
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(localizationManager.localized("support_header"))
                    
                    Spacer()
                    
                    Color.clear
                        .frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                .accessibilityElement(children: .combine)
                .accessibilityLabel(localizationManager.localized("support_nav_panel"))
                
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
                .accessibilityLabel(localizationManager.localized("support_content"))
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: 12)
        }
        .task {
            print("🚨 SupportScreen загружен!")
            initializeFAQItems()
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("support_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: localizationManager.currentLanguage) { _ in
            // Переинициализируем FAQ при смене языка
            initializeFAQItems()
        }
    }
    
    // MARK: - Search Bar
    
    private var searchBar: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
                .accessibilityLabel("Поиск")
            
            TextField(localizationManager.localized("support_search_placeholder"), text: $searchText)
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
            Text(localizationManager.localized("support_contact_us"))
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel("СВЯЗАТЬСЯ С НАМИ")
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 8) {
                contactButton(
                    icon: "💬",
                    title: localizationManager.localized("support_chat"),
                    subtitle: localizationManager.localized("support_chat_subtitle"),
                    color: .blue
                ) {
                    openSupportURL(AppConfig.supportTelegramURL)
                }
                
                contactButton(
                    icon: "📝",
                    title: localizationManager.localized("support_ai_assistant"),
                    subtitle: localizationManager.localized("support_ai_assistant_subtitle"),
                    color: .green
                ) {
                    openSupportURL(AppConfig.supportHelpCenterURL)
                }
                
                contactButton(
                    icon: "📚",
                    title: localizationManager.localized("support_phone"),
                    subtitle: localizationManager.localized("support_phone_subtitle"),
                    color: .orange
                ) {
                    openSupportURL(AppConfig.supportFAQURL)
                }
            }
            .padding(.horizontal, 20)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Способы связи с поддержкой")
    }
    
    private func contactButton(icon: String, title: String, subtitle: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
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
    
    private func openSupportURL(_ urlString: String) {
        guard let url = URL(string: urlString) else { return }
        UIApplication.shared.open(url)
    }
    
    // MARK: - FAQ Section
    
    private var faqSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("support_faq"))
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



