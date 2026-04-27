import Foundation

enum ContentVersionError: Error {
    case downgradeNotAllowed
    case invalidPatchChain
}

final class ContentVersionManager {
    static let shared = ContentVersionManager()

    private let defaults: UserDefaults
    private let versionKey = "content_manifest_version"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    var currentVersion: Int {
        defaults.integer(forKey: versionKey)
    }

    func updateVersion(to newVersion: Int) throws {
        guard newVersion >= currentVersion else {
            throw ContentVersionError.downgradeNotAllowed
        }
        defaults.set(newVersion, forKey: versionKey)
    }

    /// Откат после неудачного `applyManifest` (без проверки monotonic upgrade).
    func restoreStoredVersion(_ version: Int) {
        defaults.set(version, forKey: versionKey)
    }

    func applyDelta(_ patch: ContentDeltaPatch, to manifest: ContentManifest) throws -> ContentManifest {
        guard patch.fromVersion == manifest.manifestVersion else {
            throw ContentVersionError.invalidPatchChain
        }

        var map = Dictionary(uniqueKeysWithValues: manifest.items.map { ($0.id, $0) })
        for item in patch.added { map[item.id] = item }
        for item in patch.updated { map[item.id] = item }
        for id in patch.removedIds { map.removeValue(forKey: id) }

        return ContentManifest(
            manifestVersion: patch.toVersion,
            generatedAt: Date(),
            minSupportedAppVersion: manifest.minSupportedAppVersion,
            checksumSHA256: patch.checksumSHA256,
            signature: manifest.signature,
            categories: manifest.categories,
            items: map.values.sorted { $0.id < $1.id }
        )
    }
}

