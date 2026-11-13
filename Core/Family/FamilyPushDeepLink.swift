import Foundation

/// R10 — family push → map / member sheet (never silent-drop to SimpleHome).
///
/// Map-pending SSOT (anti sticky «Проверить → карта»):
/// - `enqueue` stores focus + open flag + timestamp
/// - UI opens map only via `takeMapPresentationIfNeeded()` (atomic clear)
/// - soft intents TTL; urgent (SOS / battery / ImOK) longer TTL
/// - sheet dismiss / intentional Antifake → `clearSoftMapPending` / `clearMapPendingOnDismiss`
enum FamilyPushDeepLink {
    static let navigateToFamilyMapName = Notification.Name("NavigateToFamilyMap")
    static let pendingMemberIdKey = "aladdin.family_push.pending_member_id"
    static let pendingDisplayNameKey = "aladdin.family_push.pending_display_name"
    static let pendingFocusKey = "aladdin.family_push.pending_focus"
    static let pendingOpenMapKey = "aladdin.family_push.pending_open_map"
    /// Epoch seconds when `pendingOpenMapKey` was set (TTL gate).
    static let pendingOpenMapAtKey = "aladdin.family_push.pending_open_map_at"

    /// Soft map intents expire quickly so they cannot hijack Antifake return.
    private static let softMapTTL: TimeInterval = 5 * 60
    /// Urgent (Need Help / battery / ImOK) may wait longer while user finishes another screen.
    private static let urgentMapTTL: TimeInterval = 30 * 60

    enum Focus: String {
        case sos
        case imOk = "im_ok"
        case battery
        case location
        case trips
        case habits
        case limits
        case map

        var isUrgentMapFocus: Bool {
            switch self {
            case .sos, .battery, .imOk: return true
            case .location, .trips, .habits, .limits, .map: return false
            }
        }
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
        if openMap {
            defaults.set(Date().timeIntervalSince1970, forKey: pendingOpenMapAtKey)
            print("WHERE_PHONE pending enqueue focus=\(focus.rawValue) urgent=\(focus.isUrgentMapFocus) openMap=1")
        } else {
            defaults.removeObject(forKey: pendingOpenMapAtKey)
        }
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
        print("WHERE_PHONE NavigateToFamilyMap post focus=\(pendingFocus().rawValue)")
        NotificationCenter.default.post(name: navigateToFamilyMapName, object: nil)
    }

    /// Atomic: if a still-valid map intent exists, clear the open flag and return focus.
    /// Call from SimpleHome / Family `onAppear` / `onReceive` — never read raw `pendingOpenMapKey` alone.
    @discardableResult
    static func takeMapPresentationIfNeeded(reason: String) -> Focus? {
        let defaults = UserDefaults.standard
        guard defaults.bool(forKey: pendingOpenMapKey) else {
            return nil
        }
        let focus = pendingFocus()
        if isPendingMapExpired(focus: focus) {
            print("WHERE_PHONE map pending TTL expired reason=\(reason) focus=\(focus.rawValue) → clear")
            clearMapOpenFlagOnly()
            return nil
        }
        clearMapOpenFlagOnly()
        print("WHERE_PHONE map take reason=\(reason) focus=\(focus.rawValue) urgent=\(focus.isUrgentMapFocus)")
        return focus
    }

    /// Soft intents only — keep SOS / battery / ImOK so Need Help survives Antifake.
    static func clearSoftMapPending(reason: String) {
        let focus = pendingFocus()
        guard UserDefaults.standard.bool(forKey: pendingOpenMapKey) else { return }
        if focus.isUrgentMapFocus {
            print("WHERE_PHONE map soft-clear skipped urgent focus=\(focus.rawValue) reason=\(reason)")
            return
        }
        clearMapOpenFlagOnly()
        print("WHERE_PHONE map soft-clear reason=\(reason) focus=\(focus.rawValue)")
    }

    /// Sheet dismissed before / without consume — never leave sticky open flag.
    static func clearMapPendingOnDismiss(reason: String) {
        guard UserDefaults.standard.bool(forKey: pendingOpenMapKey) else { return }
        clearMapOpenFlagOnly()
        print("WHERE_PHONE map dismiss-clear reason=\(reason)")
    }

    /// Consume pending member for sheet focus. Clears member/name; keeps focus until map dismiss if needed.
    static func consumePendingMember() -> (id: String, name: String, focus: Focus)? {
        let defaults = UserDefaults.standard
        let id = (defaults.string(forKey: pendingMemberIdKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let name = (defaults.string(forKey: pendingDisplayNameKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let focus = pendingFocus()
        let openFlag = defaults.bool(forKey: pendingOpenMapKey)
        // After `takeMapPresentationIfNeeded`, open flag is already false — still apply member chrome.
        guard openFlag || !id.isEmpty || focus == .sos || focus == .battery || focus == .imOk else {
            return nil
        }
        if openFlag {
            clearMapOpenFlagOnly()
        }
        defaults.removeObject(forKey: pendingMemberIdKey)
        defaults.removeObject(forKey: pendingDisplayNameKey)
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

    // MARK: - Private

    private static func pendingFocus() -> Focus {
        let raw = UserDefaults.standard.string(forKey: pendingFocusKey) ?? Focus.map.rawValue
        return Focus(rawValue: raw) ?? .map
    }

    private static func isPendingMapExpired(focus: Focus) -> Bool {
        let at = UserDefaults.standard.double(forKey: pendingOpenMapAtKey)
        // Legacy flags without timestamp: treat as expired soft (avoid eternal hijack).
        if at <= 0 {
            return !focus.isUrgentMapFocus
        }
        let age = Date().timeIntervalSince1970 - at
        let ttl = focus.isUrgentMapFocus ? urgentMapTTL : softMapTTL
        return age > ttl
    }

    private static func clearMapOpenFlagOnly() {
        let defaults = UserDefaults.standard
        defaults.set(false, forKey: pendingOpenMapKey)
        defaults.removeObject(forKey: pendingOpenMapAtKey)
    }
}
