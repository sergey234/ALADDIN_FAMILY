import SwiftUI
import Foundation
import os.log
#if !targetEnvironment(simulator)
import Darwin
#endif

/// 🩺 CRASH LOGGING СИСТЕМА ДЛЯ PRODUCTION
/// Работает в RELEASE (TestFlight) в отличие от #if DEBUG
extension ALADDINApp {

    /// Настройка системы логирования крашей
    static func getMemoryUsage() -> String {
        #if !targetEnvironment(simulator)
        let processInfo = ProcessInfo.processInfo
        // ✅ КРИТИЧЕСКОЕ: Используем Double вместо Int для предотвращения переполнения
        let totalMemory = Double(processInfo.physicalMemory)
        guard totalMemory > 0 else { return "Memory: unavailable" }

        let memoryUsage = totalMemory / 1024.0 / 1024.0
        let uptime = processInfo.systemUptime

        // ✅ Безопасное форматирование без переполнения
        return String(format: "%.1f MB total, %.1f seconds uptime", memoryUsage, uptime)
        #else
        return "Simulator - no memory info"
        #endif
    }

    static func setupCrashLogging() {
        // Регистрируем обработчик неотловленных исключений
        NSSetUncaughtExceptionHandler { exception in
            let crashInfo = """
            🚨 CRASH DETECTED: \(exception.name.rawValue)
            Reason: \(exception.reason ?? "Unknown")
            Stack trace:
            \(exception.callStackSymbols.joined(separator: "\n"))
            Thread: \(Thread.current)
            Date: \(Date())
            """
            crashLog(crashInfo)
        }

        // Регистрируем обработчик сигналов
        signal(SIGABRT) { _ in crashLog("🚨 SIGNAL: SIGABRT received") }
        signal(SIGILL) { _ in crashLog("🚨 SIGNAL: SIGILL received") }
        signal(SIGSEGV) { _ in crashLog("🚨 SIGNAL: SIGSEGV received") }
        signal(SIGBUS) { _ in crashLog("🚨 SIGNAL: SIGBUS received") }
        signal(SIGTRAP) { _ in crashLog("🚨 SIGNAL: SIGTRAP received") }

        crashLog("🩺 Crash logging system initialized")
    }
}

/// Глобальная функция для логирования крашей (работает в RELEASE)
func crashLog(_ message: String) {
    let timestamp = Date().formatted(.iso8601)
    let logMessage = "[\(timestamp)] \(message)"

    // 🔥 КРИТИЧЕСКОЕ: Всегда логируем в консоль (видно в Xcode и device logs)
    print("🔥 CRASH_LOG: \(logMessage)")

    // 🔥 КРИТИЧЕСКОЕ: Логируем через os_log с высоким приоритетом
    os_log(.fault, log: .default, "🔥 CRASH_LOG: %{public}@", logMessage)

    // 🔥 КРИТИЧЕСКОЕ: Сохраняем в NSUserDefaults для чтения на устройстве
    // Это работает на реальном устройстве и сохраняется при краше
    let defaults = UserDefaults.standard
    let key = "crash_logs_array"
    var logs = defaults.array(forKey: key) as? [String] ?? []

    // Ограничиваем до 50 последних логов
    if logs.count >= 50 {
        logs.removeFirst()
    }
    logs.append(logMessage)

    defaults.set(logs, forKey: key)
    defaults.synchronize() // Принудительно сохраняем

    // Также сохраняем последний лог отдельно
    defaults.set(logMessage, forKey: "last_crash_log")
    defaults.synchronize()

    // В DEBUG режиме также сохраняем в файл для анализа
    #if DEBUG
    let fileManager = FileManager.default
    let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
    let logURL = documentsURL.appendingPathComponent("crash_log.txt")

    if let data = (logMessage + "\n").data(using: .utf8) {
        if fileManager.fileExists(atPath: logURL.path) {
            // Добавляем к существующему файлу
            if let fileHandle = try? FileHandle(forWritingTo: logURL) {
                fileHandle.seekToEndOfFile()
                fileHandle.write(data)
                fileHandle.closeFile()
            }
        } else {
            // Создаем новый файл
            try? data.write(to: logURL)
        }
    }
    #endif
}

// Функция awaitSafeAutoFixDebugTokens удалена - Keychain операции перенесены в onAppear

/// 🔥 Функция для чтения логов крашей из NSUserDefaults
func getCrashLogs() -> [String] {
    let defaults = UserDefaults.standard
    return defaults.array(forKey: "crash_logs_array") as? [String] ?? []
}

/// 🔥 Функция для получения последнего лога краша
func getLastCrashLog() -> String? {
    let defaults = UserDefaults.standard
    return defaults.string(forKey: "last_crash_log")
}

/// 👤 User Profile Manager
/// Singleton класс для управления профилем пользователя
/// Предоставляет быстрый доступ к данным пользователя из кеша
class UserProfileManager {
    static let shared = UserProfileManager()

    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard

    private let displayNameKey = "user_display_name"
    private let profileNameKey = "user_profile_name"
    private let emailKey = "user_email"
    private let lastUpdateKey = "user_profile_last_update"

    private init() {
        // Загружаем профиль при инициализации
        loadProfileInBackground()
    }

    // MARK: - Public Methods

    /// Получить отображаемое имя пользователя
    var displayName: String {
        if let cachedName = userDefaults.string(forKey: displayNameKey),
           !cachedName.isEmpty {
            return cachedName
        }
        return NSLocalizedString("child_interface_default_name", comment: "Default user name")
    }

    /// Получить email пользователя
    var email: String? {
        return userDefaults.string(forKey: emailKey)
    }

    /// Проверить, загружен ли профиль
    var isProfileLoaded: Bool {
        return userDefaults.string(forKey: displayNameKey) != nil
    }

    /// Получить время последнего обновления профиля
    var lastUpdateTime: Date? {
        if let timestamp = userDefaults.double(forKey: lastUpdateKey) as Double?, timestamp > 0 {
            return Date(timeIntervalSince1970: timestamp)
        }
        return nil
    }

    /// Загрузить профиль из API и сохранить в кеш
    func loadProfile(completion: ((Bool) -> Void)? = nil) {
        apiService.getUserProfile { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case .success(let profile):
                    // Сохраняем данные в кеш
                    self.saveProfileToCache(profile)
                    print("✅ User profile loaded and cached: \(profile.name)")
                    completion?(true)

                case .failure(let error):
                    print("⚠️ Failed to load user profile: \(error.localizedDescription)")
                    completion?(false)
                }
            }
        }
    }

    /// Очистить кеш профиля
    func clearProfileCache() {
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        userDefaults.synchronize()
        print("🗑️ User profile cache cleared")
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        // Загружаем профиль в фоне при инициализации
        // Если профиль старше 24 часов, обновляем
        if shouldRefreshProfile() {
            DispatchQueue.global(qos: .background).async { [weak self] in
                self?.loadProfile()
            }
        }
    }

    private func shouldRefreshProfile() -> Bool {
        guard let lastUpdate = lastUpdateTime else {
            return true // Нет данных, нужно загрузить
        }

        let twentyFourHours: TimeInterval = 24 * 60 * 60
        return Date().timeIntervalSince(lastUpdate) > twentyFourHours
    }

    private func saveProfileToCache(_ profile: UserProfile) {
        userDefaults.set(profile.name, forKey: displayNameKey)
        userDefaults.set(profile.name, forKey: profileNameKey) // Для совместимости
        userDefaults.set(profile.email, forKey: emailKey)
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        userDefaults.synchronize()
    }
}

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    // ✅ Добавляем LocalizationManager
    @StateObject private var localizationManager = LocalizationManager()
    @AppStorage("selected_theme") private var selectedTheme: String = "system"
    // ✅ ИСПРАВЛЕНИЕ: Отслеживаем состояние приложения для предотвращения сброса навигации
    @Environment(\.scenePhase) private var scenePhase
    // Убрали @AppStorage для онбординга
    // private var hasCompletedOnboarding: Bool = false // больше не используется
    
    init() {
        // 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБИРАЕМ CRASH LOGGING ИЗ INIT!
        // setupCrashLogging() вызывает краш в TestFlight из-за рекурсии в обработчиках!
        // Будем инициализировать crash logging позже, в .onAppear

        // ✅ БЕЗОПАСНО: Только print() без crashLog() - не вызывает рекурсию
        print("🔴 ALADDINApp.init: ========== НАЧАЛО ИНИЦИАЛИЗАЦИИ ПРИЛОЖЕНИЯ ==========")
        print("🔴 ALADDINApp.init: Thread.isMainThread = \(Thread.isMainThread)")
        print("🔴 ALADDINApp.init: Время: \(Date())")

        // 🚨 НЕ БЕЗОПАСНО: Thread.callStackSymbols может вызвать краш
        // let stackTrace = Thread.callStackSymbols.prefix(5).joined(separator: "\n")
        // print("🔴 ALADDINApp.init: Stack trace (первые 5):\n\(stackTrace)")

        print("🚀 ALADDINApp: Начало инициализации приложения")
        // ✅ ИСПРАВЛЕНИЕ: В init() НЕ используем @StateObject, они еще не созданы!
        // Вся логика инициализации перенесена в .onAppear
        if ProcessInfo.processInfo.environment["RESET_ONBOARDING"] == "1" {
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            #if DEBUG
            print("🌍 RESET_ONBOARDING активирован — ключ сброшен")
            #endif
        }
        
#if DEBUG
        // 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ВСЕ Keychain операции убраны из init()!
        // Они вызывают deadlock в TestFlight. Перенесены в onAppear.
        print("⚠️ DEBUG: Keychain operations moved to onAppear to prevent deadlock")

        // ✅ ИСПРАВЛЕНИЕ: Проверяем, нужно ли создавать debug токены
        // Если установлена переменная окружения SKIP_DEBUG_TOKENS=1, пропускаем создание debug токенов
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Тримируем значение, чтобы убрать возможные пробелы
        let skipDebugTokensRaw = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
        let skipDebugTokens = skipDebugTokensRaw.trimmingCharacters(in: .whitespacesAndNewlines) == "1"

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если есть AUTO_LOGIN_EMAIL, автоматически считаем, что нужно пропустить debug токены
        let hasAutoLogin = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"] != nil &&
                          !ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"]!.isEmpty

        _ = skipDebugTokens || hasAutoLogin // Не используется, но оставляем для совместимости

        // 🚨 Keychain операции убраны из init() - перенесены в onAppear для безопасности
        print("⚠️ DEBUG: Keychain operations moved to onAppear to prevent deadlock")
        
        // ✅ АВТОМАТИЧЕСКИЙ ЛОГИН: Если установлены переменные окружения, выполняем логин автоматически
        // ✅ ПРОДАКШЕН: Проверяем сохраненные credentials для автоматического логина
        DispatchQueue.global(qos: .utility).async {
            // ✅ ДИАГНОСТИКА: Проверяем переменные окружения
            let email = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"]
            let password = ProcessInfo.processInfo.environment["AUTO_LOGIN_PASSWORD"]

            // ✅ ПРОДАКШЕН: Проверяем сохраненные credentials
            let savedEmail = UserDefaults.standard.string(forKey: "saved_login_email")
            let savedPassword = UserDefaults.standard.string(forKey: "saved_login_password")
            let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")
            
            print("🔍 ALADDINApp: Проверка переменных окружения...")
            let skipDebugTokensValue = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
            let skipDebugTokensTrimmed = skipDebugTokensValue.trimmingCharacters(in: .whitespacesAndNewlines)
            let skipDebugTokensIsSet = skipDebugTokensTrimmed == "1"
            print("   - AUTO_LOGIN_EMAIL: \(email != nil ? "✅ установлен (\(email?.prefix(3) ?? "")...)" : "❌ не установлен")")
            print("   - AUTO_LOGIN_PASSWORD: \(password != nil ? "✅ установлен (\(password?.count ?? 0) символов)" : "❌ не установлен")")
            print("   - SKIP_DEBUG_TOKENS: \(skipDebugTokensValue.isEmpty ? "❌ НЕ УСТАНОВЛЕН" : "✅ установлен = '\(skipDebugTokensTrimmed)' (\(skipDebugTokensIsSet ? "активен" : "не активен"))")")
            
            // ✅ ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА: Выводим все переменные окружения, начинающиеся с AUTO_ или SKIP_
            let allEnvVars = ProcessInfo.processInfo.environment
            let relevantVars = allEnvVars.keys.filter { $0.hasPrefix("AUTO_") || $0.hasPrefix("SKIP_") }
            if !relevantVars.isEmpty {
                print("   - Все найденные переменные: \(relevantVars.joined(separator: ", "))")
                for varName in relevantVars {
                    let value = allEnvVars[varName] ?? ""
                    if varName.contains("PASSWORD") {
                        print("     • \(varName) = '\(value.count) символов'")
                    } else {
                        print("     • \(varName) = '\(value)'")
                    }
                }
            } else {
                print("   - ⚠️ ВНИМАНИЕ: Не найдено ни одной переменной окружения с префиксом AUTO_ или SKIP_!")
                print("   - Проверьте, что переменные установлены в правильной схеме (Run)")
            }
            
            // ✅ ПРОДАКШЕН: Проверяем условия для автоматического логина
            let shouldAutoLogin = (email != nil && password != nil && !email!.isEmpty && !password!.isEmpty) ||
                                 (autoLoginEnabled && savedEmail != nil && savedPassword != nil)

            if shouldAutoLogin {
                let loginEmail = email ?? savedEmail!
                let loginPassword = password ?? savedPassword!

                print("🔐 ALADDINApp: Автоматический логин...")
                print("   - Email: \(loginEmail)")
                print("   - Тип: \(email != nil ? "переменные окружения" : "сохраненные credentials")")

                // Небольшая задержка, чтобы приложение успело запуститься
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                    performRealLogin(email: loginEmail, password: loginPassword) { success in
                        if success {
                            print("✅ ALADDINApp: Автоматический логин успешен!")

                            // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
                            let keychain = KeychainManager.shared
                            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
                            if let token = keychain.loadString(forKey: .authToken) {
                                print("✅ ALADDINApp: Токен подтвержден в Keychain (длина: \(token.count))")
                            } else {
                                print("⚠️ ALADDINApp: ВНИМАНИЕ! Токен не найден в Keychain после успешного логина!")
                            }
                        } else {
                            print("❌ ALADDINApp: Ошибка автоматического логина")
                            print("   - Проверьте правильность email и password")
                            print("   - Проверьте доступность сервера")
                            // В продакшене не показываем детали для безопасности
                            #if DEBUG
                            print("   - Проверьте endpoint /auth/login на сервере")
                            #endif
                        }
                    }
                }
            } else {
                #if DEBUG
                if email == nil || password == nil || email!.isEmpty || password!.isEmpty {
                    print("⚠️ ALADDINApp: Переменные окружения для автоматического логина не установлены")
                    print("   - Установите AUTO_LOGIN_EMAIL и AUTO_LOGIN_PASSWORD в Scheme → Run → Arguments → Environment Variables")
                }
                #endif
                print("ℹ️ ALADDINApp: Автоматический логин не настроен - пользователь должен войти вручную")
            }
        }
        
        print("🔴 ALADDINApp.init: ========== ЗАВЕРШЕНИЕ init() ==========")
        print("🔴 ALADDINApp.init: Время завершения: \(Date())")
#endif
    }
    
    var body: some Scene {
        // ✅ КРИТИЧЕСКОЕ: Логи в самом начале body - ПЕРВАЯ СТРОКА
        let _ = {
            print("🔴 ALADDINApp.body: ========== НАЧАЛО BODY ==========")
            print("🔴 ALADDINApp.body: Thread.isMainThread = \(Thread.isMainThread)")
            print("🔴 ALADDINApp.body: navigationManager = \(navigationManager)")
            print("🔴 ALADDINApp.body: localizationManager = \(localizationManager)")
            print("🔴 ALADDINApp.body: currentScreen = \(navigationManager.currentScreen)")
        }()
        
        return WindowGroup {
            // ✅ КРИТИЧЕСКОЕ: Логи перед NavigationView
            let _ = {
                print("🔴 ALADDINApp.body: Создание WindowGroup и NavigationView")
            }()
            
            // КРИТИЧНО: NavigationView для работы навигации
            let _ = {
                print("🔴 ALADDINApp.body: Создание NavigationView...")
            }()
            
            NavigationView {
                // ✅ КРИТИЧНО: Используем AnyView для каждого case - это заставит SwiftUI пересчитать
                let _ = {
                    print("🔴 ALADDINApp.body: Внутри NavigationView, currentScreen = \(navigationManager.currentScreen)")
                }()
                
                Group {
                    let _ = {
                        print("🔴 ALADDINApp.body: Внутри Group, начинаем switch по currentScreen = \(navigationManager.currentScreen)")
                    }()
                    
                    switch navigationManager.currentScreen {
                    case .main:
                        AnyView(MainScreen().id("main").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .family:
                        AnyView(FamilyScreen().id("family").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .networkProtection:
                        AnyView(NetworkProtectionScreen().id("network_protection").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .analytics:
                        AnyView(AnalyticsScreen().id("analytics").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .settings:
                        // ✅ [REVERT] SettingsScreen с EnvironmentObject через модификатор
                        // Modal views требуют EnvironmentObject через .environmentObject()
                        AnyView(SettingsScreen()
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .id("settings")
                            .onAppear {
                                print("🚨 [FINAL_TEST] SettingsScreen created with EnvironmentObject fixes")
                                print("🚨 [FINAL_TEST] Thread: \(Thread.isMainThread)")
                                print("🚨 [FINAL_TEST] Build 62 EnvironmentObject fixes active!")
                            })
                    case .settingsDiagnostic:
                        // 🚨 [CRASH_DIAG] ТЕСТИРОВАНИЕ SettingsDiagnostic screen
                        AnyView(SettingsScreenDiagnostic()
                            .id("settingsDiagnostic")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                print("🚨 [CRASH_DIAG] SettingsDiagnostic screen appeared successfully!")
                            })

                    case .settingsTest:
                        // ✅ [REVERT] SettingsScreen с EnvironmentObject
                        AnyView(SettingsScreen()
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .id("settingsTest")
                            .onAppear {
                                print("🚨 [CRASH_DIAG] About to create FULL SettingsScreen with computed properties")
                                print("🚨 [CRASH_DIAG] FULL SettingsScreen View created with computed properties")
                                print("🚨 [CRASH_DIAG] settingsTest screen appeared")
                            })

                    case .settingsFallback:
                        // 🚨 [CRASH_DIAG] FALLBACK SettingsScreen без сложной логики
                        AnyView(SettingsScreenFallback())

                    case .settingsTestSuite:
                        // ✅ [FIX 5] Безопасное создание SettingsTestSuiteView
                        AnyView(SettingsTestSuiteView()
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .aiAssistant:
                        AnyView(AIAssistantScreen().id("aiAssistant").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .parentalControl:
                        AnyView(ParentalControlScreen()
                            .id("parentalControl")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ParentalControlScreen отображён")
                                #endif
                            })
                    case .childInterface:
                        AnyView(ChildInterfaceScreen()
                            .id("childInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ChildInterfaceScreen отображён")
                                #endif
                            })
                    case .securityEducation:
                        AnyView(SecurityEducationScreen()
                            .id("securityEducation")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: SecurityEducationScreen отображён")
                                #endif
                            })
                    case .elderlyInterface:
                        AnyView(ElderlyInterfaceScreen()
                            .id("elderlyInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ElderlyInterfaceScreen отображён")
                                #endif
                            })
                    case .tariffs:
                        // 🚧 ВРЕМЕННО СКРЫТО: Экран тарифов временно недоступен
                        // TODO: ВОССТАНОВИТЬ ПОСЛЕ ТЕСТИРОВАНИЯ
                        // AnyView(TariffsScreen().id("tariffs").environmentObject(navigationManager).environmentObject(localizationManager))
                        AnyView(
                            VStack(spacing: 20) {
                                Text("💎")
                                    .font(.system(size: 60))
                                Text("Тарифы")
                                    .font(.title)
                                    .fontWeight(.bold)
                                Text("Скоро будет доступно")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(LinearGradient.backgroundGradient)
                            .id("tariffs_placeholder")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                        )
#if !APP_STORE_BUILD
                    case .paymentQR:
                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем AnyView для отложенного создания View
                        // Это предотвращает попытку SwiftUI вычислить body до готовности данных
                        if let tariff = navigationManager.selectedTariffForPayment {
                            // ✅ Дополнительная проверка валидности тарифа
                            if !tariff.id.isEmpty && !tariff.title.isEmpty {
                                // ✅ Обертка в AnyView для безопасности инициализации
                                AnyView(
                                    PaymentQRScreen(tariff: tariff) {
                                        print("🔍 ALADDINApp: onPaymentCompleted вызван")
                                        navigationManager.beginManualPaymentQRClose()
                                        navigationManager.goBack(reason: "PaymentQR.onPaymentCompleted")
                                        navigationManager.selectedTariffForPayment = nil
                                    }
                                    .id("paymentQR")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                    .onAppear { 
                                        print("🚨 PaymentQRScreen открыт через NavigationLink!")
                                        print("🚨 Tariff ID: \(tariff.id)")
                                    }
                                )
                            } else {
                                // ✅ Fallback если тариф невалиден
                                AnyView(
                                    VStack(spacing: 20) {
                                        Text("Ошибка: тариф невалиден")
                                            .font(.headline)
                                        Text("ID: \(tariff.id.isEmpty ? "пусто" : tariff.id)")
                                        Text("Title: \(tariff.title.isEmpty ? "пусто" : tariff.title)")
                                        Button("Назад") {
                                                navigationManager.beginManualPaymentQRClose()
                                                navigationManager.goBack(reason: "PaymentQR.invalidTariffFallback")
                                            navigationManager.selectedTariffForPayment = nil
                                        }
                                    }
                                    .padding()
                                    .id("paymentQR_error_invalid")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                )
                            }
                        } else {
                            // ✅ Fallback если тариф не передан
                            AnyView(
                                VStack(spacing: 20) {
                                    Text("Ошибка: тариф не выбран")
                                        .font(.headline)
                                    Button("Назад") {
                                            navigationManager.beginManualPaymentQRClose()
                                            navigationManager.goBack(reason: "PaymentQR.nilTariffFallback")
                                    }
                                }
                                .padding()
                                .id("paymentQR_error_nil")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                            )
                        }
#endif
                    case .activationCode:
                        AnyView(
                            ActivationCodeScreen()
                                .id("activationCode")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .profile:
                        AnyView(ProfileScreen()
                            .id("profile")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear { 
                                print("🔍 DEBUG ALADDINApp: ProfileScreen отображён!")
                                print("🔍 DEBUG ALADDINApp: currentScreen = \(navigationManager.currentScreen)")
                            })
                    case .notifications:
                        AnyView(NotificationsScreen().id("notifications").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .privacyPolicy:
                        AnyView(PrivacyPolicyScreen().id("privacyPolicy").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .termsOfService:
                        AnyView(TermsOfServiceScreen().id("termsOfService").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .onboarding:
                        // ✅ КРИТИЧЕСКОЕ: Логирование перед созданием OnboardingScreen
                        let _ = {
                            print("🔴 ALADDINApp.body: Создание OnboardingScreen - НАЧАЛО")
                            print("🔴 ALADDINApp.body: navigationManager = \(navigationManager)")
                            print("🔴 ALADDINApp.body: localizationManager = \(localizationManager)")
                            print("🔴 ALADDINApp.body: Thread.isMainThread = \(Thread.isMainThread)")
                        }()
                        AnyView(OnboardingScreen()
                            .id("onboarding")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                print("🔴 ALADDINApp.body: OnboardingScreen onAppear вызван")
                            })
                    case .devices:
                        AnyView(DevicesScreen().id("devices").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .referral:
                        AnyView(ReferralScreen().id("referral").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .deviceDetail:
                        AnyView(DeviceDetailScreen(
                            device: Device(
                                name: "iPhone 13",
                                owner: "Пользователь",
                                type: .iphone,
                                status: .protected,
                                lastActive: "Только что"
                            )
                        )
                        .id("deviceDetail")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .familyChat:
                        AnyView(FamilyChatScreen().id("familyChat").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .support:
                        AnyView(SupportScreen().id("support").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .addMemberOptions:
                        AnyView(AddMemberOptionsScreen().id("addMemberOptions").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childRewards:
                        AnyView(ChildRewardsScreen().id("childRewards").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .familyTournament:
                        AnyView(FamilyTournamentView().id("familyTournament").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .unicornPet:
                        AnyView(UnicornPetView().id("unicornPet").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .youngDefender:
                        AnyView(YoungDefenderView().id("youngDefender").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .familyProtector:
                        AnyView(FamilyProtectorView().id("familyProtector").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childGoalEditor:
                        AnyView(ChildGoalEditorView().id("childGoalEditor").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .gamesParentalControl:
                        AnyView(GamesParentalControlView().id("gamesParentalControl").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .languageSettings:
                        AnyView(LanguageSettingsScreen()
                            .id("languageSettings")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .notificationSettings:
                        AnyView(NotificationSettingsScreen().id("notificationSettings").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .widgetConfiguration:
                        AnyView(WidgetConfigurationScreen().id("widgetConfiguration").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .mainWithRegistration:
                        AnyView(MainScreenWithRegistration(
                            registrationVM: FamilyRegistrationViewModel()
                        )
                        .id("mainWithRegistration")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .childContent:
                        AnyView(ChildContentScreen(
                            category: "Игры",
                            ageGroup: .school
                        )
                        .id("childContent")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsModal:
                        AnyView(RewardsModalView(
                            unicornBalance: .constant(245),
                            weeklyRewarded: .constant(128),
                            weeklyPunished: .constant(45)
                        )
                        .id("rewardsModal")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsQuickModal:
                        AnyView(RewardsQuickModal(unicornBalance: .constant(245))
                            .id("rewardsQuickModal")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .threatProtection:
                        AnyView(ThreatProtectionScreen().id("threatProtection").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .threatProtectionSettings:
                        AnyView(ThreatProtectionSettingsScreen().id("threatProtectionSettings").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .iotSecurity:
                        // TODO: Создать IoTSecurityScreen или использовать существующий
                        AnyView(ThreatProtectionScreen().id("iotSecurity").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .advancedProtection:
                        AnyView(AdvancedProtectionSettingsScreen().id("advancedProtection").environmentObject(navigationManager).environmentObject(localizationManager))
                    }
                }
                .id("screen_\(navigationManager.currentScreen.rawValue)")
                .navigationBarHidden(true)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            // КРИТИЧНО: Передача NavigationManager через EnvironmentObject
            .environmentObject(navigationManager)
            // ✅ Передаём LocalizationManager через EnvironmentObject
            .environmentObject(localizationManager)
            // ✅ Применяем локализацию через environment
            .environment(\.locale, localizationManager.locale)
            // ✅ КРИТИЧНО: Пересоздаём NavigationView при изменении currentScreen
            .id("nav_\(navigationManager.currentScreen.rawValue)_\(localizationManager.currentLanguage.rawValue)")
            // ✅ Инициализация навигации при первом появлении
            .onAppear {
                // ✅ КРИТИЧЕСКОЕ: Сначала безопасно инициализируем crash logging
                // Теперь все @StateObject созданы, можно безопасно использовать crashLog()
                ALADDINApp.setupCrashLogging()
                crashLog("🩺 Crash logging system initialized safely in onAppear")

                // 🚨 ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА ДЛЯ TESTFLIGHT
                crashLog("📱 DEVICE INFO: iOS \(UIDevice.current.systemVersion), Model: \(UIDevice.current.model)")
                crashLog("🧵 THREAD INFO: Main thread = \(Thread.isMainThread), Quality: \(Thread.current.qualityOfService.rawValue)")
                crashLog("📊 MEMORY INFO: Available = \(ALADDINApp.getMemoryUsage()) MB")
                crashLog("🔄 APP STATE: Navigation screen = \(navigationManager.currentScreen.rawValue)")

                // ✅ КРИТИЧЕСКОЕ: Логи в самом начале onAppear
                crashLog("🔴 ALADDINApp.onAppear: ========== НАЧАЛО onAppear ==========")
                crashLog("🔴 ALADDINApp.onAppear: Thread.isMainThread = \(Thread.isMainThread)")
                crashLog("🔴 ALADDINApp.onAppear: navigationManager = \(navigationManager)")
                crashLog("🔴 ALADDINApp.onAppear: localizationManager = \(localizationManager)")
                crashLog("🔴 ALADDINApp.onAppear: currentScreen = \(navigationManager.currentScreen)")

                let navManager = navigationManager
                let locManager = localizationManager
                // ✅ БЕЗОПАСНО: Теперь можно делать Keychain операции - приложение уже инициализировано
                crashLog("🔴 ALADDINApp.onAppear: Безопасная инициализация Keychain операций...")
                #if DEBUG
                Task { @MainActor in
                    do {
                        try await Task.sleep(nanoseconds: 200_000_000) // 0.2 секунды задержки
                        KeychainAutoRecoveryService.repairTokensIfNeeded()
                        crashLog("✅ Keychain repair completed safely")
                    } catch {
                        crashLog("⚠️ Keychain repair failed safely: \(error.localizedDescription)")
                    }
                }
                #else
                crashLog("ℹ️ RELEASE: Keychain repair skipped (only available in DEBUG)")
                #endif

                crashLog("🔴 ALADDINApp.onAppear: Вызов initializeNavigation...")
                initializeNavigation(navigationManager: navManager, localizationManager: locManager)
                crashLog("🔴 ALADDINApp.onAppear: initializeNavigation завершен")
            }
            // ✅ ИСПРАВЛЕНИЕ: Упрощенная обработка возврата из фона - без лишних проверок
            .onChange(of: scenePhase) { newPhase in
                // ✅ КРИТИЧЕСКОЕ: УБРАНЫ crashLog() чтобы предотвратить рекурсию
                // crash logging в onChange может вызвать бесконечную рекурсию
                print("🔄 SCENE PHASE: изменился на \(newPhase)")

                if newPhase == .active {
                    // Приложение стало активным (вернулись из Safari/фона)
                    print("🔄 Возврат из фона: приложение активно, экран = \(navigationManager.currentScreen)")
                    // НЕ вызываем initializeNavigation - это может вызвать двойную загрузку
                } else if newPhase == .background {
                    print("🔄 Приложение ушло в фон")
                } else if newPhase == .inactive {
                    print("🔄 Приложение стало неактивным")
                }
            }
            // 🌓 ПРИМЕНЯЕМ ТЕМУ
            .preferredColorScheme(getPreferredColorScheme())
        }
    }  // ✅ Закрывает body: some Scene
    
    // MARK: - Theme Helper
    
    private func getPreferredColorScheme() -> ColorScheme? {
        switch selectedTheme {
        case "light": return .light
        case "dark": return .dark
        case "system": return nil // nil = системная тема
        default: return nil
        }
    }
    
    // MARK: - Инициализация навигации
    
    /// ✅ Инициализация навигации при первом запуске приложения
    /// Вызывается в .onAppear, когда все @StateObject уже созданы
    private static var hasInitialized = false
    
    private func initializeNavigation(navigationManager: NavigationManager, localizationManager: LocalizationManager) {
        // ✅ КРИТИЧЕСКОЕ: Логи в самом начале initializeNavigation
        print("🔴 ALADDINApp.initializeNavigation: ========== НАЧАЛО ==========")
        print("🔴 ALADDINApp.initializeNavigation: Thread.isMainThread = \(Thread.isMainThread)")
        print("🔴 ALADDINApp.initializeNavigation: hasInitialized = \(ALADDINApp.hasInitialized)")
        
        // ✅ КРИТИЧНО: ПЕРВЫЙ ЗАПУСК - СБРАСЫВАЕМ ВСЕ СОСТОЯНИЕ
        if !ALADDINApp.hasInitialized {
            print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
            // Принудительный сброс онбординга для первого запуска
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            UserDefaults.standard.synchronize()
        }

        // ✅ Используем статический флаг для предотвращения повторной инициализации
        if ALADDINApp.hasInitialized {
            print("🛠️ [ALADDINApp.initializeNavigation] Уже инициализировано, пропускаем")
            return
        }
        
        ALADDINApp.hasInitialized = true
        print("🛠️ [ALADDINApp.initializeNavigation] Начинаем инициализацию...")
        
        // ✅ Активируем бесплатный тариф при первом запуске
        let storeManager = StoreManager()
        if !storeManager.hasFreeTariff && !storeManager.hasActiveSubscription() {
            storeManager.activateFreeTariff()
            print("✅ First launch: Free tariff activated automatically")
        }

        // ✅ ЗАГРУЖАЕМ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
        // UserProfileManager инициализируется автоматически при первом обращении
        // и загружает профиль в фоне
        _ = UserProfileManager.shared
        print("✅ UserProfileManager initialized and profile loading started")
        
        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        print("🛠️ [ALADDINApp.initializeNavigation] onboardingDone = \(onboardingDone)")
        
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Всегда начинаем с онбординга при первом запуске
        if !onboardingDone {
            // Первый запуск - всегда показываем онбординг
            print("🔴 ONBOARDING: Первый запуск - показываем онбординг")
                navigationManager.currentScreen = .onboarding
        } else {
            // Онбординг пройден - переходим на main
            print("🟢 ONBOARDING: Пройден - переходим на главный экран")
                navigationManager.currentScreen = .main
        }
    }
    
    // MARK: - Проверка роли при запуске
    
    // ✅ ОТКЛЮЧЕНО: Автоматическое перенаправление по ролям
    // Пользователь сам выбирает экран через главное меню
    private func checkAndNavigateToUserInterface(navigationManager: NavigationManager) {
        // Остаёмся на главной странице
        print("✅ Остаёмся на главной странице")
        navigationManager.currentScreen = .main
    }
    
    /// Автоматически проверяет и удаляет debug токены при запуске
    /// Возвращает true, если были обнаружены и удалены debug токены
    private static func autoFixDebugTokensIfNeeded() -> Bool {
        let keychain = KeychainManager.shared
        
        // Проверяем access token
        var isDebugToken = false
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let accessToken = keychain.loadString(forKey: .authToken) {
            // Проверяем признаки debug токена
            if accessToken.contains(".debugsignature") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (содержит .debugsignature)")
            } else if accessToken.count == 140 && accessToken.contains("eyJhbGciOi") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (длина 140)")
            }
        }
        
        // Проверяем refresh token
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let refreshToken = keychain.loadString(forKey: .refreshToken) {
            if refreshToken == "debug-refresh-token" {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug refresh token")
            }
        }
        
        // Если обнаружены debug токены - удаляем их
        if isDebugToken {
            print("🔧 ALADDINApp: Автоматически удаляем debug токены...")
            keychain.delete(forKey: .authToken)
            keychain.delete(forKey: .refreshToken)
            AppConfig.authToken = nil
            UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
            print("✅ ALADDINApp: Debug токены удалены!")
            print("⚠️ ALADDINApp: ВАЖНО! Выполните реальный логин через Debug Console:")
            print("   performRealLogin(email: \"ваш_email\", password: \"ваш_пароль\") { _ in }")
            return true
        } else {
            print("✅ ALADDINApp: Debug токены не обнаружены")
            return false
        }
    }
}

#if DEBUG
private enum DebugAuthTokenSeeder {
    // ✅ ИСПРАВЛЕНИЕ: Убираем debug токены, которые не принимает сервер
    // Вместо этого приложение будет работать в демо режиме
    private static let demoAccessToken = ""
    private static let demoRefreshToken = ""
    
    static func seedIfNeeded() {
        // ✅ ИСПРАВЛЕНИЕ: Не создаем debug токены - приложение работает в демо режиме
        #if DEBUG
        print("ℹ️ DEBUG: Debug токены отключены - приложение работает в демо режиме")
        print("ℹ️ DEBUG: Для тестирования API используйте performRealLogin() в Debug Console")
        #endif
    }
}
#endif

#if DEBUG
// MARK: - Debug Console Functions

func clearDebugTokens() -> Bool {
    let keychain = KeychainManager.shared
    keychain.delete(forKey: .authToken)
    keychain.delete(forKey: .refreshToken)
    AppConfig.authToken = nil
    UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
    print("✅ Debug токены удалены. Выполните реальный логин.")
    return true
}

func performRealLogin(email: String, password: String, completion: @escaping (Bool) -> Void) {
    print("🔐 Выполняем логин для \(email)...")
    print("   - Endpoint: \(AppConfig.Endpoint.login)")
    print("   - Base URL: \(AppConfig.apiBaseURL)")
    print("   - Full URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
    
    APIService.shared.login(email: email, password: password) { result in
        switch result {
        case .success(_):
            print("✅ Логин успешен! Токены сохранены в Keychain.")
            
            // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
            let keychain = KeychainManager.shared
            var tokensSaved = true
            
            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
            if let accessToken = keychain.loadString(forKey: .authToken) {
                print("   - Access token сохранен (длина: \(accessToken.count))")
            } else {
                print("   - ⚠️ Access token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if let refreshToken = keychain.loadString(forKey: .refreshToken) {
                print("   - Refresh token сохранен (длина: \(refreshToken.count))")
            } else {
                print("   - ⚠️ Refresh token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if tokensSaved {
                print("✅ Теперь тумблеры должны работать!")

                // 🔄 Синхронизация демо-настроек после логина
                syncDemoSettingsToServer()

                completion(true)
            } else {
                print("❌ Токены не были сохранены в Keychain!")
                completion(false)
            }
        case .failure(let error):
            print("❌ Ошибка логина: \(error.localizedDescription)")
            
            // ✅ ДЕТАЛЬНАЯ ДИАГНОСТИКА ОШИБКИ
            if let networkError = error as? NetworkError {
                switch networkError {
                case .invalidStatusCode(let code):
                    print("   - HTTP Status: \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .httpError(let code):
                    print("   - HTTP Error \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .notFound(let message):
                    print("   - ⚠️ Endpoint не найден: \(message ?? "Not Found")")
                    print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                case .unauthorized(let message):
                    print("   - ⚠️ Неверные credentials: \(message ?? "Unauthorized")")
                case .forbidden(let message):
                    print("   - ⚠️ Доступ запрещен: \(message ?? "Forbidden")")
                case .invalidURL:
                    print("   - ⚠️ Неверный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                default:
                    print("   - Тип ошибки: \(networkError)")
                }
            }
            
            print("⚠️ Проверьте:")
            print("   1. Правильность email и password")
            print("   2. Доступность сервера: \(AppConfig.apiBaseURL)")
            print("   3. Правильность endpoint: \(AppConfig.Endpoint.login)")
            print("   4. Полный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
            
            completion(false)
        }
    }
}

/// Проверяет, являются ли текущие токены debug токенами
/// Использование в Debug Console: checkIfTokensAreDebug()
func checkIfTokensAreDebug() -> Bool {
    let keychain = KeychainManager.shared
    var isDebug = false
    
    // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
    if let accessToken = keychain.loadString(forKey: .authToken) {
        if accessToken.contains(".debugsignature") || (accessToken.count == 140 && accessToken.contains("eyJhbGciOi")) {
            print("⚠️ Обнаружен debug access token")
            isDebug = true
        }
    }
    
    if let refreshToken = keychain.loadString(forKey: .refreshToken) {
        if refreshToken == "debug-refresh-token" {
            print("⚠️ Обнаружен debug refresh token")
            isDebug = true
        }
    }
    
    if isDebug {
        print("❌ Токены являются debug токенами. Выполните: clearDebugTokens() и затем performRealLogin()")
    } else {
        print("✅ Токены не являются debug токенами")
    }
    
    return isDebug
}

/// 🔄 Синхронизация демо-настроек на сервер после авторизации
func syncDemoSettingsToServer() {
    print("🔄 Начинаем синхронизацию демо-настроек на сервер...")

    let demoComponentIds = [
        "crash_detection_agent",
        "roadside_assistance_agent",
        "incident_response_agent",
        "emergency_response_bot",
        "emergency_event_manager",
        "phishing_protection_agent",
        "malware_detection_agent",
        "mobile_security_agent",
        "network_security_agent",
        "password_security_agent"
    ]

    Task {
        for componentId in demoComponentIds {
            let demoKey = "demo_\(componentId)"
            if let demoValue = UserDefaults.standard.object(forKey: demoKey) as? Bool {
                print("   📤 Синхронизируем \(componentId): \(demoValue)")

                do {
                    try await APIService.shared.updateComponentStatus(
                        componentId: componentId,
                        isEnabled: demoValue
                    )
                    print("   ✅ \(componentId) синхронизирован")

                    // Удаляем демо-настройку после успешной синхронизации
                    UserDefaults.standard.removeObject(forKey: demoKey)
                } catch {
                    print("   ❌ Ошибка синхронизации \(componentId): \(error.localizedDescription)")
                }
            } else {
                print("   ⏭️ Нет демо-настройки для \(componentId)")
            }
        }

        print("✅ Синхронизация демо-настроек завершена")
    }
}
#endif
