import Foundation

/// P1.5 — MemoRecap: transcript → 5 bullets + what to tell family.
struct VoiceDayRecapResult: Equatable, Identifiable {
    let id: UUID
    var bullets: [String]
    var tellFamily: String
    var rawFallback: String?

    init(id: UUID = UUID(), bullets: [String], tellFamily: String, rawFallback: String? = nil) {
        self.id = id
        self.bullets = bullets
        self.tellFamily = tellFamily
        self.rawFallback = rawFallback
    }
}

enum VoiceDayRecapService {
    static let pendingOpenKey = "voice_day_recap_pending_open"
    static let lastSavedKey = "voice_day_recap_last_v1"
    static let familyChatDraftKey = "family_chat_draft_from_day_recap"

    static func markPendingOpen(defaults: UserDefaults = .standard) {
        defaults.set(true, forKey: pendingOpenKey)
    }

    static func consumePendingOpen(defaults: UserDefaults = .standard) -> Bool {
        let flag = defaults.bool(forKey: pendingOpenKey)
        if flag { defaults.set(false, forKey: pendingOpenKey) }
        return flag
    }

    static func recap(transcript: String) async throws -> VoiceDayRecapResult {
        let text = transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return VoiceDayRecapResult(bullets: [], tellFamily: "", rawFallback: nil)
        }
        let prompt = """
        DAY_RECAP_JSON_ONLY. Respond with one JSON object, no markdown:
        {"bullets":["..."],"tell_family":"..."}
        Exactly up to 5 short bullets summarizing the day note.
        tell_family = one short sentence the user could say to family.
        Language = language of input.
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
        if let parsed = parse(response.response) {
            _ = UnicornCareReward.grant(reason: .dayRecap, sourceId: "daily")
            saveLast(parsed)
            return parsed
        }
        return VoiceDayRecapResult(
            bullets: [],
            tellFamily: "",
            rawFallback: response.response.trimmingCharacters(in: .whitespacesAndNewlines)
        )
    }

    private static func parse(_ raw: String) -> VoiceDayRecapResult? {
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
        let bullets = (obj["bullets"] as? [Any])?
            .compactMap { ($0 as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty } ?? []
        let tell = (obj["tell_family"] as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        guard !bullets.isEmpty || !tell.isEmpty else { return nil }
        return VoiceDayRecapResult(bullets: Array(bullets.prefix(5)), tellFamily: tell)
    }

    private static func saveLast(_ result: VoiceDayRecapResult, defaults: UserDefaults = .standard) {
        let payload: [String: Any] = [
            "bullets": result.bullets,
            "tell_family": result.tellFamily,
            "saved_at": ISO8601DateFormatter().string(from: Date())
        ]
        if let data = try? JSONSerialization.data(withJSONObject: payload) {
            defaults.set(data, forKey: lastSavedKey)
        }
    }
}
