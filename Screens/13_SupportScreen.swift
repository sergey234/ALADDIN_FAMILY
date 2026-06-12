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
        UnifiedFAQEntry(id: "faq_aes256", icon: "🔐", questionKey: "faq_aes256", answerKey: "faq_aes256_answer", keywords: ["aes", "шифрование", "военное"]),
        UnifiedFAQEntry(id: "faq_viruses_trojans", icon: "🦠", questionKey: "faq_viruses_trojans", answerKey: "faq_viruses_trojans_answer", keywords: ["вирус", "троян"]),
        UnifiedFAQEntry(id: "faq_ransomware", icon: "🔒", questionKey: "faq_ransomware", answerKey: "faq_ransomware_answer", keywords: ["шифровальщик", "ransomware"]),
        UnifiedFAQEntry(id: "faq_spyware", icon: "🕵️", questionKey: "faq_spyware", answerKey: "faq_spyware_answer", keywords: ["шпион", "spyware"]),
        UnifiedFAQEntry(id: "faq_phishing_sites", icon: "🌐", questionKey: "faq_phishing_sites", answerKey: "faq_phishing_sites_answer", keywords: ["фишинг", "поддельный сайт"]),
        UnifiedFAQEntry(id: "faq_fake_apps", icon: "📱", questionKey: "faq_fake_apps", answerKey: "faq_fake_apps_answer", keywords: ["поддельные приложения"]),
        UnifiedFAQEntry(id: "faq_malicious_apps", icon: "📲", questionKey: "faq_malicious_apps", answerKey: "faq_malicious_apps_answer", keywords: ["вредоносные приложения", "malware app"]),
        UnifiedFAQEntry(id: "faq_malicious_links", icon: "🔗", questionKey: "faq_malicious_links", answerKey: "faq_malicious_links_answer", keywords: ["ссылка", "вредонос"]),
        UnifiedFAQEntry(id: "faq_phone_scam", icon: "📞", questionKey: "faq_phone_scam", answerKey: "faq_phone_scam_answer", keywords: ["телефон", "мошенник", "звонок"]),
        UnifiedFAQEntry(id: "faq_financial_scam", icon: "💳", questionKey: "faq_financial_scam", answerKey: "faq_financial_scam_answer", keywords: ["деньги", "финансов", "карта"]),
        UnifiedFAQEntry(id: "faq_social_engineering", icon: "🎭", questionKey: "faq_social_engineering", answerKey: "faq_social_engineering_answer", keywords: ["социальная инженерия", "обман"]),
        UnifiedFAQEntry(id: "faq_fake_banks", icon: "🏦", questionKey: "faq_fake_banks", answerKey: "faq_fake_banks_answer", keywords: ["банк", "поддельный банк"]),
        UnifiedFAQEntry(id: "faq_phishing_emails", icon: "📧", questionKey: "faq_phishing_emails", answerKey: "faq_phishing_emails_answer", keywords: ["email", "почта", "письмо"]),
        UnifiedFAQEntry(id: "faq_sms_scam", icon: "💬", questionKey: "faq_sms_scam", answerKey: "faq_sms_scam_answer", keywords: ["sms", "смс", "smishing"]),
        UnifiedFAQEntry(id: "faq_inappropriate_content", icon: "🚫", questionKey: "faq_inappropriate_content", answerKey: "faq_inappropriate_content_answer", keywords: ["неподходящий контент", "детям нельзя"]),
        UnifiedFAQEntry(id: "faq_cyberbullying", icon: "😢", questionKey: "faq_cyberbullying", answerKey: "faq_cyberbullying_answer", keywords: ["кибербуллинг", "травля"]),
        UnifiedFAQEntry(id: "faq_dangerous_contacts", icon: "👥", questionKey: "faq_dangerous_contacts", answerKey: "faq_dangerous_contacts_answer", keywords: ["опасные контакты", "незнакомцы"]),
        UnifiedFAQEntry(id: "faq_gaming_addiction", icon: "🎮", questionKey: "faq_gaming_addiction", answerKey: "faq_gaming_addiction_answer", keywords: ["игровая зависимость", "играет много"]),
        UnifiedFAQEntry(id: "faq_accidental_purchases", icon: "💸", questionKey: "faq_accidental_purchases", answerKey: "faq_accidental_purchases_answer", keywords: ["случайные покупки"]),
        UnifiedFAQEntry(id: "faq_password_theft", icon: "🔑", questionKey: "faq_password_theft", answerKey: "faq_password_theft_answer", keywords: ["пароль", "кража пароля"]),
        UnifiedFAQEntry(id: "faq_privacy_violation", icon: "👁️", questionKey: "faq_privacy_violation", answerKey: "faq_privacy_violation_answer", keywords: ["приватность", "нарушение"]),
        UnifiedFAQEntry(id: "faq_location_threats", icon: "📍", questionKey: "faq_location_threats", answerKey: "faq_location_threats_answer", keywords: ["геолокация", "местоположение"]),
        UnifiedFAQEntry(id: "faq_dark_web_leaks", icon: "🕸️", questionKey: "faq_dark_web_leaks", answerKey: "faq_dark_web_leaks_answer", keywords: ["темная сеть", "dark web", "утечка"]),
        UnifiedFAQEntry(id: "faq_deepfake", icon: "🎬", questionKey: "faq_deepfake", answerKey: "faq_deepfake_answer", keywords: ["дипфейк", "deepfake"]),
        UnifiedFAQEntry(id: "faq_fake_voices", icon: "🎤", questionKey: "faq_fake_voices", answerKey: "faq_fake_voices_answer", keywords: ["поддельный голос"]),
        UnifiedFAQEntry(id: "faq_fake_news", icon: "📰", questionKey: "faq_fake_news", answerKey: "faq_fake_news_answer", keywords: ["фейк", "фейковые новости"]),
        UnifiedFAQEntry(id: "faq_dangerous_sites", icon: "⚠️", questionKey: "faq_dangerous_sites", answerKey: "faq_dangerous_sites_answer", keywords: ["опасный сайт"]),
        UnifiedFAQEntry(id: "faq_suspicious_downloads", icon: "📥", questionKey: "faq_suspicious_downloads", answerKey: "faq_suspicious_downloads_answer", keywords: ["скачивание", "подозрительная загрузка"]),
        UnifiedFAQEntry(id: "faq_unsafe_wifi", icon: "📡", questionKey: "faq_unsafe_wifi", answerKey: "faq_unsafe_wifi_answer", keywords: ["wi-fi", "wifi", "публичная сеть"]),
        UnifiedFAQEntry(id: "faq_how_network_protection_works", icon: "🛡️", questionKey: "faq_how_network_protection_works", answerKey: "faq_how_network_protection_works_answer", keywords: ["защита сети", "vpn", "туннель"]),
        UnifiedFAQEntry(id: "faq_mitm_attacks", icon: "🕵️", questionKey: "faq_mitm_attacks", answerKey: "faq_mitm_attacks_answer", keywords: ["mitm", "человек посередине"]),
        UnifiedFAQEntry(id: "faq_crash_detection", icon: "🚗", questionKey: "faq_crash_detection", answerKey: "faq_crash_detection_answer", keywords: ["авария", "дтп", "crash"]),
        UnifiedFAQEntry(id: "faq_roadside_assistance", icon: "🛣️", questionKey: "faq_roadside_assistance", answerKey: "faq_roadside_assistance_answer", keywords: ["дорога", "поломка", "roadside"]),
        UnifiedFAQEntry(id: "faq_emergency_sos", icon: "🆘", questionKey: "faq_emergency_sos", answerKey: "faq_emergency_sos_answer", keywords: ["sos", "экстренно", "60+"]),
        UnifiedFAQEntry(id: "faq_parental_control_setup", icon: "👨‍👩‍👧‍👦", questionKey: "faq_parental_control_setup", answerKey: "faq_parental_control_setup_answer", keywords: ["настроить семью", "родительский контроль"]),
        UnifiedFAQEntry(id: "faq_parental_bypass", icon: "🛡️", questionKey: "faq_parental_bypass", answerKey: "faq_parental_bypass_answer", keywords: ["обход", "bypass", "инкогнито", "tor"]),
        UnifiedFAQEntry(id: "faq_geofencing", icon: "🗺️", questionKey: "faq_geofencing", answerKey: "faq_geofencing_answer", keywords: ["геозона", "геозоны", "geofence", "местоположение"]),
        UnifiedFAQEntry(id: "faq_wellness_support", icon: "💚", questionKey: "faq_wellness_support", answerKey: "faq_wellness_support_answer", keywords: ["wellness", "настроение", "эмоциональная поддержка", "самопомощь"]),
        UnifiedFAQEntry(id: "faq_cancel_subscription", icon: "💳", questionKey: "faq_cancel_subscription", answerKey: "faq_cancel_subscription_answer", keywords: ["подписка", "отменить подписку"]),
        UnifiedFAQEntry(id: "faq_ai_how_works", icon: "🤖", questionKey: "faq_ai_how_works", answerKey: "faq_ai_how_works_answer", keywords: ["учишь", "обуча", "обучен", "как работает ai", "что умеешь", "что можешь", "кто ты", "ты кто", "нейросет", "искусственный интеллект", "ai aladdin"])
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
    @State private var debouncedSearchText: String = ""
    @State private var faqVisibleCount: Int = 10
    @State private var searchDebounceTask: Task<Void, Never>?
    
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
        let query = debouncedSearchText.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !query.isEmpty else { return Array(faqItems.indices) }
        return faqItems.indices.filter { idx in
            faqItems[idx].question.lowercased().contains(query) ||
            faqItems[idx].answer.lowercased().contains(query)
        }
    }

    private var displayedFAQIndices: [Int] {
        let filtered = filteredFAQIndices
        let isSearching = !debouncedSearchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        if isSearching { return filtered }
        return Array(filtered.prefix(faqVisibleCount))
    }

    private var hasMoreFAQ: Bool {
        debouncedSearchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        filteredFAQIndices.count > faqVisibleCount
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh hub light (Batch 3, режим A)
            StormMeshBackground(variant: .hub)
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

                        antifakeShareHelpSection
                        
                        // ✅ ЗАДАЧА 26: Помощь на дороге
                        roadsideAssistanceSection
                        
                        telegramAboveFAQ
                        
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
            initializeFAQItems()
        }
        .onAppear {
            SupportScreenPerformanceGuard.setVisible(true)
        }
        .onDisappear {
            SupportScreenPerformanceGuard.setVisible(false)
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("support_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: localizationManager.currentLanguage) { _ in
            // Переинициализируем FAQ при смене языка
            initializeFAQItems()
        }
        .onChange(of: searchText) { newValue in
            searchDebounceTask?.cancel()
            searchDebounceTask = Task {
                try? await Task.sleep(nanoseconds: 300_000_000)
                guard !Task.isCancelled else { return }
                await MainActor.run {
                    debouncedSearchText = newValue
                    faqVisibleCount = 10
                }
            }
        }
        .safeAreaInset(edge: .bottom, spacing: 0) {
            telegramStickyBar
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
        .background(Color(.secondarySystemBackground).opacity(0.92))
        .cornerRadius(8)
        .padding(.horizontal, 20)
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
                    systemIcon: "paperplane.fill",
                    title: localizationManager.localized("support_telegram_write"),
                    subtitle: localizationManager.localized("support_telegram_subtitle"),
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
    
    private func contactButton(
        icon: String? = nil,
        systemIcon: String? = nil,
        title: String,
        subtitle: String,
        color: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Group {
                    if let systemIcon {
                        Image(systemName: systemIcon)
                            .font(.system(size: 28, weight: .semibold))
                            .foregroundColor(color)
                    } else {
                        Text(icon ?? "💬")
                            .font(.system(size: 32))
                    }
                }
                .frame(width: 36, height: 36)
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
            .background(Color(.secondarySystemBackground).opacity(0.92))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(color.opacity(0.3), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityLabel("\(title): \(subtitle)")
        .accessibilityHint(String(format: localizationManager.localized("support_tap_hint"), title.lowercased()))
    }
    
    private func openSupportURL(_ urlString: String) {
        guard let url = URL(string: urlString) else { return }
        UIApplication.shared.open(url)
    }

    // MARK: - Antifake Share (ux-1-09)

    private var antifakeShareHelpSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("support_antifake_share_title"))
                .font(.title2)
                .foregroundColor(.primary)
                .padding(.horizontal, 20)
                .accessibilityAddTraits(.isHeader)

            VStack(alignment: .leading, spacing: 12) {
                Text(localizationManager.localized("support_antifake_share_subtitle"))
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                antifakeShareStep(number: 1, textKey: "support_antifake_share_step1")
                antifakeShareStep(number: 2, textKey: "support_antifake_share_step2")
                antifakeShareStep(number: 3, textKey: "support_antifake_share_step3")
                antifakeShareStep(number: 4, textKey: "support_antifake_share_step4")

                Text(localizationManager.localized("support_antifake_share_note"))
                    .font(.caption)
                    .foregroundColor(.secondary)

                Button {
                    openAntifakeHubFromSupport()
                } label: {
                    HStack {
                        Image(systemName: "shield.lefthalf.filled")
                        Text(localizationManager.localized("support_antifake_share_open_hub"))
                            .font(.subheadline.bold())
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .foregroundColor(.white)
                    .padding(12)
                    .background(
                        LinearGradient(
                            colors: [Color(hex: "7C3AED"), Color(hex: "5B21B6")],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(10)
                }
                .buttonStyle(PlainButtonStyle())
            }
            .padding(14)
            .background(Color(.secondarySystemBackground).opacity(0.92))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.purple.opacity(0.25), lineWidth: 1)
            )
            .padding(.horizontal, 20)
        }
        .accessibilityElement(children: .contain)
    }

    private func antifakeShareStep(number: Int, textKey: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Text("\(number)")
                .font(.caption.bold())
                .foregroundColor(.white)
                .frame(width: 22, height: 22)
                .background(Circle().fill(Color.purple.opacity(0.85)))
            Text(localizationManager.localized(textKey))
                .font(.subheadline)
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func openAntifakeHubFromSupport() {
        if navigationManager.currentScreen == .support {
            navigationManager.navigateTo(.antifakeHub)
            return
        }
        dismiss()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
            navigationManager.navigateTo(.antifakeHub)
        }
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
                .stormGlassCard(cornerRadius: 8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.red.opacity(0.3), lineWidth: 1)
                )
            }
            .buttonStyle(PlainButtonStyle())
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
    
    // MARK: - Telegram (above FAQ + sticky)

    private var telegramAboveFAQ: some View {
        Button {
            openSupportURL(AppConfig.supportTelegramURL)
        } label: {
            HStack(spacing: 12) {
                Image(systemName: "paperplane.fill")
                    .font(.title3.weight(.semibold))
                    .foregroundColor(.white)
                VStack(alignment: .leading, spacing: 2) {
                    Text(localizationManager.localized("support_telegram_write"))
                        .font(.body.bold())
                        .foregroundColor(.white)
                    Text(localizationManager.localized("support_telegram_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
                }
                Spacer()
                Image(systemName: "arrow.up.right")
                    .foregroundColor(.white.opacity(0.9))
            }
            .padding(14)
            .background(
                LinearGradient(
                    colors: [Color.blue, Color.blue.opacity(0.75)],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, 20)
        .accessibilityLabel(localizationManager.localized("support_telegram_write"))
    }

    private var telegramStickyBar: some View {
        Button {
            openSupportURL(AppConfig.supportTelegramURL)
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "paperplane.fill")
                Text(localizationManager.localized("support_telegram_write"))
                    .font(.subheadline.bold())
                Spacer()
                Text("@AladdinchatAI_bot")
                    .font(.caption)
                    .opacity(0.9)
            }
            .foregroundColor(.white)
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(Color.blue.opacity(0.95))
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityLabel(localizationManager.localized("support_telegram_write"))
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
            
            LazyVStack(spacing: 8) {
                ForEach(displayedFAQIndices, id: \.self) { idx in
                    faqCard(item: $faqItems[idx])
                }
                if hasMoreFAQ {
                    Button {
                        withAnimation(.easeOut(duration: 0.2)) {
                            faqVisibleCount += 10
                        }
                    } label: {
                        Text(localizationManager.localized("support_faq_show_more"))
                            .font(.subheadline.bold())
                            .foregroundColor(.blue)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                    }
                    .buttonStyle(PlainButtonStyle())
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
                withAnimation(.easeOut(duration: 0.2)) {
                    let togglingId = item.wrappedValue.id
                    let expanding = !item.wrappedValue.isExpanded
                    for index in faqItems.indices {
                        if faqItems[index].id == togglingId {
                            faqItems[index].isExpanded = expanding
                        } else {
                            faqItems[index].isExpanded = false
                        }
                    }
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
        .background(Color(.secondarySystemBackground).opacity(0.88))
        .cornerRadius(8)
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



