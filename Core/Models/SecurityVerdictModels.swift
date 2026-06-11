import Foundation

// MARK: - Unified security check contract (B2-00b / GATE-D antifake)

/// Backend verdict values for antifake and explicit security agents.
enum SecurityVerdictKind: String, Codable, CaseIterable, Sendable {
    case likelyFake = "likely_fake"
    case uncertain = "uncertain"
    case likelyReal = "likely_real"
}

enum AntifakeJobStatus: String, Codable, Sendable {
    case queued
    case processing
    case completed
    case failed
}

enum SecurityVerdictValidationError: Error, Equatable {
    case invalidVerdict(String?)
    case mockSourceRejected(String)
    case emptyMockEnvelope
}

/// Canonical L3 response for `/api/antifake/check/*` and job poll (docs/IOS_EXPLICIT_API_MATRIX.md).
struct SecurityVerdict: Codable, Equatable, Sendable {
    let verdict: SecurityVerdictKind
    let confidence: Double
    let reasons: [String]
    let source: String
    let agent: String?
    let jobId: String?
    let checkedAt: Date?
    let premiumRequired: Bool
    let status: AntifakeJobStatus?

    enum CodingKeys: String, CodingKey {
        case verdict
        case confidence
        case reasons
        case source
        case agent
        case jobId = "job_id"
        case checkedAt = "checked_at"
        case premiumRequired = "premium_required"
        case status
    }

    init(
        verdict: SecurityVerdictKind,
        confidence: Double,
        reasons: [String],
        source: String,
        agent: String? = nil,
        jobId: String? = nil,
        checkedAt: Date? = nil,
        premiumRequired: Bool = false,
        status: AntifakeJobStatus? = nil
    ) {
        self.verdict = verdict
        self.confidence = confidence
        self.reasons = reasons
        self.source = source
        self.agent = agent
        self.jobId = jobId
        self.checkedAt = checkedAt
        self.premiumRequired = premiumRequired
        self.status = status
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        verdict = try container.decode(SecurityVerdictKind.self, forKey: .verdict)
        confidence = try container.decodeIfPresent(Double.self, forKey: .confidence) ?? 0
        reasons = try container.decodeIfPresent([String].self, forKey: .reasons) ?? []
        source = try container.decodeIfPresent(String.self, forKey: .source) ?? ""
        agent = try container.decodeIfPresent(String.self, forKey: .agent)
        jobId = try container.decodeIfPresent(String.self, forKey: .jobId)
        premiumRequired = try container.decodeIfPresent(Bool.self, forKey: .premiumRequired) ?? false
        status = try container.decodeIfPresent(AntifakeJobStatus.self, forKey: .status)
        if let iso = try container.decodeIfPresent(String.self, forKey: .checkedAt) {
            checkedAt = SecurityVerdictParsers.iso8601.date(from: iso)
        } else {
            checkedAt = nil
        }
    }

    /// Rejects mock / wildcard envelopes — prod policy (B-OPS-07, af-0-06).
    func validateForProduction() throws {
        let normalized = source.lowercased()
        if Self.mockSources.contains(normalized) {
            throw SecurityVerdictValidationError.mockSourceRejected(source)
        }
        if normalized.isEmpty, reasons.isEmpty, confidence == 0 {
            throw SecurityVerdictValidationError.emptyMockEnvelope
        }
        if SecurityVerdictKind(rawValue: verdict.rawValue) == nil {
            throw SecurityVerdictValidationError.invalidVerdict(verdict.rawValue)
        }
    }

    var isLikelyThreat: Bool {
        verdict == .likelyFake
    }

    private static let mockSources: Set<String> = [
        "sfm_mock",
        "mock",
        "sfm_stub",
        "sfm_fallback",
        "mock-real-protection",
        "mock_fallback",
    ]
}

/// Async enqueue response: POST check/audio|video|document|call → job_id.
struct AntifakeJobEnqueueResponse: Codable, Equatable, Sendable {
    let jobId: String
    let status: AntifakeJobStatus
    let verdict: SecurityVerdictKind?
    let confidence: Double?
    let source: String?

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case status
        case verdict
        case confidence
        case source
    }
}

enum AntifakeJobPollOutcome: Equatable, Sendable {
    case pending(AntifakeJobPendingResponse)
    case completed(SecurityVerdict)
}

enum AntifakeJobEnqueueResult: Equatable, Sendable {
    case enqueued(AntifakeJobEnqueueResponse)
    case completed(SecurityVerdict)
}

struct AntifakeJobPendingResponse: Codable, Equatable, Sendable {
    let jobId: String
    let status: AntifakeJobStatus
    let type: String?

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case status
        case type
    }
}

enum AntifakeMediaKind: String, Sendable {
    case audio
    case video
    case document
    case call

    var uploadEndpoint: String {
        switch self {
        case .audio: return AppConfig.Endpoint.antifakeCheckAudio
        case .video: return AppConfig.Endpoint.antifakeCheckVideo
        case .document: return AppConfig.Endpoint.antifakeCheckDocument
        case .call: return AppConfig.Endpoint.antifakeCallAnalyze
        }
    }
}

/// GET `/api/antifake/metrics` — per-user job stats (B2-12).
struct AntifakeMetricsResponse: Codable, Equatable, Sendable {
    let checksTotal: Int
    let fakeDetected: Int
    let latencyP95Ms: Int

    enum CodingKeys: String, CodingKey {
        case checksTotal = "checks_total"
        case fakeDetected = "fake_detected"
        case latencyP95Ms = "latency_p95_ms"
    }
}

enum SecurityVerdictParsers {
    static let iso8601: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()

    static func decodeVerdict(from data: Data) throws -> SecurityVerdict {
        let decoder = JSONDecoder()
        let verdict = try decoder.decode(SecurityVerdict.self, from: data)
        try verdict.validateForProduction()
        return verdict
    }

    static func decodeJobEnqueue(from data: Data) throws -> AntifakeJobEnqueueResponse {
        try JSONDecoder().decode(AntifakeJobEnqueueResponse.self, from: data)
    }

    static func decodeJobEnqueueResult(from data: Data) throws -> AntifakeJobEnqueueResult {
        if let verdict = try? decodeVerdict(from: data) {
            return .completed(verdict)
        }
        return .enqueued(try decodeJobEnqueue(from: data))
    }

    static func decodeJobPoll(from data: Data) throws -> AntifakeJobPollOutcome {
        if let verdict = try? decodeVerdict(from: data),
           verdict.status == .completed || !verdict.verdict.rawValue.isEmpty {
            return .completed(verdict)
        }
        let pending = try JSONDecoder().decode(AntifakeJobPendingResponse.self, from: data)
        return .pending(pending)
    }
}
