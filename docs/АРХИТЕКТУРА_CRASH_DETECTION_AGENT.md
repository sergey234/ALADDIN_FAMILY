# 🚗 АРХИТЕКТУРА: Crash Detection Agent

**Дата:** 12 декабря 2025  
**Версия:** 1.0.0

---

## 🎯 КАК РАБОТАЕТ АГЕНТ

### 📱 **Источник данных: iOS приложение**

**iOS приложение собирает данные с датчиков устройства:**

1. **Акселерометр** (CoreMotion framework):
   - Ускорение по осям X, Y, Z (м/с²)
   - Частота: ~100 Гц (10 раз в секунду)
   - Используется для определения G-сил

2. **Гироскоп** (CoreMotion framework):
   - Угловая скорость по осям X, Y, Z (рад/с)
   - Частота: ~100 Гц
   - Используется для определения вращения/переворота

3. **Геолокация** (CoreLocation framework) - **ОПЦИОНАЛЬНО:**
   - **Геозоны** (радиус 500м) - iOS ограничение
   - **Приблизительное местоположение** (если доступно)
   - **Скорость движения** (км/ч) - опционально, если недоступна - вычисляется из акселерометра

4. **Дополнительные данные:**
   - Временная метка каждого измерения
   - ID пользователя
   - Статус устройства (в движении/на месте)

---

## 🔄 ПРОЦЕСС РАБОТЫ

### **Шаг 1: Запуск мониторинга**

```
iOS App → POST /api/crash-detection/start
         ↓
Backend → CrashDetectionAgent.start_monitoring(user_id)
         ↓
Результат: Мониторинг активен для пользователя
```

**Что происходит:**
- Агент создает запись в `active_monitoring[user_id]`
- Инициализирует буфер данных `sensor_data_buffer[user_id]`
- Создает пустую историю аварий `crash_history[user_id]`

---

### **Шаг 2: Непрерывная отправка данных**

```
iOS App (каждые 0.1 сек) → POST /api/crash-detection/data
                          {
                            "user_id": "user123",
                            "accelerometer": {"x": 0.5, "y": 0.3, "z": 9.8, "timestamp": 1234567890.123},
                            "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.05, "timestamp": 1234567890.123},
                            "speed": 60.0,
                            "location": {"latitude": 55.7558, "longitude": 37.6173}
                          }
                          ↓
Backend → CrashDetectionAgent.process_sensor_data(...)
```

**Что происходит:**
1. Агент получает данные сенсоров
2. Создает объекты `AccelerometerData` и `GyroscopeData`
3. Добавляет в буфер (последние 10 секунд)
4. Вызывает `detect_crash()` для анализа

---

### **Шаг 3: Обнаружение аварии**

**Алгоритм обнаружения:**

```python
def detect_crash(...):
    # 1. Вычисление G-силы
    g_force = accelerometer_data.get_g_force()  # √(x² + y² + z²) / 9.8
    
    # 2. Проверка порога
    if g_force < 3.0G:
        return None  # Нормальное движение
    
    # 3. Фильтр ложных срабатываний
    if not _is_valid_crash_signal(...):
        return None  # Ложное срабатывание (например, телефон упал)
    
    # 4. Определение серьезности
    severity = _determine_severity(g_force, speed)
    # LOW: 3.0-4.0G
    # MEDIUM: 4.0-5.0G
    # HIGH: 5.0-8.0G
    # CRITICAL: >8.0G
    
    # 5. Создание события аварии
    crash_event = CrashEvent(...)
    
    # 6. Автоматический вызов помощи (если HIGH/CRITICAL)
    if severity in [HIGH, CRITICAL]:
        _call_emergency_service(crash_event)
    
    return crash_event
```

---

### **Шаг 4: Фильтр ложных срабатываний**

**Проверки для валидации сигнала:**

1. **Буфер данных:**
   - Должно быть минимум 3 измерения
   - G-сила должна быть высокой в 2+ последовательных измерениях

2. **Резкое изменение:**
   - Разница между измерениями должна быть >1.0G
   - Это отличает удар от плавного движения

3. **Гироскоп:**
   - При аварии угловая скорость должна быть >5 рад/с
   - Это отличает аварию от падения телефона

4. **Временной паттерн:**
   - Авария = резкий скачок G-силы
   - Падение телефона = плавное изменение

---

### **Шаг 5: Автоматический вызов помощи**

```
CrashDetectionAgent._call_emergency_service(crash_event)
         ↓
Генерация call_id: "emergency_user123_1234567890"
         ↓
Интеграция с API экстренных служб:
  - 112 (РФ) - Единая служба спасения
  - 911 (США) - Emergency Services
         ↓
Отправка данных:
  - Местоположение (latitude, longitude)
  - Серьезность аварии
  - G-сила удара
  - Время аварии
  - ID пользователя
         ↓
Получение подтверждения вызова
```

**TODO:** Интеграция с реальным API экстренных служб (День 3)

---

## 🏗️ АРХИТЕКТУРА И ОСНОВА

### **Базовый класс:**
```python
class CrashDetectionAgent(SecurityBase, ThreatMonitoringInterface):
```

**Наследуется от:**
1. **`SecurityBase`** - базовый класс всех агентов безопасности
   - Предоставляет: `self.logger`, `self.config`
   - Стандартизирует интерфейс агентов

2. **`ThreatMonitoringInterface`** - интерфейс мониторинга угроз
   - Методы: `collect_threats()`, `analyze_threats()`, `send_alert()`
   - Интеграция с ThreatEventBus

---

### **Хранилище данных (in-memory):**

```python
# Активные мониторинги
self.active_monitoring: Dict[str, Dict[str, Any]]
# {
#   "user123": {
#     "status": "active",
#     "started_at": "2025-12-12T10:00:00",
#     "last_data_time": "2025-12-12T10:05:30",
#     "crash_count": 0
#   }
# }

# История аварий
self.crash_history: Dict[str, List[CrashEvent]]
# {
#   "user123": [
#     CrashEvent(event_id="crash_...", severity=HIGH, g_force=6.5, ...),
#     ...
#   ]
# }

# Буфер данных сенсоров (последние 10 секунд)
self.sensor_data_buffer: Dict[str, List[AccelerometerData]]
# {
#   "user123": [
#     AccelerometerData(x=0.5, y=0.3, z=9.8, timestamp=...),
#     AccelerometerData(x=15.0, y=10.0, z=20.0, timestamp=...),  # Удар!
#     ...
#   ]
# }
```

**Примечание:** Для продакшена нужно использовать Redis или БД вместо in-memory хранилища.

---

## 🔌 К ЧЕМУ ОБРАЩАЕТСЯ АГЕНТ

### **1. ThreatEventBus (внутренняя система)**

```python
self.event_bus = get_threat_event_bus()
self.event_bus.publish(ThreatEvent(...))
```

**Назначение:**
- Публикация событий аварий для других агентов
- Интеграция с системой мониторинга угроз
- Централизованная обработка событий

---

### **2. API экстренных служб (внешние сервисы)**

**TODO: Интеграция (День 3)**

**Планируемые интеграции:**

1. **112 (РФ) - Единая служба спасения:**
   - API для автоматического вызова
   - Отправка местоположения
   - Получение подтверждения

**Примечание:** В России используется только **112** (Единая служба спасения). 911 используется только в США.

**Формат вызова:**
```python
POST https://api.112.ru/emergency/call
{
  "call_id": "emergency_user123_1234567890",
  "location": {
    "type": "geofence",  # или "exact"
    "geofence_center": {"latitude": 55.7558, "longitude": 37.6173},
    "radius_meters": 500
  },
  "severity": "critical",
  "g_force": 8.5,
  "timestamp": "2025-12-12T10:05:30",
  "user_id": "user123"
}
```

**Важно:** 
- iOS ограничение: точный GPS недоступен, только геозоны с радиусом 500м
- Если геозона недоступна, используется приблизительное местоположение
- Скорость вычисляется из акселерометра, если GPS недоступен

---

### **3. API endpoints (FastAPI router)**

**Агент НЕ обращается напрямую к API endpoints.**

**API endpoints обращаются к агенту:**

```python
# В crash_detection_router.py
@router.post("/data")
def process_sensor_data(request: SensorDataRequest):
    agent = get_agent()  # Получаем экземпляр CrashDetectionAgent
    result = agent.process_sensor_data(
        user_id=request.user_id,
        accelerometer_data=request.accelerometer,
        gyroscope_data=request.gyroscope,
        speed=request.speed,
        location=request.location
    )
    return result
```

---

## 📊 ДАННЫЕ И АЛГОРИТМЫ

### **Входные данные:**

1. **Акселерометр:**
   - X, Y, Z (м/с²)
   - Timestamp

2. **Гироскоп (опционально):**
   - X, Y, Z (рад/с)
   - Timestamp

3. **Скорость (опционально):**
   - км/ч

4. **Местоположение (опционально):**
   - Latitude, Longitude

---

### **Алгоритмы обработки:**

1. **Вычисление G-силы:**
   ```python
   magnitude = √(x² + y² + z²)
   g_force = magnitude / 9.8  # 1G = 9.8 м/с²
   ```

2. **Определение серьезности:**
   ```python
   if g_force >= 8.0: CRITICAL
   elif g_force >= 5.0: HIGH
   elif g_force >= 4.0: MEDIUM
   else: LOW
   ```

3. **Фильтр ложных срабатываний:**
   - Анализ буфера (последние 3 измерения)
   - Проверка резкого изменения G-силы
   - Проверка гироскопа (угловая скорость)

---

## 🔄 ИНТЕГРАЦИЯ С СИСТЕМОЙ

### **1. Регистрация в SFM (Security Functions Manager)**

```json
{
  "name": "crash_detection_agent",
  "type": "ai_agent",
  "path": "security/ai_agents/crash_detection_agent.py",
  "class": "CrashDetectionAgent",
  "functions": [
    "start_monitoring",
    "stop_monitoring",
    "process_sensor_data",
    "detect_crash",
    "get_status",
    "get_crash_history",
    "cancel_emergency_call"
  ],
  "api_endpoints": [
    "/api/crash-detection/start",
    "/api/crash-detection/stop",
    "/api/crash-detection/status",
    "/api/crash-detection/data",
    "/api/crash-detection/emergency-call",
    "/api/crash-detection/cancel-emergency-call"
  ]
}
```

---

### **2. Интеграция в main.py**

```python
# Импорт
from security.api.routers.crash_detection_router import router as crash_detection_router

# Регистрация
try:
    app.include_router(crash_detection_router)
    print("✅ Crash Detection Router зарегистрирован")
except Exception as e:
    print(f"⚠️ Не удалось зарегистрировать Crash Detection Router: {e}")
```

---

### **3. ThreatEventBus интеграция**

```python
# Подписка на события
self.event_bus.subscribe(self, event_types=["crash", "*"])

# Публикация событий
self.event_bus.publish(ThreatEvent(
    event_id=crash_event.event_id,
    agent_name="crash_detection_agent",
    threat_type="crash",
    severity=crash_event.severity.value,
    ...
))
```

---

## 📱 iOS ИНТЕГРАЦИЯ (будущее)

### **Что нужно в iOS приложении:**

1. **CoreMotion framework:**
   ```swift
   import CoreMotion
   
   let motionManager = CMMotionManager()
   motionManager.accelerometerUpdateInterval = 0.1  // 10 раз в секунду
   motionManager.startAccelerometerUpdates(to: .main) { data, error in
       // Отправка на сервер
   }
   ```

2. **CoreLocation framework:**
   ```swift
   import CoreLocation
   
   locationManager.startUpdatingLocation()
   // Получение скорости и местоположения
   ```

3. **API вызовы:**
   ```swift
   // Запуск мониторинга
   POST /api/crash-detection/start
   
   // Отправка данных (каждые 0.1 сек)
   POST /api/crash-detection/data
   {
     "user_id": "...",
     "accelerometer": {...},
     "gyroscope": {...},
     "speed": 60.0,
     "location": {...}
   }
   ```

---

## ⚙️ КОНФИГУРАЦИЯ

### **Параметры агента:**

```python
{
  "g_force_threshold": 3.0,  # Порог G-сил (3.0G)
  "speed_change_threshold": 30.0,  # Порог изменения скорости (30 км/ч)
  "emergency_service_number": "112",  # 112 для РФ, 911 для США
  "auto_call_enabled": True,  # Автоматический вызов помощи
  "false_positive_filter": True  # Фильтр ложных срабатываний
}
```

---

## 🔒 БЕЗОПАСНОСТЬ И ПРИВАТНОСТЬ

### **Защита данных:**

1. **Шифрование:**
   - Данные сенсоров передаются по HTTPS
   - Локальное хранение зашифровано

2. **Приватность:**
   - Данные хранятся только для активного мониторинга
   - История аварий хранится ограниченное время
   - Местоположение отправляется только при аварии

3. **Контроль:**
   - Пользователь может остановить мониторинг
   - Пользователь может отменить вызов помощи
   - Прозрачная логика обнаружения

---

## 📈 ПРОИЗВОДИТЕЛЬНОСТЬ

### **Оптимизации:**

1. **Буферизация:**
   - Хранятся только последние 10 секунд данных
   - Автоматическая очистка старых данных

2. **Обработка:**
   - Анализ в реальном времени
   - Минимальная задержка обнаружения

3. **Масштабируемость:**
   - In-memory хранилище (быстро, но не масштабируется)
   - Для продакшена: Redis или БД

---

## 🎯 ИТОГОВАЯ СХЕМА

```
┌─────────────────┐
│   iOS App       │
│  (CoreMotion)   │
│                 │
│  Акселерометр   │──┐
│  Гироскоп       │  │
│  GPS/Скорость   │  │  POST /api/crash-detection/data
└─────────────────┘  │  (каждые 0.1 сек)
                      │
                      ↓
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ crash_detection_router.py     │ │
│  │                               │ │
│  │  POST /start                  │ │
│  │  POST /stop                   │ │
│  │  POST /data  ←───────────────┘ │
│  │  GET /status                  │ │
│  │  POST /emergency-call         │ │
│  └───────────┬───────────────────┘ │
│              │                      │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │ CrashDetectionAgent          │ │
│  │                               │ │
│  │  • process_sensor_data()     │ │
│  │  • detect_crash()             │ │
│  │  • _call_emergency_service() │ │
│  └───────────┬───────────────────┘ │
└──────────────┼──────────────────────┘
               │
               ├──→ ThreatEventBus (внутренняя система)
               │
               └──→ API экстренных служб (112, 911)
                    (TODO: День 3)
```

---

**Последнее обновление:** 12 декабря 2025
