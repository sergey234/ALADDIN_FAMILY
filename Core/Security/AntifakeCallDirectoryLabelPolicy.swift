import Foundation

/// D-10 — relocalize server/default scam labels when user changes device locale.
enum AntifakeCallDirectoryLabelPolicy {
    private static let knownDefaultLabels: Set<String> = [
        "Возможный мошенник?",
        "Possible scam?"
    ]

    static func relocalizeIfKnownDefault(_ label: String, currentDefault: String) -> String {
        let trimmed = label.trimmingCharacters(in: .whitespacesAndNewlines)
        guard knownDefaultLabels.contains(trimmed) else { return label }
        return currentDefault
    }
}
