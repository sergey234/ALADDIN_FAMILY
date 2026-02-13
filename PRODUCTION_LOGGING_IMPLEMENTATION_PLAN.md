# 📝 ПЛАН ДОБАВЛЕНИЯ PRODUCTION ЛОГИРОВАНИЯ

**Дата:** 2025-01-22  
**Подход:** Централизованное логирование в NetworkManager

---

## 🎯 ГДЕ ДОБАВЛЯТЬ?

### ✅ НЕ ко всем эндпоинтам!

**Почему не ко всем:**
- ❌ Слишком много работы (221 эндпоинт)
- ❌ Дублирование кода
- ❌ Сложно поддерживать

### ✅ В ОДНОМ месте - NetworkManager!

**Почему NetworkManager:**
- ✅ Все запросы проходят через него
- ✅ Одно место для изменения
- ✅ Автоматически работает для всех эндпоинтов
- ✅ Легко поддерживать

---

## 📍 КОНКРЕТНОЕ МЕСТО

### Файл: `Core/Network/NetworkManager.swift`

**Что изменить:**
1. Добавить `import os.log` в начало файла
2. Создать logger для Production
3. Заменить критичные `print()` на `os_log()`

**Строки для изменения:**
- Строка 513-515: Начало запроса
- Строка 534: Получен ответ
- Строка 537-543: Ошибки сети
- Строка 550-552: Неверный ответ
- Строка 556: HTTP статус
- Строка 564-565: 401 ошибка
- Строка 617-618: HTTP ошибки

---

## 🔧 КОНКРЕТНЫЙ КОД

### Шаг 1: Добавить импорт и logger

**Место:** В начале файла `Core/Network/NetworkManager.swift`

**Добавить после строки 3:**
```swift
import Foundation
import Combine
import Security
import os.log  // ✅ ДОБАВИТЬ: Для Production логирования
```

**Добавить после строки 11 (после class NetworkManager):**
```swift
class NetworkManager: NSObject, ObservableObject {
    
    // ✅ ДОБАВИТЬ: Logger для Production логирования
    private static let networkLogger = OSLog(
        subsystem: "com.aladdin.network",
        category: "NetworkManager"
    )
    
    // MARK: - Properties
    // ... остальной код ...
```

---

### Шаг 2: Заменить критичные print() на os_log()

**Место:** В функции `performRequest` (строка 510+)

**Изменить:**

#### БЫЛО (строка 513-515):
```swift
print("🔵 NetworkManager.performRequest: Начало")
print("   - URL: \(request.url?.absoluteString ?? "unknown")")
print("   - Method: \(request.httpMethod ?? "unknown")")
```

#### СТАЛО:
```swift
// ✅ Production логирование (видно в Xcode Console на реальном устройстве)
os_log("🌐 API Request: %{public}@ %{public}@", 
       log: Self.networkLogger, 
       type: .info,
       request.httpMethod ?? "unknown",
       request.url?.absoluteString ?? "unknown")

#if DEBUG
print("🔵 NetworkManager.performRequest: Начало")
print("   - URL: \(request.url?.absoluteString ?? "unknown")")
print("   - Method: \(request.httpMethod ?? "unknown")")
#endif
```

---

#### БЫЛО (строка 537-543):
```swift
if let error = error {
    print("❌ NetworkManager.performRequest: Ошибка сети: \(error)")
    print("   - Описание: \(error.localizedDescription)")
    if let nsError = error as NSError? {
        print("   - Domain: \(nsError.domain)")
        print("   - Code: \(nsError.code)")
    }
    self?.lastError = error.localizedDescription
    completion(.failure(error))
    return
}
```

#### СТАЛО:
```swift
if let error = error {
    // ✅ Production логирование ошибок (критично для диагностики!)
    os_log("❌ Network Error: %{public}@ - %{public}@", 
           log: Self.networkLogger, 
           type: .error,
           request.url?.absoluteString ?? "unknown",
           error.localizedDescription)
    
    if let nsError = error as NSError? {
        os_log("   Domain: %{public}@, Code: %d", 
               log: Self.networkLogger, 
               type: .error,
               nsError.domain,
               nsError.code)
    }
    
    #if DEBUG
    print("❌ NetworkManager.performRequest: Ошибка сети: \(error)")
    print("   - Описание: \(error.localizedDescription)")
    if let nsError = error as NSError? {
        print("   - Domain: \(nsError.domain)")
        print("   - Code: \(nsError.code)")
    }
    #endif
    
    self?.lastError = error.localizedDescription
    completion(.failure(error))
    return
}
```

---

#### БЫЛО (строка 556):
```swift
print("   - HTTP Status: \(httpResponse.statusCode)")
```

#### СТАЛО:
```swift
// ✅ Production логирование HTTP статуса
if httpResponse.statusCode >= 400 {
    // Ошибки логируем всегда
    os_log("⚠️ HTTP Error: %d - %{public}@", 
           log: Self.networkLogger, 
           type: .error,
           httpResponse.statusCode,
           request.url?.absoluteString ?? "unknown")
} else {
    // Успешные запросы только в DEBUG
    #if DEBUG
    print("   - HTTP Status: \(httpResponse.statusCode)")
    #endif
}
```

---

#### БЫЛО (строка 617-618):
```swift
print("❌ NetworkManager.performRequest: HTTP ошибка \(httpResponse.statusCode)")
```

#### СТАЛО:
```swift
// ✅ Production логирование HTTP ошибок
os_log("❌ HTTP Error %d: %{public}@ - %{public}@", 
       log: Self.networkLogger, 
       type: .error,
       httpResponse.statusCode,
       request.url?.absoluteString ?? "unknown",
       errorMessage)

#if DEBUG
print("❌ NetworkManager.performRequest: HTTP ошибка \(httpResponse.statusCode)")
print("   - Сообщение от сервера: \(errorMessage)")
#endif
```

---

## 📊 ЧТО БУДЕТ ЛОГИРОВАТЬСЯ В PRODUCTION

### ✅ Будет логироваться (критично):

1. **Все запросы к API**
   - URL запроса
   - HTTP метод
   - Время выполнения

2. **Все ошибки**
   - Ошибки сети
   - HTTP ошибки (4xx, 5xx)
   - SSL ошибки
   - Таймауты

3. **Критические события**
   - 401 ошибки (токен истек)
   - SSL Pinning ошибки
   - Неверные ответы

### ⚠️ НЕ будет логироваться (только в DEBUG):

1. **Успешные ответы** (200 OK)
   - Тело ответа
   - Детальная информация

2. **Отладочная информация**
   - Детали запроса
   - Параметры

---

## 🎯 ПРЕИМУЩЕСТВА ЭТОГО ПОДХОДА

### ✅ Централизованно:
- Одно место для изменения
- Работает для всех 221 эндпоинта автоматически
- Легко поддерживать

### ✅ Эффективно:
- Минимум изменений (1 файл)
- Быстро реализовать (15-20 минут)
- Не влияет на производительность

### ✅ Полезно:
- Видно все запросы на реальном устройстве
- Видно все ошибки
- Можно диагностировать проблемы

---

## 📋 ПОЛНЫЙ СПИСОК ИЗМЕНЕНИЙ

### Файл: `Core/Network/NetworkManager.swift`

**Изменения:**

1. **Строка 4:** Добавить `import os.log`
2. **Строка 14:** Добавить `private static let networkLogger = OSLog(...)`
3. **Строка 513-515:** Заменить на `os_log()` + `#if DEBUG print()`
4. **Строка 534:** Заменить на `os_log()` для ошибок
5. **Строка 537-543:** Заменить на `os_log()` + `#if DEBUG print()`
6. **Строка 550-552:** Заменить на `os_log()` + `#if DEBUG print()`
7. **Строка 556:** Заменить на `os_log()` для ошибок
8. **Строка 564-565:** Заменить на `os_log()` + `#if DEBUG print()`
9. **Строка 617-618:** Заменить на `os_log()` + `#if DEBUG print()`

**Итого:** ~9 изменений в одном файле

---

## 🧪 КАК ПРОВЕРИТЬ

### На реальном устройстве:

1. **Подключить iPhone к Mac**
2. **Открыть Xcode → Window → Devices and Simulators**
3. **Выбрать устройство → Open Console**
4. **Запустить приложение**
5. **Смотреть логи:**
   - Фильтр: `subsystem:com.aladdin.network`
   - Или искать: "API Request", "Network Error", "HTTP Error"

**Что увидите:**
```
🌐 API Request: GET https://aladdin-ai.ru/api/user/profile
❌ Network Error: https://aladdin-ai.ru/api/user/profile - The Internet connection appears to be offline
⚠️ HTTP Error: 404 - https://aladdin-ai.ru/api/user/profile
```

---

## ✅ ИТОГО

### Что делать:

1. ✅ **Добавить `import os.log`** в `NetworkManager.swift`
2. ✅ **Создать logger** (`OSLog`)
3. ✅ **Заменить критичные `print()` на `os_log()`** (9 мест)
4. ✅ **Оставить `print()` в `#if DEBUG`** для детальной отладки

### Результат:

- ✅ Все запросы логируются в Production
- ✅ Все ошибки видны на реальном устройстве
- ✅ Можно диагностировать проблемы
- ✅ Работает для всех 221 эндпоинта автоматически

### Время:

- ⏱️ **15-20 минут** на реализацию
- ⏱️ **5 минут** на тестирование

---

**Автор:** iOS Development Specialist  
**Дата:** 2025-01-22  
**Версия:** 1.0
