# 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: Бесконечный цикл обновления JWT токена

**Дата:** 2026-02-13  
**Проблема:** После регистрации нового пользователя появляется огромное количество одинаковых логов о попытке обновления токена  
**Статус:** 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА - бесконечный цикл

---

## 🔍 АНАЛИЗ ПРОБЛЕМЫ

### Цепочка вызовов (БЕСКОНЕЧНЫЙ ЦИКЛ):

1. **NetworkManager.post()** (строка 244)
   ```swift
   Task {
       _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
       // ...
   }
   ```

2. **JWTTokenManager.refreshTokenIfNeeded()** (строка 121)
   ```swift
   return await refreshAccessToken(refreshToken: refreshToken)
   ```

3. **JWTTokenManager.refreshAccessToken()** (строка 219)
   ```swift
   networkManager.post(endpoint: "/auth/refresh", body: request) { ... }
   ```

4. **Снова NetworkManager.post()** → возврат к шагу 1

### Проблема:

- `refreshTokenIfNeeded()` использует `refreshAccessToken()`
- `refreshAccessToken()` использует `networkManager.post()`
- `networkManager.post()` снова вызывает `refreshTokenIfNeeded()`
- **РЕЗУЛЬТАТ: БЕСКОНЕЧНЫЙ ЦИКЛ** 🔄

---

## ✅ РЕШЕНИЕ

### 1. Исправить `refreshTokenIfNeeded()` - использовать прямой запрос

**Файл:** `Core/Security/JWTTokenManager.swift`  
**Строка:** 121

**БЫЛО:**
```swift
func refreshTokenIfNeeded() async -> Bool {
    // ...
    return await refreshAccessToken(refreshToken: refreshToken) // ❌ Использует NetworkManager
}
```

**ДОЛЖНО БЫТЬ:**
```swift
func refreshTokenIfNeeded() async -> Bool {
    // ...
    return await directRefreshTokenRequest(refreshToken: refreshToken) // ✅ Прямой запрос
}
```

### 2. Добавить защиту от множественных одновременных запросов

**Проблема:** Если несколько запросов одновременно пытаются обновить токен, все они будут делать это параллельно.

**Решение:** Добавить флаг `isRefreshing` и очередь ожидающих запросов.

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

- [ ] Исправить `refreshTokenIfNeeded()` - использовать `directRefreshTokenRequest()`
- [ ] Добавить флаг `isRefreshing` для защиты от параллельных запросов
- [ ] Добавить очередь ожидающих запросов (опционально, для оптимизации)
- [ ] Протестировать исправление
- [ ] Убедиться, что логи больше не повторяются бесконечно

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:
- ✅ Токен обновляется один раз при необходимости
- ✅ Нет бесконечных логов
- ✅ Нет перегрузки сервера
- ✅ Нет лишнего трафика

---

## ⚠️ ДОПОЛНИТЕЛЬНЫЕ ПРОБЛЕМЫ

### Проблема #2: Множественные одновременные запросы

Если несколько запросов одновременно обнаруживают, что токен истёк, все они попытаются обновить токен одновременно.

**Решение:** Добавить механизм блокировки:
```swift
private var isRefreshing = false
private var refreshTask: Task<Bool, Never>?

func refreshTokenIfNeeded() async -> Bool {
    // Если уже обновляется, ждём завершения
    if let task = refreshTask {
        return await task.value
    }
    
    // Создаём новую задачу
    refreshTask = Task {
        // ... логика обновления
    }
    
    let result = await refreshTask!.value
    refreshTask = nil
    return result
}
```
