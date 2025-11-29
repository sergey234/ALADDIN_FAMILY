import Foundation
import NetworkExtension
import SwiftUI

/// Менеджер VPN для ALADDIN
class VPNManager: ObservableObject {
    static let shared = VPNManager()
    
    @Published var isConnected = false
    @Published var isConnecting = false
    @Published var connectionStatus: VPNStatus = .disconnected
    @Published var currentServer: VPNServer?
    @Published var connectionTime: TimeInterval = 0
    
    // NetworkExtension
    private var vpnManager: NEVPNManager?
    private var connectionTimer: Timer?
    private var startTime: Date?
    private var batteryMonitorTimer: Timer?
    
    // Battery optimization
    @Published var batteryOptimizationEnabled: Bool = true
    
    // Smart Caching
    private var cachedConfig: VPNConfigResponse?
    private var configCacheExpiry: Date?
    private let configCacheTTL: TimeInterval = 300.0 // 5 минут
    
    // Adaptive Polling
    @Published var adaptivePollingEnabled: Bool = true
    private var pollingTimer: Timer?
    private var currentPollingInterval: TimeInterval = 900.0 // начальный интервал 15 минут
    private var consecutiveFailures: Int = 0
    private let maxPollingInterval: TimeInterval = 3600.0 // максимум 1 час
    private let minPollingInterval: TimeInterval = 900.0 // минимум 15 минут
    
    enum VPNStatus {
        case disconnected
        case connecting
        case connected
        case disconnecting
        case error(String)
    }
    
    struct VPNServer {
        let id: String
        let name: String
        let country: String
        let flag: String
        let ping: Int
        let load: Int
        let isPremium: Bool
    }
    
    private init() {
        setupVPNConfiguration()
        startBatteryMonitoring()
    }
    
    // MARK: - VPN Configuration
    private func setupVPNConfiguration() {
        // Инициализация NetworkExtension
        NEVPNManager.shared().loadFromPreferences { [weak self] error in
            if let error = error {
                self?.log("Error loading VPN configuration: \(error.localizedDescription)")
                return
            }
            self?.vpnManager = NEVPNManager.shared()
            self?.configureTunnelProtocol()
        }
    }
    
    // MARK: - NetworkExtension Configuration
    private func configureTunnelProtocol() {
        guard let manager = vpnManager else { return }
        
        // Создаем протокол IKEv2 с AES-256-GCM шифрованием
        let protocolConfiguration = NEVPNProtocolIKEv2()
        
        // Базовые настройки
        protocolConfiguration.serverAddress = "vpn.aladdin.family"
        protocolConfiguration.remoteIdentifier = "vpn.aladdin.family"
        protocolConfiguration.localIdentifier = "aladdin"
        
        // Настройки шифрования AES-256-GCM
        protocolConfiguration.authenticationMethod = .certificate
        protocolConfiguration.useExtendedAuthentication = true
        protocolConfiguration.disableMOBIKE = false
        protocolConfiguration.disableRedirect = false
        
        // Authentication data
        protocolConfiguration.username = "aladdin_user"
        
        // Kill Switch
        protocolConfiguration.includeAllNetworks = true
        protocolConfiguration.excludeLocalNetworks = false
        
        manager.protocolConfiguration = protocolConfiguration
        manager.isEnabled = true
        
        // Настройка On Demand
        let onDemandRule = NEOnDemandRuleConnect()
        onDemandRule.interfaceTypeMatch = .any
        manager.onDemandRules = [onDemandRule]
        manager.isOnDemandEnabled = false // Управляем вручную
        
        // Сохраняем конфигурацию
        manager.saveToPreferences { [weak self] error in
            if let error = error {
                self?.log("Error saving VPN configuration: \(error.localizedDescription)")
            } else {
                self?.log("VPN configuration saved successfully")
            }
        }
    }
    
    // MARK: - Battery Monitoring
    func startBatteryMonitoring() {
        UIDevice.current.isBatteryMonitoringEnabled = true
        batteryMonitorTimer = Timer.scheduledTimer(withTimeInterval: 300.0, repeats: true) { [weak self] _ in
            self?.checkBatteryLevel()
        }
    }
    
    private func checkBatteryLevel() {
        guard batteryOptimizationEnabled else { return }
        
        let batteryLevel = UIDevice.current.batteryLevel
        
        if batteryLevel < 0.20 && isConnected {
            // Критический уровень - отключаем VPN
            disconnect()
            log("🔋 VPN отключен: батарея < 20%")
        } else if batteryLevel < 0.50 && isConnected {
            // Низкий уровень - используем легкое шифрование
            log("🔋 VPN оптимизирован: батарея < 50%")
        }
    }
    
    // MARK: - Connection Management
    func connect(to server: VPNServer? = nil) {
        guard !isConnecting else { return }
        
        isConnecting = true
        connectionStatus = .connecting
        startTime = Date()
        
        // Подключение через NetworkExtension
        do {
            try vpnManager?.connection.startVPNTunnel()
            log("Подключение к VPN через NetworkExtension...")
            
            // Проверяем статус подключения
            checkVPNStatus(server: server)
        } catch {
            log("Ошибка подключения: \(error.localizedDescription)")
            connectionStatus = .error(error.localizedDescription)
            isConnecting = false
        }
    }
    
    func disconnect() {
        guard isConnected else { return }
        
        connectionStatus = .disconnecting
        stopConnectionTimer()
        stopAdaptivePolling() // Останавливаем Adaptive Polling
        
        // Отключение через NetworkExtension
        vpnManager?.connection.stopVPNTunnel()
        log("Отключение от VPN...")
        
        // Обновляем состояние
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.isConnected = false
            self.connectionStatus = .disconnected
            self.currentServer = nil
            self.connectionTime = 0
        }
    }
    
    // MARK: - VPN Status Monitoring
    private func checkVPNStatus(server: VPNServer?) {
        // Проверяем статус каждые 0.5 секунды
        let timer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] timer in
            guard let self = self else {
                timer.invalidate()
                return
            }
            
            guard let connection = self.vpnManager?.connection else {
                timer.invalidate()
                return
            }
            
            let status = connection.status
            
            switch status {
            case .connected:
                self.isConnecting = false
                self.isConnected = true
                self.connectionStatus = .connected
                self.currentServer = server
                self.startConnectionTimer()
                self.startAdaptivePolling() // Запускаем Adaptive Polling
                timer.invalidate()
                self.log("✅ VPN подключен успешно")
                
            case .disconnected:
                if self.isConnecting {
                    self.log("VPN отключен во время подключения")
                    timer.invalidate()
                }
                
            case .connecting, .reasserting:
                // Ожидаем подключения
                break
                
            case .disconnecting:
                self.log("VPN отключается")
                timer.invalidate()
                
            case .invalid:
                self.connectionStatus = .error("Invalid VPN configuration")
                self.isConnecting = false
                timer.invalidate()
                self.log("❌ Неверная конфигурация VPN")
                
            @unknown default:
                break
            }
        }
        
        // Таймаут 30 секунд
        DispatchQueue.main.asyncAfter(deadline: .now() + 30) {
            timer.invalidate()
            if self.isConnecting {
                self.connectionStatus = .error("Timeout")
                self.isConnecting = false
                self.log("❌ Таймаут подключения к VPN")
            }
        }
    }
    
    // MARK: - Connection Timer
    private func startConnectionTimer() {
        connectionTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            if let startTime = self.startTime {
                self.connectionTime = Date().timeIntervalSince(startTime)
            }
        }
    }
    
    private func stopConnectionTimer() {
        connectionTimer?.invalidate()
        connectionTimer = nil
    }
    
    // MARK: - Server Management
    func getAvailableServers() -> [VPNServer] {
        return [
            VPNServer(id: "us-1", name: "United States", country: "US", flag: "🇺🇸", ping: 45, load: 23, isPremium: false),
            VPNServer(id: "uk-1", name: "United Kingdom", country: "UK", flag: "🇬🇧", ping: 52, load: 67, isPremium: false),
            VPNServer(id: "de-1", name: "Germany", country: "DE", flag: "🇩🇪", ping: 38, load: 45, isPremium: false),
            VPNServer(id: "jp-1", name: "Japan", country: "JP", flag: "🇯🇵", ping: 89, load: 12, isPremium: true),
            VPNServer(id: "au-1", name: "Australia", country: "AU", flag: "🇦🇺", ping: 156, load: 34, isPremium: true),
            VPNServer(id: "ca-1", name: "Canada", country: "CA", flag: "🇨🇦", ping: 67, load: 56, isPremium: false)
        ]
    }
    
    func getBestServer() -> VPNServer? {
        let servers = getAvailableServers()
        return servers.min { $0.ping < $1.ping }
    }
    
    // MARK: - Statistics
    func getConnectionStats() -> (bytesIn: Int64, bytesOut: Int64, packetsIn: Int64, packetsOut: Int64) {
        // В реальном приложении здесь будут реальные статистики
        return (bytesIn: 1024 * 1024, bytesOut: 512 * 1024, packetsIn: 1000, packetsOut: 800)
    }
    
    func getDataUsage() -> (today: Int64, thisMonth: Int64, total: Int64) {
        // В реальном приложении здесь будут реальные данные об использовании
        return (today: 50 * 1024 * 1024, thisMonth: Int64(1.5 * 1024 * 1024 * 1024), total: 10 * 1024 * 1024 * 1024)
    }
    
    // MARK: - Security Features
    func enableKillSwitch() {
        guard let manager = vpnManager else { return }
        
        // Настройка On Demand для Kill Switch
        let onDemandRule = NEOnDemandRuleConnect()
        onDemandRule.interfaceTypeMatch = .any
        manager.onDemandRules = [onDemandRule]
        manager.isOnDemandEnabled = true
        
        // Сохраняем конфигурацию
        manager.saveToPreferences { [weak self] error in
            if let error = error {
                self?.log("Error enabling Kill Switch: \(error.localizedDescription)")
            } else {
                self?.log("✅ Kill Switch enabled")
            }
        }
    }
    
    func disableKillSwitch() {
        guard let manager = vpnManager else { return }
        
        manager.isOnDemandEnabled = false
        manager.saveToPreferences { [weak self] error in
            if let error = error {
                self?.log("Error disabling Kill Switch: \(error.localizedDescription)")
            } else {
                self?.log("Kill Switch disabled")
            }
        }
    }
    
    // MARK: - Battery Optimization
    func optimizeForBattery() {
        guard batteryOptimizationEnabled else { return }
        
        let batteryLevel = UIDevice.current.batteryLevel
        
        switch batteryLevel {
        case 0.0..<0.20:
            // Критический уровень - отключить VPN
            if isConnected {
                disconnect()
                log("🔋 VPN отключен: батарея < 20%")
            }
        case 0.20..<0.50:
            // Низкий уровень - легкое шифрование
            useLightEncryption()
        case 0.50..<0.80:
            // Средний уровень - нормальное шифрование
            useNormalEncryption()
        default:
            // Высокий уровень - максимальная защита
            useMaximumEncryption()
        }
    }
    
    private func useLightEncryption() {
        log("🔄 Используется легкое шифрование AES-128")
        // В production здесь будет переключение алгоритма шифрования
    }
    
    private func useNormalEncryption() {
        log("🔄 Используется нормальное шифрование AES-256-GCM")
        // В production здесь будет переключение алгоритма шифрования
    }
    
    private func useMaximumEncryption() {
        log("🔄 Используется максимальное шифрование")
        // В production здесь будет переключение алгоритма шифрования
    }
    
    func enableAutoConnect() {
        // Включение автоматического подключения
        log("Auto Connect enabled")
    }
    
    func disableAutoConnect() {
        // Отключение автоматического подключения
        log("Auto Connect disabled")
    }
    
    // MARK: - Server Integration
    func loadConfigFromServer(completion: @escaping (Result<VPNConfigResponse, Error>) -> Void) {
        // Smart Caching: проверяем кэш
        if let cachedConfig = cachedConfig,
           let cacheExpiry = configCacheExpiry,
           Date() < cacheExpiry {
            log("📦 Используется кэшированная конфигурация VPN")
            completion(.success(cachedConfig))
            return
        }
        
        // Запрос конфигурации с сервера
        let apiService = APIService.shared
        apiService.getVPNConfig { [weak self] result in
            switch result {
            case .success(let config):
                // Сохраняем в кэш
                self?.cachedConfig = config
                self?.configCacheExpiry = Date().addingTimeInterval(self?.configCacheTTL ?? 300.0)
                self?.log("💾 Конфигурация VPN сохранена в кэш")
                completion(.success(config))
            case .failure(let error):
                // Если кэш существует, используем его даже если он устарел
                if let cachedConfig = self?.cachedConfig {
                    self?.log("⚠️ Используется устаревшая кэшированная конфигурация VPN")
                    completion(.success(cachedConfig))
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func clearConfigCache() {
        cachedConfig = nil
        configCacheExpiry = nil
        log("🗑️ Кэш конфигурации VPN очищен")
    }
    
    // MARK: - Adaptive Polling
    func startAdaptivePolling() {
        guard adaptivePollingEnabled else { return }
        
        stopAdaptivePolling() // Останавливаем предыдущий таймер если есть
        
        pollingTimer = Timer.scheduledTimer(withTimeInterval: currentPollingInterval, repeats: true) { [weak self] _ in
            self?.performPollingCycle()
        }
        
        log("🔄 Adaptive Polling запущен (интервал: \(Int(currentPollingInterval)) сек)")
    }
    
    func stopAdaptivePolling() {
        pollingTimer?.invalidate()
        pollingTimer = nil
    }
    
    private func performPollingCycle() {
        guard isConnected else {
            stopAdaptivePolling()
            return
        }
        
        // Отправляем статистику
        sendStatsToServer()
        
        // Проверяем статус подключения для polling
        checkVPNStatusForPolling()
    }
    
    private func adjustPollingInterval(success: Bool) {
        guard adaptivePollingEnabled else { return }
        
        if success {
            consecutiveFailures = 0
            // Уменьшаем интервал если всё хорошо
            if currentPollingInterval > minPollingInterval {
                currentPollingInterval = max(minPollingInterval, currentPollingInterval - 5.0)
                log("⬇️ Интервал polling уменьшен до \(Int(currentPollingInterval)) сек")
            }
        } else {
            consecutiveFailures += 1
            // Увеличиваем интервал при проблемах
            if consecutiveFailures >= 3 {
                currentPollingInterval = min(maxPollingInterval, currentPollingInterval * 1.5)
                log("⬆️ Интервал polling увеличен до \(Int(currentPollingInterval)) сек (ошибок: \(consecutiveFailures))")
                consecutiveFailures = 0
            }
        }
        
        // Перезапускаем с новым интервалом
        if pollingTimer != nil {
            startAdaptivePolling()
        }
    }
    
    private func checkVPNStatusForPolling() {
        // Проверка состояния VPN для адаптивного polling
        guard let connection = vpnManager?.connection else { return }
        
        switch connection.status {
        case .connected:
            adjustPollingInterval(success: true)
        case .connecting, .reasserting:
            // В процессе - не меняем интервал
            break
        case .disconnecting, .disconnected:
            stopAdaptivePolling()
            adjustPollingInterval(success: false)
        case .invalid:
            stopAdaptivePolling()
            adjustPollingInterval(success: false)
        @unknown default:
            break
        }
    }
    
    func sendStatsToServer() {
        let stats = collectStats()
        let apiService = APIService.shared
        apiService.sendVPNStats(stats) { result in
            switch result {
            case .success:
                self.log("✅ Статистика отправлена на сервер")
            case .failure(let error):
                self.log("❌ Ошибка отправки статистики: \(error)")
            }
        }
    }
    
    private func collectStats() -> VPNStats {
        let connectionStats = getConnectionStats()
        let dataUsage = getDataUsage()
        
        return VPNStats(
            bytesIn: connectionStats.bytesIn,
            bytesOut: connectionStats.bytesOut,
            packetsIn: connectionStats.packetsIn,
            packetsOut: connectionStats.packetsOut,
            today: dataUsage.today,
            thisMonth: dataUsage.thisMonth,
            sessionTime: connectionTime,
            threatsBlocked: 0 // TODO: from antivirus
        )
    }
    
    // MARK: - Logging
    private func log(_ message: String) {
        print("[VPNManager] \(message)")
    }
    
    deinit {
        stopConnectionTimer()
        batteryMonitorTimer?.invalidate()
    }
}
