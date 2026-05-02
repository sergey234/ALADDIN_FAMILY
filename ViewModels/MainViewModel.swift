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

    /// Якорь для коалесцирования обновлений в первые секунды после запуска процесса.
    private static let processLaunchDate = Date()
    
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
    
    // MARK: - Stabilization State (TTL + N-threshold)
    /// Последний подтвержденный статус из успешного API-ответа
    private var lastConfirmedStatus: FamilyProtectionStatus = .active
    /// Время последнего успешного получения статуса
    private var lastSuccessAt: Date? = nil
    /// Количество подряд неуспешных попыток загрузки
    private var consecutiveFailures: Int = 0
    /// Минимальное время удержания подтвержденного статуса (сек) — меньше ложных перекрасок при единичных сбоях.
    private let statusTTLSec: TimeInterval = 18
    /// Порог неуспехов для перехода в networkUnavailable (после полевых логов MAIN.STATUS).
    private let failuresThreshold: Int = 3
    /// Debounce для внешних запросов обновления (мс)
    private let refreshDebounceMs: Int = 700
    /// На холодном старте увеличиваем окно, чтобы слить SubscriptionUpdated / MainScreen / устройства в один кадр загрузки.
    private let refreshDebounceColdStartMs: Int = 950
    private let coldStartCoalesceWindowSec: TimeInterval = 1.25
    private var refreshDebounceWorkItem: DispatchWorkItem?
    
    // MARK: - Public Orchestrator API
    func requestRefreshDebounced() {
        refreshDebounceWorkItem?.cancel()
        let work = DispatchWorkItem { [weak self] in
            DispatchQueue.main.async { [weak self] in
                self?.loadDashboardData()
            }
        }
        refreshDebounceWorkItem = work
        let elapsed = Date().timeIntervalSince(Self.processLaunchDate)
        let ms = elapsed < coldStartCoalesceWindowSec ? refreshDebounceColdStartMs : refreshDebounceMs
        let delay = DispatchTimeInterval.milliseconds(ms)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay, execute: work)
    }

    /// Счётчик устройств на главной/профиле = тот же `GET /api/devices` и та же дедупликация по `id`, что на экране «Устройства».
    private static func deduplicatedDeviceCount(_ list: [DeviceResponse]) -> Int {
        var seen = Set<String>()
        return list.filter { seen.insert($0.id).inserted }.count
    }

    /// Мгновенно подтянуть число устройств (без ожидания debounce полного дашборда) — устраняет рассинхрон 1 vs 2 после добавления/удаления.
    func refreshDevicesCountFromAPI() {
        if isLoadingDashboard {
            #if DEBUG
            print("ℹ️ MainViewModel.refreshDevicesCountFromAPI: пропуск — уже идёт loadDashboardData (будет dedupe GET /api/devices)")
            #endif
            return
        }
        apiService.getDevices { [weak self] result in
            Task { @MainActor in
                guard let self = self else { return }
                if case .success(let list) = result {
                    self.devicesProtected = Self.deduplicatedDeviceCount(list)
                }
                UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh)
                NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
            }
        }
    }
    
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
            // ❌ НЕТ ТОКЕНА: Ждём инициализации SubscriptionManager (Phase 1/2 fix)
            #if DEBUG
            print("⚠️ MainViewModel: Токен отсутствует. Ожидаем инициализацию SubscriptionManager...")
            #else
            print("❌ MainViewModel: Токен отсутствует - требуется авторизация")
            #endif

            // Не сбрасываем данные агрессивно — сохраняем предыдущее состояние
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                self.isLoading = false
                self.isLoadingDashboard = false
                PerformanceMonitor.shared.endScreenLoad("MainDashboard")

                #if DEBUG
                // В DEBUG не сбрасываем в 0 — оставляем предыдущие значения или ставим минимальные
                if self.familyMembers == 0 {
                    self.familyMembers = 1
                    self.devicesProtected = 1
                    self.familyProtectionStatus = .active
                    self.familyProtectionStatusMessage = LocalizationManager.shared.localized("main_family_protection_status_message")
                }
                NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                #else
                self.errorMessage = "Требуется авторизация"
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
                    self.isLoadingDashboard = false
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
                    // Не снимаем isLoadingDashboard до завершения GET /api/devices: иначе debounced
                    // SubscriptionUpdated/onChange запускают второй loadDashboardData параллельно (лишние GET /api/devices).
                    // ✅ BUILD 115: ОБНОВЛЯЕМ ДАННЫЕ ИЗ API с диагностикой
                    print("📊 MainViewModel: Обновление данных из API:")
                    print("   - Члены семьи: \(self.familyMembers) → \(stats.totalMembers)")
                    print("   - Устройства: \(self.devicesProtected) → (ожидаем список /api/devices, fallback stats=\(stats.totalDevices))")
                    print("   - Угрозы: \(self.threatsBlocked) → \(stats.totalThreats)")
                    print("   - Статус: \(stats.familyStatus ?? "nil")")
                    
                    // Члены: источник правды — ответ `family/stats` (избегаем рассинхрона с локальным списком до обновления экрана «Семья»).
                    self.familyMembers = stats.totalMembers
                    self.threatsBlocked = stats.totalThreats
                    self.errorMessage = nil // Авто-очистка баннера при успехе
                    
                    // Подтверждаем статус по успешному API
                    let mappedStatus = FamilyProtectionStatus(apiValue: stats.familyStatus)
                    self.lastConfirmedStatus = mappedStatus
                    self.lastSuccessAt = Date()
                    self.consecutiveFailures = 0
                    
                    // Публикуем подтвержденный статус
                    self.familyProtectionStatus = mappedStatus
                    self.familyProtectionStatusMessage = stats.familyStatusMessage
                    VisualLogger.shared.log("ℹ️ FAMILY.STATUS raw=\(stats.familyStatus ?? "nil") mapped=\(mappedStatus.rawValue) source=api ttl_left=0s fails=\(self.consecutiveFailures)", level: .info, category: "MAIN.STATUS")
                    
                    let fallbackDevices = stats.totalDevices
                    self.apiService.getDevices { devicesResult in
                        Task { @MainActor in
                            switch devicesResult {
                            case .success(let list):
                                self.devicesProtected = Self.deduplicatedDeviceCount(list)
                                print("   - Устройства (из /api/devices, dedupe): \(self.devicesProtected)")
                            case .failure(let err):
                                self.devicesProtected = fallbackDevices
                                print("   - Устройства: список API недоступен, используем family/stats: \(fallbackDevices) (\(err.localizedDescription))")
                            }
                            self.isLoading = false
                            self.isLoadingDashboard = false
                            self.lastUpdateTime = Date()
                            PerformanceMonitor.shared.endScreenLoad("MainDashboard")
                            print("✅ MainViewModel: Данные успешно обновлены из API")
                            NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                        }
                    }
                    
                case .failure(let error):
                    // ✅ BUILD 115: Улучшенная диагностика ошибок
                    print("❌ MainViewModel: Ошибка загрузки данных из API (попытка \(currentAttempt)/\(maxAttempts))")
                    print("   - Ошибка: \(error.localizedDescription)")
                    print("   - Текущие значения (fallback): члены=\(self.familyMembers), устройства=\(self.devicesProtected), угрозы=\(self.threatsBlocked)")
                    let reason = self.classifyError(error)
                    
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
                                    // TTL/N‑порог: увеличиваем счётчик фейлов и решаем, менять ли статус
                                    self.consecutiveFailures += 1
                                    let now = Date()
                                    if self.consecutiveFailures >= self.failuresThreshold && self.isTTLElapsed(now: now) {
                                        self.familyProtectionStatus = .networkUnavailable
                                        self.familyProtectionStatusMessage = LocalizationManager.shared.localized("family_status_network_unavailable_message")
                                    } else {
                                        // Удерживаем последний подтвержденный статус
                                        self.familyProtectionStatus = self.lastConfirmedStatus
                                    }
                                VisualLogger.shared.log("⚠️ FAMILY.STATUS raw=error mapped=\(self.familyProtectionStatus.rawValue) source=error_token_path reason=\(reason) ttl_left=\(self.ttlLeft(now: now))s fails=\(self.consecutiveFailures)", level: .warning, category: "MAIN.STATUS")
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
                                
                                // TTL/N‑порог: увеличиваем счётчик фейлов и решаем, менять ли статус
                                self.consecutiveFailures += 1
                                let now = Date()
                                if self.consecutiveFailures >= self.failuresThreshold && self.isTTLElapsed(now: now) {
                                    self.familyProtectionStatus = .networkUnavailable
                                    self.familyProtectionStatusMessage = LocalizationManager.shared.localized("family_status_network_unavailable_message")
                                } else {
                                    self.familyProtectionStatus = self.lastConfirmedStatus
                                }
                                VisualLogger.shared.log("⚠️ FAMILY.STATUS raw=error mapped=\(self.familyProtectionStatus.rawValue) source=error_general_path reason=\(reason) ttl_left=\(self.ttlLeft(now: now))s fails=\(self.consecutiveFailures)", level: .warning, category: "MAIN.STATUS")
                                print("❌ MainViewModel: Ошибка после \(maxAttempts) попыток: \(error.localizedDescription)")
                                NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                            }
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - TTL Helpers
    private func isTTLElapsed(now: Date = Date()) -> Bool {
        guard let last = lastSuccessAt else { return true }
        return now.timeIntervalSince(last) >= statusTTLSec
    }
    
    private func ttlLeft(now: Date = Date()) -> Int {
        guard let last = lastSuccessAt else { return 0 }
        let left = statusTTLSec - now.timeIntervalSince(last)
        return max(0, Int(left.rounded()))
    }
    
    // MARK: - Error Classification
    private func classifyError(_ error: Error) -> String {
        let text = error.localizedDescription.lowercased()
        if text.contains("timed out") || text.contains("timeout") { return "timeout" }
        if text.contains("ssl") || text.contains("tls") { return "tls" }
        if text.contains("401") || text.contains("unauthorized") { return "401" }
        if text.contains("500") || text.contains("503") { return "5xx" }
        return "other"
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
        // ✅ PHASE 2: Улучшенный onAppear с ожиданием SubscriptionManager
        print("🔄 MainViewModel.onAppear: Вызван (Phase 2 improved)")
        print("   - Текущие значения: члены=\(familyMembers), устройства=\(devicesProtected), угрозы=\(threatsBlocked)")
        print("   - lastUpdateTime: \(lastUpdateTime?.description ?? "nil")")
        print("   - Subscription initialized: \(SubscriptionManager.shared.isInitialized)")
        
        let pendingDevicesRefresh = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh)
        
        // ✅ ЗАЩИТА ОТ ЧАСТЫХ ВЫЗОВОВ (не применяем, если ждём обновление после экрана «Устройства»)
        if !pendingDevicesRefresh {
            if let lastCall = lastOnAppearTime, Date().timeIntervalSince(lastCall) < 15 {
                print("   - ⚠️ onAppear вызван слишком часто (<15 сек), пропускаем")
                return
            }
        }
        lastOnAppearTime = Date()
        refreshFamilyMembersCountFromStorage()

        // ✅ PHASE 2: Ждём готовности SubscriptionManager (важно после изменений ALADDINApp)
        if !SubscriptionManager.shared.isInitialized {
            print("⏳ SubscriptionManager ещё не инициализирован — откладываем загрузку на 800мс")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { [weak self] in
                self?.onAppear()
            }
            return
        }

        // Проверяем, нужно ли обновлять данные
        let shouldRefresh: Bool
        
        if let lastUpdate = lastUpdateTime {
            let timeSinceUpdate = Date().timeIntervalSince(lastUpdate)
            shouldRefresh = timeSinceUpdate > 180 // 3 минуты вместо 5 (быстрее обновление)
            print("   - Время с последнего обновления: \(Int(timeSinceUpdate)) сек")
            print("   - Нужно обновить: \(shouldRefresh ? "ДА" : "НЕТ")")
        } else {
            shouldRefresh = true
            print("   - Данных нет — загружаем обязательно")
        }
        
        if pendingDevicesRefresh || shouldRefresh {
            if pendingDevicesRefresh {
                UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh)
                print("   - ✅ Принудительное обновление дашборда (изменился список устройств)")
            }
            print("   - ✅ Запускаем loadDashboardData()...")
            loadDashboardData()
        } else {
            print("   - ⏭️ Пропускаем загрузку (данные свежие)")
            // Всё равно обновляем статус, если он устарел
            if familyProtectionStatus == .networkUnavailable || familyProtectionStatus == .attention {
                familyProtectionStatus = .active
            }
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

    func refreshFamilyMembersCountFromStorage() {
        // Число членей на главной берётся из `GET /api/family/stats` (см. `loadDashboardDataWithRetry`),
        // а не из `family_members_list`, чтобы не было рассинхрона «2 → 1» при устаревшем локальном кэше.
        // После изменений состава семьи экран `MainScreen` вызывает `requestRefreshDebounced()` по `FamilyMembersUpdated`.
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



