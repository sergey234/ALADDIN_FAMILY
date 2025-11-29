import Foundation
import Combine

/// 🏡 IoT Security Module
/// ТОЛЬКО запросы к API, НИКАКОЙ бизнес-логики
class IoTSecurityModule: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var iotDevices: [IoTDevice] = []
    @Published var threatsDetected: [IoTThreat] = []
    @Published var isScanning: Bool = false
    @Published var protectionLevel: Int = 0
    @Published var recommendations: [String] = []
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private var currentHomeId: String?
    
    // MARK: - Initialization
    
    init(apiService: APIService = APIService.shared) {
        self.apiService = apiService
    }
    
    // MARK: - API Methods
    
    /// ТОЛЬКО запрос к API
    func scanDevices(homeId: String) async throws {
        isScanning = true
        defer { isScanning = false }
        
        currentHomeId = homeId
        
        // ПРОСТО запрос к серверу
        let response = try await apiService.getIoTDevices(homeId: homeId)
        
        // Обновление UI
        await MainActor.run {
            iotDevices = response.devices
            threatsDetected = response.threats ?? []
        }
    }
    
    /// ТОЛЬКО запрос к API
    func monitorCameras(homeId: String) async throws {
        let response = try await apiService.getIoTThreats(homeId: homeId)
        
        // Фильтрация угроз по камерам
        await MainActor.run {
            threatsDetected = response.threats.filter { $0.threatType == .camera || $0.threatType == .cameraIntrusion }
        }
    }
    
    /// ТОЛЬКО запрос к API
    func checkPasswords(homeId: String) async throws {
        let response = try await apiService.getIoTStatus(homeId: homeId)
        
        // Отображаем рекомендации с сервера
        await MainActor.run {
            recommendations = response.recommendations ?? []
            protectionLevel = response.protectionLevel ?? 0
        }
    }
    
    /// ТОЛЬКО команда на сервер
    func blockDevice(_ deviceId: String) async throws {
        try await apiService.blockIoTDevice(deviceId: deviceId)
        
        // Обновляем список устройств
        // Получаем homeId из текущего контекста
        if let homeId = currentHomeId {
            try await scanDevices(homeId: homeId)
        }
    }
    
    /// ТОЛЬКО уведомление пользователя
    func alertCompromised(_ device: IoTDevice) {
        // Показываем уведомление
        NotificationManager.shared.sendLocalNotification(
            title: "⚠️ Устройство скомпрометировано",
            body: "\(device.name) требует внимания",
            category: .security,
            userInfo: [
                "type": "iot_device_compromised",
                "device_id": device.id,
                "device_name": device.name
            ],
            delay: 0.1 // Используем минимальную задержку, чтобы избежать ошибок триггера (delay > 0)
        )
    }
    
    /// Загрузка статуса безопасности
    func loadStatus(homeId: String) async throws {
        currentHomeId = homeId
        
        let response = try await apiService.getIoTStatus(homeId: homeId)
        
        await MainActor.run {
            iotDevices = response.devices ?? []
            threatsDetected = response.threats ?? []
            recommendations = response.recommendations ?? []
            protectionLevel = response.protectionLevel ?? 0
        }
    }
    
    /// Обновление статуса
    func refreshStatus() async throws {
        guard let homeId = currentHomeId else {
            throw IoTSecurityError.missingHomeId
        }
        
        try await loadStatus(homeId: homeId)
    }
    
    // MARK: - Device Discovery
    
    /// Сканирует сеть для обнаружения устройств
    func scanNetwork() async -> [IoTDevice] {
        print("🔍 IoT: Сканирование сети...")
        
        // TODO: Реализовать сканирование сети
        // Использовать Network.framework для сканирования
        // Пока возвращаем пустой массив - требует реализации API
        
        guard let homeId = currentHomeId else {
            print("⚠️ IoT: Home ID не установлен для сканирования сети")
            return []
        }
        
        do {
            let response = try await apiService.getIoTDevices(homeId: homeId)
            await MainActor.run {
                iotDevices = response.devices
            }
            print("✅ IoT: Обнаружено \(response.devices.count) устройств")
            return response.devices
        } catch {
            print("❌ IoT: Ошибка сканирования сети: \(error.localizedDescription)")
            return []
        }
    }
    
    /// Обнаруживает устройства по MAC адресам
    func discoverByMACAddresses(_ macAddresses: [String]) async -> [IoTDevice] {
        print("🔍 IoT: Обнаружение устройств по MAC адресам (\(macAddresses.count) адресов)...")
        
        // TODO: Реализовать обнаружение по MAC адресам
        // Фильтровать устройства по MAC адресам
        let devices = iotDevices.filter { device in
            guard let mac = device.mac else { return false }
            return macAddresses.contains(mac)
        }
        
        print("✅ IoT: Обнаружено \(devices.count) устройств по MAC адресам")
        return devices
    }
    
    /// Обнаруживает устройства по портам
    func discoverByPorts(_ ports: [Int]) async -> [IoTDevice] {
        print("🔍 IoT: Обнаружение устройств по портам (\(ports.count) портов)...")
        
        // TODO: Реализовать обнаружение по портам
        // Пока возвращаем пустой массив - требует реализации API
        print("⚠️ IoT: Обнаружение по портам требует реализации API")
        return []
    }
    
    /// Обнаруживает устройства по протоколам
    func discoverByProtocols(_ protocols: [String]) async -> [IoTDevice] {
        print("🔍 IoT: Обнаружение устройств по протоколам (\(protocols.count) протоколов)...")
        
        // TODO: Реализовать обнаружение по протоколам
        // Пока возвращаем пустой массив - требует реализации API
        print("⚠️ IoT: Обнаружение по протоколам требует реализации API")
        return []
    }
    
    // MARK: - Traffic Analysis
    
    /// Анализирует сетевой трафик устройства
    func analyzeTraffic(for device: IoTDevice) async -> TrafficAnalysisResult {
        print("📊 IoT: Анализ трафика для устройства \(device.name)...")
        
        // TODO: Реализовать анализ трафика
        // Пока возвращаем мок данные
        let result = TrafficAnalysisResult(
            deviceId: device.id,
            suspiciousActivity: device.status == .compromised,
            blockedConnections: device.status == .compromised ? 5 : 0,
            totalConnections: 100,
            dataTransmitted: 1024 * 1024, // 1 MB
            dataReceived: 512 * 1024 // 512 KB
        )
        
        print("✅ IoT: Анализ трафика завершён для \(device.name)")
        return result
    }
    
    /// Обнаруживает подозрительную активность
    func detectSuspiciousActivity(for device: IoTDevice) async -> Bool {
        print("🔍 IoT: Проверка подозрительной активности для \(device.name)...")
        
        // Проверяем статус устройства
        if device.status == .compromised {
            print("⚠️ IoT: Устройство \(device.name) скомпрометировано")
            return true
        }
        
        // TODO: Реализовать более детальную проверку подозрительной активности
        // Проверка необычных соединений, больших объёмов данных и т.д.
        
        return false
    }
    
    /// Блокирует небезопасные соединения
    func blockUnsafeConnections(for device: IoTDevice) async {
        print("🚫 IoT: Блокировка небезопасных соединений для \(device.name)...")
        
        // TODO: Реализовать блокировку небезопасных соединений
        // Отправить команду на сервер для блокировки
        do {
            try await blockDevice(device.id)
            print("✅ IoT: Небезопасные соединения заблокированы для \(device.name)")
        } catch {
            print("❌ IoT: Ошибка блокировки соединений: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Automatic Blocking
    
    /// Автоматически блокирует небезопасные устройства
    func autoBlockUnsafeDevices() async {
        print("🔄 IoT: Автоматическая блокировка небезопасных устройств...")
        
        // Сканируем сеть
        let devices = await scanNetwork()
        
        var blockedCount = 0
        
        for device in devices {
            // Проверяем, небезопасно ли устройство
            if !device.isSecure {
                // Блокируем устройство
                do {
                    try await blockDevice(device.id)
                    blockedCount += 1
                    
                    // Уведомляем о подозрительном устройстве
                    await notifySuspiciousDevice(device)
                    
                    print("✅ IoT: Устройство \(device.name) заблокировано")
                } catch {
                    print("❌ IoT: Ошибка блокировки устройства \(device.name): \(error.localizedDescription)")
                }
            }
        }
        
        print("✅ IoT: Автоматическая блокировка завершена (\(blockedCount) устройств заблокировано)")
    }
    
    /// Уведомляет о подозрительном устройстве
    private func notifySuspiciousDevice(_ device: IoTDevice) async {
        // Отправляем уведомление
        alertCompromised(device)
        
        // TODO: Отправить уведомление на сервер
        print("📢 IoT: Уведомление отправлено о подозрительном устройстве \(device.name)")
    }
}

// MARK: - IoT Device Extensions

extension IoTDevice {
    /// Проверяет, безопасно ли устройство
    var isSecure: Bool {
        return status == .safe || status == .online
    }
}

// MARK: - Traffic Analysis Models

/// Результат анализа трафика
struct TrafficAnalysisResult: Codable {
    let deviceId: String
    let suspiciousActivity: Bool
    let blockedConnections: Int
    let totalConnections: Int
    let dataTransmitted: Int64  // Байты
    let dataReceived: Int64  // Байты
}

// MARK: - Errors

enum IoTSecurityError: LocalizedError {
    case missingHomeId
    case apiError(String)
    
    var errorDescription: String? {
        switch self {
        case .missingHomeId:
            return "Home ID не установлен"
        case .apiError(let message):
            return "API ошибка: \(message)"
        }
    }
}

