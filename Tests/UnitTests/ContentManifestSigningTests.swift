import XCTest
import CryptoKit
@testable import ALADDIN

@MainActor
final class ContentManifestSigningTests: XCTestCase {

    func testCanonicalSigningDataIsStableAcrossCalls() throws {
        let manifest = Self.sampleManifest(signature: nil)
        let a = try ContentManifestSigning.canonicalSigningData(for: manifest)
        let b = try ContentManifestSigning.canonicalSigningData(for: manifest)
        XCTAssertEqual(a, b)
    }

    func testSignedCanonicalPayloadVerifiesWithP256() throws {
        let manifest = Self.sampleManifest(signature: nil)
        let payload = try ContentManifestSigning.canonicalSigningData(for: manifest)

        let privateKey = P256.Signing.PrivateKey()
        let signature = try privateKey.signature(for: payload)
        let publicB64 = privateKey.publicKey.rawRepresentation.base64EncodedString()
        let sigB64 = signature.derRepresentation.base64EncodedString()

        let signed = Self.sampleManifest(signature: sigB64)
        let roundTripPayload = try ContentManifestSigning.canonicalSigningData(for: signed)
        XCTAssertEqual(roundTripPayload, payload)

        XCTAssertTrue(
            ContentValidator.shared.verifySignature(
                payload: payload,
                signatureBase64: sigB64,
                publicKeyBase64: publicB64
            )
        )
    }

    private static func sampleManifest(signature: String?) -> ContentManifest {
        let meta = ContentMetadata(
            locale: "en",
            title: "T",
            subtitle: nil,
            description: nil,
            tags: [],
            estimatedDurationSec: nil
        )
        let cat = ContentCategory(id: "c-z", titleKey: "k", icon: "i", ageBand: .school_7_12)
        let cat2 = ContentCategory(id: "c-a", titleKey: "k2", icon: "i", ageBand: .kids_1_6)
        let item = ContentItem(
            id: "i-b",
            categoryId: "c-a",
            type: .lesson,
            ageBand: .school_7_12,
            version: 1,
            metadata: meta,
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false
        )
        let item2 = ContentItem(
            id: "i-a",
            categoryId: "c-z",
            type: .game,
            ageBand: .teen_13_17,
            version: 2,
            metadata: meta,
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false
        )
        return ContentManifest(
            manifestVersion: 7,
            generatedAt: Date(timeIntervalSince1970: 1_700_000_000),
            minSupportedAppVersion: "1.2.3",
            checksumSHA256: "manifest-checksum",
            signature: signature,
            categories: [cat, cat2],
            items: [item, item2]
        )
    }
}
