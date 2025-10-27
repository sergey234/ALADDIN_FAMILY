import SwiftUI
import Combine

/// 🛡️ VPN View Model
/// Логика для экрана VPN
class VPNViewModel: ObservableObject {
    
    static let shared = VPNViewModel()
    
    @Published var isVPNEnabled: Bool = true
    @Published var isConnected: Bool = false
    @Published var selectedServer: VPNServer = VPNServer(
        id: "1",
        country: "Россия",
        city: "Москва",
        flag: "🇷🇺",
        ping: 12,
        load: 45,
        status: .optimal
    )
    @Published var currentIP: String = "192.168.1.147"
    @Published var downloadedToday: String = "2.4 GB"
    @Published var uploadedToday: String = "1.2 GB"
    @Published var sessionTime: String = "4:37:21"
    @Published var connectionTime: String = "4:37:21"
    @Published var threatsBlocked: Int = 47
    @Published var ping: String = "12 ms"
    @Published var isConnecting: Bool = false
    
    func toggleVPN() {
        isConnecting = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
            self?.isVPNEnabled.toggle()
            self?.isConnecting = false
        }
    }
    
    func selectServer() {
        print("Show server selection")
    }
    
    func copyIP() {
        UIPasteboard.general.string = currentIP
        print("IP copied to clipboard")
    }
}



