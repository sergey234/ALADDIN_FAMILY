import Foundation
import Security

/// 🔐 JWT Token Manager
/// Управление JWT токенами: проверка истечения, автоматическое обновление
class JWTTokenManager {
    static let shared = JWTTokenManager()
    
    private let keychainManager = KeychainManager.shared
    
    // ✅ Защита от множественных одновременных запросов на обновление токена
    private var isRefreshing = false
    private var refreshTask: Task<Bool, Never>?
    
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
    
    /// Принудительно обновляет токен (для обработки 401 ошибок) - прямой HTTP запрос без рекурсии
    /// ✅ ИСПРАВЛЕНО: Защита от множественных одновременных запросов
    func forceRefreshToken() async -> Bool {
        // ✅ Если уже обновляется, ждём завершения существующей задачи
        if let existingTask = refreshTask {
            print("🔄 JWT: Обновление токена уже выполняется, ждём завершения...")
            return await existingTask.value
        }
        
        print("🔄 JWT: Принудительное обновление токена...")

        // Получаем refresh token
        guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
            print("❌ JWT: Refresh token не найден в Keychain")
            return false
        }

        // ✅ Создаём задачу обновления токена (защита от параллельных запросов)
        refreshTask = Task {
            // Делаем прямой HTTP запрос без использования NetworkManager, чтобы избежать бесконечного цикла
            let result = await directRefreshTokenRequest(refreshToken: refreshToken)
            return result
        }
        
        let result = await refreshTask!.value
        refreshTask = nil // Очищаем задачу после завершения
        return result
    }

    /// Проверяет, есть ли валидный токен
    func hasValidToken() -> Bool {
        guard let accessToken = keychainManager.loadString(forKey: .authToken) else {
            return false
        }
        return !isTokenExpired(accessToken)
    }

    /// Проверяет и обновляет токен если нужно
    /// Возвращает true только если токен был действительно обновлен
    /// ✅ ИСПРАВЛЕНО: Использует прямой запрос вместо NetworkManager, чтобы избежать бесконечного цикла
    /// ✅ ИСПРАВЛЕНО: Защита от множественных одновременных запросов
    func refreshTokenIfNeeded() async -> Bool {
        // ✅ Если уже обновляется, ждём завершения существующей задачи
        if let existingTask = refreshTask {
            print("🔄 JWT: Обновление токена уже выполняется, ждём завершения...")
            return await existingTask.value
        }
        
        guard let accessToken = keychainManager.loadString(forKey: .authToken) else {
            print("❌ JWT: Access token не найден в Keychain")
            return false
        }
        
        // Проверяем, не истёк ли токен
        if !isTokenExpired(accessToken) {
            print("✅ JWT: Access token действителен, обновление не требуется")
            return false // Возвращаем false - токен не был обновлен
        }
        
        print("🔄 JWT: Access token истёк, обновляем...")
        
        // Получаем refresh token
        guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
            print("❌ JWT: Refresh token не найден в Keychain")
            return false
        }
        
        // ✅ Создаём задачу обновления токена (защита от параллельных запросов)
        refreshTask = Task {
            // ✅ ИСПРАВЛЕНО: Используем прямой запрос вместо NetworkManager.post()
            // Это предотвращает бесконечный цикл, так как directRefreshTokenRequest
            // не использует NetworkManager, который снова вызывает refreshTokenIfNeeded()
            let result = await directRefreshTokenRequest(refreshToken: refreshToken)
            return result
        }
        
        let result = await refreshTask!.value
        refreshTask = nil // Очищаем задачу после завершения
        return result
    }
    
    /// Прямой HTTP запрос на обновление токена (без использования NetworkManager, чтобы избежать бесконечного цикла)
    private func directRefreshTokenRequest(refreshToken: String) async -> Bool {
        print("🔄 JWT: Прямой HTTP запрос на обновление токена...")

        return await withCheckedContinuation { continuation in
            let urlString = AppConfig.apiBaseURL + "/auth/refresh"
            guard let url = URL(string: urlString) else {
                print("❌ JWT: Неверный URL для обновления токена")
                continuation.resume(returning: false)
                return
            }

            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            struct RefreshTokenRequest: Codable {
                let refresh_token: String
            }

            let requestBody = RefreshTokenRequest(refresh_token: refreshToken)

            do {
                request.httpBody = try JSONEncoder().encode(requestBody)
            } catch {
                print("❌ JWT: Ошибка кодирования тела запроса: \(error)")
                continuation.resume(returning: false)
                return
            }

            let task = URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    print("❌ JWT: Сетевая ошибка при обновлении токена: \(error.localizedDescription)")
                    continuation.resume(returning: false)
                    return
                }

                guard let httpResponse = response as? HTTPURLResponse else {
                    print("❌ JWT: Неверный HTTP ответ")
                    continuation.resume(returning: false)
                    return
                }

                guard let data = data else {
                    print("❌ JWT: Пустой ответ от сервера")
                    continuation.resume(returning: false)
                    return
                }

                if httpResponse.statusCode == 200 {
                    do {
                        let response = try JSONDecoder().decode(RefreshTokenResponse.self, from: data)

                        // Сохраняем новый access token
                        self.keychainManager.save(response.access_token, forKey: .authToken)

                        // Сохраняем новый refresh token если он есть
                        if let newRefreshToken = response.refresh_token {
                            self.keychainManager.save(newRefreshToken, forKey: .refreshToken)
                        }

                        print("✅ JWT: Токен успешно обновлён через прямой запрос")
                        continuation.resume(returning: true)

                    } catch {
                        print("❌ JWT: Ошибка декодирования ответа: \(error)")
                        continuation.resume(returning: false)
                    }
                } else {
                    if let responseString = String(data: data, encoding: .utf8) {
                        print("❌ JWT: Ошибка сервера (\(httpResponse.statusCode)): \(responseString)")
                    } else {
                        print("❌ JWT: Ошибка сервера (\(httpResponse.statusCode))")
                    }
                    continuation.resume(returning: false)
                }
            }
            task.resume()
        }
    }
    
    /// Обновляет access token используя refresh token
    private func refreshAccessToken(refreshToken: String) async -> Bool {
        print("🔄 JWT: Отправляем запрос на обновление токена...")
        
        return await withCheckedContinuation { continuation in
            // Используем NetworkManager из APIService, чтобы избежать создания лишних экземпляров
            let networkManager = APIService.shared.networkManager

            struct RefreshTokenRequest: Codable {
                let refresh_token: String
            }

            let request = RefreshTokenRequest(refresh_token: refreshToken)

            networkManager.post(endpoint: "/auth/refresh", body: request) { [weak self] (result: Result<RefreshTokenResponse, Error>) in
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

