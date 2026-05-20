import Foundation
import CryptoKit

/// Facade Family Chat E2EE (E1.4): bootstrap ключей, encrypt/decrypt, v2 send.
@MainActor
final class FamilyE2EEManager: ObservableObject {
    static let shared = FamilyE2EEManager()

    @Published private(set) var isReady = false
    @Published private(set) var lastError: String?

    private let api = APIService.shared
    private var bootstrappingFamilyId: String?

    private init() {}

    var deviceId: String { FamilyE2EEDeviceIdentity.deviceId() }

    /// Вызывать при входе в Family Chat (`familyId` из локального контекста).
    func bootstrap(familyId: String) async {
        let fid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty else {
            isReady = false
            lastError = "family_id missing"
            return
        }
        if bootstrappingFamilyId == fid { return }
        bootstrappingFamilyId = fid
        defer { bootstrappingFamilyId = nil }

        do {
            try await registerDeviceIfNeeded(familyId: fid)
            try await ingestRemoteDistributions(familyId: fid)
            try await ensureLocalFamilyKey(familyId: fid)
            isReady = FamilyE2EECryptoEngine.loadFamilyKey(familyId: fid) != nil
            lastError = isReady ? nil : "E2EE key not established"
        } catch {
            if let ne = error as? NetworkError, case .internalServerError = ne {
                FamilyE2EEDeviceIdentity.resetLocalIdentity()
                do {
                    try await registerDeviceIfNeeded(familyId: fid)
                    try await ingestRemoteDistributions(familyId: fid)
                    try await ensureLocalFamilyKey(familyId: fid)
                    isReady = FamilyE2EECryptoEngine.loadFamilyKey(familyId: fid) != nil
                    lastError = isReady ? nil : "E2EE key not established"
                    if isReady { return }
                } catch {
                    // fall through to user-visible error
                }
            }
            isReady = false
            lastError = error.localizedDescription
            print("❌ FamilyE2EEManager.bootstrap: \(error)")
        }
    }

    func encryptOutgoing(plaintext: String, messageType: String, familyId: String) throws -> (ciphertext: String, senderDeviceId: String) {
        let cipher = try FamilyE2EECryptoEngine.encrypt(
            plaintext: plaintext,
            messageType: messageType,
            familyId: familyId
        )
        return (cipher, deviceId)
    }

    /// E1.6 — ciphertext envelope с дескриптором зашифрованного медиа-blob на сервере.
    func encryptOutgoingMedia(
        familyId: String,
        messageType: String,
        ciphertextUrl: String,
        contentHash: String,
        keyBase64: String,
        duration: Double? = nil,
        mimeType: String? = nil
    ) throws -> (ciphertext: String, senderDeviceId: String) {
        let descriptor = FamilyE2EEMediaCrypto.MediaDescriptor(
            url: ciphertextUrl,
            hash: contentHash,
            key: keyBase64,
            duration: duration,
            mime: mimeType
        )
        let cipher = try FamilyE2EECryptoEngine.encryptMedia(
            messageType: messageType,
            media: descriptor,
            familyId: familyId
        )
        return (cipher, deviceId)
    }

    static func encryptedMedia(from response: FamilyChatMessageResponse, familyId: String) -> FamilyChatEncryptedMedia? {
        let env = response.envelopeVersion ?? 1
        guard env == 2,
              let b64 = response.ciphertext?.trimmingCharacters(in: .whitespacesAndNewlines),
              !b64.isEmpty else { return nil }
        guard let inner = try? FamilyE2EECryptoEngine.decrypt(ciphertextBase64: b64, familyId: familyId),
              let m = inner.media else { return nil }
        return FamilyChatEncryptedMedia(
            ciphertextUrl: m.url,
            contentHash: m.hash,
            keyBase64: m.key,
            duration: m.duration,
            mimeType: m.mime,
            messageType: inner.t
        )
    }

    func decryptIncoming(_ response: FamilyChatMessageResponse, familyId: String) -> FamilyChatMessageResponse {
        let env = response.envelopeVersion ?? 1
        guard env == 2, let b64 = response.ciphertext?.trimmingCharacters(in: .whitespacesAndNewlines), !b64.isEmpty else {
            return response
        }
        do {
            let inner = try FamilyE2EECryptoEngine.decrypt(ciphertextBase64: b64, familyId: familyId)
            return FamilyChatMessageResponse(
                id: response.id,
                sender: response.sender,
                text: inner.body,
                timestamp: response.timestamp,
                isCurrentUser: response.isCurrentUser,
                messageType: inner.t,
                voiceUrl: response.voiceUrl,
                voiceDuration: response.voiceDuration,
                mediaUrl: response.mediaUrl,
                mediaThumbnailUrl: response.mediaThumbnailUrl,
                mediaType: response.mediaType,
                replyToMessageId: response.replyToMessageId,
                reactions: response.reactions,
                readStatus: response.readStatus,
                readAt: response.readAt,
                editedAt: response.editedAt,
                envelopeVersion: response.envelopeVersion,
                senderDeviceId: response.senderDeviceId,
                ciphertext: response.ciphertext,
                ciphertextContentType: response.ciphertextContentType,
                isLegacyPlaintext: false
            )
        } catch {
            print("⚠️ FamilyE2EEManager.decrypt: \(error)")
            return FamilyChatMessageResponse(
                id: response.id,
                sender: response.sender,
                text: nil,
                timestamp: response.timestamp,
                isCurrentUser: response.isCurrentUser,
                messageType: response.messageType ?? "text",
                voiceUrl: nil,
                voiceDuration: nil,
                mediaUrl: nil,
                mediaThumbnailUrl: nil,
                mediaType: nil,
                replyToMessageId: response.replyToMessageId,
                reactions: response.reactions,
                readStatus: response.readStatus,
                readAt: response.readAt,
                editedAt: response.editedAt,
                envelopeVersion: env,
                senderDeviceId: response.senderDeviceId,
                ciphertext: response.ciphertext,
                ciphertextContentType: response.ciphertextContentType,
                isLegacyPlaintext: false
            )
        }
    }

    // MARK: - Private

    private func registerDeviceIfNeeded(familyId: String) async throws {
        let request = FamilyE2EEDeviceIdentity.makeRegisterRequest(familyId: familyId)
        try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
            api.registerFamilyE2EEDevice(request: request) { result in
                switch result {
                case .success: cont.resume()
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }
    }

    private func ingestRemoteDistributions(familyId: String) async throws {
        let items = try await withCheckedThrowingContinuation { (cont: CheckedContinuation<[E2EESenderKeyDistributionItem], Error>) in
            api.fetchFamilyE2EESenderKeys(familyId: familyId) { result in
                switch result {
                case .success(let list): cont.resume(returning: list.items)
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }

        let devices = try await fetchDevices(familyId: familyId)
        let byDevice = Dictionary(uniqueKeysWithValues: devices.map { ($0.deviceId, $0) })

        var latestKey: SymmetricKey?
        for item in items.sorted(by: { $0.createdAt < $1.createdAt }) {
            guard item.senderDeviceId != deviceId,
                  let sender = byDevice[item.senderDeviceId],
                  let pub = Data(base64Encoded: sender.identityKeyPublic) else { continue }
            if let sym = try? FamilyE2EECryptoEngine.parseDistributionMessage(
                item.distributionMessage,
                senderIdentityPublic: pub
            ) {
                latestKey = sym
            }
        }
        if let sym = latestKey {
            FamilyE2EECryptoEngine.saveFamilyKey(sym, familyId: familyId)
            isReady = true
        }
    }

    private func ensureLocalFamilyKey(familyId: String) async throws {
        if FamilyE2EECryptoEngine.loadFamilyKey(familyId: familyId) != nil {
            isReady = true
            try await distributeKeyToMissingDevices(familyId: familyId)
            return
        }

        let devices = try await fetchDevices(familyId: familyId)
        let others = devices.filter { $0.deviceId != deviceId }

        if !others.isEmpty {
            try await Task.sleep(nanoseconds: 400_000_000)
            try await ingestRemoteDistributions(familyId: familyId)
            if FamilyE2EECryptoEngine.loadFamilyKey(familyId: familyId) != nil {
                isReady = true
                return
            }
            throw FamilyE2EEError.bootstrapFailed(
                "E2EE key not available yet — open Family Chat on another family device first"
            )
        }

        let sym = FamilyE2EECryptoEngine.generateFamilyKey()
        FamilyE2EECryptoEngine.saveFamilyKey(sym, familyId: familyId)
        try await distributeKeyToMissingDevices(familyId: familyId, familyKey: sym)
        isReady = true
    }

    /// Re-share family key with devices that joined after initial bootstrap.
    private func distributeKeyToMissingDevices(familyId: String, familyKey: SymmetricKey? = nil) async throws {
        guard let sym = familyKey ?? FamilyE2EECryptoEngine.loadFamilyKey(familyId: familyId) else { return }
        let devices = try await fetchDevices(familyId: familyId)
        let myId = deviceId
        for remote in devices where remote.deviceId != myId {
            guard let pub = Data(base64Encoded: remote.identityKeyPublic) else { continue }
            let dist = try FamilyE2EECryptoEngine.buildDistributionMessage(
                familyKey: sym,
                recipientIdentityPublic: pub
            )
            try await postDistribution(familyId: familyId, distributionMessage: dist)
        }
        FamilyE2EECryptoEngine.markDistributionPosted(familyId: familyId)
    }

    /// E1.7 — revoke this device on logout / lost phone.
    func revokeCurrentDevice(familyId: String) async {
        let fid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty else { return }
        let body = RevokeE2EEDeviceRequest(familyId: fid, deviceId: deviceId)
        _ = try? await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
            api.revokeFamilyE2EEDevice(request: body) { result in
                switch result {
                case .success: cont.resume()
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }
    }

    private func fetchDevices(familyId: String) async throws -> [E2EEDeviceListItem] {
        try await withCheckedThrowingContinuation { (cont: CheckedContinuation<[E2EEDeviceListItem], Error>) in
            api.fetchFamilyE2EEDevices(familyId: familyId) { result in
                switch result {
                case .success(let resp): cont.resume(returning: resp.devices)
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }
    }

    private func postDistribution(familyId: String, distributionMessage: String) async throws {
        let body = DistributeE2EESenderKeyRequest(
            familyId: familyId,
            senderDeviceId: deviceId,
            distributionMessage: distributionMessage
        )
        try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
            api.distributeFamilyE2EESenderKey(request: body) { result in
                switch result {
                case .success: cont.resume()
                case .failure(let err): cont.resume(throwing: err)
                }
            }
        }
    }
}
