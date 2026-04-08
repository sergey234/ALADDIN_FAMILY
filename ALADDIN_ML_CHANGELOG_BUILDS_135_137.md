# ALADDIN Mobile App: Technical Changelog & Architectural Updates (Builds 135 - 137)

**Target Audience:** ML Systems, Backend Developers, Technical Architects
**Module:** `ALADDIN_iOS` (Swift, iOS Client)
**Timeframe:** Builds 135 -> 136 -> 137

This document provides a detailed, technical breakdown of all architectural changes, bug fixes, and logic refactoring implemented in the mobile application to stabilize subscription management, rate limiting, and UI synchronization.

---

## 1. Core Architecture & Stability Updates (Build 136)

### 1.1. Thread-Safe Client-Side Rate Limiter
- **File:** `Core/Network/RateLimiter.swift`
- **Problem:** Data race condition (`EXC_BAD_ACCESS`) occurred in the `RateLimiter` module when multiple network requests were initiated concurrently. The dictionary `requestCounts: [String: [Date]]` was being mutated simultaneously from different threads.
- **Solution:** 
  - Entire logic rewritten for strict thread safety using `DispatchQueue(label: "com.aladdin.ratelimiter", attributes: .concurrent)`.
  - Removed problematic `cleanOldRequests` function. Integrated memory-efficient filtering directly into access methods (`canMakeRequest`, `recordRequest`).
  - Read operations use `.sync`, while write/mutate operations use `.async(flags: .barrier)` to ensure atomic transactions.
  - Offloaded heavy UI/Logger rendering for "Rate Limit Exceeded" to global background queues to prevent main thread blocking.

---

## 2. Subscription Management & Tariff Logic Refactoring (Build 137)

### 2.1. Explicit Downgrade to Free (Basic) Tier
- **Files:** `Screens/10_TariffsScreen.swift`, `Core/Managers/SubscriptionManager.swift`, `Core/Network/APIService.swift`
- **Problem:** Tapping "Базовый" (Free) on the Tariffs screen executed a `return` no-op instead of contacting the server to explicitly cancel a Trial or paid subscription.
- **Solution:** 
  - Implemented `downgradeToFree()` in `SubscriptionManager`.
  - Mapped UI action to trigger API call to `POST /api/subscription/cancel`.
  - Added logic to clear local trial status, wipe notifications, and forcefully inject a local fallback `.free` subscription state if the server doesn't respond with a new token immediately.

### 2.2. Fixing `422 Unprocessable Entity` on Subscription Cancel
- **Files:** `Core/Models/SubscriptionModels.swift`, `Core/Network/APIService.swift`, `Core/Managers/SubscriptionManager.swift`
- **Problem:** The server strictly required `userId` in the body payload for `POST /api/subscription/cancel`, but the iOS client was sending an empty body.
- **Solution:**
  - Created struct `SubscriptionCancelRequest: Codable` containing `userId`, `deviceId`, and `reason`.
  - Updated API signature `downgradeSubscription` to accept and serialize this payload.
  - `SubscriptionManager` now correctly extracts `userId` from the stored JWT token (or falls back to `your_member_id` from UserDefaults) and constructs the request.

### 2.3. Resilient Parsing of `SubscriptionCancelResponse`
- **File:** `Core/Models/SubscriptionModels.swift`
- **Problem:** `DecodingError`. The client strictly expected `success: Bool` and `newToken: String` in the server response. The server actually replied with `{"status": "success", "message": "Подписка отменена"}`. This caused the iOS JSON decoder to crash and abort the downgrade UI flow.
- **Solution:**
  - Implemented a custom `init(from decoder: Decoder)` for `SubscriptionCancelResponse`.
  - **Fuzzy Boolean/String Logic:** The decoder now checks for a boolean `success`. If absent, it checks if `status == "success"`.
  - All properties (`newToken`, `subscription`, `message`, `status`) made optional (`?`).
  - The mobile app no longer crashes if the server response structure slightly mutates or omits the token.

### 2.4. Enforcing Strict Concurrency (MainActor) for UI State
- **File:** `Core/Managers/SubscriptionManager.swift`
- **Problem:** On real iOS devices (unlike the simulator), attempting to mutate `@Published` properties (which drive the yellow status card on `01_MainScreen`) from a background network thread resulted in the OS silently dropping the UI update to prevent crashes. Thus, the tariff was updated in memory but the UI remained stuck on "Базовый".
- **Solution:**
  - Explicitly marked all state-mutating functions in `SubscriptionManager` with the `@MainActor` attribute:
    - `downgradeToFree()`
    - `activateTrialIfNeeded()`
    - `updateSubscriptionStatus(_:)`
    - `updateTrialStatus(_:)`
    - `syncWithServer()`
  - This guarantees that once the asynchronous network payload returns, the execution context forces a hop to the UI Main Thread before altering `currentSubscription` and `trialStatus`, ensuring instant and reliable re-rendering on real devices.

---

## 3. General Build Configuration

- **Files:** `ALADDIN.xcodeproj/project.pbxproj`, `Core/Config/AppConfig.swift`, `Info.plist`
- **Action:** Bumped `CURRENT_PROJECT_VERSION`, `CFBundleVersion`, and internal static config variable `buildNumber` from `135` -> `136` -> `137`.

---
*End of Technical Log. All systems stable.*