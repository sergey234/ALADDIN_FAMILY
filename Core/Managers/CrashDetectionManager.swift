import Foundation
import CoreMotion
import CoreLocation
import Combine

/// Абстракция для `NetworkProtectionViewModel` (вариант B: сначала локальный мониторинг, затем сервер).
@MainActor
protocol CrashDetectionControlling: AnyObject {
    func startMonitoring() async throws
    func stopMonitoring() async throws
    var isCrashDetectionSupportedOnCurrentDevice: Bool { get }
    var crashDetectionUnsupportedReason: String? { get }
}

/**
 * 🚨 CrashDetectionManager
 * Управление обнаружением аварий через акселерометр и гироскоп
 * Интеграция с CoreMotion для мониторинга G-силы
 * Автоматический вызов экстренных служб при обнаружении краша
 */

// MARK: - Crash Severity

enum CrashSeverity: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
}

// MARK: - Crash Detection Sensitivity

enum CrashDetectionSensitivity: String, Codable, CaseIterable {
    case low = "low"       // G > 4.0, менее чувствительный
    case medium = "medium" // G > 3.0, стандартный
    case high = "high"     // G > 2.0, более чувствительный

    var gForceThreshold: Double {
        switch self {
        case .low: return 4.0
        case .medium: return 3.0
        case .high: return 2.0
        }
    }

    var displayName: String {
        switch self {
        case .low: return "Низкая (G > 4.0)"
        case .medium: return "Средняя (G > 3.0)"
        case .high: return "Высокая (G > 2.0)"
        }
    }
}

// MARK: - Crash Detection Manager

@MainActor
class CrashDetectionManager: NSObject, ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = CrashDetectionManager()
    
    // MARK: - Published Properties
    
    @Published var isMonitoring: Bool = false
    @Published var crashDetected: Bool = false
    @Published var countdownSeconds: Int = 10
    @Published var lastGForce: Double = 0.0
    @Published var lastError: Error?
    
    // Данные последнего обнаруженного краша
    var lastDetectedGForce: Double? = nil
    var lastDetectedSpeed: Double? = nil
    
    // MARK: - Private Properties
    
    private let motionManager = CMMotionManager()
    private let locationManager = LocationManager.shared
    private let apiService = APIService.shared
    private var countdownTimer: Timer?
    private var monitoringTask: Task<Void, Never>?
    private var sendCounter: Int = 0 // Счетчик для оптимизации отправки данных
    
    // Конфигурация
    private var sensitivity: CrashDetectionSensitivity = .medium
    private let countdownDuration: Int = 10 // Обратный отсчет в секундах
    private let updateInterval: TimeInterval = 0.1 // Интервал обновления (100ms)
    private let dataSendInterval: Int = 50 // Отправка данных каждые 5 секунд (50 * 0.1 сек) - оптимизация производительности
    private let speedThreshold: Double = 50.0 // Минимальная скорость для активации мониторинга (km/h)
    private var isSpeedMonitoringActive = false
    private var speedMonitoringTask: Task<Void, Never>?
    
    // MARK: - Device capability flags
    
    var isCrashDetectionSupportedOnCurrentDevice: Bool {
        CMMotionManager().isAccelerometerAvailable
    }
    
    var crashDetectionUnsupportedReason: String? {
        guard !isCrashDetectionSupportedOnCurrentDevice else { return nil }
        return "Crash Detection недоступен на этом устройстве: отсутствует акселерометр."
    }

    // Конфигурация геозоны и обнаружения
    private let geofenceRadius: Double = 1000.0 // Радиус геозоны в метрах
    private var currentGForceThreshold: Double {
        return sensitivity.gForceThreshold
    }
    
    // MARK: - Diagnostics (synthetic crash pipeline)

    /// Синтетический сценарий: цепочка как при ДТП, без показаний реального акселерометра (только отладка / DEBUG-UI).
    private func runSyntheticCrashScenario(gForce: Double) async {
        guard !crashDetected else { return }

        print("🚨 CrashDetectionManager: SYNTHETIC crash scenario G-сила: \(String(format: "%.2f", gForce))")

        crashDetected = true

        // Получить текущее местоположение
        guard let location = try? await locationManager.getCurrentLocation() else {
            print("❌ CrashDetectionManager: Synthetic scenario — нет местоположения")
            return
        }

        // Определить серьезность (для теста - high)
        let severity = CrashSeverity.high

        // Отправить алерт на сервер
        do {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
                var hasResumed = false
                
                apiService.sendCrashAlert(
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude,
                    severity: severity.rawValue
                ) { result in
                    guard !hasResumed else {
                        print("⚠️ CRITICAL: Attempted to resume crash alert continuation twice!")
                        return
                    }
                    hasResumed = true
                    
                    switch result {
                    case .success:
                        continuation.resume()
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }
            print("✅ CrashDetectionManager: Synthetic scenario — алерт отправлен")
        } catch {
            print("❌ CrashDetectionManager: Synthetic scenario — ошибка алерта: \(error.localizedDescription)")
        }

        // Запустить обратный отсчет
        startCountdown()
    }

    // MARK: - Initialization
    
    nonisolated override init() {
        super.init()
        Task { @MainActor in
            self.setupMotionManager()
        }
    }
    
    private func setupMotionManager() {
        motionManager.accelerometerUpdateInterval = updateInterval
        motionManager.gyroUpdateInterval = updateInterval
        print("🚨 CrashDetectionManager: Инициализирован")
    }
    
    // MARK: - Public Methods

    // MARK: - Settings Management

    /// Установить чувствительность обнаружения аварий
    func setSensitivity(_ sensitivity: CrashDetectionSensitivity) {
        self.sensitivity = sensitivity
        print("🚨 CrashDetectionManager: Чувствительность установлена на \(sensitivity.rawValue) (G > \(sensitivity.gForceThreshold))")
    }

    /// Получить текущую чувствительность
    func getSensitivity() -> CrashDetectionSensitivity {
        return sensitivity
    }

    /// Получить порог G-силы для текущей чувствительности
    func getCurrentGForceThreshold() -> Double {
        return sensitivity.gForceThreshold
    }

    // MARK: - Battery Optimization Methods

    /// Запустить мониторинг скорости для оптимизации батареи
    private func startSpeedMonitoring() {
        guard !isSpeedMonitoringActive else { return }

        isSpeedMonitoringActive = true
        print("🔋 CrashDetectionManager: Запущен мониторинг скорости (>50km/h)")

        speedMonitoringTask = Task {
            await self.performSpeedMonitoring()
        }
    }

    private func performSpeedMonitoring() async {
        while !Task.isCancelled && isSpeedMonitoringActive {
            do {
                // Получаем текущую скорость
                let speedKmh = try await getCurrentSpeedKmh()

                if speedKmh > speedThreshold {
                    // Высокая скорость - включаем датчики
                    if !motionManager.isAccelerometerActive {
                        await MainActor.run {
                            startAccelerometerUpdates()
                        }
                        print("🚗 CrashDetectionManager: Датчики активированы (скорость: \(Int(speedKmh))km/h)")
                    }
                } else {
                    // Низкая скорость - отключаем датчики для экономии батареи
                    if motionManager.isAccelerometerActive {
                        await MainActor.run {
                            motionManager.stopAccelerometerUpdates()
                            motionManager.stopGyroUpdates()
                        }
                        print("🔋 CrashDetectionManager: Датчики отключены для экономии батареи (скорость: \(Int(speedKmh))km/h)")
                    }
                }

                // Проверяем скорость каждые 5 секунд
                try await Task.sleep(nanoseconds: 5_000_000_000) // 5 секунд

            } catch {
                print("⚠️ CrashDetectionManager: Ошибка мониторинга скорости: \(error.localizedDescription)")
                do {
                    try await Task.sleep(nanoseconds: 10_000_000_000) // Ждем 10 секунд при ошибке
                } catch {
                    // Игнорируем ошибку sleep
                }
            }
        }
    }

    /// Остановить мониторинг скорости
    private func stopSpeedMonitoring() {
        isSpeedMonitoringActive = false
        speedMonitoringTask?.cancel()
        speedMonitoringTask = nil
        print("🔋 CrashDetectionManager: Мониторинг скорости остановлен")
    }

    /// Получить текущую скорость в km/h
    private func getCurrentSpeedKmh() async throws -> Double {
        // Получаем текущую скорость через LocationManager
        let location = try await locationManager.getCurrentLocation()

        // Конвертируем m/s в km/h
        let speedMs = location.speed // m/s
        let speedKmh = speedMs >= 0 ? speedMs * 3.6 : 0.0

        return speedKmh
    }

    /// Запустить мониторинг крашей
    func startMonitoring() async throws {
        guard !isMonitoring else {
            print("⚠️ CrashDetectionManager: Мониторинг уже запущен")
            return
        }

        guard motionManager.isAccelerometerAvailable else {
            throw CrashDetectionError.accelerometerUnavailable
        }

        // Запросить разрешение на геолокацию
        await locationManager.requestAuthorization(always: true)

        // Получить текущее местоположение для настройки геозоны
        let location = try await locationManager.getCurrentLocation()

        // Настроить Crash Detection геозону
        do {
            // Используем CLCircularRegion напрямую для геозоны crash detection
            let region = CLCircularRegion(
                center: location.coordinate,
                radius: geofenceRadius,
                identifier: "crash_detection_zone"
            )
            region.notifyOnEntry = true
            region.notifyOnExit = false
            
            // Начать мониторинг геозоны через LocationManager
            let geofenceItem = GeofenceItem(
                name: "Crash Detection Zone",
                address: "Current Location",
                radius: geofenceRadius
            )
            try locationManager.startMonitoring(geofence: geofenceItem, center: location.coordinate)
            print("✅ CrashDetectionManager: Геозона настроена (радиус: \(geofenceRadius)м)")
        } catch {
            print("⚠️ CrashDetectionManager: Ошибка настройки геозоны: \(error.localizedDescription)")
            // Продолжаем без геозоны - мониторинг все равно работает
        }

        // 🚀 Запустить оптимизированный мониторинг скорости (экономит батарею)
        startSpeedMonitoring()

        isMonitoring = true
        print("✅ CrashDetectionManager: Оптимизированный мониторинг запущен (работает только при скорости >50km/h)")
    }

    
    /// Остановить мониторинг крашей
    func stopMonitoring() async throws {
        guard isMonitoring else {
            print("⚠️ CrashDetectionManager: Мониторинг не запущен")
            return
        }
        
        // Остановить мониторинг на сервере
        try await apiService.stopCrashDetectionMonitoring()
        
        // 🔋 Остановить оптимизированный мониторинг скорости
        stopSpeedMonitoring()

        // Остановить акселерометр (если был активен)
        motionManager.stopAccelerometerUpdates()
        motionManager.stopGyroUpdates()

        // Остановить геозону
        locationManager.stopMonitoring(identifier: "crash_detection_zone")

        // Отменить задачи
        monitoringTask?.cancel()
        monitoringTask = nil
        countdownTimer?.invalidate()
        countdownTimer = nil
        
        isMonitoring = false
        crashDetected = false
        countdownSeconds = countdownDuration
        
        print("✅ CrashDetectionManager: Мониторинг остановлен")
    }
    
    /// Отменить вызов экстренных служб
    func cancelEmergencyCall() {
        guard crashDetected else { return }
        
        countdownTimer?.invalidate()
        countdownTimer = nil
        crashDetected = false
        countdownSeconds = countdownDuration
        
        print("✅ CrashDetectionManager: Вызов экстренных служб отменен")
    }
    
    // MARK: - Private Methods
    
    /// Запустить обновления акселерометра
    private func startAccelerometerUpdates() {
        guard motionManager.isAccelerometerAvailable else {
            print("❌ CrashDetectionManager: Акселерометр недоступен")
            return
        }
        
        let queue = OperationQueue()
        queue.name = "CrashDetectionQueue"
        queue.maxConcurrentOperationCount = 1
        
        motionManager.startAccelerometerUpdates(to: queue) { [weak self] (data, error) in
            guard let self = self, let data = data else { return }
            
            Task { @MainActor in
                await self.processAccelerometerData(data)
            }
        }
        
        // Также запускаем гироскоп для более точного определения
        if motionManager.isGyroAvailable {
            motionManager.startGyroUpdates(to: queue) { [weak self] (data, error) in
                // Гироскоп используется для дополнительной информации
                // Основной анализ - через акселерометр
            }
        }
    }
    
    /// Обработать данные акселерометра
    private func processAccelerometerData(_ data: CMAccelerometerData) async {
        let x = data.acceleration.x
        let y = data.acceleration.y
        let z = data.acceleration.z
        
        // Вычислить G-силу
        let gForce = sqrt(x * x + y * y + z * z) / 9.8
        lastGForce = gForce
        
        // Проверить порог
        if gForce >= currentGForceThreshold {
            await detectCrash(gForce: gForce, accelerometer: data)
        }
        
        // Отправить данные на сервер (оптимизировано: каждые 5 секунд вместо каждой секунды)
        // Это снижает нагрузку на сервер и улучшает производительность
        sendCounter += 1
        if sendCounter >= dataSendInterval { // Каждые ~5 секунд (50 обновлений * 0.1 сек)
            sendCounter = 0
            await sendSensorData(accelerometer: data, gForce: gForce)
        }
    }
    
    /// Обнаружить краш
    private func detectCrash(gForce: Double, accelerometer: CMAccelerometerData) async {
        guard !crashDetected else { return }
        
        print("🚨 CrashDetectionManager: Обнаружен краш! G-сила: \(String(format: "%.2f", gForce))")
        
        crashDetected = true
        
        // Получить текущее местоположение
        guard let location = try? await locationManager.getCurrentLocation() else {
            print("❌ CrashDetectionManager: Не удалось получить местоположение")
            return
        }
        
        // Определить серьезность
        let severity: CrashSeverity
        if gForce >= 5.0 {
            severity = .critical
        } else if gForce >= 4.0 {
            severity = .high
        } else if gForce >= 3.5 {
            severity = .medium
        } else {
            severity = .low
        }
        
        // Отправить алерт на сервер
        do {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                // ✅ BUILD 115: Защита от двойного вызова continuation.resume()
                var hasResumed = false
                
                apiService.sendCrashAlert(
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude,
                    severity: severity.rawValue
                ) { result in
                    guard !hasResumed else {
                        print("⚠️ CRITICAL: Attempted to resume crash alert continuation twice!")
                        return
                    }
                    hasResumed = true
                    
                    switch result {
                    case .success:
                        continuation.resume()
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
            }
            print("✅ CrashDetectionManager: Алерт отправлен на сервер")
        } catch {
            print("❌ CrashDetectionManager: Ошибка отправки алерта: \(error.localizedDescription)")
        }
        
        // Запустить обратный отсчет
        startCountdown()
    }
    
    /// Запустить обратный отсчет перед вызовом экстренных служб
    private func startCountdown() {
        countdownSeconds = countdownDuration
        countdownTimer?.invalidate()
        
        countdownTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            Task { @MainActor in
                if self.countdownSeconds > 0 {
                    self.countdownSeconds -= 1
                } else {
                    timer.invalidate()
                    await self.callEmergencyServices()
                }
            }
        }
    }
    
    /// Вызвать экстренные службы
    func callEmergencyServices() async {
        print("🚨 CrashDetectionManager: Вызов экстренных служб...")
        
        // Получить текущее местоположение
        guard let location = try? await locationManager.getCurrentLocation() else {
            print("❌ CrashDetectionManager: Не удалось получить местоположение для вызова")
            return
        }
        
        // В реальном приложении здесь будет вызов API 112
        // Сейчас логируем
        print("📞 CrashDetectionManager: Вызов 112")
        print("📍 Местоположение: \(location.coordinate.latitude), \(location.coordinate.longitude)")
        print("⚠️ Серьезность: \(lastGForce >= 5.0 ? "Критическая" : "Высокая")")
        
        // Сбросить состояние
        crashDetected = false
        countdownSeconds = countdownDuration
    }
    
    /// Отправить данные сенсоров на сервер
    private func sendSensorData(accelerometer: CMAccelerometerData, gForce: Double) async {
        guard let location = try? await locationManager.getCurrentLocation() else { return }
        
        let accelerometerData: [String: Double] = [
            "x": accelerometer.acceleration.x,
            "y": accelerometer.acceleration.y,
            "z": accelerometer.acceleration.z
        ]
        
        let gyroscopeData: [String: Double] = [
            "x": 0.0, // Будет обновлено, если гироскоп доступен
            "y": 0.0,
            "z": 0.0
        ]
        
        // Вычислить скорость (приблизительно)
        let speed = calculateSpeedFromAccelerometer(accelerometer.acceleration)
        
        Task {
            do {
                try await apiService.sendCrashDetectionData(
                    accelerometer: accelerometerData,
                    gyroscope: gyroscopeData,
                    speed: speed,
                    location: location
                )
            } catch {
                print("⚠️ CrashDetectionManager: Ошибка отправки данных: \(error.localizedDescription)")
            }
        }
    }
    
    /// Вычислить скорость из данных акселерометра (приблизительно)
    private func calculateSpeedFromAccelerometer(_ acceleration: CMAcceleration) -> Double {
        // Простое приближение: интегрируем ускорение
        // В реальном приложении нужно использовать более сложные алгоритмы
        let magnitude = sqrt(acceleration.x * acceleration.x + acceleration.y * acceleration.y + acceleration.z * acceleration.z)
        return magnitude * 3.6 // Конвертация в км/ч (приблизительно)
    }
    
    // MARK: - Emergency Actions Support
    
    /// Получить текущее местоположение
    func getCurrentLocation() async throws -> CLLocation {
        return try await locationManager.getCurrentLocation()
    }
    
    /// Отправить данные аварии на сервер
    func sendCrashDataToServer(_ crashData: CrashData) async throws {
        do {
            // Сохранить данные последнего краша
            lastDetectedGForce = crashData.gForce
            lastDetectedSpeed = crashData.speed
            
            // Отправить через API
            let accelerometerData: [String: Double] = [
                "x": 0.0,
                "y": 0.0,
                "z": crashData.gForce
            ]

            let gyroscopeData: [String: Double] = [
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            ]

            let location: CLLocation?
            if let crashLocation = crashData.location {
                location = crashLocation
            } else {
                location = try? await getCurrentLocation()
            }
            
            try await apiService.sendCrashDetectionData(
                accelerometer: accelerometerData,
                gyroscope: gyroscopeData,
                speed: crashData.speed,
                location: location
            )
            
            // Отправить алерт на сервер
            if let location = location {
                try await apiService.sendCrashAlert(
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude,
                    severity: determineSeverity(gForce: crashData.gForce)
                )
            }
            
            print("✅ CrashDetectionManager: Данные аварии отправлены на сервер")
            
        } catch {
            print("❌ CrashDetectionManager: Ошибка отправки данных на сервер: \(error.localizedDescription)")
            throw error
        }
    }
    
    /// Определить серьезность аварии по G-force
    private func determineSeverity(gForce: Double) -> String {
        if gForce >= 8.0 {
            return "critical"
        } else if gForce >= 5.0 {
            return "high"
        } else if gForce >= 3.0 {
            return "medium"
        } else {
            return "low"
        }
    }
}

#if DEBUG
@MainActor
extension CrashDetectionManager {
    /// Кнопка/инструменты отладки: воспроизвести цепочку алерта без реального датчика.
    func simulateCrashForDiagnostics(gForce: Double = 5.0) async {
        await runSyntheticCrashScenario(gForce: gForce)
    }
}
#endif

extension CrashDetectionManager: CrashDetectionControlling {}

// MARK: - Crash Data Model

struct CrashData {
    let gForce: Double
    let speed: Double
    let timestamp: Date
    let location: CLLocation?
}

// MARK: - Crash Detection Error

enum CrashDetectionError: LocalizedError {
    case accelerometerUnavailable
    case locationUnavailable
    case serverSetupFailed
    case monitoringFailed
    
    var errorDescription: String? {
        switch self {
        case .accelerometerUnavailable:
            return "Акселерометр недоступен на этом устройстве"
        case .locationUnavailable:
            return "Геолокация недоступна"
        case .serverSetupFailed:
            return "Не удалось настроить Crash Detection на сервере"
        case .monitoringFailed:
            return "Не удалось запустить мониторинг"
        }
    }
}
