import Foundation

/// 🔐 Token Manager
/// Умная проверка токена: различает ситуации когда токен загружается vs когда его нет
/// Используется для предотвращения ложных срабатываний SessionExpired
@MainActor
class TokenManager {
    static let shared = TokenManager()
    
    private let keychainManager = KeychainManager.shared
    private var tokenLoadingState: TokenLoadingState = .unknown
    
    private init() {}
    
    // MARK: - Logging
    
    private func log(_ message: String, level: VisualLogger.LogLevel = .info) {
        #if DEBUG
        VisualLogger.shared.log(message, level: level, category: "TOKEN")
        print(message) // Также в консоль для Xcode
        #endif
    }
    
    // MARK: - Token Loading State
    
    enum TokenLoadingState {
        case unknown
        case loading
        case loaded
        case notFound
    }
    
    // MARK: - Smart Token Check
    
    /// Умная проверка токена
    /// Различает ситуации:
    /// - Токен есть в AppConfig → ✅ Доступен
    /// - Токена нет в AppConfig, но есть в SubscriptionManager → ⏳ Загружается
    /// - Токена нет в SubscriptionManager, но есть в Keychain → ⏳ Загружается
    /// - Токена нет нигде → ❌ Не найден
    func checkTokenAvailability() -> TokenAvailability {
        log("🔍 TokenManager: Проверка доступности токена", level: .debug)
        
        // 1. Проверяем токен в AppConfig (быстрая проверка)
        if let token = AppConfig.authToken, !token.isEmpty {
            tokenLoadingState = .loaded
            log("✅ TokenManager: Токен найден в AppConfig (длина: \(token.count))", level: .success)
            return .available(token)
        }
        
        log("⚠️ TokenManager: Токен не найден в AppConfig, проверяем SubscriptionManager...", level: .warning)
        
        // 2. ✅ КРИТИЧНО: Проверяем токен в SubscriptionManager (ГЛАВНОЕ ХРАНИЛИЩЕ!)
        if let subscriptionToken = SubscriptionManager.shared.currentToken {
            // Токен есть в SubscriptionManager, но не в AppConfig - восстанавливаем
            AppConfig.authToken = subscriptionToken.token
            tokenLoadingState = .loaded
            log("✅ TokenManager: Токен найден в SubscriptionManager, восстановлен в AppConfig (длина: \(subscriptionToken.token.count), deviceId: \(subscriptionToken.deviceId))", level: .success)
            return .available(subscriptionToken.token)
        }
        
        log("⚠️ TokenManager: Токен не найден в SubscriptionManager, проверяем Keychain...", level: .warning)
        
        // 3. Проверяем токен в Keychain (fallback)
        if let keychainToken = keychainManager.loadString(forKey: .authToken),
           !keychainToken.isEmpty {
            // Токен есть в Keychain, но не в AppConfig - значит он загружается
            // Обновляем AppConfig для будущих проверок
            AppConfig.authToken = keychainToken
            tokenLoadingState = .loaded
            log("✅ TokenManager: Токен найден в Keychain, восстановлен в AppConfig (длина: \(keychainToken.count))", level: .success)
            return .available(keychainToken)
        }
        
        // 4. Токена нет нигде
        tokenLoadingState = .notFound
        log("❌ TokenManager: Токен не найден ни в AppConfig, ни в SubscriptionManager, ни в Keychain", level: .error)
        return .notFound
    }
    
    /// Проверяет, загружается ли токен (есть в SubscriptionManager или Keychain, но не в AppConfig)
    func isTokenLoading() -> Bool {
        if AppConfig.authToken != nil {
            log("✅ TokenManager: Токен уже загружен в AppConfig", level: .success)
            return false // Токен уже загружен
        }
        
        // Проверяем SubscriptionManager (главное хранилище)
        let hasSubscriptionToken = SubscriptionManager.shared.currentToken != nil
        if hasSubscriptionToken {
            log("🔍 TokenManager: Проверка загрузки токена - SubscriptionManager: ✅ есть", level: .debug)
            return true
        }
        
        // Проверяем Keychain (fallback)
        let isAvailable = keychainManager.isDataAvailable(forKey: .authToken)
        log("🔍 TokenManager: Проверка загрузки токена - Keychain: \(isAvailable ? "✅ есть" : "❌ нет")", level: .debug)
        return isAvailable
    }
    
    /// Ждет загрузки токена (максимум указанное время)
    func waitForTokenLoad(maxWaitTime: TimeInterval = 0.5) async -> String? {
        log("⏳ TokenManager: Ожидание загрузки токена (макс. \(maxWaitTime)s)...", level: .info)
        let startTime = Date()
        
        while Date().timeIntervalSince(startTime) < maxWaitTime {
            // 1. Проверяем AppConfig
            if let token = AppConfig.authToken, !token.isEmpty {
                log("✅ TokenManager: Токен загрузился в AppConfig (длина: \(token.count))", level: .success)
                return token
            }
            
            // 2. Проверяем SubscriptionManager (главное хранилище)
            if let subscriptionToken = SubscriptionManager.shared.currentToken {
                AppConfig.authToken = subscriptionToken.token
                log("✅ TokenManager: Токен загрузился из SubscriptionManager в AppConfig (длина: \(subscriptionToken.token.count))", level: .success)
                return subscriptionToken.token
            }
            
            // 3. Проверяем Keychain (fallback)
            if let keychainToken = keychainManager.loadString(forKey: .authToken),
               !keychainToken.isEmpty {
                AppConfig.authToken = keychainToken
                log("✅ TokenManager: Токен загрузился из Keychain в AppConfig (длина: \(keychainToken.count))", level: .success)
                return keychainToken
            }
            
            // Ждем немного перед следующей проверкой
            try? await Task.sleep(nanoseconds: 50_000_000) // 50ms
        }
        
        log("⏰ TokenManager: Время ожидания истекло, токен не загрузился", level: .warning)
        return nil
    }
}

// MARK: - Token Availability Result

enum TokenAvailability {
    case available(String) // Токен доступен
    case notFound          // Токен не найден
    case loading           // Токен загружается (есть в Keychain, но не в AppConfig)
    
    var isAvailable: Bool {
        if case .available = self {
            return true
        }
        return false
    }
    
    var token: String? {
        if case .available(let token) = self {
            return token
        }
        return nil
    }
}
