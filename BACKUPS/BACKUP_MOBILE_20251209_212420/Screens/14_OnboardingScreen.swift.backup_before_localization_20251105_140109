import SwiftUI

/// 👋 Onboarding Screen
/// Экран онбординга - первое знакомство с приложением + прогрессивная регистрация
/// Источник: стандартный паттерн iOS онбординга
struct OnboardingScreen: View {
    @AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false
    
    // ✅ КРИТИЧНО: Добавляем NavigationManager для навигации
    @EnvironmentObject private var navigationManager: NavigationManager
    
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
    
    private let pages: [OnboardingPage] = [
        // Страница 1: Защита всей семьи
        OnboardingPage(
            icon: "🛡️",
            title: "Защита всей семьи в одном кармане",
            description: "Комплексная система защиты от более чем 100 видов киберугроз",
            color: Color.primaryBlue
        ),
        // Страница 2: Персональный агент
        OnboardingPage(
            icon: "🕵️",
            title: "Ваш персональный агент безопасности",
            description: "AI охраняет семью 24/7",
            color: Color.successGreen
        ),
        // Страница 3: Родительский контроль
        OnboardingPage(
            icon: "👨‍👩‍👧",
            title: "Родительский контроль",
            description: "Система обучения безопасности детей\n\nВы видите весь интернет детей",
            color: Color.orange
        ),
        // Страница 4: Аналитика
        OnboardingPage(
            icon: "📊",
            title: "Аналитика рисков",
            description: "Точно и наглядно",
            color: Color.red
        ),
        // Страница 5: Обучение детей безопасности
        OnboardingPage(
            icon: "🎮",
            title: "Защита для детей!",
            description: "Дети не смогут посещать опасные сайты, онлайн казино, сайты для взрослых, оплачивать покупки в игровых и стриминговых сервисах",
            color: Color.purple
        ),
        // Страница 6: Интерфейс для людей 60+
        OnboardingPage(
            icon: "👴",
            title: "Защита для людей 60+",
            description: "Один клик — помощь рядом. Определение поддельных видео, поддельного голоса, фейковых звонков и номеров!",
            color: Color.blue
        ),
        // Страница 7: Присоединяйтесь к ALADDIN
        OnboardingPage(
            icon: "🦄",
            title: "Присоединяйтесь к ALADDIN",
            description: "Спокойствие за близких — бесценно. Защита начинается сегодня!",
            color: Color.green
        )
    ]
    
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
                        Text("Пропустить")
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
                        Text(currentPage < pages.count - 1 ? "ПРОДОЛЖИТЬ" : "НАЧАТЬ")
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
                        label: currentPage < pages.count - 1 ? "Продолжить" : "Начать",
                        hint: currentPage < pages.count - 1 ? "Нажмите для перехода к следующей странице" : "Нажмите для начала использования приложения"
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
                                Text("У МЕНЯ ЕСТЬ КОД")
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
                                Text("ВОССТАНОВИТЬ")
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
                    // ✅ На странице 1 (index == 0) добавить "ALADDIN" над щитом золотым цветом
                    if index == 0 {
                        Text("ALADDIN")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.secondaryGold) // ✅ Золотой цвет
                            .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)
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

