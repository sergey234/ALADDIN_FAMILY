import Foundation

/// inf-deeplink — single router for Unicorn habit / check-in / day-recap / focus / medicine.
enum UnicornDeepLinkRouter {
    enum Destination: Equatable {
        case companionTalk
        case wellnessCheckin
        case voiceDayRecap
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
        if CompanionDeepLinkRouter.isVoiceDayRecapDeepLink(url) {
            return .voiceDayRecap
        }

        // aladdin://focus  | aladdin://focus/session
        if host == "focus" || (host == "unicorn" && pathParts.first == "focus") {
            return .focusSession
        }

        // aladdin://habit/medicine | aladdin://habit/done?preset=water
        if host == "habit" || host == "habits" {
            if pathParts.first == "done" {
                let preset = URLComponents(url: url, resolvingAgainstBaseURL: false)?
                    .queryItems?
                    .first(where: { $0.name.lowercased() == "preset" })?
                    .value?
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                return .habitDone(preset: (preset?.isEmpty == false ? preset! : "water"))
            }
            if pathParts.first == "medicine" || pathParts.isEmpty {
                if pathParts.first == "medicine" {
                    return .familyHabits
                }
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
        case .focusSession:
            if FamilyFocusSessionFeature.isEnabled {
                navigation.navigateTo(.focusSession)
            } else {
                navigation.navigateTo(.family)
            }
        case .familyHabits:
            navigation.navigateTo(.family)
        case .habitDone(let preset):
            Task {
                _ = await FamilyHabitRemindersScheduler.shared.handleDone(presetRaw: preset)
            }
            navigation.navigateTo(.family)
        }
        return true
    }

    /// Canonical deepLink string for habit pushes (tap → Family).
    static func habitReminderDeepLink(preset: String) -> String {
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
