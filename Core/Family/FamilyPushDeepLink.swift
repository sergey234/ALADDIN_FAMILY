import Foundation

/// R10 — family push → map / member sheet (never silent-drop to SimpleHome).
enum FamilyPushDeepLink {
    static let navigateToFamilyMapName = Notification.Name("NavigateToFamilyMap")
    static let pendingMemberIdKey = "aladdin.family_push.pending_member_id"
    static let pendingDisplayNameKey = "aladdin.family_push.pending_display_name"
    static let pendingFocusKey = "aladdin.family_push.pending_focus"
    static let pendingOpenMapKey = "aladdin.family_push.pending_open_map"

    enum Focus: String {
        case sos
        case imOk = "im_ok"
        case battery
        case location
        case trips
        case habits
        case limits
        case map
    }

    /// `aladdin://family/map?member=&focus=`
    static func mapURL(memberId: String?, focus: Focus) -> String {
        var items: [URLQueryItem] = [
            URLQueryItem(name: "focus", value: focus.rawValue)
        ]
        if let memberId, !memberId.isEmpty {
            items.append(URLQueryItem(name: "member", value: memberId))
        }
        var components = URLComponents()
        components.scheme = "aladdin"
        components.host = "family"
        components.path = "/map"
        components.queryItems = items
        return components.url?.absoluteString ?? "aladdin://family/map?focus=\(focus.rawValue)"
    }

    static func enqueue(
        memberId: String? = nil,
        displayName: String? = nil,
        focus: Focus,
        openMap: Bool = true
    ) {
        let defaults = UserDefaults.standard
        if let memberId, !memberId.isEmpty {
            defaults.set(memberId, forKey: pendingMemberIdKey)
        }
        if let displayName, !displayName.isEmpty {
            defaults.set(displayName, forKey: pendingDisplayNameKey)
        }
        defaults.set(focus.rawValue, forKey: pendingFocusKey)
        defaults.set(openMap, forKey: pendingOpenMapKey)
    }

    @discardableResult
    static func enqueueFromUserInfo(_ userInfo: [AnyHashable: Any]) -> Bool {
        let type = ((userInfo["type"] as? String) ?? "").lowercased()
        let memberId = (userInfo["member_id"] as? String)
            ?? (userInfo["memberId"] as? String)
        let displayName = (userInfo["display_name"] as? String)
            ?? (userInfo["displayName"] as? String)

        if let deepLink = userInfo["deepLink"] as? String,
           let url = URL(string: deepLink),
           apply(url: url, memberIdFallback: memberId, displayNameFallback: displayName) {
            return true
        }

        switch type {
        case "family_urgent_signal", "need_help", "family_need_help", "urgent_signal":
            enqueue(memberId: memberId, displayName: displayName, focus: .sos)
            postOpenMap()
            return true
        case "im_ok", "im_ok_signal", "family_im_ok", "im_ok_sent":
            enqueue(memberId: memberId, displayName: displayName, focus: .imOk)
            postOpenMap()
            return true
        case "battery_critical":
            enqueue(memberId: memberId, displayName: displayName, focus: .battery)
            postOpenMap()
            return true
        case "geofence", "geofence_no_show", "family_geofence":
            enqueue(memberId: memberId, displayName: displayName, focus: .location)
            postOpenMap()
            return true
        case "family_shield_week_digest", "trip_week", "trips":
            enqueue(memberId: memberId, displayName: displayName, focus: .trips)
            postOpenMap()
            return true
        case "family_habit_reminder", "family_habit_due_ping":
            enqueue(memberId: memberId, displayName: displayName, focus: .habits, openMap: false)
            NotificationCenter.default.post(name: NSNotification.Name("NavigateToFamily"), object: nil)
            return true
        case "shield_ask_parent":
            enqueue(memberId: memberId, displayName: displayName, focus: .limits, openMap: false)
            NotificationCenter.default.post(name: NSNotification.Name("NavigateToFamily"), object: nil)
            return true
        case "family_event":
            enqueue(memberId: memberId, displayName: displayName, focus: .map)
            postOpenMap()
            return true
        case "need_help_sent":
            // Local ack on sender device — stay put / family map without SOS chrome.
            enqueue(memberId: memberId, displayName: displayName, focus: .map)
            postOpenMap()
            return true
        default:
            return false
        }
    }

    @discardableResult
    static func apply(
        url: URL,
        memberIdFallback: String? = nil,
        displayNameFallback: String? = nil
    ) -> Bool {
        guard url.scheme?.lowercased() == "aladdin" else { return false }
        let host = (url.host ?? "").lowercased()
        guard host == "family" else { return false }

        let path = url.path.lowercased().trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        let parts = path.split(separator: "/").map(String.init)
        let first = parts.first ?? ""

        let query = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems ?? []
        let memberQ = query.first(where: { $0.name.lowercased() == "member" })?.value
        let focusQ = query.first(where: { $0.name.lowercased() == "focus" })?.value
        let memberId = memberQ ?? memberIdFallback
        let displayName = displayNameFallback

        switch first {
        case "", "map":
            let focus = Focus(rawValue: focusQ ?? Focus.map.rawValue) ?? .map
            enqueue(memberId: memberId, displayName: displayName, focus: focus)
            postOpenMap()
            return true
        case "location":
            enqueue(memberId: memberId, displayName: displayName, focus: .location)
            postOpenMap()
            return true
        case "limits":
            enqueue(memberId: memberId, displayName: displayName, focus: .limits, openMap: false)
            NotificationCenter.default.post(name: NSNotification.Name("NavigateToFamily"), object: nil)
            return true
        case "habits", "challenges":
            enqueue(memberId: memberId, displayName: displayName, focus: .habits, openMap: false)
            NotificationCenter.default.post(name: NSNotification.Name("NavigateToFamily"), object: nil)
            return true
        case "invite":
            NotificationCenter.default.post(name: NSNotification.Name("NavigateToFamily"), object: nil)
            return true
        default:
            enqueue(memberId: memberId, displayName: displayName, focus: .map)
            postOpenMap()
            return true
        }
    }

    static func postOpenMap() {
        NotificationCenter.default.post(name: navigateToFamilyMapName, object: nil)
    }

    /// Consume pending member for sheet focus. Clears member/name; keeps focus until map dismiss if needed.
    static func consumePendingMember() -> (id: String, name: String, focus: Focus)? {
        let defaults = UserDefaults.standard
        let id = (defaults.string(forKey: pendingMemberIdKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let name = (defaults.string(forKey: pendingDisplayNameKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let focusRaw = defaults.string(forKey: pendingFocusKey) ?? Focus.map.rawValue
        let focus = Focus(rawValue: focusRaw) ?? .map
        guard defaults.bool(forKey: pendingOpenMapKey) || !id.isEmpty || focus == .sos else {
            return nil
        }
        defaults.set(false, forKey: pendingOpenMapKey)
        defaults.removeObject(forKey: pendingMemberIdKey)
        defaults.removeObject(forKey: pendingDisplayNameKey)
        // Keep focus key briefly for UI chrome (SOS).
        let resolvedName = name.isEmpty ? id : name
        if id.isEmpty && name.isEmpty && focus != .sos && focus != .battery && focus != .imOk {
            defaults.removeObject(forKey: pendingFocusKey)
            return (id: "", name: "", focus: focus)
        }
        return (id: id, name: resolvedName, focus: focus)
    }

    static func clearFocus() {
        UserDefaults.standard.removeObject(forKey: pendingFocusKey)
    }
}
