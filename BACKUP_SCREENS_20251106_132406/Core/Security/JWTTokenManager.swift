import Foundation
import Security

/// 🔐 JWT Token Manager
/// Управление JWT токенами: проверка истечения, автоматическое обновление
class JWTTokenManager {
    static let shared = JWTTokenManager()
    
    private let keychainManager = KeychainManager.shared
    
    private init() {}
    
    // MARK: - Token Expiration Check
    
    /// Проверяет, истёк ли токен
    func isTokenExpired(_ token: String) -> Bool {
        guard let payload = decodeJWTPayload(token) else {
            print("⚠️ JWT: Не удалось декодировать токен - считаем истёкшим")
            return true // Если не можем декодировать, считаем истёкшим
        }
        
        guard let exp = payload["exp"] as? TimeInterval else {
            print("⚠️ JWT: Нет поля exp в токене - считаем истёкшим")
            return true // Если нет поля exp, считаем истёкшим
        }
        
        let expirationDate = Date(timeIntervalSince1970: exp)
        let isExpired = expirationDate < Date()
        
        if isExpired {
            let timeSinceExpiration = Date().timeIntervalSince(expirationDate)
            print("⚠️ JWT Token истёк \(Int(timeSinceExpiration)) секунд назад (истёк: \(expirationDate))")
        } else {
            let timeUntilExpiration = expirationDate.timeIntervalSinceNow
            print("✅ JWT Token действителен ещё \(Int(timeUntilExpiration)) секунд (истекает: \(expirationDate))")
        }
        
        return isExpired
    }
    
    /// Декодирует JWT payload
    private func decodeJWTPayload(_ token: String) -> [String: Any]? {
        let parts = token.components(separatedBy: ".")
        guard parts.count == 3 else {
            print("❌ JWT: Неверный формат токена (ожидается 3 части, получено: \(parts.count))")
            return nil
        }
        
        let payload = parts[1]
        
        // Добавляем padding если нужно
        var base64 = payload
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        
        let remainder = base64.count % 4
        if remainder > 0 {
            base64 = base64.padding(toLength: base64.count + 4 - remainder, withPad: "=", startingAt: 0)
        }
        
        guard let data = Data(base64Encoded: base64) else {
            print("❌ JWT: Не удалось декодировать base64 payload")
            return nil
        }
        
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            print("❌ JWT: Не удалось распарсить JSON payload")
            return nil
        }
        
        return json
    }
    
    // MARK: - Token Refresh
    
    /// Проверяет и обновляет токен если нужно
    func refreshTokenIfNeeded() async -> Bool {
        guard let accessToken: String = keychainManager.load(String.self, forKey: .authToken) else {
            print("❌ JWT: Access token не найден в Keychain")
            return false
        }
        
        // Проверяем, не истёк ли токен
        if !isTokenExpired(accessToken) {
            print("✅ JWT: Access token действителен, обновление не требуется")
            return true
        }
        
        print("🔄 JWT: Access token истёк, обновляем...")
        
        // Получаем refresh token
        guard let refreshToken: String = keychainManager.load(String.self, forKey: .refreshToken) else {
            print("❌ JWT: Refresh token не найден в Keychain")
            return false
        }
        
        // Обновляем токен через API
        return await refreshAccessToken(refreshToken: refreshToken)
    }
    
    /// Обновляет access token используя refresh token
    private func refreshAccessToken(refreshToken: String) async -> Bool {
        print("🔄 JWT: Отправляем запрос на обновление токена...")
        
        return await withCheckedContinuation { continuation in
            APIService.shared.refreshToken(refreshToken: refreshToken) { [weak self] result in
                switch result {
                case .success(let response):
                    // Сохраняем новый access token
                    self?.keychainManager.save(response.access_token, forKey: .authToken)
                    
                    // Сохраняем новый refresh token если он есть
                    if let newRefreshToken = response.refresh_token {
                        self?.keychainManager.save(newRefreshToken, forKey: .refreshToken)
                    }
                    
                    print("✅ JWT: Токен успешно обновлён")
                    continuation.resume(returning: true)
                    
                case .failure(let error):
                    print("❌ JWT: Ошибка обновления токена: \(error.localizedDescription)")
                    continuation.resume(returning: false)
                }
            }
        }
    }
    
    // MARK: - Token Validation
    
    /// Проверяет валидность токена (не истёк и правильно отформатирован)
    func isTokenValid(_ token: String?) -> Bool {
        guard let token = token, !token.isEmpty else {
            return false
        }
        
        // Проверяем формат (должно быть 3 части разделённые точками)
        let parts = token.components(separatedBy: ".")
        guard parts.count == 3 else {
            return false
        }
        
        // Проверяем, не истёк ли токен
        return !isTokenExpired(token)
    }
    
    /// Получает время истечения токена
    func getTokenExpirationDate(_ token: String) -> Date? {
        guard let payload = decodeJWTPayload(token),
              let exp = payload["exp"] as? TimeInterval else {
            return nil
        }
        
        return Date(timeIntervalSince1970: exp)
    }
    
    /// Получает время до истечения токена в секундах
    func getTimeUntilExpiration(_ token: String) -> TimeInterval? {
        guard let expirationDate = getTokenExpirationDate(token) else {
            return nil
        }
        
        let timeUntilExpiration = expirationDate.timeIntervalSinceNow
        return timeUntilExpiration > 0 ? timeUntilExpiration : 0
    }
}

