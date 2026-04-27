import Foundation

final class ContentManager: ObservableObject {
    static let shared = ContentManager()

    private let database: ContentDatabaseProtocol
    private let syncManager: ContentSyncManager
    private let cacheManager: ContentCacheManager
    private let defaults = UserDefaults.standard
    private let lastAutoSyncKey = "content.last_auto_sync_at"
    private let minAutoSyncIntervalSec: TimeInterval = 60 * 30
    private let apiClient: ContentAPIClient
    private let fallbackClient: ContentAPIClient
    private let activeChildProfileServerIdKey = "active_child_profile_server_id"

    @MainActor @Published private(set) var isSyncInProgress = false
    @MainActor @Published private(set) var lastSyncAt: Date?

    enum Audience {
        case child
        case elderly
    }

    init(
        database: ContentDatabaseProtocol = ContentDatabase.shared,
        syncManager: ContentSyncManager = .shared,
        cacheManager: ContentCacheManager = .shared,
        apiClient: ContentAPIClient = NetworkContentAPIClient.shared,
        fallbackClient: ContentAPIClient = DefaultContentAPIClient.shared
    ) {
        self.database = database
        self.syncManager = syncManager
        self.cacheManager = cacheManager
        self.apiClient = apiClient
        self.fallbackClient = fallbackClient
    }

    func syncContent(using apiClient: ContentAPIClient) async throws {
        await MainActor.run { isSyncInProgress = true }
        defer { Task { @MainActor in isSyncInProgress = false } }

        try await syncManager.sync(using: apiClient)
        await MainActor.run { lastSyncAt = Date() }
    }

    func autoRefreshIfNeeded(force: Bool = false) async {
        if !force, let last = defaults.object(forKey: lastAutoSyncKey) as? Date {
            if Date().timeIntervalSince(last) < minAutoSyncIntervalSec {
                return
            }
        }

        do {
            try await syncContent(using: apiClient)
            defaults.set(Date(), forKey: lastAutoSyncKey)
        } catch {
            do {
                try await syncContent(using: fallbackClient)
                defaults.set(Date(), forKey: lastAutoSyncKey)
            } catch {
                // Keep local content available even if sync fails.
            }
        }
    }

    /// Unified content lifecycle used by child and elderly interfaces.
    func runUnifiedLifecycle(forceRefresh: Bool = false) async {
        try? await bootstrapLocalContentIfNeeded()
        await autoRefreshIfNeeded(force: forceRefresh)
    }

    func loadContent(for categoryId: String, ageBand: ContentAgeBand) async -> [ContentItem] {
        let all = await database.loadAllItems()
        return all.filter { $0.categoryId == categoryId && $0.ageBand == ageBand }
    }

    func loadPersonalizedContent(for categoryId: String, ageBand: ContentAgeBand) async -> [ContentItem] {
        let base = await loadContent(for: categoryId, ageBand: ageBand)
            .filter { ContentExperienceResolver.shared.isRoutable($0) }
        var progressById: [String: ContentProgress] = [:]
        for item in base {
            if let progress = await database.loadProgress(contentId: item.id) {
                progressById[item.id] = progress
            }
        }
        return ContentRecommender.shared.rank(
            items: base,
            progressById: progressById,
            childId: activeChildId()
        )
    }

    func loadProgress(contentId: String) async -> ContentProgress? {
        await database.loadProgress(contentId: contentId)
    }

    func loadFeed(categoryIds: [String], limit: Int = 5) async -> [ContentItem] {
        let all = await database.loadAllItems()
        return all
            .filter { categoryIds.contains($0.categoryId) }
            .sorted { $0.metadata.title < $1.metadata.title }
            .prefix(limit)
            .map { $0 }
    }

    func loadUnifiedAudienceFeed(audience: Audience, limit: Int = 6) async -> [ContentItem] {
        await runUnifiedLifecycle(forceRefresh: false)
        return await loadFeed(categoryIds: lifecycleCategoryIds(for: audience), limit: limit)
    }

    func bootstrapLocalContentIfNeeded() async throws {
        if await database.loadManifest() != nil {
            return
        }
        let manifest = ContentSeedProvider.shared.initialManifest()
        try await database.saveManifest(manifest)
        await cacheManager.cacheManifest(manifest)
    }

    func getContent(contentId: String) async -> ContentItem? {
        if let cached = await cacheManager.loadItem(contentId: contentId) {
            return cached
        }
        let items = await database.loadAllItems()
        guard let found = items.first(where: { $0.id == contentId }) else { return nil }
        await cacheManager.cacheItem(found)
        return found
    }

    func saveProgress(_ progress: ContentProgress) async throws {
        try await database.saveProgress(progress)
    }

    func recordPersonalizationInteraction(for item: ContentItem) {
        InterestAnalyzer.shared.recordInteraction(item: item, childId: activeChildId())
    }

    func personalizedRecommendations(for categoryId: String, ageBand: ContentAgeBand) async -> [ContentRecommendation] {
        let base = await loadContent(for: categoryId, ageBand: ageBand)
        var progressById: [String: ContentProgress] = [:]
        for item in base {
            if let progress = await database.loadProgress(contentId: item.id) {
                progressById[item.id] = progress
            }
        }
        return ContentRecommender.shared.recommendations(
            items: base,
            progressById: progressById,
            childId: activeChildId()
        )
    }

    func parentDashboardSnapshot() -> ParentDashboardSnapshot {
        ParentDashboardSnapshot(
            totalOpens: ProgressTracker.shared.totalOpens,
            totalCompletions: ProgressTracker.shared.totalCompletions,
            completionRate: ProgressTracker.shared.completionRate,
            currentStreakDays: StreakTracker.shared.currentStreakDays,
            remainingTimeSecToday: TimeTracker.shared.remainingSecondsToday,
            unlockedAchievements: AchievementSystem.shared.unlockedAchievements()
        )
    }

    private func activeChildId() -> String? {
        let raw = defaults.string(forKey: activeChildProfileServerIdKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard let raw, !raw.isEmpty else { return nil }
        return raw
    }

    private func lifecycleCategoryIds(for audience: Audience) -> [String] {
        switch audience {
        case .child:
            return [
                ChildCategoryKey.safety,
                ChildCategoryKey.games,
                ChildCategoryKey.study,
                ChildCategoryKey.education
            ]
        case .elderly:
            return FamilyContentSafetyBridge.resolvedElderlyCategories()
        }
    }
}

