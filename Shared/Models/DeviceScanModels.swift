import Foundation

// MARK: - Device agent scan contract (B5 / GATE-H)

struct DeviceScanThreatItem: Codable, Equatable, Sendable, Identifiable {
    let id: String
    let name: String?
    let type: String?
    let severity: String?
    let description: String?
    let confidence: Double?

    init(
        id: String,
        name: String? = nil,
        type: String? = nil,
        severity: String? = nil,
        description: String? = nil,
        confidence: Double? = nil
    ) {
        self.id = id
        self.name = name
        self.type = type
        self.severity = severity
        self.description = description
        self.confidence = confidence
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        if let decodedId = try container.decodeIfPresent(String.self, forKey: .id) {
            id = decodedId
        } else if let threatId = try container.decodeIfPresent(String.self, forKey: .threatId) {
            id = threatId
        } else {
            id = UUID().uuidString
        }
        name = try container.decodeIfPresent(String.self, forKey: .name)
        type = try container.decodeIfPresent(String.self, forKey: .type)
            ?? container.decodeIfPresent(String.self, forKey: .threatType)
        severity = try container.decodeIfPresent(String.self, forKey: .severity)
        description = try container.decodeIfPresent(String.self, forKey: .description)
        confidence = try container.decodeIfPresent(Double.self, forKey: .confidence)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encodeIfPresent(name, forKey: .name)
        try container.encodeIfPresent(type, forKey: .type)
        try container.encodeIfPresent(severity, forKey: .severity)
        try container.encodeIfPresent(description, forKey: .description)
        try container.encodeIfPresent(confidence, forKey: .confidence)
    }

    enum CodingKeys: String, CodingKey {
        case id
        case threatId = "threat_id"
        case name
        case type
        case threatType = "threat_type"
        case severity
        case description
        case confidence
    }
}

struct DeviceAgentScanResult: Codable, Equatable, Sendable {
    let scanId: String?
    let status: String?
    let scope: String?
    let securityScore: Int?
    let threatsFound: Int
    let threats: [DeviceScanThreatItem]
    let source: String
    let agent: String?
    let checkedAt: String?
    let clean: Bool?

    enum CodingKeys: String, CodingKey {
        case scanId = "scan_id"
        case status
        case scope
        case securityScore = "security_score"
        case threatsFound = "threats_found"
        case threats
        case source
        case agent
        case checkedAt = "checked_at"
        case clean
    }

    init(
        scanId: String? = nil,
        status: String? = nil,
        scope: String? = nil,
        securityScore: Int? = nil,
        threatsFound: Int = 0,
        threats: [DeviceScanThreatItem] = [],
        source: String,
        agent: String? = nil,
        checkedAt: String? = nil,
        clean: Bool? = nil
    ) {
        self.scanId = scanId
        self.status = status
        self.scope = scope
        self.securityScore = securityScore
        self.threatsFound = threatsFound
        self.threats = threats
        self.source = source
        self.agent = agent
        self.checkedAt = checkedAt
        self.clean = clean
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        scanId = try container.decodeIfPresent(String.self, forKey: .scanId)
        status = try container.decodeIfPresent(String.self, forKey: .status)
        scope = try container.decodeIfPresent(String.self, forKey: .scope)
        securityScore = try container.decodeIfPresent(Int.self, forKey: .securityScore)
        source = try container.decodeIfPresent(String.self, forKey: .source) ?? ""
        agent = try container.decodeIfPresent(String.self, forKey: .agent)
        checkedAt = try container.decodeIfPresent(String.self, forKey: .checkedAt)
        clean = try container.decodeIfPresent(Bool.self, forKey: .clean)

        let explicitThreatsFound = try container.decodeIfPresent(Int.self, forKey: .threatsFound) ?? 0
        let decodedThreats = try container.decodeIfPresent([DeviceScanThreatItem].self, forKey: .threats) ?? []
        threats = decodedThreats
        if explicitThreatsFound == 0, !decodedThreats.isEmpty {
            threatsFound = decodedThreats.count
        } else {
            threatsFound = explicitThreatsFound
        }
    }

    func validateForProduction() throws {
        let normalized = source.lowercased()
        if DeviceScanSourceValidator.mockSources.contains(normalized) {
            throw SecurityVerdictValidationError.mockSourceRejected(source)
        }
        if normalized.isEmpty, threats.isEmpty, threatsFound == 0, securityScore == nil {
            throw SecurityVerdictValidationError.emptyMockEnvelope
        }
    }

    var isClean: Bool {
        if let clean { return clean }
        return threats.isEmpty && threatsFound == 0
    }
}

struct DeviceIncidentReportResult: Codable, Equatable, Sendable {
    let incidentId: String?
    let status: String?
    let source: String
    let message: String?

    enum CodingKeys: String, CodingKey {
        case incidentId = "incident_id"
        case status
        case source
        case message
        case error
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        incidentId = try container.decodeIfPresent(String.self, forKey: .incidentId)
        status = try container.decodeIfPresent(String.self, forKey: .status)
        source = try container.decodeIfPresent(String.self, forKey: .source) ?? ""
        message = try container.decodeIfPresent(String.self, forKey: .message)
            ?? container.decodeIfPresent(String.self, forKey: .error)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encodeIfPresent(incidentId, forKey: .incidentId)
        try container.encodeIfPresent(status, forKey: .status)
        try container.encode(source, forKey: .source)
        try container.encodeIfPresent(message, forKey: .message)
    }

    func validateForProduction() throws {
        let normalized = source.lowercased()
        if DeviceScanSourceValidator.mockSources.contains(normalized) {
            throw SecurityVerdictValidationError.mockSourceRejected(source)
        }
        if normalized.isEmpty, incidentId == nil, status == nil {
            throw SecurityVerdictValidationError.emptyMockEnvelope
        }
    }
}

enum DeviceScanSourceValidator {
    static let mockSources: Set<String> = [
        "sfm_mock",
        "mock",
        "sfm_stub",
        "sfm_fallback",
        "mock-real-protection",
        "mock_fallback",
    ]

    static let eicarPayload = Data("EICAR-STANDARD-ANTIVIRUS-TEST-FILE".utf8)
}

enum IoTHomeIdResolver {
    private static let defaultsKey = "aladdin_iot_home_id"

    static var current: String {
        UserDefaults.standard.string(forKey: defaultsKey) ?? "home_default"
    }

    static func save(_ homeId: String) {
        UserDefaults.standard.set(homeId, forKey: defaultsKey)
    }
}
