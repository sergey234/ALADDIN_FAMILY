package family.aladdin.android.network

/**
 * 🔌 Simple API Service
 * Простая реализация ApiService для компиляции
 */

import family.aladdin.android.models.*

class SimpleApiService : ApiService {
    override suspend fun getVPNStatus(): VPNStatusResponse = TODO("Not implemented")
    override suspend fun connectVPN(): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun disconnectVPN(): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun getVPNServers(): List<VPNServer> = TODO("Not implemented")
    override suspend fun getFamilyMembers(): List<FamilyMemberResponse> = TODO("Not implemented")
    override suspend fun addFamilyMember(request: AddMemberRequest): FamilyMemberResponse = TODO("Not implemented")
    override suspend fun getFamilyStats(): FamilyStatsResponse = TODO("Not implemented")
    override suspend fun removeFamilyMember(memberId: String): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun getAnalytics(period: String): AnalyticsResponse = TODO("Not implemented")
    override suspend fun getTopThreats(): List<ThreatItem> = TODO("Not implemented")
    override suspend fun sendMessageToAI(request: ChatMessageRequest): ChatMessageResponse = TODO("Not implemented")
    override suspend fun getUserProfile(): UserProfile = TODO("Not implemented")
    override suspend fun updateProfile(request: UpdateProfileRequest): UserProfile = TODO("Not implemented")
    override suspend fun changePassword(request: ChangePasswordRequest): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun getParentalControlSettings(childId: String): ParentalControlSettings = TODO("Not implemented")
    override suspend fun updateParentalLimits(request: ParentalControlSettings): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun getChildStats(childId: String): ChildStatsResponse = TODO("Not implemented")
    override suspend fun getNotifications(): List<NotificationResponse> = TODO("Not implemented")
    override suspend fun markNotificationAsRead(request: MarkReadRequest): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun getTariffs(): List<TariffResponse> = TODO("Not implemented")
    override suspend fun subscribe(request: SubscribeRequest): SubscriptionStatus = TODO("Not implemented")
    override suspend fun cancelSubscription(): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun login(request: LoginRequest): LoginResponse = TODO("Not implemented")
    override suspend fun logout(): ApiResponse<Boolean> = TODO("Not implemented")
    override suspend fun register(request: RegisterRequest): LoginResponse = TODO("Not implemented")
    override suspend fun createQRPayment(token: String, request: Map<String, Any>): family.aladdin.android.viewmodels.CreateQRPaymentResponse = TODO("Not implemented")
    override suspend fun checkQRPaymentStatus(token: String, paymentId: String): family.aladdin.android.viewmodels.CheckQRPaymentStatusResponse = TODO("Not implemented")
}
