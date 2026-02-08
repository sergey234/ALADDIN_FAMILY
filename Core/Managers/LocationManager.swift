import Foundation
import CoreLocation
import Combine

/**
 * 📍 LocationManager
 * Централизованное управление геолокацией для всех функций приложения
 * Соответствует всем правилам iOS для работы с геолокацией
 * 
 * Функциональность:
 * - Запрос разрешений на геолокацию
 * - Получение текущего местоположения
 * - Significant-Change Location Service (500+ метров)
 * - Region Monitoring (геозоны)
 * - One-time location
 * - Обработка ошибок и логирование
 */

// MARK: - Location Manager Error

enum LocationManagerError: LocalizedError {
    case authorizationDenied
    case authorizationRestricted
    case locationUnavailable
    case significantChangeUnavailable
    case tooManyRegions(maxAllowed: Int)
    case invalidRegion(radius: Double)
    case regionMonitoringFailed(identifier: String)
    
    var errorDescription: String? {
        switch self {
        case .authorizationDenied:
            return "Доступ к геолокации запрещен. Разрешите доступ в настройках."
        case .authorizationRestricted:
            return "Доступ к геолокации ограничен."
        case .locationUnavailable:
            return "Геолокация недоступна на этом устройстве."
        case .significantChangeUnavailable:
            return "Significant-Change Location Service недоступен."
        case .tooManyRegions(let maxAllowed):
            return "Превышен лимит геозон. Максимум: \(maxAllowed)."
        case .invalidRegion(let radius):
            return "Недопустимый радиус геозоны: \(radius) метров. Минимум: 100 метров."
        case .regionMonitoringFailed(let identifier):
            return "Не удалось начать мониторинг геозоны: \(identifier)."
        }
    }
}

// MARK: - Location Manager

@MainActor
class LocationManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = LocationManager()
    
    // MARK: - Published Properties
    
    /// Текущее местоположение
    @Published var currentLocation: CLLocation?
    
    /// Статус разрешения на геолокацию
    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    
    /// Активен ли мониторинг Significant-Change
    @Published var isMonitoringSignificantChanges: Bool = false
    
    /// Список отслеживаемых геозон
    @Published var monitoredRegions: [String: CLCircularRegion] = [:]
    
    /// Последняя ошибка
    @Published var lastError: LocationManagerError?
    
    /// Доступна ли геолокация
    @Published var isLocationAvailable: Bool = false
    
    // MARK: - Private Properties
    
    private let locationManager = CLLocationManager()
    private var locationContinuation: CheckedContinuation<CLLocation, Error>?
    private var cancellables = Set<AnyCancellable>()
    
    // Константы iOS
    private let maxRegions = 20  // Максимум геозон в iOS
    private let minRegionRadius: CLLocationDistance = 100  // Минимум 100 метров
    
    // MARK: - Initialization
    
    nonisolated override init() {
        super.init()
        // Настройка locationManager (не требует MainActor)
        locationManager.delegate = self
        
        // Настройки точности (экономия батареи)
        locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        locationManager.distanceFilter = 100  // Обновления при перемещении на 100+ метров
        
        // Инициализация через Task для @Published свойств
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            // Проверка доступности
            self.isLocationAvailable = CLLocationManager.locationServicesEnabled()
            
            // Инициализация статуса разрешения
            self.authorizationStatus = self.locationManager.authorizationStatus
            
            print("📍 LocationManager: Инициализирован")
            print("📍 LocationManager: Геолокация доступна: \(self.isLocationAvailable)")
            print("📍 LocationManager: Статус разрешения: \(self.authorizationStatusString)")
        }
    }
    
    // MARK: - Authorization
    
    /// Запрос разрешения на геолокацию
    /// - Parameter always: Если true, запрашивает "Always" разрешение (для фона)
    func requestAuthorization(always: Bool = true) {
        let currentStatus = locationManager.authorizationStatus
        
        switch currentStatus {
        case .notDetermined:
            print("📍 LocationManager: Запрос разрешения (always: \(always))")
            if always {
                locationManager.requestAlwaysAuthorization()
            } else {
                locationManager.requestWhenInUseAuthorization()
            }
            
        case .denied, .restricted:
            print("⚠️ LocationManager: Разрешение отклонено или ограничено")
            lastError = currentStatus == .denied ? .authorizationDenied : .authorizationRestricted
            
        case .authorizedWhenInUse:
            if always {
                print("📍 LocationManager: Запрос Always разрешения (текущее: WhenInUse)")
                locationManager.requestAlwaysAuthorization()
            } else {
                print("✅ LocationManager: Разрешение WhenInUse уже получено")
            }
            
        case .authorizedAlways:
            print("✅ LocationManager: Разрешение Always уже получено")
            
        @unknown default:
            print("⚠️ LocationManager: Неизвестный статус разрешения")
        }
    }
    
    /// Проверка, есть ли необходимое разрешение
    func hasRequiredAuthorization(forBackground: Bool = false) -> Bool {
        let status = locationManager.authorizationStatus
        if forBackground {
            return status == .authorizedAlways
        } else {
            return status == .authorizedWhenInUse || status == .authorizedAlways
        }
    }
    
    // MARK: - Current Location
    
    /// Получить текущее местоположение (one-time)
    /// - Returns: CLLocation или ошибку
    func getCurrentLocation() async throws -> CLLocation {
        guard isLocationAvailable else {
            throw LocationManagerError.locationUnavailable
        }
        
        guard hasRequiredAuthorization() else {
            throw LocationManagerError.authorizationDenied
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            locationContinuation = continuation
            locationManager.requestLocation()
            
            // Таймаут через 30 секунд
            Task {
                try? await Task.sleep(nanoseconds: 30_000_000_000)
                if locationContinuation != nil {
                    locationContinuation = nil
                    continuation.resume(throwing: LocationManagerError.locationUnavailable)
                }
            }
        }
    }
    
    /// Начать постоянные обновления местоположения (только когда приложение активно)
    func startUpdatingLocation() {
        guard isLocationAvailable else {
            print("⚠️ LocationManager: Геолокация недоступна")
            lastError = .locationUnavailable
            return
        }
        
        guard hasRequiredAuthorization() else {
            print("⚠️ LocationManager: Нет разрешения на геолокацию")
            requestAuthorization(always: false)
            return
        }
        
        print("📍 LocationManager: Начало обновлений местоположения")
        locationManager.startUpdatingLocation()
    }
    
    /// Остановить обновления местоположения
    func stopUpdatingLocation() {
        print("📍 LocationManager: Остановка обновлений местоположения")
        locationManager.stopUpdatingLocation()
    }
    
    // MARK: - Significant-Change Location Service
    
    /// Начать мониторинг значительных изменений местоположения (500+ метров)
    /// Работает в фоне, не требует location в UIBackgroundModes
    func startSignificantLocationChanges() {
        // Проверка доступности (метод доступен с iOS 4.0)
        // Используем проверку через доступность метода
        #if os(iOS)
        // Significant-Change доступен на всех iOS устройствах
        // Просто проверяем разрешение
        #else
        // Для других платформ проверяем доступность
        if !CLLocationManager.significantLocationChangesMonitoringAvailable() {
            print("⚠️ LocationManager: Significant-Change недоступен")
            lastError = .significantChangeUnavailable
            return
        }
        #endif
        
        guard hasRequiredAuthorization(forBackground: true) else {
            print("⚠️ LocationManager: Требуется Always разрешение для Significant-Change")
            requestAuthorization(always: true)
            return
        }
        
        guard !isMonitoringSignificantChanges else {
            print("📍 LocationManager: Significant-Change уже активен")
            return
        }
        
        print("📍 LocationManager: Запуск Significant-Change Location Service")
        locationManager.startMonitoringSignificantLocationChanges()
        isMonitoringSignificantChanges = true
    }
    
    /// Остановить мониторинг значительных изменений
    func stopSignificantLocationChanges() {
        guard isMonitoringSignificantChanges else {
            return
        }
        
        print("📍 LocationManager: Остановка Significant-Change Location Service")
        locationManager.stopMonitoringSignificantLocationChanges()
        isMonitoringSignificantChanges = false
    }
    
    // MARK: - Region Monitoring (Geofencing)
    
    /// Начать мониторинг геозоны с координатами
    /// - Parameters:
    ///   - geofence: Геозона для мониторинга
    ///   - center: Центр геозоны (координаты)
    func startMonitoring(geofence: GeofenceItem, center: CLLocationCoordinate2D) throws {
        // Проверка лимита геозон
        guard monitoredRegions.count < maxRegions else {
            throw LocationManagerError.tooManyRegions(maxAllowed: maxRegions)
        }
        
        // Проверка радиуса
        guard geofence.radius >= minRegionRadius else {
            throw LocationManagerError.invalidRegion(radius: geofence.radius)
        }
        
        guard hasRequiredAuthorization(forBackground: true) else {
            print("⚠️ LocationManager: Требуется Always разрешение для Region Monitoring")
            requestAuthorization(always: true)
            throw LocationManagerError.authorizationDenied
        }
        
        // Создание региона
        let region = CLCircularRegion(
            center: center,
            radius: max(minRegionRadius, geofence.radius),
            identifier: geofence.id.uuidString
        )
        
        region.notifyOnEntry = true
        region.notifyOnExit = true
        
        locationManager.startMonitoring(for: region)
        monitoredRegions[geofence.id.uuidString] = region
        
        print("✅ LocationManager: Начало мониторинга геозоны '\(geofence.name)' (ID: \(geofence.id.uuidString))")
    }
    
    /// Начать мониторинг геозоны с координатами
    /// - Parameters:
    ///   - identifier: Идентификатор геозоны
    ///   - center: Центр геозоны
    ///   - radius: Радиус в метрах
    func startMonitoring(identifier: String, center: CLLocationCoordinate2D, radius: CLLocationDistance) throws {
        // Проверка лимита
        guard monitoredRegions.count < maxRegions else {
            throw LocationManagerError.tooManyRegions(maxAllowed: maxRegions)
        }
        
        // Проверка радиуса
        guard radius >= minRegionRadius else {
            throw LocationManagerError.invalidRegion(radius: radius)
        }
        
        guard hasRequiredAuthorization(forBackground: true) else {
            print("⚠️ LocationManager: Требуется Always разрешение для Region Monitoring")
            requestAuthorization(always: true)
            throw LocationManagerError.authorizationDenied
        }
        
        // Проверка, не мониторится ли уже эта геозона
        guard monitoredRegions[identifier] == nil else {
            print("⚠️ LocationManager: Геозона '\(identifier)' уже отслеживается")
            return
        }
        
        let region = CLCircularRegion(
            center: center,
            radius: radius,
            identifier: identifier
        )
        
        region.notifyOnEntry = true
        region.notifyOnExit = true
        
        locationManager.startMonitoring(for: region)
        monitoredRegions[identifier] = region
        
        print("✅ LocationManager: Начало мониторинга геозоны '\(identifier)' (радиус: \(radius)м)")
    }
    
    /// Остановить мониторинг геозоны
    /// - Parameter identifier: Идентификатор геозоны
    func stopMonitoring(identifier: String) {
        guard let region = monitoredRegions[identifier] else {
            print("⚠️ LocationManager: Геозона '\(identifier)' не отслеживается")
            return
        }
        
        locationManager.stopMonitoring(for: region)
        monitoredRegions.removeValue(forKey: identifier)
        
        print("📍 LocationManager: Остановка мониторинга геозоны '\(identifier)'")
    }
    
    /// Остановить мониторинг всех геозон
    func stopMonitoringAllRegions() {
        for (_, region) in monitoredRegions {
            locationManager.stopMonitoring(for: region)
        }
        monitoredRegions.removeAll()
        print("📍 LocationManager: Остановка мониторинга всех геозон")
    }
    
    /// Загрузить геозоны из настроек и начать мониторинг
    /// - Parameters:
    ///   - geofences: Список геозон
    ///   - coordinates: Словарь координат для каждой геозоны [geofenceId: CLLocationCoordinate2D]
    func loadAndMonitorGeofences(_ geofences: [GeofenceItem], coordinates: [UUID: CLLocationCoordinate2D] = [:]) {
        // Остановить текущий мониторинг
        stopMonitoringAllRegions()
        
        // Начать мониторинг новых геозон
        var monitoredCount = 0
        for geofence in geofences {
            if let center = coordinates[geofence.id] {
                do {
                    try startMonitoring(geofence: geofence, center: center)
                    monitoredCount += 1
                } catch {
                    print("❌ LocationManager: Ошибка мониторинга геозоны '\(geofence.name)': \(error.localizedDescription)")
                }
            } else {
                print("⚠️ LocationManager: Геозона '\(geofence.name)' пропущена (нет координат)")
            }
        }
        
        print("📍 LocationManager: Загружено \(geofences.count) геозон, активно отслеживается: \(monitoredCount)")
    }
    
    // MARK: - Helper Properties
    
    /// Строковое представление статуса разрешения
    var authorizationStatusString: String {
        switch authorizationStatus {
        case .notDetermined: return "Не определен"
        case .restricted: return "Ограничено"
        case .denied: return "Отклонено"
        case .authorizedWhenInUse: return "Когда приложение активно"
        case .authorizedAlways: return "Всегда"
        @unknown default: return "Неизвестно"
        }
    }
    
    /// Количество активных геозон
    var activeGeofencesCount: Int {
        monitoredRegions.count
    }
    
    /// Можно ли добавить еще геозон
    var canAddMoreGeofences: Bool {
        monitoredRegions.count < maxRegions
    }
}

// MARK: - CLLocationManagerDelegate

extension LocationManager: CLLocationManagerDelegate {
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        
        currentLocation = location
        print("📍 LocationManager: Обновление местоположения: \(location.coordinate.latitude), \(location.coordinate.longitude)")
        
        // Если есть ожидающий continuation для one-time location
        if let continuation = locationContinuation {
            locationContinuation = nil
            continuation.resume(returning: location)
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("❌ LocationManager: Ошибка: \(error.localizedDescription)")
        
        // Если есть ожидающий continuation, передаем ошибку
        if let continuation = locationContinuation {
            locationContinuation = nil
            continuation.resume(throwing: error)
        }
        
        // Обработка специфичных ошибок
        if let clError = error as? CLError {
            switch clError.code {
            case .denied:
                lastError = .authorizationDenied
            case .locationUnknown:
                lastError = .locationUnavailable
            default:
                break
            }
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        authorizationStatus = status
        print("📍 LocationManager: Изменение статуса разрешения: \(authorizationStatusString)")
        
        // Если разрешение отозвано, останавливаем мониторинг
        if status == .denied || status == .restricted {
            stopSignificantLocationChanges()
            stopMonitoringAllRegions()
            lastError = status == .denied ? .authorizationDenied : .authorizationRestricted
        }
    }
    
    // MARK: - Significant-Change Delegate
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocationsForSignificantChanges locations: [CLLocation]) {
        guard let location = locations.last else { return }
        
        currentLocation = location
        print("📍 LocationManager: Significant-Change: перемещение на 500+ метров")
        print("📍 LocationManager: Новое местоположение: \(location.coordinate.latitude), \(location.coordinate.longitude)")
        
        // Отправить уведомление о значительном изменении
        NotificationCenter.default.post(
            name: .locationSignificantChange,
            object: nil,
            userInfo: ["location": location]
        )
    }
    
    // MARK: - Region Monitoring Delegate
    
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }
        
        print("✅ LocationManager: Вход в геозону '\(region.identifier)'")
        print("📍 LocationManager: Центр: \(circularRegion.center.latitude), \(circularRegion.center.longitude)")
        
        // Отправить уведомление о входе в геозону
        NotificationCenter.default.post(
            name: .locationDidEnterRegion,
            object: nil,
            userInfo: [
                "region": region,
                "center": circularRegion.center
            ]
        )
    }
    
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }
        
        print("✅ LocationManager: Выход из геозоны '\(region.identifier)'")
        print("📍 LocationManager: Центр: \(circularRegion.center.latitude), \(circularRegion.center.longitude)")
        
        // Отправить уведомление о выходе из геозоны
        NotificationCenter.default.post(
            name: .locationDidExitRegion,
            object: nil,
            userInfo: [
                "region": region,
                "center": circularRegion.center
            ]
        )
    }
    
    func locationManager(_ manager: CLLocationManager, monitoringDidFailFor region: CLRegion?, withError error: Error) {
        if let region = region {
            print("❌ LocationManager: Ошибка мониторинга геозоны '\(region.identifier)': \(error.localizedDescription)")
            lastError = .regionMonitoringFailed(identifier: region.identifier)
            
            // Удалить из списка отслеживаемых
            monitoredRegions.removeValue(forKey: region.identifier)
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didStartMonitoringFor region: CLRegion) {
        print("✅ LocationManager: Мониторинг геозоны '\(region.identifier)' успешно запущен")
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let locationSignificantChange = Notification.Name("locationSignificantChange")
    static let locationDidEnterRegion = Notification.Name("locationDidEnterRegion")
    static let locationDidExitRegion = Notification.Name("locationDidExitRegion")
}
