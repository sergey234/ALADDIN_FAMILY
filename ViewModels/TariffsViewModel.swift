import Foundation
import Combine
import StoreKit

/**
 * 💳 Tariffs View Model
 * Логика для экрана тарифов
 * ИНТЕГРИРОВАН СО STOREKIT 2!
 */

@MainActor
class TariffsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var tariffs: [Tariff] = []
    @Published var selectedTariff: Tariff?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var isPurchaseSuccessful: Bool = false
    
    // MARK: - Store Manager
    
    private let storeManager: StoreManager
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Init
    
    @MainActor
    init(storeManager: StoreManager) {
        self.storeManager = storeManager
        
        // Подписка на изменения продуктов
        storeManager.$products
            .sink { [weak self] products in
                self?.updateTariffs(from: products)
            }
            .store(in: &cancellables)
        
        // Подписка на изменения купленных продуктов
        storeManager.$purchasedProductIDs
            .sink { [weak self] _ in
                self?.updatePurchaseStatus()
            }
            .store(in: &cancellables)
        
        // Загрузить продукты
        Task {
            await loadProducts()
        }
    }
    
    // MARK: - Load Products
    
    /**
     * Загрузить продукты из App Store
     */
    func loadProducts() async {
        isLoading = true
        await storeManager.loadProducts()
        isLoading = false
    }
    
    // MARK: - Update Tariffs
    
    /**
     * Обновить список тарифов из StoreKit продуктов
     */
    private func updateTariffs(from products: [Product]) {
        tariffs = StoreManager.ProductID.allCases.compactMap { productID in
            guard let product = products.first(where: { $0.id == productID.rawValue }) else {
                return nil
            }
            
            return Tariff(
                id: product.id,
                title: productID.displayName,
                price: product.displayPrice,
                period: getPeriod(from: product),
                features: productID.features,
                product: product,
                isPurchased: storeManager.isPurchased(product.id)
            )
        }
        
        // Выбрать первый тариф по умолчанию
        if selectedTariff == nil {
            selectedTariff = tariffs.first
        }
    }
    
    /**
     * Обновить статус покупок
     */
    private func updatePurchaseStatus() {
        for index in tariffs.indices {
            tariffs[index].isPurchased = storeManager.isPurchased(tariffs[index].id)
        }
    }
    
    /**
     * Получить период подписки
     */
    private func getPeriod(from product: Product) -> String {
        if let subscription = product.subscription {
            switch subscription.subscriptionPeriod.unit {
            case .day:
                return "в день"
            case .week:
                return "в неделю"
            case .month:
                return "в месяц"
            case .year:
                return "в год"
            @unknown default:
                return "подписка"
            }
        }
        return "навсегда"
    }
    
    // MARK: - Select Tariff
    
    /**
     * Выбрать тариф
     */
    func selectTariff(_ tariff: Tariff) {
        selectedTariff = tariff
        print("Selected tariff: \(tariff.title)")
    }
    
    // MARK: - Purchase Tariff
    
    /**
     * Купить выбранный тариф
     * В России → открывает PaymentQRScreen
     * За границей → использует IAP (App Store)
     */
    func purchaseSelectedTariff() async {
        guard let selectedTariff = selectedTariff else {
            errorMessage = "Выберите тариф"
            return
        }
        
        // Проверяем регион
        if AppConfig.useAlternativePayments {
            // Россия → QR оплата
            // Навигация к PaymentQRScreen будет обработана в UI
            print("🇷🇺 Российский регион: используем QR оплату")
            return
        }
        
        // Не Россия → IAP (App Store)
        isLoading = true
        errorMessage = nil
        isPurchaseSuccessful = false
        
        do {
            let transaction = try await storeManager.purchase(selectedTariff.product)
            
            if transaction != nil {
                isPurchaseSuccessful = true
                print("✅ IAP Purchase successful!")
            }
            
            isLoading = false
        } catch {
            errorMessage = "Ошибка покупки: \(error.localizedDescription)"
            isLoading = false
            print("❌ IAP Purchase failed: \(error)")
        }
    }
    
    /**
     * Проверка, нужно ли использовать QR оплату
     */
    func shouldUseQRPayment() -> Bool {
        return AppConfig.useAlternativePayments
    }
    
    // MARK: - Restore Purchases
    
    /**
     * Восстановить покупки
     */
    func restorePurchases() async {
        isLoading = true
        errorMessage = nil
        
        await storeManager.restorePurchases()
        
        isLoading = false
        print("✅ Purchases restored")
    }
    
    // MARK: - Get Active Subscription
    
    /**
     * Получить активную подписку
     */
    func getActiveSubscription() -> Tariff? {
        return tariffs.first { $0.isPurchased }
    }
}

// MARK: - Tariff Model

struct Tariff: Identifiable {
    let id: String
    let title: String
    let price: String
    let period: String
    let features: [String]
    let product: Product
    var isPurchased: Bool
}

