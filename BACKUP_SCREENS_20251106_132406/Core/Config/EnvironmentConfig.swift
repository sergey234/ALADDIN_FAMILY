import Foundation

enum EnvironmentConfig {
    static let baseURL: URL = URL(string: "https://api.aladdin.family")!
    static var useRemoteAnalytics: Bool { false } // переключение при подключении сервера
    static func authToken() -> String? { nil } // подключить Keychain/Session при готовности
}








