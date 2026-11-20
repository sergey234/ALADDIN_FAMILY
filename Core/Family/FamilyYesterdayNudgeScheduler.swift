import Foundation
import UserNotifications

/// Growth P.1: once on day 3 at 19:00, parent/creator with family ≥2 gets
/// «Where was {name} yesterday?» → `aladdin://family/location-history?member=`.
/// Never asks for notification permission. Not a paywall push.
final class FamilyYesterdayNudgeScheduler {
    static let shared = FamilyYesterdayNudgeScheduler()

    static let minRosterSize = 2
    static let dayOffset = 3
    static let fireHour = 19
    static let identifier = "family.growth.yesterday.d3"
    static let deepLinkPrefix = "aladdin://family/location-history"

    private static let anchorKey = "family_yesterday_nudge_anchor_v1"
    private static let familyKey = "family_yesterday_nudge_family_v1"
    private static let doneKey = "family_yesterday_nudge_done_v1"
    private static let memberIdKey = "family_yesterday_nudge_member_id_v1"
    private static let memberNameKey = "family_yesterday_nudge_member_name_v1"

    struct Slot: Equatable {
        let fireDate: Date
        let memberId: String
        let memberName: String
    }

    enum Decision: Equatable {
        case ignore
        case cancel
        case schedule(Slot)
    }

    private let center = UNUserNotificationCenter.current()
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    static func deepLink(memberId: String) -> String {
        var components = URLComponents()
        components.scheme = "aladdin"
        components.host = "family"
        components.path = "/location-history"
        components.queryItems = [URLQueryItem(name: "member", value: memberId)]
        return components.url?.absoluteString ?? "\(deepLinkPrefix)?member=\(memberId)"
    }

    /// Prefer a non-self child/teen; else any other member with a real name.
    static func pickHighlightMember(from members: [FamilyMemberData]) -> (id: String, name: String)? {
        let others = members.filter { !$0.isCurrentUser }
        let preferredRoles: Set<FamilyMemberCard.FamilyRole> = [.child, .teenager]
        let preferred = others.first { preferredRoles.contains($0.role) && !$0.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
            ?? others.first { !$0.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
        guard let m = preferred else { return nil }
        let name = m.name.trimmingCharacters(in: .whitespacesAndNewlines)
        let id = m.canonicalId
        guard !name.isEmpty, !id.isEmpty else { return nil }
        return (id, name)
    }

    static func fireDate(anchor: Date, now: Date, calendar: Calendar = .current) -> Date? {
        let start = calendar.startOfDay(for: anchor)
        guard let day = calendar.date(byAdding: .day, value: dayOffset, to: start),
              let fire = calendar.date(bySettingHour: fireHour, minute: 0, second: 0, of: day),
              fire > now else { return nil }
        return fire
    }

    static func decide(
        rosterUsed: Int,
        isEligibleRole: Bool,
        alreadyDone: Bool,
        memberId: String?,
        memberName: String?,
        anchor: Date,
        now: Date,
        calendar: Calendar = .current
    ) -> Decision {
        guard isEligibleRole else { return .ignore }
        if rosterUsed < minRosterSize { return alreadyDone ? .ignore : .cancel }
        if alreadyDone { return .ignore }
        guard let memberId, !memberId.isEmpty,
              let memberName, !memberName.isEmpty,
              let fire = fireDate(anchor: anchor, now: now, calendar: calendar) else {
            return .ignore
        }
        return .schedule(Slot(fireDate: fire, memberId: memberId, memberName: memberName))
    }

    /// Call alongside growth nudge on `/api/family/stats` refresh.
    func reconcile(
        rosterUsed: Int,
        familyId: String?,
        isCreator: Bool,
        members: [FamilyMemberData] = FamilyLocalStore.loadPersistedMembers(),
        now: Date = Date()
    ) {
        guard let familyId, !familyId.isEmpty else { return }
        if defaults.string(forKey: Self.familyKey) != familyId {
            defaults.set(familyId, forKey: Self.familyKey)
            defaults.set(now.timeIntervalSince1970, forKey: Self.anchorKey)
            defaults.set(false, forKey: Self.doneKey)
            defaults.removeObject(forKey: Self.memberIdKey)
            defaults.removeObject(forKey: Self.memberNameKey)
        }

        let highlight = Self.pickHighlightMember(from: members)
        if let highlight {
            defaults.set(highlight.id, forKey: Self.memberIdKey)
            defaults.set(highlight.name, forKey: Self.memberNameKey)
        }

        let isEligible = isCreator || FamilyRosterAccess.canManageRoster(members: members)
        let anchorTs = defaults.double(forKey: Self.anchorKey)
        let decision = Self.decide(
            rosterUsed: rosterUsed,
            isEligibleRole: isEligible,
            alreadyDone: defaults.bool(forKey: Self.doneKey),
            memberId: defaults.string(forKey: Self.memberIdKey) ?? highlight?.id,
            memberName: defaults.string(forKey: Self.memberNameKey) ?? highlight?.name,
            anchor: anchorTs > 0 ? Date(timeIntervalSince1970: anchorTs) : now,
            now: now
        )

        switch decision {
        case .ignore:
            return
        case .cancel:
            defaults.set(true, forKey: Self.doneKey)
            center.removePendingNotificationRequests(withIdentifiers: [Self.identifier])
        case .schedule(let slot):
            Task { await self.schedule(slot) }
        }
    }

    private func schedule(_ slot: Slot) async {
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional else {
            return
        }
        let pending = Set(await center.pendingNotificationRequests().map(\.identifier))
        if pending.contains(Self.identifier) { return }

        let localization = LocalizationManager.shared
        let content = UNMutableNotificationContent()
        content.title = String(
            format: localization.localized("family_yesterday_push_title"),
            slot.memberName
        )
        content.body = localization.localized("family_yesterday_push_body")
        content.sound = .default
        content.userInfo = [
            "type": "family_yesterday_nudge",
            "deepLink": Self.deepLink(memberId: slot.memberId),
            "member_id": slot.memberId,
            "display_name": slot.memberName
        ]
        let comps = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: slot.fireDate)
        let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
        try? await center.add(UNNotificationRequest(identifier: Self.identifier, content: content, trigger: trigger))
    }
}
