import Foundation
import UserNotifications

/// Daily local reminder when SRS items are due. Tap opens mnemo review via deep link category.
final class MnemonicNotificationScheduler {
    static let shared = MnemonicNotificationScheduler()

    static let notificationIdentifier = "mnemo.daily.review"
    static let userInfoType = "mnemo_review"

    private let center = UNUserNotificationCenter.current()
    private let srsStore: MnemonicSRSStore

    init(srsStore: MnemonicSRSStore = .shared) {
        self.srsStore = srsStore
    }

    static func totalDueCount(store: MnemonicSRSStore = .shared, now: Date = Date()) -> Int {
        store.dueItems(category: nil, now: now).count
    }

    /// Mnemo category with the highest due count today (for notification deep link).
    static func primaryReviewCategory(store: MnemonicSRSStore = .shared, now: Date = Date()) -> String? {
        let categories = [
            ChildCategoryKey.songs,
            ChildCategoryKey.games,
            ChildCategoryKey.study,
            ChildCategoryKey.cartoons,
            ChildCategoryKey.music,
            ChildCategoryKey.video,
            ChildCategoryKey.movies,
            ChildCategoryKey.education
        ]
        var best: (category: String, count: Int)?
        for category in categories {
            let count = store.dueToday(category: category, now: now)
            guard count > 0 else { continue }
            if best == nil || count > best!.count {
                best = (category, count)
            }
        }
        return best?.category
    }

    func rescheduleDailyReminder(now: Date = Date()) async {
        center.removePendingNotificationRequests(withIdentifiers: [Self.notificationIdentifier])

        let dueCount = Self.totalDueCount(store: srsStore, now: now)
        guard dueCount > 0 else { return }

        let category = Self.primaryReviewCategory(store: srsStore, now: now) ?? ChildCategoryKey.games
        let localization = LocalizationManager.shared
        let title = localization.localized("child_mnemo_push_review_title")
        let body = String(format: localization.localized("child_mnemo_srs_due_today"), dueCount)

        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.categoryIdentifier = NotificationCategory.mnemo.rawValue
        content.userInfo = [
            "type": Self.userInfoType,
            "category": category,
            "dueCount": dueCount
        ]

        var dateComponents = Calendar.current.dateComponents([.year, .month, .day], from: now)
        dateComponents.hour = 18
        dateComponents.minute = 0

        let trigger: UNNotificationTrigger
        if let fireDate = Calendar.current.date(from: dateComponents), fireDate > now {
            trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: false)
        } else {
            var tomorrow = dateComponents
            if let nextDay = Calendar.current.date(byAdding: .day, value: 1, to: now) {
                tomorrow = Calendar.current.dateComponents([.year, .month, .day], from: nextDay)
                tomorrow.hour = 18
                tomorrow.minute = 0
            }
            trigger = UNCalendarNotificationTrigger(dateMatching: tomorrow, repeats: false)
        }

        let request = UNNotificationRequest(
            identifier: Self.notificationIdentifier,
            content: content,
            trigger: trigger
        )
        try? await center.add(request)
    }
}
