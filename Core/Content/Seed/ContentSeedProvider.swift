import Foundation

enum ChildCategoryKey {
    static let toys = "child_interface_category_toys"
    static let drawing = "child_interface_category_drawing"
    static let songs = "child_interface_category_songs"
    static let stories = "child_interface_category_stories"
    static let games = "child_interface_category_games"
    static let study = "child_interface_category_study"
    static let safety = "child_interface_category_safety"
    static let creativity = "child_interface_category_creativity"
    static let cartoons = "child_interface_category_cartoons"
    static let programming = "child_interface_category_programming"
    static let social = "child_interface_category_social"
    static let music = "child_interface_category_music"
    static let video = "child_interface_category_video"
    static let education = "child_interface_category_education"
    static let career = "child_interface_category_career"
    static let internet = "child_interface_category_internet"
    static let movies = "child_interface_category_movies"
}

enum ElderlyCategoryKey {
    static let health = "elderly_content_health"
    static let safety = "elderly_content_safety"
    static let memory = "elderly_content_memory"
    static let activity = "elderly_content_activity"
}

/// Phase 9.4: binds child content categories + family safety toggles with elderly controls.
enum FamilyContentSafetyBridge {
    static let safetyTitleKey = "family_category_safety"
    static let childSafetyMirrorCategories: [String] = [
        ChildCategoryKey.safety,
        ChildCategoryKey.internet,
        ChildCategoryKey.social
    ]

    static func resolvedElderlyCategories(defaults: UserDefaults = .standard) -> [String] {
        let base: [String] = [
            ElderlyCategoryKey.health,
            ElderlyCategoryKey.memory,
            ElderlyCategoryKey.activity
        ]
        let shouldIncludeSafety = defaults.bool(forKey: "family_content_block_enabled")
            || defaults.bool(forKey: "family_monitoring_enabled")
            || defaults.bool(forKey: "family_reports_enabled")
            || defaults.bool(forKey: "family_bypass_protection_enabled")
        return shouldIncludeSafety ? [ElderlyCategoryKey.safety] + base : base
    }
}

final class ContentSeedProvider {
    static let shared = ContentSeedProvider()

    private init() {}

    func initialManifest() -> ContentManifest {
        let categories: [ContentCategory] = [
            .init(id: ChildCategoryKey.toys, titleKey: ChildCategoryKey.toys, icon: "🧸", ageBand: .kids_1_6),
            .init(id: ChildCategoryKey.drawing, titleKey: ChildCategoryKey.drawing, icon: "🎨", ageBand: .kids_1_6),
            .init(id: ChildCategoryKey.songs, titleKey: ChildCategoryKey.songs, icon: "🎵", ageBand: .kids_1_6),
            .init(id: ChildCategoryKey.stories, titleKey: ChildCategoryKey.stories, icon: "📖", ageBand: .kids_1_6),
            .init(id: ChildCategoryKey.games, titleKey: ChildCategoryKey.games, icon: "🎮", ageBand: .school_7_12),
            .init(id: ChildCategoryKey.study, titleKey: ChildCategoryKey.study, icon: "📚", ageBand: .school_7_12),
            .init(id: ChildCategoryKey.safety, titleKey: ChildCategoryKey.safety, icon: "🛡️", ageBand: .school_7_12),
            .init(id: ChildCategoryKey.creativity, titleKey: ChildCategoryKey.creativity, icon: "🎨", ageBand: .school_7_12),
            .init(id: ChildCategoryKey.cartoons, titleKey: ChildCategoryKey.cartoons, icon: "📺", ageBand: .school_7_12),
            .init(id: ChildCategoryKey.programming, titleKey: ChildCategoryKey.programming, icon: "💻", ageBand: .teen_13_17),
            .init(id: ChildCategoryKey.social, titleKey: ChildCategoryKey.social, icon: "📱", ageBand: .teen_13_17),
            .init(id: ChildCategoryKey.music, titleKey: ChildCategoryKey.music, icon: "🎵", ageBand: .teen_13_17),
            .init(id: ChildCategoryKey.video, titleKey: ChildCategoryKey.video, icon: "📺", ageBand: .teen_13_17),
            .init(id: ChildCategoryKey.education, titleKey: ChildCategoryKey.education, icon: "🎓", ageBand: .youngAdult_18_22),
            .init(id: ChildCategoryKey.career, titleKey: ChildCategoryKey.career, icon: "💼", ageBand: .youngAdult_18_22),
            .init(id: ChildCategoryKey.internet, titleKey: ChildCategoryKey.internet, icon: "🌐", ageBand: .youngAdult_18_22),
            .init(id: ChildCategoryKey.movies, titleKey: ChildCategoryKey.movies, icon: "🎬", ageBand: .youngAdult_18_22),
            .init(id: ElderlyCategoryKey.health, titleKey: "elderly_interface_health_reminders", icon: "💊", ageBand: .youngAdult_18_22),
            .init(id: ElderlyCategoryKey.safety, titleKey: FamilyContentSafetyBridge.safetyTitleKey, icon: "🛡️", ageBand: .youngAdult_18_22),
            .init(id: ElderlyCategoryKey.memory, titleKey: "elderly_health_journal_title", icon: "🧠", ageBand: .youngAdult_18_22),
            .init(id: ElderlyCategoryKey.activity, titleKey: "elderly_interface_protected", icon: "🚶", ageBand: .youngAdult_18_22)
        ]

        var items: [ContentItem] = []
        for category in categories {
            let titles = seedTitles(for: category.id)
            for (index, title) in titles.enumerated() {
                items.append(
                    ContentItem(
                        id: "\(category.id).\(index + 1)",
                        categoryId: category.id,
                        type: inferredType(for: category.id),
                        ageBand: category.ageBand,
                        version: 1,
                        metadata: ContentMetadata(
                            locale: "ru",
                            title: title,
                            subtitle: "Контент-пакет фазы 2",
                            description: "Элемент категории \(category.id)",
                            tags: seedTags(for: category.id),
                            estimatedDurationSec: 300 + index * 60
                        ),
                        payloadURL: nil,
                        checksumSHA256: nil,
                        isOfflineAvailable: true
                    )
                )
            }
        }

        return ContentManifest(
            manifestVersion: 2,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "seed-manifest-v2",
            signature: nil,
            categories: categories,
            items: items
        )
    }

    private static let mnemoSeedCategoryIds: Set<String> = [
        ChildCategoryKey.songs,
        ChildCategoryKey.games,
        ChildCategoryKey.study,
        ChildCategoryKey.cartoons,
        ChildCategoryKey.music,
        ChildCategoryKey.video,
        ChildCategoryKey.movies,
        ChildCategoryKey.education
    ]

    private func seedTags(for categoryId: String) -> [String] {
        var tags = ["phase2", "seed", categoryId]
        if Self.mnemoSeedCategoryIds.contains(categoryId) {
            tags.append("mnemo")
        }
        return tags
    }

    private func inferredType(for category: String) -> ContentItemType {
        switch category {
        case ChildCategoryKey.games, ChildCategoryKey.toys:
            return .game
        case ChildCategoryKey.study, ChildCategoryKey.education, ChildCategoryKey.programming:
            return .lesson
        case ChildCategoryKey.cartoons, ChildCategoryKey.video, ChildCategoryKey.movies:
            return .video
        case ChildCategoryKey.songs, ChildCategoryKey.music:
            return .song
        case ChildCategoryKey.stories:
            return .story
        case ChildCategoryKey.drawing, ChildCategoryKey.creativity:
            return .drawing
        case ChildCategoryKey.career:
            return .career
        default:
            return .lesson
        }
    }

    private func seedTitles(for category: String) -> [String] {
        switch category {
        case ChildCategoryKey.toys:
            return ["child_seed_toys_1", "child_seed_toys_2", "child_seed_toys_3"]
        case ChildCategoryKey.drawing:
            return ["child_seed_drawing_1", "child_seed_drawing_2", "child_seed_drawing_3"]
        case ChildCategoryKey.songs:
            return ["child_seed_songs_1", "child_seed_songs_2", "child_seed_songs_3"]
        case ChildCategoryKey.stories:
            return ["child_seed_stories_1", "child_seed_stories_2", "child_seed_stories_3"]
        case ChildCategoryKey.games:
            return ["child_seed_games_1", "child_seed_games_2", "child_seed_games_3"]
        case ChildCategoryKey.study:
            return ["child_seed_study_1", "child_seed_study_2", "child_seed_study_3"]
        case ChildCategoryKey.safety:
            return ["child_seed_safety_1", "child_seed_safety_2", "child_seed_safety_3"]
        case ChildCategoryKey.cartoons:
            return ["child_seed_cartoons_1", "child_seed_cartoons_2", "child_seed_cartoons_3"]
        case ChildCategoryKey.creativity:
            return ["child_seed_creativity_1", "child_seed_creativity_2", "child_seed_creativity_3"]
        case ChildCategoryKey.programming:
            return ["child_seed_programming_1", "child_seed_programming_2", "child_seed_programming_3"]
        case ChildCategoryKey.social:
            return ["child_seed_social_1", "child_seed_social_2", "child_seed_social_3"]
        case ChildCategoryKey.music:
            return ["child_seed_music_1", "child_seed_music_2", "child_seed_music_3"]
        case ChildCategoryKey.video:
            return ["child_seed_video_1", "child_seed_video_2", "child_seed_video_3"]
        case ChildCategoryKey.education:
            return ["child_seed_education_1", "child_seed_education_2", "child_seed_education_3"]
        case ChildCategoryKey.career:
            return ["child_seed_career_1", "child_seed_career_2", "child_seed_career_3"]
        case ChildCategoryKey.internet:
            return ["child_seed_internet_1", "child_seed_internet_2", "child_seed_internet_3"]
        case ChildCategoryKey.movies:
            return ["child_seed_movies_1", "child_seed_movies_2", "child_seed_movies_3"]
        case ElderlyCategoryKey.health:
            return ["Памятка по лекарствам", "Ежедневный контроль давления", "План визита к врачу"]
        case ElderlyCategoryKey.safety:
            return ["Проверка подозрительных звонков", "Как распознать мошенничество", "Безопасный интернет для 60+"]
        case ElderlyCategoryKey.memory:
            return ["Тренировка памяти 10 минут", "Лёгкие логические задачи", "Дневник самочувствия"]
        case ElderlyCategoryKey.activity:
            return ["Мягкая зарядка дома", "Пешая активность без перегрузки", "Режим сна и восстановления"]
        default:
            return ["Базовый контент", "Дополнительный модуль", "Практический блок"]
        }
    }
}

