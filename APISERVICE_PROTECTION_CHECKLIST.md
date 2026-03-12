# 📋 ПОЛНЫЙ СПИСОК МЕСТ ДЛЯ ЗАЩИТЫ В APIService

**Дата:** 2026-03-12  
**Файл:** `Core/Network/APIService.swift`  
**Статус:** 🔍 **ПОЛНЫЙ АУДИТ**

---

## 🎯 ДЛЯ ЧЕГО ЭТО ДЕЛАЕМ? (ПРОСТЫМ ЯЗЫКОМ)

### ❌ ПРОБЛЕМА:
Представь, что ты звонишь в службу поддержки, и оператор говорит: "Хорошо, я помогу" - и кладет трубку. А потом через секунду звонит снова и говорит: "Хорошо, я помогу" - и снова кладет трубку. Это странно, правда?

**То же самое происходит в коде:**
- Приложение отправляет запрос на сервер
- Сервер отвечает
- Код должен вызвать `continuation.resume()` **ОДИН РАЗ** - чтобы сказать "запрос завершен"
- Но иногда из-за ошибок в коде (особенно при retry логике) `continuation.resume()` вызывается **ДВА РАЗА**
- Это вызывает краш `EXC_BREAKPOINT` - приложение падает

### ✅ РЕШЕНИЕ:
Добавляем "защиту" - флаг `hasResumed`, который говорит: "Я уже вызвал `continuation.resume()`, больше не вызывай!"

**Это как поставить галочку "уже обработано" на документе, чтобы не обработать его дважды.**

---

## 📊 ПОЛНЫЙ СПИСОК МЕСТ (34 МЕСТА)

### ✅ ГРУППА 1: Family API (1 место)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 1 | `removeFamilyMember(_:)` | 169 | `continuation.resume(with: result)` | ⏳ PENDING |

---

### ✅ ГРУППА 2: IoT API (6 мест)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 2 | `getIoTStatus(homeId:)` | 1221 | `continuation.resume(with: result)` | ⏳ PENDING |
| 3 | `getIoTDevices(homeId:)` | 1231 | `continuation.resume(with: result)` | ⏳ PENDING |
| 4 | `getIoTThreats(homeId:)` | 1241 | `continuation.resume(with: result)` | ⏳ PENDING |
| 5 | `blockIoTDevice(deviceId:)` | 1251 | `continuation.resume(with: result)` | ⏳ PENDING |
| 6 | `startIoTScan(homeId:)` | 1282 | `continuation.resume(with: result)` | ⏳ PENDING |
| 7 | `fixIoTThreat(threatId:)` | 1293 | `continuation.resume(with: result)` | ⏳ PENDING |

---

### ✅ ГРУППА 3: Component Management API (6 мест)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 8 | `getComponentStatus(componentId:)` | 1395 | `continuation.resume(returning:)` / `continuation.resume(throwing:)` | ⏳ PENDING |
| 9 | `enableComponent(componentId:configuration:)` | 1416 | `continuation.resume(returning:)` / `continuation.resume(throwing:)` | ⏳ PENDING |
| 10 | `disableComponent(componentId:)` | 1444 | `continuation.resume(returning:)` / `continuation.resume(throwing:)` | ⏳ PENDING |
| 11 | `updateComponent(componentId:isEnabled:configuration:)` | 1475 | `continuation.resume()` / `continuation.resume(throwing:)` | ⏳ PENDING |
| 12 | `getComponentConfiguration(componentId:)` | 1503 | `continuation.resume(returning:)` / `continuation.resume(throwing:)` | ⏳ PENDING |
| 13 | `updateComponentConfiguration(componentId:configuration:)` | 1515 | `continuation.resume()` / `continuation.resume(throwing:)` | ⏳ PENDING |

---

### ✅ ГРУППА 4: Crash Detection API (6 мест)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 14 | `setupCrashDetection(latitude:longitude:radius:)` | 2059 | `continuation.resume(with: result)` | ⏳ PENDING |
| 15 | `sendCrashAlert(latitude:longitude:severity:)` | 2068 | `continuation.resume(with: result)` | ⏳ PENDING |
| 16 | `startCrashDetectionMonitoring()` | 2077 | `continuation.resume(with: result)` | ⏳ PENDING |
| 17 | `stopCrashDetectionMonitoring()` | 2086 | `continuation.resume(with: result)` | ⏳ PENDING |
| 18 | `sendCrashDetectionData(...)` | 2095 | `continuation.resume(with: result)` | ⏳ PENDING |
| 19 | `getCrashDetectionStatus()` | 2104 | `continuation.resume(with: result)` | ⏳ PENDING |

---

### ✅ ГРУППА 5: Geofencing API (1 место)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 20 | `setupGeofence(...)` | 2119 | `continuation.resume(with: result)` | ⏳ PENDING |

---

### ✅ ГРУППА 6: Другие API (нужно проверить)

| # | Метод | Строка | Тип вызова | Статус |
|---|-------|--------|------------|--------|
| 21-34 | (нужно найти остальные) | ? | ? | ⏳ PENDING |

---

## 🔍 ПРОВЕРКА: НЕ УПУСТИЛИ ЛИ ЧТО-ТО?

### ✅ ПРОВЕРКА #1: Все ли места с `withCheckedThrowingContinuation` найдены?

**Команда для проверки:**
```bash
grep -n "withCheckedThrowingContinuation" Core/Network/APIService.swift | wc -l
```

**Результат:** Нужно проверить

---

### ✅ ПРОВЕРКА #2: Все ли места с `continuation.resume()` найдены?

**Команда для проверки:**
```bash
grep -n "continuation.resume" Core/Network/APIService.swift | wc -l
```

**Результат:** Нужно проверить

---

### ✅ ПРОВЕРКА #3: Есть ли места, где `continuation.resume()` вызывается в разных ветках?

**Проверка:** Нужно проверить все места с `switch result` или `if/else`

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

### ШАГ 1: Найти ВСЕ места (проверка несколько раз)
- ✅ Найти все `withCheckedThrowingContinuation`
- ✅ Найти все `continuation.resume()`
- ✅ Проверить, что ничего не упустили

### ШАГ 2: Исправить по группам (аккуратно, по очереди)
1. Группа 1: Family API (1 место)
2. Группа 2: IoT API (6 мест)
3. Группа 3: Component Management API (6 мест)
4. Группа 4: Crash Detection API (6 мест)
5. Группа 5: Geofencing API (1 место)
6. Группа 6: Другие API (нужно найти)

### ШАГ 3: Проверка после каждого исправления
- ✅ Компиляция без ошибок
- ✅ Логирование добавлено
- ✅ Защита работает

---

## 🎯 ШАБЛОН ИСПРАВЛЕНИЯ

### Для методов с `continuation.resume(with: result)`:

```swift
return try await withCheckedThrowingContinuation { continuation in
    // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
    var hasResumed = false
    
    networkManager.get(endpoint: endpoint) { (result: Result<SomeResponse, Error>) in
        guard !hasResumed else {
            logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in \(#function)!")
            return
        }
        hasResumed = true
        continuation.resume(with: result)
    }
}
```

### Для методов с `switch result`:

```swift
return try await withCheckedThrowingContinuation { continuation in
    // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
    var hasResumed = false
    
    networkManager.get(endpoint: endpoint) { (result: Result<SomeResponse, Error>) in
        guard !hasResumed else {
            logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in \(#function)!")
            return
        }
        
        switch result {
        case .success(let response):
            hasResumed = true
            continuation.resume(returning: response)
        case .failure(let error):
            hasResumed = true
            continuation.resume(throwing: error)
        }
    }
}
```

---

## 📊 СТАТИСТИКА

- **Всего мест:** ~34 (нужно уточнить)
- **Исправлено:** 0
- **Осталось:** ~34

---

**Дата создания:** 2026-03-12  
**Статус:** 🔍 **В ПРОЦЕССЕ АУДИТА**
