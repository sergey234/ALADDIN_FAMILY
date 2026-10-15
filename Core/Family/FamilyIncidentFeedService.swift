import Foundation

/// fws-09 / fvp-p1-1 — parent incident feed (API + local scam/second-hand crumbs).
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

        var merged: [FamilyIncidentItem] = []
        switch result {
        case .success(let payload):
            merged = payload.incidents
        case .failure:
            lastError = "family_incident_feed_load_failed"
        }

        merged = mergeLocalCrumbs(into: merged)
        merged.sort { ($0.createdAt ?? "") > ($1.createdAt ?? "") }
        if merged.count > 40 {
            merged = Array(merged.prefix(40))
        }
        incidents = merged
    }

    private func mergeLocalCrumbs(into remote: [FamilyIncidentItem]) -> [FamilyIncidentItem] {
        var out = remote
        let remoteIds = Set(remote.map(\.id))
        for row in FamilyScamCallFunnel.localIncidentSnapshots() {
            guard let id = row["id"], !remoteIds.contains(id) else { continue }
            let typeRaw = row["type"] ?? "scam_call"
            let item: FamilyIncidentItem?
            switch typeRaw {
            case "second_hand":
                item = FamilyIncidentItem(
                    id: id,
                    incidentType: .secondHand,
                    severity: .medium,
                    titleKey: "family_incident_title_second_hand",
                    playbookKey: "family_incident_playbook_second_hand",
                    memberUserId: 0,
                    createdAt: row["created_at"],
                    meta: ["source": row["source"] ?? "local"],
                    playbookSteps: [
                        "family_incident_playbook_second_hand_step1",
                        "family_incident_playbook_second_hand_step2",
                        "family_incident_playbook_second_hand_step3"
                    ]
                )
            default:
                item = FamilyIncidentItem(
                    id: id,
                    incidentType: .scamCall,
                    severity: .high,
                    titleKey: "family_incident_title_scam",
                    playbookKey: "family_incident_playbook_scam",
                    memberUserId: 0,
                    createdAt: row["created_at"],
                    meta: ["source": row["source"] ?? "local"],
                    playbookSteps: [
                        "family_incident_playbook_scam_step1",
                        "family_incident_playbook_scam_step2",
                        "family_incident_playbook_scam_step3"
                    ]
                )
            }
            if let item {
                out.append(item)
            }
        }
        return out
    }
}
