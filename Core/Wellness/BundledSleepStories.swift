import Foundation

/// Three sleep stories always available on-device (API may add more).
/// Catalog SSOT: `Resources/Wellness/BundledSleepStories.json` (Swift fallback if missing).
enum BundledSleepStories {
    static let ids = ["cloud", "garden", "stars"]

    private struct CatalogFile: Codable {
        struct Story: Codable {
            let id: String
            let durationMin: Int
            let titleKey: String
            let scriptKey: String
        }
        let stories: [Story]
    }

    private static let fallbackEntries: [(id: String, durationMin: Int, titleKey: String, scriptKey: String)] = [
        ("cloud", 5, "bundled_sleep_cloud_title", "bundled_sleep_cloud_script"),
        ("garden", 6, "bundled_sleep_garden_title", "bundled_sleep_garden_script"),
        ("stars", 7, "bundled_sleep_stars_title", "bundled_sleep_stars_script"),
    ]

    private static let cachedEntries: [(id: String, durationMin: Int, titleKey: String, scriptKey: String)] = {
        guard let url = Bundle.main.url(forResource: "BundledSleepStories", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let file = try? JSONDecoder().decode(CatalogFile.self, from: data),
              !file.stories.isEmpty else {
            return fallbackEntries
        }
        return file.stories.map { ($0.id, $0.durationMin, $0.titleKey, $0.scriptKey) }
    }()

    static func catalog(localization: LocalizationManager = .shared) -> [WellnessSleepStoryDTO] {
        cachedEntries.map { entry in
            WellnessSleepStoryDTO(
                id: entry.id,
                title: localization.localized(entry.titleKey),
                durationMin: entry.durationMin,
                audioUrl: nil
            )
        }
    }

    static func script(id: String, localization: LocalizationManager = .shared) -> String? {
        guard let entry = cachedEntries.first(where: { $0.id == id }) else { return nil }
        return localization.localized(entry.scriptKey)
    }

    /// Bundle first; server stories append when they have a new id.
    static func merged(apiStories: [WellnessSleepStoryDTO], localization: LocalizationManager = .shared) -> [WellnessSleepStoryDTO] {
        var byId: [String: WellnessSleepStoryDTO] = [:]
        let bundled = catalog(localization: localization)
        for story in bundled {
            byId[story.id] = story
        }
        for story in apiStories {
            if let existing = byId[story.id], (story.audioUrl == nil || story.audioUrl?.isEmpty == true) {
                byId[story.id] = existing
            } else {
                byId[story.id] = story
            }
        }
        let order = bundled.map(\.id) + apiStories.map(\.id).filter { id in !bundled.contains(where: { $0.id == id }) }
        var seen = Set<String>()
        return order.compactMap { id in
            guard seen.insert(id).inserted else { return nil }
            return byId[id]
        }
    }
}
