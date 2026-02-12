# 📋 ДЕТАЛЬНЫЙ ПЛАН ДЛЯ КАЖДОГО ИЗ 331 ENDPOINT'А

**Дата:** 2026-02-11  
**Специалист:** iOS разработчик с 15-летним опытом  
**Цель:** Детальный план проверки, исправления и тестирования КАЖДОГО endpoint'а  
**Приоритет:** 🔥 КРИТИЧНО

---

## 📊 СТРУКТУРА ДОКУМЕНТА

Этот документ содержит детальный план для каждого из 331 endpoint'а, организованный по категориям:

1. **Authentication (12 endpoint'ов)** - строки 1-12
2. **Subscription (12 endpoint'ов)** - строки 13-24
3. **Notifications (19 endpoint'ов)** - строки 25-43
4. **Parental Control (24 endpoint'а)** - строки 44-67 (4 базовых + 20 синхронизации)
5. **Identity Protection (8 endpoint'ов)** - строки 68-75
6. **Dark Web Monitoring (7 endpoint'ов)** - строки 76-82
7. **Location Tracking (15 endpoint'ов)** - строки 83-97 (7 базовых + 7 синхронизации + 1)
8. **Data Cleanup (6 endpoint'ов)** - строки 98-103
9. **Anti-Tracker (9 endpoint'ов)** - строки 104-112
10. **Roadside Assistance (5 endpoint'ов)** - строки 113-117
11. **System Management (11 endpoint'ов)** - строки 118-128
12. **Analytics (7 endpoint'ов)** - строки 129-135
13. **AI Categories (8 endpoint'ов)** - строки 136-143
14. **AI Assistant (8 endpoint'ов)** - строки 144-151
15. **Components (14 endpoint'ов)** - строки 152-165
16. **Crash Detection (10 endpoint'ов)** - строки 166-175 (6 базовых + 4 синхронизации)
17. **IoT Security (6 endpoint'ов)** - строки 176-181
18. **Gamification (30 endpoint'ов)** - строки 182-211
19. **User Profile Sync (5 endpoint'ов)** - строки 212-216
20. **Subscription Sync (8 endpoint'ов)** - строки 217-224
21. **App Settings Sync (10 endpoint'ов)** - строки 225-234
22. **Other Functions Sync (10 endpoint'ов)** - строки 235-244
23. **Offline Storage Sync (5 endpoint'ов)** - строки 245-249
24. **Elderly Interface Sync (4 endpoint'а)** - строки 250-253
25. **И другие...** - строки 254-331

---

## 🔐 1. AUTHENTICATION (12 ENDPOINT'ОВ)

### **ENDPOINT #1: POST /api/auth/login**
- **Категория:** Authentication
- **Роутер:** `app/routers/auth_router.py`
- **Статус:** ⚠️ ТРЕБУЕТ ПРОВЕРКИ
- **TODO:**
  - [ ] Проверить существование endpoint'а: `grep "@router.post.*login" app/routers/auth_router.py`
  - [ ] Проверить подключение роутера в main.py
  - [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/auth/login" -H "Content-Type: application/json" -d '{"email": "test@test.com", "password": "test"}'`
  - [ ] Проверить ответ (должен быть 200 с access_token)
  - [ ] Проверить валидацию (неправильный email/password → 422)
  - [ ] Проверить обработку ошибок (несуществующий пользователь → 401)

### **ENDPOINT #2: POST /api/auth/login-by-recovery-code** ❌ **КРИТИЧНО!**
- **Категория:** Authentication
- **Роутер:** `app/routers/auth_router.py`
- **Статус:** ❌ НЕ СУЩЕСТВУЕТ
- **Проблема:** Endpoint полностью отсутствует
- **TODO:**
  - [ ] Создать Pydantic модель `RecoveryCodeLoginRequest`
  - [ ] Создать функцию `login_by_recovery_code()`
  - [ ] Добавить endpoint `@router.post("/auth/login-by-recovery-code")`
  - [ ] Реализовать проверку recovery code в БД
  - [ ] Создать JWT токены
  - [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/auth/login-by-recovery-code" -H "Content-Type: application/json" -d '{"family_id": "FAM_TEST", "recovery_code": "TEST"}'`
  - [ ] Проверить ответ (должен быть 200 с access_token и refresh_token)

### **ENDPOINT #3: POST /api/auth/refresh**
- **Категория:** Authentication
- **Роутер:** `app/routers/auth_router.py`
- **Статус:** ⚠️ ТРЕБУЕТ ПРОВЕРКИ
- **TODO:**
  - [ ] Проверить существование endpoint'а
  - [ ] Проверить валидацию refresh_token
  - [ ] Протестировать с валидным refresh_token
  - [ ] Протестировать с невалидным refresh_token (должен быть 401)

### **ENDPOINT #4-12: Остальные Authentication endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint

---

## 💳 2. SUBSCRIPTION (12 ENDPOINT'ОВ)

### **ENDPOINT #13: GET /api/subscription/status**
- **Категория:** Subscription
- **Роутер:** Неизвестно (возможно, только в iOS)
- **Статус:** ⚠️ ТРЕБУЕТ ПРОВЕРКИ
- **TODO:**
  - [ ] Найти роутер для subscription endpoint'ов
  - [ ] Проверить существование endpoint'а
  - [ ] Протестировать с авторизацией
  - [ ] Проверить ответ (должен быть информация о подписке)

### **ENDPOINT #14-24: Остальные Subscription endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint

---

## 🔔 3. NOTIFICATIONS (19 ENDPOINT'ОВ)

### **ENDPOINT #25: GET /api/notifications**
- **Категория:** Notifications
- **Роутер:** `security/api/routers/notifications_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН (задача B1-B5 ВЫПОЛНЕНА)
- **TODO:**
  - [ ] Проверить работу: `curl -X GET "http://149.154.65.180:8002/api/notifications" -H "Authorization: Bearer TOKEN"`
  - [ ] Проверить ответ (должен быть список уведомлений)
  - [ ] Проверить пагинацию (если есть)
  - [ ] Проверить фильтрацию (если есть)

### **ENDPOINT #26: POST /api/notifications/read**
- **Категория:** Notifications
- **Роутер:** `security/api/routers/notifications_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/notifications/read" -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"notification_id": "123"}'`
  - [ ] Проверить ответ (должен быть success: true)
  - [ ] Проверить, что уведомление помечено как прочитанное

### **ENDPOINT #27-43: Остальные Notifications endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint
- **Список endpoint'ов:**
  - GET /api/notifications/stats
  - GET /api/notifications/unread_count
  - POST /api/notifications/mark_read/{notification_id}
  - POST /api/notifications/push/send
  - И другие...

---

## 👨‍👩‍👧‍👦 4. PARENTAL CONTROL (24 ENDPOINT'А)

### **ENDPOINT #44: GET /api/parental-control/stats**
- **Категория:** Parental Control
- **Роутер:** `security/api/routers/parental_control_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать с авторизацией
  - [ ] Проверить ответ (должен быть статистика)

### **ENDPOINT #45-47: Остальные базовые Parental Control endpoint'ы**
- **TODO:** Аналогично проверить

### **ENDPOINT #48-67: Parental Control Sync (20 endpoint'ов)**
- **Категория:** Parental Control Sync
- **Роутер:** `security/api/routers/parental_control_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера в main.py
  - [ ] Протестировать каждый endpoint отдельно
  - **Список endpoint'ов:**
    - GET /api/parental-control-sync/settings/{userId}
    - POST /api/parental-control-sync/settings/{userId}
    - GET /api/parental-control-sync/time-limits/{userId}
    - POST /api/parental-control-sync/time-limits/{userId}
    - И другие...

---

## 🛡️ 5. IDENTITY PROTECTION (8 ENDPOINT'ОВ)

### **ENDPOINT #68: GET /api/identity-protection/health**
- **Категория:** Identity Protection
- **Роутер:** `security/api/routers/identity_theft_protection_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать: `curl -X GET "http://149.154.65.180:8002/api/identity-protection/health"`
  - [ ] Проверить ответ (должен быть {"status": "ok"})

### **ENDPOINT #69-75: Остальные Identity Protection endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint
- **Список:**
  - POST /api/identity-protection/monitor-snils
  - POST /api/identity-protection/monitor-credit
  - POST /api/identity-protection/check
  - POST /api/identity-protection/detect
  - GET /api/identity-protection/alerts
  - GET /api/identity-protection/status
  - POST /api/identity-protection/stop-monitoring

---

## 🌐 6. DARK WEB MONITORING (7 ENDPOINT'ОВ)

### **ENDPOINT #76: GET /api/dark-web/health**
- **Категория:** Dark Web Monitoring
- **Роутер:** `security/api/routers/dark_web_monitoring_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать health check
  - [ ] Проверить ответ

### **ENDPOINT #77-82: Остальные Dark Web endpoint'ы**
- **TODO:** Аналогично проверить
- **Список:**
  - POST /api/dark-web/check
  - POST /api/dark-web/start-monitoring
  - POST /api/dark-web/stop-monitoring
  - GET /api/dark-web/status
  - GET /api/dark-web/breaches

---

## 📍 7. LOCATION TRACKING (15 ENDPOINT'ОВ)

### **ENDPOINT #83: POST /api/location-bubble**
- **Категория:** Location Tracking
- **Роутер:** `security/api/routers/location_bubble_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать генерацию пузыря
  - [ ] Проверить ответ

### **ENDPOINT #84-97: Остальные Location endpoint'ы**
- **TODO:** Аналогично проверить
- **Включая синхронизацию геозон (7 endpoint'ов)**

---

## 🧹 8. DATA CLEANUP (6 ENDPOINT'ОВ)

### **ENDPOINT #98: POST /api/data-cleanup/scan**
- **Категория:** Data Cleanup
- **Роутер:** `security/api/routers/data_cleanup_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать сканирование
  - [ ] Проверить ответ

### **ENDPOINT #99-103: Остальные Data Cleanup endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🚫 9. ANTI-TRACKER (9 ENDPOINT'ОВ)

### **ENDPOINT #104: POST /api/anti-tracker/check**
- **Категория:** Anti-Tracker
- **Роутер:** `security/api/routers/anti_tracker_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать проверку URL
  - [ ] Проверить ответ

### **ENDPOINT #105-112: Остальные Anti-Tracker endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🚗 10. ROADSIDE ASSISTANCE (5 ENDPOINT'ОВ)

### **ENDPOINT #113: POST /api/roadside-assistance/call**
- **Категория:** Roadside Assistance
- **Роутер:** `security/api/routers/roadside_assistance_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать вызов помощи
  - [ ] Проверить ответ

### **ENDPOINT #114-117: Остальные Roadside endpoint'ы**
- **TODO:** Аналогично проверить

---

## ⚙️ 11. SYSTEM MANAGEMENT (11 ENDPOINT'ОВ)

### **ENDPOINT #118: GET /api/system/health**
- **Категория:** System Management
- **Роутер:** `security/api/routers/system_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН (задача 23 ВЫПОЛНЕНА)
- **TODO:**
  - [ ] Протестировать health check
  - [ ] Проверить ответ

### **ENDPOINT #119-128: Остальные System endpoint'ы**
- **TODO:** Аналогично проверить
- **Примечание:** Эти endpoint'ы только для администраторов, не нужны в iOS

---

## 📊 12. ANALYTICS (7 ENDPOINT'ОВ)

### **ENDPOINT #129: GET /api/analytics/stats**
- **Категория:** Analytics
- **Роутер:** Неизвестно
- **Статус:** ⚠️ ТРЕБУЕТ ПРОВЕРКИ
- **TODO:**
  - [ ] Найти роутер для analytics
  - [ ] Проверить существование endpoint'а
  - [ ] Протестировать

### **ENDPOINT #130-135: Остальные Analytics endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🤖 13. AI CATEGORIES (8 ENDPOINT'ОВ)

### **ENDPOINT #136: GET /api/ai-categories/sites**
- **Категория:** AI Categories
- **Роутер:** `security/api/routers/ai_categories_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать получение списка сайтов
  - [ ] Проверить ответ

### **ENDPOINT #137-143: Остальные AI Categories endpoint'ы**
- **TODO:** Аналогично проверить

---

## 💬 14. AI ASSISTANT (8 ENDPOINT'ОВ)

### **ENDPOINT #144: GET /api/ai/assistant/capabilities**
- **Категория:** AI Assistant
- **Роутер:** `security/api/routers/ai_assistant_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН (задача B1-B5 ВЫПОЛНЕНА)
- **TODO:**
  - [ ] Протестировать: `curl -X GET "http://149.154.65.180:8002/api/ai/assistant/capabilities"`
  - [ ] Проверить ответ (должен быть 200 OK)

### **ENDPOINT #145-151: Остальные AI Assistant endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🔧 15. COMPONENTS (14 ENDPOINT'ОВ)

### **ENDPOINT #152: GET /api/components/health**
- **Категория:** Components
- **Роутер:** `security/api/routers/components_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН (задача 21 ВЫПОЛНЕНА)
- **TODO:**
  - [ ] Протестировать health check
  - [ ] Проверить ответ

### **ENDPOINT #153-165: Остальные Components endpoint'ы**
- **TODO:** Аналогично проверить

---

## 💥 16. CRASH DETECTION (10 ENDPOINT'ОВ)

### **ENDPOINT #166: POST /api/crash-detection/start**
- **Категория:** Crash Detection
- **Роутер:** `security/api/routers/crash_detection_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать запуск мониторинга
  - [ ] Проверить ответ

### **ENDPOINT #167-175: Остальные Crash Detection endpoint'ы**
- **TODO:** Аналогично проверить
- **Включая синхронизацию (4 endpoint'а)**

---

## 🏠 17. IOT SECURITY (6 ENDPOINT'ОВ)

### **ENDPOINT #176: GET /api/iot/health**
- **Категория:** IoT Security
- **Роутер:** `security/api/routers/iot_router.py`
- **Статус:** ✅ ПОДКЛЮЧЕН
- **TODO:**
  - [ ] Протестировать health check
  - [ ] Проверить ответ

### **ENDPOINT #177-181: Остальные IoT endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🎮 18. GAMIFICATION (30 ENDPOINT'ОВ)

### **ENDPOINT #182: GET /api/gamification/balance/{userId}**
- **Категория:** Gamification
- **Роутер:** `security/api/routers/gamification_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера в main.py
  - [ ] Протестировать: `curl -X GET "http://149.154.65.180:8002/api/gamification/balance/USER_ID" -H "Authorization: Bearer TOKEN"`
  - [ ] Проверить ответ (должен быть баланс единорогов)
  - [ ] Проверить авторизацию (только свой userId или родитель)

### **ENDPOINT #183-211: Остальные Gamification endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint
- **Категории:**
  - Баланс единорогов: 4 endpoint'а (#182-185)
  - Награды: 6 endpoint'ов (#186-191)
  - Достижения: 5 endpoint'ов (#192-196)
  - Турниры: 6 endpoint'ов (#197-202)
  - Настройки игр: 4 endpoint'а (#203-206)
  - Прогресс игр: 5 endpoint'ов (#207-211)

---

## 👤 19. USER PROFILE SYNC (5 ENDPOINT'ОВ)

### **ENDPOINT #212: GET /api/user-profile-sync/{userId}**
- **Категория:** User Profile Sync
- **Роутер:** `security/api/routers/user_profile_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию профиля
  - [ ] Проверить ответ

### **ENDPOINT #213-216: Остальные User Profile Sync endpoint'ы**
- **TODO:** Аналогично проверить

---

## 💰 20. SUBSCRIPTION SYNC (8 ENDPOINT'ОВ)

### **ENDPOINT #217: GET /api/subscription-sync/{userId}**
- **Категория:** Subscription Sync
- **Роутер:** `security/api/routers/subscription_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию подписки
  - [ ] Проверить ответ

### **ENDPOINT #218-224: Остальные Subscription Sync endpoint'ы**
- **TODO:** Аналогично проверить

---

## ⚙️ 21. APP SETTINGS SYNC (10 ENDPOINT'ОВ)

### **ENDPOINT #225: GET /api/app-settings-sync/{userId}**
- **Категория:** App Settings Sync
- **Роутер:** `security/api/routers/app_settings_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию настроек
  - [ ] Проверить ответ

### **ENDPOINT #226-234: Остальные App Settings Sync endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🔄 22. OTHER FUNCTIONS SYNC (10 ENDPOINT'ОВ)

### **ENDPOINT #235: GET /api/other-functions-sync/geofences/{userId}**
- **Категория:** Other Functions Sync
- **Роутер:** `security/api/routers/other_functions_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию геозон
  - [ ] Проверить ответ

### **ENDPOINT #236-244: Остальные Other Functions Sync endpoint'ы**
- **TODO:** Аналогично проверить
- **Включая:**
  - Геолокация: 7 endpoint'ов
  - Семейный чат: 3 endpoint'а

---

## 💾 23. OFFLINE STORAGE SYNC (5 ENDPOINT'ОВ)

### **ENDPOINT #245: GET /api/offline-storage-sync/{userId}**
- **Категория:** Offline Storage Sync
- **Роутер:** `security/api/routers/offline_storage_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию офлайн хранилища
  - [ ] Проверить ответ

### **ENDPOINT #246-249: Остальные Offline Storage Sync endpoint'ы**
- **TODO:** Аналогично проверить

---

## 👴 24. ELDERLY INTERFACE SYNC (4 ENDPOINT'А)

### **ENDPOINT #250: GET /api/elderly-interface-sync/{userId}**
- **Категория:** Elderly Interface Sync
- **Роутер:** `security/api/routers/elderly_interface_sync_router.py`
- **Статус:** ✅ РЕАЛИЗОВАНО (11.02.2026)
- **TODO:**
  - [ ] Проверить подключение роутера
  - [ ] Протестировать синхронизацию настроек интерфейса
  - [ ] Проверить ответ

### **ENDPOINT #251-253: Остальные Elderly Interface Sync endpoint'ы**
- **TODO:** Аналогично проверить

---

## 🏠 25. FAMILY ENDPOINT'Ы

### **ENDPOINT #254: POST /api/family/create** ❌ **КРИТИЧНО!**
- **Категория:** Family
- **Роутер:** `app/routers/family.py`
- **Статус:** ❌ НЕ РАБОТАЕТ (404)
- **Проблема:** Функция есть, но FastAPI endpoint не добавлен
- **TODO:**
  - [ ] Найти или создать файл `app/routers/family.py`
  - [ ] Импортировать `create_family` из `security.family.family_registration`
  - [ ] Создать Pydantic модели
  - [ ] Добавить endpoint `@router.post("/create")`
  - [ ] Проверить подключение роутера в main.py
  - [ ] Протестировать: `curl -X POST "http://149.154.65.180:8002/api/family/create" -H "Content-Type: application/json" -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V", "device_type": "iOS"}'`
  - [ ] Проверить ответ (должен быть 200/201 с family_id и recovery_code)

### **ENDPOINT #255-331: Остальные endpoint'ы**
- **TODO:** Аналогично проверить каждый endpoint
- **Включая:**
  - Referral endpoint'ы
  - Payments endpoint'ы
  - Protection endpoint'ы
  - Driving Reports endpoint'ы
  - И другие...

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **По статусу:**
- ✅ **Работают:** ~200 endpoint'ов (оценка)
- ⚠️ **Требуют проверки:** ~100 endpoint'ов
- ❌ **Не работают:** 2 критичных endpoint'а (POST /api/family/create, POST /api/auth/login-by-recovery-code)
- ❓ **Неизвестно:** ~29 endpoint'ов

### **По категориям:**
- ✅ **Полностью готовы:** Notifications (19), AI Assistant (8), Components (14), System (11), Gamification (30), Parental Control Sync (20), и другие синхронизации (96)
- ⚠️ **Частично готовы:** Authentication (10/12), Subscription (7/12), Parental Control (4/24), Identity Protection (8/26), Analytics (7/17)
- ❌ **Требуют внимания:** Family (1/10+), и другие

---

## 🎯 ПРИОРИТЕТЫ

### **🔥 КРИТИЧНО (сделать СЕЙЧАС):**
1. POST /api/family/create (#254)
2. POST /api/auth/login-by-recovery-code (#2)

### **🟡 ВАЖНО (сделать сегодня):**
3. Все Authentication endpoint'ы (#1-12)
4. Все Family endpoint'ы (#254-263+)

### **🟢 ОПЦИОНАЛЬНО (можно позже):**
5. Остальные endpoint'ы (#13-253, #264-331)

---

## 📝 ПРИМЕЧАНИЯ

1. **Некоторые endpoint'ы могут быть только для администраторов** (System Management) - их не нужно тестировать из iOS
2. **Некоторые endpoint'ы могут требовать специальных прав** - нужно проверить авторизацию
3. **Некоторые endpoint'ы могут быть опциональными** - можно отложить на потом
4. **Все endpoint'ы синхронизации уже реализованы** (11.02.2026) - нужно только проверить их работу

---

**Последнее обновление:** 2026-02-11  
**Статус:** 📋 **ДЕТАЛЬНЫЙ ПЛАН СОЗДАН**
