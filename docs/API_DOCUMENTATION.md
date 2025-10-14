# 🔌 API ДОКУМЕНТАЦИЯ - СИСТЕМА БЕЗОПАСНОСТИ ALADDIN

**Версия API:** 1.0  
**Дата:** 8 сентября 2025  
**Базовый URL:** `http://localhost:8000/api/v1`  

---

## 📋 ОБЗОР API

API системы ALADDIN предоставляет RESTful интерфейс для управления всеми компонентами безопасности. Все запросы используют JSON формат и требуют аутентификации.

### **Аутентификация:**
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## 🏗️ ОСНОВНЫЕ КОМПОНЕНТЫ API

### **1. Code Quality Manager API**

#### **Проверка качества файла:**
```http
POST /api/v1/quality/check-file
Content-Type: application/json

{
    "file_path": "core/base.py",
    "tools": ["flake8", "mypy", "pylint"]
}
```

**Ответ:**
```json
{
    "success": true,
    "file_path": "core/base.py",
    "overall_score": 171.4,
    "tools": {
        "flake8": {"score": 100, "errors": 0},
        "mypy": {"score": 95, "errors": 2},
        "pylint": {"score": 90, "errors": 1}
    },
    "duration": 0.69
}
```

#### **Проверка качества проекта:**
```http
POST /api/v1/quality/check-project
Content-Type: application/json

{
    "project_path": ".",
    "exclude_patterns": ["backup_*", "*.pyc"]
}
```

**Ответ:**
```json
{
    "success": true,
    "project_path": ".",
    "overall_score": 95.2,
    "files_checked": 25,
    "total_errors": 3,
    "duration": 2.15
}
```

### **2. Configuration Manager API**

#### **Получение конфигурации:**
```http
GET /api/v1/config/get
Authorization: Bearer <token>
```

**Ответ:**
```json
{
    "success": true,
    "config": {
        "security_level": "high",
        "family_mode": true,
        "mobile_support": true,
        "ai_analysis": true
    }
}
```

#### **Установка конфигурации:**
```http
POST /api/v1/config/set
Content-Type: application/json
Authorization: Bearer <token>

{
    "key": "security_level",
    "value": "maximum",
    "description": "Максимальный уровень безопасности"
}
```

**Ответ:**
```json
{
    "success": true,
    "message": "Конфигурация обновлена",
    "key": "security_level",
    "value": "maximum"
}
```

### **3. Database Manager API**

#### **Добавление события безопасности:**
```http
POST /api/v1/database/security-event
Content-Type: application/json
Authorization: Bearer <token>

{
    "event_type": "threat_detected",
    "severity": "HIGH",
    "description": "Обнаружена подозрительная активность",
    "source": "firewall",
    "event_data": {
        "ip_address": "192.168.1.100",
        "port": 8080,
        "protocol": "TCP"
    }
}
```

**Ответ:**
```json
{
    "success": true,
    "event_id": "evt_001",
    "message": "Событие безопасности добавлено"
}
```

#### **Получение событий безопасности:**
```http
GET /api/v1/database/security-events?limit=10&severity=HIGH
Authorization: Bearer <token>
```

**Ответ:**
```json
{
    "success": true,
    "events": [
        {
            "id": "evt_001",
            "event_type": "threat_detected",
            "severity": "HIGH",
            "description": "Обнаружена подозрительная активность",
            "source": "firewall",
            "timestamp": "2025-09-08T01:51:00Z",
            "resolved": false
        }
    ],
    "total": 1,
    "limit": 10
}
```

### **4. Security Base API**

#### **Добавление правила безопасности:**
```http
POST /api/v1/security/rule
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "block_suspicious_ip",
    "rule_type": "firewall",
    "enabled": true,
    "conditions": {
        "ip_address": "192.168.1.100",
        "port": 8080
    },
    "actions": ["block", "log", "alert"]
}
```

**Ответ:**
```json
{
    "success": true,
    "rule_id": "rule_001",
    "message": "Правило безопасности добавлено"
}
```

#### **Обработка события безопасности:**
```http
POST /api/v1/security/process-event
Content-Type: application/json
Authorization: Bearer <token>

{
    "event_id": "evt_001",
    "event_type": "threat_detected",
    "severity": "HIGH",
    "description": "Обнаружена подозрительная активность",
    "source": "firewall"
}
```

**Ответ:**
```json
{
    "success": true,
    "processed": true,
    "actions_taken": ["blocked", "logged", "alerted"],
    "rules_triggered": ["rule_001"]
}
```

---

## 📱 МОБИЛЬНЫЙ API

### **Базовый URL:** `http://localhost:8000/mobile/api/v1`

#### **Аутентификация мобильного устройства:**
```http
POST /mobile/api/v1/auth/device
Content-Type: application/json

{
    "device_id": "mobile_001",
    "device_type": "android",
    "app_version": "1.0.0",
    "family_id": "family_001"
}
```

**Ответ:**
```json
{
    "success": true,
    "device_token": "device_token_123",
    "expires_in": 3600,
    "permissions": ["read", "notify"]
}
```

#### **Push-уведомления:**
```http
POST /mobile/api/v1/notifications/send
Content-Type: application/json
Authorization: Bearer <device_token>

{
    "title": "Обнаружена угроза",
    "message": "Подозрительная активность на устройстве",
    "priority": "high",
    "action": "view_details"
}
```

**Ответ:**
```json
{
    "success": true,
    "notification_id": "notif_001",
    "sent_at": "2025-09-08T01:51:00Z"
}
```

#### **Офлайн режим:**
```http
GET /mobile/api/v1/offline/data
Authorization: Bearer <device_token>
```

**Ответ:**
```json
{
    "success": true,
    "offline_data": {
        "security_rules": [...],
        "blocked_sites": [...],
        "family_settings": {...}
    },
    "last_sync": "2025-09-08T01:50:00Z"
}
```

---

## 🔐 АУТЕНТИФИКАЦИЯ И БЕЗОПАСНОСТЬ

### **Получение JWT токена:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "secure_password_123"
}
```

**Ответ:**
```json
{
    "success": true,
    "access_token": "jwt_token_123",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "refresh_token_123"
}
```

### **Обновление токена:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
    "refresh_token": "refresh_token_123"
}
```

**Ответ:**
```json
{
    "success": true,
    "access_token": "new_jwt_token_123",
    "expires_in": 3600
}
```

---

## 📊 МОНИТОРИНГ И МЕТРИКИ

### **Получение статистики системы:**
```http
GET /api/v1/monitoring/stats
Authorization: Bearer <token>
```

**Ответ:**
```json
{
    "success": true,
    "stats": {
        "total_events": 150,
        "active_threats": 3,
        "blocked_attacks": 25,
        "system_uptime": "2d 5h 30m",
        "performance_score": 95.2
    }
}
```

### **Получение логов:**
```http
GET /api/v1/monitoring/logs?level=ERROR&limit=50
Authorization: Bearer <token>
```

**Ответ:**
```json
{
    "success": true,
    "logs": [
        {
            "timestamp": "2025-09-08T01:51:00Z",
            "level": "ERROR",
            "component": "firewall",
            "message": "Ошибка блокировки IP",
            "details": {...}
        }
    ],
    "total": 1,
    "limit": 50
}
```

---

## ⚠️ КОДЫ ОШИБОК

### **HTTP статус коды:**
- **200** - Успешный запрос
- **201** - Ресурс создан
- **400** - Неверный запрос
- **401** - Не авторизован
- **403** - Доступ запрещен
- **404** - Ресурс не найден
- **500** - Внутренняя ошибка сервера

### **Коды ошибок API:**
```json
{
    "success": false,
    "error_code": "AUTH_001",
    "error_message": "Неверные учетные данные",
    "details": "Пользователь не найден или пароль неверный"
}
```

**Основные коды ошибок:**
- **AUTH_001** - Ошибка аутентификации
- **AUTH_002** - Токен истек
- **AUTH_003** - Недостаточно прав
- **CONFIG_001** - Ошибка конфигурации
- **DB_001** - Ошибка базы данных
- **SECURITY_001** - Ошибка безопасности

---

## 🧪 ТЕСТИРОВАНИЕ API

### **Быстрый тест API:**
```bash
# Тест аутентификации
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Тест проверки качества
curl -X POST http://localhost:8000/api/v1/quality/check-file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"file_path": "core/base.py"}'
```

### **Автоматическое тестирование:**
```python
import requests

# Базовый URL
BASE_URL = "http://localhost:8000/api/v1"

# Аутентификация
auth_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = auth_response.json()["access_token"]

# Заголовки для авторизованных запросов
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Тест проверки качества
quality_response = requests.post(
    f"{BASE_URL}/quality/check-file",
    headers=headers,
    json={"file_path": "core/base.py"}
)

print(f"Качество кода: {quality_response.json()['overall_score']}/100")
```

---

## 📈 ПРОИЗВОДИТЕЛЬНОСТЬ API

### **Метрики производительности:**
- **Время ответа:** < 100ms для простых запросов
- **Время ответа:** < 1s для сложных запросов
- **Пропускная способность:** 1000+ запросов/секунду
- **Доступность:** 99.9%

### **Оптимизация:**
- **Кэширование** часто используемых данных
- **Параллельная обработка** запросов
- **Асинхронные операции** для длительных задач
- **Сжатие** ответов (gzip)

---

## 🔧 НАСТРОЙКА И РАЗВЕРТЫВАНИЕ

### **Переменные окружения:**
```bash
# Основные настройки
export ALADDIN_API_HOST=0.0.0.0
export ALADDIN_API_PORT=8000
export ALADDIN_DEBUG=False

# База данных
export ALADDIN_DB_PATH=aladdin.db
export ALADDIN_DB_BACKUP=True

# Безопасность
export ALADDIN_JWT_SECRET=your_secret_key_here
export ALADDIN_ENCRYPTION_KEY=your_encryption_key_here
```

### **Docker развертывание:**
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "scripts/api_server.py"]
```

---

## 📞 ПОДДЕРЖКА API

### **Контакты:**
- **Email:** api-support@aladdin-security.com
- **Документация:** docs.aladdin-security.com
- **GitHub:** github.com/aladdin-security/api
- **Slack:** aladdin-security.slack.com

### **Версионирование:**
- **Текущая версия:** v1.0
- **Поддержка:** 2 года
- **Обратная совместимость:** Да
- **Планы обновления:** Ежеквартально

---

*API документация создана автоматически системой ALADDIN v1.0*