import Foundation

/// Parses `aladdin://antifake/check` and `https://aladdin-ai.ru/antifake*` universal links.
enum AntifakeDeepLinkRouter {
    static let scheme = AntifakeShareConstants.scheme
    static let host = AntifakeShareConstants.host
    static let checkPath = AntifakeShareConstants.checkPath
    static let universalHosts: Set<String> = ["aladdin-ai.ru", "www.aladdin-ai.ru"]

    static func isUniversalAntifakeLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "https",
              let host = url.host?.lowercased(),
              universalHosts.contains(host) else { return false }
        let path = url.path.lowercased()
        return path == "/antifake.html"
            || path == "/antifake"
            || path.hasPrefix("/antifake/")
    }

    static func isAntifakeCheckDeepLink(_ url: URL) -> Bool {
        if isUniversalAntifakeLink(url) { return true }
        guard url.scheme?.lowercased() == scheme,
              url.host?.lowercased() == host else { return false }

        let trimmedPath = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return trimmedPath.isEmpty || trimmedPath == checkPath || trimmedPath == "call-check"
    }

    static func isPostCallCheckDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == scheme,
              url.host?.lowercased() == host else { return false }
        let trimmedPath = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return trimmedPath == "call-check"
    }

    static func isFamilyAlertDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == scheme,
              url.host?.lowercased() == host else { return false }
        let trimmedPath = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return trimmedPath == "family-alert"
    }

    static func parseJobIdHint(from url: URL) -> String? {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let raw = components.queryItems?.first(where: { $0.name == "job_id" })?.value else {
            return nil
        }
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }

    static func checkURL(mode: AntifakeShareMode? = nil) -> URL {
        var components = URLComponents()
        components.scheme = scheme
        components.host = host
        components.path = "/\(checkPath)"
        if let mode {
            components.queryItems = [URLQueryItem(name: "mode", value: mode.rawValue)]
        }
        return components.url ?? AntifakeShareConstants.checkDeepLinkURL
    }

    /// Web prefill from `?text=` or `?url=` (C-08).
    static func parseWebPrefill(from url: URL) -> AntifakeSharePayload? {
        guard isUniversalAntifakeLink(url) || isAntifakeCheckDeepLink(url),
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            return nil
        }
        if let raw = components.queryItems?.first(where: { $0.name == "text" })?.value {
            let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                return AntifakeSharePayload(mode: .text, value: trimmed, createdAt: Date())
            }
        }
        if let raw = components.queryItems?.first(where: { $0.name == "url" })?.value {
            let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                return AntifakeSharePayload(mode: .url, value: trimmed, createdAt: Date())
            }
        }
        return nil
    }

    /// C-04: shared verdict link `?verdict=likely_fake&confidence=0.85` (no raw content).
    static func parseSharedVerdict(from url: URL) -> (verdict: String, confidence: Double?)? {
        guard isUniversalAntifakeLink(url),
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let verdict = components.queryItems?.first(where: { $0.name == "verdict" })?.value,
              !verdict.isEmpty else { return nil }
        let confRaw = components.queryItems?.first(where: { $0.name == "confidence" })?.value
        let confidence = confRaw.flatMap { Double($0) }
        return (verdict, confidence)
    }

    static func parseModeHint(from url: URL) -> AntifakeShareMode? {
        guard isAntifakeCheckDeepLink(url),
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let raw = components.queryItems?.first(where: { $0.name == "mode" })?.value else {
            return nil
        }
        return AntifakeShareMode(rawValue: raw)
    }

    /// E-07: optional caller hint from deep link query (iOS cannot expose number from CallKit).
    static func parseCallerIdHint(from url: URL) -> String? {
        guard isPostCallCheckDeepLink(url),
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let raw = components.queryItems?.first(where: { $0.name == "caller_id" })?.value else {
            return nil
        }
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }
}
