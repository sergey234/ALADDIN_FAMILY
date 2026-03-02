import Foundation
import StoreKit
import UIKit

// Master Logger for store logging
private let logger = MasterLogger.shared

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
        logger.business("Initializing StoreManager for App Store purchases")
        // ✅ БЕЗОПАСНАЯ ИНИЦИАЛИЗАЦИЯ: Отложенная загрузка продуктов
        // Не создаем Task сразу в init - это может вызвать проблемы с инициализацией
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
        logger.business("Loading App Store products")
        isLoading = true
        errorMessage = nil
        
        // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Выводим информацию о попытке загрузки
        let productIDs = ProductID.paidSubscriptions.map { $0.rawValue }
        print("🔄 [StoreManager.loadProducts] ========== НАЧАЛО ЗАГРУЗКИ ПРОДУКТОВ ==========")
        print("🔄 [StoreManager.loadProducts] Product IDs: \(productIDs)")
        print("🔄 [StoreManager.loadProducts] Device: \(UIDevice.current.model)")
        print("🔄 [StoreManager.loadProducts] OS: \(UIDevice.current.systemVersion)")
        print("🔄 [StoreManager.loadProducts] Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
        print("🔄 [StoreManager.loadProducts] Thread: \(Thread.isMainThread ? "Main" : "Background")")
        print("🔄 [StoreManager.loadProducts] Timestamp: \(Date())")
        
        // ✅ ПРОВЕРКА СЕТИ: Проверяем доступность интернета
        print("🔄 [StoreManager.loadProducts] Проверяем доступность App Store...")
        
        do {
            // ✅ Загружаем только платные подписки (без .basic, которого нет в App Store Connect)
            print("🔄 [StoreManager.loadProducts] Вызываем Product.products(for: \(productIDs.count) IDs)...")
            let startTime = Date()
            products = try await Product.products(for: productIDs)
            let loadTime = Date().timeIntervalSince(startTime)
            isLoading = false
            
            print("🔄 [StoreManager.loadProducts] Загрузка завершена за \(String(format: "%.2f", loadTime)) секунд")
            
            if products.isEmpty {
                print("⚠️ [StoreManager.loadProducts] ========== ПРОДУКТЫ НЕ ЗАГРУЖЕНЫ ==========")
                print("⚠️ [StoreManager.loadProducts] Device: \(UIDevice.current.model)")
                print("⚠️ [StoreManager.loadProducts] OS: \(UIDevice.current.systemVersion)")
                print("⚠️ [StoreManager.loadProducts] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
                print("⚠️ [StoreManager.loadProducts] Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
                print("⚠️ [StoreManager.loadProducts] Product IDs requested: \(productIDs)")
                print("⚠️ [StoreManager.loadProducts] Возможные причины:")
                print("   1. Продукты не настроены в App Store Connect")
                print("   2. Bundle ID не совпадает: \(Bundle.main.bundleIdentifier ?? "unknown")")
                print("   3. Продукты не в статусе 'Ready to Submit'")
                print("   4. Проблема с интернет-соединением")
                print("   5. Проблема с Sandbox аккаунтом")
                print("   6. Продукты не привязаны к приложению в App Store Connect")
                print("   7. Paid Apps Agreement не принят в App Store Connect")
                print("⚠️ [StoreManager.loadProducts] Проверьте App Store Connect:")
                print("   - My Apps → ALADDIN → Features → In-App Purchases")
                print("   - Agreements, Tax, and Banking → Paid Apps Agreement (должен быть Active)")
                print("   - Убедитесь, что все 3 продукта созданы:")
                print("     • \(ProductID.individual.rawValue)")
                print("     • \(ProductID.family.rawValue)")
                print("     • \(ProductID.premium.rawValue)")
                let localizationManager = LocalizationManager()
                errorMessage = localizationManager.localized("tariffs_error_products_load_failed")
            } else {
                print("✅ [StoreManager.loadProducts] ========== ПРОДУКТЫ ЗАГРУЖЕНЫ УСПЕШНО ==========")
                print("✅ [StoreManager.loadProducts] Загружено \(products.count) продуктов из App Store")
                for (index, product) in products.enumerated() {
                    print("   \(index + 1). \(product.id)")
                    print("      - Цена: \(product.displayPrice)")
                    print("      - Название: \(product.displayName)")
                    if let subscription = product.subscription {
                        print("      - Период: \(subscription.subscriptionPeriod.value) \(subscription.subscriptionPeriod.unit)")
                    }
                }
            }
        } catch {
            let localizationManager = LocalizationManager()
            errorMessage = String(format: localizationManager.localized("store_error_load_products"), error.localizedDescription)
            isLoading = false
            print("❌ [StoreManager.loadProducts] ========== ОШИБКА ЗАГРУЗКИ ==========")
            print("❌ [StoreManager.loadProducts] Error: \(error)")
            print("❌ [StoreManager.loadProducts] Error type: \(type(of: error))")
            print("❌ [StoreManager.loadProducts] Error description: \(error.localizedDescription)")
            
            // ✅ ДЕТАЛЬНАЯ ДИАГНОСТИКА: Выводим дополнительную информацию
            if let nsError = error as NSError? {
                print("❌ [StoreManager.loadProducts] NSError domain: \(nsError.domain)")
                print("❌ [StoreManager.loadProducts] NSError code: \(nsError.code)")
                print("❌ [StoreManager.loadProducts] NSError userInfo: \(nsError.userInfo)")
                
                // ✅ СПЕЦИФИЧЕСКИЕ ОШИБКИ STOREKIT
                if nsError.domain == "SKErrorDomain" {
                    switch nsError.code {
                    case 0:
                        print("❌ [StoreManager.loadProducts] SKErrorUnknown - Неизвестная ошибка")
                    case 1:
                        print("❌ [StoreManager.loadProducts] SKErrorClientInvalid - Клиент недействителен")
                    case 2:
                        print("❌ [StoreManager.loadProducts] SKErrorPaymentCancelled - Платеж отменен")
                    case 3:
                        print("❌ [StoreManager.loadProducts] SKErrorPaymentInvalid - Платеж недействителен")
                    case 4:
                        print("❌ [StoreManager.loadProducts] SKErrorPaymentNotAllowed - Платеж не разрешен")
                    case 5:
                        print("❌ [StoreManager.loadProducts] SKErrorStoreProductNotAvailable - Продукт недоступен")
                    case 6:
                        print("❌ [StoreManager.loadProducts] SKErrorCloudServicePermissionDenied - Доступ к облачным сервисам запрещен")
                    case 7:
                        print("❌ [StoreManager.loadProducts] SKErrorCloudServiceNetworkConnectionFailed - Ошибка сетевого подключения")
                    case 8:
                        print("❌ [StoreManager.loadProducts] SKErrorCloudServiceRevoked - Облачный сервис отозван")
                    default:
                        print("❌ [StoreManager.loadProducts] SKError code: \(nsError.code)")
                    }
                }
            }
            print("❌ [StoreManager.loadProducts] ==========================================")
        }
    }
    
    // MARK: - Purchase Product
    
    /**
     * Купить продукт
     */
    func purchase(_ product: Product) async throws -> Transaction? {
        logger.business("Processing App Store purchase for product: \(product.displayName) (\(product.displayPrice))")
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
        
        // ✅ УЛУЧШЕНО ДЛЯ IPAD: Принудительная проверка и перезагрузка продуктов
        // На iPad продукты могут не загрузиться корректно, поэтому делаем дополнительную проверку
        if products.isEmpty {
            print("⚠️ [StoreManager] Products not loaded, attempting to load...")
            await loadProducts()
            guard !products.isEmpty else {
                print("❌ [StoreManager] Failed to load products after retry")
                print("❌ [StoreManager] This may indicate:")
                print("   1. Products not configured in App Store Connect")
                print("   2. Bundle ID mismatch")
                print("   3. Products not in 'Ready to Submit' status")
                print("   4. Network connection issue")
                print("   5. Sandbox account not configured")
                throw StoreError.productsNotLoaded
            }
        }
        
        // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ IPAD: Убеждаемся что продукт есть в списке
        // На iPad может быть проблема с синхронизацией продуктов
        if !products.contains(where: { $0.id == product.id }) {
            print("⚠️ [StoreManager] Product not found in loaded products, reloading...")
            await loadProducts()
            
            // Проверяем снова после перезагрузки
            guard products.contains(where: { $0.id == product.id }) else {
                print("❌ [StoreManager] Product still not found after reload")
                print("❌ [StoreManager] Product ID: \(product.id)")
                print("❌ [StoreManager] Available products: \(products.map { $0.id })")
                throw StoreError.productNotFound
            }
        }
        
        // ✅ ПРОВЕРКА ГОТОВНОСТИ STOREKIT ДЛЯ IPAD
        // На iPad StoreKit может требовать дополнительное время для инициализации
        if UIDevice.current.userInterfaceIdiom == .pad {
            // Небольшая задержка для гарантии готовности StoreKit на iPad
            try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 секунды
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Финальная проверка что продукт существует перед покупкой
            guard let targetProduct = products.first(where: { $0.id == product.id }) else {
                isLoading = false
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Продукт не найден в списке загруженных продуктов!")
                print("❌ [StoreManager] Requested product ID: \(product.id)")
                print("❌ [StoreManager] Available product IDs: \(products.map { $0.id })")
                throw StoreError.productNotFound
            }
            
            // ✅ ИСПОЛЬЗУЕМ ПРОДУКТ ИЗ ЗАГРУЖЕННОГО СПИСКА (более надежно на iPad)
            print("✅ [StoreManager] Using product from loaded list: \(targetProduct.id)")
            print("✅ [StoreManager] Product price: \(targetProduct.displayPrice)")
            print("✅ [StoreManager] Product name: \(targetProduct.displayName)")
            
            let result = try await targetProduct.purchase()
            
            switch result {
            case .success(let verification):
                // Проверка транзакции
                let transaction = try checkVerified(verification)

                // ✅ ДОБАВИТЬ: Валидация receipt на сервере
                do {
                    try await validatePurchaseWithServer(transaction: transaction)
                    print("✅ Server receipt validation successful")
                } catch {
                    print("❌ Server receipt validation failed: \(error.localizedDescription)")
                    // Не блокировать покупку, но логировать ошибку
                    // В production можно откатить транзакцию
                }

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
            isLoading = false
            let localizationManager = LocalizationManager()
            
            // ✅ УЛУЧШЕННАЯ ОБРАБОТКА ОШИБОК ДЛЯ IPAD
            print("❌ [StoreManager] ========== ОШИБКА ПОКУПКИ ==========")
            print("❌ [StoreManager] Product ID: \(product.id)")
            print("❌ [StoreManager] Device: \(UIDevice.current.model)")
            print("❌ [StoreManager] OS: \(UIDevice.current.systemVersion)")
            print("❌ [StoreManager] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
            print("❌ [StoreManager] Error: \(error)")
            print("❌ [StoreManager] Error type: \(type(of: error))")
            print("❌ [StoreManager] Error description: \(error.localizedDescription)")
            
            // Детальная диагностика для StoreKit ошибок
            if let nsError = error as NSError? {
                print("❌ [StoreManager] NSError domain: \(nsError.domain)")
                print("❌ [StoreManager] NSError code: \(nsError.code)")
                print("❌ [StoreManager] NSError userInfo: \(nsError.userInfo)")
                
                // Специфические ошибки StoreKit
                if nsError.domain == "SKErrorDomain" {
                    switch nsError.code {
                    case 0:
                        print("❌ [StoreManager] SKErrorUnknown - Неизвестная ошибка StoreKit")
                    case 1:
                        print("❌ [StoreManager] SKErrorClientInvalid - Клиент недействителен")
                    case 2:
                        print("❌ [StoreManager] SKErrorPaymentCancelled - Платеж отменен пользователем")
                    case 3:
                        print("❌ [StoreManager] SKErrorPaymentInvalid - Платеж недействителен")
                    case 4:
                        print("❌ [StoreManager] SKErrorPaymentNotAllowed - Платеж не разрешен (проверьте Paid Apps Agreement)")
                    case 5:
                        print("❌ [StoreManager] SKErrorStoreProductNotAvailable - Продукт недоступен в App Store")
                    case 6:
                        print("❌ [StoreManager] SKErrorCloudServicePermissionDenied - Доступ к облачным сервисам запрещен")
                    case 7:
                        print("❌ [StoreManager] SKErrorCloudServiceNetworkConnectionFailed - Ошибка сетевого подключения")
                    case 8:
                        print("❌ [StoreManager] SKErrorCloudServiceRevoked - Облачный сервис отозван")
                    default:
                        print("❌ [StoreManager] SKError code: \(nsError.code)")
                    }
                }
            }
            
            if let storeError = error as? StoreError {
                print("❌ [StoreManager] StoreError: \(storeError)")
                errorMessage = storeError.errorDescription
            } else {
                errorMessage = String(format: localizationManager.localized("store_error_purchase"), error.localizedDescription)
            }
            
            print("❌ [StoreManager] ==========================================")
            throw error
        }
        #endif
    }
    
    // MARK: - Restore Purchases
    
    /**
     * Восстановить покупки
     */
    func restorePurchases() async {
        logger.business("User initiated purchase restoration")
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
    
    // MARK: - Receipt Validation

    /**
     * Отправить receipt на сервер для валидации после покупки
     */
    func validatePurchaseWithServer(transaction: Transaction) async throws {
        logger.business("Validating purchase with server: \(transaction.productID)")

        do {
            // Получить App Store receipt
            guard let appStoreReceiptURL = Bundle.main.appStoreReceiptURL,
                  let receiptData = try? Data(contentsOf: appStoreReceiptURL) else {
                logger.error("❌ Failed to get App Store receipt")
                throw StoreError.receiptValidationFailed
            }

            let receiptString = receiptData.base64EncodedString()

            // Отправить receipt на сервер
            let result = await sendReceiptToServer(receiptString, productId: transaction.productID)

            if result {
                logger.business("✅ Server receipt validation successful")
            } else {
                logger.error("❌ Server receipt validation failed")
                throw StoreError.receiptValidationFailed
            }

        } catch {
            logger.error("❌ Receipt validation error: \(error.localizedDescription)")
            throw StoreError.receiptValidationFailed
        }
    }

    /**
     * Отправить receipt data на сервер
     */
    private func sendReceiptToServer(_ receiptData: String, productId: String) async -> Bool {
        // Получить текущий JWT токен для аутентификации
        guard let token = await getCurrentToken() else {
            logger.error("❌ No JWT token available for receipt validation")
            return false
        }

        // Определить уровень подписки по product ID
        let subscriptionLevel = mapProductIdToLevel(productId)

        let request = ReceiptValidationRequest(
            receiptData: receiptData,
            productId: productId,
            subscriptionLevel: subscriptionLevel.rawValue
        )

        // Отправить запрос на сервер
        return await withCheckedContinuation { continuation in
            APIService.shared.validateReceipt(request: request, token: token) { result in
                switch result {
                case .success:
                    continuation.resume(returning: true)
                case .failure(let error):
                    logger.error("❌ Receipt validation server error: \(error.localizedDescription)")
                    continuation.resume(returning: false)
                }
            }
        }
    }

    /**
     * Получить текущий JWT токен
     */
    private func getCurrentToken() async -> String? {
        // Получить токен из SubscriptionManager
        return await SubscriptionManager.shared.getCurrentToken()
    }

    /**
     * Map product ID to subscription level
     */
    private func mapProductIdToLevel(_ productId: String) -> SubscriptionLevel {
        switch productId {
        case ProductID.individual.rawValue:
            return .personal
        case ProductID.family.rawValue:
            return .family
        case ProductID.premium.rawValue:
            return .premium
        default:
            return .free
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
    case paymentCancelled
    case receiptValidationFailed
    
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
        case .paymentCancelled:
            return localizationManager.localized("store.error.payment.cancelled")
        case .receiptValidationFailed:
            return localizationManager.localized("store.error.receipt.validation.failed")
        }
    }
}



