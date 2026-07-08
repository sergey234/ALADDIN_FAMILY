import Foundation

/// fws-h06 — deep links for 1-tap companion talk + wellness check-in widget.
enum CompanionDeepLinkRouter {
    static func isCompanionTalkDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased()
        if host == "companion" {
            return path == "/talk" || path == "talk"
        }
        return false
    }

    static func isWellnessCheckinDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased()
        if host == "wellness" {
            return path == "/checkin" || path == "checkin"
        }
        return false
    }
}
