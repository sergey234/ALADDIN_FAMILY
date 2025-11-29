import SwiftUI
import Combine

/// 🧠 Main View Model
/// Логика для главного экрана
/// Управляет состоянием VPN, функций, статистикой
@MainActor
class MainViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isVPNEnabled: Bool = true
    @Published var familyMembers: Int = 4 // Дефолтное значение (fallback)
    @Published var threatsBlocked: Int = 47 // Дефолтное значение (fallback)
    @Published var devicesProtected: Int = 8 // Дефолтное значение (fallback)
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var lastUpdateTime: Date?
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    private let apiService: APIService
    
    // MARK: - Init
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
        // Загружаем данные при инициализации
        loadDashboardData()
    }
    
    // MARK: - Public Methods
    
    /// ✅ ИНТЕГРАЦИЯ С API: Загрузка данных дашборда из реального API
    func loadDashboardData() {
        // Предотвращаем множественные одновременные запросы
        guard !isLoading else {
            print("⚠️ MainViewModel: Загрузка уже выполняется, пропускаем запрос")
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        print("🔄 MainViewModel: Загружаем данные дашборда из API...")
        
        // ✅ ТАЙМАУТ: Если запрос не успевает за 5 секунд, показываем fallback данные
        let timeoutWorkItem = DispatchWorkItem { [weak self] in
            guard let self = self else { return }
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                if self.isLoading {
                    print("⚠️ MainViewModel: Таймаут загрузки данных (5 секунд)")
                    print("   Используются дефолтные значения (fallback)")
                    self.isLoading = false
                    self.errorMessage = "Таймаут загрузки данных. Проверьте подключение к интернету."
                    
                    // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ: Отправляем уведомление для обновления UI
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0, execute: timeoutWorkItem)
        
        // ✅ РЕАЛЬНЫЙ API ВЫЗОВ: Загружаем статистику семьи
        apiService.getFamilyStats { [weak self] result in
            guard let self = self else { return }
            
            // Отменяем таймаут если запрос успел
            timeoutWorkItem.cancel()
            
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                
                self.isLoading = false
                
                switch result {
                case .success(let stats):
                    // ✅ ОБНОВЛЯЕМ ДАННЫЕ ИЗ API
                    self.familyMembers = stats.totalMembers
                    self.devicesProtected = stats.totalDevices
                    self.threatsBlocked = stats.totalThreats
                    self.lastUpdateTime = Date()
                    self.errorMessage = nil // Очищаем ошибку при успехе
                    
                    print("✅ MainViewModel: Данные загружены успешно:")
                    print("   - Членов семьи: \(stats.totalMembers)")
                    print("   - Устройств: \(stats.totalDevices)")
                    print("   - Угроз заблокировано: \(stats.totalThreats)")
                    print("   - Уровень защиты: \(stats.protectionLevel)")
                    
                    // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ: Отправляем уведомление для обновления UI
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                    
                case .failure(let error):
                    // ❌ ОШИБКА: Сохраняем сообщение, но не меняем данные (fallback значения остаются)
                    self.errorMessage = error.localizedDescription
                    print("❌ MainViewModel: Ошибка загрузки данных: \(error.localizedDescription)")
                    print("   Используются дефолтные значения (fallback)")
                    
                    // ✅ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ: Отправляем уведомление для обновления UI
                    NotificationCenter.default.post(name: NSNotification.Name("MainViewModelDataUpdated"), object: nil)
                }
            }
        }
    }
    
    /// Переключение VPN
    func toggleVPN() {
        isVPNEnabled.toggle()
        
        // Haptic feedback
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // API вызов для включения/выключения VPN
        if isVPNEnabled {
            connectVPN()
        } else {
            disconnectVPN()
        }
    }
    
    /// Обновление статистики (принудительное)
    func refreshStats() {
        print("🔄 MainViewModel: Принудительное обновление статистики")
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
            print("🔄 MainViewModel: Автообновление данных (onAppear)")
            loadDashboardData()
        } else {
            print("ℹ️ MainViewModel: Данные актуальны, пропускаем обновление")
        }
    }
    
    /// Открыть семью
    func openFamily() {
        print("Navigation to Family Screen")
    }
    
    /// Открыть VPN
    func openVPN() {
        print("Navigation to VPN Screen")
    }
    
    /// Открыть аналитику
    func openAnalytics() {
        print("Navigation to Analytics Screen")
    }
    
    /// Открыть AI
    func openAI() {
        print("Navigation to AI Assistant Screen")
    }
    
    // MARK: - Private Methods
    
    private func connectVPN() {
        // В реальности: API вызов к VPN сервису
        print("Connecting to VPN...")
    }
    
    private func disconnectVPN() {
        // В реальности: API вызов к VPN сервису
        print("Disconnecting VPN...")
    }
}



