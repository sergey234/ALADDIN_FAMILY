import Foundation

enum ContentExperienceRoute: String, CaseIterable, Hashable {
    case game
    case lesson
    case video
    case story
    case song
    case drawing
    case safety
    case career

    init(itemType: ContentItemType) {
        switch itemType {
        case .game: self = .game
        case .lesson: self = .lesson
        case .video: self = .video
        case .story: self = .story
        case .song: self = .song
        case .drawing: self = .drawing
        case .safety: self = .safety
        case .career: self = .career
        }
    }

    var systemImage: String {
        switch self {
        case .game: return "gamecontroller.fill"
        case .lesson: return "book.fill"
        case .video: return "play.rectangle.fill"
        case .story: return "text.book.closed.fill"
        case .song: return "music.note"
        case .drawing: return "paintpalette.fill"
        case .safety: return "shield.checkered"
        case .career: return "briefcase.fill"
        }
    }

    var accentHexName: String {
        switch self {
        case .game: return "purple"
        case .lesson: return "blue"
        case .video: return "orange"
        case .story: return "indigo"
        case .song: return "pink"
        case .drawing: return "teal"
        case .safety: return "green"
        case .career: return "mint"
        }
    }
}
