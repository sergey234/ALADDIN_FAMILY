import XCTest
import CryptoKit
@testable import ALADDIN

private final class ApplyManifestTestDatabase: ContentDatabaseProtocol {
    var stored: ContentManifest?
    var saveError: Error?

    func saveManifest(_ manifest: ContentManifest) async throws {
        if let saveError { throw saveError }
        stored = manifest
    }

    func loadManifest() async -> ContentManifest? { stored }

    func saveProgress(_ progress: ContentProgress) async throws {}

    func loadProgress(contentId: String) async -> ContentProgress? { nil }

    func loadAllItems() async -> [ContentItem] { stored?.items ?? [] }
}

private final class StubPayloadDownloader: ContentPayloadDownloading {
    func downloadPayload(from url: URL) async throws -> Data { Data() }
}

@MainActor
final class ContentSyncManagerApplyTests: XCTestCase {

    private func suiteDefaults() -> UserDefaults {
        let name = "test.ContentSyncManagerApply.\(UUID().uuidString)"
        let ud = UserDefaults(suiteName: name)!
        ud.removePersistentDomain(forName: name)
        return ud
    }

    private func minimalItem(id: String = "item-1") -> ContentItem {
        let meta = ContentMetadata(
            locale: "en",
            title: "T",
            subtitle: nil,
            description: nil,
            tags: [],
            estimatedDurationSec: nil
        )
        return ContentItem(
            id: id,
            categoryId: "c1",
            type: .lesson,
            ageBand: .school_7_12,
            version: 1,
            metadata: meta,
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false
        )
    }

    private func manifest(version: Int, signature: String?) -> ContentManifest {
        let cat = ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)
        return ContentManifest(
            manifestVersion: version,
            generatedAt: Date(timeIntervalSince1970: 1_720_000_000),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "chk-\(version)",
            signature: signature,
            categories: [cat],
            items: [minimalItem()]
        )
    }

    func testApplyManifestRollbackRestoresVersionAndManifest() async throws {
        let db = ApplyManifestTestDatabase()
        let old = manifest(version: 1, signature: nil)
        db.stored = old
        db.saveError = NSError(domain: "ApplyManifestTest", code: 1, userInfo: nil)

        let ud = suiteDefaults()
        let vm = ContentVersionManager(defaults: ud)
        try vm.updateVersion(to: 1)

        let sync = ContentSyncManager(
            database: db,
            versionManager: vm,
            cacheManager: .shared,
            payloadDownloader: StubPayloadDownloader()
        )

        let fresh = manifest(version: 2, signature: nil)
        do {
            try await sync.applyManifest(fresh)
            XCTFail("expected save to throw")
        } catch {
            let ns = error as NSError
            XCTAssertEqual(ns.domain, "ApplyManifestTest")
            XCTAssertEqual(ns.code, 1)
        }

        XCTAssertEqual(vm.currentVersion, 1)
        XCTAssertEqual(db.stored?.manifestVersion, 1)
    }

    func testRequireSignatureThrowsWhenSignatureMissing() async throws {
        let db = ApplyManifestTestDatabase()
        let ud = suiteDefaults()
        let vm = ContentVersionManager(defaults: ud)

        let sync = ContentSyncManager(
            database: db,
            versionManager: vm,
            cacheManager: .shared,
            payloadDownloader: StubPayloadDownloader(),
            requireManifestSignature: true,
            manifestSigningPublicKeyBase64: "dummy"
        )

        let m = manifest(version: 3, signature: nil)
        do {
            try await sync.applyManifest(m)
            XCTFail("expected signature missing")
        } catch {
            XCTAssertEqual(error as? ContentSyncError, .manifestSignatureMissing)
        }
    }

    func testRequireSignatureThrowsWhenKeyMissing() async throws {
        let db = ApplyManifestTestDatabase()
        let ud = suiteDefaults()
        let vm = ContentVersionManager(defaults: ud)

        let sync = ContentSyncManager(
            database: db,
            versionManager: vm,
            cacheManager: .shared,
            payloadDownloader: StubPayloadDownloader(),
            requireManifestSignature: true,
            manifestSigningPublicKeyBase64: ""
        )

        let m = manifest(version: 3, signature: "abc")
        do {
            try await sync.applyManifest(m)
            XCTFail("expected signing key missing")
        } catch {
            XCTAssertEqual(error as? ContentSyncError, .manifestSigningKeyMissing)
        }
    }

    func testRequireSignatureThrowsWhenSignatureInvalid() async throws {
        let db = ApplyManifestTestDatabase()
        let ud = suiteDefaults()
        let vm = ContentVersionManager(defaults: ud)

        let keyA = P256.Signing.PrivateKey()
        let keyB = P256.Signing.PrivateKey()
        let payload = try ContentManifestSigning.canonicalSigningData(for: manifest(version: 5, signature: nil))
        let sig = try keyA.signature(for: payload)
        let sigB64 = sig.derRepresentation.base64EncodedString()
        let wrongPub = keyB.publicKey.rawRepresentation.base64EncodedString()

        let sync = ContentSyncManager(
            database: db,
            versionManager: vm,
            cacheManager: .shared,
            payloadDownloader: StubPayloadDownloader(),
            requireManifestSignature: true,
            manifestSigningPublicKeyBase64: wrongPub
        )

        let m = manifest(version: 5, signature: sigB64)
        do {
            try await sync.applyManifest(m)
            XCTFail("expected invalid signature")
        } catch {
            XCTAssertEqual(error as? ContentSyncError, .manifestSignatureInvalid)
        }
    }

    func testRequireSignatureAcceptsValidSignedManifest() async throws {
        let db = ApplyManifestTestDatabase()
        let ud = suiteDefaults()
        let vm = ContentVersionManager(defaults: ud)

        let unsigned = manifest(version: 4, signature: nil)
        let payload = try ContentManifestSigning.canonicalSigningData(for: unsigned)
        let key = P256.Signing.PrivateKey()
        let sig = try key.signature(for: payload)
        let sigB64 = sig.derRepresentation.base64EncodedString()
        let pubB64 = key.publicKey.rawRepresentation.base64EncodedString()
        let signed = manifest(version: 4, signature: sigB64)

        let sync = ContentSyncManager(
            database: db,
            versionManager: vm,
            cacheManager: .shared,
            payloadDownloader: StubPayloadDownloader(),
            requireManifestSignature: true,
            manifestSigningPublicKeyBase64: pubB64
        )

        try await sync.applyManifest(signed)
        XCTAssertEqual(vm.currentVersion, 4)
        XCTAssertEqual(db.stored?.manifestVersion, 4)
    }
}
