# ✅ TODO ЛИСТ: ЛОКАЛЬНАЯ ОБРАБОТКА AI ASSISTANT

**Дата создания:** 2026-03-12  
**Версия:** BUILD 115+  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ

---

## 📋 ЗАДАЧИ

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ

#### ✅ 1. Добавить локализованные строки для ответов AI Assistant

**1.1. Русский язык**
- [ ] Добавить ключ `ai_assistant_local_protection_status_active` в `LocalizationManager.swift` (~строка 2080)
- [ ] Добавить ключ `ai_assistant_local_protection_status_inactive` в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_stats_week` в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_threats_recent` в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_family_info` в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_help_faq` в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_greeting` в `LocalizationManager.swift`

**Файл:** `Core/Localization/LocalizationManager.swift`  
**Строки:** ~2080 (русский раздел)

---

**1.2. Английский язык**
- [ ] Добавить ключ `ai_assistant_local_protection_status_active` (English) в `LocalizationManager.swift` (~строка 6568)
- [ ] Добавить ключ `ai_assistant_local_protection_status_inactive` (English) в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_stats_week` (English) в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_threats_recent` (English) в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_family_info` (English) в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_help_faq` (English) в `LocalizationManager.swift`
- [ ] Добавить ключ `ai_assistant_local_greeting` (English) в `LocalizationManager.swift`

**Файл:** `Core/Localization/LocalizationManager.swift`  
**Строки:** ~6568 (английский раздел)

---

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ

#### ✅ 2. Создать структуру `AILocalResponseHelper`

**2.1. Создать структуру**
- [ ] Создать структуру `AILocalResponseHelper` в `Screens/06_AIAssistantScreen.swift`
- [ ] Добавить свойства: `localizationManager: LocalizationManager`, `apiService: APIService`
- [ ] Добавить инициализатор

**Файл:** `Screens/06_AIAssistantScreen.swift`  
**Местоположение:** После `determineMessageContext`, перед `sendRegularMessage`

---

**2.2. Реализовать основной метод**
- [ ] Добавить метод `getLocalResponse(context:message:) -> String?`
- [ ] Реализовать switch по контексту (`protection_status`, `stats`, `threat_analysis`, `help`, `greeting`)
- [ ] Вернуть `nil` для неизвестных контекстов (fallback на сервер)

---

#### ✅ 3. Реализовать методы получения данных

**3.1. Статус защиты (`getProtectionStatusResponse`)**
- [ ] Получить статус компонентов через `ComponentStatusService.shared.getAllComponentStatuses()`
- [ ] Подсчитать количество активных компонентов
- [ ] Получить статистику семьи через `APIService.getFamilyStats()`
- [ ] Получить текущий тариф через `TariffManager.shared.currentTariff`
- [ ] Сформировать локализованный ответ с параметрами
- [ ] Обработать ошибки (fallback на сервер)

**Источники данных:**
- `ComponentStatusService.shared`
- `APIService.getFamilyStats()`
- `TariffManager.shared`

---

**3.2. Статистика (`getStatsResponse`)**
- [ ] Получить аналитику за неделю через `APIService.getAnalytics(period: "week")`
- [ ] Извлечь данные: количество угроз, разбивка по типам
- [ ] Сформировать локализованный ответ с параметрами
- [ ] Обработать ошибки (fallback на сервер)

**Источники данных:**
- `APIService.getAnalytics(period: "week")`
- `AnalyticsResponse`

---

**3.3. Анализ угроз (`getThreatAnalysisResponse`)**
- [ ] Получить последние угрозы через `APIService.getTopThreats()`
- [ ] Сгруппировать по типам
- [ ] Сформировать локализованный ответ
- [ ] Обработать ошибки (fallback на сервер)

**Источники данных:**
- `APIService.getTopThreats()`
- `AnalyticsResponse.topThreats`

---

**3.4. Информация о семье (`getFamilyInfoResponse`)**
- [ ] Получить статистику семьи через `APIService.getFamilyStats()`
- [ ] Извлечь: количество членов, устройств, тариф, статус
- [ ] Сформировать локализованный ответ
- [ ] Обработать ошибки (fallback на сервер)

**Источники данных:**
- `APIService.getFamilyStats()`
- `FamilyStatsResponse`

---

#### ✅ 4. Интегрировать локальную обработку в `sendRegularMessage`

**4.1. Модифицировать метод**
- [ ] Добавить проверку локального ответа перед отправкой на сервер
- [ ] Создать экземпляр `AILocalResponseHelper`
- [ ] Вызвать `getLocalResponse(context:message:)`
- [ ] Если локальный ответ есть - использовать его, иначе отправлять на сервер

**Файл:** `Screens/06_AIAssistantScreen.swift`  
**Метод:** `sendRegularMessage(_:context:)`

---

**4.2. Добавить логирование**
- [ ] Логировать выбор локального ответа: `logger.business("✅ AI Assistant: Using local response for context: \(context)")`
- [ ] Логировать отправку на сервер: `logger.network("🤖 AI Assistant: Making API call to AI service")`

---

### 🟢 СРЕДНИЙ ПРИОРИТЕТ

#### ✅ 5. Интеграция с FAQ из SupportScreen

**5.1. Создать `FAQHelper`**
- [ ] Создать структуру `FAQHelper` для работы с FAQ
- [ ] Использовать те же `FAQItem` из `SupportScreen`
- [ ] Реализовать метод `searchFAQ(question:) -> String?`

**Файлы:**
- `Screens/06_AIAssistantScreen.swift` (новый метод)
- Можно использовать данные из `Screens/13_SupportScreen.swift`

---

**5.2. Реализовать поиск по FAQ**
- [ ] Извлечь FAQ вопросы из `SupportScreen.initializeFAQItems()`
- [ ] Реализовать поиск по ключевым словам в вопросах FAQ
- [ ] Вернуть соответствующий локализованный ответ
- [ ] Обработать случаи, когда FAQ не найден (fallback на сервер)

---

**5.3. Реализовать `getHelpResponse(message:)`**
- [ ] Использовать `FAQHelper` для поиска ответа
- [ ] Если найден FAQ ответ - вернуть его
- [ ] Если не найден - вернуть `nil` (fallback на сервер)

---

### 🔵 НИЗКИЙ ПРИОРИТЕТ (ОПЦИОНАЛЬНО)

#### ✅ 6. Кэширование данных

- [ ] Добавить кэш для данных о защите (TTL: 30 секунд)
- [ ] Добавить кэш для статистики (TTL: 1 минута)
- [ ] Обновлять кэш при изменении данных

---

#### ✅ 7. Метрики и аналитика

- [ ] Логировать использование локальных ответов
- [ ] Отслеживать, какие контексты чаще всего обрабатываются локально
- [ ] Анализировать эффективность локальной обработки

---

## 🧪 ТЕСТИРОВАНИЕ

### Тест 1: Локализация
- [ ] Протестировать на русском языке
- [ ] Протестировать на английском языке
- [ ] Проверить форматирование с параметрами

### Тест 2: Локальные ответы
- [ ] Протестировать `protection_status` контекст
- [ ] Протестировать `stats` контекст
- [ ] Протестировать `threat_analysis` контекст
- [ ] Протестировать `help` контекст
- [ ] Протестировать `greeting` контекст

### Тест 3: Fallback на сервер
- [ ] Протестировать fallback при ошибке получения данных
- [ ] Протестировать fallback для неизвестных контекстов
- [ ] Протестировать fallback при отсутствии FAQ ответа

---

## 📊 ПРОГРЕСС

**Всего задач:** 12  
**Выполнено:** 0  
**В процессе:** 0  
**Осталось:** 12

**Процент выполнения:** 0%

---

## 📝 ЗАМЕТКИ

- Все методы должны быть асинхронными или использовать completion handlers
- Обработка ошибок обязательна - всегда fallback на сервер при ошибке
- Локализация должна работать на обоих языках
- FAQ интеграция опциональна, но очень полезна

---

**Статус:** 📝 **ГОТОВ К РЕАЛИЗАЦИИ**
