# 🔐 JWT SUBSCRIPTION ARCHITECTURE FOR ALADDIN

## 🎯 POLNAYA SPECIFIKACIYA JWT TOKENOV S PODPISKAMI

---

## 📋 JWT PAYLOAD STRUKTURA

### **🔑 OSNOVNAYA STRUKTURA TOKENA:**

```json
{
  "iss": "aladdin_mobile_app",
  "sub": "device_uuid_12345",
  "iat": 1640995200,
  "exp": 1672531200,
  "device_type": "mobile",
  "app_version": "1.0.0",
  "subscription": {
    "id": "sub_12345",
    "level": "premium",
    "status": "active",
    "expires_at": "2024-12-31T23:59:59Z",
    "billing_cycle": "monthly",
    "auto_renew": true,
    "trial_ends_at": null,
    "grace_period_ends_at": null,
    "features": [
      "ai_assistant",
      "family_control",
      "dark_web_monitoring",
      "identity_theft_protection"
    ],
    "limits": {
      "devices": 10,
      "scans_per_day": -1,
      "ai_messages_per_day": -1,
      "reports_per_month": -1
    },
    "permissions": {
      "can_use_ai": true,
      "can_monitor_family": true,
      "can_access_dark_web": true,
      "can_use_emergency": true,
      "can_custom_rules": true
    },
    "usage": {
      "scans_today": 5,
      "ai_messages_today": 12,
      "reports_this_month": 3
    }
  },
  "analytics": {
    "registered_at": "2023-01-01T00:00:00Z",
    "last_active": "2023-12-01T10:30:00Z",
    "total_scans": 150,
    "total_reports": 25,
    "subscription_changes": 2
  }
}
```

---

## 🏗️ DETAILED MODELS

### **🐍 PYTHON MODELS (SERVER-SIDE):**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class SubscriptionLevel(str, Enum):
    TRIAL = "trial"
    FREE = "free"
    BASIC = "basic"
    FAMILY = "family"
    PREMIUM = "premium"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    GRACE_PERIOD = "grace_period"
    PAST_DUE = "past_due"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"

class SubscriptionLimits(BaseModel):
    devices: int = Field(default=1, description="Maximum devices")
    scans_per_day: int = Field(default=10, description="Daily scan limit")
    ai_messages_per_day: int = Field(default=0, description="AI messages per day")
    reports_per_month: int = Field(default=3, description="Monthly reports")

class SubscriptionPermissions(BaseModel):
    can_use_ai: bool = Field(default=False)
    can_monitor_family: bool = Field(default=False)
    can_access_dark_web: bool = Field(default=False)
    can_use_emergency: bool = Field(default=False)
    can_custom_rules: bool = Field(default=False)
    can_api_integrations: bool = Field(default=False)

class SubscriptionUsage(BaseModel):
    scans_today: int = Field(default=0)
    ai_messages_today: int = Field(default=0)
    reports_this_month: int = Field(default=0)
    last_reset_date: Optional[datetime] = None

class SubscriptionInfo(BaseModel):
    id: str = Field(..., description="Subscription unique ID")
    level: SubscriptionLevel
    status: SubscriptionStatus
    expires_at: datetime
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    auto_renew: bool = True
    trial_ends_at: Optional[datetime] = None
    grace_period_ends_at: Optional[datetime] = None
    features: List[str] = Field(default_factory=list)
    limits: SubscriptionLimits = Field(default_factory=SubscriptionLimits)
    permissions: SubscriptionPermissions = Field(default_factory=SubscriptionPermissions)
    usage: SubscriptionUsage = Field(default_factory=SubscriptionUsage)

class AnalyticsInfo(BaseModel):
    registered_at: datetime
    last_active: datetime
    total_scans: int = 0
    total_reports: int = 0
    subscription_changes: int = 0
    app_launches: int = 0

class JWTPayload(BaseModel):
    iss: str = "aladdin_mobile_app"
    sub: str = Field(..., description="Device UUID")
    iat: int
    exp: int
    device_type: str = "mobile"
    app_version: str = "1.0.0"
    subscription: SubscriptionInfo
    analytics: AnalyticsInfo = Field(default_factory=AnalyticsInfo)
```

---

## 📱 SWIFT MODELS (CLIENT-SIDE):

```swift
import Foundation

enum SubscriptionLevel: String, Codable {
    case trial = "trial"
    case free = "free"
    case basic = "basic"
    case family = "family"
    case premium = "premium"
}

enum SubscriptionStatus: String, Codable {
    case active = "active"
    case expired = "expired"
    case cancelled = "cancelled"
    case gracePeriod = "grace_period"
    case pastDue = "past_due"
}

enum BillingCycle: String, Codable {
    case monthly = "monthly"
    case yearly = "yearly"
    case lifetime = "lifetime"
}

struct SubscriptionLimits: Codable {
    let devices: Int
    let scansPerDay: Int
    let aiMessagesPerDay: Int
    let reportsPerMonth: Int

    static let free = SubscriptionLimits(devices: 1, scansPerDay: 10, aiMessagesPerDay: 0, reportsPerMonth: 3)
    static let basic = SubscriptionLimits(devices: 3, scansPerDay: 50, aiMessagesPerDay: 20, reportsPerMonth: 10)
    static let family = SubscriptionLimits(devices: 5, scansPerDay: 100, aiMessagesPerDay: 50, reportsPerMonth: 25)
    static let premium = SubscriptionLimits(devices: 10, scansPerDay: -1, aiMessagesPerDay: -1, reportsPerMonth: -1)
}

struct SubscriptionPermissions: Codable {
    let canUseAI: Bool
    let canMonitorFamily: Bool
    let canAccessDarkWeb: Bool
    let canUseEmergency: Bool
    let canCustomRules: Bool
    let canAPIIntegrations: Bool
}

struct SubscriptionUsage: Codable {
    var scansToday: Int
    var aiMessagesToday: Int
    var reportsThisMonth: Int
    var lastResetDate: Date?

    mutating func resetIfNeeded() {
        let calendar = Calendar.current
        let now = Date()

        if let lastReset = lastResetDate,
           !calendar.isDate(lastReset, inSameDayAs: now) {
            // Reset daily counters
            scansToday = 0
            aiMessagesToday = 0
            lastResetDate = now
        }

        // Reset monthly counter if new month
        if let lastReset = lastResetDate,
           calendar.component(.month, from: lastReset) != calendar.component(.month, from: now) {
            reportsThisMonth = 0
        }
    }
}

struct SubscriptionInfo: Codable {
    let id: String
    let level: SubscriptionLevel
    let status: SubscriptionStatus
    let expiresAt: Date
    let billingCycle: BillingCycle
    let autoRenew: Bool
    let trialEndsAt: Date?
    let gracePeriodEndsAt: Date?
    let features: [String]
    let limits: SubscriptionLimits
    let permissions: SubscriptionPermissions
    var usage: SubscriptionUsage

    var isActive: Bool {
        status == .active && expiresAt > Date()
    }

    var isInTrial: Bool {
        level == .trial && (trialEndsAt ?? Date.distantPast) > Date()
    }

    var isInGracePeriod: Bool {
        status == .gracePeriod && (gracePeriodEndsAt ?? Date.distantPast) > Date()
    }
}

struct AnalyticsInfo: Codable {
    let registeredAt: Date
    let lastActive: Date
    var totalScans: Int
    var totalReports: Int
    var subscriptionChanges: Int
    var appLaunches: Int
}

struct JWTPayload: Codable {
    let iss: String
    let sub: String
    let iat: Int
    let exp: Int
    let deviceType: String
    let appVersion: String
    let subscription: SubscriptionInfo
    let analytics: AnalyticsInfo
}
```

---

## 🔄 TOKEN LIFECYCLE MANAGEMENT

### **🎯 KOGDA OBNOVLYAT TOKEN:**

#### **1. PRI KAZHDOM ZAPUSKE APP:**
```swift
class AuthManager {
    func refreshTokenIfNeeded() async {
        guard let currentToken = keychain.getToken() else {
            await registerDeviceAnonymously()
            return
        }

        // Check if token is close to expiration (within 24 hours)
        if isTokenExpiringSoon(currentToken) {
            await refreshToken()
        }

        // Check if subscription changed on server
        if await hasSubscriptionChanged() {
            await refreshToken()
        }
    }
}
```

#### **2. POSLE IZMENENIYA PODPISKI:**
```swift
func handleSubscriptionPurchase(_ productId: String) async {
    // Process payment through App Store
    let transaction = try await processPayment(productId)

    // Update subscription on server
    let updatedSubscription = try await apiService.updateSubscription(transaction)

    // Force token refresh to get new subscription data
    await authManager.forceTokenRefresh()
}
```

#### **3. PRI PREVYSHENII LIMITOV:**
```swift
func checkAndUpdateUsage(_ feature: AppFeature) async {
    guard let token = authManager.currentToken else { return }

    // Check local usage first
    if !token.subscription.canUseFeature(feature) {
        throw SubscriptionError.featureNotAvailable
    }

    // Update usage on server
    try await apiService.updateUsage(feature)

    // Refresh token to get updated usage counters
    await authManager.refreshToken()
}
```

---

## 🛡️ SECURITY & VALIDATION

### **🔐 SERVER-SIDE VALIDATION:**

```python
def validate_subscription_token(token: str) -> dict:
    """
    Validate JWT token and extract subscription info
    """
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Validate issuer
        if payload.get("iss") != "aladdin_mobile_app":
            raise HTTPException(401, "Invalid token issuer")

        # Check expiration
        if payload["exp"] < datetime.utcnow().timestamp():
            raise HTTPException(401, "Token expired")

        # Validate subscription
        subscription = payload.get("subscription", {})
        if not validate_subscription_data(subscription):
            raise HTTPException(403, "Invalid subscription")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

def validate_subscription_data(subscription: dict) -> bool:
    """
    Validate subscription data integrity
    """
    required_fields = ["id", "level", "status", "expires_at"]
    for field in required_fields:
        if field not in subscription:
            return False

    # Validate level
    valid_levels = ["trial", "free", "basic", "family", "premium"]
    if subscription["level"] not in valid_levels:
        return False

    # Validate expiration
    expires_at = subscription.get("expires_at")
    if not expires_at or datetime.fromisoformat(expires_at) < datetime.utcnow():
        return False

    return True
```

---

## 🚪 FEATURE GATING LOGIC

### **🎯 UNIFIED FEATURE CHECK:**

```swift
enum AppFeature: String {
    case aiAssistant = "ai_assistant"
    case familyControl = "family_control"
    case darkWebMonitoring = "dark_web_monitoring"
    case identityTheftProtection = "identity_theft_protection"
    case crashDetection = "crash_detection"
    case emergencyCall = "emergency_call"
    case roadsideAssistance = "roadside_assistance"
    case customRules = "custom_rules"
    case apiIntegrations = "api_integrations"

    func requiredLevel() -> SubscriptionLevel {
        switch self {
        case .aiAssistant: return .basic
        case .familyControl: return .family
        case .darkWebMonitoring: return .premium
        case .identityTheftProtection: return .premium
        case .crashDetection: return .basic
        case .emergencyCall: return .basic
        case .roadsideAssistance: return .family
        case .customRules: return .basic
        case .apiIntegrations: return .premium
        }
    }

    func checkLimits(usage: SubscriptionUsage, limits: SubscriptionLimits) -> Bool {
        switch self {
        case .aiAssistant:
            return limits.aiMessagesPerDay == -1 || usage.aiMessagesToday < limits.aiMessagesPerDay
        case .darkWebMonitoring, .identityTheftProtection:
            return limits.scansPerDay == -1 || usage.scansToday < limits.scansPerDay
        default:
            return true
        }
    }
}

extension SubscriptionInfo {
    func canUseFeature(_ feature: AppFeature) -> Bool {
        // Check subscription level
        let requiredLevel = feature.requiredLevel()
        guard level.hasAccessTo(requiredLevel) else { return false }

        // Check permissions
        switch feature {
        case .aiAssistant: return permissions.canUseAI
        case .familyControl: return permissions.canMonitorFamily
        case .darkWebMonitoring: return permissions.canAccessDarkWeb
        case .identityTheftProtection: return permissions.canAccessDarkWeb
        case .customRules: return permissions.canCustomRules
        case .apiIntegrations: return permissions.canAPIIntegrations
        default: return true
        }

        // Check limits
        return feature.checkLimits(usage, limits)
    }
}

extension SubscriptionLevel {
    func hasAccessTo(_ requiredLevel: SubscriptionLevel) -> Bool {
        let hierarchy: [SubscriptionLevel] = [.trial, .free, .basic, .family, .premium]
        guard let currentIndex = hierarchy.firstIndex(of: self),
              let requiredIndex = hierarchy.firstIndex(of: requiredLevel) else {
            return false
        }
        return currentIndex >= requiredIndex
    }
}
```

---

## 📊 USAGE TRACKING & LIMITS

### **📈 REAL-TIME USAGE MONITORING:**

```swift
class UsageTracker {
    static let shared = UsageTracker()

    private var usageQueue: [UsageEvent] = []
    private let queue = DispatchQueue(label: "usage.tracker")

    func trackUsage(_ feature: AppFeature) {
        queue.async {
            let event = UsageEvent(feature: feature, timestamp: Date(), deviceId: Device.current.id)
            self.usageQueue.append(event)

            // Batch send to server every 10 events or 5 minutes
            if self.usageQueue.count >= 10 {
                self.flushUsage()
            }
        }
    }

    private func flushUsage() {
        let eventsToSend = usageQueue
        usageQueue.removeAll()

        Task {
            do {
                try await APIService.shared.sendUsageEvents(eventsToSend)
                // Update local token after server sync
                await AuthManager.shared.refreshToken()
            } catch {
                // Re-queue failed events
                queue.async {
                    self.usageQueue.insert(contentsOf: eventsToSend, at: 0)
                }
            }
        }
    }
}

struct UsageEvent: Codable {
    let feature: String
    let timestamp: Date
    let deviceId: String
    let metadata: [String: AnyCodable]? = nil
}
```

---

## 🔄 SUBSCRIPTION STATE MANAGEMENT

### **📱 CLIENT-SIDE STATE MANAGEMENT:**

```swift
class SubscriptionManager: ObservableObject {
    @Published var currentSubscription: SubscriptionInfo?
    @Published var isLoading = false
    @Published var error: Error?

    private let authManager: AuthManager
    private var refreshTimer: Timer?

    init(authManager: AuthManager = .shared) {
        self.authManager = authManager
        setupSubscriptionMonitoring()
    }

    private func setupSubscriptionMonitoring() {
        // Refresh subscription every 5 minutes
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 300, repeats: true) { [weak self] _ in
            Task {
                await self?.refreshSubscription()
            }
        }
    }

    func refreshSubscription() async {
        isLoading = true
        defer { isLoading = false }

        do {
            let token = try await authManager.refreshToken()
            currentSubscription = token.subscription
            error = nil
        } catch {
            self.error = error
            // Keep current subscription if refresh fails
        }
    }

    func upgrade(to level: SubscriptionLevel) async throws {
        isLoading = true
        defer { isLoading = false }

        // Process upgrade through App Store
        let productId = level.productId
        let transaction = try await StoreManager.shared.purchase(productId)

        // Update subscription on server
        try await APIService.shared.updateSubscription(transaction)

        // Refresh local subscription
        await refreshSubscription()
    }

    func cancelSubscription() async throws {
        guard let subscriptionId = currentSubscription?.id else { return }

        try await APIService.shared.cancelSubscription(subscriptionId)
        await refreshSubscription()
    }
}
```

---

## 🚨 ERROR HANDLING & FALLBACKS

### **⚠️ SUBSCRIPTION ERRORS:**

```swift
enum SubscriptionError: LocalizedError {
    case featureLocked(feature: AppFeature)
    case usageLimitExceeded(feature: AppFeature, current: Int, limit: Int)
    case subscriptionExpired(expiredAt: Date)
    case subscriptionCancelled
    case paymentRequired
    case networkError
    case serverError

    var errorDescription: String? {
        switch self {
        case .featureLocked(let feature):
            return "Feature '\(feature.rawValue)' requires subscription upgrade"
        case .usageLimitExceeded(let feature, let current, let limit):
            return "Usage limit exceeded for \(feature.rawValue): \(current)/\(limit)"
        case .subscriptionExpired(let expiredAt):
            return "Subscription expired on \(expiredAt.formatted())"
        case .subscriptionCancelled:
            return "Subscription was cancelled"
        case .paymentRequired:
            return "Payment required to continue using this feature"
        case .networkError:
            return "Unable to verify subscription. Please check your connection."
        case .serverError:
            return "Subscription service temporarily unavailable"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .featureLocked:
            return "Upgrade your subscription to access this feature"
        case .usageLimitExceeded:
            return "Wait until tomorrow or upgrade your plan"
        case .subscriptionExpired, .subscriptionCancelled:
            return "Renew your subscription to continue using all features"
        case .paymentRequired:
            return "Update your payment method"
        default:
            return "Try again later"
        }
    }
}
```

---

## 📈 ANALYTICS & MONITORING

### **📊 SUBSCRIPTION ANALYTICS:**

```swift
struct SubscriptionAnalytics {
    static func trackSubscriptionEvent(_ event: SubscriptionEvent, metadata: [String: Any] = [:]) {
        var params = metadata
        params["subscription_level"] = currentSubscription?.level.rawValue
        params["device_id"] = Device.current.id
        params["timestamp"] = Date()

        AnalyticsManager.shared.track(event: "subscription_\(event.rawValue)", parameters: params)
    }
}

enum SubscriptionEvent: String {
    case viewed_upgrade_prompt
    case started_upgrade_flow
    case completed_upgrade
    case cancelled_upgrade
    case hit_usage_limit
    case subscription_expired
    case trial_ended
    case feature_access_denied
    case token_refresh_success
    case token_refresh_failed
}
```

---

## 🎯 IMPLEMENTATION CHECKLIST

### **✅ SERVER-SIDE:**
- [ ] Pydantic models for JWT payload
- [ ] JWT generation with subscription data
- [ ] Token validation middleware
- [ ] Feature access control
- [ ] Usage tracking endpoints
- [ ] Subscription management API

### **✅ CLIENT-SIDE:**
- [ ] JWT decoding and parsing
- [ ] Subscription state management
- [ ] Feature gating logic
- [ ] Usage tracking
- [ ] Error handling
- [ ] UI components for upgrades

### **✅ SECURITY:**
- [ ] Token encryption
- [ ] Server-side validation
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Graceful degradation

### **✅ TESTING:**
- [ ] Unit tests for feature gating
- [ ] Integration tests for subscription flow
- [ ] Token validation tests
- [ ] Usage limit tests
- [ ] Error handling tests

---

## 🚀 CONCLUSION

**This JWT subscription architecture provides:**
- **Secure access control** with server-side validation
- **Flexible feature gating** based on subscription levels
- **Real-time usage tracking** with limits enforcement
- **Seamless user experience** with automatic token refresh
- **Scalable analytics** for business intelligence
- **Error resilience** with fallback mechanisms

**The system is ready for production with proper subscription management!** 🎯✨