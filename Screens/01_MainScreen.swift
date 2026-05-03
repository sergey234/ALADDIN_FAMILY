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

struct MainScreen: View {
    private enum HomeChatDestination: String, CaseIterable {
        case family
        case ai
    }
    private enum HomeChatDefaultMode: String, CaseIterable {
        case family
        case ai
        case last
        case smart
    }

    @State private var aiQuestion: String = ""
    @Environment(\.scenePhase) private var scenePhase
    @EnvironmentObject private var mainViewModel: MainViewModel
    @State private var hasAppeared = false
    @ObservedObject private var subscriptionManager = SubscriptionManager.shared
    @ObservedObject private var antivirusManager = AntivirusManager.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var profileImage: UIImage? = nil
    @AppStorage("subscription_expires_at_iso") private var subscriptionExpiresAtIso: String = ""
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    @AppStorage("home_chat_destination") private var homeChatDestinationRaw: String = HomeChatDestination.family.rawValue
    @AppStorage("home_chat_default_mode") private var homeChatDefaultModeRaw: String = HomeChatDefaultMode.last.rawValue
    @AppStorage("home_chat_last_family_activity_at") private var lastFamilyActivityAt: Double = 0
    @AppStorage("home_chat_last_ai_activity_at") private var lastAIActivityAt: Double = 0
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
                    .accessibilityIdentifier("main_nav_profile")
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
            
            // Важно: не используем глобальный флаг, иначе после добавления пользователей
            // повторный вход на MainScreen может не вызвать mainViewModel.onAppear() и оставить 0/Free.
            
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
            Task { await subscriptionManager.syncSubscriptionOnMainScreenAppear() }
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
        .onAppear {
            // Холодный старт: счётчик подтянет полный loadDashboardData из .task (без лишнего GET /api/devices).
            // После первого успешного дашборда lastUpdateTime ≠ nil — при возврате на главную обновляем только девайсы.
            if mainViewModel.lastUpdateTime != nil {
                mainViewModel.refreshDevicesCountFromAPI()
            }
            // Критично для реального устройства: .task с forceSync выполняется один раз (hasAppeared).
            // После экрана «Тарифы»/оплаты в Safari подписка на сервере уже другая — без синка главная остаётся на free/жёлтом.
            Task { await subscriptionManager.syncSubscriptionOnMainScreenAppear() }
            mainViewModel.requestRefreshDebounced()
        }
        .onChange(of: scenePhase) { newPhase in
            guard newPhase == .active else { return }
            Task { await subscriptionManager.syncSubscriptionOnMainScreenAppear() }
            mainViewModel.requestRefreshDebounced()
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
                            .accessibilityIdentifier("main_nav_network_protection")
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
                            .accessibilityIdentifier("main_nav_tariffs")
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
                            HStack(alignment: .top) {
                                Text("👨‍👩‍👧‍👦")
                                    .font(.system(size: 18))
                                
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(localizationManager.localized("main_family_header_title"))
                                        .font(.system(size: 14, weight: .bold))
                                        .foregroundColor(.black)
                                    // Лимит по тарифу (как «3 из 5» в семейной защите): сколько уже в семье / максимум по плану.
                                    Text(
                                        localizationManager.localized(
                                            "main_family_header_member_slots",
                                            min(mainViewModel.familyMembers, max(0, subscriptionManager.currentFamilyLimit)),
                                            max(0, subscriptionManager.currentFamilyLimit)
                                        )
                                    )
                                    .font(.system(size: 10, weight: .semibold))
                                    .foregroundColor(.black.opacity(0.82))
                                    .accessibilityLabel(
                                        localizationManager.localized(
                                            "main_family_header_member_slots",
                                            min(mainViewModel.familyMembers, max(0, subscriptionManager.currentFamilyLimit)),
                                            max(0, subscriptionManager.currentFamilyLimit)
                                        )
                                    )
                                }
                                
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
                                        Text(localizationManager.localized("main_member_id_not_found_debug"))
                                            .font(.system(size: 8))
                                            .foregroundColor(.red.opacity(0.5))
                                        #endif
                                    }
                                }
                                
                                Spacer()

                                // Капсула = статус защиты семьи (API), не путать с тарифом подписи ниже.
                                VStack(alignment: .trailing, spacing: 2) {
                                    Text(localizationManager.localized("main_family_protection_badge_caption"))
                                        .font(.system(size: 7, weight: .medium))
                                        .foregroundColor(.black.opacity(0.55))
                                        .multilineTextAlignment(.trailing)
                                        .accessibilityHidden(true)

                                    FamilyStatusBadge(
                                        status: mainViewModel.familyProtectionStatus,
                                        localizationManager: localizationManager,
                                        action: {
                                            navigationManager.navigateTo(.family)
                                        }
                                    )
                                }
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel(
                                    "\(localizationManager.localized("main_family_protection_badge_caption")). \(localizationManager.localized(mainViewModel.familyProtectionStatus.titleLocalizationKey))"
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
                                Text(localizationManager.localized(mainViewModel.familyProtectionStatus.messageLocalizationKey))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text(localizationManager.localized("main_family_network_protection_info", mainViewModel.threatsBlocked))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)

                                // ✅ IMPROVED: Dynamic tariff name with color accent and icon
                                // layoutPriority + minimumScaleFactor: на узких ширинах HStack не должен сжимать название тарифа до нуля.
                                HStack(spacing: 4) {
                                    Image(systemName: tariffIconForCurrentLevel())
                                        .font(.system(size: 10))
                                        .foregroundColor(currentTariffColor)
                                    Text("\(localizationManager.localized("main_family_tariff_label")) \(currentTariffDisplayName)")
                                        .font(.system(size: 9, weight: .semibold))
                                        .foregroundColor(.black)
                                        .lineLimit(2)
                                        .minimumScaleFactor(0.72)
                                        .multilineTextAlignment(.leading)
                                        .layoutPriority(1)
                                }
                                // epoch: гарантированный refresh строки тарифа после trial/IAP/синка на реальном устройстве
                                .id("tariff_\(subscriptionManager.subscriptionDisplayEpoch)_\(tariffRowViewIdentity)")

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
                                .accessibilityIdentifier("main_nav_family_manage")
                                
                                Button(action: {
                                    // Та же семья: помечаем admin-add, чтобы createFamily() вызвал addFamilyMember, а не family/create
                                    let fid = (UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "")
                                        .trimmingCharacters(in: .whitespacesAndNewlines)
                                    if !fid.isEmpty {
                                        UserDefaults.standard.set(true, forKey: "admin_add_mode")
                                        UserDefaults.standard.synchronize()
                                    }
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
                            RoundedRectangle(cornerRadius: 12)
                                .fill(
                                    LinearGradient(
                                        colors: [currentTariffColor, currentTariffColor.opacity(0.85)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(currentTariffColor.opacity(0.6), lineWidth: 2)
                                )
                        )
                        .shadow(color: currentTariffColor.opacity(0.4), radius: 10, x: 0, y: 4)
                        // Тот же epoch, что у строки тарифа: на девайсе SwiftUI иначе не пересобирает градиент/тень по `currentTariffColor`.
                        .id("family_tariff_card_\(subscriptionManager.subscriptionDisplayEpoch)_\(tariffRowViewIdentity)")
                        .padding(.horizontal, 20)
                        
                        // Chat switcher + contextual quick entry (ненавязчиво рядом с чатом)
                        VStack(alignment: .leading, spacing: 8) {
                            HStack(spacing: 8) {
                                ForEach(HomeChatDestination.allCases, id: \.rawValue) { destination in
                                    let isSelected = (HomeChatDestination(rawValue: homeChatDestinationRaw) ?? .family) == destination
                                    Button(action: {
                                        homeChatDestinationRaw = destination.rawValue
                                    }) {
                                        Text(
                                            destination == .family
                                            ? localizationManager.localized("main_home_chat_segment_family")
                                            : localizationManager.localized("main_home_chat_segment_ai")
                                        )
                                            .font(.system(size: 11, weight: .semibold))
                                            .foregroundColor(isSelected ? .black : .white.opacity(0.82))
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 8)
                                            .background(
                                                RoundedRectangle(cornerRadius: 10)
                                                    .fill(isSelected ? currentTariffColor.opacity(0.88) : Color.black.opacity(0.16))
                                            )
                                            .overlay(
                                                RoundedRectangle(cornerRadius: 10)
                                                    .stroke(isSelected ? Color.black.opacity(0.24) : Color.white.opacity(0.18), lineWidth: 1)
                                            )
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.horizontal, 4)

                            Button(action: {
                                let current = HomeChatDestination(rawValue: homeChatDestinationRaw) ?? .family
                                switch current {
                                case .family:
                                    navigationManager.navigateTo(.familyChat)
                                case .ai:
                                    navigationManager.navigateTo(.aiAssistant)
                                }
                            }) {
                            VStack(alignment: .leading, spacing: 8) {
                                let current = HomeChatDestination(rawValue: homeChatDestinationRaw) ?? .family
                                Text(
                                    current == .family
                                    ? localizationManager.localized("main_home_chat_segment_family")
                                    : localizationManager.localized("main_ai_assistant_title")
                                )
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundColor(.secondaryGold)
                                
                                Text(
                                    current == .family
                                    ? localizationManager.localized("main_home_quick_entry_family")
                                    : localizationManager.localized("main_ai_assistant_greeting")
                                )
                                    .font(.system(size: 10))
                                    .foregroundColor(.white.opacity(0.9))
                                
                                TextField(
                                    current == .family
                                    ? localizationManager.localized("main_home_chat_placeholder_family")
                                    : localizationManager.localized("main_ai_assistant_placeholder"),
                                    text: $aiQuestion
                                )
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
                        }
                        .id("home_chat_segments_\(subscriptionManager.subscriptionDisplayEpoch)_\(tariffRowViewIdentity)")
                        .accessibilityIdentifier("main_nav_ai_assistant")
                        .padding(.horizontal, 20)
                        
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Основной контент приложения")
                .onAppear {
                    applyHomeChatDefaultModeIfNeeded()
                }
                // Production-safe: обновляем Family stats/тариф сразу после подтверждённого удаления участника
                .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("MainFamilyStatsForceRefresh"))) { _ in
                    // Debounce через orchestrator ViewModel (коалесим внешние триггеры)
                    mainViewModel.refreshFamilyMembersCountFromStorage()
                    mainViewModel.requestRefreshDebounced()
                    Task { await subscriptionManager.forceSync() }
                }
                .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyMembersUpdated"))) { _ in
                    // После сохранения списка участников на экране «Семья» обязательно перезапрашиваем `/api/family/stats`,
                    // иначе на главной остаётся старый totalMembers (типичный кейс: на Семье уже 1 участник, на главной «0»).
                    mainViewModel.requestRefreshDebounced()
                }
                .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyDevicesDidChange"))) { _ in
                    // Один коалесцированный проход дашборда (внутри уже есть GET /api/devices).
                    mainViewModel.requestRefreshDebounced()
                }
                // ✅ NEW: React to tariff changes from TariffsScreen, SubscriptionManager, or forceSync
                .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("SubscriptionUpdated"))) { notification in
                    if let level = notification.userInfo?["level"] as? String {
                        print("🔄 [MainScreen] Received SubscriptionUpdated notification: \(level)")
                    }
                    mainViewModel.requestRefreshDebounced()
                }
                .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("tariffPurchased"))) { notification in
                    print("🎉 [MainScreen] Received tariffPurchased notification - forcing tariff refresh")
                    if let tariffType = notification.userInfo?["tariff"] as? String {
                        print("   Tariff: \(tariffType)")
                    }
                    Task { await subscriptionManager.forceSync() }
                    mainViewModel.requestRefreshDebounced()
                }
                .onChange(of: subscriptionManager.currentSubscription) { _ in
                    mainViewModel.requestRefreshDebounced()
                }
                .id("main_lang_\(localizationManager.currentLanguage.rawValue)")
    }

    /// Стабильный идентификатор строки тарифа: при смене уровня/триала/языка SwiftUI пересобирает блок (важно для девайса после async `forceSync`).
    private var tariffRowViewIdentity: String {
        let level = subscriptionManager.getCurrentLevel()
        let trialOn = subscriptionManager.trialStatus?.isActive == true
        let lang = localizationManager.currentLanguage.rawValue
        return "\(level.rawValue)|trial:\(trialOn)|\(lang)"
    }
    
    private var currentTariffDisplayName: String {
        // ✅ FIXED: Use single source of truth from SubscriptionManager
        // getCurrentLevel() is more reliable than currentSubscription?.level
        let level = subscriptionManager.getCurrentLevel()
        let key: String
        switch level {
        case .trial: key = "tariffs_trial"
        case .free: key = "tariffs_free"
        case .personal: key = "tariffs_personal"
        case .family: key = "tariffs_family"
        case .premium: key = "tariffs_premium"
        }
        let localized = localizationManager.localized(key).trimmingCharacters(in: .whitespacesAndNewlines)
        if !localized.isEmpty { return localized }
        // Fallback: если словарь/ключ временно недоступен — не оставляем пустую подпись на главной.
        return level.displayName
    }

    // Helper to get tariff color for UI accent
    private var currentTariffColor: Color {
        let level = subscriptionManager.getCurrentLevel()
        switch level {
        case .free:
            return .secondaryGold
        case .trial:
            // Отличие от бесплатного: пробный период — бирюзово-золотой акцент.
            return Color(red: 0.22, green: 0.78, blue: 0.72)
        case .personal: return .blue
        case .family: return .purple
        case .premium: return .orange
        }
    }

    // Helper for SF Symbols icon based on current tariff level
    private func tariffIconForCurrentLevel() -> String {
        let level = subscriptionManager.getCurrentLevel()
        switch level {
        case .free, .trial: return "shield.fill"
        case .personal: return "person.fill"
        case .family: return "person.2.fill"
        case .premium: return "crown.fill"
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

    private func applyHomeChatDefaultModeIfNeeded() {
        let mode = HomeChatDefaultMode(rawValue: homeChatDefaultModeRaw) ?? .last
        switch mode {
        case .family:
            homeChatDestinationRaw = HomeChatDestination.family.rawValue
        case .ai:
            homeChatDestinationRaw = HomeChatDestination.ai.rawValue
        case .last:
            break
        case .smart:
            let now = Date().timeIntervalSince1970
            let familyIsFresh = (now - lastFamilyActivityAt) <= 10 * 60
            let aiIsFresh = (now - lastAIActivityAt) <= 10 * 60

            if familyIsFresh && (lastFamilyActivityAt >= lastAIActivityAt + 30) {
                homeChatDestinationRaw = HomeChatDestination.family.rawValue
            } else if aiIsFresh && (lastAIActivityAt >= lastFamilyActivityAt + 30) {
                homeChatDestinationRaw = HomeChatDestination.ai.rawValue
            }
        }
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
        case .networkUnavailable: return Color(red: 0.12, green: 0.43, blue: 0.84) // #1F6ED6
        }
    }
}

struct MainScreen_Previews: PreviewProvider {
    static var previews: some View {
        MainScreen()
            .environmentObject(MainViewModel())
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager.shared)
    }
}

struct Previews_01_MainScreen_LibraryContent: LibraryContentProvider {
    var views: [LibraryItem] {
        LibraryItem(/*@START_MENU_TOKEN@*/Text("•")/*@END_MENU_TOKEN@*/)
    }
}
