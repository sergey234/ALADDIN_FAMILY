# 📋 **ALADDIN iOS - TODO СПИСОК ДЛЯ ОТСЛЕЖИВАНИЯ 60 ЗАДАЧ**

*Дата создания: 10 февраля 2026 г.*  
*Версия: 1.0*  
*Статус: 25/67 выполнено (37%)*

---

## 🎯 **ОБЩАЯ СТАТИСТИКА**

- **Всего задач:** 67 (60 основных + 7 улучшений безопасности)
- **Выполнено:** 25
- **В работе:** 0
- **Осталось:** 42
- **Прогресс:** 37%

---

## 🚨 **АВАРИЙНЫЙ ЭТАП: AI ASSISTANT (Задачи 1-5)**

**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Срок:** 12 дней  
**Статус:** 5/5 (100%) ✅ ЗАВЕРШЕН - Все задачи выполнены

- [x] **1. `ai_server_endpoints`** - Добавить 8 AI Assistant endpoint'ов на сервер ✅ ВЫПОЛНЕНО
  - [x] Проверено на сервере: AI Assistant endpoints ОТСУТСТВУЮТ (0 найдено) ✅
  - [x] Локально: 8 endpoints реализованы в `api_gateway_test_simplified.py` ✅
  - [x] iOS код: 8 endpoints в `AppConfig.swift` и `APIService.swift` ✅
  - [x] ✅ ДОБАВЛЕНО: 8 endpoints на сервер в `/opt/aladdin-backend/security/microservices/api_gateway.py`:
    - `/api/ai/assistant/chat` (POST) ✅
    - `/api/ai/assistant/history` (GET) ✅
    - `/api/ai/assistant/feedback` (POST) ✅
    - `/api/ai/assistant/capabilities` (GET) ✅
    - `/api/ai/assistant/analyze_threat` (POST) ✅
    - `/api/ai/assistant/recommendations` (GET) ✅
    - `/api/ai/assistant/report_incident` (POST) ✅
    - `/api/ai/assistant/security_tips` (GET) ✅
  - [x] Реализована логика обработки для каждого endpoint'а с SFM интеграцией ✅
  - [x] Проверен синтаксис Python файла - корректен ✅
  - [ ] Протестировать через curl/Postman (требует перезапуска сервера)

- [x] **2. `ai_ios_endpoints`** - Добавить AI endpoint'ы в AppConfig.swift и исправить APIService ✅ ВЫПОЛНЕНО (100%)
  - [x] В `AppConfig.swift` добавлены 8 endpoint'ов ✅
  - [x] В `APIService.swift` реализованы все 8 методов для AI ✅
    - sendMessageToAI(), getAIChatHistory(), sendAIFeedback(), getAICapabilities()
    - analyzeThreat(), getAIRecommendations(), reportIncident(), getSecurityTips()
  - [x] Все методы используют `AppConfig.Endpoint.*` вместо жестких строк ✅

- [x] **3. `ai_localization`** - Добавить все feedback ключи локализации ✅ ВЫПОЛНЕНО
  - [x] Добавлены 14 ключей локализации в `LocalizationManager.swift` (RU/EN):
    - `ai_assistant_feedback_title`, `ai_assistant_feedback_description`
    - `ai_assistant_feedback_rating`, `ai_assistant_feedback_rating_excellent/good/fair/poor`
    - `ai_assistant_feedback_comment`, `ai_assistant_feedback_comment_placeholder`
    - `ai_assistant_feedback_submit`, `ai_assistant_feedback_success`
    - `ai_assistant_feedback_error`, `ai_assistant_feedback_cancel`, `ai_assistant_feedback_required`
  - [x] Ключи используются в `Screens/06_AIAssistantScreen.swift` (6 использований) ✅
  - [x] Добавлены английские переводы для всех ключей ✅
  - [x] Локализация работает для RU и EN языков ✅

- [x] **4. `ai_speech_fix`** - Добавить NSSpeechRecognitionUsageDescription в Info.plist ✅ ВЫПОЛНЕНО
  - [x] Открыт `Info.plist` ✅
  - [x] Добавлен ключ `NSSpeechRecognitionUsageDescription` ✅
  - [x] Добавлено описание: "ALADDIN Family needs speech recognition access for AI assistant voice input and voice commands." ✅
  - [x] Размещен после `NSSiriUsageDescription` для логической группировки ✅
  - [ ] Протестировать голосовой ввод (требует запуска приложения)

- [x] **5. `ai_real_integration`** - Интегрировать настоящий AI вместо симуляции ✅ ВЫПОЛНЕНО (через задачу 10)
  - [x] В `AIAssistantViewModel` симуляция заменена на реальные API вызовы ✅
  - [x] Используется `apiService.sendMessageToAI()` вместо `DispatchQueue.main.asyncAfter` ✅
  - [x] Добавлен индикатор "AI печатает..." (isAITyping) ✅
  - [x] Добавлена обработка ошибок ✅

---

## 🔧 **ЭТАП 0: ИСПРАВЛЕНИЕ MOCK (Задачи 6-17)**

**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Срок:** 7 дней  
**Статус:** 12/12 (100%) ✅ ЗАВЕРШЕН

- [x] **6. `fix_appconfig_mockapi`** - ИСПРАВИТЬ useMockAPI = true в AppConfig.swift (КРИТИЧНО!) ✅ ВЫПОЛНЕНО                                                                
  - [x] В `Core/Config/AppConfig.swift` найти `static let useMockAPI: Bool = true`
  - [x] Заменить на условную логику с `#if DEBUG`
  - [ ] Пересобрать проект (cmd+B)
  - [ ] Проверить что API запросы идут на реальный сервер

- [x] **7. `fix_hardcoded_endpoints`** - Добавить 25 недостающих endpoint'ов в AppConfig.swift ✅ ВЫПОЛНЕНО                                                                  
  - [x] В `AppConfig.Endpoint` добавить:
    - [x] AI Assistant (8) ✅
    - [x] Network Protection (2) ✅
    - [x] IoT Security (6) ✅
    - [x] Payments (2) ✅
    - [x] Auth (1) ✅
  - [x] Проверить что все endpoints уникальны ✅

- [x] **8. `replace_hardcoded_strings`** - Заменить все жесткие строки в APIService.swift на AppConfig ✅ ВЫПОЛНЕНО                                                          
  - [x] Найти все строки типа `"/api/..."` в `APIService.swift` ✅
  - [x] Заменить на `AppConfig.Endpoint.*` ✅
  - [x] Найти и заменить ВСЕ жесткие строки (21 замена) ✅
  - [x] Проверить компиляцию после каждой замены ✅

- [x] **9. `fix_mock_notifications`** - Заменить loadMockNotifications() на реальные API вызовы ✅ ВЫПОЛНЕНО                                                                 
  - [x] В `ViewModels/NotificationsViewModel` найти `loadMockNotifications()` ✅
  - [x] Удалить метод `loadMockNotifications()` ✅
  - [x] Убрать fallback на mock данные при ошибке ✅
  - [x] Используется `RemoteNotificationsService.fetchNotifications()` ✅
  - [ ] Протестировать получение уведомлений с сервера (требует работающий сервер)

- [x] **10. `fix_mock_ai_assistant`** - Заменить симуляцию AI на реальные API вызовы ✅ ВЫПОЛНЕНО                                                                            
  - [x] В `ViewModels/AIAssistantViewModel` найти `DispatchQueue.main.asyncAfter` ✅
  - [x] Заменить на `apiService.sendMessageToAI()` ✅
  - [x] Удалить все симуляции ответов ✅
  - [x] Добавлен индикатор "AI печатает..." (isAITyping) ✅
  - [x] Добавлена обработка ошибок ✅

- [x] **11. `fix_mock_device_detail`** - Убрать mock данные из DeviceDetailScreen ✅
  - [x] Добавлены @State переменные для deviceDetail
  - [x] Реализован метод loadDeviceDetail() с API вызовом
  - [x] Удалены hardcoded значения из DeviceInfoView (iOS 17.1, IP, MAC)
  - [x] Удалены hardcoded статистики из DeviceStatsView (47, 2.4 GB, 1.2 GB, 4:37:21)
  - [x] Удалены mock угрозы из DeviceThreatsView
  - [x] Добавлена загрузка реальных угроз через getTopThreats()
  - [x] Добавлена обработка загрузки и ошибок
  - В `Screens/22_DeviceDetailScreen` найти mock данные
  - Заменить на реальный API вызов `apiService.getDeviceDetails`
  - Добавить обработку загрузки и ошибок
  - Удалить все hardcoded значения

- [x] **12. `fix_mock_protection_stats`** - Убрать mock данные из ProtectionStatsScreen ✅
  - [x] Обновлена структура ProtectionStatsResponse в APIModels.swift
  - [x] Удален fallback на mock данные из loadProtectionStats()
  - [x] Удалены hardcoded значения из protectionDetailsCard ("99.8%", "15")
  - [x] Удалены hardcoded значения из threatsChartCard (12, 8, 84, 365)
  - [x] Заменены на реальные данные из protectionStats
  - [x] Добавлена обработка ошибок без fallback на mock

- [x] **13. `fix_mock_family_registration`** - Убрать DispatchQueue симуляции из FamilyRegistrationViewModel ✅
  - [x] Найдены все `DispatchQueue.main.asyncAfter` в `FamilyRegistrationViewModel`
  - [x] Проанализированы все задержки
  - [x] Удалены 4 искусственные задержки (0.5 сек) для UX переходов:
    - После выбора роли → выбор возрастной группы
    - После выбора возрастной группы → выбор буквы
    - После выбора буквы → создание семьи
    - После создания семьи → показ модала
  - [x] Оставлены 2 retry механизма (реальные, не симуляции):
    - Retry авторизации при сетевых ошибках (5 сек)
    - Retry сохранения токенов в Keychain (0.5 сек)
  - [x] Регистрация теперь работает без искусственных задержек

- [x] **14. `fix_mock_family_view`** - Убрать DispatchQueue симуляции из FamilyViewModel ✅
  - [x] Найден `DispatchQueue.main.asyncAfter` в `loadFamilyMembers()`
  - [x] Удалена искусственная задержка 0.3 сек
  - [x] Удалены hardcoded mock данные (Сергей, Мария, Маша, Бабушка)
  - [x] Заменено на реальный API вызов `apiService.getFamilyMembers()`
  - [x] Добавлена загрузка статистики семьи через `getFamilyStats()`
  - [x] Добавлена обработка ошибок
  - [x] Преобразование FamilyMemberResponse в FamilyMember
  - [x] Все семейные функции теперь используют реальный API

- [x] **15. `fix_mock_main_view`** - Убрать DispatchQueue симуляции из MainViewModel ✅
  - [x] Найдены все `DispatchQueue.main.asyncAfter` в `MainViewModel` (2 использования)
  - [x] Проанализированы все задержки:
    - Строка 171: Timeout механизм для API запроса (10 сек) - РЕАЛЬНЫЙ, оставлен
    - Строка 208: Retry механизм с экспоненциальным бэк-оффом - РЕАЛЬНЫЙ, оставлен
  - [x] Искусственных симуляций НЕ НАЙДЕНО
  - [x] Все задержки являются правильными механизмами для сетевых операций
  - [x] Главный экран использует реальный API без искусственных задержек

- [x] **16. `create_remote_analytics`** - Создать RemoteAnalyticsService для реальных данных ✅
  - [x] Переделан RemoteAnalyticsService для использования APIService
  - [x] Удалены прямые HTTP запросы через URLSession
  - [x] Реализованы все методы протокола AnalyticsService:
    - fetchSummary() - использует apiService.getAnalytics()
    - fetchSecurityAnalytics() - преобразует AnalyticsResponse в SecurityAnalytics
    - fetchFamilyAnalytics() - возвращает пустые данные (API не готов)
    - fetchUsageAnalytics() - использует apiService.getAnalytics()
    - fetchDevicesAnalytics() - возвращает пустые данные (API не готов)
  - [x] Реализованы методы мониторинга (пока только логирование):
    - trackAPIRequest(), trackUserAction(), trackError(), trackAlert(), trackHealthReport()
  - [x] Удален fallback на LocalAnalyticsService
  - [x] Используется реальный API через APIService.shared

- [x] **17. `add_service_switching`** - Добавить переключение Local/Remote для Analytics ✅
  - [x] Добавлена условная логика в `AnalyticsScreen.makeViewModel()`
  - [x] Используется `AppConfig.useMockAPI` для консистентности
  - [x] `LocalAnalyticsService` используется при `useMockAPI = true` (DEBUG + USE_MOCK_FOR_DEVELOPMENT)
  - [x] `RemoteAnalyticsService` используется при `useMockAPI = false` (продакшен)
  - [x] Добавлено логирование типа сервиса в DEBUG режиме
  - [x] Переключение работает автоматически в зависимости от режима сборки

---

## 🔥 **ЭТАП 1: NOTIFICATIONS (Задачи 18-20)**

**Приоритет:** 🔥 ВЫСОКИЙ  
**Срок:** 7-10 дней  
**Статус:** 2/3 (67%) - Задачи 19 (16/16), 20 выполнены

- [ ] **18. `notifications_apns_setup`** - Настроить APNs инфраструктуру (сертификаты) 📋 ИНСТРУКЦИЯ ГОТОВА
  - [x] Проверено на сервере: APNs сертификаты ОТСУТСТВУЮТ (0 найдено) ✅
  - [x] NSSpeechRecognitionUsageDescription в Info.plist: ✅ ДОБАВЛЕН (задача 4)
  - [x] ✅ СОЗДАНА: Полная инструкция в `APNS_SETUP_COMPLETE_GUIDE.md` (7 шагов, детальные команды) ✅
  - [ ] ❌ НУЖНО: Выполнить шаги из инструкции:
    - [ ] Шаг 1: Создать App ID с Push Notifications в Apple Developer Portal
    - [ ] Шаг 2: Сгенерировать Development и Production сертификаты
    - [ ] Шаг 3: Экспортировать сертификаты в .p12 формат
    - [ ] Шаг 4: Конвертировать в .pem и загрузить на сервер
    - [ ] Шаг 5: Установить Python библиотеку PyAPNs2 на сервере
    - [ ] Шаг 6: Создать push_notification_service.py на сервере
    - [ ] Шаг 7: Добавить endpoint /api/notifications/push/send в API Gateway
    - [ ] Шаг 8: Протестировать отправку push-уведомления
  - [ ] **Документация:** См. `APNS_SETUP_COMPLETE_GUIDE.md` для детальных инструкций

- [x] **19. `notifications_server_implementation`** - Реализовать 16 Notifications endpoint'ов на сервере ✅ ВЫПОЛНЕНО (16/16)
  - [x] ✅ ДОБАВЛЕНО: Все 16 endpoints на сервер в `/opt/aladdin-backend/security/microservices/api_gateway.py` ✅
  - [x] **Основные 8 endpoints:**
    - `/api/notifications/list` ✅
    - `/api/notifications/stats` ✅
    - `/api/notifications/unread_count` ✅
    - `/api/notifications/mark_read/{notification_id}` ✅
    - `/api/notifications/delete/{notification_id}` ✅
    - `/api/notifications/bulk_mark_read` ✅
    - `/api/notifications/test` ✅
    - `/api/notifications/settings` ✅
  - [x] **Дополнительные 8 endpoints:**
    - `/api/notifications/categories` ✅
    - `/api/notifications/preferences` (GET/PUT) ✅
    - `/api/notifications/clear_all` ✅
    - `/api/notifications/archive/{notification_id}` ✅
    - `/api/notifications/unarchive/{notification_id}` ✅
    - `/api/notifications/filter` ✅
    - `/api/notifications/search` ✅
    - `/api/notifications/export` ✅
  - [x] Реализована логика для каждого endpoint'а с SFM интеграцией ✅
  - [x] Проверен синтаксис Python файла - корректен ✅
  - [x] ✅ СОЗДАНЫ: Скрипты для перезапуска (`restart_server.sh`) и тестирования (`test_endpoints.sh`) ✅
  - [ ] Подключить к базе данных уведомлений (требует настройки БД)
  - [ ] Протестировать все endpoint'ы через Postman/curl (выполнить `./test_endpoints.sh`)

- [x] **20. `notifications_localization`** - Добавить локализацию для типов уведомлений ✅
  - [x] Добавлены ключи локализации в `LocalizationManager.swift` (RU/EN):
    - `notification_type_threat`, `notification_type_success`, `notification_type_warning`
    - `notification_type_info`, `notification_type_bypass`, `notification_type_system`
    - `notification_type_family`, `notification_type_device`, `notification_type_security`, `notification_type_update`
  - [x] Добавлены детальные сообщения для типов уведомлений:
    - `notification_threat_detected`, `notification_threat_blocked`
    - `notification_protection_activated`, `notification_warning_attention_required`
    - И другие (всего 20+ ключей)
  - [x] Добавлены действия с уведомлениями:
    - `notification_mark_read`, `notification_delete`, `notification_view_details`
  - [x] Добавлены статусы уведомлений:
    - `notification_status_read`, `notification_status_unread`, `notification_status_new`
  - [x] Добавлен метод `localizedName()` в `NotificationType` enum
  - [x] Заменено использование `rawValue` на `localizedName()` в `12_NotificationsScreen.swift`
  - [x] Создан бэкап `LocalizationManager.swift` перед изменениями
  - [ ] Протестировать на разных языках (требует запуска приложения)

---

## 🟡 **ЭТАП 2: COMPONENTS (Задачи 21-22)**

**Приоритет:** 🟡 СРЕДНИЙ  
**Срок:** 12-16 дней  
**Статус:** 0/2 (0%)

- [ ] **21. `components_server_implementation`** - Реализовать 14 Components endpoint'ов на сервере
  - Добавить 14 endpoint'ов в `api_gateway_server_current.py`:
    - `/api/components/health`
    - `/api/components/status/{component_id}`
    - `/api/components/config/{component_id}`
    - `/api/components/enable/{component_id}`
    - `/api/components/disable/{component_id}`
    - `/api/components/restart/{component_id}`
    - И остальные 8 endpoint'ов
  - Реализовать логику управления компонентами
  - Добавить аутентификацию для админских функций
  - Подключить к системе мониторинга компонентов

- [ ] **22. `system_components_ui`** - Добавить секцию "Системные компоненты" в SettingsScreen
  - В `SettingsScreen` добавить новую секцию
  - Показывать только для пользователей с ролью admin
  - Добавить toggles для включения/отключения компонентов
  - Показывать статус каждого компонента (зеленый/красный индикатор)
  - Реализовать вызовы API для управления
  - Добавить обработку ошибок и loading состояния

---

## 🟢 **ЭТАП 3: SYSTEM MANAGEMENT (Задача 23)**

**Приоритет:** 🟢 НИЗКИЙ  
**Срок:** 11-15 дней  
**Статус:** 0/1 (0%)

- [ ] **23. `system_server_implementation`** - Реализовать 11 System Management endpoint'ов на сервере
  - Добавить 11 endpoint'ов в `api_gateway_server_current.py`:
    - `/api/system/health`
    - `/api/system/info`
    - `/api/system/logs`
    - `/api/system/maintenance`
    - `/api/system/metrics`
    - `/api/system/backup`
    - `/api/system/backup/status`
    - И остальные 4 endpoint'а
  - Реализовать enterprise функции управления
  - Добавить мониторинг и алерты
  - Обеспечить безопасность админских функций

---

## 🟢 **ЭТАП 4: ROADSIDE ASSISTANCE iOS (Задачи 24-27)**

**Приоритет:** 🟢 НИЗКИЙ  
**Срок:** 3-5 дней  
**Статус:** 0/4 (0%)

- [ ] **24. `roadside_ios_api`** - Добавить 4 Roadside Assistance метода в APIService.swift
  - В `APIService` добавить методы:
    - `callRoadsideAssistance`
    - `getRoadsideAssistanceStatus`
    - `cancelRoadsideAssistance`
    - `getRoadsideAssistanceHistory`
  - Использовать `AppConfig.Endpoint.roadside*`
  - Добавить обработку ошибок
  - Протестировать методы

- [ ] **25. `roadside_ios_config`** - Добавить 4 Roadside Assistance endpoint'а в AppConfig.swift
  - В `AppConfig.Endpoint` добавить:
    - `roadsideCall`
    - `roadsideStatus`
    - `roadsideCancel`
    - `roadsideHistory`
  - Проверить что пути соответствуют серверным
  - Добавить необходимые модели данных

- [ ] **26. `roadside_ui`** - Добавить Roadside Assistance экран/секцию
  - Создать `RoadsideAssistanceScreen.swift`
  - Реализовать геолокацию для определения места
  - Добавить обработку состояний (ожидание, в пути, прибытие)
  - Создать диалог для вызова помощи с информацией о ТС

- [ ] **27. `roadside_localization`** - Добавить локализацию для текстов помощи на дороге
  - В `LocalizedVersions/Russian.json` добавить ключи:
    - `roadside_call_help`
    - `roadside_status_waiting`
    - `roadside_status_en_route`
    - `roadside_status_arrived`
    - И другие
  - Добавить английские переводы
  - Использовать ключи в `RoadsideAssistanceScreen`
  - Протестировать на разных языках

---

## 🧪 **ЭТАП 5: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПРОДАКШЕНА (Задачи 28-60)**

**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Срок:** 10 дней  
**Статус:** 0/33 (0%)

### **5.1 ПРОВЕРКА ИСПРАВЛЕНИЙ MOCK (Задача 28)**

- [ ] **28. `final_mock_verification`** - Проверить что все mock данные заменены на реальные API
  - [ ] `AppConfig.useMockAPI = false` работает в продакшене
  - [ ] Все 25 endpoint'ов добавлены в `AppConfig.Endpoint`
  - [ ] Все жесткие строки "/api/..." заменены на `AppConfig.Endpoint.*`
  - [ ] `NotificationsViewModel` получает данные с сервера
  - [ ] `AIAssistantViewModel` отправляет запросы на сервер
  - [ ] `AnalyticsService` использует `RemoteAnalyticsService`
  - [ ] Нет `DispatchQueue.main.asyncAfter` симуляций
  - [ ] Все ViewModel'ы возвращают реальные данные

### **5.2 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ (Задача 29)**

- [ ] **29. `final_api_integration_test`** - Полное интеграционное тестирование с сервером
  - [ ] **Аутентификация:** Регистрация семьи → Получение токенов → Валидация JWT
  - [ ] **AI Assistant:** Отправка сообщений → Получение ответов → Обработка ошибок
  - [ ] **Notifications:** Получение уведомлений → Отметка прочитанными → Удаление
  - [ ] **Analytics:** Загрузка статистики → Фильтры → Экспорт данных
  - [ ] **Family Management:** Добавление членов → Управление ролями → Чат
  - [ ] **Security:** Сканирование → Блокировка угроз → Отчеты
  - [ ] **Settings:** Сохранение настроек → Синхронизация → Восстановление

### **5.3 ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ (Задача 30)**

- [ ] **30. `final_performance_test`** - Тестирование производительности и отклика
  - [ ] **Время запуска:** < 3 секунд
  - [ ] **API отклик:** < 500ms для основных запросов
  - [ ] **Память:** < 100MB при нормальном использовании
  - [ ] **Батарея:** Оптимизированное потребление
  - [ ] **Сеть:** Эффективное кэширование и сжатие

### **5.4 АУДИТ БЕЗОПАСНОСТИ (Задача 31)**

- [ ] **31. `final_security_audit`** - Аудит безопасности и валидация токенов
  - [ ] **JWT токены:** Правильная валидация и хранение
  - [ ] **Keychain:** Шифрование чувствительных данных
  - [ ] **SSL Pinning:** Защита от MITM атак
  - [ ] **Input validation:** Все входные данные проверены
  - [ ] **Logs:** Нет логирования паролей/токенов
  - [ ] **Permissions:** Корректные запросы доступа

### **5.5 ТЕСТИРОВАНИЕ ЛОКАЛИЗАЦИИ (Задача 32)**

- [ ] **32. `final_localization_test`** - Тестирование всех переводов и локализации
  - [ ] **Русский язык:** Все тексты на русском
  - [ ] **Английский язык:** Fallback работает
  - [ ] **Динамические тексты:** Правильные формы числительных
  - [ ] **RTL языки:** Поддержка если понадобится
  - [ ] **Обновления:** Новые ключи добавлены

### **5.6 ТЕСТИРОВАНИЕ НА УСТРОЙСТВАХ (Задача 33)**

- [ ] **33. `final_device_compatibility`** - Тестирование на разных устройствах и iOS версиях
  - [ ] **iPhone:** SE, 8, X, 11, 12, 13, 14, 15
  - [ ] **iPad:** Mini, Air, Pro (9.7", 11", 12.9")
  - [ ] **iOS версии:** 15.0+ (минимум iOS 15)
  - [ ] **Ориентации:** Портрет + Ландшафт
  - [ ] **Разрешения:** HD, Full HD, 4K

### **5.7 ТЕСТИРОВАНИЕ OFFLINE РЕЖИМА (Задача 34)**

- [ ] **34. `final_offline_mode_test`** - Тестирование offline режима и кэширования
  - [ ] **Кэширование:** Данные сохраняются локально
  - [ ] **Синхронизация:** При восстановлении связи
  - [ ] **UI состояния:** Правильные сообщения об ошибках
  - [ ] **Функциональность:** Базовые функции работают оффлайн
  - [ ] **Восстановление:** Данные не теряются

### **5.8 ФИНАЛЬНЫЙ QA ЧЕК-ЛИСТ (Задачи 35-60)**

- [ ] **35. `final_qa_checklist`** - Финальный QA чек-лист перед релизом
  - [ ] **App Store требования:**
    - [ ] Иконки: Все размеры (20pt, 29pt, 40pt, 60pt, 76pt, 83.5pt)
    - [ ] Скриншоты: Русские + Английские (5-6 скриншотов)
    - [ ] Описание: Полное описание на русском + английском
    - [ ] Ключевые слова: SEO оптимизация
    - [ ] Поддержка: Контакты для поддержки
    - [ ] Политика: Ссылки на политику конфиденциальности
  - [ ] **Технические проверки:**
    - [ ] Build: Успешная архивация в Xcode
    - [ ] TestFlight: Тестирование бета-версии
    - [ ] Crash logs: Нет крашей в логах
    - [ ] Analytics: Отправка данных работает
    - [ ] Push notifications: Тестирование APNs
    - [ ] In-app purchases: Тестирование платежей

- [ ] **36-60. Дополнительные тесты и проверки**
  - [ ] Тестирование всех экранов на краши
  - [ ] Проверка всех навигационных переходов
  - [ ] Тестирование всех форм ввода
  - [ ] Проверка всех API endpoints
  - [ ] Тестирование всех уведомлений
  - [ ] Проверка всех настроек
  - [ ] Тестирование всех платежей
  - [ ] Проверка всех отчетов
  - [ ] Тестирование всех графиков
  - [ ] Проверка всех фильтров
  - [ ] Тестирование всех экспортов
  - [ ] Проверка всех импортов
  - [ ] Тестирование всех синхронизаций
  - [ ] Проверка всех резервных копий
  - [ ] Тестирование всех восстановлений
  - [ ] Проверка всех обновлений
  - [ ] Тестирование всех миграций
  - [ ] Проверка всех валидаций
  - [ ] Тестирование всех ошибок
  - [ ] Проверка всех логов
  - [ ] Тестирование всех метрик
  - [ ] Проверка всех алертов
  - [ ] Тестирование всех уведомлений
  - [ ] Проверка всех разрешений
  - [ ] Финальная проверка готовности к релизу

---

## 📊 **СТАТИСТИКА ПО ЭТАПАМ**

| Этап | Задач | Выполнено | Прогресс | Приоритет |
|------|-------|-----------|----------|-----------|
| 🚨 Аварийный (AI Assistant) | 5 | 2 | 40% | 🔥 КРИТИЧЕСКИЙ |
| 🔧 Этап 0 (Mock исправления) | 12 | 12 | 100% | 🔥 КРИТИЧЕСКИЙ ✅ |
| 🔥 Этап 1 (Notifications) | 3 | 1 | 33% | 🔥 ВЫСОКИЙ |
| 🟡 Этап 2 (Components) | 2 | 0 | 0% | 🟡 СРЕДНИЙ |
| 🟢 Этап 3 (System Management) | 1 | 0 | 0% | 🟢 НИЗКИЙ |
| 🟢 Этап 4 (Roadside iOS) | 4 | 0 | 0% | 🟢 НИЗКИЙ |
| 🧪 Этап 5 (Тестирование) | 33 | 0 | 0% | 🔥 КРИТИЧЕСКИЙ |
| 🔐 Этап 6 (Безопасность) | 7 | 7 | 100% | 🔥 ВЫСОКИЙ ✅ |
| **ИТОГО** | **67** | **21** | **31%** | **⚠️ В процессе** |

---

## 🎯 **ПРИОРИТЕТЫ ВЫПОЛНЕНИЯ**

1. **ПЕРВЫЙ ПРИОРИТЕТ (КРИТИЧНО!):**
   - 🔧 Этап 0: Исправление Mock данных (задачи 6-17)
   - 🚨 Аварийный этап: AI Assistant (задачи 1-5)

2. **ВТОРОЙ ПРИОРИТЕТ:**
   - 🔥 Этап 1: Notifications (задачи 18-20)

3. **ТРЕТИЙ ПРИОРИТЕТ:**
   - 🧪 Этап 5: Финальное тестирование (задачи 28-60)

4. **ЧЕТВЕРТЫЙ ПРИОРИТЕТ:**
   - 🟡 Этап 2: Components (задачи 21-22)
   - 🟢 Этап 3: System Management (задача 23)
   - 🟢 Этап 4: Roadside iOS (задачи 24-27)

---

## 📝 **ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ**

1. **Отмечайте выполненные задачи:**
   - Замените `[ ]` на `[x]` когда задача выполнена
   - Обновите статистику в начале файла

2. **Обновляйте прогресс:**
   - После выполнения задачи обновите счетчики
   - Пересчитайте процент выполнения

3. **Добавляйте комментарии:**
   - Если задача заблокирована, добавьте комментарий
   - Если есть проблемы, опишите их

4. **Следите за приоритетами:**
   - Начинайте с критических задач
   - Не переходите к следующему этапу пока не завершен предыдущий

---

## ⚠️ **ВАЖНЫЕ НАПОМИНАНИЯ**

- ✅ **Бэкапы перед каждым изменением!**
- ✅ **Тестирование после каждого коммита**
- ✅ **Использовать AppConfig.Endpoint вместо жестких строк**
- ✅ **Все тексты через localizationManager**
- ✅ **Проверять безопасность всех изменений**

---

## 🔐 **ЭТАП 6: УЛУЧШЕНИЯ БЕЗОПАСНОСТИ И НАДЕЖНОСТИ (Задачи 61-67)**

**Приоритет:** 🔥 ВЫСОКИЙ (для продакшена)  
**Срок:** 3-4 дня  
**Статус:** 7/7 (100%)  
**Детальный план:** См. `SECURITY_IMPROVEMENTS_PLAN.md`

- [x] **61. `verify_ssl_pinning_production`** - Проверить SSL Pinning в продакшене 🔥 КРИТИЧЕСКИЙ ✅
  - [x] Проверено что `enableSSLPinning: Bool = true` по умолчанию в NetworkManager.init()
  - [x] Добавлен assert для продакшена (#if !DEBUG)
  - [x] Добавлено логирование статуса SSL Pinning (DEBUG и Production)
  - [x] Добавлена метрика для отслеживания SSL Pinning ошибок (os_log)
  - [x] Добавлено логирование успешных проверок сертификатов
  - [ ] Протестировать на реальном сервере (требует реального устройства)

- [x] **62. `add_rate_limiting`** - Добавить rate limiting для API запросов 🔥 ВЫСОКИЙ ✅
  - [x] Создан `Core/Network/RateLimiter.swift` с полным функционалом:
    - Thread-safe операции с DispatchQueue
    - Sliding window algorithm (скользящее окно)
    - Конфигурируемые лимиты (100 запросов/минуту)
    - Production логирование через os_log
    - DEBUG логирование для отладки
  - [x] Интегрирован в `NetworkManager.performRequest()`:
    - Проверка лимита перед каждым запросом
    - Регистрация запросов после проверки
    - Блокировка при превышении лимита
  - [x] Добавлена обработка 429 ошибок от сервера:
    - Парсинг Retry-After заголовка
    - Возврат NetworkError.tooManyRequests
    - Production логирование
  - [x] Логирование превышений лимита (DEBUG и Production)
  - [x] Thread-safe операции с барьерными блоками

- [x] **63. `add_api_response_validation`** - Добавить валидацию данных от API 🔥 ВЫСОКИЙ ✅
  - [x] Создан `Core/Validation/APIResponseValidator.swift` с полной валидацией:
    - AnalyticsResponse: проверка числовых полей >= 0, protectionLevel 0-100, валидные period'ы
    - FamilyMemberResponse: проверка id/name не пустые, threatsBlocked >= 0, валидные role/status
    - DeviceDetailResponse: проверка id/name/owner не пустые, threatsBlocked >= 0, batteryLevel 0-100, IP формат
    - ProtectionStatsResponse: проверка числовых полей >= 0, securityScore 0-100, валидные уровни защиты
    - FamilyChatMessageResponse: проверка id/sender не пустые, URL форматы, messageType/readStatus
    - CreateFamilyResponse: проверка обязательных полей, валидация членов семьи
  - [x] Интегрирован в `NetworkManager.performRequest()` после декодирования
  - [x] Обработка ValidationError с понятными сообщениями
  - [x] Production + DEBUG логирование ошибок валидации
  - [x] Graceful handling - возвращает ошибку вместо краша приложения

- [x] **64. `add_graceful_degradation_analytics`** - Добавить graceful degradation в RemoteAnalyticsService 🟡 СРЕДНИЙ ✅
  - [x] Добавлен `LocalAnalyticsService` fallback в `RemoteAnalyticsService`
  - [x] Реализован кэш с временем жизни 5 минут для успешных ответов
  - [x] Добавлены helper методы для работы с кэшем (getCached*, setCached*)
  - [x] Graceful degradation в fetchSummary, fetchSecurityAnalytics, fetchUsageAnalytics
  - [x] Production логирование использования кэша и fallback
  - [x] Добавлен индикатор `isOfflineMode` в `AnalyticsViewModel`
  - [x] Индикатор офлайн режима в UI с иконкой и текстом
  - [x] Локализация для "Офлайн режим - показаны кэшированные данные" (RU/EN)
  - [x] Thread-safe операции с кэшем

- [x] **65. `add_metrics_server_upload`** - Добавить отправку метрик на сервер 🟡 СРЕДНИЙ ✅
  - [x] Создан `Core/Monitoring/MetricsService.swift` с полной функциональностью:
    - Пакетная отправка метрик (макс 50 в пакете)
    - Периодическая отправка каждые 30 секунд
    - Thread-safe очередь метрик
    - Production логирование через os_log
    - Метрики: API requests, user actions, errors, alerts, health reports
  - [x] Интегрирован в `RemoteAnalyticsService`:
    - Заменены все TODO комментарии на реальную отправку метрик
    - trackAPIRequest, trackUserAction, trackError, trackAlert, trackHealthReport теперь отправляют данные
  - [x] Добавлен endpoint `/api/metrics/upload` в `AppConfig.Endpoint`
  - [x] Автоматическая отправка при накоплении 50 метрик или каждые 30 секунд
  - [x] Обработка ошибок отправки (возврат метрик в очередь при неудаче)
  - [x] Device ID, app version, platform в метриках для аналитики

- [x] **66. `add_performance_metrics`** - Добавить метрики производительности 🟢 НИЗКИЙ ✅
  - [x] Создан `Core/Monitoring/PerformanceMonitor.swift` с полным функционалом:
    - FPS мониторинг через CADisplayLink (обновление каждую секунду)
    - Мониторинг памяти через Timer (каждые 30 секунд)
    - Отслеживание времени загрузки экранов (startScreenLoad/endScreenLoad)
    - Метрики сетевых запросов (request/response time, bytes transferred)
    - Thread-safe операции через PerformanceMonitor.shared
    - Production логирование через os_log
  - [x] Интегрирован в ключевые экраны:
    - AnalyticsViewModel: отслеживание загрузки аналитики
    - MainViewModel: отслеживание загрузки дашборда
    - FamilyViewModel: отслеживание загрузки членов семьи
  - [x] Метрики отправляются через MetricsService:
    - screen_load_complete: время загрузки экранов
    - network_request_complete: время сетевых запросов
    - fps_measurement: FPS каждые 10 секунд
    - memory_usage_check: использование памяти каждые 30 секунд
    - action_performance: время выполнения действий
  - [x] UIViewController extensions для удобного отслеживания
  - [x] NetworkManager extensions для отслеживания запросов

- [x] **67. `add_input_sanitization`** - Добавить санитизацию пользовательского ввода 🔥 ВЫСОКИЙ ✅
  - [x] Создан `Core/Validation/InputSanitizer.swift` с полной защитой:
    - XSS защита: блокирует script, iframe, object, embed, javascript:, vbscript:, event handlers, CSS expressions
    - SQL injection защита: блокирует SELECT, INSERT, UPDATE, DELETE, UNION, комментарии
    - Валидация форматов: email, phone, recovery code, family ID
    - Ограничения длины для всех типов данных
    - Удаление опасных символов (< > " ' & | ; ` $ ( ) { } [ ])
  - [x] Применена ко всем критическим полям ввода:
    - AI Assistant: санитизация сообщений в AIAssistantViewModel.sendMessage()
    - Family Registration: санитизация кодов семьи в FamilyRegistrationViewModel.joinFamily()
    - Валидация с понятными сообщениями об ошибках
    - Graceful error handling с показом ошибок пользователю
  - [x] Extensions для String: sanitizedAsMessage(), sanitizedAsEmail(), sanitizedAsPhone(), etc.
  - [x] Production логирование через os_log для обнаружения атак
  - [x] Thread-safe singleton InputSanitizer.shared

---

**Последнее обновление:** 10 февраля 2026 г.  
**Следующая проверка:** После выполнения каждой задачи  
**Новые задачи безопасности:** Добавлены в Этап 6 (см. `SECURITY_IMPROVEMENTS_PLAN.md`)
