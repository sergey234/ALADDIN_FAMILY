# 📋 ПЛАН: ДОБАВЛЕНИЕ ENDPOINTS В API GATEWAY

**Дата:** 2025-11-26  
**Цель:** Добавить 7 endpoints для мониторинга и алертов

---

## 📊 ТЕКУЩАЯ СИТУАЦИЯ

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`

**Статус:** Восстановлен из backup (чистое состояние)

**Текущие endpoints в API Gateway:** Проверяется

**58 endpoints** - это общее количество в системе (включая Payment Service)

---

## ✅ ЧТО НУЖНО ДОБАВИТЬ

### 7 новых endpoints:

1. **GET /api/metrics** - Все метрики системы
2. **GET /api/metrics/cpu** - Метрики CPU
3. **GET /api/metrics/ram** - Метрики RAM
4. **GET /api/metrics/disk** - Метрики диска
5. **GET /api/alerts** - Все алерты
6. **GET /api/alerts/active** - Активные алерты
7. **GET /api/health** - Здоровье системы

---

## 🔧 КАК ДОБАВИТЬ (БЕЗ СКРИПТОВ)

### Шаг 1: Добавить импорты
В начало файла (после других импортов):
```python
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager
```

### Шаг 2: Добавить глобальные переменные
После создания `app`:
```python
monitor_manager = None
alert_manager = None
```

### Шаг 3: Добавить инициализацию
После создания `app`:
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
        logger.info("✅ Мониторинг и алерты инициализированы")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации мониторинга: {e}")
```

### Шаг 4: Добавить 7 endpoints
Перед строкой `if __name__ == "__main__":`

---

**ИТОГО:** 7 новых endpoints + импорты + инициализация

**Время:** 15-30 минут (вручную)

