import Foundation
import CoreLocation
import Combine
import AVFoundation
import Contacts
import CoreMotion

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
        let loc = LocalizationManager.shared
        switch self {
        case .authorizationDenied:
            return loc.localized("location_error_denied")
        case .authorizationRestricted:
            return loc.localized("location_error_restricted")
        case .locationUnavailable:
            return loc.localized("location_error_unavailable")
        case .significantChangeUnavailable:
            return loc.localized("location_error_significant_change_unavailable")
        case .tooManyRegions(let maxAllowed):
            return loc.localized("location_error_too_many_regions", maxAllowed)
        case .invalidRegion(let radius):
            return loc.localized("location_error_invalid_region", radius)
        case .regionMonitoringFailed(let identifier):
            return loc.localized("location_error_region_monitoring_failed", identifier)
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
    // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
    private var locationContinuationHasResumed = false
    private var locationRequestId: UInt64 = 0
    private var cancellables = Set<AnyCancellable>()
    
    // Константы iOS
    private let maxRegions = 20  // Максимум геозон в iOS
    private let minRegionRadius: CLLocationDistance = 50  // ✅ Минимум 50 метров (План 2026)
    
    // ✅ План 2026: Гибридный режим и Офлайн-буфер
    private let hybridTriggerRadius: CLLocationDistance = 1000 // 1 км для активации GPS
    private let highAccuracyDuration: TimeInterval = 180 // 3 минуты точного трекинга
    private var highAccuracyTimer: Timer?
    private let offlineBufferKey = "location_offline_buffer"
    private var isReporting: Bool = false
    
    // MARK: - Initialization
    
    override init() {
        super.init()
        // Настройка CLLocationManager на главном акторе
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
    /// - Parameter always: `false` по умолчанию (ep6-09) — Always только для фоновых сценариев.
    func requestAuthorization(always: Bool = false) {
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
    
    /// Upgrade path: Always — только если уже есть WhenInUse (ep6-09).
    func requestAlwaysUpgradeIfEligible() {
        let status = locationManager.authorizationStatus
        guard status == .authorizedWhenInUse else {
            if status == .notDetermined {
                requestAuthorization(always: false)
            }
            return
        }
        requestAuthorization(always: true)
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
            // Overlapping callers: finish the previous waiter, otherwise it leaks forever.
            if let previous = locationContinuation, !locationContinuationHasResumed {
                locationContinuation = nil
                previous.resume(throwing: LocationManagerError.locationUnavailable)
            }
            locationRequestId &+= 1
            let requestId = locationRequestId
            // ✅ BUILD 115: Сброс флага для нового запроса
            locationContinuationHasResumed = false
            locationContinuation = continuation
            locationManager.requestLocation()
            
            // Таймаут через 30 секунд
            Task {
                try? await Task.sleep(nanoseconds: 30_000_000_000)
                if requestId == locationRequestId,
                   let continuation = locationContinuation, !locationContinuationHasResumed {
                    locationContinuation = nil
                    locationContinuationHasResumed = true
                    continuation.resume(throwing: LocationManagerError.locationUnavailable)
                }
            }
        }
    }

    /// WAVE3 L6/L14 — precise fix only while setting a place (or SOS); then restores battery mode.
    func getCurrentLocationForPlaceSetup() async throws -> CLLocation {
        let previousAccuracy = locationManager.desiredAccuracy
        let previousFilter = locationManager.distanceFilter
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = kCLDistanceFilterNone
        defer {
            locationManager.desiredAccuracy = previousAccuracy
            locationManager.distanceFilter = previousFilter
        }
        return try await getCurrentLocation()
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
        
        let appliedRadius = max(minRegionRadius, geofence.radius)
        print("GEOFENCE_MONITOR_START id=\(geofence.id.uuidString) name=\(geofence.name) radius=\(Int(appliedRadius))")
        print("✅ LocationManager: Начало мониторинга геозоны '\(geofence.name)' (ID: \(geofence.id.uuidString), радиус: \(Int(appliedRadius))м)")
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
        
        print("GEOFENCE_MONITOR_START id=\(identifier) radius=\(Int(radius))")
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
    
    // MARK: - ✅ План 2026: Reporting & Offline Buffer
    
    struct LocationReport: Codable {
        let lat: Double
        let lon: Double
        let speed: Double?
        let timestamp: Date
    }
    
    /// Отправить текущую локацию на сервер с поддержкой офлайн-буфера
    func reportCurrentLocation(_ location: CLLocation) {
        // P0.4: trip sampling must run even when quiet-zone blocks family share/server.
        FamilyMapAutoTripTracker.note(location: location)

        // Канон B: в тихой зоне точку семье / на сервер не шлём.
        if FamilyMapQuietZoneStore.contains(location) {
            print("ℹ️ LocationManager: тихая зона — report пропущен (trip note already ran)")
            return
        }

        FamilyMapAutoShare.publishIfNeeded(location)

        let report = LocationReport(
            lat: location.coordinate.latitude,
            lon: location.coordinate.longitude,
            speed: location.speed >= 0 ? location.speed * 3.6 : nil, // Конвертация в км/ч
            timestamp: location.timestamp
        )
        
        // Добавляем в буфер
        saveToBuffer(report)
        
        // Пытаемся отправить весь буфер
        sendBuffer()
    }

    /// P0.4: while an auto-trip is open, prefer GPS over SLC coarse fixes.
    func boostAccuracyForActiveTrip() {
        beginTripTracking()
    }

    // MARK: - Trip tracking (Life360-style)

    nonisolated static let tripDepartureRegionId = "aladdin_trip_departure"
    private let tripDepartureRadius: CLLocationDistance = 150
    private let departureWatchDuration: TimeInterval = 5 * 60
    private var isTripTrackingActive = false
    private var isDepartureWatchActive = false

    /// `allowsBackgroundLocationUpdates = true` crashes without `location` in UIBackgroundModes.
    private var canTrackInBackground: Bool {
        let modes = Bundle.main.object(forInfoDictionaryKey: "UIBackgroundModes") as? [String] ?? []
        return modes.contains("location") && locationManager.authorizationStatus == .authorizedAlways
    }

    /// Continuous navigation-grade GPS for the whole trip, also with the screen locked.
    func beginTripTracking() {
        highAccuracyTimer?.invalidate()
        highAccuracyTimer = nil
        isTripTrackingActive = true
        isDepartureWatchActive = false
        stopMonitoringTripDeparture()
        if canTrackInBackground {
            locationManager.allowsBackgroundLocationUpdates = true
            locationManager.showsBackgroundLocationIndicator = false
        }
        locationManager.pausesLocationUpdatesAutomatically = false
        locationManager.activityType = .automotiveNavigation
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 15
        locationManager.startUpdatingLocation()
        print("TRIP_GPS begin background=\(canTrackInBackground)")
    }

    func ensureTripTracking() {
        guard !isTripTrackingActive else { return }
        beginTripTracking()
    }

    /// Trip closed → back to battery mode and arm a departure fence at the parking spot.
    func endTripTracking(parkedAt location: CLLocation?) {
        guard isTripTrackingActive else { return }
        isTripTrackingActive = false
        locationManager.allowsBackgroundLocationUpdates = false
        locationManager.pausesLocationUpdatesAutomatically = true
        locationManager.activityType = .other
        deactivateHighAccuracyMode()
        if let location {
            armTripDeparture(at: location)
        }
        print("TRIP_GPS end")
    }

    /// Leaving the parking spot wakes the app within ~150 m, long before the next SLC fix.
    func armTripDeparture(at location: CLLocation) {
        guard canTrackInBackground,
              CLLocationManager.isMonitoringAvailable(for: CLCircularRegion.self),
              location.horizontalAccuracy >= 0, location.horizontalAccuracy <= 200 else { return }
        stopMonitoringTripDeparture()
        let region = CLCircularRegion(
            center: location.coordinate,
            radius: tripDepartureRadius,
            identifier: Self.tripDepartureRegionId
        )
        region.notifyOnEntry = false
        region.notifyOnExit = true
        locationManager.startMonitoring(for: region)
        print("TRIP_GPS departure fence armed")
    }

    /// Parked with no fence yet (first launch, after a walk) → arm one at this spot.
    func armTripDepartureIfNeeded(at location: CLLocation) {
        guard !isTripTrackingActive, !isDepartureWatchActive,
              !locationManager.monitoredRegions.contains(where: { $0.identifier == Self.tripDepartureRegionId })
        else { return }
        armTripDeparture(at: location)
    }

    private func stopMonitoringTripDeparture() {
        for region in locationManager.monitoredRegions where region.identifier == Self.tripDepartureRegionId {
            locationManager.stopMonitoring(for: region)
        }
    }

    /// Woken by the departure fence: short GPS window so the auto tracker can see driving speed.
    private func startDepartureWatch() {
        guard !isTripTrackingActive else { return }
        stopMonitoringTripDeparture()
        if canTrackInBackground {
            locationManager.allowsBackgroundLocationUpdates = true
            locationManager.showsBackgroundLocationIndicator = false
        }
        locationManager.activityType = .automotiveNavigation
        isDepartureWatchActive = true
        activateHighAccuracyMode(duration: departureWatchDuration)
        print("TRIP_GPS departure watch")
    }
    
    private func saveToBuffer(_ report: LocationReport) {
        var buffer = getBuffer()
        buffer.append(report)
        
        // Лимит буфера (например, 1000 записей ~ 1 неделя SLC обновлений)
        if buffer.count > 1000 {
            buffer.removeFirst()
        }
        
        if let data = try? JSONEncoder().encode(buffer) {
            UserDefaults.standard.set(data, forKey: offlineBufferKey)
        }
    }
    
    private func getBuffer() -> [LocationReport] {
        guard let data = UserDefaults.standard.data(forKey: offlineBufferKey),
              let buffer = try? JSONDecoder().decode([LocationReport].self, from: data) else {
            return []
        }
        return buffer
    }
    
    private func sendBuffer() {
        guard !isReporting else { return }
        let buffer = getBuffer()
        guard !buffer.isEmpty else { return }
        
        isReporting = true
        
        // Отправляем записи по одной (или можно было бы батчем, если сервер поддерживает)
        // Для простоты и надежности плана 2026 — отправляем последнюю и очищаем, 
        // если сервер не поддерживает батчи.
        // Но мы сделали эндпоинт на одну запись.
        
        let report = buffer.last! // Берем самую свежую
        
        APIService.shared.reportLocation(latitude: report.lat, longitude: report.lon, speed: report.speed) { [weak self] result in
            guard let self = self else { return }
            self.isReporting = false
            
            switch result {
            case .success:
                print("✅ LocationManager: Локация успешно отправлена на сервер")
                // Очищаем буфер при успехе (в идеале — только отправленные записи)
                UserDefaults.standard.removeObject(forKey: self.offlineBufferKey)
            case .failure(let error):
                print("⚠️ LocationManager: Ошибка отправки локации (сохранено в буфер): \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - ✅ План 2026: Hybrid Mode Logic
    
    /// Проверка близости к геозонам для активации точного режима
    private func checkProximityAndBoostAccuracy(to location: CLLocation) {
        let regions = monitoredRegions.values
        var isNearAnyGeofence = false
        
        for region in regions {
            let center = CLLocation(latitude: region.center.latitude, longitude: region.center.longitude)
            let distance = location.distance(from: center)
            
            if distance <= hybridTriggerRadius {
                isNearAnyGeofence = true
                print("🎯 LocationManager: Обнаружена близость к геозоне '\(region.identifier)' (\(Int(distance))м). Активация GPS.")
                break
            }
        }
        
        if isNearAnyGeofence {
            activateHighAccuracyMode()
        }
    }
    
    private func activateHighAccuracyMode(duration: TimeInterval? = nil) {
        // Trip GPS is already on and must not be cut by a geofence-proximity timer.
        guard !isTripTrackingActive else { return }
        // Сбрасываем старый таймер
        highAccuracyTimer?.invalidate()
        
        // Включаем GPS
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 10 // Более частые обновления
        locationManager.startUpdatingLocation()
        
        // Выключаем через 3 минуты
        highAccuracyTimer = Timer.scheduledTimer(withTimeInterval: duration ?? highAccuracyDuration, repeats: false) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.deactivateHighAccuracyMode()
            }
        }
    }
    
    private func deactivateHighAccuracyMode() {
        guard !isTripTrackingActive else { return }
        isDepartureWatchActive = false
        if locationManager.allowsBackgroundLocationUpdates {
            locationManager.allowsBackgroundLocationUpdates = false
            locationManager.activityType = .other
        }
        print("🔋 LocationManager: Режим высокой точности завершен. Переход в эконом-режим.")
        locationManager.stopUpdatingLocation()
        locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        locationManager.distanceFilter = 100
        highAccuracyTimer?.invalidate()
        highAccuracyTimer = nil
    }
}

// MARK: - CLLocationManagerDelegate

extension LocationManager: CLLocationManagerDelegate {
    
    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        // Deferred/background delivery batches fixes; the trip track needs every one of them.
        let earlier = Array(locations.dropLast())
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            for fix in earlier {
                FamilyMapAutoTripTracker.note(location: fix)
            }
            self.currentLocation = location
            print("📍 LocationManager: Обновление местоположения: \(location.coordinate.latitude), \(location.coordinate.longitude)")
            
            // ✅ План 2026: Отправляем на сервер
            self.reportCurrentLocation(location)
            
            // ✅ BUILD 115: Если есть ожидающий continuation для one-time location
            if let continuation = self.locationContinuation, !self.locationContinuationHasResumed {
                self.locationContinuation = nil
                self.locationContinuationHasResumed = true
                continuation.resume(returning: location)
            } else if self.locationContinuation != nil && self.locationContinuationHasResumed {
                print("⚠️ CRITICAL: Attempted to resume location continuation twice in didUpdateLocations!")
            }
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            print("❌ LocationManager: Ошибка: \(error.localizedDescription)")
            
            // ✅ BUILD 115: Если есть ожидающий continuation, передаем ошибку
            if let continuation = self.locationContinuation, !self.locationContinuationHasResumed {
                self.locationContinuation = nil
                self.locationContinuationHasResumed = true
                continuation.resume(throwing: error)
            } else if self.locationContinuation != nil && self.locationContinuationHasResumed {
                print("⚠️ CRITICAL: Attempted to resume location continuation twice in didFailWithError!")
            }
            
            // Обработка специфичных ошибок
            if let clError = error as? CLError {
                switch clError.code {
                case .denied:
                    self.lastError = .authorizationDenied
                case .locationUnknown:
                    self.lastError = .locationUnavailable
                default:
                    break
                }
            }
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            self.authorizationStatus = status
            print("📍 LocationManager: Изменение статуса разрешения: \(self.authorizationStatusString)")
            
            // Если разрешение отозвано, останавливаем мониторинг
            if status == .denied || status == .restricted {
                self.stopSignificantLocationChanges()
                self.stopMonitoringAllRegions()
                self.lastError = status == .denied ? .authorizationDenied : .authorizationRestricted
            }
        }
    }
    
    // MARK: - Significant-Change Delegate
    
    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocationsForSignificantChanges locations: [CLLocation]) {
        guard let location = locations.last else { return }
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            self.currentLocation = location
            print("📍 LocationManager: Significant-Change: перемещение на 500+ метров")
            print("📍 LocationManager: Новое местоположение: \(location.coordinate.latitude), \(location.coordinate.longitude)")
            
            // ✅ План 2026: Проверяем близость к школам/дому для временного включения GPS
            self.checkProximityAndBoostAccuracy(to: location)
            
            // ✅ План 2026: Отправляем на сервер
            self.reportCurrentLocation(location)
            
            // Отправить уведомление о значительном изменении
            NotificationCenter.default.post(
                name: .locationSignificantChange,
                object: nil,
                userInfo: ["location": location]
            )
        }
    }
    
    // MARK: - Region Monitoring Delegate
    
    nonisolated func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion,
              region.identifier != LocationManager.tripDepartureRegionId else { return }
        Task { @MainActor in
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
            // fsl-05 — живая лента + пуш «школа»
            GeofenceEventStore.record(regionIdentifier: region.identifier, isArrival: true)
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }
        if region.identifier == LocationManager.tripDepartureRegionId {
            Task { @MainActor [weak self] in
                self?.startDepartureWatch()
            }
            return
        }
        Task { @MainActor in
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
            GeofenceEventStore.record(regionIdentifier: region.identifier, isArrival: false)
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, monitoringDidFailFor region: CLRegion?, withError error: Error) {
        Task { @MainActor [weak self] in
            guard let self = self, let region = region else { return }
            print("❌ LocationManager: Ошибка мониторинга геозоны '\(region.identifier)': \(error.localizedDescription)")
            self.lastError = .regionMonitoringFailed(identifier: region.identifier)
            
            // Удалить из списка отслеживаемых
            self.monitoredRegions.removeValue(forKey: region.identifier)
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, didStartMonitoringFor region: CLRegion) {
        // WAVE3 L2 — ask iOS for current inside/outside so UI is honest after cold start.
        manager.requestState(for: region)
        Task { @MainActor in
            print("✅ LocationManager: Мониторинг геозоны '\(region.identifier)' успешно запущен → requestState")
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didDetermineState state: CLRegionState, for region: CLRegion) {
        guard region.identifier != LocationManager.tripDepartureRegionId else { return }
        let stateLabel: String
        switch state {
        case .inside: stateLabel = "inside"
        case .outside: stateLabel = "outside"
        case .unknown: stateLabel = "unknown"
        @unknown default: stateLabel = "other"
        }
        Task { @MainActor in
            print("📍 LocationManager: state=\(stateLabel) region=\(region.identifier)")
            // UI-only — do NOT synthesize enter/exit push (would spam every launch if already inside).
            NotificationCenter.default.post(
                name: .locationDidDetermineRegionState,
                object: nil,
                userInfo: [
                    "region": region,
                    "state": stateLabel
                ]
            )
        }
    }
}

// MARK: - Sensitive permissions (ep5-09)

enum SensitivePermissionCoordinator {

    static func requestCameraIfNeeded() async -> Bool {
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        switch status {
        case .authorized:
            return true
        case .notDetermined:
            return await AVCaptureDevice.requestAccess(for: .video)
        default:
            return false
        }
    }

    static func requestContactsIfNeeded() async -> Bool {
        let status = CNContactStore.authorizationStatus(for: .contacts)
        switch status {
        case .authorized:
            return true
        case .notDetermined:
            return await withCheckedContinuation { continuation in
                CNContactStore().requestAccess(for: .contacts) { granted, _ in
                    continuation.resume(returning: granted)
                }
            }
        default:
            return false
        }
    }

    static func requestMotionIfNeeded() async -> Bool {
        guard CMMotionActivityManager.isActivityAvailable() else { return false }
        switch CMMotionActivityManager.authorizationStatus() {
        case .authorized:
            return true
        case .notDetermined:
            return await withCheckedContinuation { continuation in
                let manager = CMMotionActivityManager()
                manager.queryActivityStarting(
                    from: Date().addingTimeInterval(-60),
                    to: Date(),
                    to: .main
                ) { _, _ in
                    continuation.resume(returning: CMMotionActivityManager.authorizationStatus() == .authorized)
                }
            }
        default:
            return false
        }
    }
}

// Convenience alias — callers historically used LocationManager.requestMotionIfNeeded().
extension LocationManager {
    static func requestMotionIfNeeded() async -> Bool {
        await SensitivePermissionCoordinator.requestMotionIfNeeded()
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let locationSignificantChange = Notification.Name("locationSignificantChange")
    static let locationDidEnterRegion = Notification.Name("locationDidEnterRegion")
    static let locationDidExitRegion = Notification.Name("locationDidExitRegion")
    /// WAVE3 L2 — UI-only state after `requestState(for:)` (no synthetic push).
    static let locationDidDetermineRegionState = Notification.Name("locationDidDetermineRegionState")
}
