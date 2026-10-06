import Foundation

/// B2-08 / af-7-02 — App Group handoff from Share Extension to main app Antifake Hub.
/// fsl-02: also image / PDF via shared inbox file (mode `.document`, value = relative filename).
enum AntifakeShareMode: String, Codable, Equatable {
    case text
    case url
    case document
}

struct AntifakeSharePayload: Codable, Equatable {
    let mode: AntifakeShareMode
    /// Text/URL string, or relative filename under App Group inbox for `.document`.
    let value: String
    let createdAt: Date
}

enum AntifakeShareConstants {
    static let appGroupId = "group.ai.aladdin"
    static let payloadKey = "antifake_share_payload_v1"
    static let inboxFolderName = "antifake_share_inbox"
    static let maxDocumentBytes = 25 * 1024 * 1024
    static let scheme = "aladdin"
    static let host = "antifake"
    static let checkPath = "check"

    static var checkDeepLinkURL: URL {
        URL(string: "\(scheme)://\(host)/\(checkPath)")!
    }

    static let webBaseURL = "https://aladdin-ai.ru/antifake.html"

    static func webCheckURL(for payload: AntifakeSharePayload) -> URL {
        var components = URLComponents(string: webBaseURL)!
        switch payload.mode {
        case .url:
            components.queryItems = [URLQueryItem(name: "url", value: payload.value)]
        case .text:
            components.queryItems = [URLQueryItem(name: "text", value: payload.value)]
        case .document:
            // Web cannot receive binary; open Hub landing.
            components.queryItems = nil
        }
        return components.url ?? URL(string: webBaseURL)!
    }
}

enum AntifakeShareFileInbox {
    static var containerURL: URL? {
        FileManager.default.containerURL(
            forSecurityApplicationGroupIdentifier: AntifakeShareConstants.appGroupId
        )
    }

    static var inboxURL: URL? {
        guard let containerURL else { return nil }
        let url = containerURL.appendingPathComponent(
            AntifakeShareConstants.inboxFolderName,
            isDirectory: true
        )
        try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }

    /// Writes bytes into App Group inbox; returns relative filename for payload.value.
    static func store(data: Data, preferredFilename: String) throws -> String {
        guard data.count <= AntifakeShareConstants.maxDocumentBytes else {
            throw AntifakeShareInboxError.fileTooLarge
        }
        guard let inboxURL else {
            throw AntifakeShareInboxError.noAppGroup
        }
        let safeName = sanitizeFilename(preferredFilename)
        let dest = inboxURL.appendingPathComponent(safeName)
        if FileManager.default.fileExists(atPath: dest.path) {
            try FileManager.default.removeItem(at: dest)
        }
        try data.write(to: dest, options: .atomic)
        return safeName
    }

    static func fileURL(relativeName: String) -> URL? {
        guard let inboxURL else { return nil }
        let name = sanitizeFilename(relativeName)
        let url = inboxURL.appendingPathComponent(name)
        guard FileManager.default.fileExists(atPath: url.path) else { return nil }
        return url
    }

    static func loadData(relativeName: String) -> Data? {
        guard let url = fileURL(relativeName: relativeName) else { return nil }
        return try? Data(contentsOf: url)
    }

    static func remove(relativeName: String) {
        guard let url = fileURL(relativeName: relativeName) else { return }
        try? FileManager.default.removeItem(at: url)
    }

    static func clearAll() {
        guard let inboxURL,
              let items = try? FileManager.default.contentsOfDirectory(
                at: inboxURL,
                includingPropertiesForKeys: nil
              ) else { return }
        for item in items {
            try? FileManager.default.removeItem(at: item)
        }
    }

    private static func sanitizeFilename(_ raw: String) -> String {
        let base = (raw as NSString).lastPathComponent
        let trimmed = base.trimmingCharacters(in: .whitespacesAndNewlines)
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "._-"))
        let cleaned = String(trimmed.unicodeScalars.map { allowed.contains($0) ? Character($0) : "_" })
        if cleaned.isEmpty || cleaned == "." || cleaned == ".." {
            return "shared_document.bin"
        }
        return String(cleaned.prefix(120))
    }
}

enum AntifakeShareInboxError: Error {
    case fileTooLarge
    case noAppGroup
}

enum AntifakeSharePayloadStore {
    private static var defaults: UserDefaults? {
        UserDefaults(suiteName: AntifakeShareConstants.appGroupId)
    }

    static func save(_ payload: AntifakeSharePayload) {
        guard let defaults else { return }
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(payload) else { return }
        defaults.set(data, forKey: AntifakeShareConstants.payloadKey)
    }

    static func save(mode: AntifakeShareMode, value: String) {
        save(AntifakeSharePayload(mode: mode, value: value, createdAt: Date()))
    }

    /// Stores document bytes + payload pointing at relative inbox filename.
    static func saveDocument(data: Data, filename: String) throws {
        let relative = try AntifakeShareFileInbox.store(data: data, preferredFilename: filename)
        save(AntifakeSharePayload(mode: .document, value: relative, createdAt: Date()))
    }

    static func load() -> AntifakeSharePayload? {
        guard let defaults,
              let data = defaults.data(forKey: AntifakeShareConstants.payloadKey) else { return nil }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try? decoder.decode(AntifakeSharePayload.self, from: data)
    }

    /// Reads and clears the pending share payload (single-use handoff).
    /// Document inbox file is kept until Hub consumes it via `consumeDocumentFile`.
    static func consume() -> AntifakeSharePayload? {
        guard let payload = load() else { return nil }
        clearPayloadOnly()
        return payload
    }

    /// Loads document bytes for a consumed `.document` payload and deletes the inbox file.
    static func consumeDocumentFile(relativeName: String) -> (data: Data, filename: String)? {
        guard let data = AntifakeShareFileInbox.loadData(relativeName: relativeName) else {
            return nil
        }
        AntifakeShareFileInbox.remove(relativeName: relativeName)
        return (data, relativeName)
    }

    static func clear() {
        if let payload = load(), payload.mode == .document {
            AntifakeShareFileInbox.remove(relativeName: payload.value)
        }
        AntifakeShareFileInbox.clearAll()
        clearPayloadOnly()
    }

    private static func clearPayloadOnly() {
        defaults?.removeObject(forKey: AntifakeShareConstants.payloadKey)
    }
}
