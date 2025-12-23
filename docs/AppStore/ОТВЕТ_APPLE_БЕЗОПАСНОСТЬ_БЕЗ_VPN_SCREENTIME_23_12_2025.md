# ОТВЕТ APPLE: БЕЗОПАСНОСТЬ БЕЗ NEVPNManager, Screen Time API, PermissionKit

**Дата:** 23 декабря 2025  
**Submission ID:** 11470d23-e822-4879-a355-c514bdbd6a1c  
**Версия:** 1.0 (Build 15)

---

## 📋 ВОПРОС APPLE

**Guideline 2.1 - Information Needed**

**Вопрос:**
- How are you able to provide security and parental control features without using NEVPNManager API, Screen Time API, and/or PermissionKit framework?

---

## ✅ ВАРИАНТ 1: КРАТКИЙ И ТЕХНИЧЕСКИЙ (Оценка: 8/10)

**Преимущества:** Четкий, технический, без лишнего  
**Недостатки:** Может показаться слишком кратким

---

Hello,

Thank you for your question. We provide security and parental control features using standard iOS APIs and our backend server, without requiring NEVPNManager, Screen Time API, or PermissionKit framework.

### **1. SECURITY FEATURES (Безопасность)**

**iOS Native Frameworks Used:**
- **`LocalAuthentication`** - Biometric authentication (Face ID/Touch ID)
  - File: `Core/Security/SecurityManager.swift`
  - Data processed only on device, never transmitted

- **`CryptoKit`** - Data encryption (AES-256-GCM)
  - File: `Core/Security/SecurityManager.swift`
  - Local encryption, keys stored in Keychain

- **`Security` framework** - Keychain Services
  - File: `Core/Security/SecurityManager.swift`
  - Secure storage of tokens, passwords, encryption keys

- **`URLSession`** - HTTPS/TLS 1.2+ communication
  - File: `Core/Network/NetworkManager.swift`
  - SSL Pinning for secure backend communication

**What We Do NOT Use:**
- ❌ **NEVPNManager** - Not used (NetworkExtension framework is commented out in code)
- ❌ **VPN functionality** - Removed from app per Apple guidelines

### **2. PARENTAL CONTROL FEATURES (Родительский контроль)**

**iOS Native Frameworks Used:**
- **`SwiftUI`** - User interface
  - File: `Screens/07_ParentalControlScreen.swift`
  - Settings and monitoring screens

- **`UserDefaults` / `@AppStorage`** - Local settings storage
  - File: `ViewModels/ParentalControlViewModel.swift`
  - Parental control preferences stored locally

- **`CoreLocation`** (optional, with user permission)
  - File: Location features (if enabled by user)
  - Used only for family safety features with explicit consent

- **`UserNotifications`** - Local notifications
  - File: `Core/Notifications/NotificationManager.swift`
  - Alerts and reminders

**Backend Server Integration:**
- **Custom REST API** - Our own backend server
  - File: `Core/Network/APIService.swift`
  - Endpoints: `/family/members`, `/family/stats`, `/analytics`, `/parental-control/*`
  - Server-side analytics and threat detection
  - Parental control rules stored on server, synchronized across family devices

**What We Do NOT Use:**
- ❌ **Screen Time API** - Not used (we provide our own monitoring through backend analytics)
- ❌ **PermissionKit framework** - Not used (we use standard iOS permission requests)

### **3. HOW IT WORKS**

**Security:**
1. User data encrypted locally using CryptoKit (AES-256-GCM)
2. Encrypted data sent to backend via HTTPS with SSL Pinning
3. Backend analyzes threats using AI/ML (3,581+ security functions)
4. Results sent back to app for display
5. No system-level blocking - we provide recommendations and alerts

**Parental Control:**
1. Parents configure rules in app (stored locally and on server)
2. App monitors activity through backend analytics (not system-level monitoring)
3. Parents receive reports and notifications
4. Children see their interface with time limits and content suggestions
5. No forced blocking - we provide guidance and family communication tools

### **4. COMPLIANCE**

- ✅ We follow Apple's App Store Review Guidelines
- ✅ We do not use restricted APIs (NEVPNManager, Screen Time API, PermissionKit)
- ✅ We use only standard iOS frameworks available to all developers
- ✅ All permissions requested with clear descriptions in Info.plist
- ✅ User data handled according to our Privacy Policy

If you need additional technical details or code examples, we are happy to provide them.

Best regards,  
Sergey Khlystov  
ALADDIN

---

## ✅ ВАРИАНТ 2: ПОДРОБНЫЙ С ОБЪЯСНЕНИЕМ АРХИТЕКТУРЫ (Оценка: 9/10)

**Преимущества:** Полное объяснение, показывает понимание архитектуры  
**Недостатки:** Длиннее, но более убедительный

---

Hello,

Thank you for your question. We understand your concern and are happy to explain how our app provides security and parental control features using standard iOS APIs and our backend infrastructure, without requiring NEVPNManager, Screen Time API, or PermissionKit framework.

### **1. SECURITY FEATURES - TECHNICAL IMPLEMENTATION**

**A. Data Protection (Защита данных):**

We use standard iOS security frameworks:

1. **LocalAuthentication Framework:**
   - **File:** `Core/Security/SecurityManager.swift`
   - **Usage:** Biometric authentication (Face ID/Touch ID)
   - **Implementation:** `LAContext.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)`
   - **Data handling:** All biometric data processed locally in Secure Enclave, never transmitted

2. **CryptoKit Framework:**
   - **File:** `Core/Security/SecurityManager.swift`
   - **Usage:** Local data encryption
   - **Algorithm:** AES-256-GCM
   - **Implementation:** `AES.GCM.seal()` for encryption, `AES.GCM.open()` for decryption
   - **Key storage:** Encryption keys stored in Keychain using Security framework

3. **Security Framework (Keychain Services):**
   - **File:** `Core/Security/SecurityManager.swift`
   - **Usage:** Secure storage of sensitive data
   - **Implementation:** Custom Keychain wrapper using `kSecClassGenericPassword`
   - **Stored items:** JWT tokens, encryption keys, passwords (all encrypted)

**B. Network Security (Сетевая безопасность):**

1. **URLSession with SSL Pinning:**
   - **File:** `Core/Network/NetworkManager.swift`
   - **Usage:** Secure HTTPS communication with backend
   - **Implementation:** Certificate pinning in `urlSession(_:didReceive:completionHandler:)`
   - **Protocol:** TLS 1.2+ only
   - **Protection:** Prevents MITM attacks

2. **Backend Threat Detection:**
   - **File:** `Core/Network/APIService.swift`
   - **Endpoints:** `/protection/*`, `/analytics/threats`, `/analytics/top-threats`
   - **How it works:**
     - App sends anonymized threat data to backend
     - Backend analyzes using AI/ML (3,581+ security functions)
     - Results returned to app for display
     - No system-level network blocking

**C. What We Do NOT Use:**

- ❌ **NEVPNManager / NetworkExtension:** 
  - **Status:** Framework import is commented out in code
  - **File:** `Core/NetworkProtection/NetworkProtectionManager.swift` (line 2: `// import NetworkExtension`)
  - **Reason:** We removed VPN functionality per Apple guidelines for individual developers
  - **Current implementation:** Network protection is advisory only, through backend analytics

### **2. PARENTAL CONTROL FEATURES - TECHNICAL IMPLEMENTATION**

**A. Settings and Configuration (Настройки):**

1. **SwiftUI + UserDefaults:**
   - **File:** `Screens/07_ParentalControlScreen.swift`
   - **File:** `ViewModels/ParentalControlViewModel.swift`
   - **Usage:** Parental control settings interface
   - **Storage:** Settings stored locally using `@AppStorage` and `UserDefaults`
   - **Synchronization:** Settings also stored on backend server for multi-device sync

2. **Backend API Integration:**
   - **File:** `Core/Network/APIService.swift`
   - **Endpoints:**
     - `/api/v1/parental-control/rules` - Apply parental control rules
     - `/api/v1/parental-control/stats` - Get statistics
     - `/api/v1/parental-control/access-requests` - Handle access requests
   - **How it works:**
     - Parents configure rules in app
     - Rules sent to backend server
     - Backend stores rules and provides analytics
     - App displays reports and statistics
     - **No system-level enforcement** - we provide monitoring and recommendations

**B. Monitoring and Analytics (Мониторинг):**

1. **Backend Analytics:**
   - **File:** `Core/Network/APIService.swift`
   - **Endpoints:** `/analytics`, `/analytics/threats`
   - **How it works:**
     - App collects anonymized usage statistics
     - Data sent to backend for analysis
     - Backend provides aggregated reports
     - Parents see reports in app
     - **No real-time system monitoring** - we provide historical analytics

2. **Location Services (Optional, with permission):**
   - **Framework:** CoreLocation
   - **Usage:** Family safety features (geofencing, location sharing)
   - **Permission:** Requested with clear description in Info.plist
   - **Implementation:** Standard `CLLocationManager` API
   - **Privacy:** Location data only used when explicitly enabled by user

**C. What We Do NOT Use:**

- ❌ **Screen Time API:**
  - **Status:** Not used
  - **Reason:** We provide our own monitoring through backend analytics
  - **Alternative:** We track app usage through our own analytics system (with user consent)

- ❌ **PermissionKit Framework:**
  - **Status:** Not used
  - **Reason:** We use standard iOS permission requests (Info.plist descriptions)
  - **Implementation:** Standard `requestWhenInUseAuthorization()` for location, etc.

### **3. ARCHITECTURE OVERVIEW**

**Client-Server Architecture:**

```
iOS App (Client)                    Backend Server
├── SecurityManager                 ├── Threat Detection (AI/ML)
│   └── Local encryption            ├── Behavioral Analysis
├── NetworkManager                  ├── Parental Control Rules
│   └── HTTPS + SSL Pinning        ├── Analytics Engine
├── ParentalControlScreen           └── 3,581+ security functions
│   └── Settings UI
└── APIService
    └── REST API calls
```

**Key Points:**
1. **No system-level blocking** - We provide recommendations, alerts, and family communication
2. **Backend-powered** - Most security and parental control logic runs on our server
3. **Standard iOS APIs only** - We use only publicly available iOS frameworks
4. **User consent required** - All features require explicit user permission

### **4. COMPLIANCE WITH APPLE GUIDELINES**

- ✅ **Guideline 2.1:** We use only standard iOS APIs, no restricted frameworks
- ✅ **Guideline 5.4:** We removed VPN functionality (NetworkExtension commented out)
- ✅ **Guideline 2.5.1:** All permissions requested with clear descriptions
- ✅ **Guideline 5.1.1:** Privacy Policy clearly explains data collection and usage
- ✅ **Guideline 1.1.6:** We do not provide system-level security features that require special permissions

### **5. CODE EVIDENCE**

**NetworkExtension Removal:**
```swift
// File: Core/NetworkProtection/NetworkProtectionManager.swift
// import NetworkExtension  // ✅ ЗАКОММЕНТИРОВАНО: Apple не разрешает VPN
```

**Standard APIs Used:**
```swift
// File: Core/Security/SecurityManager.swift
import LocalAuthentication  // ✅ Standard iOS API
import CryptoKit            // ✅ Standard iOS API
import Security             // ✅ Standard iOS API
```

If you need access to specific code files or additional technical documentation, we are happy to provide them.

Best regards,  
Sergey Khlystov  
ALADDIN  
Email: sergey21-02-84@list.ru  
Phone: +7 (927) 005-15-77

---

## ✅ ВАРИАНТ 3: С АКЦЕНТОМ НА СООТВЕТСТВИЕ ПОЛИТИКАМ APPLE (Оценка: 10/10)

**Преимущества:** Самый безопасный, показывает полное соответствие политикам  
**Недостатки:** Самый длинный, но самый убедительный

---

Hello,

Thank you for your question and for the opportunity to clarify our implementation. We want to assure you that our app fully complies with Apple's App Store Review Guidelines and uses only standard iOS APIs available to all developers.

### **1. OUR APPROACH: ADVISORY SECURITY AND FAMILY GUIDANCE**

We want to be completely transparent: **Our app does NOT provide system-level security or parental control features.** Instead, we provide:

1. **Advisory Security Features:**
   - Threat detection through backend AI/ML analysis
   - Recommendations and alerts to users
   - Educational content about security
   - **No system-level blocking or enforcement**

2. **Family Guidance Tools:**
   - Parental control settings and preferences
   - Family communication features
   - Usage reports and analytics
   - Time management suggestions
   - **No forced restrictions or system-level monitoring**

### **2. TECHNICAL IMPLEMENTATION - STANDARD iOS APIs ONLY**

**A. Security Features (Безопасность):**

**1. Local Data Protection:**
- **Framework:** `LocalAuthentication` (standard iOS API)
  - **File:** `Core/Security/SecurityManager.swift`
  - **Usage:** Biometric authentication for app access
  - **Compliance:** ✅ Standard API, no special permissions required

- **Framework:** `CryptoKit` (standard iOS API)
  - **File:** `Core/Security/SecurityManager.swift`
  - **Usage:** Local encryption of user data (AES-256-GCM)
  - **Compliance:** ✅ Standard API, data encrypted on device only

- **Framework:** `Security` (Keychain Services, standard iOS API)
  - **File:** `Core/Security/SecurityManager.swift`
  - **Usage:** Secure storage of tokens and keys
  - **Compliance:** ✅ Standard API, data stored locally

**2. Network Communication:**
- **Framework:** `URLSession` (standard iOS API)
  - **File:** `Core/Network/NetworkManager.swift`
  - **Usage:** HTTPS communication with backend server
  - **Implementation:** SSL Pinning for certificate validation
  - **Compliance:** ✅ Standard API, no VPN functionality

**3. Backend Security Analysis:**
- **File:** `Core/Network/APIService.swift`
- **Endpoints:** `/protection/*`, `/analytics/threats`
- **How it works:**
  - App sends anonymized data to our backend
  - Backend analyzes using AI/ML (server-side, not on device)
  - Results returned as recommendations
  - **No system-level actions taken**

**B. Parental Control Features (Родительский контроль):**

**1. Settings Interface:**
- **Framework:** `SwiftUI` (standard iOS API)
  - **File:** `Screens/07_ParentalControlScreen.swift`
  - **Usage:** User interface for parental control settings
  - **Compliance:** ✅ Standard API

- **Framework:** `UserDefaults` / `@AppStorage` (standard iOS API)
  - **File:** `ViewModels/ParentalControlViewModel.swift`
  - **Usage:** Local storage of user preferences
  - **Compliance:** ✅ Standard API

**2. Backend Analytics:**
- **File:** `Core/Network/APIService.swift`
- **Endpoints:** `/api/v1/parental-control/*`, `/analytics`
- **How it works:**
  - Parents configure preferences in app
  - Preferences stored on backend server
  - Backend provides analytics and reports
  - App displays reports to parents
  - **No system-level enforcement** - parents use reports to guide their children

**3. Optional Location Services:**
- **Framework:** `CoreLocation` (standard iOS API)
  - **Usage:** Family safety features (geofencing, location sharing)
  - **Permission:** Requested with clear description in Info.plist
  - **Compliance:** ✅ Standard API, explicit user consent required

### **3. WHAT WE DO NOT USE (И ЧТО МЫ НЕ ИСПОЛЬЗУЕМ)**

**A. NEVPNManager / NetworkExtension:**
- ❌ **Status:** NOT used
- **Evidence:** Import statement commented out in code
  ```swift
  // File: Core/NetworkProtection/NetworkProtectionManager.swift, line 2
  // import NetworkExtension  // ✅ ЗАКОММЕНТИРОВАНО: Apple не разрешает VPN
  ```
- **Reason:** We removed VPN functionality per Apple's guidelines for individual developers (Guideline 5.4)
- **Current implementation:** Network protection is advisory only, through backend threat analysis

**B. Screen Time API:**
- ❌ **Status:** NOT used
- **Reason:** We provide our own analytics through backend server
- **Alternative:** We track app usage through our custom analytics (with user consent)
- **Compliance:** ✅ We do not access system-level screen time data

**C. PermissionKit Framework:**
- ❌ **Status:** NOT used
- **Reason:** We use standard iOS permission requests
- **Implementation:** Standard `Info.plist` descriptions and `requestAuthorization()` methods
- **Compliance:** ✅ All permissions requested with clear descriptions

### **4. HOW OUR SYSTEM WORKS (КАК РАБОТАЕТ НАША СИСТЕМА)**

**Security Flow:**
```
1. User enables security features in app
2. App encrypts data locally (CryptoKit)
3. Encrypted data sent to backend via HTTPS
4. Backend analyzes using AI/ML (3,581+ security functions)
5. Results sent back as recommendations
6. App displays alerts and suggestions
7. User makes informed decisions
→ NO system-level blocking or enforcement
```

**Parental Control Flow:**
```
1. Parent configures rules in app
2. Rules stored locally and on backend
3. Backend provides analytics and reports
4. Parent receives reports in app
5. Parent uses reports to guide children
6. Family communication tools available
→ NO forced restrictions or system-level monitoring
```

### **5. COMPLIANCE WITH APPLE GUIDELINES**

**✅ Guideline 2.1 - Performance:**
- We use only standard iOS APIs
- No restricted frameworks or private APIs
- All functionality works as described

**✅ Guideline 5.4 - VPN:**
- VPN functionality removed (NetworkExtension commented out)
- No VPN-related code in active use
- Network protection is advisory only

**✅ Guideline 2.5.1 - Software Requirements:**
- All permissions requested with clear descriptions in Info.plist
- No misleading permission requests
- User consent required for all features

**✅ Guideline 5.1.1 - Privacy:**
- Privacy Policy clearly explains data collection
- User data handled according to policy
- No data sold to third parties

**✅ Guideline 1.1.6 - Safety:**
- We do not provide system-level security features
- All features are advisory and educational
- Users maintain full control

### **6. CODE EVIDENCE**

**NetworkExtension Removal:**
```swift
// File: Core/NetworkProtection/NetworkProtectionManager.swift
// Line 2:
// import NetworkExtension  // ✅ ЗАКОММЕНТИРОВАНО: Apple не разрешает VPN

// Line 17-19:
// ✅ ЗАКОММЕНТИРОВАНО: NetworkExtension больше не используется
// NetworkExtension
// private var tunnelManager: NETunnelProviderManager?
```

**Standard APIs Used:**
```swift
// File: Core/Security/SecurityManager.swift
import Foundation
import Security          // ✅ Standard iOS API
import LocalAuthentication  // ✅ Standard iOS API
import CryptoKit        // ✅ Standard iOS API
```

**Parental Control Implementation:**
```swift
// File: Screens/07_ParentalControlScreen.swift
// Uses standard SwiftUI and @AppStorage
@AppStorage("parental_selected_child") private var selectedChild: String = ""
// No Screen Time API or PermissionKit used
```

### **7. SUMMARY**

**Our app provides:**
- ✅ Advisory security features (threat detection, recommendations)
- ✅ Family guidance tools (settings, reports, communication)
- ✅ Educational content about security
- ✅ Backend-powered analytics

**Our app does NOT provide:**
- ❌ System-level security blocking
- ❌ Forced parental control restrictions
- ❌ VPN functionality (removed per guidelines)
- ❌ System-level screen time monitoring

**We use:**
- ✅ Only standard iOS APIs (LocalAuthentication, CryptoKit, Security, URLSession, SwiftUI, UserDefaults, CoreLocation)
- ✅ Our own backend server for AI/ML analysis
- ✅ Standard permission requests with clear descriptions

**We comply with:**
- ✅ All Apple App Store Review Guidelines
- ✅ User privacy and data protection requirements
- ✅ No restricted or private APIs

We are happy to provide additional code examples, technical documentation, or answer any further questions you may have.

Best regards,  
Sergey Khlystov  
ALADDIN  
Email: sergey21-02-84@list.ru  
Phone: +7 (927) 005-15-77

---

## 📊 СРАВНЕНИЕ ВАРИАНТОВ

| Критерий | Вариант 1 | Вариант 2 | Вариант 3 |
|----------|-----------|-----------|-----------|
| **Длина** | Краткий | Средний | Длинный |
| **Технические детали** | Базовые | Подробные | Очень подробные |
| **Соответствие политикам** | Упоминается | Подробно | Очень подробно |
| **Код-примеры** | Нет | Есть | Есть + больше |
| **Убедительность** | 7/10 | 9/10 | 10/10 |
| **Риск** | Средний | Низкий | Очень низкий |
| **Оценка** | **8/10** | **9/10** | **10/10** |

---

## 🎯 РЕКОМЕНДАЦИЯ

**Рекомендую использовать ВАРИАНТ 3 (10/10):**

**Причины:**
1. ✅ Полное соответствие политикам Apple
2. ✅ Подробное техническое объяснение
3. ✅ Код-примеры для доказательства
4. ✅ Акцент на том, что мы НЕ используем системные API
5. ✅ Объяснение, что функционал - advisory, а не enforcement
6. ✅ Минимальный риск повторного отказа

**Ключевые моменты Варианта 3:**
- Четко объясняет, что мы НЕ предоставляем системную безопасность
- Показывает, что функционал - advisory (рекомендательный)
- Доказывает удаление VPN кода
- Показывает использование только стандартных iOS API
- Подчеркивает соответствие всем Guideline

---

**Дата создания:** 23 декабря 2025  
**Статус:** ✅ ГОТОВО К ОТПРАВКЕ

