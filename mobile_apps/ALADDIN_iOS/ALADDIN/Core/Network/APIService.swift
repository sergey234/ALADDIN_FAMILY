import Foundation
import Combine

/**
 * 🔌 API Service
 * Удобные методы для работы с API
 * Используется ViewModels для загрузки данных
 */

class APIService {
    
    private let networkManager: NetworkManager
    
    init(networkManager: NetworkManager) {
        self.networkManager = networkManager
    }
    
    // MARK: - VPN API
    
    func getVPNStatus(completion: @escaping (Result<VPNStatusResponse, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.vpnStatus, completion: completion)
    }
    
    func connectVPN(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.vpnConnect, body: EmptyBody(), completion: completion)
    }
    
    func disconnectVPN(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.vpnDisconnect, body: EmptyBody(), completion: completion)
    }
    
    func getVPNServers(completion: @escaping (Result<[VPNServer], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.vpnServers, completion: completion)
    }
    
    // MARK: - Family API
    
    func getFamilyMembers(completion: @escaping (Result<[FamilyMemberResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.familyMembers, completion: completion)
    }
    
    func addFamilyMember(name: String, role: String, completion: @escaping (Result<FamilyMemberResponse, Error>) -> Void) {
        struct AddMemberRequest: Codable {
            let name: String
            let role: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.addFamilyMember, body: AddMemberRequest(name: name, role: role), completion: completion)
    }
    
    func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
        networkManager.get(endpoint: "/family/stats", completion: completion)
    }
    
    // MARK: - Analytics API
    
    func getAnalytics(period: String, completion: @escaping (Result<AnalyticsResponse, Error>) -> Void) {
        networkManager.get(endpoint: "\(AppConfig.Endpoint.analytics)?period=\(period)", completion: completion)
    }
    
    func getTopThreats(completion: @escaping (Result<[ThreatItem], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.topThreats, completion: completion)
    }
    
    // MARK: - AI Assistant API
    
    func sendMessageToAI(message: String, completion: @escaping (Result<ChatMessageResponse, Error>) -> Void) {
        let request = ChatMessageRequest(
            message: message,
            userId: AppConfig.authToken ?? "guest",
            timestamp: Date()
        )
        networkManager.post(endpoint: AppConfig.Endpoint.aiSendMessage, body: request, completion: completion)
    }
    
    // MARK: - User API
    
    func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.profile, completion: completion)
    }
    
    func updateProfile(name: String?, email: String?, phone: String?, completion: @escaping (Result<UserProfile, Error>) -> Void) {
        let request = UpdateProfileRequest(name: name, email: email, phone: phone)
        networkManager.post(endpoint: AppConfig.Endpoint.updateProfile, body: request, completion: completion)
    }
    
    // MARK: - Notifications API
    
    func getNotifications(completion: @escaping (Result<[NotificationResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.notifications, completion: completion)
    }
    
    func markNotificationAsRead(notificationId: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct MarkReadRequest: Codable {
            let notificationId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.markRead, body: MarkReadRequest(notificationId: notificationId), completion: completion)
    }
    
    // MARK: - Subscription API
    
    func getTariffs(completion: @escaping (Result<[TariffResponse], Error>) -> Void) {
        networkManager.get(endpoint: AppConfig.Endpoint.tariffs, completion: completion)
    }
    
    func subscribe(tariffId: String, completion: @escaping (Result<SubscriptionStatus, Error>) -> Void) {
        struct SubscribeRequest: Codable {
            let tariffId: String
        }
        networkManager.post(endpoint: AppConfig.Endpoint.subscribe, body: SubscribeRequest(tariffId: tariffId), completion: completion)
    }
    
    // MARK: - Auth API
    
    func login(email: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        let request = LoginRequest(email: email, password: password)
        networkManager.post(endpoint: AppConfig.Endpoint.login, body: request, completion: completion)
    }
    
    func logout(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        struct EmptyBody: Codable {}
        networkManager.post(endpoint: AppConfig.Endpoint.logout, body: EmptyBody(), completion: completion)
    }
}




