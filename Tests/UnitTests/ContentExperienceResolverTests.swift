import XCTest
@testable import ALADDIN

final class ContentExperienceResolverTests: XCTestCase {

    func testResolveCoversAllContentItemTypes() {
        let resolver = ContentExperienceResolver.shared
        let map: [(ContentItemType, ContentExperienceRoute)] = [
            (.game, .game),
            (.lesson, .lesson),
            (.video, .video),
            (.story, .story),
            (.song, .song),
            (.drawing, .drawing),
            (.safety, .safety),
            (.career, .career)
        ]

        for (type, expected) in map {
            let item = makeItem(type: type)
            XCTAssertEqual(resolver.resolve(for: item), expected)
            XCTAssertTrue(resolver.isRoutable(item))
        }
    }

    func testSupportsAllKnownTypesContract() {
        XCTAssertTrue(ContentExperienceResolver.shared.supportsAllKnownTypes())
    }

    private func makeItem(type: ContentItemType) -> ContentItem {
        let metadata = ContentMetadata(
            locale: "en",
            title: "Title",
            subtitle: nil,
            description: "Description",
            tags: ["safe"],
            estimatedDurationSec: 120
        )
        return ContentItem(
            id: "item-\(type.rawValue)",
            categoryId: "c1",
            type: type,
            ageBand: .school_7_12,
            version: 1,
            metadata: metadata,
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false
        )
    }
}
