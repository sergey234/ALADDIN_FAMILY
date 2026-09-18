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

    /// P1.5b — wind_down / explicit day-recap → Voice Notes MemoRecap (not always-on mic).
    static func isVoiceDayRecapDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased()
        if host == "voice" {
            return path == "/day-recap" || path == "day-recap" || path == "/recap" || path == "recap"
        }
        return false
    }

    /// VSL-C P1 — open Voice Notes log (`aladdin://voice/log`).
    static func isVoiceLogDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased()
        if host == "voice" {
            return path == "/log" || path == "log" || path == "/notes" || path == "notes"
        }
        return false
    }

    /// VSL-C P2 — open weekly Voice Safety digest (`aladdin://voice/weekly`).
    static func isVoiceWeeklyDeepLink(_ url: URL) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased()
        if host == "voice" {
            return path == "/weekly" || path == "weekly" || path == "/week" || path == "week"
        }
        return false
    }
}
