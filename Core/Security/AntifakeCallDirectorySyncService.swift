import CallKit
import Foundation

enum AntifakeCallDirectorySyncFailure: Equatable {
    case notFound
    case unauthorized
    case premiumRequired
    case other(String)
}

enum AntifakeCallDirectorySyncOutcome: Equatable {
    case success(syncedCount: Int, updatedAt: Date)
    case failure(AntifakeCallDirectorySyncFailure)
}

/// Fetches scam numbers from API and reloads Call Directory extension (af-4-09).
@MainActor
enum AntifakeCallDirectorySyncService {

    private static let isoFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()

    static func syncFromServer(apiService: APIService? = nil) async -> AntifakeCallDirectorySyncOutcome {
        let service = apiService ?? APIService.shared
        let defaultLabel = LocalizationManager.shared.localized("antifake_call_directory_identification_label")
        let voiceLabel = LocalizationManager.shared.localized("antifake_call_directory_voice_label")
        let existing = AntifakeCallDirectoryStore.load()
        let sinceQuery = deltaSinceParameter(from: existing.updatedAt)

        let result: Result<AntifakeCallDirectoryAPIResponse, Error> = await withCheckedContinuation { continuation in
            service.getAntifakeCallDirectory(since: sinceQuery) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            let identified = payload.identified.compactMap { item -> AntifakeCallDirectoryIdentifiedEntry? in
                guard let phone = AntifakeCallDirectoryStore.parsePhoneNumber(item.phone) else { return nil }
                let rawLabel = item.label
                let label = AntifakeCallDirectoryLabelPolicy.resolvedLabel(
                    rawLabel,
                    defaultLabel: defaultLabel,
                    voiceLabel: voiceLabel
                )
                return AntifakeCallDirectoryIdentifiedEntry(
                    phoneNumber: phone,
                    label: label
                )
            }
            let blocked = payload.blocked.compactMap { AntifakeCallDirectoryStore.parsePhoneNumber($0) }
            let serverUpdatedAt = parseServerUpdatedAt(payload.updatedAt)

            let snapshot: AntifakeCallDirectorySnapshot
            if sinceQuery == nil {
                snapshot = AntifakeCallDirectorySnapshot(
                    identifiedNumbers: identified,
                    blockedNumbers: blocked,
                    updatedAt: serverUpdatedAt
                )
            } else {
                snapshot = AntifakeCallDirectoryStore.mergeDelta(
                    existing: existing,
                    identified: identified,
                    blocked: blocked,
                    serverUpdatedAt: serverUpdatedAt
                )
            }

            AntifakeCallDirectoryStore.saveReplacing(snapshot)
            if let reloadError = await reloadExtension() {
                _ = AntifakeCallDirectoryStore.restoreBackupSnapshot()
                return .failure(.other(reloadError))
            }
            let syncedCount = payload.totalCount ?? (snapshot.identifiedNumbers.count + snapshot.blockedNumbers.count)
            return .success(syncedCount: syncedCount, updatedAt: serverUpdatedAt)
        case .failure(let error):
            return .failure(mapFailure(error))
        }
    }

    static func reloadExtension() async -> String? {
        await withCheckedContinuation { continuation in
            CXCallDirectoryManager.sharedInstance.reloadExtension(
                withIdentifier: AntifakeCallDirectoryConstants.extensionBundleId
            ) { error in
                continuation.resume(returning: error?.localizedDescription)
            }
        }
    }

    static func extensionStatus() async -> CXCallDirectoryManager.EnabledStatus {
        await withCheckedContinuation { continuation in
            CXCallDirectoryManager.sharedInstance.getEnabledStatusForExtension(
                withIdentifier: AntifakeCallDirectoryConstants.extensionBundleId
            ) { status, _ in
                continuation.resume(returning: status)
            }
        }
    }

    private static func deltaSinceParameter(from lastUpdated: Date) -> String? {
        guard lastUpdated > Date(timeIntervalSince1970: 1) else { return nil }
        return isoFormatter.string(from: lastUpdated)
    }

    private static func parseServerUpdatedAt(_ raw: String?) -> Date {
        guard let raw, !raw.isEmpty else { return Date() }
        if let parsed = isoFormatter.date(from: raw) {
            return parsed
        }
        let fallback = ISO8601DateFormatter()
        fallback.formatOptions = [.withInternetDateTime]
        return fallback.date(from: raw) ?? Date()
    }

    private static func mapFailure(_ error: Error) -> AntifakeCallDirectorySyncFailure {
        let networkError = NetworkError.from(error)
        switch networkError {
        case .notFound:
            return .notFound
        case .unauthorized:
            return .unauthorized
        case .forbidden(let message):
            if message?.lowercased().contains("premium") == true {
                return .premiumRequired
            }
            return .other(message ?? error.localizedDescription)
        default:
            return .other(error.localizedDescription)
        }
    }
}

struct AntifakeCallDirectoryAPIResponse: Codable {
    let identified: [AntifakeCallDirectoryAPIIdentified]
    let blocked: [String]
    let totalCount: Int?
    let updatedAt: String?
    let truncated: Bool?
    let maxEntries: Int?

    enum CodingKeys: String, CodingKey {
        case identified
        case blocked
        case totalCount = "total_count"
        case updatedAt = "updated_at"
        case truncated
        case maxEntries = "max_entries"
    }
}

struct AntifakeCallDirectoryAPIIdentified: Codable {
    let phone: String
    let label: String?
}
