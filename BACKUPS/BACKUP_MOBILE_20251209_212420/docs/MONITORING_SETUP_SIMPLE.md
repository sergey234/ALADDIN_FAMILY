# 📊 ПРОСТОЕ РУКОВОДСТВО: КАК ВИДЕТЬ СТАТИСТИКУ СИСТЕМЫ

**Дата:** 2025-11-26  
**Цель:** Подключить систему мониторинга для просмотра статистики

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ (3 ШАГА)

### Шаг 1: Добавить endpoints в API Gateway ✅

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`

**Что добавить:**

1. **Импорты (в начале файла):**
```python
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager
```

2. **Глобальные переменные (после создания app):**
```python
monitor_manager = None
alert_manager = None
```

3. **Инициализация (добавить функцию):**
```python
@app.on_event("startup")
async def startup_event():
    global monitor_manager, alert_manager
    try:
        config = MonitorConfig(collection_interval=30)
        monitor_manager = MonitorManager(config)
        await monitor_manager.initialize()
        await monitor_manager.start()
        
        alert_manager = AlertManager()
        await alert_manager.start_alert_processing()
        logger.info("✅ Мониторинг инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
```

4. **Endpoints (добавить в конец файла):**
```python
@app.get("/api/metrics")
async def get_metrics():
    """Получить все метрики"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    metrics = await monitor_manager.get_metrics()
    return {"metrics": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat(), "status": m.status.value} for m in metrics]}

@app.get("/api/alerts")
async def get_alerts():
    """Получить все алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_active_alerts()
    return {"alerts": [{"id": a.id, "severity": a.severity.value, "message": a.message, "timestamp": a.timestamp.isoformat()} for a in alerts]}

@app.get("/api/health")
async def get_health():
    """Получить здоровье системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    status = await monitor_manager.get_system_status()
    return status
```

**Время:** 30 минут

---

### Шаг 2: Перезапустить API Gateway ✅

```bash
systemctl restart aladdin-api-gateway
systemctl status aladdin-api-gateway
```

**Время:** 1 минута

---

### Шаг 3: Протестировать ✅

```bash
# Получить метрики
curl https://aladdin-ai.ru/api/metrics

# Получить алерты
curl https://aladdin-ai.ru/api/alerts

# Получить здоровье системы
curl https://aladdin-ai.ru/api/health
```

**Время:** 5 минут

---

## 🔍 КАК ВИДЕТЬ СТАТИСТИКУ

### Вариант 1: Через API (JSON) ✅

**Самый простой способ:**

```bash
# Получить все метрики
curl https://aladdin-ai.ru/api/metrics | jq

# Получить алерты
curl https://aladdin-ai.ru/api/alerts | jq

# Получить здоровье системы
curl https://aladdin-ai.ru/api/health | jq
```

**Что вы увидите:**

```json
{
  "metrics": [
    {
      "name": "cpu_percent",
      "value": 45.2,
      "timestamp": "2025-11-26T12:00:00",
      "status": "healthy"
    },
    {
      "name": "memory_percent",
      "value": 65.3,
      "timestamp": "2025-11-26T12:00:00",
      "status": "healthy"
    }
  ]
}
```

---

### Вариант 2: Через браузер ✅

**Откройте в браузере:**

```
https://aladdin-ai.ru/api/metrics
https://aladdin-ai.ru/api/alerts
https://aladdin-ai.ru/api/health
```

**Что вы увидите:**
- JSON с метриками
- JSON с алертами
- JSON с здоровьем системы

---

### Вариант 3: Через веб-интерфейс (опционально) ⚠️

**Если хотите красивые графики:**

1. Создать HTML страницу с графиками (Chart.js)
2. Добавить endpoint `/dashboard`
3. Открыть в браузере: `https://aladdin-ai.ru/dashboard`

**Время:** 2-3 часа

---

## 📊 ЧТО ВЫ УВИДИТЕ

### Метрики:
- ✅ **CPU** - использование процессора (%)
- ✅ **RAM** - использование памяти (%)
- ✅ **Disk** - использование диска (%)
- ✅ **Network** - сетевая активность

### Алерты:
- ✅ **Активные алерты** - проблемы, требующие внимания
- ✅ **Уровни серьезности** - LOW, MEDIUM, HIGH, CRITICAL
- ✅ **История** - когда произошли алерты

### Здоровье системы:
- ✅ **Общий статус** - healthy, warning, critical
- ✅ **Метрики** - текущие значения
- ✅ **Время** - когда обновлено

---

## ✅ ИТОГ

**Что нужно сделать:**
1. ✅ Добавить endpoints в API Gateway (код выше)
2. ✅ Перезапустить API Gateway
3. ✅ Протестировать через curl или браузер

**Как видеть статистику:**
- ✅ Через API: `https://aladdin-ai.ru/api/metrics`
- ✅ Через браузер: открыть URL выше
- ⚠️ Через веб-интерфейс: создать dashboard (опционально)

**Время на настройку:** 30-60 минут

---

**Готово! Теперь вы можете видеть статистику вместо Prometheus и Grafana!** 🚀

