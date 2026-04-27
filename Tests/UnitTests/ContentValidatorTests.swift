import XCTest
import CryptoKit
@testable import ALADDIN

final class ContentValidatorTests: XCTestCase {

    func testVerifySignatureAcceptsDerAndRawSignatures() throws {
        let validator = ContentValidator.shared
        let payload = Data("canonical-manifest-payload".utf8)
        let privateKey = P256.Signing.PrivateKey()
        let signature = try privateKey.signature(for: payload)
        let publicKeyB64 = privateKey.publicKey.rawRepresentation.base64EncodedString()

        let derB64 = signature.derRepresentation.base64EncodedString()
        XCTAssertTrue(
            validator.verifySignature(payload: payload, signatureBase64: derB64, publicKeyBase64: publicKeyB64),
            "DER envelope should verify"
        )

        let rawB64 = signature.rawRepresentation.base64EncodedString()
        XCTAssertTrue(
            validator.verifySignature(payload: payload, signatureBase64: rawB64, publicKeyBase64: publicKeyB64),
            "Raw 64-byte P-256 signature should verify"
        )
    }

    func testVerifySignatureRejectsWrongKey() throws {
        let validator = ContentValidator.shared
        let payload = Data("manifest".utf8)
        let keyA = P256.Signing.PrivateKey()
        let keyB = P256.Signing.PrivateKey()
        let signature = try keyA.signature(for: payload)
        let derB64 = signature.derRepresentation.base64EncodedString()
        let wrongPubB64 = keyB.publicKey.rawRepresentation.base64EncodedString()

        XCTAssertFalse(
            validator.verifySignature(payload: payload, signatureBase64: derB64, publicKeyBase64: wrongPubB64)
        )
    }

    func testVerifySignatureRejectsTamperedPayload() throws {
        let validator = ContentValidator.shared
        let payload = Data("original".utf8)
        let privateKey = P256.Signing.PrivateKey()
        let signature = try privateKey.signature(for: payload)
        let publicKeyB64 = privateKey.publicKey.rawRepresentation.base64EncodedString()
        let derB64 = signature.derRepresentation.base64EncodedString()

        let tampered = Data("tampered!".utf8)
        XCTAssertFalse(
            validator.verifySignature(payload: tampered, signatureBase64: derB64, publicKeyBase64: publicKeyB64)
        )
    }

    func testVerifySignatureRejectsEmptyOrInvalidBase64() {
        let validator = ContentValidator.shared
        let payload = Data("x".utf8)
        XCTAssertFalse(validator.verifySignature(payload: payload, signatureBase64: "", publicKeyBase64: "abc"))
        XCTAssertFalse(validator.verifySignature(payload: Data(), signatureBase64: "YQ==", publicKeyBase64: "YQ=="))
    }

    func testValidateManifestRejectsEmptyItems() {
        let validator = ContentValidator.shared
        let empty = ContentManifest(
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "a",
            signature: nil,
            categories: [],
            items: []
        )
        XCTAssertFalse(validator.validateManifest(empty))
    }

    func testValidateManifestAcceptsRoutableItems() {
        let validator = ContentValidator.shared
        let item = makeItem(id: "lesson-1", categoryId: "c1", type: .lesson)
        let item2 = makeItem(id: "lesson-2", categoryId: "c1", type: .lesson)
        let item3 = makeItem(id: "lesson-3", categoryId: "c1", type: .lesson)
        let manifest = ContentManifest(
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "a",
            signature: nil,
            categories: [ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)],
            items: [item, item2, item3]
        )
        XCTAssertTrue(validator.validateManifest(manifest))
    }

    func testValidateManifestRejectsMissingCategoryMapping() {
        let validator = ContentValidator.shared
        let manifest = ContentManifest(
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "a",
            signature: nil,
            categories: [ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)],
            items: [
                makeItem(id: "x1", categoryId: "missing", type: .lesson),
                makeItem(id: "x2", categoryId: "missing", type: .lesson),
                makeItem(id: "x3", categoryId: "missing", type: .lesson)
            ]
        )
        XCTAssertFalse(validator.validateManifest(manifest))
    }

    func testValidateManifestRejectsInsufficientCategoryDensity() {
        let validator = ContentValidator.shared
        let manifest = ContentManifest(
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "a",
            signature: nil,
            categories: [ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)],
            items: [makeItem(id: "x1", categoryId: "c1", type: .lesson)]
        )
        XCTAssertFalse(validator.validateManifest(manifest))
    }

    func testValidateManifestRejectsInvalidLearningOutcomeContract() {
        let validator = ContentValidator.shared
        let invalidContract = ContentLearningOutcomeContract(
            learningObjective: "  ",
            targetAgeWindow: "7-9",
            difficultyLevel: .l2,
            successCriteria: "Child solves at least 3 tasks independently",
            assessmentType: .quiz,
            estimatedCognitiveLoad: .medium
        )
        let item = ContentItem(
            id: "lesson-1",
            categoryId: "c1",
            type: .lesson,
            ageBand: .school_7_12,
            version: 1,
            metadata: ContentMetadata(
                locale: "en",
                title: "Lesson 1",
                subtitle: nil,
                description: "Desc",
                tags: [],
                estimatedDurationSec: 120
            ),
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false,
            learningOutcomeContract: invalidContract
        )
        let manifest = ContentManifest(
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "a",
            signature: nil,
            categories: [ContentCategory(id: "c1", titleKey: "k", icon: "i", ageBand: .school_7_12)],
            items: [item, makeItem(id: "lesson-2", categoryId: "c1", type: .lesson), makeItem(id: "lesson-3", categoryId: "c1", type: .lesson)]
        )
        XCTAssertFalse(validator.validateManifest(manifest))
    }

    private func makeItem(id: String, categoryId: String, type: ContentItemType) -> ContentItem {
        ContentItem(
            id: id,
            categoryId: categoryId,
            type: type,
            ageBand: .school_7_12,
            version: 1,
            metadata: ContentMetadata(
                locale: "en",
                title: "Lesson \(id)",
                subtitle: nil,
                description: "Desc",
                tags: [],
                estimatedDurationSec: 120
            ),
            payloadURL: nil,
            checksumSHA256: nil,
            isOfflineAvailable: false
        )
    }
}
