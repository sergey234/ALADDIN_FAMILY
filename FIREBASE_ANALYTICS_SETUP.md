# 📊 Firebase Analytics Setup Guide
## Полная настройка аналитики для ALADDIN

---

## 🎯 ЦЕЛЬ
Настроить Firebase Analytics для отслеживания поведения пользователей, конверсии trial и метрик подписки.

---

## 📋 НЕОБХОДИМЫЕ ШАГИ

### 1. ДОБАВИТЬ FIREBASE SDK

#### Через CocoaPods (рекомендуется):
```ruby
# Podfile
platform :ios, '14.0'

target 'ALADDIN' do
  use_frameworks!

  # Firebase Analytics
  pod 'Firebase/Analytics'
  pod 'Firebase/Crashlytics'

  # Optional: Remote Config для A/B testing
  pod 'Firebase/RemoteConfig'
end
```

#### Установка:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
pod install
```

---

### 2. СКАЧАТЬ GOOGLE-SERVICES.JSON

1. **Перейти в Firebase Console:** https://console.firebase.google.com/
2. **Выбрать проект ALADDIN** (или создать новый)
3. **Добавить iOS приложение:**
   - Bundle ID: `com.aladdin.ios` (проверить в Xcode)
   - App nickname: ALADDIN iOS
4. **Скачать GoogleService-Info.plist**
5. **Добавить файл в Xcode проект:**
   - Перетащить в корень проекта
   - Убедиться что добавлен во все targets

---

### 3. ИНИЦИАЛИЗАЦИЯ FIREBASE

#### В ALADDINApp.swift добавить:
```swift
import SwiftUI
import Firebase

@main
struct ALADDINApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate

    init() {
        // Initialize Firebase
        FirebaseApp.configure()
    }

    // ... остальной код
}
```

#### Или создать AppDelegate:
```swift
import UIKit
import Firebase

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {

        // Initialize Firebase
        FirebaseApp.configure()

        // Configure analytics
        Analytics.setAnalyticsCollectionEnabled(true)

        // Set user properties for subscription analytics
        Analytics.setUserProperty("trial", forName: "subscription_level")

        return true
    }
}
```

---

### 4. ОБНОВИТЬ ANALYTICS MANAGER

#### Разкомментировать Firebase в AnalyticsManager.swift:
```swift
import Foundation
import Firebase // ✅ Uncommented

class AnalyticsManager {

    private init() {
        // Configure Firebase Analytics
        Analytics.setAnalyticsCollectionEnabled(true)
        Analytics.setUserProperty("free", forName: "subscription_level")
    }

    func trackScreen(_ screenName: String, screenClass: String? = nil) {
        // ✅ Production Firebase tracking
        Analytics.logEvent(AnalyticsEventScreenView, parameters: [
            AnalyticsParameterScreenName: screenName,
            AnalyticsParameterScreenClass: screenClass ?? screenName
        ])
    }

    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        let firebaseParams = parameters?.compactMapValues { value in
            if let stringValue = value as? String {
                return stringValue
            } else if let intValue = value as? Int {
                return "\(intValue)"
            } else if let doubleValue = value as? Double {
                return "\(doubleValue)"
            }
            return nil
        }

        Analytics.logEvent(eventName, parameters: firebaseParams)
    }
}
```

---

### 5. ДОБАВИТЬ КЛЮЧЕВЫЕ СОБЫТИЯ ПОДПИСКИ

#### В SubscriptionManager добавить Firebase события:
```swift
// Trial Events
Analytics.logEvent("trial_started", parameters: [
    "duration_days": 14,
    "features_count": 160  // 80% of 200 total features
])

Analytics.logEvent("trial_expiring_soon", parameters: [
    "days_remaining": daysLeft,
    "subscription_level": "trial"
])

// Subscription Events
Analytics.logEvent(AnalyticsEventPurchase, parameters: [
    AnalyticsParameterItemID: productId,
    AnalyticsParameterItemName: productName,
    AnalyticsParameterPrice: price,
    AnalyticsParameterCurrency: "USD"
])

// Upgrade Events
Analytics.logEvent("subscription_upgrade", parameters: [
    "from_level": currentLevel,
    "to_level": newLevel,
    "revenue": upgradePrice
])
```

---

### 6. НАСТРОИТЬ USER PROPERTIES

#### Обновлять свойства пользователя при изменении подписки:
```swift
func updateUserProperties(for subscription: SubscriptionStatus) {
    // Subscription level
    Analytics.setUserProperty(subscription.level.rawValue, forName: "subscription_level")

    // Trial status
    if let trial = subscription.trialInfo {
        Analytics.setUserProperty(trial.isActive ? "active" : "expired", forName: "trial_status")
        Analytics.setUserProperty("\(trial.daysRemaining)", forName: "trial_days_remaining")
    }

    // Revenue tracking
    if subscription.level != .free && subscription.level != .trial {
        Analytics.setUserProperty("paid", forName: "customer_type")
    }
}
```

---

### 7. НАСТРОИТЬ CUSTOM EVENTS

#### Добавить ключевые события для аналитики:
```swift
enum AnalyticsEvent {
    static let trialActivated = "trial_activated"
    static let trialExpired = "trial_expired"
    static let subscriptionPurchased = "subscription_purchased"
    static let featureUsed = "feature_used"
    static let upgradePromptShown = "upgrade_prompt_shown"
    static let upgradeCompleted = "upgrade_completed"
}

// Примеры использования:
Analytics.logEvent(AnalyticsEvent.trialActivated, parameters: [
    "source": "onboarding",
    "device_type": "ios"
])

Analytics.logEvent(AnalyticsEvent.featureUsed, parameters: [
    "feature_name": "antivirus_scan",
    "subscription_level": "trial",
    "usage_count": 1
])
```

---

### 8. НАСТРОИТЬ CONVERSION FUNNELS

#### Отслеживать путь пользователя:
```
1. App Install → First Launch
2. First Launch → Trial Activation
3. Trial Activation → Feature Usage
4. Trial Expiring → Upgrade Prompt
5. Upgrade Prompt → Subscription Purchase
6. Subscription Purchase → Retention
```

#### Firebase Audiences для ретаргетинга:
- Trial Users (last 14 days)
- Expired Trial (last 7 days)
- Paid Subscribers
- High-Value Users (Premium subscribers)

---

### 9. ДОБАВИТЬ CRASHLYTICS

#### Для отслеживания crashes:
```swift
import FirebaseCrashlytics

// Log custom errors
Crashlytics.crashlytics().record(error: error)

// Log user information
Crashlytics.crashlytics().setUserID(userId)
Crashlytics.crashlytics().setCustomValue(subscriptionLevel, forKey: "subscription_level")
```

---

### 10. ТЕСТИРОВАНИЕ НАСТРОЙКИ

#### Проверить в Debug Console:
```swift
// В AnalyticsManager добавить debug logging
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    #if DEBUG
    print("📊 Firebase Event: \(eventName), params: \(parameters ?? [:])")
    #endif

    Analytics.logEvent(eventName, parameters: parameters)
}
```

#### Проверить в Firebase Console:
1. **Events** - должны появляться события
2. **Audiences** - пользователи должны попадать в сегменты
3. **Conversions** - ключевые события должны отслеживаться
4. **Revenue** - покупки должны отображаться

---

## 🎯 КЛЮЧЕВЫЕ МЕТРИКИ ДЛЯ ОТСЛЕЖИВАНИЯ

### Trial Conversion Metrics:
- Trial activation rate (цель: 80%+)
- Trial completion rate (цель: 15-20%)
- Upgrade rate from trial (цель: 25-30%)

### Subscription Metrics:
- Monthly recurring revenue (MRR)
- Customer acquisition cost (CAC)
- Customer lifetime value (LTV)
- Churn rate (цель: < 5%)

### Feature Usage Metrics:
- Daily active users (DAU)
- Feature adoption rate
- Session length
- Crash-free users

---

## 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **GDPR Compliance:** Добавить consent management
2. **Privacy Settings:** Пользователи должны иметь возможность отключить аналитику
3. **Data Retention:** Настроить сроки хранения данных в Firebase
4. **Custom Definitions:** Создать custom funnels в Firebase Console

---

## 📊 DASHBOARD НАСТРОЙКИ

### Рекомендуемые отчеты:
1. **Subscription Funnel** - от trial до paid
2. **Revenue Dashboard** - MRR, ARPU, LTV
3. **User Engagement** - DAU, session length, feature usage
4. **Cohort Analysis** - retention по когортам

---

## 🔗 ИНТЕГРАЦИЯ С СЕРВЕРОМ

### Отправка аналитики на сервер:
```swift
// В RemoteAnalyticsService добавить Firebase events
func trackSubscriptionEvent(_ event: String, metadata: [String: Any]) {
    // Send to server
    apiService.request(endpoint: "/api/analytics/subscription", method: .post, body: [
        "event": event,
        "metadata": metadata,
        "user_id": userId,
        "timestamp": Date()
    ])

    // Also track in Firebase
    Analytics.logEvent(event, parameters: metadata)
}
```

---

## ✅ ПОСЛЕ НАСТРОЙКИ

1. **Тестировать** все события в Debug режиме
2. **Проверить** данные в Firebase Console
3. **Настроить** dashboards и alerts
4. **Подключить** server-side аналитику
5. **Документировать** все custom events