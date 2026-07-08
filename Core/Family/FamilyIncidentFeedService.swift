import Foundation

/// fws-09 — parent incident feed (antifake + crisis + bedtime).
@MainActor
final class FamilyIncidentFeedService: ObservableObject {
    static let shared = FamilyIncidentFeedService()

    @Published private(set) var incidents: [FamilyIncidentItem] = []
    @Published private(set) var isLoading = false
    @Published private(set) var lastError: String?

    private init() {}

    func refresh(members: [FamilyMemberData]) async {
        guard FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members) else {
            incidents = []
            return
        }
        isLoading = true
        lastError = nil
        defer { isLoading = false }

        let result: Result<FamilyIncidentFeedResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilyIncidents { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let payload):
            incidents = payload.incidents
        case .failure:
            lastError = "family_incident_feed_load_failed"
        }
    }
}
