package family.aladdin.android.viewmodels

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import family.aladdin.android.config.AppConfig
import family.aladdin.android.models.MerchantInfo
import family.aladdin.android.network.RetrofitClient
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.*

/**
 * 💳 Payment QR View Model
 * Логика для экрана QR-оплаты
 */

class PaymentQRViewModel : ViewModel() {
    
    // MARK: - State
    
    var isLoading by mutableStateOf(false)
        private set
    
    var errorMessage by mutableStateOf<String?>(null)
        private set
    
    var showErrorDialog by mutableStateOf(false)
    
    var showSuccessDialog by mutableStateOf(false)
    
    var paymentId by mutableStateOf<String?>(null)
        private set
    
    var qrCodeImageSBP by mutableStateOf<String?>(null)
        private set
    
    var qrCodeImageSberPay by mutableStateOf<String?>(null)
        private set
    
    var qrCodeImageUniversal by mutableStateOf<String?>(null)
        private set
    
    var expiresAt by mutableStateOf<Long?>(null)
        private set
    
    var merchantInfo by mutableStateOf<MerchantInfo?>(null)
        private set
    
    private var autoCheckJob: Job? = null
    
    // MARK: - Create Payment
    
    /**
     * Создание платежа и получение QR-кодов
     */
    fun createPayment(tariffTitle: String, tariffPrice: String) {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            
            try {
                // Парсим сумму из строки (например, "590 ₽" → 590.0)
                val amount = tariffPrice
                    .replace(Regex("[^0-9]"), "")
                    .toDoubleOrNull() ?: run {
                        errorMessage = "Ошибка определения суммы платежа"
                        showErrorDialog = true
                        isLoading = false
                        return@launch
                    }
                
                // Создаем запрос
                val request = mapOf(
                    "family_id" to getFamilyId(),
                    "tariff" to tariffTitle,
                    "amount" to amount,
                    "payment_method" to "sbp"
                )
                
                // Отправляем запрос на backend
                val response = RetrofitClient.apiService.createQRPayment(
                    token = "Bearer ${AppConfig.apiKey}",
                    request = request
                )
                
                if (response.success) {
                    // Сохраняем данные платежа
                    paymentId = response.payment_id
                    
                    response.qr_codes?.let { qrCodes ->
                        qrCodeImageSBP = qrCodes.sbp
                        qrCodeImageSberPay = qrCodes.sberpay
                        qrCodeImageUniversal = qrCodes.universal
                    }
                    
                    response.expires_at?.let { _ ->
                        // Парсим ISO 8601 дату
                        try {
                            val calendar = Calendar.getInstance()
                            // Простой парсинг (в реальности нужен DateTimeFormatter)
                            expiresAt = calendar.timeInMillis + (24 * 60 * 60 * 1000) // 24 часа
                        } catch (e: Exception) {
                            Log.e("PaymentQR", "Error parsing expires_at: $e")
                        }
                    }
                    
                    response.merchant_info?.let { merchantData ->
                        merchantInfo = MerchantInfo(
                            name = merchantData.name,
                            card = merchantData.card,
                            phone = merchantData.phone
                        )
                    }
                    
                    // Запускаем автопроверку
                    startAutoCheck()
                    
                    Log.d("PaymentQR", "✅ QR-коды получены: payment_id=${response.payment_id}")
                } else {
                    errorMessage = response.error ?: "Ошибка создания платежа"
                    showErrorDialog = true
                }
                
            } catch (e: Exception) {
                errorMessage = "Ошибка: ${e.message}"
                showErrorDialog = true
                Log.e("PaymentQR", "❌ Ошибка создания платежа: $e")
            } finally {
                isLoading = false
            }
        }
    }
    
    // MARK: - Check Payment Status
    
    /**
     * Проверка статуса оплаты
     */
    fun checkPaymentStatus() {
        val currentPaymentId = paymentId ?: run {
            errorMessage = "ID платежа не найден"
            showErrorDialog = true
            return
        }
        
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            
            try {
                val response = RetrofitClient.apiService.checkQRPaymentStatus(
                    token = "Bearer ${AppConfig.apiKey}",
                    paymentId = currentPaymentId
                )
                
                Log.d("PaymentQR", "ℹ️ Статус платежа: ${response.status}")
                
                when (response.status) {
                    "completed" -> {
                        // Платеж завершен!
                        showSuccessDialog = true
                        stopAutoCheck()
                        
                        // TODO: Firebase Analytics событие
                        Log.d("PaymentQR", "✅ Платеж завершен!")
                    }
                    "expired" -> {
                        errorMessage = "Срок действия платежа истек"
                        showErrorDialog = true
                        stopAutoCheck()
                    }
                    else -> {
                        // Платеж еще в ожидании
                        Log.d("PaymentQR", "⏳ Платеж ожидает оплаты")
                    }
                }
                
            } catch (e: Exception) {
                errorMessage = "Ошибка проверки: ${e.message}"
                showErrorDialog = true
                Log.e("PaymentQR", "❌ Ошибка проверки статуса: $e")
            } finally {
                isLoading = false
            }
        }
    }
    
    // MARK: - Auto Check
    
    /**
     * Запуск автоматической проверки каждые 30 секунд
     */
    private fun startAutoCheck() {
        autoCheckJob = viewModelScope.launch {
            while (true) {
                delay(30000) // 30 секунд
                checkPaymentStatus()
            }
        }
    }
    
    /**
     * Остановка автоматической проверки
     */
    private fun stopAutoCheck() {
        autoCheckJob?.cancel()
        autoCheckJob = null
    }
    
    // MARK: - Helpers
    
    /**
     * Получение ID семьи (анонимного)
     */
    private fun getFamilyId(): String {
        // В реальном приложении это будет ID из SharedPreferences
        // Пока возвращаем UUID устройства
        return UUID.randomUUID().toString()
    }
    
    // MARK: - Cleanup
    
    override fun onCleared() {
        super.onCleared()
        stopAutoCheck()
    }
}

// MARK: - API Response Models

data class CreateQRPaymentResponse(
    val success: Boolean,
    val payment_id: String,
    val qr_codes: QRCodes?,
    val merchant_info: MerchantInfoAPI?,
    val expires_at: String?,
    val error: String?
)

data class QRCodes(
    val sbp: String?,
    val sberpay: String?,
    val universal: String?
)

data class MerchantInfoAPI(
    val name: String,
    val card: String,
    val phone: String
)

data class CheckQRPaymentStatusResponse(
    val success: Boolean,
    val payment_id: String,
    val status: String,  // "pending", "completed", "expired", "cancelled"
    val amount: Double?,
    val message: String?,
    val error: String?
)



