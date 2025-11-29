# 🔗 ПОШАГОВЫЙ ПЛАН ИНТЕГРАЦИИ СИСТЕМЫ МОНИТОРИНГА

**Дата:** 2025-11-26  
**Цель:** Подключить систему мониторинга для просмотра статистики

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### 1. Добавить endpoints в API Gateway ✅

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`

**Что добавить:**

```python
# В начале файла (импорты)
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager

# После создания app
monitor_manager = None
alert_manager = None

# Инициализация при старте
@app.on_event("startup")
async def startup_event():
    global monitor_manager, alert_manager
    config = MonitorConfig(collection_interval=30)
    monitor_manager = MonitorManager(config)
    await monitor_manager.initialize()
    await monitor_manager.start()
    
    alert_manager = AlertManager()
    await alert_manager.start_alert_processing()

# Endpoints
@app.get("/api/metrics")
async def get_metrics():
    """Получить все метрики системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    return {"metrics": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat(), "status": m.status.value} for m in metrics]}

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """Получить метрики CPU"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    cpu_metrics = [m for m in metrics if 'cpu' in m.name.lower()]
    return {"cpu": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in cpu_metrics]}

@app.get("/api/metrics/ram")
async def get_ram_metrics():
    """Получить метрики RAM"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    ram_metrics = [m for m in metrics if 'ram' in m.name.lower() or 'memory' in m.name.lower()]
    return {"ram": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in ram_metrics]}

@app.get("/api/metrics/disk")
async def get_disk_metrics():
    """Получить метрики диска"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    disk_metrics = [m for m in metrics if 'disk' in m.name.lower()]
    return {"disk": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in disk_metrics]}

@app.get("/api/alerts")
async def get_alerts():
    """Получить все алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_active_alerts()
    return {"alerts": [{"id": a.id, "severity": a.severity.value, "message": a.message, "timestamp": a.timestamp.isoformat(), "resolved": a.resolved} for a in alerts]}

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Получить активные алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_active_alerts()
    active = [a for a in alerts if not a.resolved]
    return {"active_alerts": [{"id": a.id, "severity": a.severity.value, "message": a.message, "timestamp": a.timestamp.isoformat()} for a in active]}

@app.get("/api/health")
async def get_health():
    """Получить общее здоровье системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    status = await monitor_manager.get_system_status()
    return status
```

**Время:** 1-2 часа

---

### 2. Зарегистрировать в SFM ✅

**Файл:** `/opt/aladdin-backend/data/sfm/function_registry.json`

**Что добавить:**

```json
{
  "functions": {
    "monitor.get_metrics": {
      "module": "security.managers.monitor_manager",
      "function": "MonitorManager.get_metrics",
      "description": "Получить все метрики системы",
      "category": "monitoring",
      "dependencies": []
    },
    "monitor.get_alerts": {
      "module": "security.managers.alert_manager",
      "function": "AlertManager.get_active_alerts",
      "description": "Получить активные алерты",
      "category": "monitoring",
      "dependencies": []
    },
    "monitor.get_system_status": {
      "module": "security.managers.monitor_manager",
      "function": "MonitorManager.get_system_status",
      "description": "Получить общее здоровье системы",
      "category": "monitoring",
      "dependencies": []
    }
  }
}
```

**Время:** 30 минут

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
    console.log('CPU:', data.metrics.find(m => m.name.includes('cpu')));
    console.log('RAM:', data.metrics.find(m => m.name.includes('ram')));
    console.log('Disk:', data.metrics.find(m => m.name.includes('disk')));
  });
```

---

### Вариант 2: Через веб-интерфейс ⚠️

**Создать HTML страницу:**
- `/dashboard` - дашборд с графиками
- Использовать Chart.js для графиков

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
# Response: {"metrics": [{"name": "cpu_percent", "value": 45.2, "timestamp": "...", "status": "healthy"}, ...]}

GET /api/metrics/cpu
# Возвращает метрики CPU
# Response: {"cpu": [{"name": "cpu_percent", "value": 45.2, "timestamp": "..."}]}

GET /api/metrics/ram
# Возвращает метрики RAM
# Response: {"ram": [{"name": "memory_percent", "value": 65.3, "timestamp": "..."}]}

GET /api/metrics/disk
# Возвращает метрики диска
# Response: {"disk": [{"name": "disk_percent", "value": 35.1, "timestamp": "..."}]}
```

### Endpoints для алертов:

```python
GET /api/alerts
# Возвращает все алерты
# Response: {"alerts": [{"id": "...", "severity": "high", "message": "...", "timestamp": "...", "resolved": false}]}

GET /api/alerts/active
# Возвращает активные алерты
# Response: {"active_alerts": [{"id": "...", "severity": "critical", "message": "...", "timestamp": "..."}]}
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
1. ✅ Добавить endpoints в API Gateway
2. ✅ Зарегистрировать функции в SFM
3. ✅ Протестировать endpoints

### В ближайшее время:
4. ⚠️ Создать веб-интерфейс (опционально)
5. ⚠️ Добавить экран мониторинга в мобильное приложение (опционально)

---

## ✅ ИТОГ

**Что нужно сделать:**
1. ✅ Добавить endpoints в API Gateway (код выше)
2. ✅ Зарегистрировать функции в SFM (JSON выше)
3. ⚠️ Создать веб-интерфейс (опционально)

**Как видеть статистику:**
- ✅ Через API: `GET https://aladdin-ai.ru/api/metrics`
- ⚠️ Через веб-интерфейс: `/dashboard` (если создать)
- ⚠️ Через мобильное приложение (если добавить экран)

---

**План готов! Начинаем интеграцию!** 🚀

