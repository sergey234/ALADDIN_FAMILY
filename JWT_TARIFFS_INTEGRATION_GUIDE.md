# 🔗 JWT + ТАРИФЫ: ПОЛНЫЙ ГУАЙД ИНТЕГРАЦИИ

## 🎯 КАК СОЕДИНИТЬ ТАРИФЫ С JWT ТОКЕНАМИ

---

## 📋 АРХИТЕКТУРА ИНТЕГРАЦИИ

### **🔄 ПОТОК РАБОТЫ:**

```
1. ПОЛЬЗОВАТЕЛЬ ЗАПУСКАЕТ APP
   ↓
2. ПРОВЕРКА TRIAL СТАТУСА (14 дней)
   ↓
3. АВТОМАТИЧЕСКАЯ РЕГИСТРАЦИЯ УСТРОЙСТВА
   ↓
4. ПОЛУЧЕНИЕ JWT С SUBSCRIPTION INFO
   ↓
5. ДОСТУП К ФУНКЦИЯМ ПО ТАРИФУ
   ↓
6. FEATURE GATING НА КЛИЕНТЕ И СЕРВЕРЕ
```

---

## 🏗️ JWT СТРУКТУРА С ТАРИФАМИ

### **📝 ПОЛНЫЙ JWT PAYLOAD:**

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
    "level": "trial",  // "trial", "free", "personal", "family", "premium"
    "status": "active",
    "expires_at": "2024-01-15T23:59:59Z",  // Trial: +14 дней
    "trial_ends_at": "2024-01-15T23:59:59Z",
    "billing_cycle": "monthly",
    "auto_renew": false,  // Trial не авто-продляется
    "features": [
      // 80% функций для trial
      "antivirus_scan",
      "network_security",
      "phishing_block",
      "basic_monitoring",
      "ai_assistant_limited",  // Ограниченный AI
      "personal_protection",
      // ЗАБЛОКИРОВАНЫ В TRIAL:
      // "dark_web_monitoring",
      // "identity_theft_protection",
      // "full_ai_assistant"
    ],
    "limits": {
      "devices": 10,  // Trial: все устройства
      "scans_per_day": 50,
      "ai_messages_per_day": 10,  // Ограниченный AI
      "reports_per_month": 5
    },
    "permissions": {
      "can_use_basic_security": true,
      "can_use_ai_limited": true,
      "can_use_family_features": false,  // Заблокировано в trial
      "can_use_dark_web": false,
      "can_use_identity_protection": false
    },
    "trial_info": {
      "days_left": 12,  // Из 14
      "percentage_used": 14,  // 14%
      "premium_features_locked": [
        "dark_web_monitoring",
        "identity_theft_protection",
        "full_ai_assistant",
        "advanced_reports"
      ]
    }
  },
  "analytics": {
    "registered_at": "2024-01-01T00:00:00Z",
    "last_active": "2024-01-03T10:30:00Z",
    "total_scans": 25,
    "trial_engagement_score": 85  // 85% функций использовано
  }
}
```

---

## 🎛️ ЛОГИКА ПОДКЛЮЧЕНИЯ

### **1️⃣ TRIAL АКТИВАЦИЯ (14 дней 80% функций):**

```swift
class TrialManager {
    static let shared = TrialManager()

    func activateTrialIfNeeded() async {
        // Проверяем был ли trial уже активирован
        let hasUsedTrial = UserDefaults.standard.bool(forKey: "trial_used")

        if !hasUsedTrial {
            print("🎁 АКТИВАЦИЯ TRIAL: 14 дней, 80% функций")

            // Создаем trial subscription локально
            let trialEndDate = Calendar.current.date(byAdding: .day, value: 14, to: Date())!
            let trialSubscription = createTrialSubscription(endDate: trialEndDate)

            // Сохраняем trial статус
            UserDefaults.standard.set(trialEndDate, forKey: "trial_end_date")
            UserDefaults.standard.set(true, forKey: "trial_used")
            UserDefaults.standard.set(trialSubscription, forKey: "trial_subscription")

            // Регистрируем устройство с trial токеном
            await registerDeviceWithTrial()

            print("✅ TRIAL АКТИВИРОВАН: \(trialEndDate)")
        }
    }

    private func createTrialSubscription(endDate: Date) -> SubscriptionInfo {
        return SubscriptionInfo(
            level: .trial,
            expiresAt: endDate,
            features: trialFeatures,  // 80% функций
            limits: trialLimits,      // Ограниченные лимиты
            permissions: trialPermissions, // Ограниченные права
            trialInfo: TrialInfo(
                daysLeft: 14,
                premiumFeaturesLocked: premiumFeatures
            )
        )
    }
}
```

### **2️⃣ JWT ГЕНЕРАЦИЯ С TRIAL:**

```python
# server/api/auth.py
def create_trial_token(device_id: str) -> str:
    """Создать JWT токен для trial периода"""

    trial_features = [
        # 80% функций доступны
        "antivirus_scan", "network_security", "phishing_block",
        "basic_monitoring", "personal_protection", "ai_assistant_limited",
        "crash_detection", "emergency_call", "family_basic",
        # 20% заблокировано
        # "dark_web_monitoring", "identity_theft_protection", "full_ai_assistant"
    ]

    trial_limits = {
        "devices": 10,  # Полный доступ к устройствам
        "scans_per_day": 50,
        "ai_messages_per_day": 10,  # Ограниченный AI
        "reports_per_month": 5
    }

    payload = {
        "iss": "aladdin_mobile_app",
        "sub": device_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=365),  # Токен на год
        "subscription": {
            "level": "trial",
            "status": "active",
            "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "trial_ends_at": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "features": trial_features,
            "limits": trial_limits,
            "permissions": {
                "can_use_basic_security": True,
                "can_use_ai_limited": True,
                "can_use_family_features": False,  # Заблокировано
                "can_use_dark_web": False,
                "can_use_identity_protection": False
            },
            "trial_info": {
                "days_left": 14,
                "premium_features_locked": [
                    "dark_web_monitoring",
                    "identity_theft_protection",
                    "full_ai_assistant"
                ]
            }
        }
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
```

### **3️⃣ FEATURE GATING ПО JWT:**

```swift
class FeatureGate {
    static let shared = FeatureGate()

    func canAccessFeature(_ feature: AppFeature) -> Bool {
        guard let token = AuthManager.shared.currentToken else {
            return false
        }

        // Trial период - проверяем 80% доступ
        if token.subscription.level == .trial {
            return checkTrialAccess(feature, token)
        }

        // Обычные тарифы
        return checkSubscriptionAccess(feature, token)
    }

    private func checkTrialAccess(_ feature: AppFeature, _ token: JWTToken) -> Bool {
        // В trial доступны 80% функций
        let trialAllowedFeatures: Set<AppFeature> = [
            .antivirusScan, .networkSecurity, .phishingBlock,
            .basicMonitoring, .aiAssistantLimited, .personalProtection,
            .crashDetection, .emergencyCall, .familyBasic
        ]

        return trialAllowedFeatures.contains(feature)
    }

    private func checkSubscriptionAccess(_ feature: AppFeature, _ token: JWTToken) -> Bool {
        let level = token.subscription.level

        switch feature {
        case .aiAssistant:
            return [.personal, .family, .premium].contains(level)
        case .familyControl:
            return [.family, .premium].contains(level)
        case .darkWebMonitoring:
            return level == .premium
        case .identityTheftProtection:
            return level == .premium
        default:
            return true  // Базовые функции для всех
        }
    }
}
```

---

## 📊 ЧТО В КАЖДОМ ФАЙЛЕ

### **1️⃣ ALADDIN_SUBSCRIPTION_SYSTEM_ANALYSIS.md**
**Метод 6 шляп - комплексный анализ:**

**⚪ БЕЛАЯ ШЛЯПА: ФАКТЫ И ДАННЫЕ**
- Статистика подписок (конверсия 20-25%, ARPU $8-10)
- Технические метрики (JWT + subscription поле)
- Рыночные данные (security apps рынок $10B+)

**🔴 КРАСНАЯ ШЛЯПА: ЭМОЦИИ**
- Радость trial периода, разочарование после окончания
- Удовлетворение от платных функций
- Эмоциональный UX подход

**⚫ ЧЕРНАЯ ШЛЯПА: РИСКИ**
- JWT взлом, race conditions, кэширование
- Churn после trial (70-80%)
- App Store rejection, competition

**🟡 ЖЕЛТАЯ ШЛЯПА: ПРЕИМУЩЕСТВА**
- Passive income от подписок
- User segmentation, data-driven development
- Scalable бизнес-модель

**🟢 ЗЕЛЕНАЯ ШЛЯПА: КРЕАТИВ**
- Pay-per-feature, usage-based модели
- Геймификация, referral bonuses
- Apple Family Sharing интеграции

**🔵 СИНЯЯ ШЛЯПА: КОНТРОЛЬ**
- Структура реализации (4 этапа)
- JWT структура с subscription
- Upgrade flow стратегия

---

### **2️⃣ ALADDIN_SUBSCRIPTION_FEATURE_MAPPING.md**
**Детальная спецификация тарифов:**

**📊 ПОЛНАЯ МАТРИЦА ФУНКЦИЙ:**
- **Trial (14 дней):** 29 функций (80%)
- **Free:** 10 базовых функций
- **Personal:** 16 функций (+AI assistant)
- **Family:** 22 функции (+Parental control)
- **Premium:** 29 функций (все)

**💰 ЦЕНОВАЯ СТРАТЕГИЯ:**
- Trial: 0₽ (14 дней)
- Free: 0₽ (навсегда)
- Personal: 100₽/месяц
- Family: 290₽/месяц ⭐ (рекомендуемый)
- Premium: 490₽/месяц

**🔢 ОГРАНИЧЕНИЯ И ЛИМИТЫ:**
- Устройства: 1→2→6→10
- Сканирования: 10→50→100→∞ в день
- AI сообщения: 0→10→25→50 в день
- Отчеты: 3→10→25→∞ в месяц

**📱 UX/UI СТРАТЕГИИ:**
- Progressive disclosure (показывать все, блокировать замками)
- Contextual upgrade prompts
- Value communication для каждого тарифа

---

### **3️⃣ JWT_SUBSCRIPTION_ARCHITECTURE.md**
**Техническая архитектура:**

**🔐 ПОЛНАЯ СТРУКТУРА JWT:**
```json
{
  "subscription": {
    "level": "trial",
    "features": ["ai_assistant_limited"],
    "limits": {"devices": 10, "scans_per_day": 50},
    "permissions": {"can_use_ai_limited": true},
    "trial_info": {"days_left": 12}
  }
}
```

**🏗️ PYTHON & SWIFT МОДЕЛИ:**
- Pydantic models для server-side
- Swift structs для client-side
- SubscriptionInfo, SubscriptionLimits, Permissions

**🚪 FEATURE GATING ЛОГИКА:**
- Server-side validation
- Client-side UI blocking
- Progressive disclosure

**📊 USAGE TRACKING:**
- Real-time monitoring лимитов
- Batch sending to server
- Token refresh при превышении

**🛡️ SECURITY & VALIDATION:**
- Server-side JWT validation
- Feature access checks
- Error handling и fallbacks

---

## 🔗 ПОЛНАЯ ИНТЕГРАЦИЯ: ТАРИФЫ ↔ JWT

### **🎯 ПОТОК ИНТЕГРАЦИИ:**

```
ПОЛЬЗОВАТЕЛЬ ЗАПУСКАЕТ APP
       ↓
TRIAL MANAGER: Активировать 14 дней?
       ↓
JWT SERVICE: Создать trial токен с 80% функций
       ↓
SUBSCRIPTION MANAGER: Сохранить trial статус
       ↓
FEATURE GATE: Разрешить 80% функций
       ↓
UI: Показать trial уведомление + заблокированные функции
       ↓
ПОЛЬЗОВАТЕЛЬ ИСПОЛЬЗУЕТ 80% ФУНКЦИЙ СВОБОДНО
```

### **📈 TRIAL → FREE ПЕРЕХОД:**

```swift
func handleTrialExpiration() {
    // Trial закончился
    if !TrialManager.shared.isTrialActive() {
        // Перевести на Free тариф
        let freeSubscription = SubscriptionInfo.free
        AuthManager.shared.updateSubscription(freeSubscription)

        // Показать upgrade предложения
        showUpgradePrompts()

        // Заблокировать 20% премиум функций
        FeatureGate.shared.lockPremiumFeatures()
    }
}
```

### **💰 FREE → PAID АПГРЕЙД:**

```swift
func upgradeToPaidTariff(_ level: SubscriptionLevel) async {
    // Обработать оплату
    let transaction = try await processPayment(level)

    // Обновить subscription на сервере
    let newSubscription = try await apiService.updateSubscription(transaction)

    // Обновить JWT токен
    await AuthManager.shared.refreshToken()

    // Разблокировать функции
    FeatureGate.shared.unlockFeatures(for: level)

    // Показать успех
    showUpgradeSuccess(level)
}
```

---

## 🚀 РЕЗУЛЬТАТ ИНТЕГРАЦИИ

### **✅ ЧТО МЫ ПОЛУЧИМ:**

1. **🎁 Trial период:** 14 дней, 80% функций - максимальная демонстрация ценности
2. **🔄 Seamless интеграция:** Тарифы ↔ JWT ↔ Features
3. **🛡️ Security:** Server-side validation + client-side gating
4. **📊 Analytics:** Полный трекинг использования по тарифам
5. **💰 Monetization:** Trial → Free → Paid конверсия

### **🎯 КЛЮЧЕВЫЕ ПРЕИМУЩЕСТВА:**

- **80% функций в trial** - достаточно для оценки ценности
- **JWT-first подход** - подписка встроена в токен
- **Feature gating** - гибкое управление доступом
- **Real-time updates** - мгновенное применение изменений
- **Fallback protection** - graceful degradation

---

**ЭТА ИНТЕГРАЦИЯ ДАСТ ALADDIN ОПТИМАЛЬНУЮ СИСТЕМУ МОНОТИЗАЦИИ С МАКСИМАЛЬНЫМ UX!** 🚀💰✨