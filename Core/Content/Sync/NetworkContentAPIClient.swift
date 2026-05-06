import Foundation

@MainActor
final class NetworkContentAPIClient: ContentAPIClient {
    static let shared = NetworkContentAPIClient()

    private let networkManager: NetworkManager
    private let maxAttempts = 3

    private init(networkManager: NetworkManager? = nil) {
        self.networkManager = networkManager ?? APIService.shared.networkManager
    }

    func fetchManifest() async throws -> ContentManifest {
        do {
            let dto: ManifestContractDTO = try await get(endpoint: AppConfig.Endpoint.contentManifest)
            return dto.toDomain()
        } catch {
            throw mapError(error)
        }
    }

    func fetchDelta(from version: Int) async throws -> ContentDeltaPatch {
        do {
            let dto: DeltaContractDTO = try await get(
                endpoint: AppConfig.Endpoint.contentDelta,
                queryParams: ["fromVersion": String(version)]
            )
            return dto.toDomain()
        } catch {
            throw mapError(error)
        }
    }

    private func get<T: Decodable>(endpoint: String, queryParams: [String: String] = [:]) async throws -> T {
        var attempt = 0
        while true {
            do {
                return try await getOnce(endpoint: endpoint, queryParams: queryParams)
            } catch {
                attempt += 1
                let networkError = NetworkError.from(error)
                guard attempt < maxAttempts, networkError.isRetryable else {
                    throw error
                }
                let delayNs = UInt64(min(8.0, pow(2.0, Double(attempt))) * 1_000_000_000)
                try await Task.sleep(nanoseconds: delayNs)
            }
        }
    }

    private func getOnce<T: Decodable>(endpoint: String, queryParams: [String: String]) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            networkManager.get(
                endpoint: endpoint,
                queryParams: queryParams.isEmpty ? nil : queryParams,
                requiresAuth: false
            ) { (result: Result<T, Error>) in
                continuation.resume(with: result)
            }
        }
    }

    private func mapError(_ error: Error?) -> ContentSyncError {
        guard let error else {
            return .invalidServerPayload
        }
        let mapped = NetworkError.from(error)
        switch mapped {
        case .notFound:
            return .serverError(statusCode: 404)
        case .serviceUnavailable:
            return .serverError(statusCode: 503)
        default:
            return .invalidServerPayload
        }
    }
}

struct ManifestContractDTO: Decodable {
    let manifestVersion: Int
    let generatedAt: Date
    let minSupportedAppVersion: String
    let checksumSHA256: String
    let signature: String?
    let categories: [ContentCategory]
    let items: [ContentItem]

    enum CodingKeys: String, CodingKey {
        case manifest
        case manifestVersion = "manifest_version"
        case generatedAt = "generated_at"
        case minSupportedAppVersion = "min_supported_app_version"
        case checksumSHA256 = "checksum_sha256"
        case signature
        case categories
        case items
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        if let wrapped = try container.decodeIfPresent(ManifestContractDTO.self, forKey: .manifest) {
            self = wrapped
            return
        }

        manifestVersion = try container.decode(Int.self, forKey: .manifestVersion)
        minSupportedAppVersion = try container.decodeIfPresent(String.self, forKey: .minSupportedAppVersion) ?? "1.0.0"
        checksumSHA256 = try container.decodeIfPresent(String.self, forKey: .checksumSHA256) ?? "missing-checksum"
        signature = try container.decodeIfPresent(String.self, forKey: .signature)
        categories = try container.decodeIfPresent([ContentCategory].self, forKey: .categories) ?? []
        items = try container.decodeIfPresent([ContentItem].self, forKey: .items) ?? []

        if let generatedString = try container.decodeIfPresent(String.self, forKey: .generatedAt),
           let parsedDate = ISO8601DateFormatter().date(from: generatedString) {
            generatedAt = parsedDate
        } else {
            generatedAt = Date()
        }
    }

    func toDomain() -> ContentManifest {
        ContentManifest(
            manifestVersion: manifestVersion,
            generatedAt: generatedAt,
            minSupportedAppVersion: minSupportedAppVersion,
            checksumSHA256: checksumSHA256,
            signature: signature,
            categories: categories,
            items: items
        )
    }
}

struct DeltaContractDTO: Decodable {
    let fromVersion: Int
    let toVersion: Int
    let added: [ContentItem]
    let updated: [ContentItem]
    let removedIds: [String]
    let checksumSHA256: String

    enum CodingKeys: String, CodingKey {
        case delta
        case fromVersion = "from_version"
        case toVersion = "to_version"
        case added
        case updated
        case removedIds = "removed_ids"
        case checksumSHA256 = "checksum_sha256"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        if let wrapped = try container.decodeIfPresent(DeltaContractDTO.self, forKey: .delta) {
            self = wrapped
            return
        }

        fromVersion = try container.decode(Int.self, forKey: .fromVersion)
        toVersion = try container.decode(Int.self, forKey: .toVersion)
        added = try container.decodeIfPresent([ContentItem].self, forKey: .added) ?? []
        updated = try container.decodeIfPresent([ContentItem].self, forKey: .updated) ?? []
        removedIds = try container.decodeIfPresent([String].self, forKey: .removedIds) ?? []
        checksumSHA256 = try container.decodeIfPresent(String.self, forKey: .checksumSHA256) ?? "missing-checksum"
    }

    func toDomain() -> ContentDeltaPatch {
        ContentDeltaPatch(
            fromVersion: fromVersion,
            toVersion: toVersion,
            added: added,
            updated: updated,
            removedIds: removedIds,
            checksumSHA256: checksumSHA256
        )
    }
}

