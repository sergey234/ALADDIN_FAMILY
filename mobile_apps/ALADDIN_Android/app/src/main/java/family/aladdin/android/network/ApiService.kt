package family.aladdin.android.network

import family.aladdin.android.models.*
import retrofit2.http.*

/**
 * 🔌 API Service
 * Retrofit интерфейс для всех API endpoints
 */

interface ApiService {
    
    // ═══════════════════════════════════════════════════════════════
    // VPN API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/vpn/status")
    suspend fun getVPNStatus(): VPNStatusResponse
    
    @POST("/api/vpn/connect")
    suspend fun connectVPN(): ApiResponse<Boolean>
    
    @POST("/api/vpn/disconnect")
    suspend fun disconnectVPN(): ApiResponse<Boolean>
    
    @GET("/api/vpn/servers")
    suspend fun getVPNServers(): List<VPNServer>
    
    // ═══════════════════════════════════════════════════════════════
    // Family API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/family/members")
    suspend fun getFamilyMembers(): List<FamilyMemberResponse>
    
    @POST("/api/family/add")
    suspend fun addFamilyMember(@Body request: AddMemberRequest): FamilyMemberResponse
    
    @GET("/api/family/stats")
    suspend fun getFamilyStats(): FamilyStatsResponse
    
    @DELETE("/api/family/remove/{memberId}")
    suspend fun removeFamilyMember(@Path("memberId") memberId: String): ApiResponse<Boolean>
    
    // ═══════════════════════════════════════════════════════════════
    // Analytics API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/analytics")
    suspend fun getAnalytics(@Query("period") period: String): AnalyticsResponse
    
    @GET("/api/analytics/top-threats")
    suspend fun getTopThreats(): List<ThreatItem>
    
    // ═══════════════════════════════════════════════════════════════
    // AI Assistant API
    // ═══════════════════════════════════════════════════════════════
    
    @POST("/api/ai/message")
    suspend fun sendMessageToAI(@Body request: ChatMessageRequest): ChatMessageResponse
    
    // ═══════════════════════════════════════════════════════════════
    // User API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/user/profile")
    suspend fun getUserProfile(): UserProfile
    
    @POST("/api/user/update")
    suspend fun updateProfile(@Body request: UpdateProfileRequest): UserProfile
    
    @POST("/api/user/password")
    suspend fun changePassword(@Body request: ChangePasswordRequest): ApiResponse<Boolean>
    
    // ═══════════════════════════════════════════════════════════════
    // Parental Control API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/parental/control/{childId}")
    suspend fun getParentalControlSettings(@Path("childId") childId: String): ParentalControlSettings
    
    @POST("/api/parental/limits")
    suspend fun updateParentalLimits(@Body request: ParentalControlSettings): ApiResponse<Boolean>
    
    @GET("/api/parental/child-stats/{childId}")
    suspend fun getChildStats(@Path("childId") childId: String): ChildStatsResponse
    
    // ═══════════════════════════════════════════════════════════════
    // Notifications API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/notifications")
    suspend fun getNotifications(): List<NotificationResponse>
    
    @POST("/api/notifications/read")
    suspend fun markNotificationAsRead(@Body request: MarkReadRequest): ApiResponse<Boolean>
    
    // ═══════════════════════════════════════════════════════════════
    // Subscription API
    // ═══════════════════════════════════════════════════════════════
    
    @GET("/api/subscription/tariffs")
    suspend fun getTariffs(): List<TariffResponse>
    
    @POST("/api/subscription/subscribe")
    suspend fun subscribe(@Body request: SubscribeRequest): SubscriptionStatus
    
    @POST("/api/subscription/cancel")
    suspend fun cancelSubscription(): ApiResponse<Boolean>
    
    // ═══════════════════════════════════════════════════════════════
    // Auth API
    // ═══════════════════════════════════════════════════════════════
    
    @POST("/api/auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse
    
    @POST("/api/auth/logout")
    suspend fun logout(): ApiResponse<Boolean>
    
    @POST("/api/auth/register")
    suspend fun register(@Body request: RegisterRequest): LoginResponse
    
    // ═══════════════════════════════════════════════════════════════
    // QR Payment API (для России)
    // ═══════════════════════════════════════════════════════════════
    
    @POST("/api/payments/qr/create")
    suspend fun createQRPayment(
        @Header("Authorization") token: String,
        @Body request: Map<String, Any>
    ): family.aladdin.android.viewmodels.CreateQRPaymentResponse
    
    @GET("/api/payments/qr/status/{paymentId}")
    suspend fun checkQRPaymentStatus(
        @Header("Authorization") token: String,
        @Path("paymentId") paymentId: String
    ): family.aladdin.android.viewmodels.CheckQRPaymentStatusResponse
}

// ═══════════════════════════════════════════════════════════════
// Request Models
// ═══════════════════════════════════════════════════════════════

data class AddMemberRequest(
    val name: String,
    val role: String
)

data class ChangePasswordRequest(
    val oldPassword: String,
    val newPassword: String
)

data class MarkReadRequest(
    val notificationId: String
)

data class SubscribeRequest(
    val tariffId: String
)

