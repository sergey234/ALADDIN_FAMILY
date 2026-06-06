import Foundation

enum MnemonicStudyTechniqueMap {

    static func technique(for itemId: String) -> MnemonicTechnique {
        switch itemId {
        case "study.01": return .acronym
        case "study.02": return .chunking
        case "study.03": return .acronym
        case "study.04": return .storyLink
        case "study.05": return .memoryPalace
        case "study.06": return .framePeg
        case "study.07": return .acronym
        case "study.08": return .framePeg
        case "study.09": return .storyLink
        case "study.10": return .rhymePeg
        case "study.11": return .rhythmCode
        case "study.12": return .linkChain
        case "study.13": return .keyword
        case "study.14": return .framePeg
        case "study.15": return .framePeg
        case "study.16": return .acronym
        case "study.17": return .chunking
        case "study.18": return .chunking
        case "study.19": return .keyword
        case "study.20": return .rhymePeg
        case "study.21": return .memoryPalace
        case "study.22": return .acronym
        case "study.23": return .storyLink
        case "study.24": return .spacedReview
        case "study.25": return .memoryPalace
        case "study.26": return .spacedReview
        case "study.27": return .linkChain
        case "study.28": return .spacedReview
        case "study.29": return .rhymePeg
        case "study.30": return .memoryPalace
        default: return .memoryPalace
        }
    }

    static func pickerOptions(for itemId: String) -> [MnemonicTechnique] {
        let recommended = technique(for: itemId)
        var options: [MnemonicTechnique] = [recommended]
        for candidate in MnemonicTechnique.allCases where candidate != .spacedReview {
            if options.count >= 3 { break }
            if candidate != recommended { options.append(candidate) }
        }
        return options.shuffled()
    }

    static func pickerContextKey(for itemId: String) -> String {
        switch itemId {
        case "study.01", "study.03", "study.10", "study.19":
            return "child_mnemo_technique_picker_context_vocab"
        case "study.02", "study.07", "study.08", "study.17", "study.18":
            return "child_mnemo_technique_picker_context_formula"
        case "study.04", "study.05", "study.06", "study.15":
            return "child_mnemo_technique_picker_context_dates"
        default:
            return "child_mnemo_technique_picker_context_general"
        }
    }

    static func journeyStop(for itemId: String) -> Int {
        if itemId.hasPrefix("study."),
           let num = Int(itemId.replacingOccurrences(of: "study.", with: "")),
           (1...MnemonicJourneyPath.stopCount).contains(num) {
            return num
        }
        if itemId.hasPrefix("games.") || itemId.hasPrefix("songs.") {
            return MnemonicCurriculumSpine.shared.nextAvailableStop(for: itemId)
        }
        return min(MnemonicJourneyPath.stopCount, max(1, abs(itemId.hashValue) % MnemonicJourneyPath.stopCount + 1))
    }
}
