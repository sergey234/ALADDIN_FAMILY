import Foundation
import Combine

/// Менеджер тарифов для автоматической активации защиты
/// ✅ Singleton pattern для единой точки управления
// ✅ [FIX 1] @MainActor для thread safety
@MainActor
class TariffManager: ObservableObject {
    
    // MARK: - Singleton

    static let shared = TariffManager()

    // ✅ [FIX 2] Placeholder для безопасной инициализации View
    static let placeholder = TariffManager(placeholder: true)
    
    // MARK: - Published Properties
    
    @Published var currentTariff: TariffType = .free
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties

    private let userDefaults = UserDefaults.standard
    private let tariffKey = "current_tariff_type"
    private lazy var protectionSettingsManager: ProtectionSettingsManager = {
        // ✅ [FIX 1] Ленивая инициализация для предотвращения циклических зависимостей
        // ProtectionSettingsManager создается только при первом использовании
        return ProtectionSettingsManager.shared
    }()
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Init

    private init() {
        // ✅ [FIX 1] Thread-safe инициализация
        // Все операции с UserDefaults и NotificationCenter выполняются на main thread
        DispatchQueue.main.async { [weak self] in
            self?.loadTariff()
            self?.observeTariffChanges()
        }
    }

    // ✅ [FIX 2] Placeholder init для безопасной инициализации View
    private init(placeholder: Bool) {
        // Пустая инициализация для placeholder - не загружает данные
    }
    
    // MARK: - Observe Tariff Changes
    
    /// ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ: Подписка на уведомления о покупке тарифа
    private func observeTariffChanges() {
        // Подписка на уведомление о покупке тарифа через QR
        NotificationCenter.default.addObserver(
            forName: Notification.Name("tariffPurchased"),
            object: nil,
            queue: .main
        ) { [weak self] notification in
            guard let self = self else { return }
            if let tariffType = notification.userInfo?["tariff"] as? TariffType {
                print("🔄 TariffManager: Получено уведомление о покупке тарифа: \(tariffType.rawValue)")
                self.saveTariff(tariffType)
            }
        }
        
        // Подписка на уведомление об успешной оплате через QR
        NotificationCenter.default.addObserver(
            forName: Notification.Name("paymentQRSuccess"),
            object: nil,
            queue: .main
        ) { [weak self] notification in
            guard let self = self else { return }
            if let tariffType = notification.userInfo?["tariff"] as? TariffType {
                print("🔄 TariffManager: Получено уведомление об успешной оплате: \(tariffType.rawValue)")
                self.saveTariff(tariffType)
            }
        }
        
        print("✅ TariffManager: Подписка на уведомления о покупке тарифа активирована")
    }
    
    // MARK: - Load Tariff
    
    /// Загрузить текущий тариф из UserDefaults
    func loadTariff() {
        if let rawValue = userDefaults.string(forKey: tariffKey),
           let tariff = TariffType(rawValue: rawValue) {
            currentTariff = tariff
        } else {
            // Проверяем StoreKit для определения тарифа
            determineTariffFromStoreKit()
        }
    }
    
    /// Определить тариф из StoreKit
    private func determineTariffFromStoreKit() {
        // TODO: Интегрировать с StoreManager для определения купленных продуктов
        // let storeManager = StoreManager.shared
        // if storeManager.isPurchased("premium_product_id") {
        //     currentTariff = .premium
        // } else if storeManager.isPurchased("family_product_id") {
        //     currentTariff = .family
        // } else if storeManager.isPurchased("personal_product_id") {
        //     currentTariff = .personal
        // } else {
        //     currentTariff = .free
        // }
        // saveTariff()
    }
    
    // MARK: - Save Tariff
    
    /// Сохранить тариф
    func saveTariff(_ tariffType: TariffType) {
        currentTariff = tariffType
        userDefaults.set(tariffType.rawValue, forKey: tariffKey)

        // ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ: Включаем ВСЕ доступные функции для тарифа

        // 1. Защита от угроз (100 функций) - уже работало
        protectionSettingsManager.enableForTariff(tariffType)

        // 2. Родительский контроль (32 функции) - НОВОЕ
        Task {
            do {
                try await ParentalControlManager.shared.enableForTariff(tariffType)
                print("✅ TariffManager: Родительский контроль активирован")
            } catch {
                print("❌ TariffManager: Ошибка активации родительского контроля: \(error.localizedDescription)")
            }
        }

        // 3. Дополнительные функции (10 функций) - НОВОЕ
        Task {
            do {
                try await AdditionalFeaturesManager.shared.enableForTariff(tariffType)
                print("✅ TariffManager: Дополнительные функции активированы")
            } catch {
                print("❌ TariffManager: Ошибка активации дополнительных функций: \(error.localizedDescription)")
            }
        }

        // 4. Компоненты (42 компонента) - НОВОЕ
        Task {
            do {
                try await ComponentTariffManager.shared.enableComponentsForTariff(tariffType)
                print("✅ TariffManager: Компоненты активированы")
            } catch {
                print("❌ TariffManager: Ошибка активации компонентов: \(error.localizedDescription)")
            }
        }

        print("✅ TariffManager: Тариф сохранён: \(tariffType.rawValue)")
        print("🎯 TariffManager: Запущена активация всех функций (ожидается ~184)")
    }
    
    // MARK: - Check Availability
    
    /// Проверить, доступна ли категория в текущем тарифе
    func isCategoryAvailable(_ category: ThreatProtectionCategory) -> Bool {
        return protectionSettingsManager.isCategoryAvailable(category, in: currentTariff)
    }
    
    /// Получить процент доступности для группы
    func getGroupAvailabilityPercentage(_ group: ProtectionGroup) -> Double {
        return protectionSettingsManager.getGroupAvailabilityPercentage(group, for: currentTariff)
    }
    
    // MARK: - Get Required Tariff
    
    /// Получить минимальный тариф для категории
    func getRequiredTariff(for category: ThreatProtectionCategory) -> TariffType {
        return category.requiredTariff
    }
    
    // MARK: - Upgrade Required
    
    /// Проверить, нужен ли апгрейд тарифа для категории
    func isUpgradeRequired(for category: ThreatProtectionCategory) -> Bool {
        return !isCategoryAvailable(category)
    }
    
    /// Получить следующий доступный тариф для категории
    func getNextAvailableTariff(for category: ThreatProtectionCategory) -> TariffType? {
        let required = category.requiredTariff
        let currentLevel = tariffLevel(currentTariff)
        let requiredLevel = tariffLevel(required)
        
        if currentLevel >= requiredLevel {
            return nil // Уже доступно
        }
        
        return required
    }
    
    /// Получить уровень тарифа (для сравнения)
    private func tariffLevel(_ tariffType: TariffType) -> Int {
        switch tariffType {
        case .free: return 0
        case .personal: return 1
        case .family: return 2
        case .premium: return 3
        case .ultimate: return 4
        }
    }
}

