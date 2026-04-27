import Foundation

final class ContentCacheManager {
    static let shared = ContentCacheManager()

    private let cache = CacheManager.shared
    private let defaultTTL: TimeInterval = 60 * 60
    private let maxDiskBudgetMb: Int = 250

    private init() {}

    func cacheItem(_ item: ContentItem) async {
        await cache.store(
            item,
            forKey: "content.item.\(item.id)",
            ttl: defaultTTL,
            priority: .high,
            encrypt: false
        )
    }

    func loadItem(contentId: String) async -> ContentItem? {
        await cache.retrieve(ContentItem.self, forKey: "content.item.\(contentId)")
    }

    func cacheManifest(_ manifest: ContentManifest) async {
        await cache.store(
            manifest,
            forKey: "content.manifest.\(manifest.manifestVersion)",
            ttl: defaultTTL,
            priority: .critical,
            encrypt: false
        )
    }

    func cachePolicyDescription() -> String {
        "TTL=\(Int(defaultTTL))s, strategy=LRU, diskBudget=\(maxDiskBudgetMb)MB"
    }
}

