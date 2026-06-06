import Foundation

enum MnemonicTechnique: String, CaseIterable, Identifiable, Codable {
    case rhymePeg
    case linkChain
    case memoryPalace
    case keyword
    case acronym
    case chunking
    case rhythmCode
    case framePeg
    case storyLink
    case spacedReview

    var id: String { rawValue }

    var localizationKey: String {
        switch self {
        case .rhymePeg: return "child_mnemo_technique_rhyme_peg"
        case .linkChain: return "child_mnemo_technique_link_chain"
        case .memoryPalace: return "child_mnemo_technique_memory_palace"
        case .keyword: return "child_mnemo_technique_keyword"
        case .acronym: return "child_mnemo_technique_acronym"
        case .chunking: return "child_mnemo_technique_chunking"
        case .rhythmCode: return "child_mnemo_technique_rhythm_code"
        case .framePeg: return "child_mnemo_technique_frame_peg"
        case .storyLink: return "child_mnemo_technique_story_link"
        case .spacedReview: return "child_mnemo_technique_spaced_review"
        }
    }
}

enum MnemonicSkillLevel: String, Codable {
    case novice
    case apprentice
    case champion

    var localizationKey: String {
        switch self {
        case .novice: return "child_mnemo_skill_novice"
        case .apprentice: return "child_mnemo_skill_apprentice"
        case .champion: return "child_mnemo_skill_champion"
        }
    }

    static func from(successfulRecalls: Int, anchors: Int, capstoneCompleted: Bool = false) -> MnemonicSkillLevel {
        if capstoneCompleted || anchors >= 20 { return .champion }
        if successfulRecalls >= 10 { return .apprentice }
        return .novice
    }
}
