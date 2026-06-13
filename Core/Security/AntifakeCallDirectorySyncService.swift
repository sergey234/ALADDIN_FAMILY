import CallKit
import Foundation

/// Fetches scam numbers from API and reloads Call Directory extension (af-4-09).
@MainActor
enum AntifakeCallDirectorySyncService {

    static func syncFromServer(apiService: APIService? = nil) async -> String? {
        let service = apiService ?? APIService.shared
        let result: Result<AntifakeCallDirectoryAPIResponse, Error> = await withCheckedContinuation { continuation in
            service.getAntifakeCallDirectory { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            let identified = payload.identified.compactMap { item -> AntifakeCallDirectoryIdentifiedEntry? in
                guard let phone = AntifakeCallDirectoryStore.parsePhoneNumber(item.phone) else { return nil }
                return AntifakeCallDirectoryIdentifiedEntry(
                    phoneNumber: phone,
                    label: item.label ?? AntifakeCallDirectoryConstants.identificationLabel
                )
            }
            let blocked = payload.blocked.compactMap { AntifakeCallDirectoryStore.parsePhoneNumber($0) }
            AntifakeCallDirectoryStore.save(
                AntifakeCallDirectorySnapshot(
                    identifiedNumbers: identified,
                    blockedNumbers: blocked,
                    updatedAt: Date()
                )
            )
            return await reloadExtension()
        case .failure(let error):
            return error.localizedDescription
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
}

struct AntifakeCallDirectoryAPIResponse: Codable {
    let identified: [AntifakeCallDirectoryAPIIdentified]
    let blocked: [String]

    enum CodingKeys: String, CodingKey {
        case identified
        case blocked
    }
}

struct AntifakeCallDirectoryAPIIdentified: Codable {
    let phone: String
    let label: String?
}
