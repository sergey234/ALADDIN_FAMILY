# 🛡️ АРХИТЕКТУРА: Anti-Tracker Agent БЕЗ VPN

**Дата:** 12 декабря 2025  
**Статус:** Анализ завершен, архитектура определена  
**Важно:** VPN убран из системы безопасности!

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО: VPN УБРАН

### Подтверждение:

1. **iOS приложение:**
   - `VPNManager.swift` - `NetworkExtension` закомментирован
   - Комментарий: `// ✅ ЗАКОММЕНТИРОВАНО: Apple не разрешает VPN от индивидуальных разработчиков`
   - VPN функциональность отсутствует

2. **Backend (Python):**
   - Нет VPN модуля
   - Нет механизмов перехвата трафика

**Вывод:** Anti-Tracker Agent должен работать БЕЗ VPN!

---

## 🎯 РЕКОМЕНДУЕМАЯ АРХИТЕКТУРА: Гибридный подход

### Принцип работы:

```
iOS App → NetworkManager → Проверка URL → Backend API (если нужно) → Решение о блокировке
```

### Компоненты:

1. **Backend (Anti-Tracker Agent):**
   - Управление списками трекеров
   - API для проверки запросов
   - Статистика блокировок
   - Синхронизация списков с iOS

2. **iOS приложение:**
   - Локальный кэш списков трекеров
   - Проверка URL перед запросом
   - Периодическая синхронизация с backend

---

## 🔧 МЕХАНИЗМ РАБОТЫ

### Шаг 1: Локальная проверка (iOS)

```swift
// В NetworkManager перед каждым запросом
func shouldBlockRequest(url: URL) -> Bool {
    // Быстрая проверка по локальному кэшу
    if localTrackerCache.contains(url.host ?? "") {
        logBlockedRequest(url, reason: "Local cache")
        return true
    }
    
    // Проверка паттернов URL
    if matchesTrackerPattern(url.absoluteString) {
        logBlockedRequest(url, reason: "URL pattern")
        return true
    }
    
    return false
}
```

### Шаг 2: Проверка через Backend (если нужно)

```swift
// Для сложных случаев или подозрительных URL
func checkWithBackend(url: URL) async -> BlockResult {
    let response = await apiService.post(
        "/api/anti-tracker/check",
        body: CheckRequest(url: url.absoluteString, headers: headers)
    )
    return response.blocked
}
```

### Шаг 3: Backend анализ (Python)

```python
def check_request(self, url: str, headers: dict) -> dict:
    """
    Проверка запроса на трекеры
    
    Returns:
        {"blocked": bool, "reason": str, "tracker_type": str}
    """
    domain = extract_domain(url)
    
    # Проверка по доменам
    if domain in self.blocked_domains:
        return {
            "blocked": True,
            "reason": "Blocked domain",
            "tracker_type": "domain"
        }
    
    # Проверка по паттернам URL
    if self._matches_tracker_pattern(url):
        return {
            "blocked": True,
            "reason": "Tracker pattern",
            "tracker_type": "pattern"
        }
    
    return {"blocked": False}
```

---

## 📋 СПИСОК ИЗВЕСТНЫХ ТРЕКЕРОВ

### Аналитика:
- `google-analytics.com`, `analytics.google.com` - Google Analytics
- `mc.yandex.ru` - Yandex Metrica
- `omniture.com`, `adobe.com` - Adobe Analytics
- `mixpanel.com` - Mixpanel
- `hotjar.com` - Hotjar

### Рекламные сети:
- `googleadservices.com`, `doubleclick.net` - Google Ads
- `yandex.ru/ads`, `direct.yandex.ru` - Yandex Direct (популярен в России)
- `vk.com/ads`, `ads.vk.com` - VK Ads (популярен в России)
- `myTarget.ru` - myTarget (российская рекламная сеть)
- `begun.ru` - Бегун (российская рекламная сеть)

### Социальные трекеры (для России):
- `vk.com/rtrg`, `vk.com/js/api/openapi.js` - VK Pixel (очень популярен в России)
- `ok.ru/js/sdk` - Одноклассники Pixel (популярен в России)
- `linkedin.com/px` - LinkedIn Insight (менее популярен в России)

### Паттерны URL:
- `/analytics` - аналитика
- `/track` - трекинг
- `/pixel` - пиксели
- `/beacon` - маяки
- `/collect` - сбор данных
- `/gtm.js` - Google Tag Manager

---

## 🔄 ПРОЦЕСС БЛОКИРОВКИ

### Сценарий 1: Простая блокировка (локально)

```
1. iOS делает HTTP запрос к "google-analytics.com/collect"
   ↓
2. NetworkManager проверяет URL локально
   ↓
3. Домен найден в локальном кэше трекеров
   ↓
4. Запрос блокируется (не выполняется)
   ↓
5. Логирование: "Заблокирован: google-analytics.com (локальный кэш)"
```

### Сценарий 2: Сложная проверка (через backend)

```
1. iOS делает HTTP запрос к "example.com/api/tracking"
   ↓
2. NetworkManager проверяет URL локально
   ↓
3. Домен не найден в кэше, но URL содержит "/tracking"
   ↓
4. Запрос на backend: POST /api/anti-tracker/check
   ↓
5. Backend анализирует:
   - Домен: example.com (не в списке)
   - Паттерн: /tracking (подозрительно)
   - Заголовки: User-Agent, Referer
   ↓
6. Backend возвращает: {"blocked": true, "reason": "Tracking pattern"}
   ↓
7. NetworkManager блокирует запрос
   ↓
8. Логирование и статистика
```

---

## 📊 СТАТИСТИКА И МОНИТОРИНГ

### Что отслеживать на Backend:

- Количество заблокированных запросов (всего, по типам)
- Топ заблокированных доменов
- Топ пользователей по блокировкам
- Временная статистика (по часам, дням)
- Эффективность блокировки (процент успешных блокировок)

### Что отслеживать на iOS:

- Количество локальных блокировок
- Количество проверок через backend
- Размер локального кэша
- Время последней синхронизации

---

## 🔐 БЕЗОПАСНОСТЬ И ПРИВАТНОСТЬ

### Защита данных:

- Локальный кэш не содержит персональных данных
- Backend не хранит полные URL (только домены и паттерны)
- Статистика агрегированная (без привязки к конкретным пользователям)
- Логирование минимальное (только факт блокировки, не содержимое)

---

## ✅ ПРЕИМУЩЕСТВА ГИБРИДНОГО ПОДХОДА

1. **Быстрота:** Локальная проверка мгновенная
2. **Гибкость:** Backend для сложных случаев
3. **Централизация:** Легко обновлять списки на сервере
4. **Масштабируемость:** Не нагружает backend каждый запрос
5. **Работает без VPN:** Использует существующую инфраструктуру

---

## ❌ ЧТО НЕ ИСПОЛЬЗУЕМ

- ❌ VPN (убран из системы)
- ❌ Content Blocker (только для Safari, не для API запросов)
- ❌ URLProtocol interceptor (слишком сложно, может влиять на производительность)
- ❌ Системный firewall (требует root/дополнительных разрешений)

---

## 🚀 ПЛАН РЕАЛИЗАЦИИ

### Backend (Python):

1. Создать `AntiTrackerAgent` с списками трекеров
2. Метод `check_request(url, headers)` для проверки
3. Метод `get_tracker_lists()` для синхронизации с iOS
4. API endpoints для проверки и статистики

### iOS (Swift):

1. Локальный кэш списков трекеров (UserDefaults или CoreData)
2. Метод проверки URL в `NetworkManager`
3. Периодическая синхронизация с backend
4. UI для управления блокировкой

---

**Последнее обновление:** 12 декабря 2025
