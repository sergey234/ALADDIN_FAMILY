import Foundation

/**
 * 📋 Content Blocker Rule
 * Модель для правил блокировки контента в Safari
 * Соответствует формату Apple Content Blocker Extension
 */

// MARK: - Content Blocker Rule

struct ContentBlockerRule: Codable {
    let trigger: Trigger
    let action: Action
}

// MARK: - Trigger

struct Trigger: Codable {
    /// URL фильтр (регулярное выражение или паттерн)
    let urlFilter: String
    
    /// Домены, для которых применяется правило (опционально)
    let ifDomain: [String]?
    
    /// Домены, для которых правило НЕ применяется (опционально)
    let unlessDomain: [String]?
    
    /// Тип ресурса для блокировки (опционально)
    let resourceType: [String]?
    
    /// Загрузка только для верхнего фрейма (опционально)
    let loadType: [String]?
    
    /// Если-топ-URL (опционально)
    let ifTopUrl: [String]?
    
    enum CodingKeys: String, CodingKey {
        case urlFilter = "url-filter"
        case ifDomain = "if-domain"
        case unlessDomain = "unless-domain"
        case resourceType = "resource-type"
        case loadType = "load-type"
        case ifTopUrl = "if-top-url"
    }
}

// MARK: - Action

struct Action: Codable {
    /// Тип действия: "block", "block-cookies", "css-display-none"
    let type: String
    
    /// Селектор CSS (для css-display-none)
    let selector: String?
}

// MARK: - Content Blocker Category

enum ContentBlockerCategory: String, CaseIterable, Codable {
    case adult = "adult"
    case violence = "violence"
    case gambling = "gambling"
    case socialMedia = "social_media"
    case video = "video"
    case games = "games"
    case shopping = "shopping"
    case news = "news"
    case forums = "forums"
    case fileSharing = "file_sharing"
    case proxy = "proxy"
    case vpn = "vpn"
    
    var displayName: String {
        switch self {
        case .adult: return "Взрослый контент"
        case .violence: return "Насилие"
        case .gambling: return "Азартные игры"
        case .socialMedia: return "Социальные сети"
        case .video: return "Видео (YouTube)"
        case .games: return "Игры"
        case .shopping: return "Покупки"
        case .news: return "Новости"
        case .forums: return "Форумы"
        case .fileSharing: return "Файлообменники"
        case .proxy: return "Прокси-серверы"
        case .vpn: return "VPN сервисы"
        }
    }
    
    var icon: String {
        switch self {
        case .adult: return "🔞"
        case .violence: return "⚔️"
        case .gambling: return "🎰"
        case .socialMedia: return "📱"
        case .video: return "📺"
        case .games: return "🎮"
        case .shopping: return "🛒"
        case .news: return "📰"
        case .forums: return "💬"
        case .fileSharing: return "📦"
        case .proxy: return "🔀"
        case .vpn: return "🔒"
        }
    }
    
    /// Домены для блокировки по категории
    var blockedDomains: [String] {
        switch self {
        case .adult:
            return [
                ".*porn.*",
                ".*xxx.*",
                ".*adult.*",
                ".*sex.*"
            ]
        case .violence:
            return [
                ".*violence.*",
                ".*gore.*",
                ".*weapon.*"
            ]
        case .gambling:
            return [
                ".*casino.*",
                ".*poker.*",
                ".*bet.*",
                ".*gambling.*",
                ".*lottery.*"
            ]
        case .socialMedia:
            return [
                ".*facebook.*",
                ".*instagram.*",
                ".*twitter.*",
                ".*tiktok.*",
                ".*snapchat.*"
            ]
        case .video:
            return [
                ".*youtube.*",
                ".*vimeo.*",
                ".*dailymotion.*"
            ]
        case .games:
            return [
                ".*steam.*",
                ".*epicgames.*",
                ".*roblox.*"
            ]
        case .shopping:
            return [
                ".*amazon.*",
                ".*ebay.*",
                ".*aliexpress.*"
            ]
        case .news:
            return []
        case .forums:
            return [
                ".*reddit.*",
                ".*4chan.*"
            ]
        case .fileSharing:
            return [
                ".*torrent.*",
                ".*pirate.*"
            ]
        case .proxy:
            return [
                ".*proxy.*",
                ".*vpn.*"
            ]
        case .vpn:
            return [
                ".*vpn.*",
                ".*tunnel.*"
            ]
        }
    }
}

// MARK: - Content Blocker Status

enum ContentBlockerStatus {
    case disabled
    case enabled
    case needsActivation // Пользователь должен включить в настройках iOS
    case extensionMissing // Extension target отсутствует/не установлен в сборке
    case error(String)
}

