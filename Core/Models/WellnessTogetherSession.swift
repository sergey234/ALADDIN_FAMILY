import Foundation

struct WellnessTogetherSession: Codable {
    let title: String
    let intro: String
    let durationSec: Int
    let breathInSec: Int
    let breathOutSec: Int
    let steps: [String]
    let titleKey: String?
    let introKey: String?

    enum CodingKeys: String, CodingKey {
        case title
        case intro
        case durationSec = "duration_sec"
        case breathInSec = "breath_in_sec"
        case breathOutSec = "breath_out_sec"
        case steps
        case titleKey = "title_key"
        case introKey = "intro_key"
    }
}
