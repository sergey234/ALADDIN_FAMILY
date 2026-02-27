import Foundation
import Combine

// Импорты для доступа к типам из других модулей
/**
 * 📊 Additional Features Manager
 * Менеджер дополнительных функций (10 функций: защита сети, AI, реклама и т.д.)
 * Автоматическая активация при покупке тарифа
 */
class AdditionalFeaturesManager: ObservableObject {
    static let shared = AdditionalFeaturesManager()
    // MARK: - Dependencies
    private let userDefaults: UserDefaults
    private let apiService: APIService
    // MARK: - Published Properties
    @Published var activatedFeatures: Set<String> = []
    // MARK: - Private Properties
    private let activatedFeaturesKey = "additional_features_activated"
    private var cancellables = Set<AnyCancellable>()
    // MARK: - Initialization
    init(
        userDefaults: UserDefaults = .standard,
        apiService: APIService = APIService.shared
    ) {
        self.userDefaults = userDefaults
        self.apiService = apiService
        // Загружаем активированные функции из UserDefaults
        loadActivatedFeatures()
    }
    // MARK: - Public Methods
    /// Активировать дополнительные функции для тарифа
    func enableForTariff(_ tariffType: TariffType) async throws {
        let featuresToActivate = getFeaturesForTariff(tariffType)
        print("🔄 AdditionalFeaturesManager: Активация \(featuresToActivate.count) дополнительных функций для \(tariffType.rawValue)")
        // Активируем каждую функцию
        for feature in featuresToActivate {
            try await enableFeature(feature)
        }
        print("✅ AdditionalFeaturesManager: Активировано \(featuresToActivate.count) дополнительных функций")
    }
    /// Проверить, активирована ли функция
    func isFeatureActivated(_ featureId: String) -> Bool {
        return activatedFeatures.contains(featureId)
    }
    /// Получить все активированные функции
    func getActivatedFeatures() -> [AdditionalFeature] {
        let allFeatures = getAllAvailableFeatures()
        return allFeatures.filter { isFeatureActivated($0.id) }
    }
    // MARK: - Private Methods
    /// Активировать конкретную функцию
    private func enableFeature(_ feature: AdditionalFeature) async throws {
        // Проверяем, не активирована ли уже
        guard !isFeatureActivated(feature.id) else {
            print("⚠️ AdditionalFeaturesManager: Функция \(feature.id) уже активирована")
            return
        }

        // TODO: Реализовать реальный API вызов
        // try await apiService.enableAdditionalFeature(featureId: feature.id)

        // Пока что просто симулируем успешную активацию
        self.activatedFeatures.insert(feature.id)
        self.saveActivatedFeatures()
        print("✅ AdditionalFeaturesManager: Функция \(feature.id) активирована")
    }
    /// Получить функции для тарифа
    private func getFeaturesForTariff(_ tariffType: TariffType) -> [AdditionalFeature] {
        return tariffType.allAdditionalFeatures()
    }
    /// Получить все доступные дополнительные функции
    private func getAllAvailableFeatures() -> [AdditionalFeature] {
        var allFeatures: [AdditionalFeature] = []
        // Собираем из всех тарифов (вручную, так как TariffType не CaseIterable)
        let allTariffs: [TariffType] = [.free, .personal, .family, .premium, .ultimate]
        for tariff in allTariffs {
            allFeatures.append(contentsOf: tariff.allAdditionalFeatures())
        }
        // Убираем дубликаты
        return Array(Set(allFeatures))
    }
    /// Загрузить активированные функции из UserDefaults
    private func loadActivatedFeatures() {
        if let savedFeatures = userDefaults.array(forKey: activatedFeaturesKey) as? [String] {
            activatedFeatures = Set(savedFeatures)
        }
    }

    /// Сохранить активированные функции в UserDefaults
    private func saveActivatedFeatures() {
        userDefaults.set(Array(activatedFeatures), forKey: activatedFeaturesKey)
    }
}
