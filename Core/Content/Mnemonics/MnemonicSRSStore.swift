import Foundation

/// Leitner-style spaced repetition for mnemo items (intervals: 1, 3, 7, 14, 30 days).
final class MnemonicSRSStore {
    static let shared = MnemonicSRSStore()

    private let defaults: UserDefaults
    private let storageKey = "child.mnemo.srs.v1"
    private let iCloudEnabledKey = "child.mnemo.srs.icloud_enabled"
    private let reviewIntervalsDays = [1, 3, 7, 14, 30]
    private let ubiquitousStore = NSUbiquitousKeyValueStore.default

    private struct Entry: Codable {
        var itemId: String
        var box: Int
        var lastReviewed: Date?
        var nextReview: Date?
    }

    private var entries: [String: Entry] = [:]

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        load()
        if isICloudSyncEnabled {
            mergeFromICloudIfAvailable()
        }
    }

    var isICloudSyncEnabled: Bool {
        get { defaults.bool(forKey: iCloudEnabledKey) }
        set {
            defaults.set(newValue, forKey: iCloudEnabledKey)
            if newValue {
                mergeFromICloudIfAvailable()
            }
            persist()
        }
    }

#if DEBUG
    func uiTestForceDue(itemId: String, now: Date = Date()) {
        var entry = entries[itemId] ?? Entry(itemId: itemId, box: 0, lastReviewed: nil, nextReview: nil)
        entry.nextReview = Calendar.current.date(byAdding: .day, value: -1, to: now)
        entries[itemId] = entry
        persist()
    }
#endif

    func dueToday(category: String? = nil, now: Date = Date()) -> Int {
        dueItems(category: category, now: now).count
    }

    /// Unified «Повтори сегодня» queue across all mnemo categories.
    func unifiedDueItems(now: Date = Date()) -> [String] {
        dueItems(category: nil, now: now)
    }

    func unifiedDueToday(now: Date = Date()) -> Int {
        unifiedDueItems(now: now).count
    }

    /// Recall mastery 0…100 derived from SRS box (0→0%, 1→25%, …, 4→100%).
    func recallMasteryPercent(itemId: String) -> Int {
        guard let entry = entries[itemId] else { return 0 }
        return min(100, max(0, entry.box * 25))
    }

    func categoryId(for itemId: String) -> String? {
        if itemId.hasPrefix("songs.") { return ChildCategoryKey.songs }
        if itemId.hasPrefix("games.") { return ChildCategoryKey.games }
        if itemId.hasPrefix("study.") { return ChildCategoryKey.study }
        if itemId.hasPrefix("cartoons.") { return ChildCategoryKey.cartoons }
        if itemId.hasPrefix("music.") { return ChildCategoryKey.music }
        if itemId.hasPrefix("video.") { return ChildCategoryKey.video }
        if itemId.hasPrefix("movies.") { return ChildCategoryKey.movies }
        if itemId.hasPrefix("education.") { return ChildCategoryKey.education }
        return nil
    }

    func dueItems(category: String? = nil, now: Date = Date()) -> [String] {
        let start = Calendar.current.startOfDay(for: now)
        return entries.values
            .filter { entry in
                guard category == nil || entry.itemId.hasPrefix(categoryPrefix(for: category!)) else { return false }
                guard let next = entry.nextReview else { return true }
                return Calendar.current.startOfDay(for: next) <= start
            }
            .map(\.itemId)
            .sorted()
    }

    func recordSuccess(itemId: String, now: Date = Date()) {
        var entry = entries[itemId] ?? Entry(itemId: itemId, box: 0, lastReviewed: nil, nextReview: nil)
        entry.box = min(entry.box + 1, reviewIntervalsDays.count - 1)
        entry.lastReviewed = now
        entry.nextReview = Calendar.current.date(byAdding: .day, value: reviewIntervalsDays[entry.box], to: now)
        entries[itemId] = entry
        persist()
    }

    func recordFailure(itemId: String, now: Date = Date()) {
        var entry = entries[itemId] ?? Entry(itemId: itemId, box: 0, lastReviewed: nil, nextReview: nil)
        entry.box = 0
        entry.lastReviewed = now
        entry.nextReview = Calendar.current.date(
            byAdding: .day,
            value: reviewIntervalsDays[0],
            to: now
        )
        entries[itemId] = entry
        persist()
    }

    func scheduleInitial(itemId: String, now: Date = Date()) {
        guard entries[itemId] == nil else { return }
        entries[itemId] = Entry(
            itemId: itemId,
            box: 0,
            lastReviewed: now,
            nextReview: Calendar.current.date(byAdding: .day, value: reviewIntervalsDays[0], to: now)
        )
        persist()
    }

    private func categoryPrefix(for category: String) -> String {
        switch category {
        case ChildCategoryKey.songs: return "songs."
        case ChildCategoryKey.games: return "games."
        case ChildCategoryKey.study: return "study."
        case ChildCategoryKey.cartoons: return "cartoons."
        case ChildCategoryKey.music: return "music."
        case ChildCategoryKey.video: return "video."
        case ChildCategoryKey.movies: return "movies."
        case ChildCategoryKey.education: return "education."
        default: return ""
        }
    }

    private func load() {
        guard let data = defaults.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([Entry].self, from: data)
        else {
            entries = [:]
            return
        }
        entries = Dictionary(uniqueKeysWithValues: decoded.map { ($0.itemId, $0) })
    }

    private func persist() {
        let rows = Array(entries.values)
        guard let data = try? JSONEncoder().encode(rows) else { return }
        defaults.set(data, forKey: storageKey)
        if isICloudSyncEnabled {
            ubiquitousStore.set(data, forKey: storageKey)
            ubiquitousStore.synchronize()
        }
        Task {
            await MnemonicNotificationScheduler.shared.rescheduleDailyReminder()
        }
    }

    private func mergeFromICloudIfAvailable() {
        guard isICloudSyncEnabled,
              let data = ubiquitousStore.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([Entry].self, from: data)
        else { return }
        let cloudEntries = Dictionary(uniqueKeysWithValues: decoded.map { ($0.itemId, $0) })
        for (itemId, cloudEntry) in cloudEntries {
            guard let local = entries[itemId] else {
                entries[itemId] = cloudEntry
                continue
            }
            let localDate = local.lastReviewed ?? .distantPast
            let cloudDate = cloudEntry.lastReviewed ?? .distantPast
            if cloudDate >= localDate {
                entries[itemId] = cloudEntry
            }
        }
        if let data = try? JSONEncoder().encode(Array(entries.values)) {
            defaults.set(data, forKey: storageKey)
        }
    }
}
