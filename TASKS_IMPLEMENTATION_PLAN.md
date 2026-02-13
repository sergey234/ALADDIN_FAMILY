# 📋 ПЛАН РЕАЛИЗАЦИИ ОСТАВШИХСЯ ЗАДАЧ

**Дата:** 2026-02-12  
**Статус:** План реализации

---

## 🔍 АНАЛИЗ: ЧТО МЫ ДЕЛАЛИ РАНЬШЕ?

### **1. METRICS_ROUTER** ⚠️

**Что было сделано:**
- ✅ Создан файл `metrics_router.py` на сервере (согласно `METRICS_ENDPOINT_ADDED.md`)
- ✅ Добавлен импорт в `main.py`: `from security.api.routers.metrics_router import router as metrics_router`
- ✅ Добавлено подключение: `app.include_router(metrics_router)` (внутри блока `if system_router_available`)

**Проблема:**
- ❌ В логах все еще 404 для `/api/metrics/upload`
- ⚠️ Возможные причины:
  1. Роутер подключен условно (`if system_router_available`), и `system_router` недоступен
  2. Сервер не перезапущен после изменений
  3. Роутер подключен неправильно

**Вывод:** ✅ **МЫ ЭТО ДЕЛАЛИ**, но нужно **ПРОВЕРИТЬ И ИСПРАВИТЬ** на сервере

---

### **2. PARENTAL_CONTROL_STATS_RESPONSE** ❌

**Что было сделано:**
- ✅ Модель `ParentalControlStatsResponse` существует в `APIModels.swift`
- ❌ **НЕТ** `CodingKeys` для маппинга `snake_case` → `camelCase`

**Проблема:**
- Сервер возвращает: `{"content_blocked": {...}}` (snake_case)
- Модель ожидает: `contentBlocked` (camelCase)
- Результат: ошибка декодирования `keyNotFound(CodingKeys(stringValue: "contentBlocked", ...))`

**Вывод:** ❌ **МЫ ЭТО НЕ ДЕЛАЛИ** - нужно исправить модель

---

## 🎯 ЗАЧЕМ ЭТО НУЖНО? (ПРОСТЫМ ЯЗЫКОМ)

### **1. `/api/metrics/upload` - Зачем нужен?**

**Простыми словами:**
- 📊 **Метрики** - это данные о том, как работает приложение
- 📈 Например: сколько времени загружается экран, сколько памяти используется, сколько FPS
- 🚨 Если что-то работает медленно или падает - метрики это покажут
- 📱 Приложение собирает эти данные и отправляет на сервер
- 🔍 На сервере можно анализировать метрики и находить проблемы

**Что происходит сейчас:**
- ❌ Приложение пытается отправить метрики → получает 404
- ❌ Метрики накапливаются в очереди, но не отправляются
- ⚠️ Мы не видим, как работает приложение у пользователей

**Что будет после исправления:**
- ✅ Метрики отправляются на сервер
- ✅ Можно видеть производительность приложения
- ✅ Можно находить и исправлять проблемы быстрее

**Аналогия:** Как счетчик в машине - показывает скорость, расход топлива. Метрики показывают "скорость" работы приложения.

---

### **2. `ParentalControlStatsResponse` - Зачем нужен?**

**Простыми словами:**
- 👨‍👩‍👧‍👦 **Родительский контроль** - это функция для родителей
- 📊 **Статистика** показывает: сколько сайтов заблокировано, сколько времени ребенок провел в приложениях, где находится ребенок
- 📱 Родители видят эту статистику в приложении

**Что происходит сейчас:**
- ✅ Запрос к серверу работает (200 OK)
- ❌ Но данные не декодируются (ошибка формата)
- ❌ Статистика не отображается в приложении

**Что будет после исправления:**
- ✅ Статистика правильно декодируется
- ✅ Родители видят все данные в приложении
- ✅ Функция родительского контроля работает полностью

**Аналогия:** Как переводчик - сервер говорит на одном языке (snake_case), приложение понимает другой (camelCase). Нужно добавить "переводчик" (CodingKeys).

---

## 📋 ПЛАН РЕАЛИЗАЦИИ

### **ЗАДАЧА 1: ПРОВЕРИТЬ И ИСПРАВИТЬ METRICS_ROUTER** 🔴 ВЫСОКИЙ ПРИОРИТЕТ

**Статус:** ⚠️ Роутер создан, но не работает (404 в логах)

**Шаги:**

1. **Проверить на сервере:**
```bash
# Подключиться к серверу
ssh root@149.154.65.180

# Проверить наличие роутера
ls -la /opt/aladdin-backend/security/api/routers/metrics_router.py

# Проверить подключение в main.py
grep -n "metrics_router" /opt/aladdin-backend/main.py
```

2. **Если роутер не подключен или подключен неправильно:**
```python
# В main.py добавить/исправить:

# Импорт (после других импортов роутеров)
try:
    from security.api.routers.metrics_router import router as metrics_router
    metrics_router_available = True
except ImportError as e:
    print(f"⚠️ metrics_router недоступен: {e}")
    metrics_router_available = False
    metrics_router = None

# Подключение (после других роутеров, НЕ внутри if system_router_available!)
if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
```

3. **Перезапустить сервер:**
```bash
sudo systemctl restart aladdin-production-api
sleep 5
systemctl status aladdin-production-api
```

4. **Протестировать:**
```bash
curl -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test","appVersion":"1.0.0","platform":"ios","metrics":[]}'
```

**Ожидаемый результат:** HTTP 200 OK

**Время:** 10-15 минут

---

### **ЗАДАЧА 2: ИСПРАВИТЬ PARENTAL_CONTROL_STATS_RESPONSE** ⚠️ СРЕДНИЙ ПРИОРИТЕТ

**Статус:** ❌ Модель не поддерживает snake_case

**Шаги:**

1. **Открыть файл:** `Core/Models/APIModels.swift`

2. **Найти структуру `ParentalControlStatsResponse`** (строка ~760)

3. **Добавить `CodingKeys` для всех полей:**
```swift
// Статистика родительского контроля
struct ParentalControlStatsResponse: Codable {
    let contentBlocked: ContentBlockedStats
    let screenTime: ScreenTimeStats
    let location: ParentalControlLocationStats
    let monitoring: MonitoringStats
    
    // ✅ ДОБАВИТЬ: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case contentBlocked = "content_blocked"
        case screenTime = "screen_time"
        case location
        case monitoring
    }
}

struct ContentBlockedStats: Codable {
    let websitesBlocked: Int
    let appsBlocked: Int
    let searchQueriesBlocked: Int
    let activeFilters: Int
    
    // ✅ ДОБАВИТЬ: CodingKeys
    enum CodingKeys: String, CodingKey {
        case websitesBlocked = "websites_blocked"
        case appsBlocked = "apps_blocked"
        case searchQueriesBlocked = "search_queries_blocked"
        case activeFilters = "active_filters"
    }
}

struct ScreenTimeStats: Codable {
    let todayUsage: String
    let todayLimit: String
    let remaining: String
    let schedulesCount: Int
    
    // ✅ ДОБАВИТЬ: CodingKeys
    enum CodingKeys: String, CodingKey {
        case todayUsage = "today_usage"
        case todayLimit = "today_limit"
        case remaining
        case schedulesCount = "schedules_count"
    }
}

struct ParentalControlLocationStats: Codable {
    let currentLocation: String?
    let lastUpdate: String?
    let geofencesCount: Int
    let eventsToday: Int
    
    // ✅ ДОБАВИТЬ: CodingKeys
    enum CodingKeys: String, CodingKey {
        case currentLocation = "current_location"
        case lastUpdate = "last_update"
        case geofencesCount = "geofences_count"
        case eventsToday = "events_today"
    }
}

struct MonitoringStats: Codable {
    let sitesTracked: Int
    let appsTracked: Int
    let contactsTracked: Int
    let messagesMonitored: Bool
    let screenshotsEnabled: Bool
    
    // ✅ ДОБАВИТЬ: CodingKeys
    enum CodingKeys: String, CodingKey {
        case sitesTracked = "sites_tracked"
        case appsTracked = "apps_tracked"
        case contactsTracked = "contacts_tracked"
        case messagesMonitored = "messages_monitored"
        case screenshotsEnabled = "screenshots_enabled"
    }
}
```

4. **Проверить компиляцию:**
```bash
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator clean build
```

5. **Протестировать после запуска:**
- Открыть экран родительского контроля
- Проверить, что статистика отображается

**Ожидаемый результат:** Статистика декодируется и отображается

**Время:** 15-20 минут

---

## 📊 ПРИОРИТЕТЫ

### 🔴 **ВЫСОКИЙ ПРИОРИТЕТ:**
1. **Проверить и исправить metrics_router** - метрики не отправляются, мы не видим проблемы

### ⚠️ **СРЕДНИЙ ПРИОРИТЕТ:**
2. **Исправить ParentalControlStatsResponse** - статистика не отображается, но функция работает частично

---

## ✅ ИТОГОВЫЙ СТАТУС

**Что мы делали:**
- ✅ **metrics_router** - создавали и подключали, но нужно проверить на сервере
- ❌ **ParentalControlStatsResponse** - НЕ исправляли, нужно добавить CodingKeys

**Что нужно сделать:**
1. Проверить metrics_router на сервере (10-15 мин)
2. Исправить модель ParentalControlStatsResponse (15-20 мин)

**Общее время:** 25-35 минут

---

**Последнее обновление:** 2026-02-12  
**Статус:** План готов к реализации
