import Foundation
import UserNotifications

/// Family growth nudge (L360 stage 3): the family creator with fewer than `targetRosterSize` people
/// gets local reminders on day 2 and day 3 at 18:00 to invite relatives. Tap → `aladdin://family/invite`.
/// Reaching the target cancels pending reminders for good. Never asks for notification permission.
final class FamilyGrowthNudgeScheduler {
    static let shared = FamilyGrowthNudgeScheduler()

    static let targetRosterSize = 3
    static let dayOffsets = [2, 3]
    static let fireHour = 18
    static let identifierPrefix = "family.growth.invite."
    static let deepLink = "aladdin://family/invite"

    private static let anchorKey = "family_growth_nudge_anchor_v1"
    private static let familyKey = "family_growth_nudge_family_v1"
    private static let doneKey = "family_growth_nudge_done_v1"

    struct Slot: Equatable {
        let day: Int
        let fireDate: Date
    }

    enum Decision: Equatable {
        case ignore
        case cancel
        case schedule([Slot])
    }

    private let center = UNUserNotificationCenter.current()
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    static func identifier(day: Int) -> String {
        "\(identifierPrefix)d\(day)"
    }

    static func slots(anchor: Date, now: Date, calendar: Calendar = .current) -> [Slot] {
        let startOfAnchor = calendar.startOfDay(for: anchor)
        return dayOffsets.compactMap { day in
            guard let date = calendar.date(byAdding: .day, value: day, to: startOfAnchor),
                  let fire = calendar.date(bySettingHour: fireHour, minute: 0, second: 0, of: date),
                  fire > now else { return nil }
            return Slot(day: day, fireDate: fire)
        }
    }

    static func decide(
        rosterUsed: Int,
        isCreator: Bool,
        alreadyDone: Bool,
        anchor: Date,
        now: Date,
        calendar: Calendar = .current
    ) -> Decision {
        guard isCreator else { return .ignore }
        if rosterUsed >= targetRosterSize { return alreadyDone ? .ignore : .cancel }
        if alreadyDone { return .ignore }
        let upcoming = slots(anchor: anchor, now: now, calendar: calendar)
        return upcoming.isEmpty ? .ignore : .schedule(upcoming)
    }

    /// Call on every `/api/family/stats` refresh. A new `familyId` restarts the day-2/day-3 window.
    func reconcile(rosterUsed: Int, familyId: String?, isCreator: Bool, now: Date = Date()) {
        guard let familyId, !familyId.isEmpty else { return }
        if defaults.string(forKey: Self.familyKey) != familyId {
            defaults.set(familyId, forKey: Self.familyKey)
            defaults.set(now.timeIntervalSince1970, forKey: Self.anchorKey)
            defaults.set(false, forKey: Self.doneKey)
        }
        let anchorTs = defaults.double(forKey: Self.anchorKey)
        let decision = Self.decide(
            rosterUsed: rosterUsed,
            isCreator: isCreator,
            alreadyDone: defaults.bool(forKey: Self.doneKey),
            anchor: anchorTs > 0 ? Date(timeIntervalSince1970: anchorTs) : now,
            now: now
        )
        switch decision {
        case .ignore:
            return
        case .cancel:
            defaults.set(true, forKey: Self.doneKey)
            center.removePendingNotificationRequests(withIdentifiers: Self.dayOffsets.map(Self.identifier(day:)))
        case .schedule(let slots):
            Task { await self.schedule(slots) }
        }
    }

    private func schedule(_ slots: [Slot]) async {
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional else {
            return
        }
        let pending = Set(await center.pendingNotificationRequests().map(\.identifier))
        let localization = LocalizationManager.shared
        for slot in slots {
            let identifier = Self.identifier(day: slot.day)
            if pending.contains(identifier) { continue }
            let content = UNMutableNotificationContent()
            content.title = localization.localized("family_growth_nudge_title")
            content.body = localization.localized("family_growth_nudge_body_d\(slot.day)")
            content.sound = .default
            content.userInfo = ["type": "family_growth_invite", "deepLink": Self.deepLink]
            let comps = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: slot.fireDate)
            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
            try? await center.add(UNNotificationRequest(identifier: identifier, content: content, trigger: trigger))
        }
    }
}
