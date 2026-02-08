# 📱 ПРАВИЛА iOS ДЛЯ LocationManager

**Дата:** 2026-01-11  
**Версия:** 1.0.0

---

## 📋 ОГЛАВЛЕНИЕ

1. [Разрешения (Permissions)](#1-разрешения-permissions)
2. [Info.plist требования](#2-infoplist-требования)
3. [Фоновый режим](#3-фоновый-режим)
4. [Методы получения геолокации](#4-методы-получения-геолокации)
5. [Ограничения и правила](#5-ограничения-и-правила)
6. [App Store требования](#6-app-store-требования)
7. [Рекомендации для ALADDIN](#7-рекомендации-для-aladdin)

---

## 1. РАЗРЕШЕНИЯ (PERMISSIONS)

### 1.1 Типы разрешений

iOS требует явного запроса разрешения на геолокацию:

#### **When In Use (Когда приложение активно)**
```swift
locationManager.requestWhenInUseAuthorization()
```
- Работает только когда приложение открыто
- Пользователь видит синий индикатор геолокации
- **Требуется:** `NSLocationWhenInUseUsageDescription` в Info.plist

#### **Always (Всегда)**
```swift
locationManager.requestAlwaysAuthorization()
```
- Работает в фоне
- Требуется для Significant-Change и Region Monitoring
- **Требуется:** `NSLocationAlwaysAndWhenInUseUsageDescription` в Info.plist
- **Важно:** iOS показывает предупреждение пользователю о фоновом использовании

### 1.2 Статусы разрешений

```swift
enum CLAuthorizationStatus {
    case notDetermined      // Пользователь еще не выбрал
    case restricted         // Ограничено (родительский контроль)
    case denied            // Отклонено пользователем
    case authorizedWhenInUse  // Разрешено только когда приложение активно
    case authorizedAlways    // Разрешено всегда
}
```

### 1.3 Проверка статуса

```swift
let status = locationManager.authorizationStatus
switch status {
case .notDetermined:
    locationManager.requestAlwaysAuthorization()
case .denied, .restricted:
    // Показать объяснение пользователю
case .authorizedWhenInUse, .authorizedAlways:
    // Можно использовать геолокацию
}
```

---

## 2. INFO.PLIST ТРЕБОВАНИЯ

### 2.1 Обязательные ключи

**✅ Уже есть в проекте:**

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>ALADDIN Family needs location access for family safety and emergency features.</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>ALADDIN Family needs location access for family safety and emergency features.</string>
```

### 2.2 Описание должно быть:
- ✅ Понятным для пользователя
- ✅ Объяснять ЗАЧЕМ нужна геолокация
- ✅ На языке пользователя (русский/английский)
- ❌ НЕ должно быть пустым или техническим

### 2.3 UIBackgroundModes

**⚠️ ВАЖНО:** В проекте НЕТ `location` в UIBackgroundModes (строка 112-115):

```xml
<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
    <!-- НЕТ <string>location</string> -->
</array>
```

**Это правильно!** Потому что:
- Significant-Change Location Service **НЕ требует** `location` в UIBackgroundModes
- Region Monitoring **НЕ требует** `location` в UIBackgroundModes
- `location` нужен только для **persistent location** (постоянное отслеживание каждую секунду)

---

## 3. ФОНОВЫЙ РЕЖИМ

### 3.1 Ограничения iOS

iOS **НЕ разрешает** точное определение местоположения в фоне без специальных разрешений.

**Проблема:**
- Постоянное GPS в фоне разряжает батарею
- Apple строго контролирует фоновое использование геолокации
- App Store может отклонить приложение с неправильным использованием

### 3.2 Решения для фона

#### **Вариант 1: Significant-Change Location Service** ✅ РЕКОМЕНДУЕТСЯ

```swift
if CLLocationManager.significantLocationChangesMonitoringAvailable() {
    locationManager.startMonitoringSignificantLocationChanges()
}
```

**Характеристики:**
- ✅ Обновления только при значительных изменениях (500+ метров)
- ✅ Работает в фоне автоматически
- ✅ **НЕ требует** `location` в UIBackgroundModes
- ✅ Экономит батарею
- ✅ Идеально для родительского контроля

**Ограничения:**
- ⚠️ Обновления только при перемещении на 500+ метров
- ⚠️ Не подходит для точного отслеживания маршрута

#### **Вариант 2: Region Monitoring (Geofencing)** ✅ РЕКОМЕНДУЕТСЯ

```swift
let region = CLCircularRegion(
    center: CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173),
    radius: 500,  // Минимум 100 метров, максимум не ограничен
    identifier: "home"
)
locationManager.startMonitoring(for: region)
```

**Характеристики:**
- ✅ Обновления при входе/выходе из зоны
- ✅ Работает в фоне автоматически
- ✅ **НЕ требует** `location` в UIBackgroundModes
- ✅ Экономит батарею
- ✅ Идеально для геозон (дом, школа, секция)

**Ограничения:**
- ⚠️ Минимальный радиус: 100 метров
- ⚠️ Максимум 20 геозон одновременно
- ⚠️ iOS может не уведомить, если устройство перезагружено

#### **Вариант 3: Persistent Location** ❌ НЕ РЕКОМЕНДУЕТСЯ

```swift
// Требует location в UIBackgroundModes
locationManager.allowsBackgroundLocationUpdates = true
locationManager.startUpdatingLocation()
```

**Характеристики:**
- ❌ Требует `location` в UIBackgroundModes
- ❌ Разряжает батарею
- ❌ Apple строго контролирует
- ❌ Может быть отклонено App Store

**Когда использовать:**
- Только для критических функций (навигация, фитнес-трекинг)
- Требует обоснования для App Store

---

## 4. МЕТОДЫ ПОЛУЧЕНИЯ ГЕОЛОКАЦИИ

### 4.1 One-Time Location (Одноразовое получение)

```swift
locationManager.requestLocation()
```

**Использование:**
- Получить текущее местоположение один раз
- Не требует фонового режима
- Работает только когда приложение активно

### 4.2 Continuous Updates (Постоянные обновления)

```swift
locationManager.startUpdatingLocation()
locationManager.stopUpdatingLocation()
```

**Использование:**
- Постоянные обновления координат
- Работает только когда приложение активно
- Разряжает батарею при длительном использовании

### 4.3 Significant-Change Location Service

```swift
if CLLocationManager.significantLocationChangesMonitoringAvailable() {
    locationManager.startMonitoringSignificantLocationChanges()
    locationManager.stopMonitoringSignificantLocationChanges()
}
```

**Использование:**
- Обновления при перемещении на 500+ метров
- Работает в фоне
- Экономит батарею

### 4.4 Region Monitoring (Geofencing)

```swift
let region = CLCircularRegion(center: coordinate, radius: 100, identifier: "home")
locationManager.startMonitoring(for: region)
locationManager.stopMonitoring(for: region)
```

**Использование:**
- Отслеживание входа/выхода из зон
- Работает в фоне
- Экономит батарею

---

## 5. ОГРАНИЧЕНИЯ И ПРАВИЛА

### 5.1 Точность

**iOS автоматически управляет точностью:**
- Высокая точность (GPS) - разряжает батарею
- Низкая точность (WiFi/Cellular) - экономит батарею
- iOS выбирает оптимальную точность автоматически

**Настройка точности:**
```swift
locationManager.desiredAccuracy = kCLLocationAccuracyBest
// или
locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
```

### 5.2 Расстояние фильтр

```swift
locationManager.distanceFilter = 100  // Обновления только при перемещении на 100+ метров
```

**Использование:**
- Уменьшает количество обновлений
- Экономит батарею
- Не влияет на Significant-Change и Region Monitoring

### 5.3 Ограничения геозон

- ⚠️ **Максимум 20 геозон** одновременно на устройстве
- ⚠️ **Минимальный радиус:** 100 метров
- ⚠️ **Максимальный радиус:** не ограничен (но рекомендуется до 1000 метров)
- ⚠️ iOS может не уведомить, если устройство перезагружено

### 5.4 Ограничения Significant-Change

- ⚠️ Обновления только при перемещении на **500+ метров**
- ⚠️ Требует **authorizedAlways** разрешение
- ⚠️ Может не работать в некоторых регионах (зависит от сотовой сети)

---

## 6. APP STORE ТРЕБОВАНИЯ

### 6.1 Обязательные требования

1. **Описание в Info.plist:**
   - ✅ Должно быть понятным
   - ✅ Объяснять зачем нужна геолокация
   - ✅ На языке пользователя

2. **Обоснование использования:**
   - ✅ Для родительского контроля - **приемлемо**
   - ✅ Для безопасности семьи - **приемлемо**
   - ✅ Для экстренных ситуаций - **приемлемо**
   - ❌ Для рекламы - **неприемлемо**

3. **UIBackgroundModes:**
   - ✅ Если используете Significant-Change или Region Monitoring - **НЕ нужен** `location`
   - ⚠️ Если используете persistent location - **нужен** `location` и обоснование

### 6.2 Что проверяет Apple

1. **Соответствие описанию:**
   - Используете ли геолокацию так, как описано в Info.plist?
   - Есть ли реальная необходимость?

2. **Батарея:**
   - Не разряжает ли приложение батарею из-за геолокации?
   - Используете ли экономичные методы?

3. **Приватность:**
   - Защищаете ли данные пользователя?
   - Используете ли Location Bubble для приватности?

---

## 7. РЕКОМЕНДАЦИИ ДЛЯ ALADDIN

### 7.1 Что использовать

#### **Для родительского контроля:**
```swift
// 1. Significant-Change для общих перемещений
if CLLocationManager.significantLocationChangesMonitoringAvailable() {
    locationManager.startMonitoringSignificantLocationChanges()
}

// 2. Region Monitoring для геозон (дом, школа, секция)
let homeRegion = CLCircularRegion(center: homeLocation, radius: 100, identifier: "home")
locationManager.startMonitoring(for: homeRegion)

let schoolRegion = CLCircularRegion(center: schoolLocation, radius: 100, identifier: "school")
locationManager.startMonitoring(for: schoolRegion)
```

**Преимущества:**
- ✅ Работает в фоне
- ✅ Экономит батарею
- ✅ Не требует `location` в UIBackgroundModes
- ✅ Приемлемо для App Store

#### **Для Crash Detection:**
```swift
// Использовать геозоны с радиусом 500 метров
let crashZone = CLCircularRegion(
    center: currentLocation,
    radius: 500,
    identifier: "crash_detection_zone"
)
locationManager.startMonitoring(for: crashZone)
```

**Преимущества:**
- ✅ Работает в фоне
- ✅ Экономит батарею
- ✅ Соответствует iOS ограничениям

#### **Для Driving Reports:**
```swift
// One-time location при начале поездки
locationManager.requestLocation()

// Или continuous updates только когда приложение активно
locationManager.startUpdatingLocation()
```

**Преимущества:**
- ✅ Точное отслеживание маршрута
- ✅ Работает только когда приложение активно
- ✅ Не требует фонового режима

### 7.2 Что НЕ использовать

❌ **Persistent Location (постоянное отслеживание):**
- Разряжает батарею
- Требует обоснования для App Store
- Может быть отклонено

❌ **Высокая точность без необходимости:**
- Используйте `kCLLocationAccuracyHundredMeters` вместо `kCLLocationAccuracyBest`
- Экономит батарею

### 7.3 Архитектура LocationManager

```swift
import CoreLocation
import Combine

@MainActor
class LocationManager: NSObject, ObservableObject {
    static let shared = LocationManager()
    
    @Published var currentLocation: CLLocation?
    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published var isMonitoringSignificantChanges: Bool = false
    @Published var monitoredRegions: [String: CLCircularRegion] = [:]
    
    private let locationManager = CLLocationManager()
    
    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        locationManager.distanceFilter = 100  // Обновления при перемещении на 100+ метров
    }
    
    // Запрос разрешения
    func requestAuthorization() {
        let status = locationManager.authorizationStatus
        switch status {
        case .notDetermined:
            locationManager.requestAlwaysAuthorization()  // Для фонового режима
        case .denied, .restricted:
            // Показать объяснение пользователю
            break
        case .authorizedWhenInUse, .authorizedAlways:
            // Уже разрешено
            break
        }
    }
    
    // Significant-Change Location Service
    func startSignificantLocationChanges() {
        guard CLLocationManager.significantLocationChangesMonitoringAvailable() else {
            print("⚠️ Significant-Change недоступен")
            return
        }
        
        guard locationManager.authorizationStatus == .authorizedAlways else {
            print("⚠️ Требуется authorizedAlways разрешение")
            return
        }
        
        locationManager.startMonitoringSignificantLocationChanges()
        isMonitoringSignificantChanges = true
    }
    
    // Region Monitoring
    func startMonitoring(geofence: GeofenceItem) {
        guard locationManager.authorizationStatus == .authorizedAlways else {
            print("⚠️ Требуется authorizedAlways разрешение")
            return
        }
        
        let region = CLCircularRegion(
            center: CLLocationCoordinate2D(
                latitude: geofence.latitude,
                longitude: geofence.longitude
            ),
            radius: max(100, geofence.radius),  // Минимум 100 метров
            identifier: geofence.id
        )
        
        region.notifyOnEntry = true
        region.notifyOnExit = true
        
        locationManager.startMonitoring(for: region)
        monitoredRegions[geofence.id] = region
    }
    
    // One-time location
    func getCurrentLocation() async throws -> CLLocation {
        return try await withCheckedThrowingContinuation { continuation in
            locationManager.requestLocation()
            // Обработка в delegate
        }
    }
}

// MARK: - CLLocationManagerDelegate
extension LocationManager: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        currentLocation = location
    }
    
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        print("✅ Вошли в геозону: \(region.identifier)")
        // Отправить на сервер
    }
    
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        print("✅ Покинули геозону: \(region.identifier)")
        // Отправить на сервер
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        authorizationStatus = status
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("❌ Ошибка геолокации: \(error.localizedDescription)")
    }
}
```

---

## ✅ ИТОГОВЫЕ РЕКОМЕНДАЦИИ

### Для ALADDIN:

1. **Использовать:**
   - ✅ Significant-Change Location Service для общих перемещений
   - ✅ Region Monitoring для геозон
   - ✅ One-time location для Driving Reports (когда приложение активно)

2. **НЕ использовать:**
   - ❌ Persistent Location (постоянное отслеживание)
   - ❌ `location` в UIBackgroundModes (не нужен)

3. **Info.plist:**
   - ✅ Уже настроен правильно
   - ✅ Описания понятные и на русском/английском

4. **App Store:**
   - ✅ Обоснование: "family safety and emergency features"
   - ✅ Приемлемо для родительского контроля
   - ✅ Не требует дополнительных разрешений

---

**Последнее обновление:** 2026-01-11  
**Статус:** Готово к реализации LocationManager
