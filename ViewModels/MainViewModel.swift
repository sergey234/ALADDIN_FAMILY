import SwiftUI
import Combine

// Master Logger for business logic logging
private let logger = MasterLogger.shared
// Visual Logger for on-screen display
private let visualLogger = VisualLogger.shared

// MARK: - Family Protection Status

enum FamilyProtectionStatus: String, Codable {
    case active
    case paused
    case attention
    case critical
    
    init(apiValue: String?) {
        self = FamilyProtectionStatus(rawValue: apiValue?.lowercased() ?? "") ?? .active
    }
    
    var iconName: String {
        switch self {
        case .active: return "checkmark.circle.fill"
        case .paused: return "pause.circle.fill"
        case .attention: return "exclamationmark.triangle.fill"
        case .critical: return "xmark.octagon.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .active: return Color(red: 0.05, green: 0.8, blue: 0.42) // #0CCE6B
        case .paused: return Color(red: 0.6, green: 0.63, blue: 0.68) // #9AA0AE
        case .attention: return Color(red: 1.0, green: 0.62, blue: 0.18) // #FF9D2E
        case .critical: return Color(red: 1.0, green: 0.3, blue: 0.31) // #FF4D4F
        }
    }
    
    var titleLocalizationKey: String {
        switch self {
        case .active: return "family_status_active"
        case .paused: return "family_status_paused"
        case .attention: return "family_status_attention"
        case .critical: return "family_status_critical"
        }
    }
    
    var messageLocalizationKey: String {
        switch self {
        case .active: return "family_status_active_message"
        case .paused: return "family_status_paused_message"
        case .attention: return "family_status_attention_message"
        case .critical: return "family_status_critical_message"
        }
    }
}

/// 🧠 Main View Model
/// Логика для главного экрана
/// Управляет состоянием защиты сети, функций, статистикой
@MainActor
class MainViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isNetworkProtectionEnabled: Bool = true
    @Published var familyMembers: Int = 4 // Дефолтное значение (fallback)
    @Published var threatsBlocked: Int = 47 // Дефолтное значение (fallback)
    @Published var devicesProtected: Int = 8 // Дефолтное значение (fallback)
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var lastUpdateTime: Date?
    @Published var familyProtectionStatus: FamilyProtectionStatus = .active
    @Published var familyProtectionStatusMessage: String?
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    private let apiService: APIService
    private let keychainManager: KeychainManager
    
    // ✅ ЗАЩИТА ОТ БЕСКОНЕЧНЫХ ЦИКЛОВ
    private var isLoadingDashboard = false
    private var lastOnAppearTime: Date?
    private var isLoadingFamilyStats = false // ✅ ЗАЩИТА ОТ РЕКУРСИИ: Флаг для getFamilyStats
    
    // MARK: - Init
    
    init(apiService: APIService = .shared, keychainManager: KeychainManager = .shared) {
        // ✅ КРИТИЧНО: Детальное логирование для диагностики краша (работает в RELEASE)
        let startTime = Date()
        let logPrefix = "🔍 MainViewModel.init"
        
        // Сохраняем в UserDefaults для получения после краша
        var debugLog: [String] = []
        debugLog.append("\(logPrefix) START - \(Date())")
        print("\(logPrefix) START - \(Date())")
        visualLogger.log("\(logPrefix) START", level: .debug)
        logger.business("Initializing MainViewModel")
        
        // ✅ ШАГ 1: Проверка параметров
        debugLog.append("\(logPrefix) ШАГ 1: Проверка параметров...")
        print("\(logPrefix) ШАГ 1: Проверка параметров...")
        visualLogger.log("\(logPrefix) ШАГ 1: Проверка параметров...", level: .debug)
        
        do {
            // Проверяем APIService
            let _ = apiService
            debugLog.append("✅ APIService доступен")
            print("✅ \(logPrefix) APIService доступен")
            visualLogger.log("✅ APIService доступен", level: .success)
            
            // Проверяем KeychainManager
            let _ = keychainManager
            debugLog.append("✅ KeychainManager доступен")
            print("✅ \(logPrefix) KeychainManager доступен")
            visualLogger.log("✅ KeychainManager доступен", level: .success)
            
        } catch {
            let errorMsg = "❌ Ошибка при проверке параметров: \(error)"
            debugLog.append(errorMsg)
            print("\(logPrefix) \(errorMsg)")
            visualLogger.log(errorMsg, level: .error)
            logger.error(errorMsg)
        }
        
        // ✅ ШАГ 2: Инициализация свойств
        debugLog.append("\(logPrefix) ШАГ 2: Инициализация свойств...")
        print("\(logPrefix) ШАГ 2: Инициализация свойств...")
        visualLogger.log("\(logPrefix) ШАГ 2: Инициализация свойств...", level: .debug)
        
        do {
            self.apiService = apiService
            self.keychainManager = keychainManager
            
            debugLog.append("✅ Свойства инициализированы")
            print("✅ \(logPrefix) Свойства инициализированы")
            visualLogger.log("✅ Свойства инициализированы", level: .success)
            
        } catch {
            let errorMsg = "❌ Ошибка при инициализации свойств: \(error)"
            debugLog.append(errorMsg)
            print("\(logPrefix) \(errorMsg)")
            visualLogger.log(errorMsg, level: .error)
            logger.error(errorMsg)
        }
        
        // ✅ ШАГ 3: Проверка thread safety
        debugLog.append("\(logPrefix) ШАГ 3: Проверка thread safety...")
        print("\(logPrefix) ШАГ 3: Проверка thread safety...")
        visualLogger.log("\(logPrefix) ШАГ 3: Проверка thread safety...", level: .debug)
        
        if Thread.isMainThread {
            debugLog.append("✅ Выполняется на main thread")
            print("✅ \(logPrefix) Выполняется на main thread")
            visualLogger.log("✅ Выполняется на main thread", level: .success)
        } else {
            let warningMsg = "⚠️ Выполняется НЕ на main thread: \(Thread.current)"
            debugLog.append(warningMsg)
            print("\(logPrefix) \(warningMsg)")
            visualLogger.log(warningMsg, level: .warning)
            logger.warn(warningMsg)
        }
        
        // НЕ загружаем данные автоматически при инициализации - только по требованию
        // loadDashboardData() // Закомментировано чтобы избежать бесконечных циклов
        
        let duration = Date().timeIntervalSince(startTime)
        let completeMsg = "✅ \(logPrefix) COMPLETE - Duration: \(String(format: "%.3f", duration))s"
        debugLog.append(completeMsg)
        print(completeMsg)
        visualLogger.log(completeMsg, level: .success)
        
        // Сохраняем логи
        saveInitDebugLog(debugLog)
    }
    
    /// Сохраняет логи инициализации MainViewModel
    private func saveInitDebugLog(_ logs: [String]) {
        let key = "main_view_model_init_debug_log"
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
    
    // MARK: - Public Methods
    
    /// ✅ ИНТЕГРАЦИЯ С API: Загрузка данных дашборда из реального API
    func loadDashboardData() {
        logger.business("Loading dashboard data")
        // ✅ ЗАЩИТА ОТ БЕСКОНЕЧНЫХ ЦИКЛОВ: Если уже загружается, пропускаем
        guard !isLoadingDashboard else {
            print("⚠️ MainViewModel: Загрузка дашборда уже выполняется, пропускаем")
            return
        }

        // ✅ ЗАДАЧА 66: Начинаем отслеживание производительности загрузки дашборда
        PerformanceMonitor.shared.startScreenLoad("MainDashboard")

        loadDashboardDataWithRetry(maxAttempts: 3)
    }
    
    private func loadDashboardDataWithRetry(maxAttempts: Int, currentAttempt: Int = 1) {
        // Предотвращаем множественные одновременные запросы
        if currentAttempt == 1 {
            guard !isLoading else {
                #if DEBUG
                print("⚠️ MainViewModel: Загрузка уже выполняется, пропускаем запрос")
                #endif
                return
            }
            isLoading = true
            isLoadingDashboard = true
            errorMessage = nil
        }
        
        #if DEBUG
        print("🔄 MainViewModel: Загружаем данные дашборда из API... (attempt \(currentAttempt)/\(maxAttempts))")
        #endif
        
        // ✅ ПРОВЕРКА ТОКЕНА: Если нет токена, не делаем API вызов
        let hasAuthToken = keychainManager.isDataAvailable(forKey: .authToken)
        #if DEBUG
        print("🔐 MainViewModel: Проверка токена авторизации - \(hasAuthToken ? "✅ токен найден" : "ℹ️ токен отсутствует (демо режим)")")
        #endif

        if !hasAuthToken {
            // ❌ НЕТ ТОКЕНА: В продакшн требуем авторизацию, в DEBUG показываем демо данные
            #if DEBUG
            print("ℹ️ MainViewModel: Debug режим - демо данные (токен отсутствует)")
            #else
            // ✅ В ПРОДАКШН: Демо режим НЕ допустим - требуем авторизацию
            print("❌ MainViewModel: Токен отсутствует - требуется авторизация")
            #endif

            Task { @MainActor [weak self] in
                guard let self = self else { return }
                self.isLoading = false
                self.isLoadingDashboard = false

                // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности загрузки дашборда
                PerformanceMonitor.shared.endScreenLoad("MainDashboard")
                
                #if DEBUG
                // Только в DEBUG режиме показываем демо данные
                self.familyMembers = 1
                self.devicesProtected = 1
                self.threatsBlocked = 0
                self.lastUpdateTime = Date()
                self.errorMessage = nil
                self.familyProtectionStatus = .active
                let localizationManager = LocalizationManager()
                self.familyProtectionStatusMessage = localizationManager.localized("main_family_protection_status_message")
                NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                #else
                // В продакшн: показываем ошибку и требуем авторизацию
                self.errorMessage = "Требуется авторизация"
                // TODO: Переход на экран авторизации
                #endif
            }
            return
        }

        // ✅ ЕСТЬ ТОКЕН: Делаем API вызов
        let timeoutInterval: TimeInterval = 10.0
        let timeoutWorkItem = DispatchWorkItem { [weak self] in
            guard let self = self else { return }
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                if self.isLoading {
                    #if DEBUG
                    print("⚠️ MainViewModel: Таймаут загрузки данных (10 секунд) на попытке \(currentAttempt)")
                    #endif
                    self.isLoading = false
                    // Показываем баннер только если исчерпаны попытки
                    if currentAttempt >= maxAttempts {
                        self.errorMessage = "Таймаут загрузки данных. Проверьте подключение к интернету."
                    }
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + timeoutInterval, execute: timeoutWorkItem)
        
        // ✅ РЕАЛЬНЫЙ API ВЫЗОВ: Загружаем статистику семьи
        // ✅ ЗАЩИТА ОТ РЕКУРСИИ: Проверяем, не загружается ли уже статистика
        guard !isLoadingFamilyStats else {
            #if DEBUG
            print("⚠️ MainViewModel: Статистика семьи уже загружается, пропускаем повторный вызов")
            #endif
            return
        }
        
        isLoadingFamilyStats = true
        apiService.getFamilyStats { [weak self] result in
            guard let self = self else { return }
            
            // Отменяем таймаут если запрос успел
            timeoutWorkItem.cancel()
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                self.isLoadingFamilyStats = false // Сбрасываем флаг в любом случае
                
                switch result {
                case .success(let stats):
                    self.isLoading = false
                    self.isLoadingDashboard = false

                    // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности загрузки дашборда
                    PerformanceMonitor.shared.endScreenLoad("MainDashboard")
                    // ✅ ОБНОВЛЯЕМ ДАННЫЕ ИЗ API
                    self.familyMembers = stats.totalMembers
                    self.devicesProtected = stats.totalDevices
                    self.threatsBlocked = stats.totalThreats
                    self.lastUpdateTime = Date()
                    self.errorMessage = nil // Авто-очистка баннера при успехе
                    self.familyProtectionStatus = FamilyProtectionStatus(apiValue: stats.familyStatus)
                    self.familyProtectionStatusMessage = stats.familyStatusMessage
                    
                    #if DEBUG
                    print("✅ MainViewModel: Данные загружены успешно")
                    #endif
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                    
                case .failure(let error):
                    // Экспоненциальный бэк-офф: 0.5s, 1.0s, 2.0s
                    if currentAttempt < maxAttempts {
                        let delay = pow(2.0, Double(currentAttempt - 1)) * 0.5
                        #if DEBUG
                        print("❌ MainViewModel: Ошибка загрузки (попытка \(currentAttempt)): \(error.localizedDescription). Повтор через \(delay)s")
                        #endif
                        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                            self.loadDashboardDataWithRetry(maxAttempts: maxAttempts, currentAttempt: currentAttempt + 1)
                        }
                    } else {
                        // После всех неудачных попыток проверяем, связана ли ошибка с токеном
                        let isTokenError = error.localizedDescription.contains("Сессия истекла") ||
                                          error.localizedDescription.contains("токен") ||
                                          error.localizedDescription.contains("Token")

                        if isTokenError {
                            // Сессия истекла - очищаем токены и отправляем на логин
                            self.handleSessionExpired()
                        } else {
                            // Другая ошибка - просто показываем сообщение
                            // ✅ ИСПРАВЛЕНИЕ: Обновление UI на main thread
                            Task { @MainActor [weak self] in
                                guard let self = self else { return }
                                self.isLoading = false
                                self.errorMessage = error.localizedDescription
                                #if DEBUG
                                print("❌ MainViewModel: Ошибка после \(maxAttempts) попыток: \(error.localizedDescription)")
                                #endif
                                NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                            }
                        }
                    }
                }
            }
        }
    }
    
    /// Переключение защиты сети
    func toggleNetworkProtection() {
        logger.business("Toggling network protection")
        isNetworkProtectionEnabled.toggle()
        
        // Haptic feedback
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // API вызов для включения/выключения защиты сети
        if isNetworkProtectionEnabled {
            connectNetworkProtection()
        } else {
            disconnectNetworkProtection()
        }
    }
    
    /// Обновление статистики (принудительное)
    func refreshStats() {
        #if DEBUG
        print("🔄 MainViewModel: Принудительное обновление статистики")
        #endif
        loadDashboardData()
    }

    /// Обработка истекшей сессии
    private func handleSessionExpired() {
        // Проверяем, являются ли токены debug токенами
        let isDebugToken = isUsingDebugTokens()

        if isDebugToken {
            print("🔐 MainViewModel: Debug токены не работают с сервером - работаем в offline режиме")
            // Для debug токенов не очищаем их и не отправляем на логин
            // Просто показываем сообщение и работаем с дефолтными данными
            isLoading = false
            errorMessage = "Работа в демо-режиме с тестовыми данными"
            NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
            return
        }

        print("🔐 MainViewModel: Сессия истекла - очищаем токены и отправляем на логин")

        // Очищаем токены из Keychain
        keychainManager.delete(forKey: .authToken)
        keychainManager.delete(forKey: .refreshToken)

        // Сбрасываем состояние
        isLoading = false
        errorMessage = "Сессия истекла. Пожалуйста, войдите заново."

        // Отправляем уведомление о необходимости логина
        NotificationCenter.default.post(
            name: NSNotification.Name("SessionExpired"),
            object: nil,
            userInfo: ["message": "Ваша сессия истекла. Пожалуйста, войдите заново."]
        )

        // Также отправляем стандартное уведомление для UI
        NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
    }

    /// Проверяет, используются ли debug токены
    private func isUsingDebugTokens() -> Bool {
        guard let token = keychainManager.loadString(forKey: .authToken) else {
            return false
        }

        // Debug токен содержит специфический payload
        return token.contains("debug-auth") || token.contains("debugsignature")
    }
    
    /// ✅ АВТООБНОВЛЕНИЕ: Загрузка данных при открытии экрана
    func onAppear() {
        // ✅ КРИТИЧНО: Проверяем, завершен ли онбординг
        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        if !onboardingDone {
            #if DEBUG
            print("⚠️ MainViewModel: Онбординг не завершен - пропускаем загрузку данных")
            #endif
            return
        }

        // ✅ ЗАЩИТА ОТ ЧАСТЫХ ВЫЗОВОВ: Проверяем, не было ли onAppear недавно
        if let lastCall = lastOnAppearTime, Date().timeIntervalSince(lastCall) < 30 {
            #if DEBUG
            print("⚠️ MainViewModel: onAppear вызван слишком часто, пропускаем")
            #endif
            return
        }
        lastOnAppearTime = Date()

        // Проверяем, используются ли debug токены
        if isUsingDebugTokens() {
            #if DEBUG
            print("ℹ️ MainViewModel: Debug токены - работаем в демо-режиме, пропускаем загрузку API")
            #endif
            // Для debug токенов показываем демо-сообщение
            errorMessage = "Демо-режим: тестовые данные"
            NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
            return
        }

        // Проверяем, нужно ли обновлять данные
        let shouldRefresh: Bool
        
        if let lastUpdate = lastUpdateTime {
            // Обновляем, если прошло больше 5 минут
            let timeSinceUpdate = Date().timeIntervalSince(lastUpdate)
            shouldRefresh = timeSinceUpdate > 300 // 5 минут
        } else {
            // Если данных ещё нет - загружаем
            shouldRefresh = true
        }
        
        if shouldRefresh {
            #if DEBUG
            print("🔄 MainViewModel: Автообновление данных (onAppear)")
            #endif
            loadDashboardData()
        } else {
            #if DEBUG
            print("ℹ️ MainViewModel: Данные актуальны, пропускаем обновление")
            #endif
        }
    }
    
    /// Открыть семью
    func openFamily() {
        #if DEBUG
        print("Navigation to Family Screen")
        #endif
    }
    
    /// Открыть защиту сети
    func openNetworkProtection() {
        #if DEBUG
        print("Navigation to Network Protection Screen")
        #endif
    }
    
    /// Открыть аналитику
    func openAnalytics() {
        #if DEBUG
        print("Navigation to Analytics Screen")
        #endif
    }
    
    /// Открыть AI
    func openAI() {
        #if DEBUG
        print("Navigation to AI Assistant Screen")
        #endif
    }
    
    // MARK: - Private Methods
    
    private func connectNetworkProtection() {
        logger.business("Connecting to network protection service")
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Connecting to Network Protection...")
        #endif
    }

    private func disconnectNetworkProtection() {
        logger.business("Disconnecting from network protection service")
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Disconnecting Network Protection...")
        #endif
    }
}



