package family.aladdin.android.models

import com.google.gson.annotations.SerializedName
import java.util.Date

/**
 * 📦 API Models
 * Модели данных для API запросов и ответов (Android)
 * Соответствуют структуре Python backend
 */

// ═══════════════════════════════════════════════════════════════
// Payment Models (QR оплата)
// ═══════════════════════════════════════════════════════════════

data class MerchantInfo(
    val name: String,
    val card: String,
    val phone: String
)

// ═══════════════════════════════════════════════════════════════
// VPN Models
// ═══════════════════════════════════════════════════════════════

data class VPNStatusResponse(
    val isConnected: Boolean,
    val serverLocation: String,
    val ipAddress: String,
    val ping: Int,
    val downloadSpeed: String,
    val uploadSpeed: String,
    val sessionTime: String,
    val threatsBlocked: Int
)

data class VPNServer(
    val id: String,
    val country: String,
    val city: String,
    val flag: String,
    val ping: Int,
    val load: Int // 0-100%
)

// ═══════════════════════════════════════════════════════════════
// Family Models
// ═══════════════════════════════════════════════════════════════

data class FamilyMemberResponse(
    val id: String,
    val name: String,
    val role: String, // "parent", "child", "teenager", "elderly"
    val avatar: String,
    val status: String, // "protected", "warning", "danger", "offline"
    val threatsBlocked: Int,
    val lastActive: String,
    val devices: Int
)

data class FamilyStatsResponse(
    val totalMembers: Int,
    val totalDevices: Int,
    val totalThreats: Int,
    val protectionLevel: Int
)

// ═══════════════════════════════════════════════════════════════
// Analytics Models
// ═══════════════════════════════════════════════════════════════

data class AnalyticsResponse(
    val period: String, // "day", "week", "month"
    val threatsDetected: Int,
    val threatsBlocked: Int,
    val itemsScanned: Int,
    val protectionLevel: Int,
    val topThreats: List<ThreatItem>,
    val threatsByType: List<ThreatByType>
)

data class ThreatItem(
    val id: String,
    val name: String,
    val count: Int,
    val icon: String,
    val severity: String // "low", "medium", "high", "critical"
)

data class ThreatByType(
    val type: String, // "web", "app", "network", "file"
    val count: Int,
    val percentage: Double
)

// ═══════════════════════════════════════════════════════════════
// AI Assistant Models
// ═══════════════════════════════════════════════════════════════

data class ChatMessageRequest(
    val message: String,
    val userId: String,
    val timestamp: Long = System.currentTimeMillis()
)

data class ChatMessageResponse(
    val message: String,
    val timestamp: Long,
    val suggestions: List<String>?
)

// ═══════════════════════════════════════════════════════════════
// User Models
// ═══════════════════════════════════════════════════════════════

data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val phone: String?,
    val registrationDate: String,
    val subscriptionType: String,
    val subscriptionEndDate: String?,
    val threatsBlocked: Int,
    val familyMembers: Int,
    val devices: Int
)

data class UpdateProfileRequest(
    val name: String?,
    val email: String?,
    val phone: String?
)

// ═══════════════════════════════════════════════════════════════
// Parental Control Models
// ═══════════════════════════════════════════════════════════════

data class ParentalControlSettings(
    val childId: String,
    val isContentFilterEnabled: Boolean,
    val isAppBlockingEnabled: Boolean,
    val screenTimeLimitHours: Int,
    val allowedApps: List<String>,
    val blockedWebsites: List<String>,
    val bedtime: String? // "22:00"
)

data class ChildStatsResponse(
    val screenTimeToday: String,
    val blockedSitesToday: Int,
    val allowedAppsCount: Int,
    val timeRemaining: String
)

// ═══════════════════════════════════════════════════════════════
// Notifications Models
// ═══════════════════════════════════════════════════════════════

data class NotificationResponse(
    val id: String,
    val icon: String,
    val title: String,
    val message: String,
    val timestamp: Long,
    val isRead: Boolean,
    val type: String // "threat", "success", "info", "warning"
)

// ═══════════════════════════════════════════════════════════════
// Subscription Models
// ═══════════════════════════════════════════════════════════════

data class TariffResponse(
    val id: String,
    val name: String,
    val price: Int,
    val period: String,
    val features: List<String>,
    val isRecommended: Boolean
)

data class SubscriptionStatus(
    val isActive: Boolean,
    val tariffId: String,
    val startDate: Long,
    val endDate: Long,
    val autoRenew: Boolean
)

// ═══════════════════════════════════════════════════════════════
// Auth Models
// ═══════════════════════════════════════════════════════════════

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    val token: String,
    val userId: String,
    val expiresAt: Long
)

data class RegisterRequest(
    val name: String,
    val email: String,
    val password: String,
    val phone: String?
)

// ═══════════════════════════════════════════════════════════════
// Generic Response
// ═══════════════════════════════════════════════════════════════

data class ApiResponse<T>(
    val success: Boolean,
    val data: T?,
    val message: String?,
    val error: String?
)

