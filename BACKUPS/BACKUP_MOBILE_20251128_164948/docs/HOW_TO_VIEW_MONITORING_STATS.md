# 📊 КАК ВИДЕТЬ СТАТИСТИКУ СИСТЕМЫ МОНИТОРИНГА

**Дата:** 2025-11-26  
**Цель:** Объяснить, как подключить и видеть статистику вместо Prometheus и Grafana

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### 1. Добавить endpoints в API Gateway ✅

**Файл:** `/opt/aladdin-backend/security/microservices/api_gateway.py`

**Что добавить в конец файла:**

```python
# Импорты (в начале файла)
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager

# Глобальные переменные (после создания app)
monitor_manager = None
alert_manager = None

# Инициализация при старте
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
    cpu_metrics = [m for m in metrics if 'cpu' in m.name.lower()]
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
    ram_metrics = [m for m in metrics if 'ram' in m.name.lower() or 'memory' in m.name.lower()]
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
    disk_metrics = [m for m in metrics if 'disk' in m.name.lower()]
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
    alerts = alert_manager.get_active_alerts()
    return {
        "alerts": [
            {
                "id": a.id,
                "severity": a.severity.value,
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
                "resolved": a.resolved
            } for a in alerts
        ]
    }

@app.get("/api/alerts/active")
async def get_active_alerts():
    """Получить активные алерты"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="Alert manager not initialized")
    alerts = alert_manager.get_active_alerts()
    active = [a for a in alerts if not a.resolved]
    return {
        "active_alerts": [
            {
                "id": a.id,
                "severity": a.severity.value,
                "message": a.message,
                "timestamp": a.timestamp.isoformat()
            } for a in active
        ]
    }

# Endpoint для здоровья системы
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

## 🔍 КАК ВИДЕТЬ СТАТИСТИКУ

### Вариант 1: Через API (JSON) ✅

**Простейший способ - через curl:**

```bash
# Получить все метрики
curl https://aladdin-ai.ru/api/metrics

# Получить метрики CPU
curl https://aladdin-ai.ru/api/metrics/cpu

# Получить метрики RAM
curl https://aladdin-ai.ru/api/metrics/ram

# Получить метрики диска
curl https://aladdin-ai.ru/api/metrics/disk

# Получить все алерты
curl https://aladdin-ai.ru/api/alerts

# Получить активные алерты
curl https://aladdin-ai.ru/api/alerts/active

# Получить здоровье системы
curl https://aladdin-ai.ru/api/health
```

**Для мобильного приложения:**
```swift
// В APIService.swift добавить:
func getMetrics(completion: @escaping (Result<MetricsResponse, Error>) -> Void) {
    networkManager.get(endpoint: "/metrics", completion: completion)
}

func getAlerts(completion: @escaping (Result<AlertsResponse, Error>) -> Void) {
    networkManager.get(endpoint: "/alerts", completion: completion)
}
```

---

### Вариант 2: Через веб-интерфейс ⚠️

**Создать простую HTML страницу:**

**Файл:** `/opt/aladdin-backend/security/microservices/dashboard.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>ALADDIN Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; padding: 20px; }
        .metric { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .alert { padding: 10px; margin: 5px 0; border-left: 4px solid; }
        .alert.critical { border-color: red; background: #ffe6e6; }
        .alert.high { border-color: orange; background: #fff4e6; }
        .alert.medium { border-color: yellow; background: #fffce6; }
    </style>
</head>
<body>
    <h1>ALADDIN Monitoring Dashboard</h1>
    
    <div class="metric">
        <h2>CPU Usage</h2>
        <canvas id="cpuChart"></canvas>
    </div>
    
    <div class="metric">
        <h2>RAM Usage</h2>
        <canvas id="ramChart"></canvas>
    </div>
    
    <div class="metric">
        <h2>Disk Usage</h2>
        <canvas id="diskChart"></canvas>
    </div>
    
    <div class="metric">
        <h2>Active Alerts</h2>
        <div id="alerts"></div>
    </div>
    
    <script>
        // Загрузка метрик
        async function loadMetrics() {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            // Обновление графиков
            updateChart('cpuChart', data.metrics.filter(m => m.name.includes('cpu')));
            updateChart('ramChart', data.metrics.filter(m => m.name.includes('ram')));
            updateChart('diskChart', data.metrics.filter(m => m.name.includes('disk')));
        }
        
        // Загрузка алертов
        async function loadAlerts() {
            const response = await fetch('/api/alerts/active');
            const data = await response.json();
            
            const alertsDiv = document.getElementById('alerts');
            alertsDiv.innerHTML = data.active_alerts.map(alert => 
                `<div class="alert ${alert.severity}">
                    <strong>${alert.severity.toUpperCase()}</strong>: ${alert.message}
                    <br><small>${new Date(alert.timestamp).toLocaleString()}</small>
                </div>`
            ).join('');
        }
        
        // Обновление графика
        function updateChart(canvasId, metrics) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: metrics.map(m => new Date(m.timestamp).toLocaleTimeString()),
                    datasets: [{
                        label: 'Usage %',
                        data: metrics.map(m => m.value),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });
        }
        
        // Обновление каждые 30 секунд
        loadMetrics();
        loadAlerts();
        setInterval(() => {
            loadMetrics();
            loadAlerts();
        }, 30000);
    </script>
</body>
</html>
```

**Добавить в API Gateway:**

```python
from fastapi.responses import FileResponse

@app.get("/dashboard")
async def dashboard():
    """Веб-интерфейс для мониторинга"""
    return FileResponse("/opt/aladdin-backend/security/microservices/dashboard.html")
```

**Время:** 2-3 часа

---

### Вариант 3: Через мобильное приложение ⚠️

**Добавить экран мониторинга:**

**Файл:** `Screens/MonitoringScreen.swift`

```swift
import SwiftUI
import Charts

struct MonitoringScreen: View {
    @StateObject private var viewModel = MonitoringViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // CPU метрика
                MetricCard(title: "CPU", value: viewModel.cpuUsage, color: .blue)
                
                // RAM метрика
                MetricCard(title: "RAM", value: viewModel.ramUsage, color: .green)
                
                // Disk метрика
                MetricCard(title: "Disk", value: viewModel.diskUsage, color: .orange)
                
                // Алерты
                AlertsList(alerts: viewModel.alerts)
            }
            .padding()
        }
        .onAppear {
            viewModel.loadMetrics()
        }
    }
}
```

**Время:** 3-4 часа

---

## 📊 СТРУКТУРА API

### Endpoints для метрик:

```python
GET /api/metrics
# Возвращает все метрики
# Response: {
#   "metrics": [
#     {"name": "cpu_percent", "value": 45.2, "timestamp": "...", "status": "healthy", "unit": "percent"},
#     {"name": "memory_percent", "value": 65.3, "timestamp": "...", "status": "healthy", "unit": "percent"},
#     ...
#   ]
# }

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
# Response: {
#   "alerts": [
#     {"id": "...", "severity": "high", "message": "...", "timestamp": "...", "resolved": false},
#     ...
#   ]
# }

GET /api/alerts/active
# Возвращает активные алерты
# Response: {
#   "active_alerts": [
#     {"id": "...", "severity": "critical", "message": "...", "timestamp": "..."},
#     ...
#   ]
# }
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
1. ✅ Добавить endpoints в API Gateway (код выше)
2. ✅ Перезапустить API Gateway
3. ✅ Протестировать endpoints через curl

### В ближайшее время:
4. ⚠️ Создать веб-интерфейс (опционально)
5. ⚠️ Добавить экран мониторинга в мобильное приложение (опционально)

---

## ✅ ИТОГ

**Что нужно сделать:**
1. ✅ Добавить endpoints в API Gateway (код выше)
2. ✅ Перезапустить API Gateway: `systemctl restart aladdin-api-gateway`
3. ✅ Протестировать: `curl https://aladdin-ai.ru/api/metrics`

**Как видеть статистику:**
- ✅ Через API: `GET https://aladdin-ai.ru/api/metrics`
- ⚠️ Через веб-интерфейс: `https://aladdin-ai.ru/dashboard` (если создать)
- ⚠️ Через мобильное приложение (если добавить экран)

---

**План готов! Начинаем интеграцию!** 🚀

