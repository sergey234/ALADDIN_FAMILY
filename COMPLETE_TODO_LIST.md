# 📋 ПОЛНЫЙ СПИСОК ОСТАВШИХСЯ ЗАДАЧ

**Дата:** 2026-01-11  
**Статус:** Все задачи для завершения проекта

---

## 🎯 ПРИОРИТЕТНЫЙ ПЛАН ДЕЙСТВИЙ

### 🔴 ВЫСОКИЙ ПРИОРИТЕТ (1-2 недели):

---

## 1. ⚠️ CRASH DETECTION КОМПОНЕНТ

### Задача 1.1: Создать CrashDetectionManager
- [ ] Создать `Core/Managers/CrashDetectionManager.swift`
- [ ] Импортировать `CoreMotion` и `CoreLocation`
- [ ] Реализовать `@MainActor class CrashDetectionManager: NSObject, ObservableObject`
- [ ] Добавить `@Published var isMonitoring: Bool = false`
- [ ] Добавить `@Published var crashDetected: Bool = false`
- [ ] Добавить `@Published var countdownSeconds: Int = 10`
- [ ] Добавить `private let motionManager = CMMotionManager()`
- [ ] Добавить `private let locationManager = LocationManager.shared`
- [ ] Добавить `private let apiService = APIService.shared`

### Задача 1.2: Интеграция с CoreMotion
- [ ] Реализовать `func startMonitoring()`
- [ ] Проверить доступность акселерометра (`motionManager.isAccelerometerAvailable`)
- [ ] Настроить интервал обновления (`motionManager.accelerometerUpdateInterval = 0.1`)
- [ ] Запустить обновления акселерометра (`motionManager.startAccelerometerUpdates`)
- [ ] Реализовать `func processAccelerometerData(_ data: CMAccelerometerData)`
- [ ] Вычислить G-силу: `sqrt(x² + y² + z²) / 9.8`
- [ ] Проверить порог G-силы (3.0G по умолчанию)
- [ ] Реализовать `func detectCrash()`
- [ ] Реализовать `func stopMonitoring()`

### Задача 1.3: Интеграция с LocationManager
- [ ] Использовать `LocationManager.shared.getCurrentLocation()` при обнаружении краша
- [ ] Настроить геозону через `startMonitoring(identifier:center:radius:)`
- [ ] Радиус: 500 метров (стандарт для Crash Detection)

### Задача 1.4: Отправка данных на сервер
- [ ] Реализовать `func sendSensorData(accelerometer:gyroscope:speed:location:)`
- [ ] Вызвать `POST /api/crash-detection/data` через APIService
- [ ] Обработать ответ сервера
- [ ] При обнаружении краша вызвать `sendCrashAlert()`

### Задача 1.5: Интеграция с NetworkProtectionViewModel
- [ ] Добавить `private let crashDetectionManager = CrashDetectionManager.shared` в ViewModel
- [ ] Обновить `func toggleCrashDetection(_ newValue: Bool)`:
  - [ ] При `newValue == true`: вызвать `crashDetectionManager.startMonitoring()`
  - [ ] При `newValue == false`: вызвать `crashDetectionManager.stopMonitoring()`
  - [ ] Вызвать `POST /api/crash-detection/start` при включении
  - [ ] Вызвать `POST /api/crash-detection/stop` при выключении

### Задача 1.6: Создать UI для обнаружения краша
- [ ] Создать `Shared/Components/Modals/CrashDetectionAlertModal.swift`
- [ ] Реализовать обратный отсчет (10 секунд)
- [ ] Добавить кнопку "Отменить"
- [ ] Добавить кнопку "Вызвать 112"
- [ ] Показывать модал при `crashDetected == true`
- [ ] Автоматически вызывать 112 после отсчета

### Задача 1.7: Добавить эндпоинты в AppConfig
- [ ] Добавить `static let crashDetectionSetup = "/api/crash-detection/setup"`
- [ ] Добавить `static let crashDetectionAlert = "/api/crash-detection/alert"`
- [ ] Добавить `static let crashDetectionStart = "/api/crash-detection/start"`
- [ ] Добавить `static let crashDetectionStop = "/api/crash-detection/stop"`
- [ ] Добавить `static let crashDetectionData = "/api/crash-detection/data"`
- [ ] Добавить `static let crashDetectionStatus = "/api/crash-detection/status"`

### Задача 1.8: Обновить APIService
- [ ] Заменить прямую строку в `setupCrashDetection()` на `AppConfig.Endpoint.crashDetectionSetup`
- [ ] Заменить прямую строку в `sendCrashAlert()` на `AppConfig.Endpoint.crashDetectionAlert`
- [ ] Добавить `func startCrashDetectionMonitoring(userId:completion:)` → `POST /api/crash-detection/start`
- [ ] Добавить `func stopCrashDetectionMonitoring(userId:completion:)` → `POST /api/crash-detection/stop`
- [ ] Добавить `func sendCrashDetectionData(userId:accelerometer:gyroscope:speed:location:completion:)` → `POST /api/crash-detection/data`
- [ ] Добавить `func getCrashDetectionStatus(userId:completion:)` → `GET /api/crash-detection/status`

### Задача 1.9: Добавить локализацию
- [ ] Добавить `crash_detection_monitoring_active` = "Мониторинг активен" / "Monitoring active"
- [ ] Добавить `crash_detection_crash_detected` = "Обнаружена авария!" / "Crash detected!"
- [ ] Добавить `crash_detection_countdown` = "Вызов 112 через %d сек" / "Calling 112 in %d sec"
- [ ] Добавить `crash_detection_cancel` = "Отменить" / "Cancel"
- [ ] Добавить `crash_detection_call_112` = "Вызвать 112" / "Call 112"
- [ ] Добавить `crash_detection_sensitivity` = "Чувствительность" / "Sensitivity"
- [ ] Добавить `crash_detection_sensitivity_low` = "Низкая" / "Low"
- [ ] Добавить `crash_detection_sensitivity_medium` = "Средняя" / "Medium"
- [ ] Добавить `crash_detection_sensitivity_high` = "Высокая" / "High"

---

## 2. ⚠️ ЭНДПОИНТЫ В APPCONFIG

### Задача 2.1: Добавить Location Bubble & Requests
- [ ] Добавить `static let locationBubble = "/reports/privacy/location/bubble"`
- [ ] Добавить `static let locationSend = "/reports/privacy/location/send"`

### Задача 2.2: Добавить Parental Control Geofences
- [ ] Добавить `static let geofences = "/api/v1/parental-control/location/geofences"`
- [ ] Добавить `static let geofenceTrack = "/api/v1/parental-control/location/track"`

### Задача 2.3: Добавить Driving Reports
- [ ] Добавить `static let drivingStart = "/reports/driving/start"`
- [ ] Добавить `static let drivingEnd = "/reports/driving/end"`

### Задача 2.4: Обновить APIService (заменить прямые строки)
- [ ] В `sendLocationBubble()`: заменить на `AppConfig.Endpoint.locationBubble`
- [ ] В `sendLocationForRequest()`: заменить на `AppConfig.Endpoint.locationSend`
- [ ] В `getGeofences()`: заменить на `AppConfig.Endpoint.geofences`
- [ ] В `createGeofence()`: заменить на `AppConfig.Endpoint.geofences`
- [ ] В `deleteGeofence()`: заменить на `AppConfig.Endpoint.geofences`
- [ ] В `trackLocation()`: заменить на `AppConfig.Endpoint.geofenceTrack`
- [ ] В `startDrivingTrip()`: заменить на `AppConfig.Endpoint.drivingStart`
- [ ] В `endDrivingTrip()`: заменить на `AppConfig.Endpoint.drivingEnd`

---

## 3. ⚠️ ЭНДПОИНТЫ НА СЕРВЕРЕ (10 эндпоинтов)

### Задача 3.1: Location Bubble & Requests (2 эндпоинта)
- [ ] Создать `POST /reports/privacy/location/bubble`
  - [ ] Принять `latitude`, `longitude`
  - [ ] Сгенерировать приблизительное местоположение (пузырь)
  - [ ] Вернуть `approximateLocation: {latitude, longitude, radius}`
- [ ] Создать `POST /reports/privacy/location/send`
  - [ ] Принять `requestId`, `latitude`, `longitude`
  - [ ] Сохранить координаты для запроса

### Задача 3.2: Parental Control Geofences (4 эндпоинта)
- [ ] Создать `GET /api/v1/parental-control/location/geofences`
  - [ ] Вернуть список геозон пользователя
- [ ] Создать `POST /api/v1/parental-control/location/geofences`
  - [ ] Принять `name`, `address`, `latitude`, `longitude`, `radius`
  - [ ] Создать геозону
- [ ] Создать `DELETE /api/v1/parental-control/location/geofences/{id}`
  - [ ] Удалить геозону по ID
- [ ] Создать `POST /api/v1/parental-control/location/track`
  - [ ] Принять `latitude`, `longitude`, `timestamp`
  - [ ] Сохранить обновление местоположения

### Задача 3.3: Driving Reports (2 эндпоинта)
- [ ] Создать `POST /reports/driving/start`
  - [ ] Принять `userId` (optional), `startLatitude`, `startLongitude`
  - [ ] Создать поездку
  - [ ] Вернуть `tripId`
- [ ] Создать `POST /reports/driving/end`
  - [ ] Принять `tripId`, `endLatitude`, `endLongitude`
  - [ ] Завершить поездку
  - [ ] Вернуть `report: DrivingReport`

### Задача 3.4: Crash Detection (2 эндпоинта - проверить работу)
- [ ] Проверить работу `POST /api/crash-detection/setup`
- [ ] Проверить работу `POST /api/crash-detection/alert`

---

## 4. ⚠️ DARK WEB СКАНИРОВАНИЕ - ПРОВЕРКА

### Задача 4.1: Проверка эндпоинта на сервере
- [ ] Проверить работает ли `POST /api/darkweb/scan_start`
- [ ] Проверить формат ответа
- [ ] Проверить обработку ошибок

### Задача 4.2: Улучшение обработки ошибок
- [ ] Обновить `DarkWebMonitoringViewModel.swift`
- [ ] Улучшить сообщения об ошибках:
  - [ ] `dark_web_error_server_not_available` для 404
  - [ ] `dark_web_error_server_error` для 500
  - [ ] `dark_web_error_scan_failed` для других ошибок

### Задача 4.3: Добавить логирование
- [ ] Добавить логирование в `startScan()`:
  - [ ] `print("🌑 DarkWebMonitoringViewModel: Запуск сканирования")`
  - [ ] `print("🌑 DarkWebMonitoringViewModel: Эндпоинт: \(AppConfig.Endpoint.darkWebScanStart)")`
  - [ ] Логировать успешные запросы
  - [ ] Логировать ошибки

---

## 📊 ИТОГОВАЯ СВОДКА ЗАДАЧ

### По категориям:

| Категория | Задач | Статус |
|-----------|-------|--------|
| **Crash Detection** | 9 задач | 🔴 0% |
| **AppConfig эндпоинты** | 4 задачи | 🟡 0% |
| **Эндпоинты на сервере** | 4 задачи | 🔴 0% |
| **Dark Web проверка** | 3 задачи | 🟡 0% |
| **ИТОГО** | **20 задач** | **0%** |

### По приоритетам:

| Приоритет | Задач | Время |
|-----------|-------|-------|
| 🔴 Высокий | 13 | 6-9 дней |
| 🟡 Средний | 7 | 1-2 дня |
| **ИТОГО** | **20** | **7-11 дней** |

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **Начать с Crash Detection (высокий приоритет):**
   - Создать `CrashDetectionManager.swift`
   - Интегрировать с `CoreMotion`
   - Добавить отправку данных на сервер

2. **Добавить эндпоинты в AppConfig (быстро, 1 час):**
   - Обновить `AppConfig.swift`
   - Обновить `APIService.swift`

3. **Добавить эндпоинты на сервере (4-7 дней):**
   - 10 новых эндпоинтов
   - Интеграция с SFM

4. **Проверить Dark Web (2 часа):**
   - Проверка эндпоинта
   - Улучшение ошибок

---

**Последнее обновление:** 2026-01-11  
**Следующий шаг:** Создать `CrashDetectionManager.swift`
