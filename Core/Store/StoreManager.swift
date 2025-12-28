import Foundation
import StoreKit
import UIKit

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
    
    // MARK: - Free Tariff
    
    /// ID бесплатного тарифа
    static let FREE_TARIFF_ID = "free"
    
    /// Ключ для хранения статуса бесплатного тарифа в UserDefaults
    private let FREE_TARIFF_KEY = "hasFreeTariffActivated"
    
    /// Проверить активирован ли бесплатный тариф
    var hasFreeTariff: Bool {
        UserDefaults.standard.bool(forKey: FREE_TARIFF_KEY)
    }
    
    /// Активировать бесплатный тариф
    func activateFreeTariff() {
        UserDefaults.standard.set(true, forKey: FREE_TARIFF_KEY)
        print("✅ Free tariff activated")
    }
    
    // MARK: - Product IDs
    
    enum ProductID: String, CaseIterable {
        case basic = "family.aladdin.ios.subscription.basic.v2"
        case individual = "family.aladdin.ios.subscription.individual.v2"
        case family = "family.aladdin.ios.subscription.family"
        case premium = "family.aladdin.ios.subscription.premium"
        
        /// Только платные подписки (без бесплатного .basic)
        static var paidSubscriptions: [ProductID] {
            return [.individual, .family, .premium]
        }
        
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
            // ✅ Загружаем только платные подписки (без .basic, которого нет в App Store Connect)
            let productIDs = ProductID.paidSubscriptions.map { $0.rawValue }
            products = try await Product.products(for: productIDs)
            isLoading = false
            print("✅ Loaded \(products.count) products from App Store")
        } catch {
            let localizationManager = LocalizationManager()
            errorMessage = String(format: localizationManager.localized("store_error_load_products"), error.localizedDescription)
            isLoading = false
            print("❌ Error loading products: \(error)")
        }
    }
    
    // MARK: - Purchase Product
    
    /**
     * Купить продукт
     */
    func purchase(_ product: Product) async throws -> Transaction? {
        // ✅ ЛОГИРОВАНИЕ ДЛЯ IPAD: Информация об устройстве
        print("🔍 [StoreManager] Starting purchase for: \(product.id)")
        print("🔍 [StoreManager] Device: \(UIDevice.current.model)")
        print("🔍 [StoreManager] OS: \(UIDevice.current.systemVersion)")
        print("🔍 [StoreManager] Products loaded: \(products.count)")
        print("🔍 [StoreManager] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
        
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
        
        // ✅ ДОБАВЛЕНО ДЛЯ IPAD: Проверка что продукты загружены
        if products.isEmpty {
            print("⚠️ [StoreManager] Products not loaded, attempting to load...")
            await loadProducts()
            guard !products.isEmpty else {
                print("❌ [StoreManager] Failed to load products")
                throw StoreError.productsNotLoaded
            }
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
            let localizationManager = LocalizationManager()
            errorMessage = String(format: localizationManager.localized("store_error_purchase"), error.localizedDescription)
            isLoading = false
            print("❌ [StoreManager] Purchase error: \(error)")
            print("❌ [StoreManager] Error type: \(type(of: error))")
            print("❌ [StoreManager] Error description: \(error.localizedDescription)")
            if let storeError = error as? StoreError {
                print("❌ [StoreManager] StoreError: \(storeError)")
            }
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
            let localizationManager = LocalizationManager()
            errorMessage = String(format: localizationManager.localized("store_error_restore"), error.localizedDescription)
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
    
    /**
     * Проверить есть ли активная подписка (платная или бесплатная)
     */
    func hasActiveSubscription() -> Bool {
        // Сначала проверяем платную подписку
        if !purchasedProductIDs.isEmpty {
            return true
        }
        
        // Если платной нет → проверяем бесплатный тариф
        return hasFreeTariff
    }
    
    /**
     * Получить тип текущего тарифа
     */
    func currentTariffType() -> String {
        // Если есть платная подписка → возвращаем её ID
        if let active = activeSubscription {
            return active.id
        }
        
        // Если есть бесплатный тариф → возвращаем "free"
        if hasFreeTariff {
            return StoreManager.FREE_TARIFF_ID
        }
        
        // По умолчанию → нет тарифа
        return ""
    }
}

// MARK: - Store Error

enum StoreError: LocalizedError {
    case failedVerification
    case productNotFound
    case simulatorNotSupported
    case storeNotReady
    case purchaseInProgress
    case productsNotLoaded
    
    var errorDescription: String? {
        let localizationManager = LocalizationManager()
        switch self {
        case .failedVerification:
            return localizationManager.localized("store.error.verification.failed")
        case .productNotFound:
            return localizationManager.localized("store.error.product.not.found")
        case .simulatorNotSupported:
            return localizationManager.localized("store.error.simulator.not.supported")
        case .storeNotReady:
            return localizationManager.localized("store.error.store.not.ready")
        case .purchaseInProgress:
            return localizationManager.localized("store.error.purchase.in.progress")
        case .productsNotLoaded:
            return localizationManager.localized("store.error.products.not.loaded")
        }
    }
}



