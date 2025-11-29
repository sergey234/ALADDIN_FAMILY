# 🚀 RELEASE BUILD CHECKLIST

**Дата:** 15 ноября 2025  
**Статус:** 🔄 **В ПРОЦЕССЕ**

---

## ✅ ШАГ 1: НАСТРОЙКА RELEASE КОНФИГУРАЦИИ

### 1.1. Проверить AppConfig

**Файл:** `Core/Config/AppConfig.swift`

**Проверить:**
- [ ] `isDebugMode` правильно определяется через `#if DEBUG`
- [ ] `useMockAPI` всегда `false` в Release (уже настроено ✅)
- [ ] `apiBaseURL` указывает на production сервер
- [ ] Все debug логи отключены в Release

**Текущее состояние:**
```swift
#if DEBUG
static let isDebugMode = true
#else
static let isDebugMode = false
#endif

static var useMockAPI: Bool {
    get {
        #if DEBUG
        // ...
        #else
        return false // ✅ В Release всегда false
        #endif
    }
}
```

---

### 1.2. Отключить Debug UI

**Проверить файлы на наличие:**
- [ ] Debug кнопки
- [ ] Dev меню
- [ ] Тестовые данные
- [ ] Mock данные (кроме MockAPIService, который отключен в Release)

**Где искать:**
- `Screens/*.swift` - проверить на `#if DEBUG`
- `ViewModels/*.swift` - проверить на debug UI
- `Components/*.swift` - проверить на debug элементы

---

### 1.3. Отключить Debug Логи

**Проверить:**
- [ ] `print()` statements обернуты в `#if DEBUG`
- [ ] `NSLog()` отключены в Release
- [ ] Логирование сетевых запросов отключено в Release

**Пример:**
```swift
#if DEBUG
print("Debug info")
#endif
```

---

### 1.4. Проверить API URL

**Файл:** `Core/Config/AppConfig.swift`

**Проверить:**
- [ ] `currentEnvironment` в Release = `.production`
- [ ] Production URL правильный: `https://api.aladdin.family/api`

```swift
static let currentEnvironment: Environment = {
    #if DEBUG
    return .development
    #else
    return .production // ✅ Проверить
    #endif
}()
```

---

## ✅ ШАГ 2: CODE SIGNING

### 2.1. Проверить Bundle ID

**В Xcode:**
1. Project → Target → General
2. Bundle Identifier: `family.aladdin.ios`
3. ✅ Проверить, что совпадает с App Store Connect

---

### 2.2. Проверить Team

**В Xcode:**
1. Project → Target → Signing & Capabilities
2. Team: Выбрать вашу команду
3. ✅ Проверить, что сертификат валидный

---

### 2.3. Проверить Provisioning Profile

**В Xcode:**
1. Project → Target → Signing & Capabilities
2. Provisioning Profile: Automatic или конкретный профиль
3. ✅ Проверить, что профиль для App Store Distribution

---

### 2.4. Проверить Capabilities

**В Xcode:**
1. Project → Target → Signing & Capabilities
2. Проверить все Capabilities:
   - ✅ Push Notifications
   - ✅ VPN (Network Extension)
   - ✅ Keychain Sharing (если используется)
   - ✅ App Groups (если используется)

---

## ✅ ШАГ 3: УСТАНОВКА ВЕРСИИ

### 3.1. Version Number

**В Xcode:**
1. Project → Target → General
2. Version: `1.0.0`
3. Build: `1`

**Или в Info.plist:**
- `CFBundleShortVersionString`: `1.0.0`
- `CFBundleVersion`: `1`

---

## ✅ ШАГ 4: СОЗДАНИЕ ARCHIVE

### 4.1. Выбрать схему

**В Xcode:**
1. Product → Scheme → Edit Scheme...
2. Выбрать схему: `ALADDIN`
3. Run → Build Configuration: `Release`
4. Archive → Build Configuration: `Release`

---

### 4.2. Выбрать устройство

**В Xcode:**
1. Вверху выбрать: `Any iOS Device (arm64)`
2. НЕ выбирать симулятор!

---

### 4.3. Создать Archive

**В Xcode:**
1. Product → Archive
2. Дождаться завершения сборки
3. Откроется Organizer

---

### 4.4. Проверить Archive

**В Organizer:**
1. ✅ Проверить, что Archive создан
2. ✅ Проверить версию и build number
3. ✅ Проверить размер Archive

---

## ✅ ШАГ 5: UPLOAD В APP STORE CONNECT

### 5.1. Validate Archive

**В Organizer:**
1. Выбрать Archive
2. Нажать "Validate App"
3. Выбрать метод: "Automatically manage signing"
4. Дождаться валидации
5. ✅ Проверить, что нет ошибок

---

### 5.2. Distribute App

**В Organizer:**
1. Выбрать Archive
2. Нажать "Distribute App"
3. Выбрать: "App Store Connect"
4. Выбрать: "Upload"
5. Следовать инструкциям

---

### 5.3. Проверить Upload

**В App Store Connect:**
1. Зайти в App Store Connect
2. Выбрать приложение ALADDIN
3. Перейти в "TestFlight" или "App Store"
4. ✅ Проверить, что build появился

---

## 📋 ЧЕКЛИСТ ПЕРЕД ARCHIVE

- [ ] Release конфигурация настроена
- [ ] Debug UI отключен
- [ ] Debug логи отключены
- [ ] API URL указывает на production
- [ ] Mock API отключен (автоматически в Release)
- [ ] Bundle ID правильный
- [ ] Team выбран
- [ ] Provisioning Profile валидный
- [ ] Version: 1.0.0
- [ ] Build: 1
- [ ] Выбрано "Any iOS Device"
- [ ] Схема настроена на Release

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После успешного Upload:
1. ✅ Подготовить Review Notes
2. ✅ Заполнить App Privacy
3. ✅ Загрузить скриншоты
4. ✅ Указать публичные URL
5. ✅ Зарегистрировать IAP
6. ✅ Выбрать категорию

---

**Дата создания:** 15 ноября 2025  
**Статус:** 🔄 **ГОТОВ К ВЫПОЛНЕНИЮ**




