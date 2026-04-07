import Foundation

struct DeviceRegistrationSubscription: Codable {
    let level: String
    let startDate: String?
    let expiresAt: String?
    let isActive: Bool
    let trialInfo: String?
    let limits: String?
    let permissions: String?
    let deviceId: String?
    let userId: Int?
}

struct JWTDeviceRegisterResponse: Codable {
    let token: String
    let refreshToken: String?
    let deviceId: String
    let expiresAt: String
    let registeredAt: String
    let subscription: DeviceRegistrationSubscription
    
    let expiresIn: Int?
    let tokenType: String?

    enum CodingKeys: String, CodingKey {
        case token = "access_token"
        case refreshToken = "refresh_token"
        case deviceId = "device_id"
        case expiresAt = "expires_at"
        case registeredAt = "registered_at"
        case subscription
        case expiresIn = "expires_in"
        case tokenType = "token_type"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        if let accessToken = try container.decodeIfPresent(String.self, forKey: .token) {
            self.token = accessToken
        } else {
            throw DecodingError.keyNotFound(CodingKeys.token, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "not found"))
        }
        
        self.refreshToken = try container.decodeIfPresent(String.self, forKey: .refreshToken)
        self.deviceId = try container.decodeIfPresent(String.self, forKey: .deviceId) ?? "unknown_device"
        self.expiresAt = try container.decodeIfPresent(String.self, forKey: .expiresAt) ?? ""
        self.registeredAt = try container.decodeIfPresent(String.self, forKey: .registeredAt) ?? ""
        self.subscription = try container.decodeIfPresent(DeviceRegistrationSubscription.self, forKey: .subscription) ?? DeviceRegistrationSubscription(level: "free", startDate: nil, expiresAt: nil, isActive: true, trialInfo: nil, limits: nil, permissions: nil, deviceId: nil, userId: nil)
        
        self.expiresIn = try container.decodeIfPresent(Int.self, forKey: .expiresIn)
        self.tokenType = try container.decodeIfPresent(String.self, forKey: .tokenType)
    }
}

let jsonStr = """
{"access_token":"eyJhbG...","refresh_token":"eyJhbG...","expires_in":86400,"token_type":"Bearer"}
"""

let data = jsonStr.data(using: .utf8)!
do {
    let decoded = try JSONDecoder().decode(JWTDeviceRegisterResponse.self, from: data)
    print("Success: \(decoded.token)")
} catch {
    print("Error: \(error)")
}
