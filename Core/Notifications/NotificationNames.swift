import Foundation

/// Имена уведомлений для системы
extension Notification.Name {
    /// Уведомление о покупке тарифа
    static let tariffPurchased = Notification.Name("tariffPurchased")
    
    /// Уведомление об изменении тарифа
    static let tariffChanged = Notification.Name("tariffChanged")
    
    /// Уведомление об успешной оплате через QR
    static let paymentQRSuccess = Notification.Name("paymentQRSuccess")

    /// Access JWT обновлён (refresh / keychain) — WebSocket и долгоживущие сессии должны перечитать `AppConfig.authToken`.
    static let appAuthAccessTokenDidChange = Notification.Name("appAuthAccessTokenDidChange")
}

