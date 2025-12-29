import Foundation
import Combine
import StoreKit
import UserNotifications
import SwiftUI

// Импортируем необходимые типы
// StoreManager находится в Core/Store/StoreManager.swift
// AppConfig находится в Core/Config/AppConfig.swift
// NotificationManager находится в Core/Notifications/NotificationManager.swift
// TariffType определен в Shared/Models/ThreatProtectionCategory.swift как typealias TariffType = TariffsScreen.TariffType

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
    
    init(storeManager: StoreManager? = nil) {
        self.storeManager = storeManager ?? StoreManager()
        
        print("🔍 TariffsViewModel.init: Начало инициализации")
        
        // Подписка на изменения продуктов
        self.storeManager.$products
            .sink { [weak self] products in
                self?.updateTariffs(from: products)
            }
            .store(in: &cancellables)
        
        // Подписка на изменения купленных продуктов
        self.storeManager.$purchasedProductIDs
            .sink { [weak self] _ in
                self?.updatePurchaseStatus()
            }
            .store(in: &cancellables)
        
        // ✅ БЕЗОПАСНАЯ ЗАГРУЗКА: Откладываем загрузку продуктов
        // Используем DispatchQueue для гарантии выполнения на main thread после инициализации
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            // Начинаем загрузку продуктов
            self.storeManager.startLoading()
            
            // Загрузить продукты
            Task { @MainActor in
                await self.loadProducts()
            }
        }
        
        // ✅ ДОПОЛНИТЕЛЬНАЯ ЗАГРУЗКА: Загружаем продукты при создании ViewModel
        // Это гарантирует, что продукты будут загружены до попытки покупки
        Task { @MainActor in
            // Небольшая задержка для гарантии готовности StoreKit
            try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 секунды
            if self.storeManager.products.isEmpty {
                print("🔄 [TariffsViewModel] Продукты пусты при инициализации, загружаем...")
                await self.loadProducts()
            }
        }
        
        print("✅ TariffsViewModel.init: Инициализация завершена")
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
    
    /**
     * Получить количество загруженных продуктов (для проверки в UI)
     */
    func getProductsCount() async -> Int {
        return storeManager.products.count
    }
    
    // MARK: - Update Tariffs
    
    /**
     * Обновить список тарифов из StoreKit продуктов
     */
    private func updateTariffs(from products: [Product]) {
        // ✅ Загружаем только платные подписки (без .basic, которого нет в App Store Connect)
        tariffs = StoreManager.ProductID.paidSubscriptions.compactMap { productID in
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
                isPurchased: storeManager.isPurchased(product.id),
                periodMonths: 1,
                originalPrice: nil,
                discountPercent: nil,
                monthlyPrice: product.displayPrice,
                savings: nil
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
     * В России → открывает PaymentQRScreen (обрабатывается в UI)
     * За границей → использует IAP (App Store)
     */
    func purchaseSelectedTariff() async {
        guard let selectedTariff = selectedTariff else {
            let localizationManager = LocalizationManager()
            errorMessage = localizationManager.localized("tariffs_error_select_tariff")
            return
        }
        await purchaseTariff(selectedTariff)
    }
    
    /**
     * Купить конкретный тариф (перегрузка для прямого вызова)
     */
    func purchaseSelectedTariff(tariff: Tariff) async {
        await purchaseTariff(tariff)
    }
    
    /**
     * Основная функция покупки тарифа
     */
    private func purchaseTariff(_ tariff: Tariff) async {
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверяем валидность тарифа
        guard !tariff.id.isEmpty, !tariff.title.isEmpty else {
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: НЕВАЛИДНЫЙ ТАРИФ!")
            print("   - id.isEmpty: \(tariff.id.isEmpty)")
            print("   - title.isEmpty: \(tariff.title.isEmpty)")
            let localizationManager = LocalizationManager()
            errorMessage = localizationManager.localized("tariffs_error_invalid_tariff")
            return
        }
        
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Бесплатный тариф не покупается через IAP
        if tariff.id == "free" || tariff.id == StoreManager.FREE_TARIFF_ID {
            print("✅ Бесплатный тариф - активируем без покупки")
            storeManager.activateFreeTariff()
            isPurchaseSuccessful = true
            isLoading = false
            
            // Обновляем статус тарифа
            if let index = tariffs.firstIndex(where: { $0.id == tariff.id }) {
                tariffs[index].isPurchased = true
            }
            
            // Активируем тариф
            if let tariffType = mapTariffToTariffType(tariff) {
                TariffManager.shared.saveTariff(tariffType)
                print("✅ TariffManager: Бесплатный тариф активирован")
            }
            return
        }
        
        // Проверяем регион
        if AppConfig.useAlternativePayments {
            // Россия → QR оплата обрабатывается в UI
            print("🇷🇺 Российский регион: QR оплата обрабатывается в UI")
            return
        }
        
        // 🌍 Не Россия → IAP (App Store)
        print("🌍 [TariffsViewModel] ========== ЗАПУСК IAP ПОКУПКИ ==========")
        print("🌍 [TariffsViewModel] Тариф: \(tariff.title) (ID: \(tariff.id))")
        print("🌍 [TariffsViewModel] Device: \(UIDevice.current.model)")
        print("🌍 [TariffsViewModel] OS: \(UIDevice.current.systemVersion)")
        print("🌍 [TariffsViewModel] Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
        print("🔍 [TariffsViewModel] DEBUG: Проверяем storeManager...")
        print("   - storeManager.products.count: \(storeManager.products.count)")
        print("   - storeManager.isLoading: \(storeManager.isLoading)")
        print("   - storeManager.purchasedProductIDs: \(storeManager.purchasedProductIDs)")
        
        // ✅ КРИТИЧЕСКАЯ ПРОВЕРКА: StoreKit может быть недоступен
        // Проверяем доступность StoreKit перед использованием
        #if targetEnvironment(simulator)
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: StoreKit вызывается в симуляторе!")
        let localizationManager = LocalizationManager()
        errorMessage = localizationManager.localized("store.error.simulator.not.supported")
        return
        #else
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка что StoreManager не выполняет другую операцию
        guard !storeManager.isLoading else {
            let localizationManager = LocalizationManager()
            errorMessage = localizationManager.localized("tariffs_error_loading_products")
            print("⚠️ StoreManager уже загружает продукты")
            return
        }
        
        // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Проверка что продукты загружены
        if storeManager.products.isEmpty {
            let localizationManager = LocalizationManager()
            errorMessage = localizationManager.localized("tariffs_error_products_not_loaded")
            print("⚠️ [TariffsViewModel] ========== ПРОДУКТЫ НЕ ЗАГРУЖЕНЫ ПЕРЕД ПОКУПКОЙ ==========")
            print("⚠️ [TariffsViewModel] Попытка покупки тарифа: \(tariff.title) (ID: \(tariff.id))")
            print("⚠️ [TariffsViewModel] Bundle ID: \(Bundle.main.bundleIdentifier ?? "unknown")")
            print("⚠️ [TariffsViewModel] Product IDs для загрузки: \(StoreManager.ProductID.paidSubscriptions.map { $0.rawValue })")
            print("⚠️ [TariffsViewModel] StoreManager.isLoading: \(storeManager.isLoading)")
            print("⚠️ [TariffsViewModel] Пытаемся загрузить продукты...")
            
            // Пытаемся загрузить продукты
            await storeManager.loadProducts()
            
            // Проверяем снова после загрузки
            guard !storeManager.products.isEmpty else {
                let localizationManager = LocalizationManager()
                errorMessage = localizationManager.localized("tariffs_error_products_load_failed")
                print("❌ [TariffsViewModel] ========== ПРОДУКТЫ ВСЕ ЕЩЕ НЕ ЗАГРУЖЕНЫ ==========")
                print("❌ [TariffsViewModel] Продукты все еще не загружены после попытки перезагрузки")
                print("❌ [TariffsViewModel] Проверьте:")
                print("   1. Продукты настроены в App Store Connect")
                print("   2. Bundle ID совпадает: \(Bundle.main.bundleIdentifier ?? "unknown")")
                print("   3. Продукты в статусе 'Ready to Submit'")
                print("   4. Интернет-соединение работает")
                print("   5. Sandbox аккаунт настроен")
                print("   6. Вы вошли в Sandbox аккаунт на устройстве")
                print("❌ [TariffsViewModel] ==========================================")
                return
            }
            
            print("✅ [TariffsViewModel] Продукты успешно загружены после перезагрузки")
            print("✅ [TariffsViewModel] Загружено продуктов: \(storeManager.products.count)")
        }
        
        isLoading = true
        errorMessage = nil
        isPurchaseSuccessful = false
        
        // Диагностика: выводим информацию о продуктах (безопасно)
        let productIds = storeManager.products.isEmpty ? "нет продуктов" : storeManager.products.map { $0.id }.joined(separator: ", ")
        print("🔍 Доступные продукты из StoreKit: \(productIds)")
        print("🔍 Ищем ProductID для tariff.id: '\(tariff.id)'")
        
        // Способ 1: Если тариф уже имеет продукт (из StoreKit), используем его
        if let existingProduct = tariff.product {
            print("✅ Найден продукт напрямую из тарифа: \(existingProduct.id)")
            print("🔍 [TariffsViewModel] Device: \(UIDevice.current.model)")
            print("🔍 [TariffsViewModel] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
            do {
                let transaction = try await storeManager.purchase(existingProduct)
                
                if transaction != nil {
                    isPurchaseSuccessful = true
                    isLoading = false
                    print("✅ IAP Purchase successful: \(tariff.title)")
                    
                    // Обновляем статус тарифа
                    if let index = tariffs.firstIndex(where: { $0.id == tariff.id }) {
                        tariffs[index].isPurchased = true
                    }
                    
                    // ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ: Сохраняем тариф и активируем защиту
                    if let tariffType = mapTariffToTariffType(tariff) {
                        TariffManager.shared.saveTariff(tariffType)
                        print("✅ TariffManager: Тариф активирован: \(tariffType.rawValue)")
                        
                        // Отправляем уведомление о покупке
                        NotificationCenter.default.post(
                            name: Notification.Name("tariffPurchased"),
                            object: nil,
                            userInfo: ["tariff": tariffType]
                        )
                    }
                    
                    // ✅ ПЛАНИРОВАНИЕ УВЕДОМЛЕНИЙ О ПОДПИСКЕ
                    // Вычисляем дату окончания подписки (30 дней от текущей даты)
                    if let endDate = calculateSubscriptionEndDate() {
                        NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
                        print("✅ Уведомления о подписке запланированы до \(endDate)")
                    }
                } else {
                    isLoading = false
                    print("⚠️ IAP Purchase cancelled or pending")
                }
            } catch {
                isLoading = false
                
                // ✅ УЛУЧШЕНИЕ: Специальная обработка для productsNotLoaded
                let localizationManager = LocalizationManager()
                if let storeError = error as? StoreError, storeError == .productsNotLoaded {
                    errorMessage = localizationManager.localized("tariffs_error_products_load_failed")
                    print("❌ [TariffsViewModel] Products not loaded error")
                } else {
                    let errorDesc = error.localizedDescription
                    errorMessage = String(format: localizationManager.localized("store_error_purchase"), errorDesc)
                    print("❌ [TariffsViewModel] IAP Purchase failed: \(errorDesc)")
                }
                
                print("❌ [TariffsViewModel] Error type: \(type(of: error))")
                print("❌ [TariffsViewModel] Device: \(UIDevice.current.model)")
                print("❌ [TariffsViewModel] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
                if let storeError = error as? StoreError {
                    print("❌ [TariffsViewModel] StoreError: \(storeError)")
                }
            }
            return
        }
        
        // Способ 2: Ищем по ID через маппинг
        if let productID = findProductID(for: tariff.id) {
            print("🔍 Найден ProductID: \(productID.rawValue)")
            print("🔍 Ищем продукт в StoreManager...")
            
            if let product = storeManager.product(for: productID) {
                print("✅ Продукт найден: \(product.id)")
                
                // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: Дополнительная проверка продукта
                guard !product.id.isEmpty else {
                    isLoading = false
                    let localizationManager = LocalizationManager()
                    errorMessage = localizationManager.localized("tariffs_error_invalid_tariff")
                    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Product ID пустой!")
                    return
                }
                
                do {
                    print("🔍 [TariffsViewModel] Device: \(UIDevice.current.model)")
                    print("🔍 [TariffsViewModel] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
                    let transaction = try await storeManager.purchase(product)
                    
                    if transaction != nil {
                        isPurchaseSuccessful = true
                        isLoading = false
                        print("✅ IAP Purchase successful: \(tariff.title)")
                        
                        // Обновляем статус тарифа
                        if let index = tariffs.firstIndex(where: { $0.id == tariff.id }) {
                            tariffs[index].isPurchased = true
                        }
                        
                        // ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ: Сохраняем тариф и активируем защиту
                        if let tariffType = mapTariffToTariffType(tariff) {
                            TariffManager.shared.saveTariff(tariffType)
                            print("✅ TariffManager: Тариф активирован: \(tariffType.rawValue)")
                            
                            // Отправляем уведомление о покупке
                            NotificationCenter.default.post(
                                name: Notification.Name("tariffPurchased"),
                                object: nil,
                                userInfo: ["tariff": tariffType]
                            )
                        }
                        
                        // ✅ ПЛАНИРОВАНИЕ УВЕДОМЛЕНИЙ О ПОДПИСКЕ (при продлении)
                        // Вычисляем дату окончания подписки (30 дней от текущей даты)
                        if let endDate = calculateSubscriptionEndDate() {
                            NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
                            print("✅ Уведомления о подписке запланированы до \(endDate)")
                        }
                    } else {
                        isLoading = false
                        print("⚠️ IAP Purchase cancelled or pending")
                    }
                } catch {
                    isLoading = false
                    
                    // ✅ УЛУЧШЕНИЕ: Специальная обработка для productsNotLoaded
                    let localizationManager = LocalizationManager()
                    if let storeError = error as? StoreError, storeError == .productsNotLoaded {
                        errorMessage = localizationManager.localized("tariffs_error_products_load_failed")
                        print("❌ [TariffsViewModel] Products not loaded error")
                    } else {
                        let errorDesc = error.localizedDescription
                        errorMessage = String(format: localizationManager.localized("store_error_purchase"), errorDesc)
                        print("❌ [TariffsViewModel] IAP Purchase failed: \(errorDesc)")
                    }
                    
                    print("❌ [TariffsViewModel] Error type: \(type(of: error))")
                    print("❌ [TariffsViewModel] Device: \(UIDevice.current.model)")
                    print("❌ [TariffsViewModel] Is iPad: \(UIDevice.current.userInterfaceIdiom == .pad)")
                    if let storeError = error as? StoreError {
                        print("❌ [TariffsViewModel] StoreError: \(storeError)")
                    }
                }
            } else {
                // Продукт не загружен из App Store
                isLoading = false
                let localizationManager = LocalizationManager()
                errorMessage = localizationManager.localized("tariffs_error_products_load_failed")
                print("❌ Продукт не найден в StoreManager для ProductID: \(productID.rawValue)")
                print("💡 Это может означать:")
                print("   1. Продукты не настроены в App Store Connect")
                print("   2. Продукты ещё не загружены из App Store")
                print("   3. Bundle ID не совпадает с App Store Connect")
            }
        } else {
            // Не удалось найти ProductID
            isLoading = false
            let localizationManager = LocalizationManager()
            errorMessage = localizationManager.localized("tariffs_error_invalid_tariff")
            print("❌ Не удалось найти ProductID для tariff.id: '\(tariff.id)'")
            print("💡 Проверьте маппинг в функции findProductID")
            print("💡 Текущий ID тарифа: '\(tariff.id)'")
        }
        #endif
    }
    
    /**
     * Найти ProductID для тарифа
     */
    private func findProductID(for tariffId: String) -> StoreManager.ProductID? {
        // Маппинг тарифов на Product IDs
        let mapping: [String: StoreManager.ProductID] = [
            "free": .basic,
            "personal": .individual,
            "family": .family,
            "premium": .premium,
            // Также проверяем прямые значения из enum
            "TariffsScreen.TariffType.free": .basic,
            "TariffsScreen.TariffType.personal": .individual,
            "TariffsScreen.TariffType.family": .family,
            "TariffsScreen.TariffType.premium": .premium
        ]
        
        let lowercasedId = tariffId.lowercased()
        
        // Пробуем точное совпадение
        for (key, productID) in mapping {
            if lowercasedId == key.lowercased() {
                print("✅ Точное совпадение: '\(tariffId)' → \(productID.rawValue)")
                return productID
            }
        }
        
        // Пробуем частичное совпадение (contains)
        for (key, productID) in mapping {
            if lowercasedId.contains(key.lowercased()) {
                print("✅ Частичное совпадение: '\(tariffId)' содержит '\(key)' → \(productID.rawValue)")
                return productID
            }
        }
        
        // Также проверяем, может быть это уже Product ID из App Store
        if lowercasedId.contains("family.aladdin.ios.subscription") {
            // Это уже Product ID
            for productID in StoreManager.ProductID.allCases {
                if lowercasedId == productID.rawValue.lowercased() {
                    print("✅ Прямое совпадение с Product ID: \(productID.rawValue)")
                    return productID
                }
            }
        }
        
        print("❌ Не найдено совпадение для: '\(tariffId)'")
        return nil
    }
    
    // MARK: - Map Tariff to TariffType
    
    /**
     * Преобразовать Tariff в TariffType для TariffManager
     */
    private func mapTariffToTariffType(_ tariff: Tariff) -> TariffType? {
        // Маппинг по ID тарифа
        let lowercasedId = tariff.id.lowercased()
        
        if lowercasedId.contains("free") || lowercasedId.contains("basic") {
            return .free
        } else if lowercasedId.contains("personal") || lowercasedId.contains("individual") {
            return .personal
        } else if lowercasedId.contains("family") {
            return .family
        } else if lowercasedId.contains("premium") {
            return .premium
        }
        
        // Маппинг по названию тарифа
        let lowercasedTitle = tariff.title.lowercased()
        if lowercasedTitle.contains("бесплатный") || lowercasedTitle.contains("free") || lowercasedTitle.contains("базовый") {
            return .free
        } else if lowercasedTitle.contains("персональный") || lowercasedTitle.contains("personal") || lowercasedTitle.contains("индивидуальный") {
            return .personal
        } else if lowercasedTitle.contains("семейный") || lowercasedTitle.contains("family") {
            return .family
        } else if lowercasedTitle.contains("премиум") || lowercasedTitle.contains("premium") {
            return .premium
        }
        
        // Маппинг по ProductID
        if let productID = findProductID(for: tariff.id) {
            switch productID {
            case .basic: return .free
            case .individual: return .personal
            case .family: return .family
            case .premium: return .premium
            }
        }
        
        print("⚠️ Не удалось определить TariffType для тарифа: \(tariff.id) (\(tariff.title))")
        return nil
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
        
        // ✅ ПЛАНИРОВАНИЕ УВЕДОМЛЕНИЙ О ПОДПИСКЕ (при восстановлении покупок)
        // Если есть активная подписка, планируем уведомления
        if let _ = getActiveSubscription(),
           let endDate = calculateSubscriptionEndDate() {
            NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
            print("✅ Уведомления о подписке запланированы при восстановлении покупок")
        }
        
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
    
    // MARK: - Subscription End Date Calculation
    
    /**
     * Вычисляет дату окончания подписки (30 дней от текущей даты)
     * В будущем можно получать из API или из StoreKit transaction
     */
    private func calculateSubscriptionEndDate() -> Date? {
        return Calendar.current.date(byAdding: .day, value: 30, to: Date())
    }
}

// MARK: - Tariff Model

struct Tariff: Identifiable {
    let id: String
    let title: String
    let price: String
    let period: String
    let features: [String]
    let product: Product?
    var isPurchased: Bool
    
    // Новые поля для скидок
    let periodMonths: Int  // 1, 3, 6, 12
    let originalPrice: String?  // Цена без скидки
    let discountPercent: Int?  // Процент скидки (10, 15, 20)
    let monthlyPrice: String  // Цена за месяц
    let savings: String?  // Экономия
    
    init(
        id: String,
        title: String,
        price: String,
        period: String,
        features: [String],
        product: Product? = nil,
        isPurchased: Bool = false,
        periodMonths: Int = 1,
        originalPrice: String? = nil,
        discountPercent: Int? = nil,
        monthlyPrice: String? = nil,
        savings: String? = nil
    ) {
        self.id = id
        self.title = title
        self.price = price
        self.period = period
        self.features = features
        self.product = product
        self.isPurchased = isPurchased
        self.periodMonths = periodMonths
        self.originalPrice = originalPrice
        self.discountPercent = discountPercent
        self.monthlyPrice = monthlyPrice ?? price
        self.savings = savings
    }
}

