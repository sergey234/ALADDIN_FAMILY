import Foundation

/// hab-03 — cold start / scene active: reschedule family habit local notifications from cache.
@MainActor
enum FamilyHabitRemindersBootstrap {
    static func reloadIfNeeded() async {
        let members = FamilyLocalStore.loadPersistedMembers()
        await FamilyHabitRemindersService.shared.rescheduleFromCache(members: members)
    }
}
