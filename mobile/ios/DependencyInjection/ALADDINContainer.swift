import Foundation
import Swinject
import SwinjectAutoregistration

class ALADDINContainer {
    static let shared = Container()
    
    static func configure() {
        configureNetworking()
        configureSecurity()
        configureAI()
        configureVPN()
        configureViewModels()
        configureViewControllers()
    }
    
    // MARK: - Networking
    
    private static func configureNetworking() {
        // Network Manager
        shared.register(NetworkManagerProtocol.self) { _ in
            ALADDINNetworkManager.shared
        }.inObjectScope(.container)
        
        // Certificate Pinning Manager
        shared.register(CertificatePinningManagerProtocol.self) { _ in
            CertificatePinningManager.shared
        }.inObjectScope(.container)
    }
    
    // MARK: - Security
    
    private static func configureSecurity() {
        // Security Manager
        shared.register(SecurityManagerProtocol.self) { _ in
            ALADDINSecurityManager()
        }.inObjectScope(.container)
        
        // Jailbreak Detector
        shared.register(JailbreakDetectorProtocol.self) { _ in
            JailbreakDetector.shared
        }.inObjectScope(.container)
        
        // RASP Manager
        shared.register(RASPManagerProtocol.self) { _ in
            RASPManager.shared
        }.inObjectScope(.container)
        
        // Anti-Tampering Manager
        shared.register(AntiTamperingManagerProtocol.self) { _ in
            AntiTamperingManager.shared
        }.inObjectScope(.container)
    }
    
    // MARK: - AI & Support
    
    private static func configureAI() {
        // AI Support Assistant API
        shared.register(AIAssistantProtocol.self) { _ in
            UnifiedSupportAPI()
        }.inObjectScope(.container)
        
        // Support API Client
        shared.register(SupportAPIClientProtocol.self) { _ in
            SupportAPIClient()
        }.inObjectScope(.container)
        
        // Support API Manager
        shared.register(SupportAPIManagerProtocol.self) { resolver in
            SupportAPIManager(
                apiClient: resolver.resolve(SupportAPIClientProtocol.self)!
            )
        }.inObjectScope(.container)
    }
    
    // MARK: - VPN
    
    private static func configureVPN() {
        // VPN Client
        shared.register(VPNClientProtocol.self) { _ in
            ALADDINVPNClient()
        }.inObjectScope(.container)
        
        // VPN Manager
        shared.register(VPNManagerProtocol.self) { resolver in
            VPNManager(
                vpnClient: resolver.resolve(VPNClientProtocol.self)!
            )
        }.inObjectScope(.container)
    }
    
    // MARK: - ViewModels
    
    private static func configureViewModels() {
        // Main ViewModel
        shared.register(MainViewModel.self) { resolver in
            MainViewModel(
                networkManager: resolver.resolve(NetworkManagerProtocol.self)!,
                aiAssistant: resolver.resolve(AIAssistantProtocol.self)!,
                securityManager: resolver.resolve(SecurityManagerProtocol.self)!
            )
        }
        
        // Protection ViewModel
        shared.register(ProtectionViewModel.self) { resolver in
            ProtectionViewModel(
                vpnManager: resolver.resolve(VPNManagerProtocol.self)!,
                securityManager: resolver.resolve(SecurityManagerProtocol.self)!
            )
        }
        
        // Family ViewModel
        shared.register(FamilyViewModel.self) { resolver in
            FamilyViewModel(
                networkManager: resolver.resolve(NetworkManagerProtocol.self)!
            )
        }
        
        // Analytics ViewModel
        shared.register(AnalyticsViewModel.self) { resolver in
            AnalyticsViewModel(
                networkManager: resolver.resolve(NetworkManagerProtocol.self)!
            )
        }
        
        // Settings ViewModel
        shared.register(SettingsViewModel.self) { resolver in
            SettingsViewModel(
                networkManager: resolver.resolve(NetworkManagerProtocol.self)!,
                securityManager: resolver.resolve(SecurityManagerProtocol.self)!
            )
        }
        
        // Support ViewModel
        shared.register(SupportViewModel.self) { resolver in
            SupportViewModel(
                supportAPIManager: resolver.resolve(SupportAPIManagerProtocol.self)!
            )
        }
    }
    
    // MARK: - ViewControllers
    
    private static func configureViewControllers() {
        // Main ViewController
        shared.register(MainViewController.self) { resolver in
            let viewController = MainViewController()
            viewController.viewModel = resolver.resolve(MainViewModel.self)!
            return viewController
        }
        
        // Protection ViewController
        shared.register(ProtectionViewController.self) { resolver in
            let viewController = ProtectionViewController()
            viewController.viewModel = resolver.resolve(ProtectionViewModel.self)!
            return viewController
        }
        
        // Family ViewController
        shared.register(FamilyViewController.self) { resolver in
            let viewController = FamilyViewController()
            viewController.viewModel = resolver.resolve(FamilyViewModel.self)!
            return viewController
        }
        
        // Analytics ViewController
        shared.register(AnalyticsViewController.self) { resolver in
            let viewController = AnalyticsViewController()
            viewController.viewModel = resolver.resolve(AnalyticsViewModel.self)!
            return viewController
        }
        
        // Settings ViewController
        shared.register(SettingsViewController.self) { resolver in
            let viewController = SettingsViewController()
            viewController.viewModel = resolver.resolve(SettingsViewModel.self)!
            return viewController
        }
        
        // Support Chat Interface
        shared.register(SupportChatInterface.self) { resolver in
            let viewController = SupportChatInterface()
            viewController.viewModel = resolver.resolve(SupportViewModel.self)!
            return viewController
        }
    }
    
    // MARK: - Helper Methods
    
    /// Получить экземпляр из контейнера
    static func resolve<T>(_ serviceType: T.Type) -> T? {
        return shared.resolve(serviceType)
    }
    
    /// Проверить, зарегистрирован ли сервис
    static func isRegistered<T>(_ serviceType: T.Type) -> Bool {
        return shared.resolve(serviceType) != nil
    }
    
    /// Очистить контейнер (для тестирования)
    static func reset() {
        shared.removeAll()
    }
}

// MARK: - Protocols

// Networking Protocols
protocol NetworkManagerProtocol {
    func secureRequest<T: Codable>(_ endpoint: String, method: HTTPMethod, parameters: Parameters?, headers: HTTPHeaders?, responseType: T.Type, completion: @escaping (Result<T, Error>) -> Void)
}

protocol CertificatePinningManagerProtocol {
    func validateCertificate(_ serverTrust: SecTrust, host: String) -> Bool
}

// Security Protocols
protocol SecurityManagerProtocol {
    func performSecurityChecks() -> Bool
    func getSecurityStatus() -> SecurityStatus
}

protocol JailbreakDetectorProtocol {
    func detectJailbreak() -> JailbreakDetectionResult
}

protocol RASPManagerProtocol {
    func startMonitoring()
    func stopMonitoring()
    func getMonitoringStatus() -> RASPStatus
}

protocol AntiTamperingManagerProtocol {
    func validateAppIntegrity() -> TamperingDetectionResult
}

// AI & Support Protocols
protocol AIAssistantProtocol {
    func processRequest(_ request: String, completion: @escaping (Result<String, Error>) -> Void)
}

protocol SupportAPIClientProtocol {
    func sendRequest(_ request: SupportRequest, completion: @escaping (Result<SupportResponse, Error>) -> Void)
}

protocol SupportAPIManagerProtocol {
    func processMessage(_ message: String, category: SupportCategory, priority: PriorityLevel, completion: @escaping (Result<SupportResponse, Error>) -> Void)
}

// VPN Protocols
protocol VPNClientProtocol {
    func connect(to server: String, completion: @escaping (Result<Bool, Error>) -> Void)
    func disconnect(completion: @escaping (Result<Bool, Error>) -> Void)
}

protocol VPNManagerProtocol {
    func getConnectionStatus() -> VPNConnectionStatus
    func getAvailableServers() -> [VPNServer]
}

// Security Status
struct SecurityStatus {
    let isJailbroken: Bool
    let isBeingDebugged: Bool
    let isTampered: Bool
    let overallStatus: SecurityLevel
}

