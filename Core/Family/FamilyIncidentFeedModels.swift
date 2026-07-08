import Foundation

// MARK: - fws-09 Family incident feed

enum FamilyIncidentType: String, Codable, Sendable {
    case antifakeAlert = "antifake_alert"
    case wellnessCrisis = "wellness_crisis"
    case bedtimeBreach = "bedtime_breach"
}

enum FamilyIncidentSeverity: String, Codable, Sendable {
    case low
    case medium
    case high
    case critical
}

struct FamilyIncidentItem: Codable, Equatable, Identifiable, Sendable {
    let id: String
    let incidentType: FamilyIncidentType
    let severity: FamilyIncidentSeverity
    let titleKey: String
    let playbookKey: String
    let memberUserId: Int
    let createdAt: String?
    let meta: [String: String]
    let playbookSteps: [String]

    enum CodingKeys: String, CodingKey {
        case id
        case incidentType = "incident_type"
        case severity
        case titleKey = "title_key"
        case playbookKey = "playbook_key"
        case memberUserId = "member_user_id"
        case createdAt = "created_at"
        case meta
        case playbookSteps = "playbook_steps"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        incidentType = try container.decode(FamilyIncidentType.self, forKey: .incidentType)
        severity = try container.decode(FamilyIncidentSeverity.self, forKey: .severity)
        titleKey = try container.decode(String.self, forKey: .titleKey)
        playbookKey = try container.decode(String.self, forKey: .playbookKey)
        memberUserId = try container.decode(Int.self, forKey: .memberUserId)
        createdAt = try container.decodeIfPresent(String.self, forKey: .createdAt)
        playbookSteps = try container.decodeIfPresent([String].self, forKey: .playbookSteps) ?? []
        if let dict = try? container.decode([String: String].self, forKey: .meta) {
            meta = dict
        } else if let anyDict = try? container.decode([String: LossyString].self, forKey: .meta) {
            meta = anyDict.mapValues(\.value)
        } else {
            meta = [:]
        }
    }
}

private struct LossyString: Decodable {
    let value: String

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let s = try? container.decode(String.self) {
            value = s
        } else if let i = try? container.decode(Int.self) {
            value = String(i)
        } else if let d = try? container.decode(Double.self) {
            value = String(d)
        } else if let b = try? container.decode(Bool.self) {
            value = b ? "true" : "false"
        } else {
            value = ""
        }
    }
}

struct FamilyIncidentFeedResponse: Codable, Equatable, Sendable {
    let ok: Bool
    let familyId: String?
    let shared: Bool
    let incidents: [FamilyIncidentItem]
    let typesPresent: [String]?
    let reason: String?

    enum CodingKeys: String, CodingKey {
        case ok
        case familyId = "family_id"
        case shared
        case incidents
        case typesPresent = "types_present"
        case reason
    }
}
