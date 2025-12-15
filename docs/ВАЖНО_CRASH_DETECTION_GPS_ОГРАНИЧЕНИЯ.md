# ⚠️ ВАЖНО: Ограничения GPS в Crash Detection Agent

**Дата:** 12 декабря 2025

---

## 🚫 iOS ОГРАНИЧЕНИЯ GPS

### Проблема:
iOS **НЕ разрешает** точное определение местоположения в фоновом режиме без специальных разрешений и ограничений.

### Решение:
Использовать **геозоны** (geofencing) с радиусом **500 метров** вместо точного GPS.

---

## 🔧 РЕАЛИЗАЦИЯ БЕЗ ТОЧНОГО GPS

### 1. **Геозоны вместо точного GPS**

**iOS приложение:**
```swift
import CoreLocation

// Создание геозоны
let geofence = CLCircularRegion(
    center: CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173),
    radius: 500,  // 500 метров (максимум для iOS)
    identifier: "crash_detection_zone"
)

locationManager.startMonitoring(for: geofence)
```

**Backend получает:**
```json
{
  "location": {
    "type": "geofence",
    "geofence_center": {
      "latitude": 55.7558,
      "longitude": 37.6173
    },
    "radius_meters": 500
  }
}
```

---

### 2. **Вычисление скорости из акселерометра**

**Проблема:** GPS скорость может быть недоступна.

**Решение:** Интеграция ускорения для вычисления скорости.

```python
def _calculate_speed_from_accelerometer(self, user_id: str, accel: AccelerometerData) -> float:
    # Горизонтальное ускорение (убираем гравитацию)
    horizontal_accel = √(x² + y²)
    
    # Интеграция: v = v₀ + a * dt
    dt = 0.1  # 0.1 сек (100 Гц)
    current_velocity = last_velocity + horizontal_accel * dt
    
    # Конвертация м/с → км/ч
    speed_kmh = current_velocity * 3.6
    
    return speed_kmh
```

**Точность:**
- ✅ Работает без GPS
- ⚠️ Накопление ошибки со временем
- ✅ Решение: периодический сброс при остановке (определяется по низкому ускорению)

---

### 3. **Определение местоположения**

**Варианты (по приоритету):**

1. **Геозона (предпочтительно):**
   ```json
   {
     "type": "geofence",
     "geofence_center": {"latitude": 55.7558, "longitude": 37.6173},
     "radius_meters": 500
   }
   ```

2. **Приблизительное местоположение (если геозона недоступна):**
   ```json
   {
     "type": "approximate",
     "latitude": 55.7558,
     "longitude": 37.6173,
     "accuracy_meters": 1000  // Низкая точность
   }
   ```

3. **Без местоположения (если ничего не доступно):**
   ```json
   {
     "type": "unknown",
     "note": "Местоположение недоступно"
   }
   ```

---

## 📱 iOS РЕАЛИЗАЦИЯ

### **CoreLocation с геозонами:**

```swift
import CoreLocation

class CrashDetectionLocationManager: NSObject, CLLocationManagerDelegate {
    let locationManager = CLLocationManager()
    
    func setupGeofence() {
        // Запрос разрешения
        locationManager.requestAlwaysAuthorization()
        
        // Создание геозоны
        let center = CLLocationCoordinate2D(latitude: currentLat, longitude: currentLon)
        let region = CLCircularRegion(
            center: center,
            radius: 500,  // 500 метров
            identifier: "crash_zone"
        )
        
        locationManager.startMonitoring(for: region)
    }
    
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        // Пользователь вошел в геозону
        // Отправка центра геозоны на сервер
        sendGeofenceCenter(region.center)
    }
}
```

---

## 🚨 ВЫЗОВ ЭКСТРЕННЫХ СЛУЖБ

### **Только 112 (РФ):**

```python
# Убрано: 911 (только для США)
self.emergency_service_number = "112"  # Только для РФ
```

**Формат вызова с геозоной:**
```json
{
  "call_id": "emergency_user123_1234567890",
  "location": {
    "type": "geofence",
    "geofence_center": {
      "latitude": 55.7558,
      "longitude": 37.6173
    },
    "radius_meters": 500,
    "note": "Точное местоположение недоступно из-за iOS ограничений"
  },
  "severity": "critical",
  "g_force": 8.5,
  "timestamp": "2025-12-12T10:05:30",
  "user_id": "user123"
}
```

---

## ✅ ИТОГОВАЯ АРХИТЕКТУРА

### **Обязательные данные:**
- ✅ Акселерометр (X, Y, Z)
- ✅ Гироскоп (X, Y, Z) - опционально, но рекомендуется

### **Опциональные данные:**
- ⚠️ Геозона (центр + радиус 500м) - предпочтительно
- ⚠️ Приблизительное местоположение - если геозона недоступна
- ⚠️ GPS скорость - если недоступна, вычисляется из акселерометра

### **Алгоритм работы:**
1. Получаем данные акселерометра (обязательно)
2. Вычисляем G-силу
3. Если GPS скорость недоступна → вычисляем из акселерометра
4. Если точный GPS недоступен → используем геозону или приблизительное местоположение
5. Обнаруживаем аварию по G-силе
6. Вызываем 112 с доступной информацией о местоположении

---

## 📝 ИЗМЕНЕНИЯ В АГЕНТЕ

### **Обновлено:**
1. ✅ Убрана обязательность GPS
2. ✅ Добавлена поддержка геозон
3. ✅ Вычисление скорости из акселерометра
4. ✅ Убран 911, оставлен только 112
5. ✅ Местоположение опционально

### **Новые параметры конфигурации:**
```python
{
  "use_geofence": True,  # Использовать геозоны
  "geofence_radius": 500  # Радиус геозоны (метры)
}
```

---

**Последнее обновление:** 12 декабря 2025
