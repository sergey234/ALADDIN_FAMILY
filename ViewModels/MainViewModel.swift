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
    case networkUnavailable
    
    init(apiValue: String?) {
        guard let raw = apiValue?.lowercased(), !raw.isEmpty else {
            self = .attention
            return
        }

        // Canonical iOS values
        if let direct = FamilyProtectionStatus(rawValue: raw) {
            self = direct
            return
        }

        // Backend compatibility mapping
        switch raw {
        case "protected":
            self = .active
        case "warning":
            self = .attention
        case "danger":
            self = .critical
        case "offline":
            self = .networkUnavailable
        default:
            // Safe fallback: never promote unknown state to "active".
            self = .attention
        }
    }
    
    var iconName: String {
        switch self {
        case .active: return "checkmark.circle.fill"
        case .paused: return "pause.circle.fill"
        case .attention: return "exclamationmark.triangle.fill"
        case .critical: return "xmark.octagon.fill"
        case .networkUnavailable: return "wifi.exclamationmark"
        }
    }
    
    var color: Color {
        switch self {
        case .active: return Color(red: 0.05, green: 0.8, blue: 0.42) // #0CCE6B
        case .paused: return Color(red: 0.6, green: 0.63, blue: 0.68) // #9AA0AE
        case .attention: return Color(red: 1.0, green: 0.62, blue: 0.18) // #FF9D2E
        case .critical: return Color(red: 1.0, green: 0.3, blue: 0.31) // #FF4D4F
        case .networkUnavailable: return Color(red: 0.22, green: 0.54, blue: 0.96) // #3889F5
        }
    }
    
    var titleLocalizationKey: String {
        switch self {
        case .active: return "family_status_active"
        case .paused: return "family_status_paused"
        case .attention: return "family_status_attention"
        case .critical: return "family_status_critical"
        case .networkUnavailable: return "family_status_network_unavailable"
        }
    }
    
    var messageLocalizationKey: String {
        switch self {
        case .active: return "family_status_active_message"
        case .paused: return "family_status_paused_message"
        case .attention: return "family_status_attention_message"
        case .critical: return "family_status_critical_message"
        case .networkUnavailable: return "family_status_network_unavailable_message"
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
    @Published var familyMembers: Int = 0 // ✅ BUILD 115: Начальное значение 0 - будет обновлено из API
    @Published var threatsBlocked: Int = 0 // ✅ BUILD 115: Начальное значение 0 - будет обновлено из API
    @Published var devicesProtected: Int = 0 // ✅ BUILD 115: Начальное значение 0 - будет обновлено из API
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
        // ✅ BUILD 109: Полная изоляция конструктора. Никаких логов или системных вызовов.
        self.apiService = apiService
        self.keychainManager = keychainManager
    }
    
    // MARK: - Public Methods
    
    /// ✅ ИНТЕГРАЦИЯ С API: Загрузка данных дашборда из реального API
    func loadDashboardData() {
        // ✅ BUILD 115: Добавлена диагностика для отслеживания загрузки
        print("🔄 MainViewModel.loadDashboardData: Начало загрузки данных")
        print("   - isLoadingDashboard: \(isLoadingDashboard)")
        print("   - Текущие значения: члены=\(familyMembers), устройства=\(devicesProtected), угрозы=\(threatsBlocked)")
        
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
        print("🔐 MainViewModel: Проверка токена авторизации")
        print("   - Токен найден: \(hasAuthToken ? "✅ ДА" : "❌ НЕТ")")
        if hasAuthToken {
            if let token = keychainManager.loadString(forKey: .authToken) {
                print("   - Токен: \(token.prefix(20))...")
            }
        }

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
                // ✅ BUILD 112: Используем Singleton вместо создания нового тяжелого объекта
                // Это критически важно для предотвращения переполнения стека при старте
                let localizationManager = LocalizationManager.shared
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
            print("⚠️ MainViewModel: Статистика семьи уже загружается, пропускаем повторный вызов")
            return
        }
        
        isLoadingFamilyStats = true
        print("🔄 MainViewModel: Вызов API getFamilyStats...")
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
                    // ✅ BUILD 115: ОБНОВЛЯЕМ ДАННЫЕ ИЗ API с диагностикой
                    print("📊 MainViewModel: Обновление данных из API:")
                    print("   - Члены семьи: \(self.familyMembers) → \(stats.totalMembers)")
                    print("   - Устройства: \(self.devicesProtected) → \(stats.totalDevices)")
                    print("   - Угрозы: \(self.threatsBlocked) → \(stats.totalThreats)")
                    print("   - Статус: \(stats.familyStatus ?? "nil")")
                    
                    self.familyMembers = stats.totalMembers
                    self.devicesProtected = stats.totalDevices
                    self.threatsBlocked = stats.totalThreats
                    self.lastUpdateTime = Date()
                    self.errorMessage = nil // Авто-очистка баннера при успехе
                    let mappedStatus = FamilyProtectionStatus(apiValue: stats.familyStatus)
                    self.familyProtectionStatus = mappedStatus
                    self.familyProtectionStatusMessage = stats.familyStatusMessage
                    VisualLogger.shared.log("ℹ️ FAMILY.STATUS raw=\(stats.familyStatus ?? "nil") mapped=\(mappedStatus.rawValue) source=api", level: .info, category: "MAIN.STATUS")
                    
                    print("✅ MainViewModel: Данные успешно обновлены из API")
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                    
                case .failure(let error):
                    // ✅ BUILD 115: Улучшенная диагностика ошибок
                    print("❌ MainViewModel: Ошибка загрузки данных из API (попытка \(currentAttempt)/\(maxAttempts))")
                    print("   - Ошибка: \(error.localizedDescription)")
                    print("   - Текущие значения (fallback): члены=\(self.familyMembers), устройства=\(self.devicesProtected), угрозы=\(self.threatsBlocked)")
                    
                    // Экспоненциальный бэк-офф: 0.5s, 1.0s, 2.0s
                    if currentAttempt < maxAttempts {
                        let delay = pow(2.0, Double(currentAttempt - 1)) * 0.5
                        print("   - Повтор через \(delay)s...")
                        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                            self.loadDashboardDataWithRetry(maxAttempts: maxAttempts, currentAttempt: currentAttempt + 1)
                        }
                    } else {
                        // После всех неудачных попыток проверяем, связана ли ошибка с токеном
                        let isTokenError = error.localizedDescription.contains("Сессия истекла") ||
                                          error.localizedDescription.contains("токен") ||
                                          error.localizedDescription.contains("Token")

                        if isTokenError {
                            print("   - Ошибка связана с токеном - проверяем валидность токена")
                            // ✅ BUILD 121: Проверяем валидность токена перед удалением
                            let tokenStatus = TokenValidator.validateCurrentToken()
                            if case .valid = tokenStatus {
                                print("   - ⚠️ Токен валиден, но сервер вернул 401 - НЕ удаляем токен")
                                print("   - Это может быть серверная проблема или проблема с конкретным endpoint")
                                // Не удаляем токен и не отправляем SessionExpired
                                Task { @MainActor [weak self] in
                                    guard let self = self else { return }
                                    self.isLoading = false
                                    self.isLoadingDashboard = false
                                    self.errorMessage = "Не удалось загрузить данные. Проверьте подключение к интернету."
                                    // Production-safe: при серверном фейле не оставляем старые “реальные” цифры.
                                    self.familyMembers = 0
                                    self.devicesProtected = 0
                                    self.threatsBlocked = 0
                                    self.lastUpdateTime = nil
                                    // Temporary server/network failure is not a "critical disable" state.
                                    self.familyProtectionStatus = .networkUnavailable
                                    self.familyProtectionStatusMessage = LocalizationManager.shared.localized("family_status_network_unavailable_message")
                                    VisualLogger.shared.log("⚠️ FAMILY.STATUS raw=error mapped=networkUnavailable source=error_token_path", level: .warning, category: "MAIN.STATUS")
                                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                                }
                            } else {
                                print("   - Токен действительно невалиден - очищаем токены")
                                // Сессия истекла - очищаем токены и отправляем на логин
                                self.handleSessionExpired()
                            }
                        } else {
                            // Другая ошибка - показываем сообщение и оставляем fallback значения
                            print("   - Критическая ошибка после всех попыток - данные НЕ обновлены из API")
                            print("   - ⚠️ ВНИМАНИЕ: Отображаются fallback значения, а не реальные данные!")
                            Task { @MainActor [weak self] in
                                guard let self = self else { return }
                                self.isLoading = false
                                self.isLoadingDashboard = false
                                self.errorMessage = "Не удалось загрузить данные: \(error.localizedDescription)"
                                // Production-safe: при серверном фейле не оставляем старые “реальные” цифры.
                                self.familyMembers = 0
                                self.devicesProtected = 0
                                self.threatsBlocked = 0
                                self.lastUpdateTime = nil
                                // Temporary server/network failure is not a "critical disable" state.
                                self.familyProtectionStatus = .networkUnavailable
                                self.familyProtectionStatusMessage = LocalizationManager.shared.localized("family_status_network_unavailable_message")
                                VisualLogger.shared.log("⚠️ FAMILY.STATUS raw=error mapped=networkUnavailable source=error_general_path", level: .warning, category: "MAIN.STATUS")
                                print("❌ MainViewModel: Ошибка после \(maxAttempts) попыток: \(error.localizedDescription)")
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
        // ✅ BUILD 110: Удален лог
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
    /// ✅ BUILD 121: ИСПРАВЛЕНО - Проверяет валидность токена перед удалением
    private func handleSessionExpired() {
        // ✅ BUILD 121: Проверяем валидность токена ПЕРЕД удалением
        let tokenStatus = TokenValidator.validateCurrentToken()
        if case .valid = tokenStatus {
            #if DEBUG
            print("⚠️ MainViewModel.handleSessionExpired: Токен валиден - НЕ удаляем токен")
            let stackTrace = Thread.callStackSymbols.prefix(5).joined(separator: "\n")
            print("   - Call stack:")
            print(stackTrace)
            VisualLogger.shared.log("⚠️ MainViewModel: SessionExpired игнорировано - токен валиден", level: .warning, category: "SESSION")
            MasterLogger.shared.log(.warn, category: .business, message: "⚠️ MainViewModel: SessionExpired ignored - token is valid")
            #endif
            // Токен валиден - не удаляем и не отправляем SessionExpired
            isLoading = false
            isLoadingDashboard = false
            errorMessage = "Не удалось загрузить данные. Проверьте подключение к интернету."
            NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
            return
        }
        
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

        // ✅ BUILD 121: Логирование отправки SessionExpired
        #if DEBUG
        let stackTrace = Thread.callStackSymbols.prefix(5).joined(separator: "\n")
        print("📤 MainViewModel.handleSessionExpired: Отправка SessionExpired notification")
        print("   - Call stack:")
        print(stackTrace)
        VisualLogger.shared.log("📤 MainViewModel: Отправка SessionExpired", level: .warning, category: "SESSION")
        MasterLogger.shared.log(.warn, category: .business, message: "📤 MainViewModel: Sending SessionExpired notification")
        #endif

        print("🔐 MainViewModel: Сессия истекла - очищаем токены и отправляем на логин")

        // ✅ BUILD 121: Используем SubscriptionManager.clearToken() вместо прямого удаления
        // Это обеспечивает правильную очистку всех хранилищ
        Task { @MainActor in
            await SubscriptionManager.shared.clearToken()
        }

        // Сбрасываем состояние
        isLoading = false
        isLoadingDashboard = false
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
        // ✅ BUILD 115: Добавлена диагностика для отслеживания загрузки данных
        print("🔄 MainViewModel.onAppear: Вызван")
        print("   - Текущие значения: члены=\(familyMembers), устройства=\(devicesProtected), угрозы=\(threatsBlocked)")
        print("   - lastUpdateTime: \(lastUpdateTime?.description ?? "nil")")
        
        // ✅ ЗАЩИТА ОТ ЧАСТЫХ ВЫЗОВОВ: Проверяем, не было ли onAppear недавно
        if let lastCall = lastOnAppearTime, Date().timeIntervalSince(lastCall) < 30 {
            print("   - ⚠️ onAppear вызван слишком часто (<30 сек), пропускаем")
            return
        }
        lastOnAppearTime = Date()

        // Проверяем, нужно ли обновлять данные
        let shouldRefresh: Bool
        
        if let lastUpdate = lastUpdateTime {
            // Обновляем, если прошло больше 5 минут
            let timeSinceUpdate = Date().timeIntervalSince(lastUpdate)
            shouldRefresh = timeSinceUpdate > 300 // 5 минут
            print("   - Время с последнего обновления: \(Int(timeSinceUpdate)) сек")
            print("   - Нужно обновить: \(shouldRefresh ? "ДА" : "НЕТ")")
        } else {
            // Если данных ещё нет - загружаем
            shouldRefresh = true
            print("   - Данных нет - загружаем обязательно")
        }
        
        if shouldRefresh {
            print("   - ✅ Запускаем loadDashboardData()...")
            loadDashboardData()
        } else {
            print("   - ⏭️ Пропускаем загрузку (данные свежие)")
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
        // ✅ BUILD 110: Удален лог
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Connecting to Network Protection...")
        #endif
    }

    private func disconnectNetworkProtection() {
        // ✅ BUILD 110: Удален лог
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Disconnecting Network Protection...")
        #endif
    }
}



