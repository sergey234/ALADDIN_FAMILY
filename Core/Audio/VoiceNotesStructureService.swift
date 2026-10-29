import Foundation

/// P0.2 — Happens-lite: transcript → structured bullets (fixed prompt, not a Notion clone).
struct VoiceNotesStructureResult: Equatable, Identifiable {
    let id: UUID
    var tasks: [String]
    var people: [String]
    var urgent: [String]
    var listCandidates: [String]
    var polite: String
    var rawFallback: String?

    init(
        id: UUID = UUID(),
        tasks: [String],
        people: [String],
        urgent: [String],
        listCandidates: [String],
        polite: String = "",
        rawFallback: String?
    ) {
        self.id = id
        self.tasks = tasks
        self.people = people
        self.urgent = urgent
        self.listCandidates = listCandidates
        self.polite = polite
        self.rawFallback = rawFallback
    }
}

enum VoiceNotesStructureService {
    static func structure(transcript: String) async throws -> VoiceNotesStructureResult {
        let text = transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return VoiceNotesStructureResult(tasks: [], people: [], urgent: [], listCandidates: [], polite: "", rawFallback: nil)
        }

        let prompt = """
        STRUCTURE_JSON_ONLY. Respond with one JSON object, no markdown, keys:
        {"tasks":[],"people":[],"urgent":[],"list_candidates":[],"polite":""}
        Language of values = language of input.
        Use only facts that are written in the input. If a fact is not there, leave the list empty and polite empty.
        polite is one short kind sentence for the family, or empty.
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
        if let parsed = parseJSON(response.response, source: text) {
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

    static func keepGrounded(_ items: [String], source: String) -> [String] {
        let sourceWords = Set(VoiceNotesTextCleanup.words(source).map(VoiceNotesTextCleanup.normalize).filter { $0.count > 3 })
        return items.filter { item in
            let words = VoiceNotesTextCleanup.words(item).map(VoiceNotesTextCleanup.normalize).filter { $0.count > 3 }
            guard !words.isEmpty else { return false }
            return words.contains { sourceWords.contains($0) }
        }
    }

    private static func parseJSON(_ raw: String, source: String) -> VoiceNotesStructureResult? {
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
        let polite = (obj["polite"] as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let groundedPolite = keepGrounded(polite.isEmpty ? [] : [polite], source: source).first ?? ""
        return VoiceNotesStructureResult(
            tasks: keepGrounded(arr("tasks"), source: source),
            people: keepGrounded(arr("people"), source: source),
            urgent: keepGrounded(arr("urgent"), source: source),
            listCandidates: keepGrounded(arr("list_candidates"), source: source),
            polite: groundedPolite,
            rawFallback: nil
        )
    }
}
