import SwiftUI

// MARK: - OnboardingAladdinLogoView Component
/// 🎨 Стилизованный золотой логотип "Aladdin" в скриптном стиле для онбординга
struct OnboardingAladdinLogoView: View {
    var size: CGFloat = 24
    var showSubtitle: Bool = true
    
    var body: some View {
        VStack(alignment: .center, spacing: 2) {
            // ✅ Стилизованный золотой текст "Aladdin"
            Text("Aladdin")
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
                    Text("Aladdin")
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
                .accessibilityLabel("Название приложения Aladdin")
            
            if showSubtitle {
                Text("AI Защита семьи")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.7))
                    .dynamicTypeSize(.small ... .medium)
                    .accessibilityLabel("Описание: AI Защита семьи")
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Aladdin - AI Защита семьи")
    }
}

/// 👋 Onboarding Screen
/// Экран онбординга - первое знакомство с приложением + прогрессивная регистрация
/// Источник: стандартный паттерн iOS онбординга
struct OnboardingScreen: View {
    @AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false
    
    // ✅ КРИТИЧНО: Добавляем NavigationManager для навигации
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // MARK: - State
    
    @State private var currentPage: Int = 0
    @State private var showJoinFamily: Bool = false
    @State private var showRecovery: Bool = false
    @State private var profileImage: UIImage? = nil
    
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
    
    private var pages: [OnboardingPage] {
        [
        // Страница 1: Защита всей семьи
        OnboardingPage(
            icon: "🛡️",
            title: localizationManager.localized("onboarding_page1_title"),
            description: localizationManager.localized("onboarding_page1_desc"),
            color: Color.primaryBlue
        ),
        // Страница 2: Персональный агент безопасности + Многоуровневая защита
        OnboardingPage(
            icon: "🕵️",
            title: localizationManager.localized("onboarding_page2_title"),
            description: localizationManager.localized("onboarding_page2_desc"),
            color: Color.successGreen
        ),
        // Страница 3: Родительский контроль
        OnboardingPage(
            icon: "👨‍👩‍👧",
            title: localizationManager.localized("onboarding_page3_title"),
            description: localizationManager.localized("onboarding_page3_desc"),
            color: Color.orange
        ),
        // Страница 4: Аналитика
        OnboardingPage(
            icon: "📊",
            title: localizationManager.localized("onboarding_page4_title"),
            description: localizationManager.localized("onboarding_page4_desc"),
            color: Color.red
        ),
        // Страница 5: Обучение детей безопасности
        OnboardingPage(
            icon: "🎮",
            title: localizationManager.localized("onboarding_page5_title"),
            description: localizationManager.localized("onboarding_page5_desc"),
            color: Color.purple
        ),
        // Страница 6: Интерфейс для людей 60+
        OnboardingPage(
            icon: "👴",
            title: localizationManager.localized("onboarding_page6_title"),
            description: localizationManager.localized("onboarding_page6_desc"),
            color: Color.blue
        ),
        // Страница 7: Присоединяйтесь к ALADDIN
        OnboardingPage(
            icon: "🦄",
            title: localizationManager.localized("onboarding_page7_title"),
            description: localizationManager.localized("onboarding_page7_desc"),
            color: Color.green
        )
        ]
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана онбординга")
            
            VStack(spacing: 0) {
                // Кнопка пропустить
                HStack {
                    Spacer()
                    
                    Button(action: {
                        // ✅ Сохраняем статус онбординга
                        hasCompletedOnboarding = true
                        // ✅ Используем NavigationManager для перехода на главный экран
                        navigationManager.navigateTo(.main)
                        print("✅ OnboardingScreen: Пропущен, переход на главный экран")
                    }) {
                        Text(localizationManager.localized("onboarding_skip"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .accessibilityElement(label: "Пропустить онбординг", hint: "Нажмите для пропуска введения и перехода к главному экрану")
                }
                .padding(Spacing.m)
                
                // Контент страниц
                TabView(selection: $currentPage) {
                    ForEach(0..<pages.count, id: \.self) { index in
                        onboardingPage(pages[index], index: index)
                            .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Страница \(currentPage + 1) из \(pages.count)")
                
                // Индикаторы страниц
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
                            hasCompletedOnboarding = true
                            navigationManager.navigateTo(.main)
                            print("✅ OnboardingScreen: Онбординг завершён, переход на главный экран")
                        }
                    }) {
                        Text(currentPage < pages.count - 1 ? localizationManager.localized("onboarding_continue") : localizationManager.localized("onboarding_start"))
                            .font(.buttonText)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                LinearGradient(
                                    colors: [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(CornerRadius.large)
                    }
                    .accessibilityElement(
                        label: currentPage < pages.count - 1 ? localizationManager.localized("onboarding_continue") : localizationManager.localized("onboarding_start"),
                        hint: currentPage < pages.count - 1 ? localizationManager.localized("onboarding_continue_hint") : localizationManager.localized("onboarding_start_hint")
                    )
                    
                    // Дополнительные кнопки на последнем слайде
                    if currentPage == pages.count - 1 {
                        HStack(spacing: Spacing.m) {
                            // У меня есть код
                            Button(action: {
                                showJoinFamily = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text(localizationManager.localized("onboarding_have_code"))
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
                                showRecovery = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text(localizationManager.localized("onboarding_recover"))
                                    .font(.caption)
                                    .foregroundColor(.primaryBlue)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 44)
                                    .background(Color.primaryBlue.opacity(0.15))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            .accessibilityElement(label: "Восстановить доступ", hint: "Нажмите для восстановления доступа к аккаунту")
                        }
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .padding(.bottom, Spacing.l)
            }
        }
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 OnboardingScreen загружен!")
            // Загружаем изображение профиля при загрузке экрана
            profileImage = ProfileImageManager.shared.loadProfileImage()
            
            // ⚠️ КРИТИЧЕСКАЯ ПРОВЕРКА: Количество страниц должно быть 7!
            if pages.count != Self.EXPECTED_PAGES_COUNT {
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Количество страниц онбординга изменилось!")
                print("   Ожидалось: \(Self.EXPECTED_PAGES_COUNT)")
                print("   Найдено: \(pages.count)")
                print("   Проверьте файл: Screens/14_OnboardingScreen.swift")
                print("   Возможные причины:")
                print("   1. Файл был перезаписан из резервной копии")
                print("   2. Git автоматически откатил изменения")
                print("   3. Xcode использует старую версию из кеша")
                assertionFailure("Количество страниц онбординга изменилось с \(Self.EXPECTED_PAGES_COUNT) на \(pages.count)!")
            } else {
                print("✅ Проверка онбординга: \(pages.count) страниц (ожидалось \(Self.EXPECTED_PAGES_COUNT))")
            }
        }
        // ✅ УБРАНО: .fullScreenCover() - теперь используем NavigationManager для навигации
        .sheet(isPresented: $showJoinFamily) {
            QRScannerModal(
                isPresented: $showJoinFamily
            )
        }
        .sheet(isPresented: $showRecovery) {
            RecoveryOptionsModal(
                isPresented: $showRecovery
            )
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("onboarding_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Onboarding Page
    
    private func onboardingPage(_ page: OnboardingPage, index: Int) -> some View {
        VStack(spacing: Spacing.xxl) {
            Spacer()
            
            // Иконка или логотип (для страницы 7 используем логотип приложения или изображение профиля)
            if index == 6 { // Страница 7 (индекс 6)
                // Логотип приложения или изображение профиля
                // ✅ ТОЛЬКО ОДИН ЗОЛОТОЙ ОБОДОК вокруг логотипа!
                if let profileImage = profileImage {
                    Image(uiImage: profileImage)
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
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.secondaryGold) // ✅ Золотой цвет для ALADDIN
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                        .padding(.horizontal, Spacing.l)
                        .accessibilityLabel("Заголовок: \(page.title)")
                        .accessibilityAddTraits(.isHeader)
                } else {
                    Text(page.title)
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                        .padding(.horizontal, Spacing.l)
                        .accessibilityLabel("Заголовок: \(page.title)")
                        .accessibilityAddTraits(.isHeader)
                }
                
                Text(page.description)
                    .font(.system(size: 16))
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
                    .minimumScaleFactor(0.85)
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
}

// MARK: - Preview

struct OnboardingScreen_Previews: PreviewProvider {
    static var previews: some View {
        OnboardingScreen()
    }
}

