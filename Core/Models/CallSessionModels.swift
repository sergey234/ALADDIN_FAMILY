import Foundation

/// Structured call memory card (local-first). Not carrier line recording.
struct CallSessionSummary: Codable, Equatable {
    var agreements: String
    var amounts: String
    var nextStep: String
    var risks: String
    var freeText: String

    static let empty = CallSessionSummary(
        agreements: "",
        amounts: "",
        nextStep: "",
        risks: "",
        freeText: ""
    )

    var isEmpty: Bool {
        [agreements, amounts, nextStep, risks, freeText]
            .allSatisfy { $0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    var previewLine: String {
        let parts = [agreements, nextStep, freeText]
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        return parts.first ?? ""
    }
}

enum CallSessionMode: String, Codable {
    case prepOnly
    case micRecord
    case postOnly
    case antifakeOnly
}

enum CallSessionSource: String, Codable {
    case userPrep
    case postCallPush
    case importFile
    case callAssistant
}

struct CallSession: Identifiable, Codable, Equatable {
    let id: UUID
    var createdAt: Date
    var endedAt: Date?
    var goal: String
    var mode: CallSessionMode
    var source: CallSessionSource
    var audioPath: String
    var transcript: String
    var summary: CallSessionSummary
    var antifakeCheckId: String?
    var consentVersion: String
    var recordInterrupted: Bool

    init(
        id: UUID = UUID(),
        createdAt: Date = Date(),
        endedAt: Date? = nil,
        goal: String = "",
        mode: CallSessionMode = .postOnly,
        source: CallSessionSource = .userPrep,
        audioPath: String = "",
        transcript: String = "",
        summary: CallSessionSummary = .empty,
        antifakeCheckId: String? = nil,
        consentVersion: String = CallConsentPolicy.currentVersion,
        recordInterrupted: Bool = false
    ) {
        self.id = id
        self.createdAt = createdAt
        self.endedAt = endedAt
        self.goal = goal
        self.mode = mode
        self.source = source
        self.audioPath = audioPath
        self.transcript = transcript
        self.summary = summary
        self.antifakeCheckId = antifakeCheckId
        self.consentVersion = consentVersion
        self.recordInterrupted = recordInterrupted
    }
}

enum CallConsentPolicy {
    static let currentVersion = "calls_memory_v1_2026-10-13"
    static let userDefaultsKey = "calls_memory_consent_version"

    static var hasAcceptedCurrent: Bool {
        UserDefaults.standard.string(forKey: userDefaultsKey) == currentVersion
    }

    static func acceptCurrent() {
        UserDefaults.standard.set(currentVersion, forKey: userDefaultsKey)
    }
}
