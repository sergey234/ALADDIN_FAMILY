import SwiftUI

// MARK: - OnboardingAladdinLogoView Component
/// 🎨 Стилизованный золотой логотип "Aladdin" в скриптном стиле для онбординга
struct OnboardingAladdinLogoView: View {
    var size: CGFloat = 24
    var showSubtitle: Bool = true
    
    var body: some View {
        VStack(alignment: .center, spacing: 2) {
            // ✅ Стилизованный золотой текст "Aladdin AI"
            Text(AppConfig.localizedAppMarketingName)
                .font(.system(size: size, weight: .bold, design: .rounded))
                .foregroundStyle(
                    LinearGradient(
                        colors: [
                            Color(red: 1.0, green: 0.84, blue: 0.0),      // Яркий золотой
                            Color(red: 0.96, green: 0.77, blue: 0.19),     // Средний золотой
                            Color(red: 0.85, green: 0.65, blue: 0.13)        // Тёмный золотой
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: Color(red: 1.0, green: 0.84, blue: 0.0).opacity(0.8), radius: 8, x: 0, y: 2)
                .shadow(color: Color(red: 0.85, green: 0.65, blue: 0.13).opacity(0.6), radius: 4, x: 0, y: 1)
                .overlay(
                    // ✅ Блики для объёмного эффекта
                    Text(AppConfig.localizedAppMarketingName)
                        .font(.system(size: size, weight: .bold, design: .rounded))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.4),
                                    Color.clear
                                ],
                                startPoint: .topLeading,
                                endPoint: .center
                            )
                        )
                        .blendMode(.overlay)
                )
                .accessibilityLabel("Название приложения Aladdin AI")
            
            if showSubtitle {
                Text(AppConfig.localizedAppMarketingTagline)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.7))
                    .dynamicTypeSize(.small ... .medium)
                    .accessibilityLabel("Описание: AI Защита семьи")
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Aladdin AI - AI Защита семьи")
    }
}

/// 👋 Onboarding Screen
/// Экран онбординга - первое знакомство с приложением + прогрессивная регистрация
/// Источник: стандартный паттерн iOS онбординга
struct OnboardingScreen: View {
    // ✅ BUILD 98: Используем @State вместо @AppStorage для предотвращения конфликта с ALADDINApp
    // @AppStorage в OnboardingScreen конфликтовал с @AppStorage в ALADDINApp, вызывая рекурсию
    @State private var hasCompletedOnboarding: Bool = false
    
    // ✅ BUILD 112: Используем Singleton LocalizationManager для предотвращения переполнения стека
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.accessibilityReduceMotion) private var accessibilityReduceMotion
    @Environment(\.layoutDirection) private var layoutDirection
    @Environment(\.colorScheme) private var colorScheme

    // MARK: - State

    @State private var currentPage: Int = 0
    /// Увеличивается при выборе языка — короткий графический «всплеск» (без новых строк локализации).
    @State private var languageSparkTick: Int = 0
    @State private var showJoinFamily: Bool = false
    @State private var showRecovery: Bool = false
    @State private var showRecoveryOptions = false
    @State private var showBackupRecovery = false
    @State private var showInvitationCodeInput = false
    @State private var showQRScanner = false
    @State private var profileImage: UIImage? = nil
    @State private var dataConsentAccepted: Bool = false
    @State private var termsConsentAccepted: Bool = false
    @State private var showPrivacyPolicy: Bool = false
    @State private var showTermsOfService: Bool = false

    /// Выбранный на шаге 0 язык (кнопки шага 0 не зависят от `LocalizationManager.isReady`).
    @State private var selectedLanguageForOnboarding: LocalizationManager.Language = .russian

    // ✅ НОВОЕ: Stored property вместо computed для устранения race condition
    // Стартуем не с пустого массива, чтобы исключить гонку первого кадра TabView(.page).
    @State private var pages: [OnboardingPage] = [
        OnboardingPage(
            icon: "🛡️",
            title: "Защита семьи",
            description: "Комплексная система защиты от киберугроз",
            color: Color.primaryBlue
        ),
        OnboardingPage(
            icon: "🦄",
            title: "ALADDIN",
            description: "Присоединяйтесь к системе безопасности",
            color: Color.secondaryGold
        )
    ]
    
    // @StateObject private var registrationVM = FamilyRegistrationViewModel()
    
    struct OnboardingPage {
        let icon: String
        let title: String
        let description: String
        let color: Color
    }
    
    // ⚠️ Контент онбординга (без шага 0 «Язык»): 7 полных или 2 минимальных.
    private static let EXPECTED_CONTENT_PAGES_COUNT = 7
    private static let MINIMAL_CONTENT_PAGES_COUNT = 2

    /// Вкладки TabView: 0 = язык, 1…N = контент (`N == pages.count`).
    private var lastTabIndex: Int {
        guard !pages.isEmpty else { return 0 }
        return pages.count
    }

    private var totalTabCount: Int {
        pages.isEmpty ? 0 : pages.count + 1
    }

    // ✅ НОВОЕ: Fallback тексты на случай проблем с локализацией
    private let fallbackTexts: [String: String] = [
        "onboarding_page1_title": "Защита всей семьи в кармане",
        "onboarding_page1_desc": "Комплексная система защиты от более 100 видов киберугроз",
        "onboarding_page2_title": "Ваш персональный агент безопасности",
        "onboarding_page2_desc": "ИИ охраняет вашу семью 24/7 + Многоуровневая система защиты ⭐⭐⭐⭐⭐! Военные технологии шифрования",
        "onboarding_page3_title": "Родительский контроль",
        "onboarding_page3_desc": "Система обучения детей безопасности. Вы видите всю активность детей в интернете. Самообучающаяся система защиты AI",
        "onboarding_page4_title": "Аналитика рисков",
        "onboarding_page4_desc": "Система ALADDIN AI предсказывает, обнаруживает и предотвращает киберугрозы, постоянно обучаясь и улучшаясь.",
        "onboarding_page5_title": "Защита для детей!",
        "onboarding_page5_desc": "Дети не смогут посещать опасные сайты, онлайн-казино, взрослые сайты или совершать покупки в играх и стриминговых сервисах",
        "onboarding_page6_title": "Защита для людей 23+",
        "onboarding_page6_desc": "AI распознает фейковые звонки, новости, сообщения и видео. Защита от поддельных голосов и номеров.",
        "onboarding_page7_title": "Присоединяйтесь к ALADDIN",
        "onboarding_page7_desc": "Спокойствие близких - бесценно. Защита начинается сегодня!",
        "onboarding_skip": "Пропустить",
        "onboarding_continue": "ПРОДОЛЖИТЬ",
        "onboarding_start": "НАЧАТЬ",
        "onboarding_have_code": "У МЕНЯ ЕСТЬ КОД",
        "onboarding_recover": "ВОССТАНОВИТЬ",
        "onboarding_data_collection_info": "Мы собираем анонимную статистику использования для улучшения приложения",
        "onboarding_privacy_policy_link": "Политика конфиденциальности",
        "onboarding_terms_of_service_link": "Пользовательское соглашение",
        "onboarding_data_consent": "Я согласен с обработкой данных",
        "onboarding_terms_consent": "Я принимаю пользовательское соглашение",
        "onboarding_continue_hint": "Нажмите для перехода к следующей странице",
        "onboarding_start_hint": "Нажмите для начала использования приложения"
    ]

    private let fallbackTextsEnglish: [String: String] = [
        "onboarding_page1_title": "Family protection in your pocket",
        "onboarding_page1_desc": "A complete protection system against cyber threats",
        "onboarding_page2_title": "Your personal security assistant",
        "onboarding_page2_desc": "AI protects your family 24/7",
        "onboarding_page3_title": "Parental control",
        "onboarding_page3_desc": "See and protect your children's digital activity",
        "onboarding_page4_title": "Risk analytics",
        "onboarding_page4_desc": "ALADDIN AI predicts and prevents cyber threats",
        "onboarding_page5_title": "Protection for kids",
        "onboarding_page5_desc": "Block unsafe websites and risky content",
        "onboarding_page6_title": "Protection for 23+ users",
        "onboarding_page6_desc": "Detect fraud calls, fake news, and spoofed voices",
        "onboarding_page7_title": "Join ALADDIN",
        "onboarding_page7_desc": "Protect your loved ones starting today",
        "onboarding_skip": "Skip",
        "onboarding_continue": "CONTINUE",
        "onboarding_start": "GET STARTED",
        "onboarding_have_code": "I HAVE A CODE",
        "onboarding_recover": "RECOVER",
        "onboarding_data_collection_info": "We collect anonymous usage metrics to improve the app",
        "onboarding_privacy_policy_link": "Privacy Policy",
        "onboarding_terms_of_service_link": "Terms of Service",
        "onboarding_data_consent": "I agree to the Privacy Policy",
        "onboarding_terms_consent": "I agree to the Terms of Service",
        "onboarding_continue_hint": "Tap to go to the next page",
        "onboarding_start_hint": "Tap to start using the app"
    ]

    // ✅ НОВОЕ: Безопасная функция локализации с fallback
    private func safeLocalized(_ key: String, fallback: String? = nil) -> String {
        let localized = localizationManager.localized(key)

        if localized.isEmpty || localized == key {
            return fallback ?? localizedFallbackValue(for: key) ?? key
        }

        // EN UI must not show Russian from LocalizationManager's global RU fallback (e.g. missing en.lproj in older builds).
        if localizationManager.currentLanguage == .english,
           let ruRef = fallbackTexts[key],
           localized == ruRef {
            return fallback ?? fallbackTextsEnglish[key] ?? localized
        }

        return localized
    }

    private func localizedFallbackValue(for key: String) -> String? {
        if localizationManager.currentLanguage == .russian {
            return fallbackTexts[key]
        }
        return fallbackTextsEnglish[key] ?? fallbackTexts[key]
    }

    private var isFinalOnboardingPage: Bool {
        guard !pages.isEmpty else { return false }
        return currentPage == lastTabIndex
    }

    private var finalRequiredConsentsAccepted: Bool {
        dataConsentAccepted && termsConsentAccepted
    }

    /// Без шага выбора роли `current_user_role` пуст — `FamilyAccessPolicy` блокирует ростер («только для родителя»).
    private func markPrimaryUserRoleParentIfUnset() {
        let existing = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard existing.isEmpty else { return }
        UserDefaults.standard.set("parent", forKey: "current_user_role")
    }

    // MARK: - Шаг 0: язык (без ожидания тяжёлого словаря)

    /// Подпись кнопки «Продолжить» на шаге 0 — только фиксированные строки по языку.
    private func languageStepContinueTitle(for language: LocalizationManager.Language) -> String {
        switch language {
        case .russian: return "Продолжить"
        case .english: return "Continue"
        case .chinese: return "继续"
        case .arabic: return "متابعة"
        }
    }

    /// Заголовок шага языка (минимальный набор фраз).
    private func languageStepTitle(for language: LocalizationManager.Language) -> String {
        switch language {
        case .russian: return "Язык приложения"
        case .english: return "App language"
        case .chinese: return "应用语言"
        case .arabic: return "لغة التطبيق"
        }
    }

    /// Если язык уже сохранён (`appLanguage`), шаг 0 пропускаем — сразу вкладка 1.
    private func applyStoredLanguageSkipIfNeeded() {
        guard UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.appLanguage) != nil else { return }
        if let raw = UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.appLanguage),
           let lang = LocalizationManager.Language(rawValue: raw) {
            selectedLanguageForOnboarding = LocalizationManager.Language.userSelectableLanguages.contains(lang) ? lang : .english
        } else {
            selectedLanguageForOnboarding = localizationManager.currentLanguage
        }
        if currentPage == 0 {
            currentPage = 1
        }
    }

    @ViewBuilder
    private func languageStepGlobe() -> some View {
        if accessibilityReduceMotion {
            Text("🌐")
                .font(.system(size: 56))
        } else {
            TimelineView(.animation(minimumInterval: 1.0 / 30.0, paused: false)) { context in
                let t = context.date.timeIntervalSinceReferenceDate
                let s = 1.0 + 0.04 * sin(t * .pi / 1.15)
                Text("🌐")
                    .font(.system(size: 56))
                    .scaleEffect(s)
            }
        }
    }

    @ViewBuilder
    private func languageStepView() -> some View {
        ZStack {
            VStack(spacing: Spacing.xl) {
            Spacer(minLength: 12)

            languageStepGlobe()

            Text(languageStepTitle(for: selectedLanguageForOnboarding))
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)
                .padding(.horizontal, Spacing.l)

            VStack(spacing: Spacing.m) {
                ForEach(LocalizationManager.Language.userSelectableLanguages, id: \.rawValue) { lang in
                    Button {
                        selectedLanguageForOnboarding = lang
                        // Тот же источник истины, что и LanguageSettingsScreen: `changeLanguage` пишет `appLanguage` + обновляет UI.
                        localizationManager.changeLanguage(to: lang)
                        loadPages()
                        HapticFeedback.selection()
                        languageSparkTick += 1
                    } label: {
                        HStack(spacing: Spacing.m) {
                            Text(lang.flag)
                                .font(.system(size: 28))
                            Text(lang.displayName)
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(.white)
                            Spacer()
                            if selectedLanguageForOnboarding == lang {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.primaryBlue)
                            }
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.white.opacity(selectedLanguageForOnboarding == lang ? 0.22 : 0.12))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(
                                            selectedLanguageForOnboarding == lang ? Color.primaryBlue : Color.white.opacity(0.2),
                                            lineWidth: selectedLanguageForOnboarding == lang ? 2 : 1
                                        )
                                )
                        )
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("\(lang.displayName)")
                }
            }
            .padding(.horizontal, Spacing.screenPadding)

            Spacer(minLength: 12)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            OnboardingLanguageSparkBurst(tick: languageSparkTick, reduceMotion: accessibilityReduceMotion)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Выбор языка приложения")
    }

    // ✅ НОВОЕ: Функция безопасной загрузки страниц с fallback
    private func loadPages() {
        print("🔄 OnboardingScreen.loadPages: Starting, localizationManager.isReady = \(localizationManager.isReady)")
        do {
            if localizationManager.isReady {
                // Попытка загрузить полные страницы
                pages = try createFullPages()
                print("✅ OnboardingScreen: Successfully loaded \(pages.count) full pages")
            } else {
                // Fallback к минимальным страницам
                pages = createMinimalPages()
                print("⚠️ OnboardingScreen: Localization not ready, using \(pages.count) minimal pages")
            }
        } catch {
            // Graceful degradation - используем минимальные страницы
            pages = createMinimalPages()
            print("❌ OnboardingScreen: Error loading pages: \(error.localizedDescription), using \(pages.count) minimal pages")
        }
        clampCurrentPageIfNeeded()
        applyStoredLanguageSkipIfNeeded()
    }

    private func clampCurrentPageIfNeeded() {
        guard !pages.isEmpty else {
            currentPage = 0
            return
        }

        let maxTab = lastTabIndex
        if currentPage > maxTab {
            currentPage = maxTab
        } else if currentPage < 0 {
            currentPage = 0
        }
    }

    // ✅ Создание полных страниц (может выбросить ошибку)
    private func createFullPages() throws -> [OnboardingPage] {
        guard localizationManager.isReady else {
            throw OnboardingError.localizationNotReady
        }

        return [
            // Страница 1: Защита всей семьи
            OnboardingPage(
                icon: "🛡️",
                title: safeLocalized("onboarding_page1_title"),
                description: safeLocalized("onboarding_page1_desc"),
                color: Color.primaryBlue
            ),
            // Страница 2: Персональный агент безопасности + Многоуровневая защита
            OnboardingPage(
                icon: "🕵️",
                title: safeLocalized("onboarding_page2_title"),
                description: safeLocalized("onboarding_page2_desc"),
                color: Color.successGreen
            ),
            // Страница 3: Родительский контроль
            OnboardingPage(
                icon: "👨‍👩‍👧",
                title: safeLocalized("onboarding_page3_title"),
                description: safeLocalized("onboarding_page3_desc"),
                color: Color.orange
            ),
            // Страница 4: Аналитика
            OnboardingPage(
                icon: "📊",
                title: safeLocalized("onboarding_page4_title"),
                description: safeLocalized("onboarding_page4_desc"),
                color: Color.red
            ),
            // Страница 5: Обучение детей безопасности
            OnboardingPage(
                icon: "🎮",
                title: safeLocalized("onboarding_page5_title"),
                description: safeLocalized("onboarding_page5_desc"),
                color: Color.purple
            ),
            // Страница 6: Интерфейс для людей 23+
            OnboardingPage(
                icon: "🧑",
                title: safeLocalized("onboarding_page6_title"),
                description: safeLocalized("onboarding_page6_desc"),
                color: Color.blue
            ),
            // Страница 7: Присоединяйтесь к ALADDIN AI
            OnboardingPage(
                icon: "🦄",
                title: safeLocalized("onboarding_page7_title"),
                description: safeLocalized("onboarding_page7_desc"),
                color: Color.green
            )
        ]
    }

    // ✅ Минимальные страницы для graceful degradation
    private func createMinimalPages() -> [OnboardingPage] {
        return [
            OnboardingPage(
                icon: "🛡️",
                title: "Защита семьи",
                description: "Комплексная система защиты от киберугроз",
                color: Color.primaryBlue
            ),
            OnboardingPage(
                icon: "🦄",
                title: "ALADDIN",
                description: "Присоединяйтесь к системе безопасности",
                color: Color.secondaryGold
            )
        ]
    }

    // MARK: - Error Types

    enum OnboardingError: Error {
        case localizationNotReady
        case invalidConfiguration

        var localizedDescription: String {
            switch self {
            case .localizationNotReady:
                return "Localization manager is not ready"
            case .invalidConfiguration:
                return "Invalid onboarding configuration"
            }
        }
    }

    // ✅ НОВОЕ: Безопасная валидация количества страниц с error handling
    private func validatePagesCount() {
        do {
            try performPagesValidation()
        } catch {
            print("❌ OnboardingScreen: Page validation error: \(error.localizedDescription)")
            // Не крашим приложение, просто логируем ошибку
            #if DEBUG
            // В debug режиме показываем alert
            print("🔍 DEBUG: Page validation failed, but continuing gracefully")
            #endif
        }
    }

    private func performPagesValidation() throws {
        // Проверяем, что страницы загружены
        guard !pages.isEmpty else {
            throw OnboardingError.invalidConfiguration
        }

        // Валидация количества страниц (только если это полные страницы)
        if pages.count != Self.EXPECTED_CONTENT_PAGES_COUNT && pages.count != Self.MINIMAL_CONTENT_PAGES_COUNT {
            // 2 контент-страницы = минимальная версия, это нормально
            print("⚠️ OnboardingScreen: Unexpected page count: \(pages.count) (expected \(Self.EXPECTED_CONTENT_PAGES_COUNT) or \(Self.MINIMAL_CONTENT_PAGES_COUNT))")
            print("   This might indicate a configuration issue, but continuing gracefully")

            // Не выбрасываем ошибку, просто логируем предупреждение
            // Приложение продолжит работать с имеющимися страницами
        } else {
            print("✅ OnboardingScreen: Page validation successful (\(pages.count) content pages + шаг языка)")
        }
    }

    /// Слот фонового героя: вкладка 0 = язык, 1…N = индекс контент-страницы `currentPage - 1`.
    private var currentHeroSlot: HeroSlot {
        if currentPage == 0 { return .onboardingLanguage }
        return .onboardingContent(pageIndex: max(0, currentPage - 1))
    }

    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана онбординга")

            HeroAmbientLayerView(slot: currentHeroSlot)
                .ignoresSafeArea()
                .opacity(0.4)
                .modifier(OnboardingHeroRTLFlipModifier(isRTL: layoutDirection == .rightToLeft))
                .accessibilityHidden(true)

            HeroBottomReadableGradient()
                .ignoresSafeArea()

            // ✅ ВАРИАНТ 1: Показываем онбординг сразу, без проверки готовности локализации
            // (как в рабочем бэкапе - локализация загрузится позже и обновит тексты)
            mainOnboardingContent()
        }
        .onAppear {
            print("🚨 OnboardingScreen.onAppear: localizationManager.isReady = \(localizationManager.isReady), pages.count = \(pages.count)")
            if UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.appLanguage) == nil {
                selectedLanguageForOnboarding = localizationManager.currentLanguage
            }
            // ✅ ВАРИАНТ 1: Загружаем страницы сразу при появлении экрана
            // loadPages() сама решит - показывать полные страницы или минимальные
            loadPages()
            print("✅ OnboardingScreen: Pages loaded (minimal or full depending on localization)")
        }
        .onChange(of: localizationManager.currentLanguage) { newLang in
            if LocalizationManager.Language.userSelectableLanguages.contains(newLang) {
                selectedLanguageForOnboarding = newLang
                loadPages()
            }
        }
        .onChange(of: localizationManager.isReady) { isReady in
            print("🔄 OnboardingScreen.onChange: localizationManager.isReady changed to \(isReady)")
            if isReady {
                loadPages()
                print("✅ OnboardingScreen: Localization became ready, loaded pages")
            }
        }
        // ✅ Модальные окна
        .sheet(isPresented: $showJoinFamily) {
            QRScannerModal { code in
                // Обработка отсканированного кода
                showJoinFamily = false
                // Можно добавить логику обработки кода
            }
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBackupRecovery) {
            BackupRecoveryModal(
                isPresented: $showBackupRecovery,
                onRecoverySuccess: {
                    // После успешного восстановления
                    // Обновить UI или перейти на главный экран
                    // ✅ BUILD 98: Устанавливаем hasCompletedOnboarding асинхронно для предотвращения рекурсии
                    hasCompletedOnboarding = true
                    markPrimaryUserRoleParentIfUnset()
                    Task { @MainActor in
                        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                    }
                    navigationManager.navigateTo(.main)
                }
            )
        }
        .sheet(isPresented: $showInvitationCodeInput) {
            InvitationCodeInputModal(
                isPresented: $showInvitationCodeInput
            )
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showQRScanner) {
            QRScannerModal { code in
                // Обработка отсканированного кода
                showQRScanner = false
                // Можно добавить логику обработки кода
            }
            .environmentObject(navigationManager)
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPrivacyPolicy) {
            PrivacyPolicyScreen()
        }
        .sheet(isPresented: $showTermsOfService) {
            TermsOfServiceScreen()
        }
    }

    // ✅ Основной контент онбординга
    private func mainOnboardingContent() -> some View {
        print("🎯 OnboardingScreen.mainOnboardingContent: \(totalTabCount) вкладок (шаг языка + \(pages.count) контента)")
        return VStack(spacing: 0) {
            // «Пропустить» только до финального шага: ведёт к экрану с 2 обязательными согласиями. На последнем шаге скрыта — иначе обход без галочек.
            // Шаг 0 (язык) пропускать нельзя — без явного «Продолжить» и записи языка.
            if currentPage > 0 && !isFinalOnboardingPage {
                HStack {
                    Spacer()

                    Button(action: {
                        guard !pages.isEmpty else { return }
                        if currentPage < lastTabIndex {
                            withAnimation {
                                currentPage = lastTabIndex
                            }
                            HapticFeedback.selection()
                        }
                    }) {
                        Text(safeLocalized("onboarding_skip"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .accessibilityElement(label: safeLocalized("onboarding_skip"), hint: safeLocalized("onboarding_continue_hint"))
                }
                .padding(Spacing.m)
            }

            // Контент страниц
            if pages.isEmpty {
                ProgressView()
                    .progressViewStyle(.circular)
                    .tint(.white)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                TabView(selection: $currentPage) {
                    languageStepView()
                        .tag(0)

                    ForEach(Array(pages.enumerated()), id: \.offset) { contentIndex, page in
                        let tabIndex = contentIndex + 1
                        onboardingPage(
                            page,
                            tabIndex: tabIndex,
                            contentIndex: contentIndex,
                            isActiveTab: currentPage == tabIndex
                        )
                            .tag(tabIndex)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Страница \(currentPage + 1) из \(totalTabCount)")
            }

            // Индикаторы страниц
            if !pages.isEmpty {
                HStack(spacing: Spacing.sm) {
                    ForEach(0..<totalTabCount, id: \.self) { index in
                        Circle()
                            .fill(currentPage == index ? Color.primaryBlue : Color.textSecondary.opacity(0.3))
                            .frame(width: currentPage == index ? 12 : 8, height: currentPage == index ? 12 : 8)
                            .animation(.spring(), value: currentPage)
                            .accessibilityLabel(currentPage == index ? "Текущая страница \(index + 1)" : "Страница \(index + 1)")
                    }
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(
                    Capsule()
                        .fill(Color.black.opacity(colorScheme == .dark ? 0.48 : 0.28))
                )
                .padding(.vertical, Spacing.l)
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Индикаторы страниц")
            }

            // Кнопки (на последнем слайде показываем дополнительные)
            VStack(spacing: Spacing.m) {
                    // Основная кнопка
                    Button(action: {
                        if currentPage == 0 {
                            localizationManager.changeLanguage(to: selectedLanguageForOnboarding)
                            UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasChosenLanguageOnce)
                            UserDefaults.standard.synchronize()
                            // Страницы собираются через safeLocalized → currentLanguage; до этого шага был язык системы/дефолт.
                            loadPages()
                            withAnimation {
                                currentPage = 1
                            }
                            HapticFeedback.selection()
                            return
                        }
                        if currentPage < lastTabIndex {
                            withAnimation {
                                currentPage += 1
                            }
                            HapticFeedback.selection()
                            return
                        }
                        if isFinalOnboardingPage {
                            guard finalRequiredConsentsAccepted else {
                                HapticFeedback.notification(.warning)
                                return
                            }
                            // ✅ Начать регистрацию - сохраняем статус и переходим через NavigationManager
                            // Сохраняем подтверждение обязательных документов раздельно
                            let now = Date()
                            UserDefaults.standard.set(dataConsentAccepted, forKey: "onboarding_privacy_policy_accepted")
                            UserDefaults.standard.set(termsConsentAccepted, forKey: "onboarding_terms_of_service_accepted")
                            UserDefaults.standard.set(dataConsentAccepted, forKey: "personal_data_consent_accepted")
                            UserDefaults.standard.set(now, forKey: "onboarding_privacy_policy_accepted_at")
                            UserDefaults.standard.set(now, forKey: "onboarding_terms_of_service_accepted_at")
                            UserDefaults.standard.set("1.0", forKey: "onboarding_privacy_policy_version")
                            UserDefaults.standard.set("1.0", forKey: "onboarding_terms_of_service_version")
                            
                            // ✅ BUILD 98: Устанавливаем hasCompletedOnboarding асинхронно для предотвращения рекурсии
                            hasCompletedOnboarding = true
                            markPrimaryUserRoleParentIfUnset()
                            Task { @MainActor in
                                UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                            }

                            // ✅ ИСПРАВЛЕНИЕ: НЕ создаем demo токены - приложение работает в демо режиме
                            print("ℹ️ OnboardingScreen: Онбординг завершен - приложение работает в демо режиме")

                            navigationManager.navigateTo(.main)
                            print("✅ OnboardingScreen: Онбординг завершён, переход на главный экран")
                        }
                    }) {
                        Group {
                            if currentPage == 0 {
                                Text(languageStepContinueTitle(for: selectedLanguageForOnboarding))
                            } else if currentPage < lastTabIndex {
                                Text(safeLocalized("onboarding_continue"))
                            } else {
                                Text(safeLocalized("onboarding_start"))
                            }
                        }
                            .font(.buttonText)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                LinearGradient(
                                    colors: isFinalOnboardingPage && !finalRequiredConsentsAccepted
                                        ? [Color.gray, Color.gray]
                                        : [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(CornerRadius.large)
                    }
                    .disabled(isFinalOnboardingPage && !finalRequiredConsentsAccepted)
                    .accessibilityElement(
                        label: currentPage == 0
                            ? languageStepContinueTitle(for: selectedLanguageForOnboarding)
                            : (currentPage < lastTabIndex ? safeLocalized("onboarding_continue") : safeLocalized("onboarding_start")),
                        hint: currentPage == 0
                            ? safeLocalized("onboarding_continue_hint")
                            : (currentPage < lastTabIndex ? safeLocalized("onboarding_continue_hint") : safeLocalized("onboarding_start_hint"))
                    )

                    // Информация о данных и согласие на последней странице
                    if isFinalOnboardingPage {
                        VStack(spacing: Spacing.s) {
                            // Краткая информация о сборе данных
                            HStack(spacing: Spacing.xs) {
                                Image(systemName: "info.circle.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.textSecondary)

                                Text(safeLocalized("onboarding_data_collection_info"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.leading)

                                Button(action: {
                                    showPrivacyPolicy = true
                                }) {
                                    Text(safeLocalized("onboarding_privacy_policy_link"))
                                        .font(.caption)
                                        .foregroundColor(.primaryBlue)
                                        .underline()
                                        .fixedSize(horizontal: false, vertical: true)
                                        .lineLimit(1)
                                        .minimumScaleFactor(0.8)
                                }
                            }
                            .padding(.horizontal, Spacing.screenPadding)

                            // Чекбокс согласия с Privacy Policy
                            HStack(spacing: Spacing.s) {
                                Button(action: {
                                    withAnimation {
                                        dataConsentAccepted.toggle()
                                    }
                                    HapticFeedback.selection()
                                }) {
                                    Image(systemName: dataConsentAccepted ? "checkmark.square.fill" : "square")
                                        .font(.system(size: 20))
                                        .foregroundColor(dataConsentAccepted ? .primaryBlue : .textSecondary)
                                }

                                Text(safeLocalized("onboarding_data_consent"))
                                    .font(.caption)
                                    .foregroundColor(.textPrimary)

                                Spacer()
                            }
                            .padding(.horizontal, Spacing.screenPadding)

                            // Ссылка + чекбокс согласия с Terms of Service
                            HStack(spacing: Spacing.s) {
                                Button(action: {
                                    showTermsOfService = true
                                }) {
                                    Text(safeLocalized("onboarding_terms_of_service_link"))
                                        .font(.caption)
                                        .foregroundColor(.primaryBlue)
                                        .underline()
                                }

                                Spacer()
                            }
                            .padding(.horizontal, Spacing.screenPadding)

                            HStack(spacing: Spacing.s) {
                                Button(action: {
                                    withAnimation {
                                        termsConsentAccepted.toggle()
                                    }
                                    HapticFeedback.selection()
                                }) {
                                    Image(systemName: termsConsentAccepted ? "checkmark.square.fill" : "square")
                                        .font(.system(size: 20))
                                        .foregroundColor(termsConsentAccepted ? .primaryBlue : .textSecondary)
                                }

                                Text(safeLocalized("onboarding_terms_consent"))
                                    .font(.caption)
                                    .foregroundColor(.textPrimary)

                                Spacer()
                            }
                            .padding(.horizontal, Spacing.screenPadding)
                        }
                        .padding(.top, Spacing.s)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    }

                    // Дополнительные кнопки на последнем слайде
                    if isFinalOnboardingPage {
                        HStack(spacing: Spacing.m) {
                            // У меня есть код
                            Button(action: {
                                showJoinFamily = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text(safeLocalized("onboarding_have_code"))
                                    .font(.caption)
                                    .foregroundColor(.secondaryGold)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 44)
                                    .background(Color.secondaryGold.opacity(0.15))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            .accessibilityElement(label: "У меня есть код", hint: "Нажмите для ввода кода семьи")

                            // Восстановить доступ
                            Button(action: {
                                showRecoveryOptions = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text(safeLocalized("onboarding_recover"))
                                    .font(.caption)
                                    .foregroundColor(.primaryBlue)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 44)
                                    .background(Color.primaryBlue.opacity(0.15))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            .accessibilityElement(label: "Восстановить доступ", hint: "Нажмите для восстановления доступа к аккаунту")
                            .confirmationDialog(
                                localizationManager.localized("recovery_options_title"),
                                isPresented: $showRecoveryOptions,
                                titleVisibility: .visible
                            ) {
                                Button(localizationManager.localized("recovery_option_manual")) {
                                    showInvitationCodeInput = true
                                }

                                Button(localizationManager.localized("recovery_option_qr")) {
                                    showQRScanner = true
                                }

                                Button(localizationManager.localized("recovery_option_backup")) {
                                    showBackupRecovery = true
                                }

                                Button(localizationManager.localized("common.cancel"), role: .cancel) {}
                            }
                        }
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .padding(.bottom, Spacing.l)
        }
    }


    // MARK: - Onboarding Page
    
    private func onboardingPage(_ page: OnboardingScreen.OnboardingPage, tabIndex _: Int, contentIndex: Int, isActiveTab _: Bool) -> some View {
        Group {
            if contentIndex == 6 {
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        Color.clear.frame(height: 8)

                        VStack(spacing: 0) {
                            if UIImage(named: "app_icon") != nil || UIImage(named: "AppIcon") != nil {
                                Image("app_icon")
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 140, height: 140)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 14)
                                    )
                            } else {
                                Text(page.icon)
                                    .font(.system(size: 80))
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 14)
                                            .frame(width: 140, height: 140)
                                    )
                            }
                        }

                        VStack(spacing: Spacing.m) {
                            Text(page.title)
                                .font(.system(size: 26, weight: .bold))
                                .foregroundColor(.secondaryGold)
                                .multilineTextAlignment(.center)
                                .lineLimit(2)
                                .minimumScaleFactor(0.7)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.horizontal, Spacing.m)
                                .accessibilityLabel("Заголовок: \(page.title)")
                                .accessibilityAddTraits(.isHeader)

                            Text(page.description)
                                .font(.system(size: 16))
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                                .fixedSize(horizontal: false, vertical: true)
                                .lineSpacing(6)
                                .padding(.horizontal, Spacing.l)
                                .accessibilityLabel("Описание: \(page.description)")
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, Spacing.xs)
                    .padding(.bottom, Spacing.m)
                }
            } else {
                VStack(spacing: Spacing.xxl) {
                    Spacer()
                    
                    VStack(spacing: Spacing.m) {
                        if contentIndex == 0 {
                            OnboardingAladdinLogoView(size: 36, showSubtitle: false)
                                .padding(.bottom, Spacing.s)
                        }
                        
                        ZStack {
                            Circle()
                                .fill(page.color.opacity(0.2))
                                .frame(width: 200, height: 200)
                            
                            Circle()
                                .fill(page.color.opacity(0.1))
                                .frame(width: 160, height: 160)
                            
                            Text(page.icon)
                                .font(.system(size: 80))
                        }
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("Иконка: \(page.icon)")
                    }
                    
                    VStack(spacing: Spacing.m) {
                        Text(page.title)
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.center)
                            .lineLimit(3)
                            .minimumScaleFactor(0.7)
                            .fixedSize(horizontal: false, vertical: true)
                            .padding(.horizontal, Spacing.m)
                            .accessibilityLabel("Заголовок: \(page.title)")
                            .accessibilityAddTraits(.isHeader)
                        
                        Text(page.description)
                            .font(.system(size: 16))
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                            .fixedSize(horizontal: false, vertical: true)
                            .lineSpacing(6)
                            .padding(.horizontal, Spacing.l)
                            .accessibilityLabel("Описание: \(page.description)")
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("\(page.title). \(page.description)")
                    
                    Spacer()
                }
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Страница онбординга: \(page.title)")
    }

}

// MARK: - Onboarding hero chrome (RTL / искры языка)

private struct OnboardingHeroRTLFlipModifier: ViewModifier {
    let isRTL: Bool

    @ViewBuilder
    func body(content: Content) -> some View {
        if isRTL {
            if #available(iOS 16.0, *) {
                content.scaleEffect(x: -1, y: 1, anchor: .center)
            } else {
                content
            }
        } else {
            content
        }
    }
}

private struct OnboardingLanguageSparkBurst: View {
    let tick: Int
    let reduceMotion: Bool
    @State private var burstVisible = false

    var body: some View {
        RadialGradient(
            colors: [Color.secondaryGold.opacity(0.55), Color.clear],
            center: .center,
            startRadius: 4,
            endRadius: 100
        )
        .frame(width: 200, height: 200)
        .opacity(burstVisible ? 1 : 0)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .onChange(of: tick) { _ in
            guard !reduceMotion else { return }
            burstVisible = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.28) {
                burstVisible = false
            }
        }
    }
}

// MARK: - Loading View

/// ✅ НОВОЕ: View для отображения загрузки во время инициализации
struct LoadingOnboardingView: View {
    var body: some View {
        VStack(spacing: Spacing.xl) {
            Spacer()

            // Анимация загрузки
            ProgressView()
                .scaleEffect(1.5)
                .tint(.secondaryGold)

            // Текст загрузки
            Text(NSLocalizedString("onboarding.preparing_app", comment: "Loading onboarding state"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LinearGradient.backgroundGradient)
    }
}

// MARK: - Preview

struct OnboardingScreen_Previews: PreviewProvider {
    static var previews: some View {
        OnboardingScreen()
    }
}

