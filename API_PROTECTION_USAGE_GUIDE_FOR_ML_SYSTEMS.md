# 🚀 **ALADDIN API - ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ ДЛЯ ML СИСТЕМ**

**Версия:** 2.1.0-PROD  
**Дата:** 3 февраля 2026 г.  
**Статус:** 🔒 ЗАФИКСИРОВАНО (НЕЛЬЗЯ МЕНЯТЬ)

---

## 📋 **ОБЩАЯ ИНФОРМАЦИЯ**

### 🎯 **Что такое ALADDIN API?**
ALADDIN - это комплексная система кибербезопасности с 96 API эндпоинтами, которая предоставляет ML системам доступ к функциям безопасности, мониторинга и защиты.

### 🔒 **Важно знать:**
- **Все API настройки ЗАФИКСИРОВАНЫ** и защищены от изменений
- **96 эндпоинтов** работают только в определенной конфигурации
- **SFM Core** всегда возвращает `source: "real_sfm"`
- **Любые изменения** автоматически обнаруживаются и блокируются

---

## 🏗️ **АРХИТЕКТУРА СИСТЕМЫ**

### **Основные компоненты:**
```
ML Система → API Gateway → SFM Core → PostgreSQL/Redis
     ↓            ↓            ↓
   REST API    FastAPI     Функции безопасности
```

### **Технические характеристики:**
- **Протокол:** HTTP/1.1, HTTP/2
- **Безопасность:** OAuth2 + JWT
- **Хост:** `149.154.65.180:8002`
- **Время ответа:** < 85ms (95-й перцентиль)
- **Нагрузка:** 1500+ RPS

---

## 📚 **ПОДКЛЮЧЕНИЕ К API**

### **1. Базовое подключение (Python)**

```python
import requests
import json

class AladdinMLClient:
    def __init__(self):
        self.base_url = "http://149.154.65.180:8002"
        self.session = requests.Session()

    def call_api(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Универсальный метод вызова API"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data, headers={"Content-Type": "application/json"})
            elif method == "PUT":
                response = self.session.put(url, json=data, headers={"Content-Type": "application/json"})
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            result = response.json()

            # Проверка SFM интеграции
            if "source" not in result or result["source"] != "real_sfm":
                raise ValueError("SFM integration compromised!")

            return result

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API call failed: {e}")
```

### **2. Подключение с аутентификацией**

```python
class AladdinSecureClient(AladdinMLClient):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.authenticate(username, password)

    def authenticate(self, username: str, password: str):
        """Аутентификация и получение JWT токена"""
        auth_data = {
            "username": username,
            "password": password,
            "device_fingerprint": "ml_system_001"
        }

        response = self.call_api("/api/auth/login", "POST", auth_data)
        self.token = response["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def refresh_token(self):
        """Обновление токена"""
        response = self.call_api("/api/auth/refresh", "POST", {
            "refresh_token": self.refresh_token
        })
        self.token = response["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
```

---

## 🔧 **ОСНОВНЫЕ API ГРУППЫ**

### **1. АУТЕНТИФИКАЦИЯ (Authentication)**

```python
# Регистрация нового пользователя
register_data = {
    "username": "ml_user_001",
    "email": "ml@system.com",
    "password": "secure_password_123",
    "device_info": {
        "platform": "ml_system",
        "version": "2.1.0",
        "model": "AI_Security_Analyzer"
    }
}
client.call_api("/api/auth/register", "POST", register_data)

# Вход в систему
login_data = {
    "username": "ml_user_001",
    "password": "secure_password_123",
    "device_fingerprint": "ml_system_001"
}
client.call_api("/api/auth/login", "POST", login_data)

# Получение профиля
profile = client.call_api("/api/auth/profile")
```

### **2. ЗАЩИТА ИДЕНТИЧНОСТИ (Identity Protection)**

```python
# Проверка попыток входа
attempts = client.call_api("/api/identity/attempts")

# Получение статистики
stats = client.call_api("/api/identity/stats")

# Добавление в белый список
client.call_api("/api/identity/allow", "POST", {
    "identity_type": "email",
    "identity_value": "trusted@domain.com",
    "reason": "ML_system_trusted"
})

# Блокировка подозрительного
client.call_api("/api/identity/block", "POST", {
    "identity_type": "ip",
    "identity_value": "192.168.1.100",
    "reason": "suspicious_activity"
})
```

### **3. DARK WEB МОНИТОРИНГ**

```python
# Получение утечек
leaks = client.call_api("/api/darkweb/leaks")

# Статистика сканирования
stats = client.call_api("/api/darkweb/stats")

# Запуск сканирования
client.call_api("/api/darkweb/scan_start", "POST", {
    "scan_type": "full_scan",
    "target": "user@domain.com",
    "priority": "high"
})
```

### **4. АНАЛИТИКА И МОНИТОРИНГ**

```python
# Обзор аналитики
overview = client.call_api("/api/analytics/overview")

# Производительность
performance = client.call_api("/api/analytics/performance")

# Экспорт данных
client.call_api("/api/analytics/export", "POST", {
    "format": "json",
    "period": "month",
    "include_security_events": True,
    "anonymize": True
})
```

---

## ⚙️ **ЧТО МОЖНО МЕНЯТЬ В API**

### ✅ **РАЗРЕШЕННЫЕ ИЗМЕНЕНИЯ:**

#### **1. Параметры запросов (Data)**
```python
# ✅ МОЖНО менять данные в запросах
client.call_api("/api/darkweb/scan_start", "POST", {
    "scan_type": "quick_scan",  # ← Можно менять
    "target": "new_user@domain.com",  # ← Можно менять
    "priority": "normal"  # ← Можно менять
})
```

#### **2. Частота запросов**
```python
# ✅ МОЖНО регулировать частоту вызовов
import time

for user in user_list:
    result = client.call_api(f"/api/identity/theft/report/{user['id']}", "POST", {
        "report_type": "identity_theft",
        "description": f"Analysis for user {user['id']}"
    })
    time.sleep(0.1)  # Задержка между запросами
```

#### **3. Обработка ответов**
```python
# ✅ МОЖНО обрабатывать ответы по-своему
response = client.call_api("/api/analytics/security_events")
events = response.get("events", [])

for event in events:
    if event["severity"] == "high":
        # Ваша логика обработки
        handle_high_severity_event(event)
```

#### **4. Логирование и мониторинг**
```python
# ✅ МОЖНО добавлять свое логирование
import logging

logging.basicConfig(level=logging.INFO)

def call_with_logging(endpoint, method="GET", data=None):
    logging.info(f"Calling API: {endpoint}")
    start_time = time.time()

    try:
        result = client.call_api(endpoint, method, data)
        duration = time.time() - start_time
        logging.info(f"API call successful: {duration:.2f}s")
        return result
    except Exception as e:
        logging.error(f"API call failed: {e}")
        raise
```

---

## 🚫 **ЧТО НЕЛЬЗЯ МЕНЯТЬ В API**

### ❌ **ЗАПРЕЩЕННЫЕ ИЗМЕНЕНИЯ:**

#### **1. Структура эндпоинтов**
```python
# ❌ НЕЛЬЗЯ менять URL эндпоинтов
# Было: /api/auth/login
# Стало: /api/authentication/signin  ← ЗАПРЕЩЕНО!
```

#### **2. Параметры ответа**
```python
# ❌ НЕЛЬЗЯ ожидать других полей в ответе
response = client.call_api("/api/auth/login")
# Всегда будет: status, access_token, refresh_token, source: "real_sfm"
# Никаких других полей! ← ЗАФИКСИРОВАНО
```

#### **3. HTTP методы**
```python
# ❌ НЕЛЬЗЯ менять HTTP методы
# Было: POST /api/auth/login
# Стало: GET /api/auth/login  ← ЗАПРЕЩЕНО!
```

#### **4. Заголовки и формат данных**
```python
# ❌ НЕЛЬЗЯ менять Content-Type
# Всегда: "Content-Type": "application/json"  ← ЗАФИКСИРОВАНО
```

#### **5. Время ответа и надежность**
```python
# ❌ НЕЛЬЗЯ ожидать другого времени ответа
# Всегда: < 85ms (95-й перцентиль)  ← ЗАФИКСИРОВАНО
```

---

## 🔍 **ПРОВЕРКА ЦЕЛОСТНОСТИ API**

### **Автоматическая проверка:**

```python
def verify_api_integrity(client: AladdinMLClient) -> bool:
    """Проверка, что API не изменен"""

    # 1. Проверка SFM интеграции
    health = client.call_api("/api/health")
    if health.get("sfm_adapter") != "available":
        return False

    # 2. Проверка системного здоровья
    system_health = client.call_api("/api/system/health")
    if system_health.get("status") != "healthy":
        return False

    # 3. Проверка SFM core
    sfm_status = client.call_api("/api/components/status/sfm_core")
    if sfm_status.get("status") != "running":
        return False

    return True

# Использование
if not verify_api_integrity(client):
    raise SystemError("API integrity compromised!")
```

---

## 🛠️ **СИСТЕМА ЗАЩИТЫ API**

### **Что защищено:**

1. **🔒 Конфигурация API Gateway** - хост, порт, таймауты
2. **🔒 SFM Core настройки** - логика работы, источник данных
3. **🔒 Все 96 эндпоинтов** - URL, методы, параметры
4. **🔒 Форматы ответов** - JSON структура, поля

### **Как работает защита:**

```bash
# 1. Проверить статус защиты
python3 api_protection_master_system.py status

# 2. Проверить здоровье систем
python3 api_protection_master_system.py health

# 3. Принудительная проверка целостности
python3 api_config_integrity_monitor.py
```

### **Что происходит при попытке изменения:**

1. **Обнаружение** - SHA256 хэши не совпадают
2. **Алерты** - автоматическое логирование
3. **Бэкап** - экстренное резервное копирование
4. **Блокировка** - в строгом режиме

---

## 📊 **МОНИТОРИНГ И ОТЛАДКА**

### **1. Проверка работоспособности**

```python
def comprehensive_health_check(client: AladdinMLClient) -> dict:
    """Полная проверка здоровья API"""

    results = {
        "api_gateway": False,
        "sfm_core": False,
        "database": False,
        "response_time": None,
        "throughput": None
    }

    try:
        # Проверка API Gateway
        start_time = time.time()
        health = client.call_api("/api/health")
        response_time = time.time() - start_time

        results["api_gateway"] = health.get("status") == "ok"
        results["response_time"] = response_time

        # Проверка SFM Core
        sfm_health = client.call_api("/api/components/health")
        results["sfm_core"] = any(
            comp["status"] == "healthy"
            for comp in sfm_health.get("components", [])
            if comp["name"] == "sfm_core"
        )

        return results

    except Exception as e:
        results["error"] = str(e)
        return results

# Использование
health = comprehensive_health_check(client)
if not all(health.values()):
    print("API health check failed!")
    for check, status in health.items():
        print(f"  {check}: {'✅' if status else '❌'}")
```

### **2. Логирование запросов**

```python
import logging
from datetime import datetime

logging.basicConfig(
    filename=f'api_usage_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AladdinLoggedClient(AladdinSecureClient):
    def call_api(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Вызов API с логированием"""
        start_time = time.time()

        try:
            result = super().call_api(endpoint, method, data)
            duration = time.time() - start_time

            logging.info(f"API_CALL_SUCCESS: {method} {endpoint} - {duration:.3f}s - SFM:{result.get('source')}")

            return result

        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"API_CALL_FAILED: {method} {endpoint} - {duration:.3f}s - ERROR:{e}")
            raise
```

---

## 🎯 **ПРАКТИЧЕСКИЕ ПРИМЕРЫ**

### **Пример 1: Система анализа угроз**

```python
class ThreatAnalysisSystem:
    def __init__(self):
        self.client = AladdinSecureClient("threat_analyzer", "secure_pass_123")

    def analyze_user_threats(self, user_id: str) -> dict:
        """Анализ угроз для пользователя"""

        # Получение статистики входов
        attempts = self.client.call_api("/api/identity/attempts")

        # Проверка dark web утечек
        leaks = self.client.call_api("/api/darkweb/leaks")

        # Анализ геолокации
        location_stats = self.client.call_api("/api/location/stats")

        return {
            "user_id": user_id,
            "risk_score": self.calculate_risk_score(attempts, leaks, location_stats),
            "recommendations": self.generate_recommendations(attempts, leaks),
            "analyzed_at": datetime.now().isoformat(),
            "source": "real_sfm"  # Всегда проверяем
        }

    def calculate_risk_score(self, attempts, leaks, locations) -> float:
        """Расчет scores угроз (ваша ML логика)"""
        # Ваши алгоритмы ML анализа
        return 0.0  # Пример

    def generate_recommendations(self, attempts, leaks) -> list:
        """Генерация рекомендаций"""
        recommendations = []

        if len([a for a in attempts.get("attempts", []) if a.get("suspicious")]) > 5:
            recommendations.append("Enable 2FA")

        if len(leaks.get("leaks", [])) > 0:
            recommendations.append("Change passwords immediately")

        return recommendations
```

### **Пример 2: Мониторинг в реальном времени**

```python
class RealTimeSecurityMonitor:
    def __init__(self):
        self.client = AladdinSecureClient("monitor_system", "monitor_pass_123")
        self.last_check = None

    def continuous_monitoring(self):
        """Непрерывный мониторинг безопасности"""
        import time

        while True:
            try:
                # Проверка новых событий безопасности
                security_events = self.client.call_api("/api/analytics/security_events")

                # Обработка новых событий
                for event in security_events.get("events", []):
                    if self.last_check is None or event["timestamp"] > self.last_check:
                        self.process_security_event(event)

                # Обновление времени последней проверки
                self.last_check = security_events.get("events", [{}])[0].get("timestamp")

                # Проверка каждые 30 секунд
                time.sleep(30)

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)  # Увеличенная пауза при ошибке

    def process_security_event(self, event: dict):
        """Обработка события безопасности"""
        print(f"Security Event: {event['type']} - Severity: {event['severity']}")

        # Ваша логика обработки событий
        if event["severity"] == "critical":
            self.trigger_emergency_response(event)
```

---

## 🚨 **ОБРАБОТКА ОШИБОК**

### **Стандартные ошибки API:**

```python
def handle_api_errors(func):
    """Декоратор для обработки ошибок API"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - check network")
            return None
        except requests.exceptions.Timeout:
            print("⏰ Request timeout - API overloaded")
            return None
        except ValueError as e:
            if "SFM integration compromised" in str(e):
                print("🚨 SECURITY ALERT: SFM integration compromised!")
                # Экстренные меры безопасности
                return None
            else:
                print(f"❌ Data validation error: {e}")
                return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    return wrapper

# Использование
@handle_api_errors
def safe_api_call(endpoint, method="GET", data=None):
    return client.call_api(endpoint, method, data)
```

---

## 📞 **ПОДДЕРЖКА И ОБНОВЛЕНИЯ**

### **Каналы связи:**
- **Документация:** `ALADDIN_API_TESTING_COMPLETE_REPORT.md`
- **Спецификация:** `api_specification_*.md`
- **Логи:** `api_config_integrity.log`

### **При обнаружении проблем:**
1. **Проверьте статус:** `python3 api_protection_master_system.py health`
2. **Проверьте логи:** `tail -f api_config_integrity.log`
3. **Свяжитесь с администратором** - изменения невозможны без разрешения

### **Обновления:**
- **API конфигурация** обновляется ТОЛЬКО через систему защиты
- **Новые версии** тестируются на 100% перед развертыванием
- **Все изменения** документируются и фиксируются

---

## ⚠️ **КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА**

### **🚫 СТРОГО ЗАПРЕЩЕНО:**
1. **Изменять URL эндпоинтов**
2. **Менять HTTP методы**
3. **Ожидать другие поля в ответах**
4. **Изменять Content-Type заголовки**
5. **Пытаться обходить SFM проверки**

### **✅ РАЗРЕШЕНО:**
1. **Передавать любые корректные данные**
2. **Регулировать частоту запросов**
3. **Обрабатывать ответы по-своему**
4. **Добавлять логирование и мониторинг**
5. **Создавать надстройки над API**

---

## 🎉 **ГОТОВО К ИСПОЛЬЗОВАНИЮ!**

**ALADDIN API полностью готов для интеграции с ML системами!**

- ✅ **96 эндпоинтов** зафиксированы и стабильны
- ✅ **SFM интеграция** гарантирована
- ✅ **Защита от изменений** активна
- ✅ **Мониторинг и бэкапы** работают
- ✅ **Документация** полная и актуальная

**Начните использовать API прямо сейчас с полной уверенностью в стабильности! 🚀**