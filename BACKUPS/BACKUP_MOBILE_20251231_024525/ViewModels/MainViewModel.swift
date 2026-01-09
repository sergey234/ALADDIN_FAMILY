import SwiftUI
import Combine

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
    
    // MARK: - Init
    
    init(apiService: APIService = .shared, keychainManager: KeychainManager = .shared) {
        self.apiService = apiService
        self.keychainManager = keychainManager
        // Загружаем данные при инициализации
        loadDashboardData()
    }
    
    // MARK: - Public Methods
    
    /// ✅ ИНТЕГРАЦИЯ С API: Загрузка данных дашборда из реального API
    func loadDashboardData() {
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
            errorMessage = nil
        }
        
        #if DEBUG
        print("🔄 MainViewModel: Загружаем данные дашборда из API... (attempt \(currentAttempt)/\(maxAttempts))")
        #endif
        
        // ✅ ТАЙМАУТ: Если запрос не успевает за N секунд, показываем fallback данные (для попытки)
        let hasAuthToken = keychainManager.isDataAvailable(forKey: .authToken)
        let timeoutInterval: TimeInterval = hasAuthToken ? 10.0 : 5.0
        let timeoutWorkItem = DispatchWorkItem { [weak self] in
            guard let self = self else { return }
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                if self.isLoading {
                    #if DEBUG
                    print("⚠️ MainViewModel: Таймаут загрузки данных (5 секунд) на попытке \(currentAttempt)")
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
        apiService.getFamilyStats { [weak self] result in
            guard let self = self else { return }
            
            // Отменяем таймаут если запрос успел
            timeoutWorkItem.cancel()
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                switch result {
                case .success(let stats):
                    self.isLoading = false
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
    
    /// Переключение защиты сети
    func toggleNetworkProtection() {
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
    
    /// ✅ АВТООБНОВЛЕНИЕ: Загрузка данных при открытии экрана
    func onAppear() {
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
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Connecting to Network Protection...")
        #endif
    }
    
    private func disconnectNetworkProtection() {
        // В реальности: API вызов к сервису защиты сети
        #if DEBUG
        print("Disconnecting Network Protection...")
        #endif
    }
}



