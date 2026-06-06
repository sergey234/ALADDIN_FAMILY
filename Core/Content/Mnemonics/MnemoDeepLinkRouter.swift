import Foundation

/// Parses `aladdin://mnemo/review?category=games` deep links for SRS review routing.
enum MnemoDeepLinkRouter {
    static let scheme = "aladdin"
    static let host = "mnemo"
    static let reviewPath = "review"

    private static let shortCategoryMap: [String: String] = [
        "songs": ChildCategoryKey.songs,
        "games": ChildCategoryKey.games,
        "study": ChildCategoryKey.study,
        "cartoons": ChildCategoryKey.cartoons,
        "music": ChildCategoryKey.music,
        "video": ChildCategoryKey.video,
        "movies": ChildCategoryKey.movies,
        "education": ChildCategoryKey.education
    ]

    static func parseReviewCategory(from url: URL) -> String? {
        guard url.scheme?.lowercased() == scheme,
              url.host?.lowercased() == host else { return nil }

        let trimmedPath = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard trimmedPath.isEmpty || trimmedPath == reviewPath else { return nil }

        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let raw = components.queryItems?.first(where: { $0.name == "category" })?.value,
              !raw.isEmpty else { return nil }

        return resolveCategory(raw)
    }

    static func reviewURL(category: String) -> URL? {
        guard let short = shortName(for: category) else { return nil }
        var components = URLComponents()
        components.scheme = scheme
        components.host = host
        components.path = "/\(reviewPath)"
        components.queryItems = [URLQueryItem(name: "category", value: short)]
        return components.url
    }

    static func resolveCategory(_ raw: String) -> String? {
        if shortCategoryMap[raw.lowercased()] != nil {
            return shortCategoryMap[raw.lowercased()]
        }
        if shortCategoryMap.values.contains(raw) {
            return raw
        }
        return nil
    }

    static func shortName(for category: String) -> String? {
        shortCategoryMap.first(where: { $0.value == category })?.key
    }

    static func ageGroup(for category: String) -> ChildInterfaceScreen.AgeGroup {
        switch category {
        case ChildCategoryKey.songs:
            return .kids
        case ChildCategoryKey.games, ChildCategoryKey.study, ChildCategoryKey.cartoons:
            return .school
        case ChildCategoryKey.music, ChildCategoryKey.video:
            return .teen
        case ChildCategoryKey.movies, ChildCategoryKey.education:
            return .youngAdult
        default:
            return .school
        }
    }
}
