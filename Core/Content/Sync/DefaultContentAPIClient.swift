import Foundation

final class DefaultContentAPIClient: ContentAPIClient {
    static let shared = DefaultContentAPIClient()

    private init() {}

    func fetchManifest() async throws -> ContentManifest {
        // Fallback source until backend manifest endpoints are finalized.
        return ContentSeedProvider.shared.initialManifest()
    }

    func fetchDelta(from version: Int) async throws -> ContentDeltaPatch {
        // No real backend delta yet; return a no-op patch.
        return ContentDeltaPatch(
            fromVersion: version,
            toVersion: version,
            added: [],
            updated: [],
            removedIds: [],
            checksumSHA256: "noop-delta-\(version)"
        )
    }
}

