import SwiftUI
import Combine

/// 🛡️ VPN View Model
/// Логика для экрана VPN
class VPNViewModel: ObservableObject {
    
    static let shared = VPNViewModel()
    
    // Сохраняем последнее состояние VPN
    @AppStorage("vpn_last_enabled_state") private var vpnLastEnabledState: Bool = true
    
    @Published var isVPNEnabled: Bool = true {
        didSet {
            // Сохраняем состояние при изменении
            vpnLastEnabledState = isVPNEnabled
        }
    }
    
    @Published var isConnected: Bool = false
    
    // Сохраняем выбранный сервер по ID
    @AppStorage("vpn_selected_server_id") private var selectedServerID: String = "1"
    @Published var selectedServer: VPNServer = VPNServer(
        id: "1",
        country: "Singapore",
        city: "Singapore",
        flag: "🇸🇬",
        ping: 12,
        load: 45,
        status: .optimal
    ) {
        didSet {
            // Сохраняем ID сервера при изменении
            selectedServerID = selectedServer.id
        }
    }
    
    @Published var currentIP: String = "192.168.1.147"
    @Published var downloadedToday: String = "2.4 GB"
    @Published var uploadedToday: String = "1.2 GB"
    @Published var sessionTime: String = "4:37:21"
    @Published var connectionTime: String = "4:37:21"
    @Published var threatsBlocked: Int = 47
    @Published var ping: String = "12 ms"
    @Published var isConnecting: Bool = false
    
    // Сохраняем настройку автоотключения
    @AppStorage("vpn_auto_disconnect_enabled") var autoDisconnectEnabled: Bool = true
    
    // Таймер для автоотключения VPN при неактивности
    private var inactivityTimer: Timer?
    private let inactivityTimeout: TimeInterval = 300 // 5 минут
    
    private init() {
        // Восстанавливаем сохранённое состояние VPN
        isVPNEnabled = vpnLastEnabledState
        // TODO: Загрузить выбранный сервер по ID
        startInactivityTimer()
    }
    
    func toggleVPN() {
        isConnecting = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
            guard let self = self else { return }
            self.isVPNEnabled.toggle()
            self.isConnecting = false
            
            if self.isVPNEnabled {
                // При включении VPN - запускаем таймер автоотключения
                self.startInactivityTimer()
            } else {
                // При выключении VPN - останавливаем таймер
                self.stopInactivityTimer()
            }
        }
    }
    
    // Запуск таймера автоотключения при неактивности
    private func startInactivityTimer() {
        guard autoDisconnectEnabled else { return }
        
        stopInactivityTimer()
        
        inactivityTimer = Timer.scheduledTimer(withTimeInterval: inactivityTimeout, repeats: false) { [weak self] _ in
            self?.autoDisconnectVPN()
        }
    }
    
    // Остановка таймера
    private func stopInactivityTimer() {
        inactivityTimer?.invalidate()
        inactivityTimer = nil
    }
    
    // Автоматическое отключение VPN при неактивности
    private func autoDisconnectVPN() {
        if isVPNEnabled && autoDisconnectEnabled {
            print("🔋 VPN автоматически отключен для экономии батареи")
            isVPNEnabled = false
        }
    }
    
    // Перезапуск таймера при активности (можно вызвать при взаимодействии с VPN экраном)
    func resetInactivityTimer() {
        if isVPNEnabled {
            startInactivityTimer()
        }
    }
    
    func selectServer(_ server: VPNServer) {
        selectedServer = server
        print("Server selected: \(server.name)")
    }
    
    func copyIP() {
        UIPasteboard.general.string = currentIP
        print("IP copied to clipboard")
    }
    
    deinit {
        stopInactivityTimer()
    }
}



