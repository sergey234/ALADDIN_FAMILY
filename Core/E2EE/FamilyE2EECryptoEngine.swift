import Foundation
import CryptoKit

/// AES-GCM + X25519 групповой ключ семьи (E1.4).
/// Совместим с `envelope_version=2` на сервере; LibSignalClient — через Podfile (см. docs).
enum FamilyE2EECryptoEngine {

    private static let familyKeyPrefix = "family_e2ee_symmetric_key_"
    private static let distributionPrefix = "family_e2ee_distribution_done_"

    struct InnerPayload: Codable {
        let v: Int
        let t: String
        let body: String
        let media: FamilyE2EEMediaCrypto.MediaDescriptor?
    }

    struct DistributionPlaintext: Codable {
        let v: Int
        let key: String
    }

    // MARK: - Family symmetric key

    static func loadFamilyKey(familyId: String) -> SymmetricKey? {
        let scoped = KeychainManager.e2eeFamilySymmetricKey(familyId: familyId)
        guard let data = KeychainManager.shared.loadData(scopedKey: scoped), data.count == 32 else {
            return nil
        }
        return SymmetricKey(data: data)
    }

    static func saveFamilyKey(_ key: SymmetricKey, familyId: String) {
        let raw = key.withUnsafeBytes { Data($0) }
        let scoped = KeychainManager.e2eeFamilySymmetricKey(familyId: familyId)
        KeychainManager.shared.save(raw, scopedKey: scoped)
    }

    static func generateFamilyKey() -> SymmetricKey {
        SymmetricKey(size: .bits256)
    }

    // MARK: - Encrypt / decrypt messages

    static func encrypt(plaintext: String, messageType: String, familyId: String) throws -> String {
        try encryptPayload(
            InnerPayload(v: 1, t: messageType, body: plaintext, media: nil),
            familyId: familyId
        )
    }

    static func encryptMedia(
        messageType: String,
        media: FamilyE2EEMediaCrypto.MediaDescriptor,
        familyId: String,
        caption: String = ""
    ) throws -> String {
        try encryptPayload(
            InnerPayload(v: 1, t: messageType, body: caption, media: media),
            familyId: familyId
        )
    }

    private static func encryptPayload(_ inner: InnerPayload, familyId: String) throws -> String {
        guard let sym = loadFamilyKey(familyId: familyId) else {
            throw FamilyE2EEError.familyKeyMissing
        }
        let blob = try JSONEncoder().encode(inner)
        let sealed = try AES.GCM.seal(blob, using: sym)
        guard let combined = sealed.combined else {
            throw FamilyE2EEError.encryptionFailed
        }
        return combined.base64EncodedString()
    }

    static func decrypt(ciphertextBase64: String, familyId: String) throws -> InnerPayload {
        guard let sym = loadFamilyKey(familyId: familyId) else {
            throw FamilyE2EEError.familyKeyMissing
        }
        guard let combined = Data(base64Encoded: ciphertextBase64) else {
            throw FamilyE2EEError.invalidCiphertext
        }
        let box = try AES.GCM.SealedBox(combined: combined)
        let clear = try AES.GCM.open(box, using: sym)
        return try JSONDecoder().decode(InnerPayload.self, from: clear)
    }

    // MARK: - Key distribution (ECIES-style для одного blob на всех)

    static func buildDistributionMessage(familyKey: SymmetricKey, recipientIdentityPublic: Data) throws -> String {
        let identity = FamilyE2EEDeviceIdentity.identityPrivateKey()
        let recipient = try Curve25519.KeyAgreement.PublicKey(rawRepresentation: recipientIdentityPublic)
        let shared = try identity.sharedSecretFromKeyAgreement(with: recipient)
        let sharedData = shared.withUnsafeBytes { Data($0) }
        let derived = HKDF<SHA256>.deriveKey(
            inputKeyMaterial: SymmetricKey(data: sharedData),
            salt: Data("aladdin-e2ee-dist-v1".utf8),
            info: Data("family-key".utf8),
            outputByteCount: 32
        )
        let rawKey = familyKey.withUnsafeBytes { Data($0) }
        let payload = DistributionPlaintext(v: 1, key: rawKey.base64EncodedString())
        let blob = try JSONEncoder().encode(payload)
        let sealed = try AES.GCM.seal(blob, using: derived)
        guard let combined = sealed.combined else {
            throw FamilyE2EEError.encryptionFailed
        }
        return combined.base64EncodedString()
    }

    static func parseDistributionMessage(
        _ distributionBase64: String,
        senderIdentityPublic: Data
    ) throws -> SymmetricKey {
        let identity = FamilyE2EEDeviceIdentity.identityPrivateKey()
        let sender = try Curve25519.KeyAgreement.PublicKey(rawRepresentation: senderIdentityPublic)
        let shared = try identity.sharedSecretFromKeyAgreement(with: sender)
        let sharedData = shared.withUnsafeBytes { Data($0) }
        let derived = HKDF<SHA256>.deriveKey(
            inputKeyMaterial: SymmetricKey(data: sharedData),
            salt: Data("aladdin-e2ee-dist-v1".utf8),
            info: Data("family-key".utf8),
            outputByteCount: 32
        )
        guard let combined = Data(base64Encoded: distributionBase64) else {
            throw FamilyE2EEError.invalidCiphertext
        }
        let box = try AES.GCM.SealedBox(combined: combined)
        let clear = try AES.GCM.open(box, using: derived)
        let dist = try JSONDecoder().decode(DistributionPlaintext.self, from: clear)
        guard dist.v == 1, let keyData = Data(base64Encoded: dist.key), keyData.count == 32 else {
            throw FamilyE2EEError.invalidDistribution
        }
        return SymmetricKey(data: keyData)
    }

    static func markDistributionPosted(familyId: String) {
        UserDefaults.standard.set(true, forKey: distributionPrefix + familyId)
    }

    static func hasPostedDistribution(familyId: String) -> Bool {
        UserDefaults.standard.bool(forKey: distributionPrefix + familyId)
    }
}

enum FamilyE2EEError: LocalizedError {
    case familyKeyMissing
    case encryptionFailed
    case invalidCiphertext
    case invalidDistribution
    case bootstrapFailed(String)

    var errorDescription: String? {
        switch self {
        case .familyKeyMissing: return "Family E2EE key not ready"
        case .encryptionFailed: return "E2EE encryption failed"
        case .invalidCiphertext: return "Invalid E2EE ciphertext"
        case .invalidDistribution: return "Invalid E2EE key distribution"
        case .bootstrapFailed(let msg): return msg
        }
    }
}
