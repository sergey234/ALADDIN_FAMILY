import XCTest
import CryptoKit
@testable import ALADDIN

private final class StubPayloadDownloader: ContentPayloadDownloading {
    let data: Data
    init(data: Data) { self.data = data }
    func downloadPayload(from url: URL) async throws -> Data { data }
}

final class ContentManifestPayloadHydrationTests: XCTestCase {

    func testHydrateSetsOfflineWhenChecksumMatches() async throws {
        let body = Data("hello-payload".utf8)
        let digest = SHA256.hash(data: body)
        let hex = digest.map { String(format: "%02x", $0) }.joined()

        let meta = ContentMetadata(
            locale: "en",
            title: "Title",
            subtitle: nil,
            description: nil,
            tags: [],
            estimatedDurationSec: nil
        )
        let cat = ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)
        let item = ContentItem(
            id: "item-offline-test",
            categoryId: "c1",
            type: .lesson,
            ageBand: .school_7_12,
            version: 1,
            metadata: meta,
            payloadURL: URL(string: "https://example.invalid/payload.bin")!,
            checksumSHA256: hex,
            isOfflineAvailable: false
        )
        let manifest = ContentManifest(
            manifestVersion: 2,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "top-level",
            signature: nil,
            categories: [cat],
            items: [item]
        )

        let out = await ContentManifestPayloadHydration.hydrate(
            manifest: manifest,
            downloader: StubPayloadDownloader(data: body),
            validator: .shared
        )

        XCTAssertEqual(out.items.count, 1)
        XCTAssertTrue(out.items[0].isOfflineAvailable)

        let root = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            .appendingPathComponent("ContentPayloads", isDirectory: true)
            .appendingPathComponent("item-offline-test", isDirectory: true)
            .appendingPathComponent("payload.bin", isDirectory: false)
        XCTAssertTrue(FileManager.default.fileExists(atPath: root.path))
        try? FileManager.default.removeItem(at: root.deletingLastPathComponent())
    }

    func testHydrateKeepsOfflineFalseWhenChecksumMismatch() async {
        let body = Data("a".utf8)
        let meta = ContentMetadata(
            locale: "en",
            title: "Title",
            subtitle: nil,
            description: nil,
            tags: [],
            estimatedDurationSec: nil
        )
        let cat = ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)
        let item = ContentItem(
            id: "item-bad-hash",
            categoryId: "c1",
            type: .lesson,
            ageBand: .school_7_12,
            version: 1,
            metadata: meta,
            payloadURL: URL(string: "https://example.invalid/payload.bin")!,
            checksumSHA256: "deadbeef",
            isOfflineAvailable: false
        )
        let manifest = ContentManifest(
            manifestVersion: 3,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "top-level",
            signature: nil,
            categories: [cat],
            items: [item]
        )

        let out = await ContentManifestPayloadHydration.hydrate(
            manifest: manifest,
            downloader: StubPayloadDownloader(data: body),
            validator: .shared
        )

        XCTAssertFalse(out.items[0].isOfflineAvailable)
    }
}
