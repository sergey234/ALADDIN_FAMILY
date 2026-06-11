import Foundation
import Combine

/// Менеджер настроек защиты от угроз
/// ✅ Singleton pattern для единой точки управления
@MainActor
class ProtectionSettingsManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = ProtectionSettingsManager()
    
    // MARK: - Published Properties
    
    @Published var settings: ProtectionSettings = ProtectionSettings()
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let userDefaults = UserDefaults.standard
    private let settingsKey = "protection_settings"
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Init
    
    private init() {
        loadSettings()
    }
    
    // MARK: - Load Settings
    
    /// Загрузить настройки из UserDefaults
    func loadSettings() {
        guard let data = userDefaults.data(forKey: settingsKey),
              let decoded = try? JSONDecoder().decode(ProtectionSettings.self, from: data) else {
            // Если нет сохранённых настроек, используем дефолтные
            settings = ProtectionSettings()
            return
        }
        settings = decoded
    }
    
    /// Загрузить настройки с сервера
    func loadSettingsFromServer(completion: @escaping (Result<ProtectionSettings, Error>) -> Void) {
        isLoading = true
        errorMessage = nil

        APIService.shared.getProtectionSettings { [weak self] result in
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                self.isLoading = false
                switch result {
                case .success(let response):
                    self.settings = response.settings
                    self.saveSettings()
                    completion(.success(response.settings))
                case .failure(let error):
                    self.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    // MARK: - Save Settings
    
    /// Сохранить настройки в UserDefaults
    func saveSettings() {
        guard let data = try? JSONEncoder().encode(settings) else {
            print("❌ ProtectionSettingsManager: Ошибка кодирования настроек")
            return
        }
        
        // ✅ BUILD 114: Асинхронный разрыв для предотвращения рекурсии
        // Мы используем DispatchQueue.main.async, чтобы запись в UserDefaults
        // не вызывала мгновенного уведомления во время текущего цикла отрисовки.
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.userDefaults.set(data, forKey: self.settingsKey)
            print("💾 ProtectionSettingsManager: Настройки сохранены асинхронно")
        }
    }
    
    /// Сохранить настройки на сервер
    func saveSettingsToServer(completion: @escaping (Result<Bool, Error>) -> Void) {
        isLoading = true
        errorMessage = nil
        
        // ✅ API СИНХРОНИЗАЦИЯ: Сохранение на сервер через APIService
        APIService.shared.updateProtectionSettings(settings) { [weak self] result in
            guard let self = self else { return }
            Task { @MainActor [weak self] in
                guard let self = self else { return }
                self.isLoading = false
                switch result {
                case .success(let response):
                    if response.success {
                        // Сохраняем локально после успешной синхронизации
                        self.saveSettings()
                        completion(.success(true))
                        print("✅ ProtectionSettingsManager: Настройки синхронизированы с сервером")
                    } else {
                        let error = NSError(domain: "ProtectionSettingsManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "Ошибка сохранения на сервере"])
                        self.errorMessage = error.localizedDescription
                        completion(.failure(error))
                    }
                case .failure(let error):
                    self.errorMessage = error.localizedDescription
                    // Сохраняем локально даже при ошибке сети (офлайн режим)
                    self.saveSettings()
                    print("⚠️ ProtectionSettingsManager: Ошибка синхронизации, сохранено локально: \(error.localizedDescription)")
                    completion(.failure(error))
                }
            }
        }
    }
    
    // MARK: - Enable/Disable Category
    
    /// Включить категорию защиты
    func enableCategory(_ category: ThreatProtectionCategory) {
        settings.setEnabled(category, true)
        saveSettings()
        // ✅ API СИНХРОНИЗАЦИЯ: Автоматическая синхронизация при изменении
        saveSettingsToServer { result in
            if case .failure(let error) = result {
                print("⚠️ ProtectionSettingsManager: Ошибка синхронизации при включении категории: \(error.localizedDescription)")
            }
        }
    }
    
    /// Выключить категорию защиты
    func disableCategory(_ category: ThreatProtectionCategory) {
        settings.setEnabled(category, false)
        saveSettings()
        // ✅ API СИНХРОНИЗАЦИЯ: Автоматическая синхронизация при изменении
        saveSettingsToServer { result in
            if case .failure(let error) = result {
                print("⚠️ ProtectionSettingsManager: Ошибка синхронизации при выключении категории: \(error.localizedDescription)")
            }
        }
    }
    
    /// Переключить категорию защиты
    func toggleCategory(_ category: ThreatProtectionCategory) {
        let isEnabled = settings.isEnabled(category)
        settings.setEnabled(category, !isEnabled)
        saveSettings()
        // ✅ API СИНХРОНИЗАЦИЯ: Автоматическая синхронизация при изменении
        saveSettingsToServer { result in
            if case .failure(let error) = result {
                print("⚠️ ProtectionSettingsManager: Ошибка синхронизации при переключении категории: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Enable for Tariff
    
    /// ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ: Включить категории для тарифа
    func enableForTariff(_ tariffType: TariffType) {
        var updated = false
        
        ThreatProtectionCategory.allCases.forEach { category in
            // Проверяем, доступна ли категория для тарифа
            if isCategoryAvailable(category, in: tariffType) {
                // Включаем категорию, если она ещё не включена
                if !settings.isEnabled(category) {
                    settings.setEnabled(category, true)
                    updated = true
                }
            }
        }
        
        if updated {
            saveSettings()
        }
    }
    
    /// Проверить, доступна ли категория для тарифа
    func isCategoryAvailable(_ category: ThreatProtectionCategory, in tariffType: TariffType) -> Bool {
        let requiredTariff = category.requiredTariff
        return tariffLevel(tariffType) >= tariffLevel(requiredTariff)
    }
    
    /// Получить уровень тарифа (для сравнения)
    private func tariffLevel(_ tariffType: TariffType) -> Int {
        switch tariffType {
        case .trial: return 0    // Trial уровень
        case .free: return 1     // Free уровень
        case .personal: return 2 // Personal уровень
        case .family: return 3   // Family уровень
        case .premium: return 4  // Premium уровень (максимум)
        }
    }
    
    // MARK: - Get Status
    
    /// Получить статус категории
    func getCategoryStatus(_ category: ThreatProtectionCategory) -> ProtectionCategoryStatus {
        let isEnabled = settings.isEnabled(category)
        return ProtectionCategoryStatus(
            category: category,
            isEnabled: isEnabled,
            isAvailable: true // TODO: Проверить доступность через TariffManager
        )
    }
    
    /// Получить процент доступности для группы
    func getGroupAvailabilityPercentage(_ group: ProtectionGroup, for tariffType: TariffType) -> Double {
        let categories = group.categories
        guard !categories.isEmpty else { return 0.0 }
        
        let availableCount = categories.filter { isCategoryAvailable($0, in: tariffType) }.count
        return Double(availableCount) / Double(categories.count) * 100.0
    }
}

// MARK: - Protection Category Status

struct ProtectionCategoryStatus {
    let category: ThreatProtectionCategory
    let isEnabled: Bool
    let isAvailable: Bool
}

