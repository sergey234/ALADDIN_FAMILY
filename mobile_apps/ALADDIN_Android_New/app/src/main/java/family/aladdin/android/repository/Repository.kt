package family.aladdin.android.repository

import family.aladdin.android.models.*
import family.aladdin.android.network.ApiService
import family.aladdin.android.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * 📚 Repository
 * MVVM репозиторий для работы с данными
 * Слой между ViewModels и Network
 */

class Repository {
    
    private val apiService: ApiService = RetrofitClient.apiService
    
    // ═══════════════════════════════════════════════════════════════
    // VPN Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getVPNStatus(): Result<VPNStatusResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getVPNStatus())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun connectVPN(): Result<ApiResponse<Boolean>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.connectVPN())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun disconnectVPN(): Result<ApiResponse<Boolean>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.disconnectVPN())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getVPNServers(): Result<List<VPNServer>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getVPNServers())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Family Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getFamilyMembers(): Result<List<FamilyMemberResponse>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getFamilyMembers())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun addFamilyMember(name: String, role: String): Result<FamilyMemberResponse> = withContext(Dispatchers.IO) {
        try {
            val request = family.aladdin.android.network.AddMemberRequest(name, role)
            Result.success(apiService.addFamilyMember(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getFamilyStats(): Result<FamilyStatsResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getFamilyStats())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Analytics Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getAnalytics(period: String): Result<AnalyticsResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getAnalytics(period))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getTopThreats(): Result<List<ThreatItem>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getTopThreats())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // AI Assistant Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun sendMessageToAI(message: String, userId: String): Result<ChatMessageResponse> = withContext(Dispatchers.IO) {
        try {
            val request = ChatMessageRequest(message, userId)
            Result.success(apiService.sendMessageToAI(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // User Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getUserProfile(): Result<UserProfile> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getUserProfile())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun updateProfile(name: String?, email: String?, phone: String?): Result<UserProfile> = withContext(Dispatchers.IO) {
        try {
            val request = UpdateProfileRequest(name, email, phone)
            Result.success(apiService.updateProfile(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Notifications Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getNotifications(): Result<List<NotificationResponse>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getNotifications())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun markNotificationAsRead(notificationId: String): Result<ApiResponse<Boolean>> = withContext(Dispatchers.IO) {
        try {
            val request = family.aladdin.android.network.MarkReadRequest(notificationId)
            Result.success(apiService.markNotificationAsRead(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Subscription Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun getTariffs(): Result<List<TariffResponse>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getTariffs())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun subscribe(tariffId: String): Result<SubscriptionStatus> = withContext(Dispatchers.IO) {
        try {
            val request = family.aladdin.android.network.SubscribeRequest(tariffId)
            Result.success(apiService.subscribe(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Auth Repository
    // ═══════════════════════════════════════════════════════════════
    
    suspend fun login(email: String, password: String): Result<LoginResponse> = withContext(Dispatchers.IO) {
        try {
            val request = LoginRequest(email, password)
            Result.success(apiService.login(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout(): Result<ApiResponse<Boolean>> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.logout())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}



