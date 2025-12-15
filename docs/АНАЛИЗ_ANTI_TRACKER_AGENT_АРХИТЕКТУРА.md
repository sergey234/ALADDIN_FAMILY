# 🛡️ АНАЛИЗ АРХИТЕКТУРЫ: Anti-Tracker Agent

**Дата:** 12 декабря 2025  
**Статус:** Анализ перед реализацией  
**Важно:** VPN убран из системы безопасности!

---

## ⚠️ КРИТИЧЕСКИ ВАЖНО: VPN УБРАН ИЗ СИСТЕМЫ

### Текущее состояние VPN:

1. **iOS приложение:**
   - `VPNManager.swift` - закомментирован `NetworkExtension`
   - `VPNViewModel.swift` - только UI, нет реальной VPN функциональности
   - VPN API endpoints существуют, но не работают на уровне системы
   - **Вывод:** VPN не может использоваться для блокировки трекеров

2. **Backend (Python):**
   - Нет VPN модуля для фильтрации трафика
   - Нет механизмов перехвата сетевых запросов
   - **Вывод:** Backend не может блокировать трафик напрямую

---

## 🎯 КАК ДОЛЖЕН РАБОТАТЬ ANTI-TRACKER AGENT БЕЗ VPN

### Вариант 1: Гибридный подход (РЕКОМЕНДУЕТСЯ)

**Архитектура:**
```
iOS App → NetworkManager → Backend API → Anti-Tracker Agent → Решение о блокировке
```

**Механизм работы:**

1. **iOS приложение:**
   - При каждом HTTP запросе (через `NetworkManager`) проверяет URL
   - Отправляет запрос на backend: `POST /api/anti-tracker/check`
   - Получает решение: `{"blocked": true/false, "reason": "..."}`
   - Если заблокирован - не выполняет запрос, возвращает ошибку

2. **Backend (Anti-Tracker Agent):**
   - Получает URL и заголовки запроса
   - Проверяет домен по спискам трекеров
   - Анализирует паттерны URL (например, `/analytics`, `/track`, `/pixel`)
   - Возвращает решение о блокировке
   - Логирует заблокированные запросы

**Преимущества:**
- ✅ Работает без VPN
- ✅ Централизованное управление списками трекеров
- ✅ Легко обновлять списки на сервере
- ✅ Статистика и аналитика на backend

**Недостатки:**
- ⚠️ Требует проверки каждого запроса (небольшая задержка)
- ⚠️ Не блокирует запросы из других приложений (только ALADDIN app)

---

### Вариант 2: Content Blocker (iOS Safari)

**Архитектура:**
```
Safari → Content Blocker Extension → JSON правила → Блокировка
```

**Механизм работы:**

1. **iOS приложение:**
   - Создает `ContentBlocker` extension
   - Генерирует JSON правила из списков трекеров
   - Safari автоматически применяет правила

2. **Backend (Anti-Tracker Agent):**
   - Управляет списками трекеров
   - Генерирует JSON правила для Content Blocker
   - API для обновления правил

**Преимущества:**
- ✅ Нативная блокировка в Safari
- ✅ Работает автоматически
- ✅ Не требует проверки каждого запроса

**Недостатки:**
- ⚠️ Работает только в Safari, не в других приложениях
- ⚠️ Не работает для API запросов из самого ALADDIN app
- ⚠️ Требует Safari Extension (дополнительная разработка)

---

### Вариант 3: URLSession Interceptor (iOS)

**Архитектура:**
```
URLSession → Custom URLProtocol → Anti-Tracker Agent → Блокировка
```

**Механизм работы:**

1. **iOS приложение:**
   - Регистрирует кастомный `URLProtocol`
   - Перехватывает все HTTP запросы
   - Проверяет через локальный список или backend API
   - Блокирует запросы к трекерам

2. **Backend (Anti-Tracker Agent):**
   - Управляет списками трекеров
   - API для синхронизации списков с iOS
   - Статистика блокировок

**Преимущества:**
- ✅ Блокирует все запросы из приложения
- ✅ Работает автоматически
- ✅ Не требует VPN

**Недостатки:**
- ⚠️ Сложная реализация (кастомный URLProtocol)
- ⚠️ Может влиять на производительность
- ⚠️ Нужна синхронизация списков с backend

---

## 🏆 РЕКОМЕНДУЕМАЯ АРХИТЕКТУРА: Гибридный подход

### Компоненты:

1. **Backend (Anti-Tracker Agent):**
   - Список известных трекеров (домены, паттерны URL)
   - API для проверки запросов
   - Статистика блокировок
   - Управление белыми/черными списками

2. **iOS приложение:**
   - Локальный кэш списков трекеров (для быстрой проверки)
   - Проверка через `NetworkManager` перед запросом
   - Периодическая синхронизация с backend
   - UI для управления блокировкой

### Механизм работы:

```
1. iOS App делает HTTP запрос
   ↓
2. NetworkManager проверяет URL локально (быстрая проверка)
   ↓
3. Если подозрительный → запрос на backend: POST /api/anti-tracker/check
   ↓
4. Anti-Tracker Agent анализирует:
   - Домен (google-analytics.com, facebook.com, и т.д.)
   - Паттерны URL (/analytics, /track, /pixel, и т.д.)
   - Заголовки (User-Agent, Referer)
   ↓
5. Возвращает решение: {"blocked": true, "reason": "Google Analytics tracker"}
   ↓
6. NetworkManager блокирует запрос (не выполняет)
   ↓
7. Логирование и статистика
```

---

## 📋 СПИСОК ИЗВЕСТНЫХ ТРЕКЕРОВ

### Аналитика:
- Google Analytics (`google-analytics.com`, `analytics.google.com`)
- Yandex Metrica (`mc.yandex.ru`)
- Adobe Analytics (`omniture.com`, `adobe.com`)
- Mixpanel (`mixpanel.com`)

### Рекламные сети:
- Google Ads (`googleadservices.com`, `doubleclick.net`)
- Facebook Ads (`facebook.com/tr`, `fbcdn.net`)
- Yandex Direct (`yandex.ru/ads`)
- VK Ads (`vk.com/ads`)

### Социальные трекеры:
- Facebook Pixel (`facebook.com/tr`)
- Twitter Pixel (`twitter.com/i/adsct`)
- LinkedIn Insight (`linkedin.com/px`)
- VK Pixel (`vk.com/rtrg`)

### Другие трекеры:
- Hotjar (`hotjar.com`)
- Crazy Egg (`crazyegg.com`)
- Mouseflow (`mouseflow.com`)

---

## 🔧 РЕАЛИЗАЦИЯ БЕЗ VPN

### Backend (Python):

```python
class AntiTrackerAgent:
    def check_request(self, url: str, headers: dict) -> dict:
        """
        Проверка запроса на трекеры
        
        Returns:
            {"blocked": bool, "reason": str, "tracker_type": str}
        """
        domain = extract_domain(url)
        
        # Проверка по доменам
        if domain in self.blocked_domains:
            return {"blocked": True, "reason": "Blocked domain", "tracker_type": "domain"}
        
        # Проверка по паттернам URL
        if self._matches_tracker_pattern(url):
            return {"blocked": True, "reason": "Tracker pattern", "tracker_type": "pattern"}
        
        return {"blocked": False}
```

### iOS (Swift):

```swift
extension NetworkManager {
    func shouldBlockRequest(url: URL) -> Bool {
        // Быстрая локальная проверка
        if localTrackerList.contains(url.host ?? "") {
            return true
        }
        
        // Проверка через backend
        let result = checkWithBackend(url: url)
        return result.blocked
    }
}
```

---

## 📊 СТАТИСТИКА И МОНИТОРИНГ

### Что отслеживать:
- Количество заблокированных запросов
- Типы трекеров (аналитика, реклама, социальные)
- Домены-лидеры по блокировкам
- Время блокировок
- Пользователи с наибольшим количеством блокировок

---

## ✅ ИТОГОВАЯ РЕКОМЕНДАЦИЯ

**Использовать Гибридный подход:**
1. Backend управляет списками трекеров
2. iOS проверяет запросы через API
3. Локальный кэш для быстрой проверки
4. Статистика и аналитика на backend

**НЕ использовать:**
- ❌ VPN (убран из системы)
- ❌ Content Blocker (только для Safari, не для API запросов)
- ❌ URLProtocol interceptor (слишком сложно)

---

**Последнее обновление:** 12 декабря 2025
