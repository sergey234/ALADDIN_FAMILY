# 📡 ИНСТРУКЦИЯ: Интеграция API Endpoints для Dark Web Monitoring

**Дата:** 9 декабря 2025  
**Файл:** `security/api/routers/dark_web_monitoring_router.py` (FastAPI)

---

## 🎯 ЦЕЛЬ

Добавить Flask endpoints для Dark Web Monitoring в основной API сервера.

---

## 📋 ШАГИ ИНТЕГРАЦИИ

### Шаг 1: Отправка файла на сервер

```bash
scp security/api/routers/dark_web_monitoring_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/
```

### Шаг 2: Подключение к серверу

```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
```

### Шаг 3: Добавление в main.py

Открыть файл `/opt/aladdin-backend/api/main.py` или главный FastAPI файл и добавить:

```python
# В начале файла с другими импортами:
from security.api.routers.dark_web_monitoring_router import router as dark_web_router

# После создания app (FastAPI()):
app.include_router(dark_web_router)

# Или с обработкой ошибок (рекомендуется):
try:
    from security.api.routers.dark_web_monitoring_router import router as dark_web_router
    app.include_router(dark_web_router)
    logger.info("✅ Dark Web Monitoring Router зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ Не удалось зарегистрировать Dark Web Monitoring Router: {e}")
```

### Шаг 4: Настройка переменных окружения

Добавить API ключи в `.env` или через export:

```bash
export HIBP_API_KEY="your-haveibeenpwned-api-key"
export BREACHDIRECTORY_API_KEY="your-breachdirectory-api-key"  # опционально
```

Или в конфиге:

```python
# В main.py или config.py
import os
os.environ['HIBP_API_KEY'] = 'your-api-key'
```

### Шаг 5: Перезапуск приложения

```bash
# Если используется systemd
systemctl restart aladdin-backend

# Или если используется supervisor
supervisorctl restart aladdin-backend

# Или если запускается вручную
# Остановить текущий процесс и запустить заново
```

---

## 🔌 ДОСТУПНЫЕ ENDPOINTS

### 1. POST /api/darkweb/check
Проверка email на утечки

**Request:**
```json
{
  "email": "user@example.com",
  "include_hibp": true,
  "include_breachdirectory": true,
  "include_russian": true
}
```

**Response:**
```json
{
  "success": true,
  "email": "user@example.com",
  "breaches_found": 2,
  "breaches": [
    {
      "id": "hibp_...",
      "breach_name": "Example Breach",
      "count": 1000,
      "severity": "high",
      "detected_at": "2025-12-09T12:00:00"
    }
  ],
  "checked_at": "2025-12-09T12:00:00",
  "sources": ["Have I Been Pwned", "BreachDirectory"]
}
```

### 2. POST /api/darkweb/start-monitoring
Запуск автоматического мониторинга

**Request:**
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "phone": "+79991234567",
  "interval_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "next_check": "2025-12-10T12:00:00",
  "interval_hours": 24
}
```

### 3. POST /api/darkweb/stop-monitoring
Остановка мониторинга

**Request:**
```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user123"
}
```

### 4. GET /api/darkweb/status
Получение статуса мониторинга

**Request:**
```
GET /api/darkweb/status?user_id=user123
```

**Response:**
```json
{
  "success": true,
  "is_monitoring": true,
  "user_id": "user123",
  "status": {
    "email": "user@example.com",
    "interval_hours": 24,
    "next_check": "2025-12-10T12:00:00"
  }
}
```

### 5. GET /api/darkweb/breaches
Получение всех найденных утечек

**Request:**
```
GET /api/darkweb/breaches
```

**Response:**
```json
{
  "success": true,
  "threats": [...],
  "analyzed_threats": [...],
  "total_threats": 10,
  "collected_at": "2025-12-09T12:00:00"
}
```

### 6. GET /api/darkweb/health
Health check (без авторизации)

**Request:**
```
GET /api/darkweb/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_loaded": true,
  "cache_stats": {
    "total_entries": 5,
    "valid_entries": 5
  },
  "timestamp": "2025-12-09T12:00:00"
}
```

---

## 🔐 АВТОРИЗАЦИЯ

Все endpoints (кроме `/health`) требуют токен авторизации в заголовке:

```
Authorization: Bearer <token>
```

TODO: Реализовать проверку JWT токена в декораторе `@require_auth`.

---

## ✅ ВАЛИДАЦИЯ

Endpoints автоматически валидируют:
- ✅ Формат email (regex)
- ✅ Формат телефона (10-15 цифр)
- ✅ Наличие обязательных полей
- ✅ Типы данных (int, string)

---

## 🧪 ТЕСТИРОВАНИЕ

После интеграции протестировать:

```bash
# Health check (без авторизации)
curl http://localhost:5000/api/darkweb/health

# Проверка email (требует токен)
curl -X POST http://localhost:5000/api/darkweb/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"email": "test@example.com"}'
```

---

## ⚠️ ВАЖНО

1. ✅ Убедитесь что переменные окружения установлены (HIBP_API_KEY)
2. ✅ Проверьте что путь к агенту правильный в импорте
3. ✅ Проверьте логи после перезапуска на наличие ошибок
4. ✅ Тестируйте endpoints через curl или Postman

---

**Готово к интеграции!** 🚀
