import Foundation

enum ContentSyncError: Error, Equatable {
    case manifestValidationFailed
    case manifestSignatureMissing
    case manifestSignatureInvalid
    case manifestSigningKeyMissing
    case networkUnavailable
    case invalidServerPayload
    case serverError(statusCode: Int)
}

protocol ContentAPIClient {
    func fetchManifest() async throws -> ContentManifest
    func fetchDelta(from version: Int) async throws -> ContentDeltaPatch
}

/// Загрузка бинарного payload по `payloadURL` (G2 / W1-1).
protocol ContentPayloadDownloading: AnyObject {
    func downloadPayload(from url: URL) async throws -> Data
}

extension ContentDownloader: ContentPayloadDownloading {}

/// Скачивание payload и выставление `isOfflineAvailable` (W1-1). Вынесено для unit-тестов.
enum ContentManifestPayloadHydration {
    static func hydrate(
        manifest: ContentManifest,
        downloader: ContentPayloadDownloading,
        validator: ContentValidator
    ) async -> ContentManifest {
        var nextItems: [ContentItem] = []
        nextItems.reserveCapacity(manifest.items.count)

        for item in manifest.items {
            guard let url = item.payloadURL,
                  let expected = item.checksumSHA256,
                  !expected.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            else {
                nextItems.append(item)
                continue
            }

            do {
                let data = try await downloader.downloadPayload(from: url)
                guard validator.validateChecksum(data: data, expectedSHA256: expected) else {
                    nextItems.append(item)
                    continue
                }
                try Self.persistPayloadOnDisk(contentId: item.id, data: data)
                nextItems.append(
                    ContentItem(
                        id: item.id,
                        categoryId: item.categoryId,
                        type: item.type,
                        ageBand: item.ageBand,
                        version: item.version,
                        metadata: item.metadata,
                        payloadURL: item.payloadURL,
                        checksumSHA256: item.checksumSHA256,
                        isOfflineAvailable: true
                    )
                )
            } catch {
                nextItems.append(item)
            }
        }

        return ContentManifest(
            manifestVersion: manifest.manifestVersion,
            generatedAt: manifest.generatedAt,
            minSupportedAppVersion: manifest.minSupportedAppVersion,
            checksumSHA256: manifest.checksumSHA256,
            signature: manifest.signature,
            categories: manifest.categories,
            items: nextItems
        )
    }

    static func persistPayloadOnDisk(contentId: String, data: Data) throws {
        let root = try ContentPayloadDiskCachePolicy.payloadsRoot()
        let dir = root.appendingPathComponent(contentId, isDirectory: true)
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let fileURL = dir.appendingPathComponent("payload.bin", isDirectory: false)
        try data.write(to: fileURL, options: .atomic)
        try ContentPayloadDiskCachePolicy.enforceBudgetIfNeeded(maxTotalBytes: AppConfig.contentPayloadDiskCacheMaxBytes)
    }
}

final class ContentSyncManager {
    static let shared = ContentSyncManager()

    private let database: ContentDatabaseProtocol
    private let versionManager: ContentVersionManager
    private let validator: ContentValidator
    private let cacheManager: ContentCacheManager
    private let payloadDownloader: ContentPayloadDownloading
    /// Тесты: принудительно как Release. По умолчанию `AppConfig.contentManifestRequireValidSignature`.
    private let requireManifestSignature: Bool
    /// Тесты: переопределение публичного ключа (Base64 raw P-256). По умолчанию `AppConfig.contentManifestSigningPublicKeyBase64`.
    private let manifestSigningPublicKeyBase64Override: String?

    init(
        database: ContentDatabaseProtocol = ContentDatabase.shared,
        versionManager: ContentVersionManager = .shared,
        validator: ContentValidator = .shared,
        cacheManager: ContentCacheManager = .shared,
        payloadDownloader: ContentPayloadDownloading = ContentDownloader.shared,
        requireManifestSignature: Bool? = nil,
        manifestSigningPublicKeyBase64: String? = nil
    ) {
        self.database = database
        self.versionManager = versionManager
        self.validator = validator
        self.cacheManager = cacheManager
        self.payloadDownloader = payloadDownloader
        self.requireManifestSignature = requireManifestSignature ?? AppConfig.contentManifestRequireValidSignature
        self.manifestSigningPublicKeyBase64Override = manifestSigningPublicKeyBase64
    }

    private var manifestSigningPublicKeyBase64: String {
        if let override = manifestSigningPublicKeyBase64Override { return override }
        return AppConfig.contentManifestSigningPublicKeyBase64
    }

    func sync(using apiClient: ContentAPIClient) async throws {
        guard OfflineManager.shared.isOnline else {
            throw ContentSyncError.networkUnavailable
        }

        let localManifest = await database.loadManifest()
        let localVersion = localManifest?.manifestVersion ?? 0

        if localVersion == 0 {
            let manifest = try await apiClient.fetchManifest()
            try await applyManifest(manifest)
            return
        }

        do {
            let patch = try await apiClient.fetchDelta(from: localVersion)
            if let localManifest {
                let merged = try versionManager.applyDelta(patch, to: localManifest)
                try await applyManifest(merged)
            }
        } catch {
            let manifest = try await apiClient.fetchManifest()
            try await applyManifest(manifest)
        }
    }

    func applyManifest(_ manifest: ContentManifest) async throws {
        guard validator.validateManifest(manifest) else {
            throw ContentSyncError.manifestValidationFailed
        }

        try validateManifestSignatureIfNeeded(manifest)

        let hydrated = await ContentManifestPayloadHydration.hydrate(
            manifest: manifest,
            downloader: payloadDownloader,
            validator: validator
        )

        let previousManifest = await database.loadManifest()
        let previousVersion = versionManager.currentVersion

        do {
            try versionManager.updateVersion(to: hydrated.manifestVersion)
            try await database.saveManifest(hydrated)
            await cacheManager.cacheManifest(hydrated)
        } catch {
            versionManager.restoreStoredVersion(previousVersion)
            if let previousManifest {
                try? await database.saveManifest(previousManifest)
                await cacheManager.cacheManifest(previousManifest)
            }
            throw error
        }
    }

    private func validateManifestSignatureIfNeeded(_ manifest: ContentManifest) throws {
        guard requireManifestSignature else { return }

        let sig = manifest.signature?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard !sig.isEmpty else {
            throw ContentSyncError.manifestSignatureMissing
        }

        let pub = manifestSigningPublicKeyBase64.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !pub.isEmpty else {
            throw ContentSyncError.manifestSigningKeyMissing
        }

        let payload = try ContentManifestSigning.canonicalSigningData(for: manifest)
        guard validator.verifySignature(payload: payload, signatureBase64: sig, publicKeyBase64: pub) else {
            throw ContentSyncError.manifestSignatureInvalid
        }
    }
}
