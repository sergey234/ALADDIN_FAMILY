package family.aladdin.android.viewmodels

import android.app.Activity
import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.android.billingclient.api.ProductDetails
import family.aladdin.android.billing.BillingManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * 💳 Tariffs View Model
 * Логика для экрана тарифов
 * ИНТЕГРИРОВАН С GOOGLE PLAY BILLING!
 */

data class AndroidTariff(
    val id: String,
    val title: String,
    val price: String,
    val period: String,
    val features: List<String>,
    val productDetails: ProductDetails?,
    val isPurchased: Boolean = false,
    val isRecommended: Boolean = false
)

class TariffsViewModel(
    private val context: Context
) : ViewModel() {
    
    // MARK: - Billing Manager
    
    private val billingManager = BillingManager(context)
    
    // MARK: - State
    
    private val _tariffs = MutableStateFlow<List<AndroidTariff>>(emptyList())
    val tariffs: StateFlow<List<AndroidTariff>> = _tariffs.asStateFlow()
    
    private val _selectedTariff = MutableStateFlow<AndroidTariff?>(null)
    val selectedTariff: StateFlow<AndroidTariff?> = _selectedTariff.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    private val _isPurchaseSuccessful = MutableStateFlow(false)
    val isPurchaseSuccessful: StateFlow<Boolean> = _isPurchaseSuccessful.asStateFlow()
    
    // MARK: - Init
    
    init {
        // Подписка на изменения продуктов
        viewModelScope.launch {
            billingManager.products.collect { products ->
                updateTariffs(products)
            }
        }
        
        // Подписка на изменения купленных продуктов
        viewModelScope.launch {
            billingManager.purchasedProductIds.collect { purchasedIds ->
                updatePurchaseStatus(purchasedIds)
            }
        }
        
        // Подписка на ошибки
        viewModelScope.launch {
            billingManager.errorMessage.collect { error ->
                _errorMessage.value = error
            }
        }
        
        // Подписка на loading
        viewModelScope.launch {
            billingManager.isLoading.collect { loading ->
                _isLoading.value = loading
            }
        }
    }
    
    // MARK: - Update Tariffs
    
    /**
     * Обновить список тарифов из Billing продуктов
     */
    private fun updateTariffs(products: List<ProductDetails>) {
        val productMap = mapOf(
            BillingManager.PRODUCT_BASIC to TariffInfo("Базовый", listOf("1 устройство", "Базовая защита", "Ограниченная аналитика"), false),
            BillingManager.PRODUCT_INDIVIDUAL to TariffInfo("Индивидуальный", listOf("1 устройство", "Полная защита", "Расширенная аналитика", "AI помощник"), false),
            BillingManager.PRODUCT_FAMILY to TariffInfo("Семейный", listOf("До 5 устройств", "Полная защита", "AI помощник", "Родительский контроль"), true),
            BillingManager.PRODUCT_PREMIUM to TariffInfo("Премиум", listOf("До 10 устройств", "Все функции", "Приоритетная поддержка", "Эксклюзивные возможности"), false)
        )
        
        _tariffs.value = products.map { product ->
            val info = productMap[product.productId] ?: TariffInfo("Неизвестно", emptyList(), false)
            AndroidTariff(
                id = product.productId,
                title = info.title,
                price = billingManager.getProductPrice(product),
                period = "в месяц",
                features = info.features,
                productDetails = product,
                isPurchased = billingManager.isPurchased(product.productId),
                isRecommended = info.isRecommended
            )
        }
        
        // Выбрать первый тариф по умолчанию
        if (_selectedTariff.value == null && _tariffs.value.isNotEmpty()) {
            _selectedTariff.value = _tariffs.value.first()
        }
    }
    
    /**
     * Обновить статус покупок
     */
    private fun updatePurchaseStatus(purchasedIds: Set<String>) {
        _tariffs.value = _tariffs.value.map { tariff ->
            tariff.copy(isPurchased = purchasedIds.contains(tariff.id))
        }
    }
    
    // MARK: - Public Methods
    
    /**
     * Выбрать тариф
     */
    fun selectTariff(tariff: AndroidTariff) {
        _selectedTariff.value = tariff
        println("Selected tariff: ${tariff.title}")
    }
    
    /**
     * Купить выбранный тариф
     */
    fun purchaseSelectedTariff(activity: Activity) {
        val tariff = _selectedTariff.value
        
        if (tariff == null) {
            _errorMessage.value = "Выберите тариф"
            return
        }
        
        if (tariff.productDetails == null) {
            _errorMessage.value = "Продукт не найден"
            return
        }
        
        _isLoading.value = true
        _errorMessage.value = null
        _isPurchaseSuccessful.value = false
        
        billingManager.purchase(activity, tariff.productDetails)
        
        println("✅ Initiating purchase for: ${tariff.title}")
    }
    
    /**
     * Восстановить покупки
     */
    fun restorePurchases() {
        _isLoading.value = true
        _errorMessage.value = null
        
        billingManager.queryPurchases()
        
        _isLoading.value = false
        println("✅ Purchases restored")
    }
    
    /**
     * Получить активную подписку
     */
    fun getActiveSubscription(): AndroidTariff? {
        return _tariffs.value.firstOrNull { it.isPurchased }
    }
    
    // MARK: - Cleanup
    
    override fun onCleared() {
        super.onCleared()
        billingManager.endConnection()
    }
}

// MARK: - Helper Models

private data class TariffInfo(
    val title: String,
    val features: List<String>,
    val isRecommended: Boolean
)

