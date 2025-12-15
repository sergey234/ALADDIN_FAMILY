# 📝 КОД ДЛЯ ДОБАВЛЕНИЯ В API GATEWAY

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`  
**Место:** Перед строкой `if __name__ == "__main__":`

---

## КОД ДЛЯ ВСТАВКИ:

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

# Endpoints для метрик
@app.get("/api/metrics")
async def get_metrics():
    """Получить все метрики системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    return {
        "metrics": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value,
                "unit": m.unit
            } for m in metrics
        ]
    }

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """Получить метрики CPU"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    cpu_metrics = [m for m in metrics if "cpu" in m.name.lower()]
    return {
        "cpu": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in cpu_metrics
        ]
    }

@app.get("/api/metrics/ram")
async def get_ram_metrics():
    """Получить метрики RAM"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    ram_metrics = [m for m in metrics if "ram" in m.name.lower() or "memory" in m.name.lower()]
    return {
        "ram": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in ram_metrics
        ]
    }

@app.get("/api/metrics/disk")
async def get_disk_metrics():
    """Получить метрики диска"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    metrics = await monitor_manager.get_metrics()
    disk_metrics = [m for m in metrics if "disk" in m.name.lower()]
    return {
        "disk": [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status.value
            } for m in disk_metrics
        ]
    }

# Endpoints для алертов
@app.get("/api/alerts")
async def get_alerts():
    """Получить все алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_alert_history()
    return {
        "alerts": [
            {
                "id": str(a.id) if hasattr(a, "id") else str(a.get("id", "")),
                "severity": a.severity.value if hasattr(a, "severity") else a.get("severity", ""),
                "message": a.message if hasattr(a, "message") else a.get("message", ""),
                "timestamp": a.timestamp.isoformat() if hasattr(a, "timestamp") else a.get("timestamp", ""),
                "resolved": a.resolved if hasattr(a, "resolved") else a.get("resolved", False)
            } for a in alerts
        ]
    }

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Получить активные алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_alert_history()
    active = [a for a in alerts if not (a.resolved if hasattr(a, "resolved") else a.get("resolved", False))]
    return {
        "active_alerts": [
            {
                "id": str(a.id) if hasattr(a, "id") else str(a.get("id", "")),
                "severity": a.severity.value if hasattr(a, "severity") else a.get("severity", ""),
                "message": a.message if hasattr(a, "message") else a.get("message", ""),
                "timestamp": a.timestamp.isoformat() if hasattr(a, "timestamp") else a.get("timestamp", "")
            } for a in active
        ]
    }

@app.get("/api/health")
async def get_health():
    """Получить общее здоровье системы"""
    if not monitor_manager:
        raise HTTPException(status_code=503, detail="Monitor manager not initialized")
    status = await monitor_manager.get_system_status()
    return status
```

---

**Скопируйте этот код и вставьте перед `if __name__ == "__main__":`** 📋

