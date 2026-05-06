import Foundation

protocol ContentDatabaseProtocol {
    func saveManifest(_ manifest: ContentManifest) async throws
    func loadManifest() async -> ContentManifest?
    func saveProgress(_ progress: ContentProgress) async throws
    func loadProgress(contentId: String) async -> ContentProgress?
    func loadAllItems() async -> [ContentItem]
}

final class ContentDatabase: ContentDatabaseProtocol, @unchecked Sendable {
    static let shared = ContentDatabase()

    private let queue = DispatchQueue(label: "content.database.queue", qos: .userInitiated)
    private let persistenceURL: URL
    private var manifest: ContentManifest?
    private var progressById: [String: ContentProgress] = [:]

    private struct PersistedContentSnapshot: Codable {
        let manifest: ContentManifest?
        let progressById: [String: ContentProgress]
    }

    private init() {
        let baseDir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        let contentDir = baseDir.appendingPathComponent("ContentStorage", isDirectory: true)
        self.persistenceURL = contentDir.appendingPathComponent("content-db-v1.json")
        loadFromDiskIfAvailable()
    }

    func saveManifest(_ manifest: ContentManifest) async throws {
        try await withCheckedThrowingContinuation { continuation in
            queue.async {
                let previous = self.manifest
                self.manifest = manifest
                do {
                    try self.persistToDisk()
                    continuation.resume(returning: ())
                } catch {
                    self.manifest = previous
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    func loadManifest() async -> ContentManifest? {
        await withCheckedContinuation { continuation in
            queue.async {
                continuation.resume(returning: self.manifest)
            }
        }
    }

    func saveProgress(_ progress: ContentProgress) async throws {
        try await withCheckedThrowingContinuation { continuation in
            queue.async {
                self.progressById[progress.contentId] = progress
                do {
                    try self.persistToDisk()
                    continuation.resume(returning: ())
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    func loadProgress(contentId: String) async -> ContentProgress? {
        await withCheckedContinuation { continuation in
            queue.async {
                continuation.resume(returning: self.progressById[contentId])
            }
        }
    }

    func loadAllItems() async -> [ContentItem] {
        await withCheckedContinuation { continuation in
            queue.async {
                continuation.resume(returning: self.manifest?.items ?? [])
            }
        }
    }

    private func loadFromDiskIfAvailable() {
        queue.sync {
            guard FileManager.default.fileExists(atPath: persistenceURL.path) else { return }
            do {
                let data = try Data(contentsOf: persistenceURL)
                let snapshot = try JSONDecoder().decode(PersistedContentSnapshot.self, from: data)
                self.manifest = snapshot.manifest
                self.progressById = snapshot.progressById
            } catch {
                // If snapshot is corrupted, start with clean in-memory state and overwrite on next save.
                self.manifest = nil
                self.progressById = [:]
            }
        }
    }

    private func persistToDisk() throws {
        let snapshot = PersistedContentSnapshot(manifest: manifest, progressById: progressById)
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.withoutEscapingSlashes]
        let data = try encoder.encode(snapshot)

        let dir = persistenceURL.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try data.write(to: persistenceURL, options: .atomic)
    }
}

