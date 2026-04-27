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
                            tags: ["phase2", "seed", category.id],
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
            manifestVersion: 1,
            generatedAt: Date(),
            minSupportedAppVersion: "1.0.0",
            checksumSHA256: "seed-manifest-v1",
            signature: nil,
            categories: categories,
            items: items
        )
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
            return ["Умные игрушки", "Логическая мозаика", "Игра Найди форму"]
        case ChildCategoryKey.drawing:
            return ["Рисуем животных", "Цветные фигуры", "Мой первый альбом"]
        case ChildCategoryKey.songs:
            return ["Песенка про буквы", "Считалочка", "Добрая колыбельная"]
        case ChildCategoryKey.stories:
            return ["Сказка про дружбу", "Лесные приключения", "Маленький герой"]
        case ChildCategoryKey.games:
            return ["Математический квест", "Словесный лабиринт", "Логический спринт"]
        case ChildCategoryKey.study:
            return ["Русский язык: основы", "Математика: базовый уровень", "Окружающий мир"]
        case ChildCategoryKey.safety:
            return ["Безопасный интернет", "Как не доверять незнакомцам", "Проверка ссылок"]
        case ChildCategoryKey.cartoons:
            return ["Обучающий мультфильм 1", "Обучающий мультфильм 2", "Научный мини-сериал"]
        case ChildCategoryKey.creativity:
            return ["Творческая мастерская", "Цвет и композиция", "Мини-проект своими руками"]
        case ChildCategoryKey.programming:
            return ["Логика алгоритмов", "Swift Start", "Визуальное программирование"]
        case ChildCategoryKey.social:
            return ["Безопасное общение", "Цифровой этикет", "Контроль приватности"]
        case ChildCategoryKey.music:
            return ["Музыкальные жанры", "Ритм и мелодия", "Практика слуха"]
        case ChildCategoryKey.video:
            return ["Образовательное видео 1", "Образовательное видео 2", "Видео-разбор темы"]
        case ChildCategoryKey.education:
            return ["Финансовая грамотность", "Навыки самообучения", "Подготовка к экзаменам"]
        case ChildCategoryKey.career:
            return ["Профессии будущего", "Карьерные треки", "Портфолио и навыки"]
        case ChildCategoryKey.internet:
            return ["Работа с источниками", "Критическое мышление онлайн", "Цифровая гигиена"]
        case ChildCategoryKey.movies:
            return ["Кино и анализ сюжета", "Документальные форматы", "Кино-клуб"]
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

