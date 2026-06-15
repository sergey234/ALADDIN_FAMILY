import Foundation

/// Parses `aladdin://antifake/check` deep links opened from Share Extension or external apps.
enum AntifakeDeepLinkRouter {
    static let scheme = AntifakeShareConstants.scheme
    static let host = AntifakeShareConstants.host
    static let checkPath = AntifakeShareConstants.checkPath

    static func isAntifakeCheckDeepLink(_ url: URL) -> Bool {
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

    /// Optional `mode` query hint; payload body lives in App Group storage.
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
