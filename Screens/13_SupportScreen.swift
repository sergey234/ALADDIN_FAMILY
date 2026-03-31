import SwiftUI

struct UnifiedFAQItem: Identifiable {
    let id: String
    let icon: String
    let question: String
    let answer: String
}

private struct UnifiedFAQEntry {
    let id: String
    let icon: String
    let questionKey: String
    let answerKey: String
    let keywords: [String]
}

enum UnifiedFAQCatalog {
    private static let entries: [UnifiedFAQEntry] = [
        UnifiedFAQEntry(id: "faq_what_protects", icon: "🛡️", questionKey: "faq_what_protects", answerKey: "faq_what_protects_answer", keywords: ["защищает", "система", "что умеет"]),
        UnifiedFAQEntry(id: "faq_protect_children", icon: "👶", questionKey: "faq_protect_children", answerKey: "faq_protect_children_answer", keywords: ["детей", "ребенка", "родительский"]),
        UnifiedFAQEntry(id: "faq_protect_elderly", icon: "👴", questionKey: "faq_protect_elderly", answerKey: "faq_protect_elderly_answer", keywords: ["пожилых", "бабуш", "дедуш"]),
        UnifiedFAQEntry(id: "faq_data_safe", icon: "🔐", questionKey: "faq_data_safe", answerKey: "faq_data_safe_answer", keywords: ["данные", "безопасны", "шифрование"]),
        UnifiedFAQEntry(id: "faq_viruses_trojans", icon: "🦠", questionKey: "faq_viruses_trojans", answerKey: "faq_viruses_trojans_answer", keywords: ["вирус", "троян"]),
        UnifiedFAQEntry(id: "faq_ransomware", icon: "🔒", questionKey: "faq_ransomware", answerKey: "faq_ransomware_answer", keywords: ["шифровальщик", "ransomware"]),
        UnifiedFAQEntry(id: "faq_spyware", icon: "🕵️", questionKey: "faq_spyware", answerKey: "faq_spyware_answer", keywords: ["шпион", "spyware"]),
        UnifiedFAQEntry(id: "faq_phishing_sites", icon: "🌐", questionKey: "faq_phishing_sites", answerKey: "faq_phishing_sites_answer", keywords: ["фишинг", "поддельный сайт"]),
        UnifiedFAQEntry(id: "faq_fake_apps", icon: "📱", questionKey: "faq_fake_apps", answerKey: "faq_fake_apps_answer", keywords: ["поддельные приложения"]),
        UnifiedFAQEntry(id: "faq_malicious_links", icon: "🔗", questionKey: "faq_malicious_links", answerKey: "faq_malicious_links_answer", keywords: ["ссылка", "вредонос"]),
        UnifiedFAQEntry(id: "faq_phone_scam", icon: "📞", questionKey: "faq_phone_scam", answerKey: "faq_phone_scam_answer", keywords: ["телефон", "мошенник", "звонок"]),
        UnifiedFAQEntry(id: "faq_financial_scam", icon: "💳", questionKey: "faq_financial_scam", answerKey: "faq_financial_scam_answer", keywords: ["деньги", "финансов", "карта"]),
        UnifiedFAQEntry(id: "faq_social_engineering", icon: "🎭", questionKey: "faq_social_engineering", answerKey: "faq_social_engineering_answer", keywords: ["социальная инженерия", "обман"]),
        UnifiedFAQEntry(id: "faq_fake_banks", icon: "🏦", questionKey: "faq_fake_banks", answerKey: "faq_fake_banks_answer", keywords: ["банк", "поддельный банк"]),
        UnifiedFAQEntry(id: "faq_phishing_emails", icon: "📧", questionKey: "faq_phishing_emails", answerKey: "faq_phishing_emails_answer", keywords: ["email", "почта", "письмо"]),
        UnifiedFAQEntry(id: "faq_inappropriate_content", icon: "🚫", questionKey: "faq_inappropriate_content", answerKey: "faq_inappropriate_content_answer", keywords: ["неподходящий контент", "детям нельзя"]),
        UnifiedFAQEntry(id: "faq_cyberbullying", icon: "😢", questionKey: "faq_cyberbullying", answerKey: "faq_cyberbullying_answer", keywords: ["кибербуллинг", "травля"]),
        UnifiedFAQEntry(id: "faq_dangerous_contacts", icon: "👥", questionKey: "faq_dangerous_contacts", answerKey: "faq_dangerous_contacts_answer", keywords: ["опасные контакты", "незнакомцы"]),
        UnifiedFAQEntry(id: "faq_gaming_addiction", icon: "🎮", questionKey: "faq_gaming_addiction", answerKey: "faq_gaming_addiction_answer", keywords: ["игровая зависимость", "играет много"]),
        UnifiedFAQEntry(id: "faq_accidental_purchases", icon: "💸", questionKey: "faq_accidental_purchases", answerKey: "faq_accidental_purchases_answer", keywords: ["случайные покупки"]),
        UnifiedFAQEntry(id: "faq_password_theft", icon: "🔑", questionKey: "faq_password_theft", answerKey: "faq_password_theft_answer", keywords: ["пароль", "кража пароля"]),
        UnifiedFAQEntry(id: "faq_privacy_violation", icon: "👁️", questionKey: "faq_privacy_violation", answerKey: "faq_privacy_violation_answer", keywords: ["приватность", "нарушение"]),
        UnifiedFAQEntry(id: "faq_deepfake", icon: "🎬", questionKey: "faq_deepfake", answerKey: "faq_deepfake_answer", keywords: ["дипфейк", "deepfake"]),
        UnifiedFAQEntry(id: "faq_fake_voices", icon: "🎤", questionKey: "faq_fake_voices", answerKey: "faq_fake_voices_answer", keywords: ["поддельный голос"]),
        UnifiedFAQEntry(id: "faq_fake_news", icon: "📰", questionKey: "faq_fake_news", answerKey: "faq_fake_news_answer", keywords: ["фейк", "фейковые новости"]),
        UnifiedFAQEntry(id: "faq_dangerous_sites", icon: "⚠️", questionKey: "faq_dangerous_sites", answerKey: "faq_dangerous_sites_answer", keywords: ["опасный сайт"]),
        UnifiedFAQEntry(id: "faq_suspicious_downloads", icon: "📥", questionKey: "faq_suspicious_downloads", answerKey: "faq_suspicious_downloads_answer", keywords: ["скачивание", "подозрительная загрузка"]),
        UnifiedFAQEntry(id: "faq_unsafe_wifi", icon: "📡", questionKey: "faq_unsafe_wifi", answerKey: "faq_unsafe_wifi_answer", keywords: ["wi-fi", "wifi", "публичная сеть"]),
        UnifiedFAQEntry(id: "faq_mitm_attacks", icon: "🕵️", questionKey: "faq_mitm_attacks", answerKey: "faq_mitm_attacks_answer", keywords: ["mitm", "человек посередине"]),
        UnifiedFAQEntry(id: "faq_parental_control_setup", icon: "👨‍👩‍👧‍👦", questionKey: "faq_parental_control_setup", answerKey: "faq_parental_control_setup_answer", keywords: ["настроить семью", "родительский контроль"]),
        UnifiedFAQEntry(id: "faq_cancel_subscription", icon: "💳", questionKey: "faq_cancel_subscription", answerKey: "faq_cancel_subscription_answer", keywords: ["подписка", "отменить подписку"])
    ]

    static func localizedItems(localize: (String) -> String) -> [UnifiedFAQItem] {
        entries.map { entry in
            UnifiedFAQItem(
                id: entry.id,
                icon: entry.icon,
                question: localize(entry.questionKey),
                answer: localize(entry.answerKey)
            )
        }
    }

    static func bestMatch(for query: String, localize: (String) -> String) -> UnifiedFAQItem? {
        let normalizedQuery = query.lowercased()
        guard !normalizedQuery.isEmpty else { return nil }

        var bestScore = 0
        var bestEntry: UnifiedFAQEntry?

        for entry in entries {
            var score = 0
            for keyword in entry.keywords where normalizedQuery.contains(keyword) {
                score += 3
            }
            let localizedQuestion = localize(entry.questionKey).lowercased()
            if localizedQuestion.contains(normalizedQuery) || normalizedQuery.contains(localizedQuestion) {
                score += 2
            }
            if score > bestScore {
                bestScore = score
                bestEntry = entry
            }
        }

        guard let entry = bestEntry, bestScore >= 3 else { return nil }
        return UnifiedFAQItem(
            id: entry.id,
            icon: entry.icon,
            question: localize(entry.questionKey),
            answer: localize(entry.answerKey)
        )
    }
}

/// 💬 Support Screen
/// Экран поддержки - помощь и FAQ
/// Источник дизайна: комбинация из разных wireframes
struct SupportScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var searchText: String = ""
    
    // ✅ ЗАДАЧА 26: Roadside Assistance
    @State private var showRoadsideAssistance: Bool = false
    private let apiService = APIService.shared
    
    struct FAQItem: Identifiable {
        let id: String
        let icon: String
        let question: String
        let answer: String
        var isExpanded: Bool = false
    }
    
    // ✅ ИСПРАВЛЕНИЕ: Используем @State массив как в бэкапе для правильной работы раскрывающихся секций
    @State private var faqItems: [FAQItem] = []
    
    // Инициализация FAQ при появлении экрана
    private func initializeFAQItems() {
        let expandedIds = Set(faqItems.filter(\.isExpanded).map(\.id))
        faqItems = UnifiedFAQCatalog.localizedItems(localize: localizationManager.localized).map { item in
            FAQItem(
                id: item.id,
                icon: item.icon,
                question: item.question,
                answer: item.answer,
                isExpanded: expandedIds.contains(item.id)
            )
        }
    }

    private var filteredFAQIndices: [Int] {
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !query.isEmpty else { return Array(faqItems.indices) }
        return faqItems.indices.filter { idx in
            faqItems[idx].question.lowercased().contains(query) ||
            faqItems[idx].answer.lowercased().contains(query)
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
                        
                        // ✅ ЗАДАЧА 26: Помощь на дороге
                        roadsideAssistanceSection
                        
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
                .accessibilityLabel(localizationManager.localized("support_search_icon"))
            
            TextField(localizationManager.localized("support_search_placeholder"), text: $searchText)
                .textFieldStyle(PlainTextFieldStyle())
                .accessibilityLabel(localizationManager.localized("support_search_field"))
                .accessibilityHint(localizationManager.localized("support_search_hint"))
        }
        .padding()
        .background(Color.gray.opacity(0.3))
        .cornerRadius(8)
        .padding(.horizontal, 20)
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("support_search_label"))
    }
    
    // MARK: - Contact Methods
    
    private var contactMethods: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("support_contact_us"))
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel(localizationManager.localized("support_contact_us_label"))
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
        .accessibilityLabel(localizationManager.localized("support_contact_methods"))
    }
    
    private func contactButton(icon: String, title: String, subtitle: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Text(icon)
                    .font(.system(size: 32))
                    .accessibilityLabel(String(format: localizationManager.localized("support_icon_label"), title))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.body.bold())
                        .foregroundColor(.primary)
                        .accessibilityLabel(String(format: localizationManager.localized("support_title_label"), title))
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .accessibilityLabel(String(format: localizationManager.localized("support_subtitle_label"), subtitle))
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(title): \(subtitle)")
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(color)
                    .accessibilityLabel(localizationManager.localized("support_go"))
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
        .accessibilityHint(String(format: localizationManager.localized("support_tap_hint"), title.lowercased()))
    }
    
    private func openSupportURL(_ urlString: String) {
        guard let url = URL(string: urlString) else { return }
        UIApplication.shared.open(url)
    }
    
    // MARK: - Roadside Assistance Section (✅ ЗАДАЧА 26)
    
    private var roadsideAssistanceSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("roadside_assistance_title"))
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel(localizationManager.localized("roadside_assistance_title"))
                .accessibilityAddTraits(.isHeader)
            
            Button(action: {
                VisualLogger.shared.log(
                    "🆘 Roadside Assistance tapped",
                    level: .info,
                    category: "SUPPORT.UI"
                )
                showRoadsideAssistance = true
            }) {
                HStack(spacing: 12) {
                    Image(systemName: "car.fill")
                        .font(.system(size: 32))
                        .foregroundColor(.red)
                        .accessibilityLabel(localizationManager.localized("roadside_assistance_icon"))
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("roadside_call_help"))
                            .font(.body.bold())
                            .foregroundColor(.primary)
                            .accessibilityLabel(localizationManager.localized("roadside_call_help"))
                        
                        Text(localizationManager.localized("roadside_assistance_subtitle"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .accessibilityLabel(localizationManager.localized("roadside_assistance_subtitle"))
                    }
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .foregroundColor(.red)
                }
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.3))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.red.opacity(0.3), lineWidth: 1)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
            .cardShadow()
            .padding(.horizontal, 20)
        }
        .sheet(isPresented: $showRoadsideAssistance) {
            // Минимальный экран вместо пустого листа
            VStack(spacing: 12) {
                Text(localizationManager.localized("roadside_assistance_title"))
                    .font(.title2)
                Text(localizationManager.localized("roadside_assistance_subtitle"))
                    .font(.caption)
                    .foregroundColor(.secondary)
                Button {
                    VisualLogger.shared.log(
                        "📞 Roadside Assistance: Call requested",
                        level: .info,
                        category: "SUPPORT.UI"
                    )
                    if let url = URL(string: "tel://112") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Text(localizationManager.localized("roadside_assistance_call"))
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 10)
                        .background(Color.red)
                        .cornerRadius(8)
                }
                Button {
                    VisualLogger.shared.log(
                        "🧰 Roadside Assistance: Close",
                        level: .info,
                        category: "SUPPORT.UI"
                    )
                    showRoadsideAssistance = false
                } label: {
                    Text(localizationManager.localized("common_close"))
                        .foregroundColor(.primaryBlue)
                }
            }
            .padding()
                .environmentObject(localizationManager)
        }
    }
    
    // MARK: - FAQ Section
    
    private var faqSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("support_faq"))
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityLabel(localizationManager.localized("support_faq_label"))
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: 8) {
                ForEach(filteredFAQIndices, id: \.self) { idx in
                    faqCard(item: $faqItems[idx])
                }
            }
            .padding(.horizontal, 20)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localizationManager.localized("support_faq_section"))
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
                        .accessibilityLabel(localizationManager.localized("support_question_icon"))
                    
                    Text(item.wrappedValue.question)
                        .font(.body.bold())
                        .foregroundColor(.primary)
                        .accessibilityLabel(String(format: localizationManager.localized("support_question_label"), item.wrappedValue.question))
                    
                    Spacer()
                    
                    Image(systemName: item.wrappedValue.isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.blue)
                        .accessibilityLabel(item.wrappedValue.isExpanded ? localizationManager.localized("support_collapse") : localizationManager.localized("support_expand"))
                }
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel(item.wrappedValue.isExpanded ? String(format: localizationManager.localized("support_collapse_label"), item.wrappedValue.question) : String(format: localizationManager.localized("support_expand_label"), item.wrappedValue.question))
            .accessibilityHint(item.wrappedValue.isExpanded ? localizationManager.localized("support_collapse_hint") : localizationManager.localized("support_expand_hint"))
            
            // Ответ (раскрывается)
            if item.wrappedValue.isExpanded {
                Text(item.wrappedValue.answer)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .padding(.leading, 36)
                    .transition(.opacity)
                    .accessibilityLabel(String(format: localizationManager.localized("support_answer_label"), item.wrappedValue.answer))
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.3))
        )
        .cardShadow()
        .accessibilityElement(children: .contain)
        .accessibilityLabel(String(format: localizationManager.localized("support_faq_item"), item.wrappedValue.question))
    }
}

// MARK: - Preview

struct SupportScreen_Previews: PreviewProvider {
    static var previews: some View {
        SupportScreen()
    }
}



