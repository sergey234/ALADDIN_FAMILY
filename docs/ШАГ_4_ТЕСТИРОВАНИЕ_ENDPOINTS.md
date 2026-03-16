# 📋 ШАГ 4: ТЕСТИРОВАНИЕ ENDPOINTS

**Дата:** 2026-03-14  
**Статус:** ⏳ **В ПРОЦЕССЕ**

---

## 🎯 ЦЕЛЬ

Протестировать все обновленные endpoints для проверки работы с PostgreSQL.

---

## 📝 ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 4.1: Получить JWT токен для тестирования**

```bash
# Войти на сервер
ssh root@149.154.65.180

# Получить токен (замените на реальные credentials)
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password"
  }'

# Сохранить токен в переменную
export TOKEN="Bearer YOUR_TOKEN_HERE"
```

---

### **ШАГ 4.2: Тестирование crash_detection_router**

#### **4.2.1: GET /api/crash-detection/status**

```bash
curl -X GET http://localhost:8002/api/crash-detection/status \
  -H "Authorization: $TOKEN"
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "active_sessions": 0,
  "total_alerts_last_hour": 0,
  "is_monitoring": false
}
```

---

#### **4.2.2: POST /api/crash-detection/alert**

```bash
curl -X POST http://localhost:8002/api/crash-detection/alert \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "severity": "high",
    "accelerometer_data": {"x": 1.5, "y": 2.0, "z": 1.8},
    "gyroscope_data": {"x": 0.1, "y": 0.2, "z": 0.1},
    "speed": 60.5,
    "g_force": 4.2
  }'
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "alert_id": "uuid-here",
  "message": "Crash alert processed..."
}
```

**Проверить в БД:**
```bash
psql -U postgres -d aladdin_db -c "SELECT * FROM crash_detection_alerts ORDER BY created_at DESC LIMIT 1;"
```

---

### **ШАГ 4.3: Тестирование roadside_assistance_router**

#### **4.3.1: POST /api/roadside-assistance/call**

```bash
curl -X POST http://localhost:8002/api/roadside-assistance/call \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "problem_type": "flat_tire",
    "location": {
      "latitude": 55.7558,
      "longitude": 37.6173,
      "address": "Test Address"
    },
    "description": "Flat tire on front left wheel",
    "vehicle_info": {
      "make": "Toyota",
      "model": "Camry",
      "year": 2020
    }
  }'
```

**Ожидаемый результат:**
```json
{
  "status": "success",
  "request": {
    "request_id": "uuid-here",
    "status": "pending",
    ...
  }
}
```

**Проверить в БД:**
```bash
psql -U postgres -d aladdin_db -c "SELECT * FROM roadside_assistance_requests ORDER BY created_at DESC LIMIT 1;"
```

---

#### **4.3.2: GET /api/roadside-assistance/history**

```bash
curl -X GET "http://localhost:8002/api/roadside-assistance/history?limit=10" \
  -H "Authorization: $TOKEN"
```

**Ожидаемый результат:** Список запросов из БД

---

### **ШАГ 4.4: Тестирование parental_control_router**

#### **4.4.1: GET /api/v1/parental-control/stats**

```bash
curl -X GET "http://localhost:8002/api/v1/parental-control/stats?childId=test_child" \
  -H "Authorization: $TOKEN"
```

**Ожидаемый результат:**
```json
{
  "content_blocked": {
    "websites_blocked": 0,
    "apps_blocked": 0,
    ...
  },
  "screen_time": {...},
  "location": {...},
  "monitoring": {...}
}
```

**Проверить в БД:**
```bash
psql -U postgres -d aladdin_db -c "SELECT * FROM parental_control_stats LIMIT 1;"
```

---

#### **4.4.2: GET /parental/bypass/stats**

```bash
curl -X GET "http://localhost:8002/parental/bypass/stats?childId=test_child" \
  -H "Authorization: $TOKEN"
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "today": 0,
  "week": 0,
  "blocked": 0,
  ...
}
```

---

### **ШАГ 4.5: Тестирование subscription_sync_router**

#### **4.5.1: GET /api/subscription/status**

```bash
curl -X GET http://localhost:8002/api/subscription/status \
  -H "Authorization: $TOKEN"
```

**Ожидаемый результат:**
```json
{
  "userId": "uuid-here",
  "isActive": true,
  "daysRemaining": null,
  "canRenew": false,
  "lastModified": "2026-03-14T..."
}
```

---

#### **4.5.2: POST /api/subscription/update**

```bash
curl -X POST http://localhost:8002/api/subscription/update \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test_user",
    "subscriptionType": "premium",
    "status": "active",
    "deviceId": "test_device"
  }'
```

**Проверить в БД:**
```bash
psql -U postgres -d aladdin_db -c "SELECT * FROM subscriptions WHERE user_id = 'test_user'::uuid;"
```

---

### **ШАГ 4.6: Тестирование metrics_router**

#### **4.6.1: POST /api/metrics/upload**

```bash
curl -X POST http://localhost:8002/api/metrics/upload \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test_device_123",
    "appVersion": "1.0.0",
    "platform": "ios",
    "metrics": [
      {
        "type": "event",
        "timestamp": 1700000000.0,
        "action": "button_click",
        "parameters": {"button": "submit"}
      },
      {
        "type": "api_call",
        "timestamp": 1700000001.0,
        "endpoint": "/api/test",
        "method": "GET",
        "responseTime": 0.123,
        "statusCode": 200,
        "success": true
      }
    ]
  }'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "uploadedCount": 2,
  "message": "Успешно загружено 2 метрик"
}
```

**Проверить в БД:**
```bash
psql -U postgres -d aladdin_db -c "SELECT * FROM analytics_metrics ORDER BY created_at DESC LIMIT 2;"
```

---

## ✅ КРИТЕРИИ УСПЕХА

- [ ] Все endpoints отвечают (200 или 422)
- [ ] Данные сохраняются в БД
- [ ] Нет ошибок в логах сервера
- [ ] JWT авторизация работает
- [ ] Все таблицы используются корректно

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### **Проблема 1: 401 Unauthorized**

**Решение:**
```bash
# Проверить токен
echo $TOKEN

# Получить новый токен
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "...", "password": "..."}'
```

---

### **Проблема 2: 500 Internal Server Error**

**Решение:**
```bash
# Проверить логи
tail -n 50 /opt/aladdin-backend/logs/app.log | grep -i error

# Проверить подключение к БД
psql -U postgres -d aladdin_db -c "SELECT 1;"
```

---

### **Проблема 3: Данные не сохраняются в БД**

**Решение:**
```bash
# Проверить, что таблицы существуют
psql -U postgres -d aladdin_db -c "\dt"

# Проверить права доступа
psql -U postgres -d aladdin_db -c "\du"

# Проверить логи на ошибки БД
tail -n 100 /opt/aladdin-backend/logs/app.log | grep -i "database\|postgres\|sql"
```

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного тестирования:

- ✅ Все endpoints работают
- ✅ Данные сохраняются в БД
- ✅ Нет ошибок
- ✅ Система готова к использованию

---

**Статус:** ⏳ **ГОТОВО К ВЫПОЛНЕНИЮ**
