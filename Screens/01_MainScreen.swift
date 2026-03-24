import SwiftUI
import UIKit

// ✅ BUILD 112: Оптимизация - используем статические ссылки вместо computed properties
// Master Logger for screen logging
private let logger = MasterLogger.shared
// Visual Logger for on-screen display
private let visualLogger = VisualLogger.shared

// ✅ BUILD 99 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Глобальные флаги для защиты от рекурсии
// @State не работает при пересоздании View, поэтому используем глобальные флаги с NSLock
private var isUpdatingExpirationTextGlobal: Bool = false
private let expirationTextUpdateLock = NSLock()

private var mainScreenTaskExecuted: Bool = false
private let mainScreenTaskLock = NSLock()

struct MainScreen: View {
    @State private var aiQuestion: String = ""
    @StateObject private var mainViewModel: MainViewModel
    @State private var hasAppeared = false
    @ObservedObject private var tariffManager = TariffManager.shared
    @ObservedObject private var antivirusManager = AntivirusManager.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var profileImage: UIImage? = nil
    @AppStorage("subscription_expires_at_iso") private var subscriptionExpiresAtIso: String = ""
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    // ✅ ИСПРАВЛЕНИЕ BUILD 92: Используем @AppStorage для onboarding вместо UserDefaults.standard
    // Это безопасно, так как мы НЕ используем его в .id() или computed properties
    @AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 91+: Кешированное значение для предотвращения рекурсии
    // Вместо computed property используем @State, который обновляется только при изменении subscriptionExpiresAtIso
    @State private var cachedExpirationText: String? = nil
    
    // ✅ BUILD 100: Рефакторинг - используем DateFormatterService вместо статических форматтеров
    // Централизованное управление форматтерами предотвращает рекурсию и упрощает поддержку
    private let dateFormatterService = DateFormatterService.shared
    
    // ✅ BUILD 99: Защита от рекурсии теперь через глобальный флаг (см. выше)
    // @State не работает при пересоздании View, поэтому используем глобальный флаг
    
    // MARK: - Init
    
    init() {
        // ✅ BUILD 109: Конструктор теперь абсолютно бесшумный. 
        // Логирование перенесено в .task {}, когда экран уже создан.
        let viewModel = MainViewModel()
        _mainViewModel = StateObject(wrappedValue: viewModel)
    }
    
    var body: some View {
        ZStack {
            // Фон - красивый градиент как в SupportScreen
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // ✅ УДАЛЕНО: Декораторы времени и заряда/сети - они больше не нужны
                // Заголовок - логотип слева, профиль справа
                HStack {
                    // Логотип и контент - ЛЕВЫЙ УГОЛ
                    HStack(spacing: 10) {
                        // ✅ Логотип с ободком из онбординга (как на странице 7)
                        Group {
                            if let profileImage = profileImage {
                                // Используем изображение профиля если есть
                                Image(uiImage: profileImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок (пропорционально 14px для 140x140)
                                    )
                            } else if UIImage(named: "app_icon") != nil || UIImage(named: "AppIcon") != nil {
                                // Используем логотип из Assets
                                Image("app_icon")
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок
                                    )
                            } else {
                                // Fallback - единорог с золотым ободком
                                Circle()
                                    .fill(Color.secondaryGold.opacity(0.2))
                                    .frame(width: 44, height: 44)
                                    .overlay(
                                        Text("🦄")
                                            .font(.system(size: 22))
                                    )
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок
                                    )
                            }
                        }
                        .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)
                        .accessibilityLabel("Логотип ALADDIN")
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(localizationManager.localized("main_aladdin_title"))
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.secondaryGold)
                                .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)
                                .dynamicTypeSize(.medium ... .large)
                                .accessibilityLabel("Название приложения ALADDIN")
                            
                            Text(localizationManager.localized("main_ai_protection"))
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(.white.opacity(0.7))
                                .dynamicTypeSize(.small ... .medium)
                                .accessibilityLabel("Описание: AI Защита семьи")
                        }
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("ALADDIN - AI Защита семьи")
                    }
                    
                    Spacer()
                    
                    // Кнопка профиля - ПРАВЫЙ УГОЛ (через NavigationManager)
                    Button(action: {
                        navigationManager.navigateTo(.profile)
                    }) {
                        ZStack {
                            Circle()
                                .fill(Color.secondaryGold)
                                .frame(width: 44, height: 44)
                            
                            if let profileImage = profileImage {
                                Image(uiImage: profileImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок (как у логотипа слева)
                                    )
                            } else {
                                Text("👤")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(.white)
                            }
                        }
                    }
                    .accessibilityLabel("Открыть профиль")
                    .accessibilityHint("Нажмите для перехода в профиль пользователя")
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
                
                // Основной контент - главная страница
                homeContent
                
                // Нижняя навигация - красивое меню с эмодзи
                HStack(spacing: 0) {
                    // 🎮 Игра (быстрый переход в геймификацию)
                    Button(action: {
                        logger.buttonTap("Game Tab", screen: "Main")
                        navigationManager.navigateTo(.childRewards)
                    }) {
                        VStack(spacing: 4) {
                            Text("🦄")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_game"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 🛡️ Защита (Каталог угроз)
                    Button(action: {
                        navigationManager.navigateTo(.threatProtection)
                    }) {
                        VStack(spacing: 4) {
                            Text("🛡️")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_protection"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 🔔 Уведомления
                    Button(action: {
                        navigationManager.navigateTo(.notifications)
                    }) {
                        VStack(spacing: 4) {
                            Text("🔔")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_notifications"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                                .lineLimit(1)
                                .minimumScaleFactor(0.8)  // ✅ Исправление: Предотвращение переноса "Уведомления" на две строки
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 👤 Профиль
                    Button(action: {
                        navigationManager.navigateTo(.profile)
                    }) {
                        VStack(spacing: 4) {
                            Text("👤")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_profile"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 📱 Устройства
                    Button(action: {
                        navigationManager.navigateTo(.devices)
                    }) {
                        VStack(spacing: 4) {
                            Text("📱")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_devices"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 2)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.black.opacity(0.4))
                )
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
        }
        .task {
            // ✅ BUILD 99: Заменено .onAppear на .task для предотвращения повторных вызовов при обновлении View
            // ✅ КРИТИЧНО: Логирование для TestFlight (работает в RELEASE)
            let startTime = Date()
            let logPrefix = "🔍 MainScreen.task"
            
            // ✅ BUILD 99 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Глобальный флаг для предотвращения повторных вызовов
            // @State не работает при пересоздании View, поэтому используем глобальный флаг
            mainScreenTaskLock.lock()
            guard !mainScreenTaskExecuted else {
                mainScreenTaskLock.unlock()
                let message = "\(logPrefix) Повторный вызов пропущен (глобальный флаг)"
                print("⚠️ \(message)")
                return
            }
            mainScreenTaskExecuted = true
            mainScreenTaskLock.unlock()
            
            // Сохраняем в UserDefaults для получения после краша
            var debugLog: [String] = []
            debugLog.append("\(logPrefix) START - \(Date())")
            
            // ✅ ИСПРАВЛЕНИЕ: Предотвращаем двойной вызов onAppear (дополнительная защита)
            guard !hasAppeared else {
                let message = "\(logPrefix) Повторный вызов пропущен (hasAppeared)"
                print("⚠️ \(message)")
                debugLog.append("⚠️ \(message)")
                // ✅ ИСПРАВЛЕНИЕ BUILD 92: Сохраняем логи асинхронно (копируем массив для безопасности)
                let logCopy = debugLog
                Task {
                    saveDebugLog(logCopy)
                }
                return
            }
            hasAppeared = true
            debugLog.append("✅ hasAppeared установлен в true")

            // ✅ BUILD 110: Удален logger.screenLoad для абсолютной тишины на старте
            debugLog.append("✅ logger.screenLoad пропущен (BUILD 110)")

            // ✅ ИСПРАВЛЕНИЕ BUILD 92: Используем @AppStorage вместо UserDefaults.standard
            // Это безопасно, так как мы НЕ используем его в .id() или computed properties
            debugLog.append("✅ onboardingDone = \(hasCompletedOnboarding)")
            if !hasCompletedOnboarding {
                let message = "Onboarding not completed, redirecting back"
                // ✅ BUILD 110: Удален logger.warn
                debugLog.append("⚠️ \(message)")
                // ✅ Сохраняем логи асинхронно (копируем массив для безопасности)
                let logCopy = debugLog
                Task {
                    saveDebugLog(logCopy)
                }
                navigationManager.currentScreen = .onboarding
                return
            }

            // ✅ ИСПРАВЛЕНИЕ BUILD 92: УБРАНО чтение UserDefaults в onAppear - может вызывать рекурсию с @AppStorage
            // Member ID проверка перенесена в отдельную функцию, вызываемую асинхронно

            debugLog.append("✅ Загрузка profileImage...")
            loadProfileImage()
            debugLog.append("✅ profileImage загружен")

            // ✅ ВЫЗОВ onAppear MainViewModel для автоматической загрузки данных из API
            debugLog.append("✅ Вызов mainViewModel.onAppear()...")
            mainViewModel.onAppear()
            debugLog.append("✅ mainViewModel.onAppear() завершен")
            
            // ✅ BUILD 100: Асинхронное обновление кеша expiration text для предотвращения рекурсии
            // Читаем значение один раз и передаем в функцию, чтобы избежать повторного чтения @AppStorage
            // ✅ ИСПРАВЛЕНИЕ: Убран избыточный Task { @MainActor in }, так как .task {} уже выполняется на MainActor
            let currentExpiresAt = subscriptionExpiresAtIso
            await updateExpirationTextCache(from: currentExpiresAt)
            debugLog.append("✅ cachedExpirationText инициализирован")
            
            let duration = Date().timeIntervalSince(startTime)
            debugLog.append("✅ \(logPrefix) COMPLETE - Duration: \(String(format: "%.3f", duration))s")
            // ✅ ИСПРАВЛЕНИЕ BUILD 92: Сохраняем логи асинхронно, чтобы избежать рекурсии с @AppStorage (копируем массив для безопасности)
            let logCopy = debugLog
            Task {
                saveDebugLog(logCopy)
            }
        }
        // ✅ ИСПРАВЛЕНИЕ BUILD 92: УБРАН .id() с localizationManager - может вызывать рекурсию с @AppStorage
        // localizationManager.currentLanguage читает из UserDefaults, что может вызвать рекурсию
        // View будет обновляться автоматически через @EnvironmentObject
    }
    
    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        // ✅ BUILD 113: Абсолютная детоксикация. 
        // Удалены все вызовы visualLogger.log и print, которые могут вызвать рекурсию при старте.
        
        // ШАГ 1: Проверка на Main Thread (важно для UI)
        if !Thread.isMainThread {
            DispatchQueue.main.async {
                self.loadProfileImage()
            }
            return
        }
        
        // ШАГ 2: Загрузка изображения через Singleton
        let image = ProfileImageManager.shared.loadProfileImage(for: .main)
        
        if let image = image {
            profileImage = image
        }
    }
    
    // MARK: - Debug Logging для TestFlight
    
    /// Сохраняет debug логи в UserDefaults для получения после краша
    private func saveDebugLog(_ logs: [String]) {
        let key = "main_screen_debug_log"
        let logText = logs.joined(separator: "\n")
        
        // Сохраняем текущий лог
        UserDefaults.standard.set(logText, forKey: key)
        
        // Добавляем к истории (последние 5 запусков)
        var history = UserDefaults.standard.stringArray(forKey: "\(key)_history") ?? []
        history.append(logText)
        if history.count > 5 {
            history.removeFirst()
        }
        UserDefaults.standard.set(history, forKey: "\(key)_history")
        UserDefaults.standard.synchronize()
        
        // Также сохраняем в файл для TestFlight
        saveDebugLogToFile(logs)
    }
    
    /// Сохраняет debug логи в файл (работает в RELEASE/TestFlight)
    private func saveDebugLogToFile(_ logs: [String]) {
        guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        
        let logFile = documentsPath.appendingPathComponent("main_screen_debug_log.txt")
        let logText = logs.joined(separator: "\n")
        
        do {
            try logText.write(to: logFile, atomically: true, encoding: .utf8)
            UserDefaults.standard.set(logFile.path, forKey: "main_screen_debug_log_file_path")
            UserDefaults.standard.synchronize()
        } catch {
            // Игнорируем ошибки записи файла
        }
    }
    
    /// Сохраняет логи инициализации MainScreen
    private func saveInitDebugLog(_ logs: [String]) {
        let key = "main_screen_init_debug_log"
        let logText = logs.joined(separator: "\n")
        UserDefaults.standard.set(logText, forKey: key)
        
        // Добавляем к истории
        var history = UserDefaults.standard.stringArray(forKey: "\(key)_history") ?? []
        history.append(logText)
        if history.count > 5 {
            history.removeFirst()
        }
        UserDefaults.standard.set(history, forKey: "\(key)_history")
        UserDefaults.standard.synchronize()
    }
    
    /// Сохраняет логи body MainScreen
    private func saveBodyDebugLog(_ logs: [String]) {
        let key = "main_screen_body_debug_log"
        let logText = logs.joined(separator: "\n")
        UserDefaults.standard.set(logText, forKey: key)
        
        // Добавляем к истории
        var history = UserDefaults.standard.stringArray(forKey: "\(key)_history") ?? []
        history.append(logText)
        if history.count > 5 {
            history.removeFirst()
        }
        UserDefaults.standard.set(history, forKey: "\(key)_history")
        UserDefaults.standard.synchronize()
    }
    
    /// Сохраняет логи loadProfileImage
    private func saveLoadProfileImageDebugLog(_ logs: [String]) {
        let key = "main_screen_load_profile_image_debug_log"
        let logText = logs.joined(separator: "\n")
        UserDefaults.standard.set(logText, forKey: key)
        
        // Добавляем к истории
        var history = UserDefaults.standard.stringArray(forKey: "\(key)_history") ?? []
        history.append(logText)
        if history.count > 5 {
            history.removeFirst()
        }
        UserDefaults.standard.set(history, forKey: "\(key)_history")
        UserDefaults.standard.synchronize()
    }
    
    // MARK: - Home Content
    
    private var homeContent: some View {
        ScrollView {
            VStack(spacing: 20) {
                        // Карточки функций - сетка 2x2
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 15) {
                            // Антивирус карточка (вместо VPN)
                            Button(action: {
                                navigationManager.navigateTo(.networkProtection)
                            }) {
                                VStack(spacing: 8) {
                                    HStack(spacing: 8) {
                                        Text("🛡️")
                                            .font(.system(size: 20))
                                            .accessibilityLabel("Иконка антивируса")
                                        Text(antivirusEnabled ? "🟢" : "🔴")
                                            .font(.system(size: 24))
                                            .accessibilityLabel(antivirusEnabled ? "Статус: Активен" : "Статус: Отключен")
                                    }
                                    
                                    Text(localizationManager.localized("main_antivirus_title"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: Антивирус Аладин")
                                    
                                    Text(localizationManager.localized("main_antivirus_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                        .accessibilityLabel("Описание: Защита устройств")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            .accessibilityLabel("Антивирус Аладин - \(antivirusEnabled ? "Активен" : "Отключен")")
                            .accessibilityHint("Нажмите для открытия экрана защиты")
                            
                            // Тарифы карточка
                            Button(action: {
                                navigationManager.navigateTo(.tariffs)
                            }) {
                                VStack(spacing: 8) {
                                    Text("💎")
                                        .font(.system(size: 20))
                                        .accessibilityLabel("Иконка тарифов")
                                    
                                    Text(localizationManager.localized("main_tariffs"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: Тарифы")
                                    
                                    Text(localizationManager.localized("main_tariffs_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                        .accessibilityLabel("Описание: Выбор плана")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            .accessibilityLabel("Тарифы - Выбор плана")
                            .accessibilityHint("Нажмите для открытия экрана тарифов")
                            
                            // Аналитика карточка (через NavigationManager)
                            Button(action: {
                                navigationManager.navigateTo(.analytics)
                            }) {
                                VStack(spacing: 8) {
                                    Text("📊")
                                        .font(.system(size: 20))
                                    
                                    Text(localizationManager.localized("main_analytics"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text(localizationManager.localized("main_analytics_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            
                            // Настройки карточка
                            NavigationLink(destination: Group {
                                // ✅ [REVERT] SettingsScreen с EnvironmentObject
                                SettingsScreen()
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                            }) {
                                VStack(spacing: 8) {
                                    Text("⚙️")
                                        .font(.system(size: 20))
                                    
                                    Text(localizationManager.localized("main_settings"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text(localizationManager.localized("main_settings_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                        }
                        .padding(.horizontal, 20)
                        
                        // FAMILY статус - большая карточка
                        VStack(spacing: 12) {
                            // Заголовок с капсулой статуса
                            HStack {
                                Text("👨‍👩‍👧‍👦")
                                    .font(.system(size: 18))
                                
                                Text(localizationManager.localized("main_family_title"))
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.black)
                                
                                // ✅ BUILD 115: Восстановлен ID пользователя из бэкапа от 6 марта
                                Group {
                                    let memberId = UserDefaults.standard.string(forKey: "your_member_id") ?? ""
                                    if !memberId.isEmpty {
                                        Spacer()
                                        
                                        Button(action: {
                                            UIPasteboard.general.string = memberId
                                            let generator = UINotificationFeedbackGenerator()
                                            generator.notificationOccurred(.success)
                                            logger.business("Member ID copied: \(memberId)")
                                        }) {
                                            HStack(spacing: 4) {
                                                Text("\(localizationManager.localized("main_family_user_id")) \(memberId)")
                                                    .font(.system(size: 9, weight: .semibold))
                                                    .foregroundColor(.black)
                                                
                                                Image(systemName: "doc.on.doc")
                                                    .font(.system(size: 10, weight: .medium))
                                                    .foregroundColor(.black.opacity(0.8))
                                            }
                                            .padding(.horizontal, 10)
                                            .padding(.vertical, 5)
                                            .background(
                                                Capsule()
                                                    .fill(Color.black.opacity(0.15))
                                            )
                                        }
                                        .buttonStyle(PlainButtonStyle())
                                    } else {
                                        // ✅ ОТЛАДКА: Выводим информацию если ID не найден
                                        #if DEBUG
                                        Spacer()
                                        Text("(ID не найден)")
                                            .font(.system(size: 8))
                                            .foregroundColor(.red.opacity(0.5))
                                        #endif
                                    }
                                }
                                
                                Spacer()
                                
                                // Капсула статуса (вместо тумблера)
                                FamilyStatusBadge(
                                    status: mainViewModel.familyProtectionStatus,
                                    localizationManager: localizationManager,
                                    action: {
                                        navigationManager.navigateTo(.family)
                                    }
                                )
                            }
                            .onAppear {
                                // ✅ BUILD 115: Восстановлена отладка ID пользователя из бэкапа
                                let memberId = UserDefaults.standard.string(forKey: "your_member_id")
                                logger.business("🔍 MainScreen: Проверка ID пользователя")
                                logger.business("   - your_member_id = \(memberId ?? "nil")")
                                if let id = memberId, !id.isEmpty {
                                    logger.business("✅ MainScreen: ID найден и будет отображен: \(id)")
                                } else {
                                    logger.business("⚠️ MainScreen: ID не найден в UserDefaults!")
                                    logger.business("   - ID будет отображаться только после регистрации/присоединения к семье")
                                }
                            }
                            
                            // Информация о семье - ДИНАМИЧЕСКАЯ из MainViewModel
                            VStack(alignment: .leading, spacing: 3) {
                                Text(localizationManager.localized("main_family_info", mainViewModel.familyMembers, mainViewModel.devicesProtected))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                // Сообщение статуса (из API или fallback)
                                Text(mainViewModel.familyProtectionStatusMessage ?? localizationManager.localized(mainViewModel.familyProtectionStatus.messageLocalizationKey))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text(localizationManager.localized("main_family_network_protection_info", mainViewModel.threatsBlocked))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)

                                Text("\(localizationManager.localized("main_family_tariff_label")) \(currentTariffDisplayName)")
                                    .font(.system(size: 9, weight: .semibold))
                                    .foregroundColor(.black)

                                if let expirationText = cachedExpirationText {
                                    Text("\(localizationManager.localized("main_family_subscription_valid_until")) \(expirationText)")
                                        .font(.system(size: 9))
                                        .foregroundColor(.black)
                                }
                            }
                            
                            // Кнопки действий
                            HStack(spacing: 8) {
                                Button(action: {
                                    navigationManager.navigateTo(.family)
                                }) {
                                    Text(localizationManager.localized("main_family_manage"))
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.secondaryGold)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black)
                                        )
                                }
                                
                                Button(action: {
                                    // Используем модал для добавления участника
                                    navigationManager.navigateTo(.addMemberOptions)
                                }) {
                                    Text(localizationManager.localized("main_family_add_member"))
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.black)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black.opacity(0.2))
                                                .overlay(
                                                    RoundedRectangle(cornerRadius: 8)
                                                        .stroke(Color.black, lineWidth: 2)
                                                )
                                        )
                                }
                            }
                        }
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(
                                    LinearGradient(
                                        colors: [Color.secondaryGold, Color.secondaryGold.opacity(0.8)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.secondaryGold, lineWidth: 2)
                                )
                        )
                        .shadow(color: Color.secondaryGold.opacity(0.3), radius: 8)
                        .padding(.horizontal, 20)
                        
                        // AI помощник
                        Button(action: {
                            navigationManager.navigateTo(.aiAssistant)
                        }) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(localizationManager.localized("main_ai_assistant_title"))
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundColor(.secondaryGold)
                                
                                Text(localizationManager.localized("main_ai_assistant_greeting"))
                                    .font(.system(size: 10))
                                    .foregroundColor(.white.opacity(0.9))
                                
                                TextField(localizationManager.localized("main_ai_assistant_placeholder"), text: $aiQuestion)
                                    .font(.system(size: 11))
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 8)
                                    .background(
                                        RoundedRectangle(cornerRadius: 16)
                                            .fill(Color.white.opacity(0.1))
                                            .overlay(
                                                RoundedRectangle(cornerRadius: 16)
                                                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
                                            )
                                    )
                            }
                            .padding(10)
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(Color.secondaryGold.opacity(0.1))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 10)
                                            .stroke(Color.secondaryGold, lineWidth: 2)
                                    )
                            )
                        }
                        .padding(.horizontal, 20)
                        
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Основной контент приложения")
    }

    private var currentTariffDisplayName: String {
        switch tariffManager.currentTariff {
        case .trial:
            return localizationManager.localized("tariffs_trial")
        case .free:
            return localizationManager.localized("tariffs_free")
        case .personal:
            return localizationManager.localized("tariffs_personal")
        case .family:
            return localizationManager.localized("tariffs_family")
        case .premium:
            return localizationManager.localized("tariffs_premium")
        }
    }

    // ✅ BUILD 100: Старые статические форматтеры удалены
    // Теперь используется DateFormatterService для всех операций форматирования дат
    // Это предотвращает рекурсию и упрощает поддержку кода
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 92: Функция для обновления кеша БЕЗ чтения @AppStorage напрямую
    // Принимает значение как параметр, чтобы избежать рекурсии через @AppStorage
    // ✅ BUILD 99: Функция сделана асинхронной для предотвращения блокировки main thread и рекурсии
    private func updateExpirationTextCache(from isoString: String) async {
        // ✅ BUILD 99 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Глобальный флаг с NSLock для защиты от рекурсии
        // @State не работает при пересоздании View, поэтому используем глобальный флаг
        let callId = UUID().uuidString
        print("🔍 [MainScreen] updateExpirationTextCache START - \(callId) - \(Date())")
        
        expirationTextUpdateLock.lock()
        guard !isUpdatingExpirationTextGlobal else {
            expirationTextUpdateLock.unlock()
            print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем - \(callId)")
            return
        }
        isUpdatingExpirationTextGlobal = true
        expirationTextUpdateLock.unlock()
        
        defer {
            expirationTextUpdateLock.lock()
            isUpdatingExpirationTextGlobal = false
            expirationTextUpdateLock.unlock()
            print("✅ [MainScreen] updateExpirationTextCache COMPLETE - \(callId) - \(Date())")
        }
        
        guard !isoString.isEmpty else {
            await MainActor.run {
                cachedExpirationText = nil
            }
            return
        }
        
        // ✅ BUILD 100 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем DateFormatterService вместо старого кода
        // DateFormatterService использует статический Calendar и предотвращает рекурсию
        // Это исправляет краш в background thread (Thread 7)
        let formattedText = await MainActor.run {
            dateFormatterService.formatExpirationDate(from: isoString)
        }
        
        await MainActor.run {
            cachedExpirationText = formattedText
        }
    }
    
    // MARK: - Navigation Button Content
    
    private func navButtonContent(icon: String, label: String, isActive: Bool = false) -> some View {
        VStack(spacing: 2) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundColor(isActive ? .white : .white.opacity(0.7))
            
            Text(label)
                .font(.system(size: 8, weight: .bold))
                .foregroundColor(isActive ? .white : .white.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 4)
    }
}

// MARK: - Family Status Badge

struct FamilyStatusBadge: View {
    let status: FamilyProtectionStatus
    let localizationManager: LocalizationManager
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                // Иконка
                Image(systemName: status.iconName)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(status.iconColor)
                
                // Текст статуса
                Text(localizationManager.localized(status.titleLocalizationKey))
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(status.iconColor)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(status.color.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - FamilyProtectionStatus Extension

extension FamilyProtectionStatus {
    var iconColor: Color {
        switch self {
        case .active: return Color(red: 0.04, green: 0.55, blue: 0.28) // #0A8C47
        case .paused: return Color(red: 0.43, green: 0.45, blue: 0.52) // #6E7484
        case .attention: return Color(red: 0.88, green: 0.55, blue: 0.16) // #E08F29
        case .critical: return Color(red: 0.88, green: 0.26, blue: 0.27) // #E04345
        }
    }
}

struct MainScreen_Previews: PreviewProvider {
    static var previews: some View {
        MainScreen()
    }
}

struct Previews_01_MainScreen_LibraryContent: LibraryContentProvider {
    var views: [LibraryItem] {
        LibraryItem(/*@START_MENU_TOKEN@*/Text("Hello, World!")/*@END_MENU_TOKEN@*/)
    }
}
