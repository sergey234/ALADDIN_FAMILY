import Foundation

/// P0.2 — Happens-lite: transcript → structured bullets (fixed prompt, not a Notion clone).
struct VoiceNotesStructureResult: Equatable, Identifiable {
    let id: UUID
    var tasks: [String]
    var people: [String]
    var urgent: [String]
    var listCandidates: [String]
    var rawFallback: String?

    init(
        id: UUID = UUID(),
        tasks: [String],
        people: [String],
        urgent: [String],
        listCandidates: [String],
        rawFallback: String?
    ) {
        self.id = id
        self.tasks = tasks
        self.people = people
        self.urgent = urgent
        self.listCandidates = listCandidates
        self.rawFallback = rawFallback
    }
}

enum VoiceNotesStructureService {
    static func structure(transcript: String) async throws -> VoiceNotesStructureResult {
        let text = transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return VoiceNotesStructureResult(tasks: [], people: [], urgent: [], listCandidates: [], rawFallback: nil)
        }

        let prompt = """
        STRUCTURE_JSON_ONLY. Respond with one JSON object, no markdown, keys:
        {"tasks":[],"people":[],"urgent":[],"list_candidates":[]}
        Language of values = language of input.
        Input:
        \(text)
        """

        let characterId = UserDefaults.standard.string(forKey: "companion_selected_character_id") ?? "aladdin"
        let response = try await CompanionAPIService.shared.sendChat(
            message: prompt,
            characterId: characterId,
            sessionId: nil,
            inputMode: "text",
            chatMode: "fast",
            wellnessPillar: nil,
            guideMode: nil
        )
        if let parsed = parseJSON(response.response) {
            _ = UnicornCareReward.grant(reason: .voiceStructure, sourceId: String(text.prefix(32)))
            return parsed
        }
        return VoiceNotesStructureResult(
            tasks: [],
            people: [],
            urgent: [],
            listCandidates: [],
            rawFallback: response.response.trimmingCharacters(in: .whitespacesAndNewlines)
        )
    }

    private static func parseJSON(_ raw: String) -> VoiceNotesStructureResult? {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let jsonSlice: String
        if let start = trimmed.firstIndex(of: "{"), let end = trimmed.lastIndex(of: "}") {
            jsonSlice = String(trimmed[start...end])
        } else {
            jsonSlice = trimmed
        }
        guard let data = jsonSlice.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        func arr(_ key: String) -> [String] {
            (obj[key] as? [Any])?.compactMap { ($0 as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty } ?? []
        }
        return VoiceNotesStructureResult(
            tasks: arr("tasks"),
            people: arr("people"),
            urgent: arr("urgent"),
            listCandidates: arr("list_candidates"),
            rawFallback: nil
        )
    }
}
