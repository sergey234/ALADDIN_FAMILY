import Foundation

/// Parent guide copy registry (§T) — HTML built in `MnemoParentGuideSheet` (B14-T02).
enum MnemoParentGuideContent {
    static let shellKeys: [String] = [
        "parent_mnemo_guide_title",
        "parent_mnemo_guide_subtitle",
        "parent_mnemo_guide_open_cta",
    ]

    static let introKeys: [String] = [
        "parent_mnemo_guide_intro_title",
        "parent_mnemo_guide_intro_lead",
        "parent_mnemo_guide_intro_aim_title",
        "parent_mnemo_guide_intro_aim_association",
        "parent_mnemo_guide_intro_aim_imagination",
        "parent_mnemo_guide_intro_aim_location",
        "parent_mnemo_guide_intro_4d_title",
        "parent_mnemo_guide_intro_4d_body",
    ]

    static let srsKeys: [String] = [
        "parent_mnemo_guide_srs_title",
        "parent_mnemo_guide_srs_lead",
        "parent_mnemo_guide_srs_tip_calm",
        "parent_mnemo_guide_srs_tip_routine",
        "parent_mnemo_guide_srs_tip_praise",
    ]

    static let mqKeys: [String] = [
        "parent_mnemo_guide_mq_title",
        "parent_mnemo_guide_mq_lead",
        "parent_mnemo_guide_mq_scale",
        "parent_mnemo_guide_mq_quarterly",
    ]

    static let techniqueTipKeys: [String] = MnemonicTechnique.allCases.map(\.parentGuideLocalizationKey)

    static let allLocalizationKeys: [String] =
        shellKeys + introKeys + srsKeys + mqKeys + techniqueTipKeys
}

extension MnemonicTechnique {
    var parentGuideLocalizationKey: String {
        "parent_mnemo_guide_technique_\(rawValue)"
    }
}
