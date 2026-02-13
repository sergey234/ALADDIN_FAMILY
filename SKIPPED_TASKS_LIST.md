# ⏭️ СПИСОК ПРОПУЩЕННЫХ ЗАДАЧ (ВЕРНУТЬСЯ ПОЗЖЕ)

*Дата создания: 10 февраля 2026 г.*  
*Статус: Задачи пропущены для выполнения позже*

---

## 🚨 **АВАРИЙНЫЙ ЭТАП: AI ASSISTANT (Задачи 1-5)**

**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Статус:** 2/5 задач выполнено, 3 задачи пропущены

### ✅ **ВЫПОЛНЕННЫЕ ЗАДАЧИ:**

- [x] **2. `ai_ios_endpoints`** - ✅ **ВЫПОЛНЕНО (100%)**
  - ✅ В `AppConfig.swift` добавлены 8 endpoint'ов
  - ✅ В `APIService.swift` реализованы все 8 методов для AI:
    - `sendMessageToAI()` - использует `AppConfig.Endpoint.aiAssistantChat`
    - `getAIChatHistory()` - использует `AppConfig.Endpoint.aiAssistantHistory`
    - `sendAIFeedback()` - использует `AppConfig.Endpoint.aiAssistantFeedback`
    - `getAICapabilities()` - использует `AppConfig.Endpoint.aiAssistantCapabilities`
    - `analyzeThreat()` - использует `AppConfig.Endpoint.aiAssistantAnalyzeThreat`
    - `getAIRecommendations()` - использует `AppConfig.Endpoint.aiAssistantRecommendations`
    - `reportIncident()` - использует `AppConfig.Endpoint.aiAssistantReportIncident`
    - `getSecurityTips()` - использует `AppConfig.Endpoint.aiAssistantSecurityTips`
  - ✅ Все методы используют `AppConfig.Endpoint.*` вместо жестких строк

- [x] **5. `ai_real_integration`** - ✅ **ВЫПОЛНЕНО (через задачу 10)**
  - ✅ В `AIAssistantViewModel.swift` симуляция заменена на реальные API вызовы
  - ✅ Используется `apiService.sendMessageToAI()` вместо `DispatchQueue.main.asyncAfter`
  - ✅ Добавлен индикатор "AI печатает..." (isAITyping)
  - ✅ Добавлена обработка ошибок

### ❌ **ПРОПУЩЕННЫЕ ЗАДАЧИ:**

- [ ] **1. `ai_server_endpoints`** - Добавить 8 AI Assistant endpoint'ов на сервере
  - **Причина пропуска:** Требует SSH доступ к серверу (149.154.65.180)
  - **Файл:** `api_gateway_server_current.py`
  - **Endpoints:** `/api/ai/assistant/chat`, `/api/ai/assistant/history`, и т.д.
  - **Когда вернуться:** После настройки доступа к серверу

- [ ] **3. `ai_localization`** - Добавить все feedback ключи локализации
  - **Причина пропуска:** Не критично для работы, можно добавить позже
  - **Файлы:** `LocalizationManager.swift` (вместо Russian.json/English.json)
  - **Ключи:** `ai_assistant_feedback_title`, `ai_assistant_feedback_description`, и т.д.
  - **Когда вернуться:** После завершения критических задач

- [ ] **4. `ai_speech_fix`** - Добавить NSSpeechRecognitionUsageDescription в Info.plist
  - **Причина пропуска:** Не критично, приложение работает без этого
  - **Файл:** `Info.plist`
  - **Ключ:** `NSSpeechRecognitionUsageDescription`
  - **Когда вернуться:** Когда будет использоваться голосовой ввод

---

## 🔥 **ЭТАП 1: NOTIFICATIONS (Задачи 18-19)**

**Приоритет:** 🔥 ВЫСОКИЙ  
**Причина пропуска:** Требуют настройки сертификатов APNs и работы на сервере  
**Когда вернуться:** После получения доступа к Apple Developer Account и серверу

### Пропущенные задачи:

- [ ] **18. `notifications_apns_setup`** - Настроить APNs инфраструктуру (сертификаты)
  - Требует:
    - Доступ к Apple Developer Account
    - Создание App ID с Push Notifications capability
    - Генерация development и production сертификатов
    - Установка сертификатов на сервер (149.154.65.180)
    - Настройка provisioning profile с Push Notifications
  - Тестирование: Отправка тестового push через curl

- [ ] **19. `notifications_server_implementation`** - Реализовать 16 Notifications endpoint'ов на сервере
  - Требует: SSH доступ к серверу (149.154.65.180)
  - Файл: `api_gateway_server_current.py`
  - Endpoints:
    - `/api/notifications/list`
    - `/api/notifications/stats`
    - `/api/notifications/unread_count`
    - `/api/notifications/mark_read/{notification_id}`
    - `/api/notifications/delete/{notification_id}`
    - `/api/notifications/bulk_mark_read`
    - `/api/notifications/test`
    - + 9 дополнительных endpoint'ов

---

## 📋 **ИТОГО:**

- **Аварийный этап:** 2 выполнено, 3 пропущено (задачи 1, 3, 4)
- **Этап 1:** 1 выполнено, 2 пропущено (задачи 18, 19)
- **Всего пропущено:** 5 задач (1, 3, 4, 18, 19)
- **Всего выполнено из пропущенных:** 2 задачи (2, 5)

---

## ✅ **ЧТО ВЫПОЛНЯЕМ СЕЙЧАС:**

- **Задача 20:** `notifications_localization` - Добавить локализацию для типов уведомлений
  - Не требует сервера или сертификатов
  - Можно выполнить сразу в iOS коде

---

## 🔄 **ПЛАН ВОЗВРАТА К ПРОПУЩЕННЫМ ЗАДАЧАМ:**

1. **После настройки доступа к серверу:**
   - Выполнить задачу 1 (`ai_server_endpoints`) - добавить 8 endpoint'ов на сервер
   - Выполнить задачу 19 (`notifications_server_implementation`) - добавить 16 endpoint'ов на сервер

2. **После получения доступа к Apple Developer Account:**
   - Выполнить задачу 18 (`notifications_apns_setup`) - настроить APNs сертификаты

3. **После завершения критических задач (низкий приоритет):**
   - Выполнить задачу 3 (`ai_localization`) - добавить ключи локализации для AI Assistant
   - Выполнить задачу 4 (`ai_speech_fix`) - добавить NSSpeechRecognitionUsageDescription в Info.plist

---

*Последнее обновление: 10 февраля 2026 г.*  
*Следующая проверка: После выполнения задачи 20*
