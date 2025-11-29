# 🔗 ПОЛНЫЙ ПЛАН ИНТЕГРАЦИИ СИСТЕМЫ МОНИТОРИНГА

**Дата:** 2025-11-26  
**Цель:** Подключить систему мониторинга для просмотра статистики вместо Prometheus и Grafana

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### 1. Интегрировать с API Gateway ✅

**Цель:** Создать endpoints для получения статистики

**Что нужно:**
1. Импортировать monitor_manager и alert_manager в API Gateway
2. Создать endpoints для метрик
3. Создать endpoints для алертов
4. Создать endpoint для общего здоровья системы

---

### 2. Зарегистрировать в SFM ✅

**Цель:** Сделать функции доступными через SFM

**Что нужно:**
1. Зарегистрировать функции мониторинга в SFM
2. Обновить function_registry.json

---

### 3. Создать веб-интерфейс (опционально) ⚠️

**Цель:** Визуализация статистики

**Варианты:**
1. **Простой JSON API** - мобильное приложение получает данные
2. **Веб-интерфейс** - HTML страница с графиками
3. **Dashboard** - отдельная страница с виджетами

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН ДЕЙСТВИЙ

### Шаг 1: Интегрировать с API Gateway

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`

**Что добавить:**

```python
# Импорты
from security.managers.monitor_manager import MonitorManager
from security.managers.alert_manager import AlertManager

# Инициализация
monitor_manager = MonitorManager()
alert_manager = AlertManager()

# Endpoints
@app.get("/api/metrics")
async def get_metrics():
    """Получить все метрики"""
    metrics = await monitor_manager.get_metrics()
    return {"metrics": metrics}

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """Получить метрики CPU"""
    metrics = await monitor_manager.get_metrics()
    cpu_metrics = [m for m in metrics if 'cpu' in m.name.lower()]
    return {"cpu": cpu_metrics}

@app.get("/api/metrics/ram")
async def get_ram_metrics():
    """Получить метрики RAM"""
    metrics = await monitor_manager.get_metrics()
    ram_metrics = [m for m in metrics if 'ram' in m.name.lower() or 'memory' in m.name.lower()]
    return {"ram": ram_metrics}

@app.get("/api/metrics/disk")
async def get_disk_metrics():
    """Получить метрики диска"""
    metrics = await monitor_manager.get_metrics()
    disk_metrics = [m for m in metrics if 'disk' in m.name.lower()]
    return {"disk": disk_metrics}

@app.get("/api/alerts")
async def get_alerts():
    """Получить все алерты"""
    alerts = await alert_manager.get_active_alerts()
    return {"alerts": alerts}

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Получить активные алерты"""
    alerts = await alert_manager.get_active_alerts()
    active = [a for a in alerts if not a.resolved]
    return {"active_alerts": active}

@app.get("/api/health")
async def get_health():
    """Получить общее здоровье системы"""
    status = await monitor_manager.get_system_status()
    return status
```

**Время:** 1-2 часа

---

### Шаг 2: Зарегистрировать в SFM

**Файл:** `/opt/aladdin-backend/data/sfm/function_registry.json`

**Что добавить:**

```json
{
  "functions": {
    "monitor.get_metrics": {
      "module": "security.managers.monitor_manager",
      "function": "MonitorManager.get_metrics",
      "description": "Получить все метрики системы",
      "category": "monitoring"
    },
    "monitor.get_alerts": {
      "module": "security.managers.alert_manager",
      "function": "AlertManager.get_active_alerts",
      "description": "Получить активные алерты",
      "category": "monitoring"
    },
    "monitor.get_system_status": {
      "module": "security.managers.monitor_manager",
      "function": "MonitorManager.get_system_status",
      "description": "Получить общее здоровье системы",
      "category": "monitoring"
    }
  }
}
```

**Время:** 30 минут

---

### Шаг 3: Создать веб-интерфейс (опционально)

**Файл:** `/opt/aladdin-backend/security/microservices/dashboard.py` (новый)

**Что создать:**

```python
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Веб-интерфейс для мониторинга"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ALADDIN Monitoring Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>ALADDIN Monitoring Dashboard</h1>
        <div id="metrics"></div>
        <div id="alerts"></div>
        <script>
            // Загрузка метрик
            fetch('/api/metrics')
                .then(res => res.json())
                .then(data => {
                    // Отображение метрик
                    console.log(data);
                });
        </script>
    </body>
    </html>
    """
    return html
```

**Время:** 2-3 часа

---

## 🔍 КАК ВИДЕТЬ СТАТИСТИКУ

### Вариант 1: Через API (JSON) ✅

**Для мобильного приложения:**
```swift
// Получить метрики
GET https://aladdin-ai.ru/api/metrics

// Получить алерты
GET https://aladdin-ai.ru/api/alerts

// Получить здоровье системы
GET https://aladdin-ai.ru/api/health
```

**Для веб-интерфейса:**
```javascript
// Получить метрики
fetch('https://aladdin-ai.ru/api/metrics')
  .then(res => res.json())
  .then(data => {
    console.log('CPU:', data.metrics.cpu);
    console.log('RAM:', data.metrics.ram);
    console.log('Disk:', data.metrics.disk);
  });
```

---

### Вариант 2: Через веб-интерфейс ⚠️

**Создать HTML страницу:**
- `/dashboard` - дашборд с графиками
- `/metrics` - страница с метриками
- `/alerts` - страница с алертами

**Использовать:**
- Chart.js для графиков
- Bootstrap для стилей
- JavaScript для обновления данных

---

### Вариант 3: Через мобильное приложение ⚠️

**Добавить экран мониторинга:**
- `MonitoringScreen.swift` - экран с метриками
- Графики CPU, RAM, диск
- Список алертов

---

## 📊 СТРУКТУРА API

### Endpoints для метрик:

```python
GET /api/metrics
# Возвращает все метрики
# Response: {"metrics": [{"name": "cpu", "value": 45.2, ...}, ...]}

GET /api/metrics/cpu
# Возвращает метрики CPU
# Response: {"cpu": [{"name": "cpu_percent", "value": 45.2, ...}]}

GET /api/metrics/ram
# Возвращает метрики RAM
# Response: {"ram": [{"name": "memory_percent", "value": 65.3, ...}]}

GET /api/metrics/disk
# Возвращает метрики диска
# Response: {"disk": [{"name": "disk_percent", "value": 35.1, ...}]}
```

### Endpoints для алертов:

```python
GET /api/alerts
# Возвращает все алерты
# Response: {"alerts": [{"id": "...", "severity": "high", ...}, ...]}

GET /api/alerts/active
# Возвращает активные алерты
# Response: {"active_alerts": [{"id": "...", "severity": "critical", ...}]}
```

### Endpoint для здоровья:

```python
GET /api/health
# Возвращает общее здоровье системы
# Response: {"status": "healthy", "cpu": 45.2, "ram": 65.3, "disk": 35.1}
```

---

## 🎯 РЕКОМЕНДАЦИИ

### Немедленно:
1. ✅ Интегрировать с API Gateway (добавить endpoints)
2. ✅ Зарегистрировать в SFM
3. ✅ Протестировать endpoints

### В ближайшее время:
4. ⚠️ Создать веб-интерфейс (опционально)
5. ⚠️ Добавить экран мониторинга в мобильное приложение (опционально)

---

## ✅ ИТОГ

**Что нужно сделать:**
1. ✅ Добавить endpoints в API Gateway
2. ✅ Зарегистрировать функции в SFM
3. ⚠️ Создать веб-интерфейс (опционально)

**Как видеть статистику:**
- ✅ Через API: `GET https://aladdin-ai.ru/api/metrics`
- ⚠️ Через веб-интерфейс: `/dashboard` (если создать)
- ⚠️ Через мобильное приложение (если добавить экран)

---

**План готов! Начинаем интеграцию!** 🚀

