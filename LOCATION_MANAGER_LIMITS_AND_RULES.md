# 📍 ЛИМИТЫ И ПРАВИЛА LocationManager

**Дата:** 2026-01-11  
**Версия:** 1.0.0

---

## 🎯 ОБЗОР

Документ описывает все лимиты, правила и ограничения LocationManager, и как они влияют на компоненты приложения.

---

## 1. SIGNIFICANT-CHANGE LOCATION SERVICE

### Что значит "доступна всегда на iOS"

**Проверка в коде:**
```swift
#if os(iOS)
// Significant-Change доступен на всех iOS устройствах
// Просто проверяем разрешение
#else
// Для других платформ проверяем доступность
if !CLLocationManager.significantLocationChangesMonitoringAvailable() {
    // Обработка ошибки
}
#endif
```

**Объяснение:**
- ✅ На iOS Significant-Change доступен **всегда** (с iOS 4.0+)
- ✅ Не требует проверки доступности на iOS
- ✅ Требует только разрешение `authorizedAlways`
- ⚠️ На других платформах (macOS, watchOS) может быть недоступен

**Влияние на компоненты:**

#### ✅ Родительский контроль
- **Использует:** Significant-Change + Region Monitoring
- **Статус:** ✅ Работает всегда на iOS
- **Требования:** Разрешение `authorizedAlways`
- **Ограничения:** Нет (доступен всегда)

#### ✅ Crash Detection
- **Использует:** Region Monitoring (500м радиус)
- **Статус:** ✅ Работает всегда на iOS
- **Требования:** Разрешение `authorizedAlways`
- **Ограничения:** Нет (доступен всегда)

---

## 2. ЛИМИТЫ ГЕОЗОН

### 2.1 Максимум геозон: 20

**Реализация в LocationManager:**
```swift
private let maxRegions = 20  // Максимум геозон в iOS

func startMonitoring(identifier: String, center: CLLocationCoordinate2D, radius: CLLocationDistance) throws {
    // Проверка лимита геозон
    guard monitoredRegions.count < maxRegions else {
        throw LocationManagerError.tooManyRegions(maxAllowed: maxRegions)
    }
    // ...
}
```

**Проверка:**
- ✅ Проверяется перед добавлением каждой геозоны
- ✅ Выбрасывает ошибку `LocationManagerError.tooManyRegions(maxAllowed: 20)`
- ✅ Свойство `canAddMoreGeofences` показывает, можно ли добавить еще

**Влияние на компоненты:**

#### Родительский контроль
- **Геозоны:** Дом, школа, секция, бабушка и т.д.
- **Лимит:** Максимум 20 геозон на устройстве
- **Проверка:** ✅ Автоматическая при добавлении
- **Ошибка:** Показывается пользователю при превышении

#### Crash Detection
- **Геозоны:** 1 геозона с радиусом 500м
- **Лимит:** ✅ Не превышает (использует только 1)
- **Проверка:** ✅ Автоматическая

**Пример использования:**
```swift
// Проверка перед добавлением
if locationManager.canAddMoreGeofences {
    try locationManager.startMonitoring(identifier: "home", center: center, radius: 100)
} else {
    print("⚠️ Достигнут лимит геозон (20)")
}
```

---

### 2.2 Минимальный радиус: 100 метров

**Реализация в LocationManager:**
```swift
private let minRegionRadius: CLLocationDistance = 100  // Минимум 100 метров

func startMonitoring(identifier: String, center: CLLocationCoordinate2D, radius: CLLocationDistance) throws {
    // Проверка радиуса
    guard radius >= minRegionRadius else {
        throw LocationManagerError.invalidRegion(radius: radius)
    }
    // ...
}
```

**Проверка:**
- ✅ Проверяется перед созданием каждой геозоны
- ✅ Выбрасывает ошибку `LocationManagerError.invalidRegion(radius: Double)`
- ✅ Автоматически увеличивает радиус до минимума: `max(minRegionRadius, geofence.radius)`

**Влияние на компоненты:**

#### Родительский контроль
- **Геозоны:** Дом (100м), школа (200м), секция (150м)
- **Минимум:** ✅ 100 метров (проверяется автоматически)
- **Если меньше:** Автоматически увеличивается до 100м

#### Crash Detection
- **Геозоны:** 500 метров (больше минимума)
- **Минимум:** ✅ Не нарушает (500 > 100)
- **Проверка:** ✅ Автоматическая

**Пример использования:**
```swift
// Попытка создать геозону с радиусом 50 метров
do {
    try locationManager.startMonitoring(identifier: "home", center: center, radius: 50)
} catch LocationManagerError.invalidRegion(let radius) {
    print("❌ Радиус \(radius) метров слишком мал. Минимум: 100 метров")
    // Автоматически увеличится до 100м при создании
}
```

---

## 3. ПРАВИЛА ДЛЯ КАЖДОГО КОМПОНЕНТА

### 3.1 Родительский контроль

**Использует:**
- ✅ Significant-Change Location Service (500+ метров)
- ✅ Region Monitoring (геозоны: дом, школа, секция)

**Лимиты:**
- ✅ Максимум 20 геозон (проверяется автоматически)
- ✅ Минимум 100 метров радиус (проверяется автоматически)
- ✅ Significant-Change доступен всегда на iOS

**Проверки:**
```swift
// При добавлении геозоны
func addGeofence(_ geofence: GeofenceItem, center: CLLocationCoordinate2D) {
    // 1. Проверка лимита (автоматически в LocationManager)
    guard locationManager.canAddMoreGeofences else {
        showError("Достигнут лимит геозон (20)")
        return
    }
    
    // 2. Проверка радиуса (автоматически в LocationManager)
    guard geofence.radius >= 100 else {
        showError("Минимальный радиус: 100 метров")
        return
    }
    
    // 3. Добавление (все проверки внутри)
    do {
        try locationManager.startMonitoring(geofence: geofence, center: center)
    } catch {
        showError(error.localizedDescription)
    }
}
```

---

### 3.2 Driving Reports

**Использует:**
- ✅ One-time location (при начале поездки)
- ✅ Continuous updates (только когда приложение активно)

**Лимиты:**
- ❌ Не использует геозоны (нет лимитов)
- ❌ Не использует Significant-Change (нет лимитов)
- ✅ Только разрешение `authorizedWhenInUse` или `authorizedAlways`

**Проверки:**
```swift
// При начале поездки
func startTrip() async {
    // Проверка разрешения
    guard locationManager.hasRequiredAuthorization() else {
        locationManager.requestAuthorization(always: false)
        return
    }
    
    // Получение местоположения (без лимитов)
    do {
        let location = try await locationManager.getCurrentLocation()
        // Начать поездку
    } catch {
        showError(error.localizedDescription)
    }
}
```

---

### 3.3 Crash Detection

**Использует:**
- ✅ Region Monitoring (1 геозона с радиусом 500м)

**Лимиты:**
- ✅ Максимум 20 геозон (использует только 1) ✅
- ✅ Минимум 100 метров (использует 500м) ✅
- ✅ Significant-Change не используется (нет лимитов)

**Проверки:**
```swift
// При настройке Crash Detection
func setupCrashDetectionZone() async {
    // 1. Получить текущее местоположение
    do {
        let location = try await locationManager.getCurrentLocation()
        
        // 2. Создать геозону 500м (все проверки внутри LocationManager)
        try locationManager.startMonitoring(
            identifier: "crash_detection_zone",
            center: location.coordinate,
            radius: 500  // Больше минимума (100м) ✅
        )
    } catch LocationManagerError.tooManyRegions {
        // Невозможно (используется только 1 геозона)
    } catch LocationManagerError.invalidRegion {
        // Невозможно (500 > 100) ✅
    } catch {
        showError(error.localizedDescription)
    }
}
```

---

### 3.4 Location Bubble

**Использует:**
- ✅ One-time location (для отправки на сервер)

**Лимиты:**
- ❌ Не использует геозоны (нет лимитов)
- ❌ Не использует Significant-Change (нет лимитов)
- ✅ Только разрешение `authorizedWhenInUse` или `authorizedAlways`

**Проверки:**
```swift
// При отправке местоположения
func sendLocationForBubble() async {
    // Проверка разрешения
    guard locationManager.hasRequiredAuthorization() else {
        locationManager.requestAuthorization(always: false)
        return
    }
    
    // Получение местоположения (без лимитов)
    do {
        let location = try await locationManager.getCurrentLocation()
        // Отправить на сервер
    } catch {
        showError(error.localizedDescription)
    }
}
```

---

### 3.5 Location Requests

**Использует:**
- ✅ One-time location (при разрешении запроса)

**Лимиты:**
- ❌ Не использует геозоны (нет лимитов)
- ❌ Не использует Significant-Change (нет лимитов)
- ✅ Только разрешение `authorizedWhenInUse` или `authorizedAlways`

**Проверки:**
```swift
// При разрешении запроса
func allowLocationRequest(requestId: String) async {
    // Проверка разрешения
    guard locationManager.hasRequiredAuthorization() else {
        locationManager.requestAuthorization(always: false)
        return
    }
    
    // Получение местоположения (без лимитов)
    do {
        let location = try await locationManager.getCurrentLocation()
        // Отправить на сервер
    } catch {
        showError(error.localizedDescription)
    }
}
```

---

## 4. СВОДНАЯ ТАБЛИЦА ЛИМИТОВ

| Компонент | Significant-Change | Region Monitoring | Лимит геозон | Минимум радиус | One-time Location |
|-----------|-------------------|-------------------|--------------|----------------|-------------------|
| **Родительский контроль** | ✅ Использует | ✅ Использует | ✅ 20 максимум | ✅ 100м минимум | ❌ Не использует |
| **Driving Reports** | ❌ Не использует | ❌ Не использует | ❌ Нет лимитов | ❌ Нет лимитов | ✅ Использует |
| **Crash Detection** | ❌ Не использует | ✅ Использует (1) | ✅ 20 максимум | ✅ 100м минимум | ✅ Использует |
| **Location Bubble** | ❌ Не использует | ❌ Не использует | ❌ Нет лимитов | ❌ Нет лимитов | ✅ Использует |
| **Location Requests** | ❌ Не использует | ❌ Не использует | ❌ Нет лимитов | ❌ Нет лимитов | ✅ Использует |

---

## 5. АВТОМАТИЧЕСКИЕ ПРОВЕРКИ

### Что проверяется автоматически:

1. ✅ **Лимит геозон (20 максимум)**
   - Проверяется в `startMonitoring()`
   - Выбрасывает `LocationManagerError.tooManyRegions`
   - Свойство `canAddMoreGeofences` для проверки

2. ✅ **Минимальный радиус (100 метров)**
   - Проверяется в `startMonitoring()`
   - Выбрасывает `LocationManagerError.invalidRegion`
   - Автоматически увеличивает до минимума

3. ✅ **Разрешение на геолокацию**
   - Проверяется во всех методах
   - Автоматически запрашивает при необходимости

4. ✅ **Доступность Significant-Change**
   - На iOS доступен всегда (проверка не нужна)
   - На других платформах проверяется

---

## 6. ОБРАБОТКА ОШИБОК

### Типы ошибок для лимитов:

```swift
enum LocationManagerError {
    case tooManyRegions(maxAllowed: Int)      // Превышен лимит 20 геозон
    case invalidRegion(radius: Double)        // Радиус меньше 100 метров
    // ...
}
```

### Пример обработки:

```swift
do {
    try locationManager.startMonitoring(identifier: "home", center: center, radius: 50)
} catch LocationManagerError.tooManyRegions(let maxAllowed) {
    showAlert("Достигнут лимит геозон. Максимум: \(maxAllowed)")
} catch LocationManagerError.invalidRegion(let radius) {
    showAlert("Радиус \(radius) метров слишком мал. Минимум: 100 метров")
} catch {
    showAlert("Ошибка: \(error.localizedDescription)")
}
```

---

## 7. РЕКОМЕНДАЦИИ

### Для разработчиков:

1. **Всегда проверяйте `canAddMoreGeofences`** перед добавлением геозоны
2. **Проверяйте радиус** перед созданием (минимум 100м)
3. **Обрабатывайте ошибки** `tooManyRegions` и `invalidRegion`
4. **Используйте Significant-Change** для родительского контроля (доступен всегда)

### Для пользователей:

1. **Максимум 20 геозон** на устройстве
2. **Минимум 100 метров** радиус геозоны
3. **Significant-Change** работает всегда на iOS (не требует проверки)

---

## ✅ ИТОГОВАЯ СВОДКА

### Лимиты iOS:

- ✅ **Максимум геозон:** 20 (проверяется автоматически)
- ✅ **Минимум радиус:** 100 метров (проверяется автоматически)
- ✅ **Significant-Change:** Доступен всегда на iOS (проверка не нужна)

### Влияние на компоненты:

- ✅ **Родительский контроль:** Использует оба лимита (20 геозон, 100м радиус)
- ✅ **Crash Detection:** Использует лимиты (1 геозона, 500м радиус)
- ✅ **Driving Reports:** Не использует лимиты (one-time location)
- ✅ **Location Bubble:** Не использует лимиты (one-time location)
- ✅ **Location Requests:** Не использует лимиты (one-time location)

---

**Последнее обновление:** 2026-01-11  
**Статус:** ✅ Все лимиты реализованы и проверяются автоматически
