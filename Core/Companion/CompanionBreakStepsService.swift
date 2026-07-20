import Foundation

/// P1.4 — Goblin-lite: goal → 3–7 micro-steps (not a PM tool).
struct CompanionBreakStepsPlan: Equatable, Identifiable {
    let id: UUID
    var goal: String
    var steps: [String]

    init(id: UUID = UUID(), goal: String, steps: [String]) {
        self.id = id
        self.goal = goal
        self.steps = steps
    }
}

enum CompanionBreakStepsService {
    static let draftKey = "companion_break_steps_draft"
    static let donePrefix = "companion_break_step_done_"

    static func consumeDraft(defaults: UserDefaults = .standard) -> String? {
        let raw = defaults.string(forKey: draftKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard let raw, !raw.isEmpty else { return nil }
        defaults.removeObject(forKey: draftKey)
        return raw
    }

    /// Water habit must not use Goblin step XP (P1.4b).
    static func isWaterHabitGoal(_ text: String) -> Bool {
        let lower = text.lowercased()
        return lower.contains("water")
            || lower.contains("вод")
            || lower.contains("пить")
            || lower.contains("hydrate")
    }

    static func breakIntoSteps(goal: String) async throws -> CompanionBreakStepsPlan {
        let text = goal.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return CompanionBreakStepsPlan(goal: "", steps: [])
        }
        let prompt = """
        BREAK_STEPS_JSON_ONLY. Respond with one JSON object, no markdown:
        {"steps":["..."]}
        Produce 3 to 7 short micro-steps for the goal. Language of steps = language of goal.
        Goal:
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
        let steps = parseSteps(response.response)
        if steps.isEmpty {
            return CompanionBreakStepsPlan(
                goal: text,
                steps: fallbackSteps(from: text)
            )
        }
        return CompanionBreakStepsPlan(goal: text, steps: Array(steps.prefix(7)))
    }

    private static func parseSteps(_ raw: String) -> [String] {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let jsonSlice: String
        if let start = trimmed.firstIndex(of: "{"), let end = trimmed.lastIndex(of: "}") {
            jsonSlice = String(trimmed[start...end])
        } else {
            jsonSlice = trimmed
        }
        guard let data = jsonSlice.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let arr = obj["steps"] as? [Any] else {
            return []
        }
        return arr.compactMap { ($0 as? String)?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    private static func fallbackSteps(from goal: String) -> [String] {
        let chunks = goal
            .components(separatedBy: CharacterSet(charactersIn: ".;\n"))
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        if chunks.count >= 3 {
            return Array(chunks.prefix(7))
        }
        return [
            String(goal.prefix(80)),
            "Сделать первый маленький шаг",
            "Отметить, что получилось"
        ]
    }

    static func markStepDone(planId: UUID, index: Int, goal: String) -> UnicornCareReward.GrantResult? {
        guard !isWaterHabitGoal(goal) else { return nil }
        let source = "\(planId.uuidString)_\(index)"
        return UnicornCareReward.grant(reason: .goblinStep, sourceId: source)
    }
}
