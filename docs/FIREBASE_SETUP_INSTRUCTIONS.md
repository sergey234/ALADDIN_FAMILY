# 🔥 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ FIREBASE

**Дата:** 04.12.2025  
**Статус:** ✅ Готово к настройке

---

## 📋 ЧТО ДОБАВЛЕНО

### **1. Firebase Crashlytics**
- ✅ Отслеживание сбоев приложения
- ✅ Логирование ошибок сети и API
- ✅ Пользовательские ключи для контекста

### **2. Firebase Analytics**
- ✅ Отслеживание экранов
- ✅ Отслеживание событий
- ✅ Пользовательские свойства

---

## 🚀 ШАГИ НАСТРОЙКИ

### **ШАГ 1: Установка зависимостей**

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
pod install
```

**Что установится:**
- `Firebase/Core` - базовая функциональность
- `Firebase/Analytics` - аналитика
- `Firebase/Crashlytics` - отчеты о сбоях

---

### **ШАГ 2: Создание проекта в Firebase Console**

1. Откройте [Firebase Console](https://console.firebase.google.com/)
2. Нажмите "Add project" (Добавить проект)
3. Введите название: **ALADDIN Family Security**
4. Включите Google Analytics (рекомендуется)
5. Выберите или создайте Analytics аккаунт
6. Нажмите "Create project"

---

### **ШАГ 3: Добавление iOS приложения**

1. В Firebase Console нажмите "Add app" → iOS
2. Введите:
   - **Bundle ID:** `com.aladdin.family` (проверьте в Xcode)
   - **App nickname:** ALADDIN iOS
   - **App Store ID:** (опционально)
3. Нажмите "Register app"

---

### **ШАГ 4: Загрузка GoogleService-Info.plist**

1. Скачайте `GoogleService-Info.plist` из Firebase Console
2. Откройте Xcode проект
3. Перетащите `GoogleService-Info.plist` в корень проекта `ALADDIN`
4. **ВАЖНО:** Убедитесь, что файл добавлен в Target Membership для `ALADDIN`
5. **ВАЖНО:** Не добавляйте в `.gitignore` (но можно добавить в `.gitignore` для безопасности)

---

### **ШАГ 5: Проверка настройки**

1. Откройте `AppDelegate.swift`
2. Убедитесь, что есть:
   ```swift
   import FirebaseCore
   import FirebaseCrashlytics
   
   func application(_ application: UIApplication,
                    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
       FirebaseApp.configure()
       return true
   }
   ```

3. Откройте `ALADDINApp.swift`
4. Убедитесь, что есть:
   ```swift
   import FirebaseCore
   
   @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
   ```

---

### **ШАГ 6: Сборка и тестирование**

1. Откройте Xcode
2. Выберите схему `ALADDIN`
3. Нажмите `Cmd + B` для сборки
4. Если есть ошибки - проверьте:
   - Установлены ли зависимости (`pod install`)
   - Добавлен ли `GoogleService-Info.plist`
   - Правильный ли Bundle ID

---

## ✅ ПРОВЕРКА РАБОТЫ

### **1. Проверка Analytics**

Добавьте в код (например, в `MainScreen`):

```swift
.onAppear {
    AnalyticsManager.shared.trackScreen("Main Screen")
    AnalyticsManager.shared.trackEvent("app_opened")
}
```

**Как проверить:**
1. Запустите приложение
2. Подождите 24 часа (или используйте DebugView в Firebase Console)
3. Откройте Firebase Console → Analytics → Events

---

### **2. Проверка Crashlytics**

Добавьте тестовый сбой (только для тестирования):

```swift
// ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ!
#if DEBUG
Button("Test Crash") {
    fatalError("Test crash for Crashlytics")
}
#endif
```

**Как проверить:**
1. Запустите приложение
2. Нажмите кнопку "Test Crash"
3. Подождите 5-10 минут
4. Откройте Firebase Console → Crashlytics
5. Должен появиться отчет о сбое

---

## 📊 ИСПОЛЬЗОВАНИЕ

### **Analytics**

```swift
// Отслеживание экрана
AnalyticsManager.shared.trackScreen("Settings Screen")

// Отслеживание события
AnalyticsManager.shared.trackEvent("button_tapped", parameters: [
    "button_name": "subscribe",
    "screen": "tariffs"
])

// Установка User ID
AnalyticsManager.shared.setUserID("user123")

// Установка свойства пользователя
AnalyticsManager.shared.setUserProperty("premium", forName: "subscription_type")
```

### **Crashlytics**

```swift
// Логирование ошибки
do {
    try someOperation()
} catch {
    CrashReportingManager.shared.recordError(error)
}

// Логирование ошибки сети
CrashReportingManager.shared.recordNetworkError(
    error,
    endpoint: "/api/users",
    method: "GET"
)

// Логирование API ошибки
CrashReportingManager.shared.recordAPIError(
    error,
    endpoint: "/api/subscription",
    statusCode: 500
)

// Логирование сообщения
CrashReportingManager.shared.log("User completed onboarding")

// Установка пользовательского ключа
CrashReportingManager.shared.setCustomValue("premium", forKey: "subscription_type")
```

---

## 🔒 БЕЗОПАСНОСТЬ

### **Рекомендации:**

1. **GoogleService-Info.plist:**
   - ✅ Добавьте в `.gitignore` для безопасности
   - ✅ Используйте разные файлы для Debug/Release
   - ✅ Не коммитьте в публичный репозиторий

2. **Данные пользователей:**
   - ✅ Не логируйте пароли, токены, персональные данные
   - ✅ Используйте хеширование для чувствительных данных
   - ✅ Соблюдайте GDPR/CCPA требования

3. **Crashlytics:**
   - ✅ Не логируйте чувствительные данные в ключах
   - ✅ Используйте обобщенные сообщения об ошибках

---

## 📝 ФАЙЛЫ ИЗМЕНЕНЫ

1. ✅ `Podfile` - добавлены Firebase зависимости
2. ✅ `AppDelegate.swift` - инициализация Firebase
3. ✅ `ALADDINApp.swift` - добавлен AppDelegate адаптер
4. ✅ `AnalyticsManager.swift` - интеграция Firebase Analytics
5. ✅ `CrashReportingManager.swift` - новый файл для Crashlytics
6. ✅ `NetworkManager.swift` - интеграция Crashlytics для ошибок сети

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. ✅ Установить зависимости: `pod install`
2. ✅ Создать проект в Firebase Console
3. ✅ Добавить `GoogleService-Info.plist`
4. ✅ Собрать проект в Xcode
5. ✅ Протестировать Analytics и Crashlytics

---

**Документ создан:** 04.12.2025  
**Статус:** ✅ Готово к использованию

