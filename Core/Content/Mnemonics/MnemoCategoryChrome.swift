import Foundation

/// Фазы игрового цикла мнемотехники (AIM+4D).
enum MnemoAcademyPhase: Int, CaseIterable, Identifiable {
    case techniquePick = -1
    case warmup = 0
    case encode = 1
    case anchor = 2
    case recall = 3
    case reward = 4
    case reflect = 5

    var id: Int { rawValue }

    var localizationKey: String {
        switch self {
        case .techniquePick: return "child_mnemo_phase_technique_pick"
        case .warmup: return "child_mnemo_phase_warmup"
        case .encode: return "child_mnemo_phase_encode"
        case .anchor: return "child_mnemo_phase_anchor"
        case .recall: return "child_mnemo_phase_recall"
        case .reward: return "child_mnemo_phase_reward"
        case .reflect: return "child_mnemo_phase_reflect"
        }
    }

    /// Catalog banner dots — always 4 core phases (WARMUP/REFLECT only in lesson flow — B14-T05/T06).
    static var catalogPhases: [MnemoAcademyPhase] {
        [.encode, .anchor, .recall, .reward]
    }
}

/// Политика: **полная замена** UX/текстов в мнемо-категориях (Same ID, new soul).
/// ID категорий (`ChildCategoryKey`) не меняются.
enum MnemoCategoryChrome {

    // MARK: - Mnemo scope per age

    static func isMnemoCategory(_ category: String, ageGroup: ChildInterfaceScreen.AgeGroup) -> Bool {
        labelKey(category: category, ageGroup: ageGroup) != nil
    }

    static func labelKey(category: String, ageGroup: ChildInterfaceScreen.AgeGroup) -> String? {
        switch ageGroup {
        case .kids:
            if category == ChildCategoryKey.songs { return "child_mnemo_label_songs_kids" }
            return nil
        case .school:
            switch category {
            case ChildCategoryKey.games: return "child_mnemo_label_games_school"
            case ChildCategoryKey.study: return "child_mnemo_label_study_school"
            case ChildCategoryKey.cartoons: return "child_mnemo_label_cartoons_school"
            default: return nil
            }
        case .teen:
            switch category {
            case ChildCategoryKey.music: return "child_mnemo_label_music_teen"
            case ChildCategoryKey.video: return "child_mnemo_label_video_teen"
            default: return nil
            }
        case .youngAdult:
            switch category {
            case ChildCategoryKey.movies: return "child_mnemo_label_movies_young"
            case ChildCategoryKey.education: return "child_mnemo_label_education_young"
            default: return nil
            }
        }
    }

    static func subtitleKey(category: String, ageGroup: ChildInterfaceScreen.AgeGroup) -> String? {
        guard let label = labelKey(category: category, ageGroup: ageGroup) else { return nil }
        return label.replacingOccurrences(of: "_label_", with: "_subtitle_")
    }

    static func greetingKey(category: String, ageGroup: ChildInterfaceScreen.AgeGroup) -> String? {
        guard let label = labelKey(category: category, ageGroup: ageGroup) else { return nil }
        return label.replacingOccurrences(of: "_label_", with: "_catalog_greeting_")
    }

    static func displayTitle(category: String, ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String {
        if let key = labelKey(category: category, ageGroup: ageGroup) {
            return localization.localized(key)
        }
        return localization.localized(category)
    }

    static func displaySubtitle(category: String, ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String? {
        guard let key = subtitleKey(category: category, ageGroup: ageGroup) else { return nil }
        return localization.localized(key)
    }

    static func catalogGreeting(category: String, ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String? {
        guard let key = greetingKey(category: category, ageGroup: ageGroup) else { return nil }
        return localization.localized(key)
    }
}

// MARK: - Memory Academy brand (v2.2)

/// Главный бренд: **Академия памяти** / Memory Academy.
/// Второстепенные: promise (banner), superpower (rewards), smart memory (parent).
enum MnemoBrandChrome {

    static func brandTitleKey(ageGroup: ChildInterfaceScreen.AgeGroup) -> String {
        switch ageGroup {
        case .kids: return "child_mnemo_brand_title_kids"
        case .school: return "child_mnemo_brand_title_school"
        case .teen: return "child_mnemo_brand_title_teen"
        case .youngAdult: return "child_mnemo_brand_title_young_adult"
        }
    }

    static func brandTaglineKey(ageGroup: ChildInterfaceScreen.AgeGroup) -> String {
        switch ageGroup {
        case .kids: return "child_mnemo_brand_tagline_kids"
        case .school: return "child_mnemo_brand_tagline_school"
        case .teen: return "child_mnemo_brand_tagline_teen"
        case .youngAdult: return "child_mnemo_brand_tagline_young_adult"
        }
    }

    static func brandAccentKey(ageGroup: ChildInterfaceScreen.AgeGroup) -> String {
        switch ageGroup {
        case .kids: return "child_mnemo_brand_accent_kids"
        case .school: return "child_mnemo_brand_accent_school"
        case .teen: return "child_mnemo_brand_accent_teen"
        case .youngAdult: return "child_mnemo_brand_accent_young_adult"
        }
    }

    static let promiseKey = "child_mnemo_brand_promise"
    static let superpowerTitleKey = "child_mnemo_brand_superpower_title"
    static let superpowerToastKey = "child_mnemo_brand_superpower_toast"
    static let parentSmartTitleKey = "parent_mnemo_brand_smart_title"
    static let parentSmartSubtitleKey = "parent_mnemo_brand_smart_subtitle"
    static let onboardingTitleKey = "onboarding_mnemo_academy_title"
    static let onboardingDescKey = "onboarding_mnemo_academy_desc"

    static func brandTitle(ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String {
        localization.localized(brandTitleKey(ageGroup: ageGroup))
    }

    static func brandTagline(ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String {
        localization.localized(brandTaglineKey(ageGroup: ageGroup))
    }

    static func brandAccent(ageGroup: ChildInterfaceScreen.AgeGroup, localization: LocalizationManager) -> String {
        if MnemoFeatureFlags.teenExamHacksCopy, ageGroup == .teen {
            return localization.localized("child_mnemo_exam_hacks_accent")
        }
        return localization.localized(brandAccentKey(ageGroup: ageGroup))
    }

    /// B14-T10: optional exam-hacks banner line (teen + flag).
    static func examHacksBannerLine(localization: LocalizationManager) -> String? {
        guard MnemoFeatureFlags.teenExamHacksCopy else { return nil }
        return localization.localized("child_mnemo_exam_hacks_banner")
    }
}
