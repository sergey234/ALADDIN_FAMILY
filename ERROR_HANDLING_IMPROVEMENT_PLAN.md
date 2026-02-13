# 🔧 ПЛАН УЛУЧШЕНИЯ ОБРАБОТКИ ОШИБОК

**Дата:** 2025-01-22  
**Приоритет:** 🟢 Низкий (можно после релиза)

---

## 📋 СОДЕРЖАНИЕ

1. [Где показываются ошибки](#где-показываются-ошибки)
2. [Что конкретно улучшить](#что-конкретно-улучшить)
3. [Примеры до/после](#примеры-допосле)
4. [План действий](#план-действий)

---

## 🔍 ГДЕ ПОКАЗЫВАЮТСЯ ОШИБКИ?

### 1. ViewModels (показывают технические ошибки)

#### Место 1: NetworkProtectionViewModel

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 333

**Текущий код:**
```swift
toastManager.showError("Ошибка: \(error.localizedDescription)")
```

**Проблема:**
- Показывает техническое сообщение типа "NetworkError.notFound: Ресурс не найден"
- Пользователь не понимает, что делать

**Что нужно:**
- Понятное сообщение: "Не удалось подключиться к защите сети. Проверьте интернет-соединение."

---

#### Место 2: ParentalControlViewModel

**Файл:** `ViewModels/ParentalControlViewModel.swift`  
**Строка:** 184

**Текущий код:**
```swift
toastManager.showError("Ошибка: \(error.localizedDescription)")
```

**Проблема:**
- Показывает техническое сообщение
- Пользователь не понимает, что делать

**Что нужно:**
- Понятное сообщение: "Не удалось обновить настройки родительского контроля. Попробуйте позже."

---

#### Место 3: MainViewModel

**Файл:** `ViewModels/MainViewModel.swift`  
**Строка:** ~200 (в обработке ошибок API)

**Текущий код:**
```swift
errorMessage = error.localizedDescription
```

**Проблема:**
- Показывает техническое сообщение
- Пользователь не понимает, что делать

**Что нужно:**
- Понятное сообщение: "Не удалось загрузить данные. Проверьте интернет-соединение."

---

### 2. ALADDINApp (показывает технические ошибки)

**Файл:** `ALADDINApp.swift`  
**Строка:** 66, 734

**Текущий код:**
```swift
print("⚠️ Failed to load user profile: \(error.localizedDescription)")
print("❌ Ошибка логина: \(error.localizedDescription)")
```

**Проблема:**
- Это только в консоли (не видно пользователю)
- Но можно улучшить для случаев, когда ошибка показывается пользователю

**Что нужно:**
- Если ошибка показывается пользователю - использовать понятные сообщения

---

### 3. NetworkManager (показывает технические ошибки)

**Файл:** `Core/Network/NetworkManager.swift`  
**Строка:** ~600-700 (в обработке ошибок)

**Текущий код:**
```swift
print("❌ NetworkManager.performRequest: HTTP ошибка 404")
print("   - Сообщение от сервера: Not Found")
```

**Проблема:**
- Это только в консоли (не видно пользователю)
- Но можно улучшить для случаев, когда ошибка показывается пользователю

**Что нужно:**
- Если ошибка показывается пользователю - использовать понятные сообщения

---

### 4. ErrorMessageManager (уже есть, но можно улучшить)

**Файл:** `Core/Network/ErrorMessageManager.swift`  
**Строка:** 146-352

**Текущий код:**
```swift
case .apiError(let message, let code):
    return (
        "Ошибка API",
        "\(message)\(code != nil ? " (код: \(code!))" : "")",
        .error,
        .retry
    )
```

**Проблема:**
- Показывает "Ошибка API" и технический код
- Можно сделать более понятным для конкретных случаев

**Что нужно:**
- Улучшить сообщения для конкретных кодов ошибок (404, 500, и т.д.)

---

## 🎯 ЧТО КОНКРЕТНО УЛУЧШИТЬ?

### Улучшение 1: ViewModels - понятные сообщения

**Где:** Все ViewModels, которые показывают ошибки

**Что сделать:**
- Вместо `error.localizedDescription` использовать понятные сообщения
- Добавить проверку типа ошибки и показывать соответствующее сообщение

**Примеры:**

#### NetworkProtectionViewModel:
```swift
// БЫЛО:
toastManager.showError("Ошибка: \(error.localizedDescription)")

// СТАЛО:
let userMessage = getErrorMessage(for: error, context: "network_protection")
toastManager.showError(userMessage)

private func getErrorMessage(for error: Error, context: String) -> String {
    if let networkError = error as? NetworkError {
        switch networkError {
        case .notFound:
            return "Не удалось подключиться к защите сети. Проверьте интернет-соединение."
        case .unauthorized:
            return "Требуется авторизация. Пожалуйста, войдите в аккаунт."
        case .timeout:
            return "Превышено время ожидания. Проверьте интернет-соединение и попробуйте снова."
        default:
            return "Не удалось выполнить операцию. Попробуйте позже."
        }
    }
    return "Произошла ошибка. Попробуйте позже."
}
```

---

#### ParentalControlViewModel:
```swift
// БЫЛО:
toastManager.showError("Ошибка: \(error.localizedDescription)")

// СТАЛО:
let userMessage = getErrorMessage(for: error, context: "parental_control")
toastManager.showError(userMessage)

private func getErrorMessage(for error: Error, context: String) -> String {
    if let networkError = error as? NetworkError {
        switch networkError {
        case .notFound:
            return "Не удалось обновить настройки родительского контроля. Проверьте интернет-соединение."
        case .unauthorized:
            return "Требуется авторизация. Пожалуйста, войдите в аккаунт."
        default:
            return "Не удалось сохранить настройки. Попробуйте позже."
        }
    }
    return "Произошла ошибка. Попробуйте позже."
}
```

---

### Улучшение 2: ErrorMessageManager - улучшить для конкретных случаев

**Где:** `Core/Network/ErrorMessageManager.swift`

**Что сделать:**
- Улучшить сообщения для конкретных HTTP кодов
- Добавить контекстные сообщения

**Пример:**

```swift
// БЫЛО:
case .apiError(let message, let code):
    return (
        "Ошибка API",
        "\(message)\(code != nil ? " (код: \(code!))" : "")",
        .error,
        .retry
    )

// СТАЛО:
case .apiError(let message, let code):
    let (title, userMessage) = getUserFriendlyMessage(for: code, originalMessage: message)
    return (
        title,
        userMessage,
        .error,
        .retry
    )

private func getUserFriendlyMessage(for code: Int?, originalMessage: String) -> (String, String) {
    guard let code = code else {
        return ("Ошибка", "Произошла ошибка при обращении к серверу. Попробуйте позже.")
    }
    
    switch code {
    case 404:
        return ("Ресурс не найден", "Запрашиваемые данные не найдены. Пожалуйста, войдите в аккаунт или обновите страницу.")
    case 401:
        return ("Требуется авторизация", "Ваша сессия истекла. Пожалуйста, войдите в аккаунт заново.")
    case 403:
        return ("Доступ запрещен", "У вас нет доступа к этому ресурсу. Обратитесь в поддержку.")
    case 500:
        return ("Ошибка сервера", "На сервере произошла ошибка. Мы уже работаем над исправлением. Попробуйте позже.")
    case 503:
        return ("Сервис недоступен", "Сервис временно недоступен. Мы уже работаем над восстановлением. Попробуйте позже.")
    default:
        return ("Ошибка", "Произошла ошибка при обращении к серверу. Попробуйте позже.")
    }
}
```

---

### Улучшение 3: MainViewModel - улучшить для 404

**Где:** `ViewModels/MainViewModel.swift`

**Что сделать:**
- Улучшить обработку 404 для профиля
- Показывать понятное сообщение вместо технического

**Пример:**

```swift
// БЫЛО:
errorMessage = error.localizedDescription

// СТАЛО:
if let networkError = error as? NetworkError,
   case .notFound = networkError {
    // 404 для профиля - это нормально для неавторизованного пользователя
    errorMessage = nil  // Не показываем ошибку, работаем в демо режиме
} else {
    errorMessage = "Не удалось загрузить данные. Проверьте интернет-соединение."
}
```

---

## 📊 ПРИМЕРЫ ДО/ПОСЛЕ

### Пример 1: Ошибка сети

**ДО:**
```
Пользователь видит:
"Ошибка: NetworkError.notFound: Ресурс не найден: Not Found"
```

**ПОСЛЕ:**
```
Пользователь видит:
"Не удалось подключиться к защите сети. Проверьте интернет-соединение."
```

---

### Пример 2: Ошибка 404 (профиль)

**ДО:**
```
Пользователь видит:
"⚠️ Failed to load user profile: Ресурс не найден: Not Found"
```

**ПОСЛЕ:**
```
Пользователь НЕ видит ошибку (работает в демо режиме)
ИЛИ видит:
"Профиль не найден. Пожалуйста, войдите в аккаунт."
```

---

### Пример 3: Ошибка авторизации

**ДО:**
```
Пользователь видит:
"Ошибка: NetworkError.unauthorized: Не авторизован"
```

**ПОСЛЕ:**
```
Пользователь видит:
"Ваша сессия истекла. Пожалуйста, войдите в аккаунт заново."
```

---

### Пример 4: Ошибка сервера (500)

**ДО:**
```
Пользователь видит:
"Ошибка API: Internal Server Error (код: 500)"
```

**ПОСЛЕ:**
```
Пользователь видит:
"На сервере произошла ошибка. Мы уже работаем над исправлением. Попробуйте позже."
```

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Улучшить ViewModels (1 час)

**Файлы:**
1. `ViewModels/NetworkProtectionViewModel.swift` - добавить функцию `getErrorMessage()`
2. `ViewModels/ParentalControlViewModel.swift` - добавить функцию `getErrorMessage()`
3. `ViewModels/MainViewModel.swift` - улучшить обработку 404
4. Другие ViewModels, которые показывают ошибки

**Что сделать:**
- Добавить функцию `getErrorMessage(for:context:)` в каждый ViewModel
- Заменить `error.localizedDescription` на понятные сообщения
- Использовать локализацию для сообщений

---

### Шаг 2: Улучшить ErrorMessageManager (30 минут)

**Файл:** `Core/Network/ErrorMessageManager.swift`

**Что сделать:**
- Улучшить функцию `getUserFriendlyMessage()` для конкретных HTTP кодов
- Добавить контекстные сообщения
- Использовать локализацию

---

### Шаг 3: Добавить локализацию (30 минут)

**Файл:** `Core/Localization/LocalizationManager.swift`

**Что сделать:**
- Добавить ключи для всех сообщений об ошибках
- Поддержка RU/EN

**Пример ключей:**
```swift
"error_network_connection": "Не удалось подключиться. Проверьте интернет-соединение."
"error_unauthorized": "Ваша сессия истекла. Пожалуйста, войдите в аккаунт заново."
"error_not_found": "Данные не найдены. Пожалуйста, войдите в аккаунт или обновите страницу."
"error_server_error": "На сервере произошла ошибка. Мы уже работаем над исправлением. Попробуйте позже."
```

---

## 🎯 КОНКРЕТНЫЕ МЕСТА ДЛЯ ИСПРАВЛЕНИЯ

### 1. ViewModels (показывают ошибки пользователю)

| Файл | Строка | Что исправить |
|------|--------|---------------|
| `ViewModels/NetworkProtectionViewModel.swift` | 333 | Заменить `error.localizedDescription` на понятное сообщение |
| `ViewModels/ParentalControlViewModel.swift` | 184 | Заменить `error.localizedDescription` на понятное сообщение |
| `ViewModels/MainViewModel.swift` | ~200 | Улучшить обработку 404 для профиля |
| `ViewModels/DrivingReportsViewModel.swift` | 77, 128, 165 | Улучшить сообщения об ошибках |
| `ViewModels/PrivacyReportsViewModel.swift` | 88 | Улучшить сообщения об ошибках |

---

### 2. ErrorMessageManager (централизованная обработка)

| Файл | Строка | Что исправить |
|------|--------|---------------|
| `Core/Network/ErrorMessageManager.swift` | 306-312 | Улучшить сообщения для `apiError` |
| `Core/Network/ErrorMessageManager.swift` | 351+ | Добавить обработку `invalidStatusCode` с понятными сообщениями |

---

### 3. ALADDINApp (если ошибки показываются пользователю)

| Файл | Строка | Что исправить |
|------|--------|---------------|
| `ALADDINApp.swift` | 66, 734 | Если ошибки показываются пользователю - использовать понятные сообщения |

---

## ✅ ЧТО ПОЛУЧИМ?

### До улучшения:
- Пользователь видит: "Ошибка: NetworkError.notFound: Ресурс не найден"
- Пользователь не понимает, что делать
- Много обращений в поддержку

### После улучшения:
- Пользователь видит: "Не удалось подключиться. Проверьте интернет-соединение."
- Пользователь понимает, что делать
- Меньше обращений в поддержку

---

## 📝 ИТОГО

**Где улучшать:**
- ✅ **ViewModels** - 5-7 файлов (показывают ошибки пользователю)
- ✅ **ErrorMessageManager** - 1 файл (централизованная обработка)
- ✅ **Локализация** - добавить ключи для сообщений

**Время:**
- ViewModels: ~1 час
- ErrorMessageManager: ~30 минут
- Локализация: ~30 минут
- **Итого:** ~2 часа

**Приоритет:** 🟢 Низкий (можно после релиза)

---

**Автор:** AI Assistant  
**Дата:** 2025-01-22  
**Версия:** 1.0
