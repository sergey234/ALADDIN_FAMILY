import SwiftUI

// MARK: - OnboardingAladdinLogoView Component
/// 🎨 Стилизованный золотой логотип "Aladdin" в скриптном стиле для онбординга
struct OnboardingAladdinLogoView: View {
    var size: CGFloat = 24
    var showSubtitle: Bool = true
    
    var body: some View {
        VStack(alignment: .center, spacing: 2) {
            // ✅ Стилизованный золотой текст "Aladdin AI"
            Text(NSLocalizedString("app.name", comment: "App name"))
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
                    Text(NSLocalizedString("app.name", comment: "App name"))
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
                Text(NSLocalizedString("app.tagline", comment: "App tagline"))
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
    
    // MARK: - State

    @State private var currentPage: Int = 0
    @State private var showJoinFamily: Bool = false
    @State private var showRecovery: Bool = false
    @State private var showRecoveryOptions = false
    @State private var showBackupRecovery = false
    @State private var showInvitationCodeInput = false
    @State private var showQRScanner = false
    @State private var profileImage: UIImage? = nil
    @State private var dataConsentAccepted: Bool = false
    @State private var showPrivacyPolicy: Bool = false

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
    
    // ⚠️ КРИТИЧНО: ДОЛЖНО БЫТЬ РОВНО 7 СТРАНИЦ!
    // Если количество страниц изменилось, это ошибка!
    // НЕ ИЗМЕНЯТЬ БЕЗ ПОДТВЕРЖДЕНИЯ!
    private static let EXPECTED_PAGES_COUNT = 7

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
        "onboarding_data_consent": "Я согласен с обработкой данных",
        "onboarding_continue_hint": "Нажмите для перехода к следующей странице",
        "onboarding_start_hint": "Нажмите для начала использования приложения"
    ]

    // ✅ НОВОЕ: Безопасная функция локализации с fallback
    private func safeLocalized(_ key: String, fallback: String? = nil) -> String {
        // Сначала пробуем получить из LocalizationManager
        let localized = localizationManager.localized(key)
        if !localized.isEmpty && localized != key { // Проверяем что это не fallback на ключ
            return localized
        }

        // Fallback к предоставленному тексту или из словаря
        return fallback ?? fallbackTexts[key] ?? key
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
    }

    private func clampCurrentPageIfNeeded() {
        guard !pages.isEmpty else {
            currentPage = 0
            return
        }

        let maxPage = pages.count - 1
        if currentPage > maxPage {
            currentPage = maxPage
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
        if pages.count != Self.EXPECTED_PAGES_COUNT && pages.count != 2 {
            // 2 страницы = минимальная версия, это нормально
            print("⚠️ OnboardingScreen: Unexpected page count: \(pages.count) (expected \(Self.EXPECTED_PAGES_COUNT) or 2)")
            print("   This might indicate a configuration issue, but continuing gracefully")

            // Не выбрасываем ошибку, просто логируем предупреждение
            // Приложение продолжит работать с имеющимися страницами
        } else {
            print("✅ OnboardingScreen: Page validation successful (\(pages.count) pages)")
        }
    }

    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана онбординга")

            // ✅ ВАРИАНТ 1: Показываем онбординг сразу, без проверки готовности локализации
            // (как в рабочем бэкапе - локализация загрузится позже и обновит тексты)
            mainOnboardingContent()
        }
        .onAppear {
            print("🚨 OnboardingScreen.onAppear: localizationManager.isReady = \(localizationManager.isReady), pages.count = \(pages.count)")
            // ✅ ВАРИАНТ 1: Загружаем страницы сразу при появлении экрана
            // loadPages() сама решит - показывать полные страницы или минимальные
            loadPages()
            print("✅ OnboardingScreen: Pages loaded (minimal or full depending on localization)")
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
        }
        .sheet(isPresented: $showBackupRecovery) {
            BackupRecoveryModal(
                isPresented: $showBackupRecovery,
                onRecoverySuccess: {
                    // После успешного восстановления
                    // Обновить UI или перейти на главный экран
                    // ✅ BUILD 98: Устанавливаем hasCompletedOnboarding асинхронно для предотвращения рекурсии
                    hasCompletedOnboarding = true
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
        }
        .sheet(isPresented: $showQRScanner) {
            QRScannerModal { code in
                // Обработка отсканированного кода
                showQRScanner = false
                // Можно добавить логику обработки кода
            }
        }
        .sheet(isPresented: $showPrivacyPolicy) {
            PrivacyPolicyScreen()
        }
    }

    // ✅ Основной контент онбординга
    private func mainOnboardingContent() -> some View {
        print("🎯 OnboardingScreen.mainOnboardingContent: showing \(pages.count) pages")
        return VStack(spacing: 0) {
            // Кнопка пропустить
            HStack {
                Spacer()

                Button(action: {
                    // ✅ Сохраняем статус онбординга
                    hasCompletedOnboarding = true
                    // ✅ BUILD 98: Устанавливаем hasCompletedOnboarding асинхронно для предотвращения рекурсии
                    hasCompletedOnboarding = true
                    Task { @MainActor in
                        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                    }
                    // ✅ Используем NavigationManager для перехода на главный экран
                    navigationManager.navigateTo(.main)
                    print("✅ OnboardingScreen: Пропущен, переход на главный экран")
                }) {
                    Text(safeLocalized("onboarding_skip"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .accessibilityElement(label: "Пропустить онбординг", hint: "Нажмите для пропуска введения и перехода к главному экрану")
                }
                .padding(Spacing.m)

                // Контент страниц
                if pages.isEmpty {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    TabView(selection: $currentPage) {
                        ForEach(0..<pages.count, id: \.self) { index in
                            onboardingPage(pages[index], index: index)
                                .tag(index)
                        }
                    }
                    .tabViewStyle(.page(indexDisplayMode: .never))
                    .accessibilityElement(children: .contain)
                    .accessibilityLabel("Страница \(currentPage + 1) из \(pages.count)")
                }

                // Индикаторы страниц
                if !pages.isEmpty {
                    HStack(spacing: Spacing.sm) {
                        ForEach(0..<pages.count, id: \.self) { index in
                            Circle()
                                .fill(currentPage == index ? Color.primaryBlue : Color.textSecondary.opacity(0.3))
                                .frame(width: currentPage == index ? 12 : 8, height: currentPage == index ? 12 : 8)
                                .animation(.spring(), value: currentPage)
                                .accessibilityLabel(currentPage == index ? "Текущая страница \(index + 1)" : "Страница \(index + 1)")
                        }
                    }
                    .padding(.vertical, Spacing.l)
                    .accessibilityElement(children: .contain)
                    .accessibilityLabel("Индикаторы страниц")
                }

                // Кнопки (на последнем слайде показываем дополнительные)
                VStack(spacing: Spacing.m) {
                    // Основная кнопка
                    Button(action: {
                        if currentPage < pages.count - 1 {
                            withAnimation {
                                currentPage += 1
                            }
                        } else {
                            // ✅ Начать регистрацию - сохраняем статус и переходим через NavigationManager
                            // Сохраняем согласие на обработку данных
                            UserDefaults.standard.set(dataConsentAccepted, forKey: "personal_data_consent_accepted")
                            
                            // ✅ BUILD 98: Устанавливаем hasCompletedOnboarding асинхронно для предотвращения рекурсии
                            hasCompletedOnboarding = true
                            Task { @MainActor in
                                UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                            }

                            // ✅ ИСПРАВЛЕНИЕ: НЕ создаем demo токены - приложение работает в демо режиме
                            print("ℹ️ OnboardingScreen: Онбординг завершен - приложение работает в демо режиме")

                            navigationManager.navigateTo(.main)
                            print("✅ OnboardingScreen: Онбординг завершён, переход на главный экран")
                        }
                    }) {
                        Text(currentPage < pages.count - 1 ? safeLocalized("onboarding_continue") : safeLocalized("onboarding_start"))
                            .font(.buttonText)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                LinearGradient(
                                    colors: currentPage == pages.count - 1 && !dataConsentAccepted
                                        ? [Color.gray, Color.gray]
                                        : [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(CornerRadius.large)
                    }
                    .disabled(currentPage == pages.count - 1 && !dataConsentAccepted)
                    .accessibilityElement(
                        label: currentPage < pages.count - 1 ? safeLocalized("onboarding_continue") : safeLocalized("onboarding_start"),
                        hint: currentPage < pages.count - 1 ? safeLocalized("onboarding_continue_hint") : safeLocalized("onboarding_start_hint")
                    )

                    // Информация о данных и согласие на последней странице
                    if currentPage == pages.count - 1 {
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

                            // Чекбокс согласия
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
                        }
                        .padding(.top, Spacing.s)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    }

                    // Дополнительные кнопки на последнем слайде
                    if currentPage == pages.count - 1 {
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
    }


    // MARK: - Onboarding Page
    
    private func onboardingPage(_ page: OnboardingScreen.OnboardingPage, index: Int) -> some View {
        VStack(spacing: Spacing.xxl) {
            Spacer()
            
            // Иконка или логотип (для страницы 7 используем логотип приложения или изображение профиля)
            if index == 6 { // Страница 7 (индекс 6)
                // Логотип приложения или изображение профиля
                // ✅ ТОЛЬКО ОДИН ЗОЛОТОЙ ОБОДОК вокруг логотипа!
                // ✅ Опускаем логотип вниз на несколько мм, чтобы не заходил за края экрана
                VStack(spacing: 0) {
                    Spacer()
                        .frame(height: 50) // Отступ сверху для кнопки SKIP (увеличено с 40 до 50)
                    
                    // Логотип приложения
                    if UIImage(named: "app_icon") != nil || UIImage(named: "AppIcon") != nil {
                        Image("app_icon")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 140, height: 140)
                            .clipShape(Circle())
                            .overlay(
                                Circle()
                                    .stroke(Color.secondaryGold, lineWidth: 14) // ✅ ОДИН золотой ободок (14px)
                            )
                    } else {
                        // Пробуем загрузить логотип из Assets или используем fallback
                        if UIImage(named: "app_icon") != nil || UIImage(named: "AppIcon") != nil {
                            Image("app_icon")
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 140, height: 140)
                                .clipShape(Circle())
                                .overlay(
                                    Circle()
                                        .stroke(Color.secondaryGold, lineWidth: 14) // ✅ ОДИН золотой ободок (14px)
                                )
                        } else {
                            Text(page.icon)
                                .font(.system(size: 80))
                                .overlay(
                                    Circle()
                                        .stroke(Color.secondaryGold, lineWidth: 14) // ✅ ОДИН золотой ободок (14px)
                                        .frame(width: 140, height: 140)
                                )
                        }
                    }
                }
            } else {
                // Обычная иконка для остальных страниц
                VStack(spacing: Spacing.m) {
                    // ✅ На странице 1 (index == 0) добавить стилизованный золотой "Aladdin" над щитом
                    if index == 0 {
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
            }
            
            // Текст
            VStack(spacing: Spacing.m) {
                // ✅ На странице 7 (index == 6) название "ALADDIN" золотым цветом
                if index == 6 {
                    Text(page.title)
                        .font(.system(size: 26, weight: .bold))
                        .foregroundColor(.secondaryGold) // ✅ Золотой цвет для ALADDIN
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.7)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.horizontal, Spacing.m)
                        .accessibilityLabel("Заголовок: \(page.title)")
                        .accessibilityAddTraits(.isHeader)
                } else {
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
                }
                
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
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Страница онбординга: \(page.title)")
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

