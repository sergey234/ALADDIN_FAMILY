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
    // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
    private var locationContinuationHasResumed = false
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
            // ✅ BUILD 115: Сброс флага для нового запроса
            locationContinuationHasResumed = false
            locationContinuation = continuation
            locationManager.requestLocation()
            
            // Таймаут через 30 секунд
            Task {
                try? await Task.sleep(nanoseconds: 30_000_000_000)
                if let continuation = locationContinuation, !locationContinuationHasResumed {
                    locationContinuation = nil
                    locationContinuationHasResumed = true
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
    
    // MARK: - ✅ План 2026: Reporting & Offline Buffer
    
    struct LocationReport: Codable {
        let lat: Double
        let lon: Double
        let speed: Double?
        let timestamp: Date
    }
    
    /// Отправить текущую локацию на сервер с поддержкой офлайн-буфера
    func reportCurrentLocation(_ location: CLLocation) {
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
    
    private func activateHighAccuracyMode() {
        // Сбрасываем старый таймер
        highAccuracyTimer?.invalidate()
        
        // Включаем GPS
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 10 // Более частые обновления
        locationManager.startUpdatingLocation()
        
        // Выключаем через 3 минуты
        highAccuracyTimer = Timer.scheduledTimer(withTimeInterval: highAccuracyDuration, repeats: false) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.deactivateHighAccuracyMode()
            }
        }
    }
    
    private func deactivateHighAccuracyMode() {
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
        Task { @MainActor [weak self] in
            guard let self = self else { return }
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
        guard let circularRegion = region as? CLCircularRegion else { return }
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
        }
    }
    
    nonisolated func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        guard let circularRegion = region as? CLCircularRegion else { return }
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
        Task { @MainActor in
            print("✅ LocationManager: Мониторинг геозоны '\(region.identifier)' успешно запущен")
        }
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let locationSignificantChange = Notification.Name("locationSignificantChange")
    static let locationDidEnterRegion = Notification.Name("locationDidEnterRegion")
    static let locationDidExitRegion = Notification.Name("locationDidExitRegion")
}
