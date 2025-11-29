import SwiftUI
import UIKit

/// Helper для открытия внешних ссылок (Safari / системный браузер)
struct URLHelper {
    
    /// Открыть ссылку на сайт с опциональным `tariffId` и `referralCode`
    /// - Parameters:
    ///   - urlString: базовый URL (например, AppConfig.subscriptionWebsiteURL)
    ///   - tariffId: идентификатор тарифа, который нужно передать как query-параметр
    ///   - referralCode: реферальный код, который нужно передать как query-параметр `ref`
    static func openWebsite(urlString: String, tariffId: String? = nil, referralCode: String? = nil) {
        var finalURLString = urlString
        var queryParams: [String] = []
        
        // Добавить tariffId
        if let tariffId = tariffId, !tariffId.isEmpty {
            queryParams.append("tariff=\(tariffId)")
        }
        
        // Добавить referralCode
        if let referralCode = referralCode, !referralCode.isEmpty {
            queryParams.append("ref=\(referralCode)")
        }
        
        // Объединить параметры
        if !queryParams.isEmpty {
            let separator = urlString.contains("?") ? "&" : "?"
            finalURLString = "\(urlString)\(separator)\(queryParams.joined(separator: "&"))"
        }
        
        guard let url = URL(string: finalURLString) else {
            print("❌ URLHelper.openWebsite: невалидный URL \(finalURLString)")
            return
        }
        
        print("✅ URLHelper.openWebsite: открываем URL \(finalURLString)")
        UIApplication.shared.open(url, options: [:], completionHandler: nil)
    }
}

