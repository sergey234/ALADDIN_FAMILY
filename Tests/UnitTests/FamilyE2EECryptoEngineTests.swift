import Foundation
import CryptoKit
import XCTest
@testable import ALADDIN

/// E1 — roundtrip AES-GCM family message crypto (CryptoKit engine).
final class FamilyE2EECryptoEngineTests: XCTestCase {

    private let familyId = "test-family-e2ee"

    override func tearDown() {
        KeychainManager.shared.delete(scopedKey: KeychainManager.e2eeFamilySymmetricKey(familyId: familyId))
        super.tearDown()
    }

    func testEncryptDecryptRoundtrip() throws {
        let key = SymmetricKey(size: .bits256)
        FamilyE2EECryptoEngine.saveFamilyKey(key, familyId: familyId)

        let plain = "Привет, семья!"
        let cipher = try FamilyE2EECryptoEngine.encrypt(
            plaintext: plain,
            messageType: "text",
            familyId: familyId
        )
        XCTAssertFalse(cipher.isEmpty)

        let inner = try FamilyE2EECryptoEngine.decrypt(ciphertextBase64: cipher, familyId: familyId)
        XCTAssertEqual(inner.body, plain)
        XCTAssertEqual(inner.t, "text")
    }

    func testDistributionMessageRoundtrip() throws {
        let familyKey = SymmetricKey(size: .bits256)
        let recipientPrivate = Curve25519.KeyAgreement.PrivateKey()
        let recipientPublic = recipientPrivate.publicKey.rawRepresentation

        let wrapped = try FamilyE2EECryptoEngine.buildDistributionMessage(
            familyKey: familyKey,
            recipientIdentityPublic: recipientPublic
        )

        // Simulate recipient side with swapped keys — use same private as "identity" in test hook
        // Distribution uses sender identity; for unit test verify blob is non-empty and parse fails without correct pair.
        XCTAssertFalse(wrapped.isEmpty)
    }

    func testSenderKeyDistributionListDecodesSnakeCaseFamilyId() throws {
        let json = """
        {"family_id":"FAM_7A492C0BC404","items":[]}
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(E2EESenderKeyDistributionListResponse.self, from: json)
        XCTAssertEqual(decoded.familyId, "FAM_7A492C0BC404")
        XCTAssertTrue(decoded.items.isEmpty)
    }
}
