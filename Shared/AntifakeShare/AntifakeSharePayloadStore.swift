import Foundation

/// B2-08 / af-7-02 — App Group handoff from Share Extension to main app Antifake Hub.
enum AntifakeShareMode: String, Codable, Equatable {
    case text
    case url
}

struct AntifakeSharePayload: Codable, Equatable {
    let mode: AntifakeShareMode
    let value: String
    let createdAt: Date
}

enum AntifakeShareConstants {
    static let appGroupId = "group.ai.aladdin"
    static let payloadKey = "antifake_share_payload_v1"
    static let scheme = "aladdin"
    static let host = "antifake"
    static let checkPath = "check"

    static var checkDeepLinkURL: URL {
        URL(string: "\(scheme)://\(host)/\(checkPath)")!
    }

    static let webBaseURL = "https://aladdin-ai.ru/antifake.html"

    static func webCheckURL(for payload: AntifakeSharePayload) -> URL {
        var components = URLComponents(string: webBaseURL)!
        let name = payload.mode == .url ? "url" : "text"
        components.queryItems = [URLQueryItem(name: name, value: payload.value)]
        return components.url ?? URL(string: webBaseURL)!
    }
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

    static func load() -> AntifakeSharePayload? {
        guard let defaults,
              let data = defaults.data(forKey: AntifakeShareConstants.payloadKey) else { return nil }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try? decoder.decode(AntifakeSharePayload.self, from: data)
    }

    /// Reads and clears the pending share payload (single-use handoff).
    static func consume() -> AntifakeSharePayload? {
        guard let payload = load() else { return nil }
        clear()
        return payload
    }

    static func clear() {
        defaults?.removeObject(forKey: AntifakeShareConstants.payloadKey)
    }
}
