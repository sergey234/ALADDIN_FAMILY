package family.aladdin.android.billing

import android.app.Activity
import android.content.Context
import com.android.billingclient.api.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 💰 Billing Manager
 * Управление покупками в Google Play (Billing Library 6.0)
 * In-App Purchase для Android
 */

class BillingManager(private val context: Context) : PurchasesUpdatedListener {
    
    // MARK: - Properties
    
    private var billingClient: BillingClient
    
    private val _products = MutableStateFlow<List<ProductDetails>>(emptyList())
    val products: StateFlow<List<ProductDetails>> = _products.asStateFlow()
    
    private val _purchasedProductIds = MutableStateFlow<Set<String>>(emptySet())
    val purchasedProductIds: StateFlow<Set<String>> = _purchasedProductIds.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    // MARK: - Product IDs
    
    companion object {
        const val PRODUCT_BASIC = "family_aladdin_android_subscription_basic"
        const val PRODUCT_INDIVIDUAL = "family_aladdin_android_subscription_individual"
        const val PRODUCT_FAMILY = "family_aladdin_android_subscription_family"
        const val PRODUCT_PREMIUM = "family_aladdin_android_subscription_premium"
        
        val ALL_PRODUCT_IDS = listOf(
            PRODUCT_BASIC,
            PRODUCT_INDIVIDUAL,
            PRODUCT_FAMILY,
            PRODUCT_PREMIUM
        )
    }
    
    // MARK: - Init
    
    init {
        billingClient = BillingClient.newBuilder(context)
            .setListener(this)
            .enablePendingPurchases()
            .build()
        
        startConnection()
    }
    
    // MARK: - Start Connection
    
    /**
     * Подключиться к Google Play Billing
     */
    private fun startConnection() {
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    println("✅ Billing client connected")
                    queryProducts()
                    queryPurchases()
                } else {
                    println("❌ Billing setup failed: ${billingResult.debugMessage}")
                    _errorMessage.value = "Ошибка подключения к Google Play: ${billingResult.debugMessage}"
                }
            }
            
            override fun onBillingServiceDisconnected() {
                println("⚠️ Billing service disconnected, reconnecting...")
                // Попробовать переподключиться
                startConnection()
            }
        })
    }
    
    // MARK: - Query Products
    
    /**
     * Загрузить продукты из Google Play
     */
    private fun queryProducts() {
        _isLoading.value = true
        
        val productList = ALL_PRODUCT_IDS.map { productId ->
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(productId)
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
        }
        
        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(productList)
            .build()
        
        billingClient.queryProductDetailsAsync(params) { billingResult, productDetailsList ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                _products.value = productDetailsList
                _isLoading.value = false
                println("✅ Loaded ${productDetailsList.size} products from Google Play")
            } else {
                _errorMessage.value = "Ошибка загрузки продуктов: ${billingResult.debugMessage}"
                _isLoading.value = false
                println("❌ Error loading products: ${billingResult.debugMessage}")
            }
        }
    }
    
    // MARK: - Query Purchases
    
    /**
     * Проверить активные покупки
     */
    fun queryPurchases() {
        billingClient.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
        ) { billingResult, purchases ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                val activePurchases = purchases.filter { it.purchaseState == Purchase.PurchaseState.PURCHASED }
                _purchasedProductIds.value = activePurchases.flatMap { it.products }.toSet()
                println("✅ Active purchases: ${_purchasedProductIds.value}")
            } else {
                println("❌ Error querying purchases: ${billingResult.debugMessage}")
            }
        }
    }
    
    // MARK: - Purchase Product
    
    /**
     * Купить продукт
     */
    fun purchase(activity: Activity, productDetails: ProductDetails) {
        _isLoading.value = true
        _errorMessage.value = null
        
        val offerToken = productDetails.subscriptionOfferDetails?.firstOrNull()?.offerToken
        
        if (offerToken == null) {
            _errorMessage.value = "Не удалось найти предложение подписки"
            _isLoading.value = false
            return
        }
        
        val productDetailsParamsList = listOf(
            BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(productDetails)
                .setOfferToken(offerToken)
                .build()
        )
        
        val billingFlowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(productDetailsParamsList)
            .build()
        
        val billingResult = billingClient.launchBillingFlow(activity, billingFlowParams)
        
        if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
            _errorMessage.value = "Ошибка запуска покупки: ${billingResult.debugMessage}"
            _isLoading.value = false
            println("❌ Error launching billing flow: ${billingResult.debugMessage}")
        }
    }
    
    // MARK: - Purchases Updated Listener
    
    override fun onPurchasesUpdated(billingResult: BillingResult, purchases: MutableList<Purchase>?) {
        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            for (purchase in purchases) {
                handlePurchase(purchase)
            }
        } else if (billingResult.responseCode == BillingClient.BillingResponseCode.USER_CANCELED) {
            println("⚠️ User cancelled purchase")
            _isLoading.value = false
        } else {
            _errorMessage.value = "Ошибка покупки: ${billingResult.debugMessage}"
            _isLoading.value = false
            println("❌ Purchase error: ${billingResult.debugMessage}")
        }
    }
    
    // MARK: - Handle Purchase
    
    /**
     * Обработать покупку
     */
    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            if (!purchase.isAcknowledged) {
                acknowledgePurchase(purchase)
            }
            
            // Обновить список купленных продуктов
            queryPurchases()
            
            println("✅ Purchase handled: ${purchase.products}")
        }
    }
    
    // MARK: - Acknowledge Purchase
    
    /**
     * Подтвердить покупку
     */
    private fun acknowledgePurchase(purchase: Purchase) {
        val acknowledgePurchaseParams = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()
        
        billingClient.acknowledgePurchase(acknowledgePurchaseParams) { billingResult ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                println("✅ Purchase acknowledged")
                _isLoading.value = false
            } else {
                println("❌ Acknowledge error: ${billingResult.debugMessage}")
                _isLoading.value = false
            }
        }
    }
    
    // MARK: - Helper Methods
    
    /**
     * Проверить куплен ли продукт
     */
    fun isPurchased(productId: String): Boolean {
        return _purchasedProductIds.value.contains(productId)
    }
    
    /**
     * Получить активную подписку
     */
    fun getActiveSubscription(): ProductDetails? {
        return _products.value.firstOrNull { isPurchased(it.productId) }
    }
    
    /**
     * Получить цену продукта
     */
    fun getProductPrice(productDetails: ProductDetails): String {
        return productDetails.subscriptionOfferDetails?.firstOrNull()
            ?.pricingPhases?.pricingPhaseList?.firstOrNull()
            ?.formattedPrice ?: "Н/Д"
    }
    
    // MARK: - Cleanup
    
    fun endConnection() {
        billingClient.endConnection()
        println("🔌 Billing client disconnected")
    }
}



