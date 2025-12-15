# 📋 ENDPOINTS ДЛЯ ДОБАВЛЕНИЯ В API GATEWAY

**Дата:** 2025-11-26  
**Цель:** Добавить 7 endpoints для мониторинга и алертов

---

## 📊 ТЕКУЩАЯ СИТУАЦИЯ

**Текущее количество endpoints в API Gateway:** Проверяется

**Нужно добавить:** 7 endpoints

---

## ✅ ENDPOINTS ДЛЯ ДОБАВЛЕНИЯ

### 1. `/api/metrics` - Все метрики
- Метод: GET
- Описание: Получить все метрики системы

### 2. `/api/metrics/cpu` - Метрики CPU
- Метод: GET
- Описание: Получить метрики CPU

### 3. `/api/metrics/ram` - Метрики RAM
- Метод: GET
- Описание: Получить метрики RAM

### 4. `/api/metrics/disk` - Метрики диска
- Метод: GET
- Описание: Получить метрики диска

### 5. `/api/alerts` - Все алерты
- Метод: GET
- Описание: Получить все алерты

### 6. `/api/alerts/active` - Активные алерты
- Метод: GET
- Описание: Получить активные алерты

### 7. `/api/health` - Здоровье системы
- Метод: GET
- Описание: Получить общее здоровье системы

---

## 🔧 ЧТО НУЖНО ДОБАВИТЬ В КОД

### 1. Импорты (в начало файла):
```python
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager
```

### 2. Глобальные переменные (после создания app):
```python
monitor_manager = None
alert_manager = None
```

### 3. Инициализация при старте:
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

### 4. 7 endpoints (перед `if __name__ == "__main__"`)

---

**ИТОГО:** 7 новых endpoints

