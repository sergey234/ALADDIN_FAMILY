# 📊 Firebase Setup Guide - ALADDIN

## ✅ Настройка Firebase для iOS и Android

### 🔥 ШАГ 1: Создать Firebase проект

1. Перейдите: https://console.firebase.google.com
2. Нажмите **Add project** (Создать проект)
3. Название: **ALADDIN Family Protection**
4. Enable Google Analytics: **YES** ✅
5. Создайте проект

---

### 📱 ШАГ 2: Добавить iOS приложение

1. В Firebase Console нажмите **Add app → iOS**

2. **Параметры регистрации:**
   - iOS bundle ID: `family.aladdin.ios`
   - App nickname: `ALADDIN iOS`
   - App Store ID: (оставить пустым пока не опубликовано)

3. Нажмите **Register app**

4. **Скачать GoogleService-Info.plist:**
   - Нажмите **Download GoogleService-Info.plist**
   - Сохраните в: `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`
   - В Xcode: Drag & Drop файл в проект
   - ✅ **Copy items if needed**
   - ✅ **Add to targets: ALADDIN**

5. **Добавить Firebase SDK в Xcode:**
   
   В Xcode: **File → Add Package Dependencies**
   
   URL: `https://github.com/firebase/firebase-ios-sdk`
   
   Version: `10.18.0` (latest)
   
   Выберите пакеты:
   - ✅ FirebaseAnalytics
   - ✅ FirebaseCore
   - ✅ FirebaseCrashlytics (опционально)
   - ✅ FirebasePerformance (опционально)

6. **Инициализация в AppDelegate или App.swift:**

```swift
import Firebase

@main
struct ALADDINApp: App {
    
    init() {
        FirebaseApp.configure()
    }
    
    var body: some Scene {
        // ... существующий код
    }
}
```

7. Нажмите **Next** в Firebase Console
8. **Skip** оставшиеся шаги

---

### 🤖 ШАГ 3: Добавить Android приложение

1. В Firebase Console нажмите **Add app → Android**

2. **Параметры регистрации:**
   - Android package name: `family.aladdin.android`
   - App nickname: `ALADDIN Android`
   - Debug signing certificate SHA-1: (получить из Android Studio)

3. Нажмите **Register app**

4. **Скачать google-services.json:**
   - Нажмите **Download google-services.json**
   - Сохраните в: `/Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android/app/`
   - В Android Studio: Drag & Drop в папку `app/`

5. **Добавить Firebase SDK в build.gradle.kts:**

**Project-level build.gradle.kts:**
```kotlin
plugins {
    id("com.google.gms.google-services") version "4.4.0" apply false
}
```

**App-level build.gradle.kts:**
```kotlin
plugins {
    id("com.google.gms.google-services")
}

dependencies {
    // Firebase BOM (Bill of Materials)
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    
    // Firebase Analytics
    implementation("com.google.firebase:firebase-analytics-ktx")
    
    // Firebase Crashlytics (опционально)
    implementation("com.google.firebase:firebase-crashlytics-ktx")
    
    // Firebase Performance (опционально)
    implementation("com.google.firebase:firebase-perf-ktx")
}
```

6. **Sync Project with Gradle Files**

7. **Инициализация в MainActivity:**

```kotlin
import com.google.firebase.analytics.FirebaseAnalytics
import com.google.firebase.analytics.ktx.analytics
import com.google.firebase.ktx.Firebase

class MainActivity : ComponentActivity() {
    
    private lateinit var firebaseAnalytics: FirebaseAnalytics
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Инициализация Firebase
        firebaseAnalytics = Firebase.analytics
        
        // ... существующий код
    }
}
```

---

### 🎯 ШАГ 4: Настроить Analytics Events

**Автоматические события (уже работают):**
- ✅ `first_open` - первый запуск
- ✅ `session_start` - начало сессии
- ✅ `app_update` - обновление приложения
- ✅ `app_remove` - удаление приложения

**Кастомные события (уже настроены в AnalyticsManager):**
- ✅ `login` - вход
- ✅ `sign_up` - регистрация
- ✅ `purchase` - подписка
- ✅ `vpn_connect` - VPN подключение
- ✅ `add_family_member` - добавление члена семьи
- ✅ `threat_blocked` - блокировка угрозы
- ✅ `ai_assistant_message` - использование AI
- ✅ `referral_share` - реферальное приглашение
- ✅ И ещё 10+ событий!

---

### 📊 ШАГ 5: Просмотр аналитики

1. Перейдите в Firebase Console
2. **Analytics → Events**
3. Увидите все события в реальном времени!
4. **Analytics → User Properties** - свойства пользователей
5. **Analytics → Audiences** - сегменты пользователей
6. **Analytics → Conversions** - конверсии (подписки)

---

### 🧪 Тестирование

#### iOS:

```bash
# Запустить в симуляторе
Xcode → Run (Cmd + R)

# Проверить что Firebase инициализирован
# Смотрите в консоль Xcode:
# "✅ Firebase configured successfully"

# Events появятся в Firebase Console через 24 часа
# Для мгновенного тестирования используйте DebugView:
# Xcode → Product → Scheme → Edit Scheme → Arguments
# Добавьте: -FIRDebugEnabled
```

#### Android:

```bash
# Запустить в эмуляторе
Android Studio → Run (Shift + F10)

# Проверить что Firebase инициализирован
# Смотрите в Logcat:
# "✅ Firebase Analytics initialized"

# Для DebugView:
adb shell setprop debug.firebase.analytics.app family.aladdin.android
```

---

### 🎯 Готовность Firebase Analytics

| Фича | iOS | Android | Статус |
|------|-----|---------|--------|
| Analytics Manager | ✅ | ✅ | Готово |
| Screen Tracking | ✅ | ✅ | Готово |
| Event Tracking | ✅ | ✅ | Готово |
| User Properties | ✅ | ✅ | Готово |
| Conversion Tracking | ✅ | ✅ | Готово |
| Custom Events (15+) | ✅ | ✅ | Готово |

**ПОКРЫТИЕ: 100% ✅**

---

### 📈 Ключевые метрики для отслеживания

**Пользовательские:**
- DAU (Daily Active Users)
- MAU (Monthly Active Users)
- Retention (возврат пользователей)
- Session Duration (длительность сессии)

**Конверсионные:**
- Trial → Subscription (триал в подписку)
- Free → Paid (бесплатный в платный)
- Referral Conversion (реферальные конверсии)

**Функциональные:**
- VPN Usage (использование VPN)
- Threat Blocks (блокировки угроз)
- AI Assistant Usage (использование AI)
- Parental Control Actions (родительский контроль)

**Все метрики уже настроены! Готово к запуску!** 🚀



