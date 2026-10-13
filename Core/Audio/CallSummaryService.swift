import Foundation

/// Local heuristic structured summary for call notes (no cloud by default).
enum CallSummaryService {
    static func summarize(goal: String, transcriptOrNote: String) -> CallSessionSummary {
        let raw = [goal, transcriptOrNote]
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .joined(separator: "\n")

        guard !raw.isEmpty else { return .empty }

        let lower = raw.lowercased()
        var risks = ""
        let riskHints = ["пароль", "код из смс", "перевод", "банк", "карт", "password", "wire", "gift card"]
        if riskHints.contains(where: { lower.contains($0) }) {
            risks = String(raw.prefix(180))
        }

        var amounts = ""
        if let match = raw.range(of: #"(\d[\d\s]{0,12}(?:₽|руб|рублей|\$|€|%))"#, options: .regularExpression) {
            amounts = String(raw[match])
        }

        let free = String(raw.prefix(500))
        let agreements = goal.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? String(raw.prefix(200))
            : goal.trimmingCharacters(in: .whitespacesAndNewlines)

        return CallSessionSummary(
            agreements: agreements,
            amounts: amounts,
            nextStep: "",
            risks: risks,
            freeText: free
        )
    }
}
