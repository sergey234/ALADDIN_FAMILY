package com.aladdin.mobile.api

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.TimeUnit

// MARK: - Data Models
@Serializable
data class SupportRequest(
    val message: String,
    val category: SupportCategory,
    val priority: SupportPriority,
    val context: SupportContext
)

@Serializable
data class SupportResponse(
    val message: String,
    val category: SupportCategory,
    val priority: SupportPriority,
    val suggestions: List<String>,
    val timestamp: String,
    val responseTime: Double,
    val isResolved: Boolean = false,
    val nextSteps: List<String>? = null
)

@Serializable
data class SupportContext(
    val userID: String,
    val deviceInfo: String,
    val appVersion: String,
    val language: String = "ru",
    val timezone: String = "Europe/Moscow",
    val location: String? = null,
    val previousTickets: List<String>? = null
)

@Serializable
data class SupportTicket(
    val id: String,
    val title: String,
    val status: TicketStatus,
    val category: SupportCategory,
    val priority: SupportPriority,
    val createdAt: String,
    val lastMessage: String,
    val assignedAgent: String? = null,
    val resolutionTime: Double? = null
)

@Serializable
data class SupportMessage(
    val id: String,
    val text: String,
    val isFromUser: Boolean,
    val timestamp: String,
    val category: SupportCategory,
    val attachments: List<String>? = null
)

// MARK: - Status Enums
@Serializable
enum class TicketStatus(val value: String) {
    OPEN("open"),
    IN_PROGRESS("in_progress"),
    RESOLVED("resolved"),
    CLOSED("closed"),
    ESCALATED("escalated");
    
    val displayName: String
        get() = when (this) {
            OPEN -> "Открыт"
            IN_PROGRESS -> "В работе"
            RESOLVED -> "Решен"
            CLOSED -> "Закрыт"
            ESCALATED -> "Эскалирован"
        }
}

@Serializable
enum class SupportStatus(val value: String) {
    ONLINE("online"),
    BUSY("busy"),
    OFFLINE("offline"),
    MAINTENANCE("maintenance");
    
    val displayName: String
        get() = when (this) {
            ONLINE -> "Онлайн"
            BUSY -> "Занят"
            OFFLINE -> "Офлайн"
            MAINTENANCE -> "Техническое обслуживание"
        }
}

// MARK: - API Manager
class UnifiedSupportAPIManager {
    private val baseURL: String
    private val json = Json { ignoreUnknownKeys = true }
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()
    
    private var _currentStatus = MutableStateFlow(SupportStatus.OFFLINE)
    val currentStatus: StateFlow<SupportStatus> = _currentStatus.asStateFlow()
    
    private var _recentTickets = MutableStateFlow<List<SupportTicket>>(emptyList())
    val recentTickets: StateFlow<List<SupportTicket>> = _recentTickets.asStateFlow()
    
    constructor(baseURL: String = "https://api.aladdin-security.com") {
        this.baseURL = baseURL
    }
    
    // MARK: - API Methods
    suspend fun sendSupportRequest(request: SupportRequest): Result<SupportResponse> {
        return try {
            val url = URL("$baseURL/api/v2/support/request")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            connection.doOutput = true
            
            val requestJson = json.encodeToString(SupportRequest.serializer(), request)
            connection.outputStream.use { it.write(requestJson.toByteArray()) }
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val supportResponse = json.decodeFromString(SupportResponse.serializer(), response)
                Result.success(supportResponse)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getRecentTickets(): Result<List<SupportTicket>> {
        return try {
            val url = URL("$baseURL/api/v2/support/tickets")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "GET"
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val tickets = json.decodeFromString(List.serializer(SupportTicket.serializer()), response)
                Result.success(tickets)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getSupportStatus(): Result<SupportStatus> {
        return try {
            val url = URL("$baseURL/api/v2/support/status")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "GET"
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val status = json.decodeFromString(SupportStatus.serializer(), response)
                Result.success(status)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun sendCrisisRequest(crisisType: CrisisType, message: String, userID: String): Result<SupportResponse> {
        val request = SupportRequest(
            message = message,
            category = SupportCategory.CRISIS,
            priority = SupportPriority.CRITICAL,
            context = SupportContext(
                userID = userID,
                deviceInfo = "Android Crisis",
                appVersion = "1.0.0"
            )
        )
        
        return sendSupportRequest(request)
    }
    
    suspend fun sendTechnicalTicket(issueType: String, description: String, userID: String, deviceInfo: String): Result<SupportTicket> {
        return try {
            val url = URL("$baseURL/api/v2/support/technical")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            connection.doOutput = true
            
            val ticketData = mapOf(
                "issue_type" to issueType,
                "description" to description,
                "user_id" to userID,
                "device_info" to deviceInfo
            )
            
            val requestJson = json.encodeToString(Map.serializer(String.serializer(), String.serializer()), ticketData)
            connection.outputStream.use { it.write(requestJson.toByteArray()) }
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val ticket = json.decodeFromString(SupportTicket.serializer(), response)
                Result.success(ticket)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getFAQ(category: SupportCategory): Result<List<String>> {
        return try {
            val url = URL("$baseURL/api/v2/support/faq/${category.value}")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "GET"
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val faq = json.decodeFromString(List.serializer(String.serializer()), response)
                Result.success(faq)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getSupportMetrics(): Result<Map<String, Any>> {
        return try {
            val url = URL("$baseURL/api/v2/support/metrics")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "GET"
            connection.setRequestProperty("Authorization", "Bearer ${getAuthToken()}")
            
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val metrics = json.decodeFromString(Map.serializer(String.serializer(), String.serializer()), response)
                Result.success(metrics)
            } else {
                Result.failure(Exception("HTTP Error: $responseCode"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // MARK: - Helper Methods
    private fun getAuthToken(): String {
        // В реальном приложении здесь будет получение токена из SecurePreferences
        return "mock_auth_token"
    }
    
    fun connect() {
        scope.launch {
            getSupportStatus()
                .onSuccess { status ->
                    _isConnected.value = true
                    _currentStatus.value = status
                }
                .onFailure {
                    _isConnected.value = false
                    _currentStatus.value = SupportStatus.OFFLINE
                }
        }
    }
    
    fun disconnect() {
        scope.cancel()
        _isConnected.value = false
        _currentStatus.value = SupportStatus.OFFLINE
    }
    
    fun loadRecentTickets() {
        scope.launch {
            getRecentTickets()
                .onSuccess { tickets ->
                    _recentTickets.value = tickets
                }
        }
    }
    
    fun refreshStatus() {
        connect()
    }
}

// MARK: - Error Handling
sealed class SupportAPIError : Exception() {
    object NetworkError : SupportAPIError()
    object DecodingError : SupportAPIError()
    data class ServerError(val code: Int, val message: String) : SupportAPIError()
    object AuthenticationError : SupportAPIError()
    object RateLimitExceeded : SupportAPIError()
    object InvalidRequest : SupportAPIError()
    
    override val message: String
        get() = when (this) {
            is NetworkError -> "Ошибка сети"
            is DecodingError -> "Ошибка декодирования"
            is ServerError -> "Ошибка сервера $code: $message"
            is AuthenticationError -> "Ошибка аутентификации"
            is RateLimitExceeded -> "Превышен лимит запросов"
            is InvalidRequest -> "Неверный запрос"
        }
}