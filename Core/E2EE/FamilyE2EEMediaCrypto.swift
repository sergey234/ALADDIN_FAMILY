import Foundation
import CryptoKit

/// E1.6 — шифрование медиа/голоса перед загрузкой на сервер (AES-GCM, ключ внутри envelope v2).
enum FamilyE2EEMediaCrypto {

    struct EncryptedBlob {
        let data: Data
        let keyBase64: String
        let sha256Hex: String
    }

    struct MediaDescriptor: Codable, Equatable {
        let url: String
        let hash: String
        let key: String
        let duration: Double?
        let mime: String?
    }

    static func encryptFile(_ plaintext: Data) throws -> EncryptedBlob {
        let key = SymmetricKey(size: .bits256)
        let sealed = try AES.GCM.seal(plaintext, using: key)
        guard let combined = sealed.combined else {
            throw FamilyE2EEError.encryptionFailed
        }
        let hash = SHA256.hash(data: combined)
        let hashHex = hash.map { String(format: "%02x", $0) }.joined()
        let keyData = key.withUnsafeBytes { Data($0) }
        return EncryptedBlob(
            data: combined,
            keyBase64: keyData.base64EncodedString(),
            sha256Hex: hashHex
        )
    }

    static func decryptFile(combined: Data, keyBase64: String, expectedHash: String?) throws -> Data {
        guard let keyData = Data(base64Encoded: keyBase64), keyData.count == 32 else {
            throw FamilyE2EEError.invalidCiphertext
        }
        if let expected = expectedHash?.lowercased(), !expected.isEmpty {
            let actual = SHA256.hash(data: combined).map { String(format: "%02x", $0) }.joined()
            guard actual == expected else {
                throw FamilyE2EEError.invalidCiphertext
            }
        }
        let key = SymmetricKey(data: keyData)
        let box = try AES.GCM.SealedBox(combined: combined)
        return try AES.GCM.open(box, using: key)
    }
}
