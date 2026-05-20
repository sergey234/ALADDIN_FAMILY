import Foundation

/// Загрузка и расшифровка E2EE-медиа для воспроизведения в UI (E1.6).
@MainActor
final class FamilyE2EEMediaLoader: ObservableObject {
    static let shared = FamilyE2EEMediaLoader()

    private var cacheDir: URL {
        let base = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return base.appendingPathComponent("family_e2ee_media", isDirectory: true)
    }

    private init() {
        try? FileManager.default.createDirectory(at: cacheDir, withIntermediateDirectories: true)
    }

    /// Локальный file:// URL для плеера / превью.
    func resolvePlayableURL(messageId: String, media: FamilyChatEncryptedMedia) async throws -> URL {
        let cacheKey = "\(messageId)_\(media.contentHash.prefix(16))"
        let ext = fileExtension(for: media.mimeType, messageType: media.messageType)
        let local = cacheDir.appendingPathComponent("\(cacheKey).\(ext)")
        if FileManager.default.fileExists(atPath: local.path) {
            return local
        }

        guard let remote = URL(string: media.ciphertextUrl) else {
            throw FamilyE2EEError.invalidCiphertext
        }
        var request = URLRequest(url: remote)
        if let token = AppConfig.authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw FamilyE2EEError.encryptionFailed
        }

        let clear = try FamilyE2EEMediaCrypto.decryptFile(
            combined: data,
            keyBase64: media.keyBase64,
            expectedHash: media.contentHash
        )
        try clear.write(to: local, options: .atomic)
        return local
    }

    private func fileExtension(for mime: String?, messageType: String) -> String {
        let m = (mime ?? "").lowercased()
        if m.contains("jpeg") || m.contains("jpg") { return "jpg" }
        if m.contains("png") { return "png" }
        if m.contains("mp4") { return "mp4" }
        if m.contains("m4a") || m.contains("audio") { return "m4a" }
        switch messageType {
        case "image": return "jpg"
        case "video": return "mp4"
        case "voice", "audio": return "m4a"
        default: return "bin"
        }
    }
}

/// Метаданные E2EE-медиа из расшифрованного envelope.
struct FamilyChatEncryptedMedia: Equatable {
    let ciphertextUrl: String
    let contentHash: String
    let keyBase64: String
    let duration: Double?
    let mimeType: String?
    let messageType: String
}
