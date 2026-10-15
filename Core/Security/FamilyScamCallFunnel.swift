import Foundation

/// P0 funnel + P1-1 local crumbs for Family incident feed.
enum FamilyScamCallFunnel {
    enum Step: String {
        case open
        case alertSent = "alert_sent"
        case calm
        case checklistSeen = "checklist_seen"
        case callDirectoryCTA = "call_directory_cta"
        case callDirectoryOpened = "call_directory_opened"
        case hubManualEntry = "hub_manual_entry"
        case mainParentsCTA = "main_parents_cta"
        case secondHandSetup = "second_hand_setup"
    }

    private static let localEventsKey = "fvp_family_local_incidents_v1"
    private static let maxLocal = 12

    static func log(_ step: Step, source: String = "") {
        let src = source.isEmpty ? "" : " source=\(source)"
        print("📊 FVP_SCAM_FUNNEL step=\(step.rawValue)\(src)")
        switch step {
        case .alertSent:
            persistLocal(type: "scam_call", source: source.isEmpty ? "alert" : source)
        case .secondHandSetup:
            persistLocal(type: "second_hand", source: source.isEmpty ? "setup" : source)
        default:
            break
        }
    }

    /// Local crumbs when API is empty or offline (same device / parent phone).
    static func localIncidentSnapshots() -> [[String: String]] {
        guard let data = UserDefaults.standard.data(forKey: localEventsKey),
              let rows = try? JSONDecoder().decode([[String: String]].self, from: data) else {
            return []
        }
        return rows
    }

    private static func persistLocal(type: String, source: String) {
        var rows = localIncidentSnapshots()
        let iso = ISO8601DateFormatter().string(from: Date())
        rows.insert(
            [
                "id": "local-\(type)-\(iso)",
                "type": type,
                "source": source,
                "created_at": iso
            ],
            at: 0
        )
        if rows.count > maxLocal {
            rows = Array(rows.prefix(maxLocal))
        }
        if let data = try? JSONEncoder().encode(rows) {
            UserDefaults.standard.set(data, forKey: localEventsKey)
        }
    }
}
