import Foundation

struct ContentExperienceResolver {
    static let shared = ContentExperienceResolver()

    private let supportedTypes: Set<ContentItemType> = [
        .game, .lesson, .video, .story, .song, .drawing, .safety, .career
    ]

    private init() {}

    func resolve(for item: ContentItem) -> ContentExperienceRoute? {
        guard supportedTypes.contains(item.type) else { return nil }
        return ContentExperienceRoute(itemType: item.type)
    }

    func isRoutable(_ item: ContentItem) -> Bool {
        resolve(for: item) != nil
    }

    func supportsAllKnownTypes() -> Bool {
        supportedTypes == Set(ContentItemType.allCases)
    }
}
