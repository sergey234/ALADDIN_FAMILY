import Foundation
import CryptoKit

/// Локальная крипто-идентичность устройства для Family Chat E2EE (E1.4).
/// Публичные ключи уходят на сервер; приватные — только Keychain.
enum FamilyE2EEDeviceIdentity {

    private static let signedPreKeyPrivateScoped = "family_e2ee_signed_prekey_private"
    private static let signedPreKeyIdScoped = "family_e2ee_signed_prekey_id"

    static func deviceId() -> String {
        if let existing = KeychainManager.shared.loadString(forKey: .e2eeDeviceId)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !existing.isEmpty {
            return existing
        }
        let fresh = UUID().uuidString.lowercased()
        KeychainManager.shared.save(fresh, forKey: .e2eeDeviceId)
        return fresh
    }

    static func registrationId() -> UInt32 {
        if let data = KeychainManager.shared.loadData(forKey: .e2eeRegistrationId),
           data.count == 4 {
            return data.withUnsafeBytes { $0.load(as: UInt32.self) }
        }
        let value = UInt32.random(in: 1...0x3FFF)
        var bytes = value.bigEndian
        KeychainManager.shared.save(Data(bytes: &bytes, count: 4), forKey: .e2eeRegistrationId)
        return value
    }

    static func identityPrivateKey() -> Curve25519.KeyAgreement.PrivateKey {
        if let data = KeychainManager.shared.loadData(forKey: .e2eeIdentityPrivate),
           let key = try? Curve25519.KeyAgreement.PrivateKey(rawRepresentation: data) {
            return key
        }
        let key = Curve25519.KeyAgreement.PrivateKey()
        KeychainManager.shared.save(key.rawRepresentation, forKey: .e2eeIdentityPrivate)
        return key
    }

    static func identityPublicKeyData() -> Data {
        identityPrivateKey().publicKey.rawRepresentation
    }

    static func signedPreKeyMaterial() -> (id: UInt32, publicData: Data, signature: Data, privateKey: Curve25519.Signing.PrivateKey) {
        if let privData = KeychainManager.shared.loadData(scopedKey: signedPreKeyPrivateScoped),
           let idData = KeychainManager.shared.loadData(scopedKey: signedPreKeyIdScoped),
           idData.count == 4,
           let signingKey = try? Curve25519.Signing.PrivateKey(rawRepresentation: privData) {
            let id = idData.withUnsafeBytes { $0.load(as: UInt32.self) }
            let pub = signingKey.publicKey.rawRepresentation
            let sig = try? signingKey.signature(for: pub)
            return (id, pub, sig ?? Data(), signingKey)
        }

        let signingKey = Curve25519.Signing.PrivateKey()
        let id = UInt32.random(in: 1...0xFFFFFF)
        let pub = signingKey.publicKey.rawRepresentation
        let sig = (try? signingKey.signature(for: pub)) ?? Data()
        KeychainManager.shared.save(signingKey.rawRepresentation, scopedKey: signedPreKeyPrivateScoped)
        var idBE = id.bigEndian
        KeychainManager.shared.save(Data(bytes: &idBE, count: 4), scopedKey: signedPreKeyIdScoped)
        return (id, pub, sig, signingKey)
    }

    static func makeRegisterRequest(familyId: String) -> RegisterE2EEDeviceRequest {
        let spk = signedPreKeyMaterial()
        return RegisterE2EEDeviceRequest(
            familyId: familyId,
            deviceId: deviceId(),
            registrationId: Int(registrationId()),
            identityKeyPublic: identityPublicKeyData().base64EncodedString(),
            signedPrekey: E2EESignedPreKeyIn(
                id: Int(spk.id),
                public: spk.publicData.base64EncodedString(),
                signature: spk.signature.base64EncodedString()
            ),
            oneTimePrekeys: []
        )
    }
}
