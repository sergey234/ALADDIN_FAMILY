import Foundation

/// inf-deeplink — single router for Unicorn habit / check-in / day-recap / focus / medicine.
enum UnicornDeepLinkRouter {
    enum Destination: Equatable {
        case companionTalk
        case wellnessCheckin
        case voiceDayRecap
        case voiceLog
        case voiceWeekly
        case focusSession
        case familyHabits
        case habitDone(preset: String)
    }

    /// Parse `aladdin://…` Unicorn destinations. Returns nil if not ours.
    static func parse(_ url: URL) -> Destination? {
        guard url.scheme?.lowercased() == "aladdin" else { return nil }
        let host = (url.host ?? "").lowercased()
        let path = url.path.lowercased().trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        let pathParts = path.split(separator: "/").map(String.init)

        if CompanionDeepLinkRouter.isCompanionTalkDeepLink(url) {
            return .companionTalk
        }
        if CompanionDeepLinkRouter.isWellnessCheckinDeepLink(url) {
            return .wellnessCheckin
        }
        if CompanionDeepLinkRouter.isVoiceWeeklyDeepLink(url) {
            return .voiceWeekly
        }
        if CompanionDeepLinkRouter.isVoiceDayRecapDeepLink(url) {
            return .voiceDayRecap
        }
        if CompanionDeepLinkRouter.isVoiceLogDeepLink(url) {
            return .voiceLog
        }

        // aladdin://focus  | aladdin://focus/session
        if host == "focus" || (host == "unicorn" && pathParts.first == "focus") {
            return .focusSession
        }

        // aladdin://habit/medicine | aladdin://habit/done?preset=water|custom.<uuid>
        if host == "habit" || host == "habits" {
            if pathParts.first == "done" {
                let rawPreset = URLComponents(url: url, resolvingAgainstBaseURL: false)?
                    .queryItems?
                    .first(where: { $0.name.lowercased() == "preset" })?
                    .value
                if let normalized = normalizedDonePreset(rawPreset) {
                    return .habitDone(preset: normalized)
                }
                // Malformed custom.* → open Family, do not fake Done
                if let raw = rawPreset?.trimmingCharacters(in: .whitespacesAndNewlines),
                   raw.hasPrefix(FamilyHabitRemindersScheduler.customPresetPrefix) {
                    return .familyHabits
                }
                return .habitDone(preset: "water")
            }
            // aladdin://habit/custom.<uuid> → Family (Done only via done?preset=)
            if let first = pathParts.first,
               first.hasPrefix(FamilyHabitRemindersScheduler.customPresetPrefix) {
                return .familyHabits
            }
            if pathParts.first == "medicine" || pathParts.isEmpty {
                return .familyHabits
            }
            return .familyHabits
        }

        // aladdin://family/habits
        if host == "family", pathParts.first == "habits" || pathParts.first == "challenges" {
            return .familyHabits
        }

        return nil
    }

    /// Apply destination via NavigationManager + notifications. Returns true if handled.
    @MainActor
    @discardableResult
    static func route(_ url: URL, navigation: NavigationManager) -> Bool {
        guard let dest = parse(url) else { return false }
        switch dest {
        case .companionTalk:
            navigation.navigateToCompanionTalkNow()
        case .wellnessCheckin:
            navigation.navigateToWellnessCheckinFromDeepLink()
        case .voiceDayRecap:
            VoiceDayRecapService.markPendingOpen()
            navigation.navigateTo(.settings)
            NotificationCenter.default.post(
                name: NSNotification.Name("NavigateToVoiceDayRecap"),
                object: nil
            )
        case .voiceLog:
            VoiceSafetyNowStore.markPendingOpen()
            navigation.navigateTo(.settings)
            NotificationCenter.default.post(name: .navigateToVoiceNotes, object: nil)
        case .voiceWeekly:
            VoiceWeeklyDigestService.markPendingOpen()
            VoiceSafetyNowStore.markPendingOpen()
            navigation.navigateTo(.settings)
            NotificationCenter.default.post(name: .navigateToVoiceNotes, object: nil)
        case .focusSession:
            if FamilyFocusSessionFeature.isEnabled {
                navigation.navigateTo(.focusSession)
            } else {
                navigation.navigateTo(.family)
            }
        case .familyHabits:
            navigation.navigateTo(.family)
        case .habitDone(let preset):
            Task { @MainActor in
                await performHabitDone(presetRaw: preset)
            }
            navigation.navigateTo(.family)
        }
        return true
    }

    /// Shared Done path for deep link + NotificationManager (fhc-04).
    @MainActor
    static func performHabitDone(presetRaw: String) async {
        guard let preset = normalizedDonePreset(presetRaw) else { return }
        let members = FamilyLocalStore.loadPersistedMembers()
        // fhc-15 — once_at Done → disable locally (best-effort sync).
        if let customId = FamilyHabitRemindersScheduler.customId(fromPresetRaw: preset) {
            await FamilyHabitRemindersService.shared.disableCustomAfterOnceAtDone(
                id: customId,
                members: members
            )
        }
        _ = await FamilyHabitRemindersScheduler.shared.handleDone(
            presetRaw: preset,
            config: FamilyHabitRemindersService.shared.config,
            members: members
        )
    }

    /// Resolve preset from notification userInfo (`preset` or deepLink query).
    static func habitPreset(fromUserInfo userInfo: [AnyHashable: Any]) -> String? {
        if let raw = userInfo["preset"] as? String {
            if let normalized = normalizedDonePreset(raw) {
                return normalized
            }
        }
        if let deepLink = userInfo["deepLink"] as? String,
           let url = URL(string: deepLink),
           case .habitDone(let preset) = parse(url) {
            return preset
        }
        return nil
    }

    /// Valid Done preset, or nil for malformed `custom.` (empty id).
    static func normalizedDonePreset(_ raw: String?) -> String? {
        let trimmed = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        if trimmed.hasPrefix(FamilyHabitRemindersScheduler.customPresetPrefix) {
            guard FamilyHabitRemindersScheduler.customId(fromPresetRaw: trimmed) != nil else {
                return nil
            }
        }
        return trimmed
    }

    /// Canonical deepLink string for habit pushes.
    static func habitReminderDeepLink(preset: String) -> String {
        // fhc-04 — custom Done uses explicit done?preset= (action + tap).
        if preset.hasPrefix(FamilyHabitRemindersScheduler.customPresetPrefix) {
            var components = URLComponents()
            components.scheme = "aladdin"
            components.host = "habit"
            components.path = "/done"
            components.queryItems = [URLQueryItem(name: "preset", value: preset)]
            return components.url?.absoluteString ?? "aladdin://habit/done?preset=\(preset)"
        }
        if preset == FamilyHabitPresetId.medicine.rawValue {
            return "aladdin://habit/medicine"
        }
        if preset == FamilyHabitPresetId.windDown.rawValue {
            return "aladdin://voice/day-recap"
        }
        return "aladdin://habit/\(preset)"
    }

    static func focusDeepLink() -> String { "aladdin://focus" }
}

// MARK: - fhc-04 hook / fhc-17 events (no title / body in params)

enum FamilyHabitCustomAnalytics {
    enum Event: String {
        case create = "family_habit_custom_create"
        case done = "family_habit_custom_done"
        case edit = "family_habit_custom_edit"
        case delete = "family_habit_custom_delete"
        case testPush = "family_habit_custom_test_push"
    }

    /// Allowed param keys only — never `title` / body (privacy).
    static let allowedParamKeys: Set<String> = ["id", "mode"]

    /// Builds sanitized params (id + optional mode). Exposed for unit tests.
    static func parameters(id: String, mode: String? = nil) -> [String: String] {
        var params: [String: String] = ["id": id]
        if let mode {
            let trimmed = mode.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                params["mode"] = trimmed
            }
        }
        return params
    }

    static func log(_ event: Event, id: String, mode: String? = nil) {
        let params = parameters(id: id, mode: mode)
        #if DEBUG
        assert(Set(params.keys).isSubset(of: allowedParamKeys))
        assert(!params.keys.contains("title"))
        #endif
        AnalyticsManager.shared.trackEvent(event.rawValue, parameters: params)
    }
}
