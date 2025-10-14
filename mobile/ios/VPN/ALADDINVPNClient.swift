//
//  ALADDINVPNClient.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import Foundation
import NetworkExtension
import UIKit

// MARK: - VPN Status Enum
enum VPNStatus: String, CaseIterable {
    case disconnected = "disconnected"
    case connecting = "connecting"
    case connected = "connected"
    case disconnecting = "disconnecting"
    case error = "error"
    
    var displayName: String {
        switch self {
        case .disconnected: return "Отключен"
        case .connecting: return "Подключение..."
        case .connected: return "Подключен"
        case .disconnecting: return "Отключение..."
        case .error: return "Ошибка"
        }
    }
    
    var color: UIColor {
        switch self {
        case .disconnected: return UIColor.systemGray
        case .connecting: return UIColor.systemYellow
        case .connected: return UIColor.systemGreen
        case .disconnecting: return UIColor.systemOrange
        case .error: return UIColor.systemRed
        }
    }
}

// MARK: - VPN Protocol Enum
enum VPNProtocol: String, CaseIterable {
    case wireguard = "wireguard"
    case openvpn = "openvpn"
    case shadowsocks = "shadowsocks"
    case v2ray = "v2ray"
    
    var displayName: String {
        switch self {
        case .wireguard: return "WireGuard"
        case .openvpn: return "OpenVPN"
        case .shadowsocks: return "Shadowsocks"
        case .v2ray: return "V2Ray"
        }
    }
}

// MARK: - VPN Server Model
struct VPNServer: Codable, Identifiable {
    let id: String
    let name: String
    let country: String
    let flag: String
    let ip: String
    let port: Int
    let protocol: VPNProtocol
    let isAvailable: Bool
    let performanceScore: Double
    let ping: Int
    let load: Int
    
    var displayName: String {
        return "\(flag) \(name)"
    }
    
    var statusText: String {
        return "\(ping)ms • \(load)% нагрузка"
    }
}

// MARK: - Connection Info
struct ConnectionInfo {
    let server: VPNServer
    let startTime: Date
    var bytesSent: Int64
    var bytesReceived: Int64
    let status: VPNStatus
    
    var connectionTime: TimeInterval {
        return Date().timeIntervalSince(startTime)
    }
    
    var speed: (download: Double, upload: Double) {
        let time = connectionTime
        guard time > 0 else { return (0, 0) }
        
        let downloadSpeed = Double(bytesReceived) / time / 1024 // KB/s
        let uploadSpeed = Double(bytesSent) / time / 1024 // KB/s
        
        return (downloadSpeed, uploadSpeed)
    }
}

// MARK: - ALADDIN VPN Client
class ALADDINVPNClient: ObservableObject {
    
    // MARK: - Published Properties
    @Published var status: VPNStatus = .disconnected
    @Published var currentConnection: ConnectionInfo?
    @Published var availableServers: [VPNServer] = []
    @Published var isConnecting = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    private var vpnManager: NEVPNManager?
    private var connectionHistory: [ConnectionInfo] = []
    private let apiClient: ALADDINAPIClient
    
    // MARK: - Initialization
    init(apiClient: ALADDINAPIClient) {
        self.apiClient = apiClient
        setupVPNManager()
        loadServers()
    }
    
    // MARK: - Setup
    private func setupVPNManager() {
        NEVPNManager.shared().loadFromPreferences { [weak self] error in
            if let error = error {
                print("Ошибка загрузки VPN настроек: \(error)")
                return
            }
            
            DispatchQueue.main.async {
                self?.vpnManager = NEVPNManager.shared()
                self?.updateStatus()
            }
        }
    }
    
    private func loadServers() {
        // Загружаем серверы из API
        Task {
            do {
                let servers = try await apiClient.getVPNServers()
                await MainActor.run {
                    self.availableServers = servers
                }
            } catch {
                print("Ошибка загрузки серверов: \(error)")
                // Используем серверы по умолчанию
                await MainActor.run {
                    self.loadDefaultServers()
                }
            }
        }
    }
    
    private func loadDefaultServers() {
        availableServers = [
            VPNServer(
                id: "sg-1",
                name: "Сингапур",
                country: "SG",
                flag: "🇸🇬",
                ip: "192.168.2.10",
                port: 443,
                protocol: .shadowsocks,
                isAvailable: true,
                performanceScore: 95.0,
                ping: 25,
                load: 15
            ),
            VPNServer(
                id: "de-1",
                name: "Германия",
                country: "DE",
                flag: "🇩🇪",
                ip: "192.168.2.11",
                port: 443,
                protocol: .v2ray,
                isAvailable: true,
                performanceScore: 92.0,
                ping: 45,
                load: 25
            ),
            VPNServer(
                id: "hk-1",
                name: "Гонконг",
                country: "HK",
                flag: "🇭🇰",
                ip: "192.168.2.12",
                port: 443,
                protocol: .shadowsocks,
                isAvailable: true,
                performanceScore: 88.0,
                ping: 35,
                load: 20
            ),
            VPNServer(
                id: "jp-1",
                name: "Япония",
                country: "JP",
                flag: "🇯🇵",
                ip: "192.168.2.13",
                port: 51820,
                protocol: .wireguard,
                isAvailable: true,
                performanceScore: 90.0,
                ping: 40,
                load: 30
            ),
            VPNServer(
                id: "us-1",
                name: "США",
                country: "US",
                flag: "🇺🇸",
                ip: "192.168.2.14",
                port: 1194,
                protocol: .openvpn,
                isAvailable: true,
                performanceScore: 85.0,
                ping: 80,
                load: 40
            ),
            VPNServer(
                id: "ca-1",
                name: "Канада",
                country: "CA",
                flag: "🇨🇦",
                ip: "192.168.2.15",
                port: 51820,
                protocol: .wireguard,
                isAvailable: true,
                performanceScore: 87.0,
                ping: 75,
                load: 35
            )
        ]
    }
    
    // MARK: - Public Methods
    
    /// Подключение к VPN серверу
    func connect(to server: VPNServer? = nil) async {
        guard !isConnecting else { return }
        
        let targetServer = server ?? selectBestServer()
        guard let targetServer = targetServer else {
            await MainActor.run {
                errorMessage = "Нет доступных серверов"
            }
            return
        }
        
        await MainActor.run {
            isConnecting = true
            status = .connecting
            errorMessage = nil
        }
        
        do {
            try await performConnection(to: targetServer)
            
            await MainActor.run {
                currentConnection = ConnectionInfo(
                    server: targetServer,
                    startTime: Date(),
                    bytesSent: 0,
                    bytesReceived: 0,
                    status: .connected
                )
                status = .connected
                isConnecting = false
                connectionHistory.append(currentConnection!)
            }
            
        } catch {
            await MainActor.run {
                status = .error
                isConnecting = false
                errorMessage = error.localizedDescription
            }
        }
    }
    
    /// Отключение от VPN
    func disconnect() async {
        guard status != .disconnected else { return }
        
        await MainActor.run {
            status = .disconnecting
        }
        
        do {
            try await performDisconnection()
            
            await MainActor.run {
                currentConnection = nil
                status = .disconnected
            }
            
        } catch {
            await MainActor.run {
                status = .error
                errorMessage = error.localizedDescription
            }
        }
    }
    
    /// Выбор лучшего сервера
    func selectBestServer() -> VPNServer? {
        let availableServers = availableServers.filter { $0.isAvailable }
        guard !availableServers.isEmpty else { return nil }
        
        // Выбираем сервер с лучшей производительностью
        return availableServers.max { $0.performanceScore < $1.performanceScore }
    }
    
    /// Получение серверов для быстрого подключения
    func getQuickConnectServers() -> [VPNServer] {
        return Array(availableServers
            .filter { $0.isAvailable }
            .sorted { $0.ping < $1.ping }
            .prefix(4))
    }
    
    /// Обновление статистики трафика
    func updateTraffic(bytesSent: Int64, bytesReceived: Int64) {
        guard var connection = currentConnection else { return }
        
        connection.bytesSent += bytesSent
        connection.bytesReceived += bytesReceived
        
        currentConnection = connection
    }
    
    /// Получение сводки подключения
    func getConnectionSummary() -> [String: Any] {
        guard let connection = currentConnection else {
            return [
                "isConnected": false,
                "statusText": status.displayName,
                "serverInfo": [String: Any](),
                "connectionTime": 0.0,
                "speed": ["download": 0.0, "upload": 0.0],
                "dataUsage": ["sent": 0, "received": 0, "total": 0]
            ]
        }
        
        let speed = connection.speed
        
        return [
            "isConnected": status == .connected,
            "statusText": status.displayName,
            "serverInfo": [
                "id": connection.server.id,
                "name": connection.server.name,
                "country": connection.server.country,
                "flag": connection.server.flag
            ],
            "connectionTime": connection.connectionTime,
            "speed": [
                "download": speed.download,
                "upload": speed.upload
            ],
            "dataUsage": [
                "sent": connection.bytesSent,
                "received": connection.bytesReceived,
                "total": connection.bytesSent + connection.bytesReceived
            ]
        ]
    }
    
    // MARK: - Private Methods
    
    private func performConnection(to server: VPNServer) async throws {
        // Здесь будет реальная логика подключения к VPN
        // Пока что симулируем подключение
        
        try await Task.sleep(nanoseconds: 2_000_000_000) // 2 секунды
        
        // Симулируем успешное подключение
        // В реальной реализации здесь будет настройка NEVPNManager
    }
    
    private func performDisconnection() async throws {
        // Здесь будет реальная логика отключения от VPN
        // Пока что симулируем отключение
        
        try await Task.sleep(nanoseconds: 1_000_000_000) // 1 секунда
        
        // В реальной реализации здесь будет отключение NEVPNManager
    }
    
    private func updateStatus() {
        guard let manager = vpnManager else { return }
        
        switch manager.connection.status {
        case .connected:
            status = .connected
        case .connecting:
            status = .connecting
        case .disconnecting:
            status = .disconnecting
        case .disconnected:
            status = .disconnected
        case .invalid:
            status = .error
        @unknown default:
            status = .error
        }
    }
}

// MARK: - ALADDIN API Client Protocol
protocol ALADDINAPIClient {
    func getVPNServers() async throws -> [VPNServer]
}

