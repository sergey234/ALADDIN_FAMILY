import Foundation

/// Builds mnemo academy catalog items from PlanItem275 mirror (games×20, study×30, …).
enum MnemoCatalogManifestBuilder {

    private static let mnemoCategoryIds: Set<String> = [
        ChildCategoryKey.songs,
        ChildCategoryKey.games,
        ChildCategoryKey.study,
        ChildCategoryKey.cartoons,
        ChildCategoryKey.music,
        ChildCategoryKey.video,
        ChildCategoryKey.movies,
        ChildCategoryKey.education
    ]

    /// games.05 first in Memory Games catalog.
    private static let gamesSortOrder: [String: Int] = [
        "games.05": 0,
        "games.01": 1,
        "games.02": 2,
        "games.03": 3
    ]

    static func isMnemoCategory(_ categoryId: String) -> Bool {
        mnemoCategoryIds.contains(categoryId)
    }

    static func items(for categoryId: String, ageBand: ContentAgeBand) -> [ContentItem] {
        guard mnemoCategoryIds.contains(categoryId) else { return [] }

        var lines = PlanItem275CatalogMirror.allLines.filter { $0.categoryId == categoryId }
        if categoryId == ChildCategoryKey.games {
            lines.sort { lhs, rhs in
                let lo = gamesSortOrder[lhs.itemId] ?? 100 + sortKey(from: lhs.itemId)
                let ro = gamesSortOrder[rhs.itemId] ?? 100 + sortKey(from: rhs.itemId)
                if lo != ro { return lo < ro }
                return sortKey(from: lhs.itemId) < sortKey(from: rhs.itemId)
            }
        } else {
            lines.sort { sortKey(from: $0.itemId) < sortKey(from: $1.itemId) }
        }

        return lines.enumerated().map { index, line in
            ContentItem(
                id: line.itemId,
                categoryId: categoryId,
                type: contentType(for: categoryId),
                ageBand: ageBand,
                version: 1,
                metadata: ContentMetadata(
                    locale: "ru",
                    title: MnemoCatalogTitles.titleKey(for: line.itemId),
                    subtitle: "child_mnemo_catalog_subtitle",
                    description: line.planTitle,
                    tags: ["phase2", "mnemo", "plan275", categoryId, line.itemId],
                    estimatedDurationSec: 300 + index * 30
                ),
                payloadURL: nil,
                checksumSHA256: nil,
                isOfflineAvailable: true
            )
        }
    }

    static func allMnemoItems(categories: [ContentCategory]) -> [ContentItem] {
        var result: [ContentItem] = []
        for category in categories where mnemoCategoryIds.contains(category.id) {
            result.append(contentsOf: items(for: category.id, ageBand: category.ageBand))
        }
        return result
    }

    private static func sortKey(from itemId: String) -> Int {
        guard let suffix = itemId.split(separator: ".").last,
              let num = Int(suffix) else { return Int.max }
        return num
    }

    private static func contentType(for categoryId: String) -> ContentItemType {
        switch categoryId {
        case ChildCategoryKey.games:
            return .game
        case ChildCategoryKey.study, ChildCategoryKey.education:
            return .lesson
        case ChildCategoryKey.cartoons, ChildCategoryKey.video, ChildCategoryKey.movies:
            return .video
        case ChildCategoryKey.songs, ChildCategoryKey.music:
            return .song
        default:
            return .lesson
        }
    }
}
