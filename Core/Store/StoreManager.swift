import Foundation
import StoreKit

/**
 * 💰 Store Manager
 * Управление покупками в App Store (StoreKit 2)
 * In-App Purchase для iOS
 */

@MainActor
class StoreManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var products: [Product] = []
    @Published var purchasedProductIDs: Set<String> = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Product IDs
    
    enum ProductID: String, CaseIterable {
        case basic = "family.aladdin.ios.subscription.basic.v2"
        case individual = "family.aladdin.ios.subscription.individual.v2"
        case family = "family.aladdin.ios.subscription.family"
        case premium = "family.aladdin.ios.subscription.premium"
        
        var displayName: String {
            switch self {
            case .basic: return "Базовый"
            case .individual: return "Индивидуальный"
            case .family: return "Семейный"
            case .premium: return "Премиум"
            }
        }
        
        var description: String {
            switch self {
            case .basic: return "1 устройство, базовая защита"
            case .individual: return "1 устройство, полная защита, AI помощник"
            case .family: return "До 5 устройств, родительский контроль"
            case .premium: return "До 10 устройств, все функции, приоритетная поддержка"
            }
        }
        
        var features: [String] {
            switch self {
            case .basic:
                return ["1 устройство", "Базовая защита", "Ограниченная аналитика"]
            case .individual:
                return ["1 устройство", "Полная защита", "Расширенная аналитика", "AI помощник"]
            case .family:
                return ["До 5 устройств", "Полная защита", "Расширенная аналитика", "AI помощник", "Родительский контроль"]
            case .premium:
                return ["До 10 устройств", "Все функции", "Приоритетная поддержка", "Эксклюзивные возможности"]
            }
        }
    }
    
    // MARK: - Init
    
    init() {
        // ✅ БЕЗОПАСНАЯ ИНИЦИАЛИЗАЦИЯ: Отложенная загрузка продуктов
        // Не создаем Task сразу в init - это может вызвать проблемы с инициализацией
        print("🔍 StoreManager.init: Инициализация начата")
    }
    
    /**
     * Начать загрузку продуктов (вызывается явно после инициализации)
     */
    func startLoading() {
        print("🔍 StoreManager.startLoading: Начало загрузки продуктов")
        
        // ✅ ЗАЩИТА: Проверяем симулятор перед загрузкой
        #if targetEnvironment(simulator)
        print("⚠️ StoreManager.startLoading: Симулятор - пропускаем загрузку продуктов")
        return
        #else
        Task { @MainActor in
            await loadProducts()
            await updatePurchasedProducts()
            await listenForTransactions()
        }
        #endif
    }
    
    // MARK: - Load Products
    
    /**
     * Загрузить продукты из App Store
     */
    func loadProducts() async {
        isLoading = true
        
        do {
            let productIDs = ProductID.allCases.map { $0.rawValue }
            products = try await Product.products(for: productIDs)
            isLoading = false
            print("✅ Loaded \(products.count) products from App Store")
        } catch {
            errorMessage = "Ошибка загрузки продуктов: \(error.localizedDescription)"
            isLoading = false
            print("❌ Error loading products: \(error)")
        }
    }
    
    // MARK: - Purchase Product
    
    /**
     * Купить продукт
     */
    func purchase(_ product: Product) async throws -> Transaction? {
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка симулятора перед вызовом purchase()
        #if targetEnvironment(simulator)
        throw StoreError.simulatorNotSupported
        #else
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка что продукт валиден
        guard !product.id.isEmpty else {
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: Product ID пустой!")
            throw StoreError.productNotFound
        }
        
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка что StoreKit готов
        guard !isLoading else {
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: StoreKit уже выполняет операцию!")
            throw StoreError.storeNotReady
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка что продукт существует перед покупкой
            guard products.contains(where: { $0.id == product.id }) else {
                isLoading = false
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Продукт не найден в списке загруженных продуктов!")
                throw StoreError.productNotFound
            }
            
            let result = try await product.purchase()
            
            switch result {
            case .success(let verification):
                // Проверка транзакции
                let transaction = try checkVerified(verification)
                
                // Обновить purchased products
                await updatePurchasedProducts()
                
                // Завершить транзакцию
                await transaction.finish()
                
                isLoading = false
                print("✅ Purchase successful: \(product.id)")
                return transaction
                
            case .userCancelled:
                isLoading = false
                print("⚠️ User cancelled purchase")
                return nil
                
            case .pending:
                isLoading = false
                print("⏳ Purchase pending")
                return nil
                
            @unknown default:
                isLoading = false
                return nil
            }
        } catch {
            errorMessage = "Ошибка покупки: \(error.localizedDescription)"
            isLoading = false
            print("❌ Purchase error: \(error)")
            throw error
        }
        #endif
    }
    
    // MARK: - Restore Purchases
    
    /**
     * Восстановить покупки
     */
    func restorePurchases() async {
        isLoading = true
        
        do {
            try await AppStore.sync()
            await updatePurchasedProducts()
            isLoading = false
            print("✅ Purchases restored")
        } catch {
            errorMessage = "Ошибка восстановления: \(error.localizedDescription)"
            isLoading = false
            print("❌ Restore error: \(error)")
        }
    }
    
    // MARK: - Update Purchased Products
    
    /**
     * Обновить список купленных продуктов
     */
    func updatePurchasedProducts() async {
        var purchasedIDs: Set<String> = []
        
        for await result in Transaction.currentEntitlements {
            do {
                let transaction = try checkVerified(result)
                
                // Проверка что подписка активна
                if transaction.revocationDate == nil {
                    purchasedIDs.insert(transaction.productID)
                }
            } catch {
                print("❌ Failed to verify transaction: \(error)")
            }
        }
        
        purchasedProductIDs = purchasedIDs
        print("✅ Updated purchased products: \(purchasedIDs)")
    }
    
    // MARK: - Listen for Transactions
    
    /**
     * Слушать новые транзакции
     */
    func listenForTransactions() async {
        for await result in Transaction.updates {
            do {
                let transaction = try checkVerified(result)
                await updatePurchasedProducts()
                await transaction.finish()
                print("✅ Transaction update: \(transaction.productID)")
            } catch {
                print("❌ Transaction verification failed: \(error)")
            }
        }
    }
    
    // MARK: - Check Verified
    
    /**
     * Проверить подлинность транзакции
     */
    func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }
    
    // MARK: - Helper Methods
    
    /**
     * Проверить куплен ли продукт
     */
    func isPurchased(_ productID: String) -> Bool {
        purchasedProductIDs.contains(productID)
    }
    
    /**
     * Получить продукт по ID
     */
    func product(for id: ProductID) -> Product? {
        products.first { $0.id == id.rawValue }
    }
    
    /**
     * Получить активную подписку
     */
    var activeSubscription: Product? {
        products.first { isPurchased($0.id) }
    }
}

// MARK: - Store Error

enum StoreError: LocalizedError {
    case failedVerification
    case productNotFound
    case simulatorNotSupported
    case storeNotReady
    case purchaseInProgress
    
    var errorDescription: String? {
        switch self {
        case .failedVerification:
            return "Не удалось проверить покупку"
        case .productNotFound:
            return "Продукт не найден"
        case .simulatorNotSupported:
            return "In-App Purchase недоступен в симуляторе. Используйте реальное устройство."
        case .storeNotReady:
            return "StoreKit не готов. Пожалуйста, подождите."
        case .purchaseInProgress:
            return "Покупка уже выполняется. Пожалуйста, подождите."
        }
    }
}



