# 📍 РУКОВОДСТВО ПО ИСПОЛЬЗОВАНИЮ LocationManager

**Дата:** 2026-01-11  
**Версия:** 1.0.0

---

## 🎯 ОБЗОР

`LocationManager` - централизованный менеджер геолокации для всех функций приложения. Соответствует всем правилам iOS и готов к использованию.

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Импорт

```swift
import CoreLocation
```

### 2. Получение экземпляра

```swift
let locationManager = LocationManager.shared
```

### 3. Запрос разрешения

```swift
locationManager.requestAuthorization(always: true)  // Для фонового режима
```

---

## 📋 ОСНОВНЫЕ МЕТОДЫ

### Запрос разрешения

```swift
// Запрос Always разрешения (для фона)
locationManager.requestAuthorization(always: true)

// Запрос WhenInUse разрешения (только когда приложение активно)
locationManager.requestAuthorization(always: false)

// Проверка разрешения
if locationManager.hasRequiredAuthorization(forBackground: true) {
    // Можно использовать геолокацию в фоне
}
```

### Получение текущего местоположения

```swift
// One-time location (async/await)
do {
    let location = try await locationManager.getCurrentLocation()
    print("Координаты: \(location.coordinate.latitude), \(location.coordinate.longitude)")
} catch {
    print("Ошибка: \(error.localizedDescription)")
}

// Постоянные обновления (только когда приложение активно)
locationManager.startUpdatingLocation()
// ...
locationManager.stopUpdatingLocation()
```

### Significant-Change Location Service

```swift
// Начать мониторинг значительных изменений (500+ метров)
locationManager.startSignificantLocationChanges()

// Остановить
locationManager.stopSignificantLocationChanges()

// Подписка на уведомления
NotificationCenter.default.addObserver(
    forName: .locationSignificantChange,
    object: nil,
    queue: .main
) { notification in
    if let location = notification.userInfo?["location"] as? CLLocation {
        print("Значительное изменение: \(location.coordinate)")
    }
}
```

### Region Monitoring (Geofencing)

```swift
// Начать мониторинг геозоны с координатами
let center = CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173)
do {
    try locationManager.startMonitoring(
        identifier: "home",
        center: center,
        radius: 100  // Минимум 100 метров
    )
} catch {
    print("Ошибка: \(error.localizedDescription)")
}

// Начать мониторинг из GeofenceItem
let geofence = GeofenceItem(name: "Дом", address: "ул. Ленина, 42", radius: 100)
let center = CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173)
try locationManager.startMonitoring(geofence: geofence, center: center)

// Остановить мониторинг
locationManager.stopMonitoring(identifier: "home")

// Остановить все геозоны
locationManager.stopMonitoringAllRegions()

// Подписка на уведомления
NotificationCenter.default.addObserver(
    forName: .locationDidEnterRegion,
    object: nil,
    queue: .main
) { notification in
    if let region = notification.userInfo?["region"] as? CLRegion {
        print("Вход в геозону: \(region.identifier)")
    }
}

NotificationCenter.default.addObserver(
    forName: .locationDidExitRegion,
    object: nil,
    queue: .main
) { notification in
    if let region = notification.userInfo?["region"] as? CLRegion {
        print("Выход из геозоны: \(region.identifier)")
    }
}
```

---

## 🔗 ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩИМ КОДОМ

### 1. Родительский контроль (FamilyLocationModal)

```swift
struct FamilyLocationModal: View {
    @StateObject private var locationManager = LocationManager.shared
    
    var body: some View {
        // ...
        .onAppear {
            // Запрос разрешения
            locationManager.requestAuthorization(always: true)
            
            // Запуск Significant-Change
            locationManager.startSignificantLocationChanges()
            
            // Загрузка и мониторинг геозон
            loadAndMonitorGeofences()
        }
    }
    
    private func loadAndMonitorGeofences() {
        // Загрузить геозоны из UserDefaults
        let geofences = loadGeofencesFromUserDefaults()
        
        // Получить координаты (из сохраненных данных или геокодирование)
        var coordinates: [UUID: CLLocationCoordinate2D] = [:]
        for geofence in geofences {
            // TODO: Получить координаты из сохраненных данных или геокодирование
            if let savedCoordinates = getSavedCoordinates(for: geofence.id) {
                coordinates[geofence.id] = savedCoordinates
            }
        }
        
        // Начать мониторинг
        locationManager.loadAndMonitorGeofences(geofences, coordinates: coordinates)
    }
}
```

### 2. Driving Reports

```swift
struct DrivingReportsModal: View {
    @StateObject private var locationManager = LocationManager.shared
    
    func startTrip() async {
        // Получить начальную точку
        do {
            let startLocation = try await locationManager.getCurrentLocation()
            // Сохранить для отчета
        } catch {
            print("Ошибка получения местоположения: \(error)")
        }
    }
}
```

### 3. Crash Detection

```swift
class CrashDetectionManager {
    private let locationManager = LocationManager.shared
    
    func setupCrashDetectionZone() {
        // Получить текущее местоположение
        Task {
            do {
                let location = try await locationManager.getCurrentLocation()
                
                // Создать геозону с радиусом 500 метров
                try locationManager.startMonitoring(
                    identifier: "crash_detection_zone",
                    center: location.coordinate,
                    radius: 500
                )
            } catch {
                print("Ошибка настройки геозоны: \(error)")
            }
        }
    }
}
```

### 4. Location Bubble и Requests

```swift
class PrivacyReportsViewModel {
    private let locationManager = LocationManager.shared
    
    func sendLocationForBubble() async {
        do {
            let location = try await locationManager.getCurrentLocation()
            // Отправить на сервер для генерации "пузыря"
            await sendToServer(location: location)
        } catch {
            print("Ошибка получения местоположения: \(error)")
        }
    }
    
    func allowLocationRequest(requestId: String) async {
        do {
            let location = try await locationManager.getCurrentLocation()
            // Отправить местоположение на сервер
            await sendLocationToServer(requestId: requestId, location: location)
        } catch {
            print("Ошибка получения местоположения: \(error)")
        }
    }
}
```

---

## 📊 ОТСЛЕЖИВАНИЕ СОСТОЯНИЯ

### Published свойства

```swift
// Текущее местоположение
@Published var currentLocation: CLLocation?

// Статус разрешения
@Published var authorizationStatus: CLAuthorizationStatus

// Активен ли Significant-Change
@Published var isMonitoringSignificantChanges: Bool

// Отслеживаемые геозоны
@Published var monitoredRegions: [String: CLCircularRegion]

// Последняя ошибка
@Published var lastError: LocationManagerError?

// Доступна ли геолокация
@Published var isLocationAvailable: Bool
```

### Использование в SwiftUI

```swift
struct LocationStatusView: View {
    @StateObject private var locationManager = LocationManager.shared
    
    var body: some View {
        VStack {
            if let location = locationManager.currentLocation {
                Text("Координаты: \(location.coordinate.latitude), \(location.coordinate.longitude)")
            }
            
            Text("Статус: \(locationManager.authorizationStatusString)")
            
            Text("Геозон: \(locationManager.activeGeofencesCount)")
            
            if let error = locationManager.lastError {
                Text("Ошибка: \(error.localizedDescription)")
                    .foregroundColor(.red)
            }
        }
    }
}
```

---

## ⚠️ ОБРАБОТКА ОШИБОК

### Типы ошибок

```swift
enum LocationManagerError {
    case authorizationDenied          // Разрешение отклонено
    case authorizationRestricted      // Разрешение ограничено
    case locationUnavailable          // Геолокация недоступна
    case significantChangeUnavailable // Significant-Change недоступен
    case tooManyRegions(maxAllowed: Int)  // Превышен лимит геозон
    case invalidRegion(radius: Double)    // Недопустимый радиус
    case regionMonitoringFailed(identifier: String)  // Ошибка мониторинга
}
```

### Пример обработки

```swift
do {
    try locationManager.startMonitoring(identifier: "home", center: center, radius: 50)
} catch LocationManagerError.invalidRegion(let radius) {
    print("Радиус \(radius) метров слишком мал. Минимум: 100 метров")
} catch LocationManagerError.tooManyRegions(let maxAllowed) {
    print("Превышен лимит геозон. Максимум: \(maxAllowed)")
} catch {
    print("Ошибка: \(error.localizedDescription)")
}
```

---

## 🔒 ПРАВИЛА iOS

### Что используется:

✅ **Significant-Change Location Service**
- Обновления при перемещении на 500+ метров
- Работает в фоне
- Не требует `location` в UIBackgroundModes

✅ **Region Monitoring**
- Отслеживание входа/выхода из геозон
- Работает в фоне
- Не требует `location` в UIBackgroundModes

✅ **One-time Location**
- Получение текущего местоположения
- Работает только когда приложение активно

### Что НЕ используется:

❌ **Persistent Location**
- Постоянное отслеживание каждую секунду
- Разряжает батарею
- Требует `location` в UIBackgroundModes

---

## 📝 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Родительский контроль

```swift
class ParentalControlLocationService {
    private let locationManager = LocationManager.shared
    
    func setupLocationTracking() {
        // 1. Запрос разрешения
        locationManager.requestAuthorization(always: true)
        
        // 2. Запуск Significant-Change
        locationManager.startSignificantLocationChanges()
        
        // 3. Загрузка геозон
        let geofences = loadGeofences()
        let coordinates = loadCoordinates()
        locationManager.loadAndMonitorGeofences(geofences, coordinates: coordinates)
        
        // 4. Подписка на уведомления
        NotificationCenter.default.addObserver(
            forName: .locationSignificantChange,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            self?.handleSignificantChange(notification)
        }
        
        NotificationCenter.default.addObserver(
            forName: .locationDidEnterRegion,
            object: nil,
            queue: .main
        ) { [weak self] notification in
            self?.handleRegionEntry(notification)
        }
    }
    
    private func handleSignificantChange(_ notification: Notification) {
        if let location = notification.userInfo?["location"] as? CLLocation {
            // Отправить на сервер
            sendLocationToServer(location: location)
        }
    }
    
    private func handleRegionEntry(_ notification: Notification) {
        if let region = notification.userInfo?["region"] as? CLRegion {
            // Отправить уведомление о входе в геозону
            sendRegionEntryNotification(regionIdentifier: region.identifier)
        }
    }
}
```

### Пример 2: Crash Detection

```swift
class CrashDetectionService {
    private let locationManager = LocationManager.shared
    
    func setupCrashDetection() async {
        // Получить текущее местоположение
        do {
            let location = try await locationManager.getCurrentLocation()
            
            // Создать геозону с радиусом 500 метров
            try locationManager.startMonitoring(
                identifier: "crash_detection_zone",
                center: location.coordinate,
                radius: 500
            )
        } catch {
            print("Ошибка настройки Crash Detection: \(error)")
        }
    }
    
    func getCurrentGeofence() -> CLLocationCoordinate2D? {
        // Получить центр текущей геозоны для отправки на сервер
        if let region = locationManager.monitoredRegions["crash_detection_zone"] as? CLCircularRegion {
            return region.center
        }
        return nil
    }
}
```

---

## ✅ ПРОВЕРКА ГОТОВНОСТИ

### Перед использованием проверьте:

1. ✅ Info.plist содержит `NSLocationWhenInUseUsageDescription`
2. ✅ Info.plist содержит `NSLocationAlwaysAndWhenInUseUsageDescription`
3. ✅ НЕТ `location` в UIBackgroundModes (для Significant-Change и Region Monitoring)
4. ✅ LocationManager.shared доступен

### Статус в проекте:

- ✅ LocationManager создан
- ✅ Соответствует правилам iOS
- ✅ Готов к использованию
- ✅ Интеграция с существующим кодом готова

---

**Последнее обновление:** 2026-01-11  
**Статус:** ✅ Готово к использованию
