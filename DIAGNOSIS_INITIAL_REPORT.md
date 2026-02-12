# 🔍 ПЕРВИЧНЫЙ ОТЧЕТ ДИАГНОСТИКИ ENDPOINT'ОВ

**Дата:** 2026-02-11  
**Время:** Начало диагностики  
**Сервер:** 149.154.65.180:8002

---

## ✅ ПОДКЛЮЧЕНИЕ К СЕРВЕРУ

**Статус:** ✅ Успешно подключен

**Параметры:**
- IP: 149.154.65.180
- Пользователь: root
- Путь проекта: /opt/aladdin-backend
- API порт: 8002

---

## 📊 ОБНАРУЖЕННАЯ СТАТИСТИКА

### **Роутеры на сервере:**

#### **security/api/routers/** (25 роутеров):
1. `gamification_router.py` - **30 endpoint'ов** ✅
2. `parental_control_sync_router.py` - **20 endpoint'ов** ✅
3. `notifications_router.py` - **18 endpoint'ов** ✅
4. `components_router.py` - **14 endpoint'ов** ✅
5. `system_router.py` - **11 endpoint'ов** ✅
6. `other_functions_sync_router.py` - **10 endpoint'ов** ✅
7. `app_settings_sync_router.py` - **10 endpoint'ов** ✅
8. `subscription_sync_router.py` - **8 endpoint'ов** ✅
9. `dark_web_monitoring_router.py` - **8 endpoint'ов** ✅
10. `crash_detection_router.py` - **8 endpoint'ов** ✅
11. `ai_assistant_router.py` - **8 endpoint'ов** ✅
12. `location_bubble_router.py` - **6 endpoint'ов** ✅
13. `iot_router.py` - **6 endpoint'ов** ✅
14. `identity_theft_protection_router.py` - **6 endpoint'ов** ✅
15. `user_profile_sync_router.py` - **5 endpoint'ов** ✅
16. `roadside_assistance_router.py` - **5 endpoint'ов** ✅
17. `offline_storage_sync_router.py` - **5 endpoint'ов** ✅
18. `ai_categories_router.py` - **5 endpoint'ов** ✅
19. `elderly_interface_sync_router.py` - **4 endpoint'а** ✅
20. `data_cleanup_router.py` - **4 endpoint'а** ✅
21. `crash_detection_sync_router.py` - **4 endpoint'а** ✅
22. `anti_tracker_router.py` - **4 endpoint'а** ✅
23. `driving_reports_router.py` - **3 endpoint'а** ✅
24. `parental_control_router.py` - **2 endpoint'а** ✅
25. И другие...

**ИТОГО в security/api/routers:** ~250+ endpoint'ов

#### **app/routers/** (8 роутеров):
1. `protection.py` - **8 endpoint'ов** ✅
2. `components.py` - **6 endpoint'ов** ✅
3. `payments.py` - **5 endpoint'ов** ✅
4. `referral.py` - **4 endpoint'а** ✅
5. `auth_router.py` - **4 endpoint'а** ✅
6. `referral_test.py` - **3 endpoint'а** ✅
7. `family.py` - **1 endpoint** ⚠️ (мало!)
8. `__init__.py` - **0 endpoint'ов**

**ИТОГО в app/routers:** ~31 endpoint

### **Общее количество endpoint'ов в коде:** ~280+ endpoint'ов

### **Endpoint'ы видимые в OpenAPI:** 115 endpoint'ов

**Разница:** ~165 endpoint'ов не видны в OpenAPI (требуют авторизацию или не подключены)

---

## ❌ КРИТИЧНЫЕ ПРОБЛЕМЫ

### **1. POST /api/family/create** ❌ **НЕ РАБОТАЕТ**

**Диагностика:**
- ✅ Функция существует: `security/comprehensive_anonymous_family_system.py:create_family_profile`
- ❌ FastAPI endpoint не найден в `app/routers/family.py`
- ✅ Роутер подключен в main.py
- ❌ HTTP: 404 Not Found

**Проблема:** Функция есть, но FastAPI endpoint не добавлен в роутер

**Решение:** Добавить `@router.post("/create")` в `app/routers/family.py`

---

### **2. POST /api/auth/login-by-recovery-code** ❌ **НЕ СУЩЕСТВУЕТ**

**Диагностика:**
- ❌ FastAPI endpoint не найден в `app/routers/auth_router.py`
- ❌ Функция не найдена
- ❌ HTTP: 404 Not Found

**Проблема:** Endpoint полностью отсутствует

**Решение:** Создать полностью (функция + endpoint)

---

## 📋 ENDPOINT'Ы В OPENAPI (115 штук)

### **Категории:**

1. **AI Assistant** (8 endpoint'ов):
   - `/api/ai/assistant/capabilities`
   - `/api/ai/assistant/chat`
   - `/api/ai/assistant/analyze_threat`
   - `/api/ai/assistant/recommendations`
   - `/api/ai/assistant/security_tips`
   - `/api/ai/assistant/report_incident`
   - `/api/ai/assistant/history`
   - `/api/ai/assistant/feedback`

2. **Authentication** (4 endpoint'а):
   - `/api/auth/login`
   - `/api/auth/logout`
   - `/api/auth/refresh`
   - `/api/auth/register`
   - ❌ `/api/auth/login-by-recovery-code` - **ОТСУТСТВУЕТ!**

3. **Notifications** (18 endpoint'ов):
   - `/api/notifications`
   - `/api/notifications/read`
   - `/api/notifications/stats`
   - `/api/notifications/unread_count`
   - И другие...

4. **Components** (5 endpoint'ов):
   - `/api/components/status/{component_id}`
   - `/api/components/enable/{component_id}`
   - `/api/components/disable/{component_id}`
   - `/api/components/configuration/{component_id}`
   - `/api/components/batch/status`

5. **Crash Detection** (6 endpoint'ов):
   - `/api/crash-detection/start`
   - `/api/crash-detection/stop`
   - `/api/crash-detection/status`
   - `/api/crash-detection/data`
   - `/api/crash-detection/setup`
   - `/api/crash-detection/alert`

6. **IoT Security** (6 endpoint'ов):
   - `/api/iot/scan/{homeId}`
   - `/api/iot/threats/{homeId}`
   - `/api/iot/fix/{threatId}`
   - `/api/iot/status/{homeId}`
   - `/api/iot/devices/{homeId}`
   - `/api/iot/device/{deviceId}/block`

7. **Family** (1 endpoint):
   - `/api/family/stats`
   - ❌ `/api/family/create` - **ОТСУТСТВУЕТ!**

8. **И другие...**

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### **Этап 1: Исправление критичных endpoint'ов (СЕЙЧАС)**
1. ✅ Диагностика завершена
2. ⏳ Исправить POST /api/family/create
3. ⏳ Создать POST /api/auth/login-by-recovery-code

### **Этап 2: Полная диагностика всех endpoint'ов (2-3 часа)**
1. ⏳ Создать полный список всех 331 endpoint'а
2. ⏳ Проверить каждый endpoint отдельно
3. ⏳ Создать детальный отчет

### **Этап 3: Исправление проблем (4-6 часов)**
1. ⏳ Исправить все неработающие endpoint'ы
2. ⏳ Проверить подключение всех роутеров
3. ⏳ Устранить дублирование

---

## 📊 СТАТИСТИКА

- **Всего endpoint'ов в коде:** ~280+
- **Видимых в OpenAPI:** 115
- **Требуют авторизацию:** ~165
- **Критичных проблем:** 2
- **Роутеров найдено:** 33

---

**Следующий шаг:** Начать исправление критичных endpoint'ов
