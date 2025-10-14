/*
 * SupportAPI.kt
 * ALADDIN Mobile Security
 *
 * Support API Integration for Android
 * API client for Super AI Support Assistant and Psychological Support Agent
 *
 * Created by ALADDIN Security Team
 * Date: 2025-01-27
 * Version: 1.0
 */

package com.aladdin.security.api.support

import android.content.Context
import android.os.Build
import android.util.Log
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.*

// MARK: - Support API Models
data class SupportRequest(
    @SerializedName("question") val question: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("context") val context: SupportContext,
    @SerializedName("category") val category: String?,
    @SerializedName("language") val language: String,
    @SerializedName("timestamp") val timestamp: Date
) {
    constructor(
        question: String,
        userId: String,
        context: SupportContext,
        category: SupportCategory? = null,
        language: String = "ru"
    ) : this(
        question = question,
        userId = userId,
        context = context,
        category = category?.value,
        language = language,
        timestamp = Date()
    )
}

data class SupportContext(
    @SerializedName("current_screen") val currentScreen: String?,
    @SerializedName("user_age_group") val userAgeGroup: String?,
    @SerializedName("emotional_state") val emotionalState: String?,
    @SerializedName("device_info") val deviceInfo: DeviceInfo,
    @SerializedName("session_id") val sessionId: String
)

data class DeviceInfo(
    @SerializedName("platform") val platform: String,
    @SerializedName("version") val version: String,
    @SerializedName("model") val model: String,
    @SerializedName("screen_size") val screenSize: String,
    @SerializedName("orientation") val orientation: String
)

data class SupportResponse(
    @SerializedName("answer") val answer: String,
    @SerializedName("category") val category: String,
    @SerializedName("suggested_actions") val suggestedActions: List<String>,
    @SerializedName("related_topics") val relatedTopics: List<String>,
    @SerializedName("confidence") val confidence: Double,
    @SerializedName("response_time") val responseTime: Double,
    @SerializedName("timestamp") val timestamp: Date,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("follow_up_questions") val followUpQuestions: List<String>?,
    @SerializedName("emotional_analysis") val emotionalAnalysis: EmotionalAnalysis?,
    @SerializedName("priority") val priority: String
)

data class EmotionalAnalysis(
    @SerializedName("emotion") val emotion: String,
    @SerializedName("confidence") val confidence: Double,
    @SerializedName("sentiment") val sentiment: String,
    @SerializedName("recommendations") val recommendations: List<String>
)

enum class SupportCategory(val value: String) {
    CYBERSECURITY("cybersecurity"),
    FAMILY_SUPPORT("family_support"),
    MEDICAL_SUPPORT("medical_support"),
    EDUCATION("education"),
    FINANCE("finance"),
    HOUSEHOLD("household"),
    PSYCHOLOGY("psychology"),
    TECHNOLOGY("technology"),
    LEGAL("legal"),
    TRAVEL("travel"),
    ENTERTAINMENT("entertainment"),
    HEALTH("health"),
    FITNESS("fitness"),
    RELATIONSHIPS("relationships"),
    CAREER("career"),
    BUSINESS("business"),
    SHOPPING("shopping"),
    COOKING("cooking"),
    GARDENING("gardening"),
    REPAIR("repair")
}

enum class SupportPriority(val value: String) {
    LOW("low"),
    MEDIUM("medium"),
    HIGH("high"),
    URGENT("urgent")
}

// MARK: - Additional Models
data class FAQItem(
    @SerializedName("id") val id: String,
    @SerializedName("question") val question: String,
    @SerializedName("answer") val answer: String,
    @SerializedName("category") val category: String,
    @SerializedName("tags") val tags: List<String>,
    @SerializedName("helpful") val helpful: Int,
    @SerializedName("not_helpful") val notHelpful: Int,
    @SerializedName("last_updated") val lastUpdated: Date
)

data class SupportFeedback(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("rating") val rating: Int,
    @SerializedName("comment") val comment: String?,
    @SerializedName("helpful") val helpful: Boolean,
    @SerializedName("category") val category: String,
    @SerializedName("timestamp") val timestamp: Date
)

data class SupportHistoryItem(
    @SerializedName("id") val id: String,
    @SerializedName("question") val question: String,
    @SerializedName("answer") val answer: String,
    @SerializedName("category") val category: String,
    @SerializedName("timestamp") val timestamp: Date,
    @SerializedName("rating") val rating: Int?,
    @SerializedName("helpful") val helpful: Boolean?
)

// MARK: - API Errors
sealed class APIError : Exception() {
    object InvalidURL : APIError()
    object NoData : APIError()
    data class DecodingError(val error: Throwable) : APIError()
    data class EncodingError(val error: Throwable) : APIError()
    data class NetworkError(val error: Throwable) : APIError()
    data class ServerError(val code: Int, val message: String) : APIError()
    object Unauthorized : APIError()
    object Forbidden : APIError()
    object NotFound : APIError()
    object RateLimited : APIError()
    object Timeout : APIError()
}

// MARK: - Support API Client
class SupportAPIClient(
    private val baseURL: String = "https://api.aladdin-security.com",
    private val apiKey: String
) {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
        .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()
    
    private val gson = Gson()
    private val jsonMediaType = "application/json".toMediaType()
    
    // MARK: - Public Methods
    
    suspend fun askQuestion(request: SupportRequest): Result<SupportResponse> {
        return performRequest("/api/v1/support/ask", "POST", request)
    }
    
    suspend fun getPsychologicalSupport(request: SupportRequest): Result<SupportResponse> {
        return performRequest("/api/v1/support/psychological", "POST", request)
    }
    
    suspend fun getNavigationHelp(request: SupportRequest): Result<SupportResponse> {
        return performRequest("/api/v1/support/navigation", "POST", request)
    }
    
    suspend fun getFAQ(category: SupportCategory? = null): Result<List<FAQItem>> {
        var endpoint = "/api/v1/support/faq"
        if (category != null) {
            endpoint += "?category=${category.value}"
        }
        return performRequest(endpoint, "GET", null)
    }
    
    suspend fun getSupportCategories(): Result<List<SupportCategory>> {
        return performRequest("/api/v1/support/categories", "GET", null)
    }
    
    suspend fun submitFeedback(feedback: SupportFeedback): Result<SupportResponse> {
        return performRequest("/api/v1/support/feedback", "POST", feedback)
    }
    
    suspend fun getSupportHistory(userId: String, limit: Int = 50): Result<List<SupportHistoryItem>> {
        val endpoint = "/api/v1/support/history?userId=$userId&limit=$limit"
        return performRequest(endpoint, "GET", null)
    }
    
    // MARK: - Private Methods
    
    private suspend fun <T> performRequest(
        endpoint: String,
        method: String,
        body: T?
    ): Result<SupportResponse> = withContext(Dispatchers.IO) {
        try {
            val url = "$baseURL$endpoint"
            val requestBuilder = Request.Builder()
                .url(url)
                .addHeader("Content-Type", "application/json")
                .addHeader("Authorization", "Bearer $apiKey")
                .addHeader("X-Platform", "Android")
                .addHeader("X-App-Version", "1.0")
            
            when (method) {
                "POST" -> {
                    val jsonBody = if (body != null) {
                        gson.toJson(body).toRequestBody(jsonMediaType)
                    } else {
                        "{}".toRequestBody(jsonMediaType)
                    }
                    requestBuilder.post(jsonBody)
                }
                "GET" -> requestBuilder.get()
                else -> throw APIError.InvalidURL
            }
            
            val request = requestBuilder.build()
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                if (responseBody != null) {
                    val result = gson.fromJson(responseBody, SupportResponse::class.java)
                    Result.success(result)
                } else {
                    Result.failure(APIError.NoData)
                }
            } else {
                when (response.code) {
                    401 -> Result.failure(APIError.Unauthorized)
                    403 -> Result.failure(APIError.Forbidden)
                    404 -> Result.failure(APIError.NotFound)
                    429 -> Result.failure(APIError.RateLimited)
                    else -> Result.failure(APIError.ServerError(response.code, response.message))
                }
            }
        } catch (e: IOException) {
            Result.failure(APIError.NetworkError(e))
        } catch (e: Exception) {
            Result.failure(APIError.DecodingError(e))
        }
    }
    
    private suspend fun <T> performRequest(
        endpoint: String,
        method: String,
        body: T?,
        responseType: Class<*>
    ): Result<T> = withContext(Dispatchers.IO) {
        try {
            val url = "$baseURL$endpoint"
            val requestBuilder = Request.Builder()
                .url(url)
                .addHeader("Content-Type", "application/json")
                .addHeader("Authorization", "Bearer $apiKey")
                .addHeader("X-Platform", "Android")
                .addHeader("X-App-Version", "1.0")
            
            when (method) {
                "POST" -> {
                    val jsonBody = if (body != null) {
                        gson.toJson(body).toRequestBody(jsonMediaType)
                    } else {
                        "{}".toRequestBody(jsonMediaType)
                    }
                    requestBuilder.post(jsonBody)
                }
                "GET" -> requestBuilder.get()
                else -> throw APIError.InvalidURL
            }
            
            val request = requestBuilder.build()
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                if (responseBody != null) {
                    val result = gson.fromJson(responseBody, responseType) as T
                    Result.success(result)
                } else {
                    Result.failure(APIError.NoData)
                }
            } else {
                when (response.code) {
                    401 -> Result.failure(APIError.Unauthorized)
                    403 -> Result.failure(APIError.Forbidden)
                    404 -> Result.failure(APIError.NotFound)
                    429 -> Result.failure(APIError.RateLimited)
                    else -> Result.failure(APIError.ServerError(response.code, response.message))
                }
            }
        } catch (e: IOException) {
            Result.failure(APIError.NetworkError(e))
        } catch (e: Exception) {
            Result.failure(APIError.DecodingError(e))
        }
    }
}

// MARK: - Support API Manager
class SupportAPIManager(
    private val context: Context,
    private val apiClient: SupportAPIClient,
    private val userId: String,
    private val sessionId: String = UUID().randomUUID().toString()
) {
    
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    var isLoading = false
    var lastError: APIError? = null
    var supportHistory: List<SupportHistoryItem> = emptyList()
    var faqItems: List<FAQItem> = emptyList()
    
    // MARK: - Public Methods
    
    fun askQuestion(
        question: String,
        category: SupportCategory? = null,
        context: SupportContext? = null,
        onSuccess: (SupportResponse) -> Unit,
        onError: (APIError) -> Unit
    ) {
        scope.launch {
            isLoading = true
            lastError = null
            
            val defaultContext = context ?: createDefaultContext()
            val request = SupportRequest(
                question = question,
                userId = userId,
                context = defaultContext,
                category = category
            )
            
            when (val result = apiClient.askQuestion(request)) {
                is Result.success -> {
                    isLoading = false
                    onSuccess(result.getOrThrow())
                }
                is Result.failure -> {
                    isLoading = false
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                    onError(lastError!!)
                }
            }
        }
    }
    
    fun getPsychologicalSupport(
        question: String,
        ageGroup: String? = null,
        emotionalState: String? = null,
        onSuccess: (SupportResponse) -> Unit,
        onError: (APIError) -> Unit
    ) {
        scope.launch {
            isLoading = true
            lastError = null
            
            val context = SupportContext(
                currentScreen = null,
                userAgeGroup = ageGroup,
                emotionalState = emotionalState,
                deviceInfo = createDeviceInfo(),
                sessionId = sessionId
            )
            
            val request = SupportRequest(
                question = question,
                userId = userId,
                context = context,
                category = SupportCategory.PSYCHOLOGY
            )
            
            when (val result = apiClient.getPsychologicalSupport(request)) {
                is Result.success -> {
                    isLoading = false
                    onSuccess(result.getOrThrow())
                }
                is Result.failure -> {
                    isLoading = false
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                    onError(lastError!!)
                }
            }
        }
    }
    
    fun loadFAQ(category: SupportCategory? = null) {
        scope.launch {
            when (val result = apiClient.getFAQ(category)) {
                is Result.success -> {
                    faqItems = result.getOrThrow()
                }
                is Result.failure -> {
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                }
            }
        }
    }
    
    fun loadSupportHistory() {
        scope.launch {
            when (val result = apiClient.getSupportHistory(userId)) {
                is Result.success -> {
                    supportHistory = result.getOrThrow()
                }
                is Result.failure -> {
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                }
            }
        }
    }
    
    fun submitFeedback(
        sessionId: String,
        rating: Int,
        comment: String? = null,
        helpful: Boolean,
        category: String
    ) {
        scope.launch {
            val feedback = SupportFeedback(
                sessionId = sessionId,
                rating = rating,
                comment = comment,
                helpful = helpful,
                category = category,
                timestamp = Date()
            )
            
            when (val result = apiClient.submitFeedback(feedback)) {
                is Result.success -> {
                    // Feedback submitted successfully
                }
                is Result.failure -> {
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                }
            }
        }
    }
    
    fun getScreenHelp(screen: String, onSuccess: (SupportResponse) -> Unit, onError: (APIError) -> Unit) {
        val context = SupportContext(
            currentScreen = screen,
            userAgeGroup = null,
            emotionalState = null,
            deviceInfo = createDeviceInfo(),
            sessionId = sessionId
        )
        
        val request = SupportRequest(
            question = "Помощь по экрану $screen",
            userId = userId,
            context = context,
            category = SupportCategory.TECHNOLOGY
        )
        
        scope.launch {
            when (val result = apiClient.getNavigationHelp(request)) {
                is Result.success -> {
                    onSuccess(result.getOrThrow())
                }
                is Result.failure -> {
                    lastError = result.exceptionOrNull() as? APIError ?: APIError.NetworkError(Exception("Unknown error"))
                    onError(lastError!!)
                }
            }
        }
    }
    
    // MARK: - Private Methods
    
    private fun createDefaultContext(): SupportContext {
        return SupportContext(
            currentScreen = null,
            userAgeGroup = null,
            emotionalState = null,
            deviceInfo = createDeviceInfo(),
            sessionId = sessionId
        )
    }
    
    private fun createDeviceInfo(): DeviceInfo {
        val displayMetrics = context.resources.displayMetrics
        val screenSize = "${displayMetrics.widthPixels}x${displayMetrics.heightPixels}"
        
        return DeviceInfo(
            platform = "Android",
            version = Build.VERSION.RELEASE,
            model = Build.MODEL,
            screenSize = screenSize,
            orientation = if (displayMetrics.widthPixels > displayMetrics.heightPixels) "landscape" else "portrait"
        )
    }
    
    fun cleanup() {
        scope.cancel()
    }
}

// MARK: - Flow-based API (Alternative approach)
class SupportAPIFlow(
    private val apiClient: SupportAPIClient,
    private val userId: String,
    private val sessionId: String = UUID().randomUUID().toString()
) {
    
    fun askQuestionFlow(
        question: String,
        category: SupportCategory? = null,
        context: SupportContext? = null
    ): Flow<Result<SupportResponse>> = flow {
        val defaultContext = context ?: createDefaultContext()
        val request = SupportRequest(
            question = question,
            userId = userId,
            context = defaultContext,
            category = category
        )
        
        emit(apiClient.askQuestion(request))
    }
    
    fun getPsychologicalSupportFlow(
        question: String,
        ageGroup: String? = null,
        emotionalState: String? = null
    ): Flow<Result<SupportResponse>> = flow {
        val context = SupportContext(
            currentScreen = null,
            userAgeGroup = ageGroup,
            emotionalState = emotionalState,
            deviceInfo = createDeviceInfo(),
            sessionId = sessionId
        )
        
        val request = SupportRequest(
            question = question,
            userId = userId,
            context = context,
            category = SupportCategory.PSYCHOLOGY
        )
        
        emit(apiClient.getPsychologicalSupport(request))
    }
    
    private fun createDefaultContext(): SupportContext {
        return SupportContext(
            currentScreen = null,
            userAgeGroup = null,
            emotionalState = null,
            deviceInfo = createDeviceInfo(),
            sessionId = sessionId
        )
    }
    
    private fun createDeviceInfo(): DeviceInfo {
        return DeviceInfo(
            platform = "Android",
            version = Build.VERSION.RELEASE,
            model = Build.MODEL,
            screenSize = "unknown",
            orientation = "portrait"
        )
    }
}

