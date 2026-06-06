import Foundation

/// Three-step recall hints: image → letter → 3-choice (B14-T04).
enum MnemonicHintLadder {
    enum Level: Int, CaseIterable, Identifiable {
        case image = 0
        case letter = 1
        case threeChoice = 2

        var id: Int { rawValue }

        var localizationKey: String {
            switch self {
            case .image: return "child_mnemo_hint_ladder_step_image"
            case .letter: return "child_mnemo_hint_ladder_step_letter"
            case .threeChoice: return "child_mnemo_hint_ladder_step_choice"
            }
        }

        var next: Level? {
            Level(rawValue: rawValue + 1)
        }
    }

    static func firstLetter(from answer: String) -> String {
        let trimmed = answer.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let first = trimmed.first else { return "?" }
        return String(first).uppercased()
    }
}
