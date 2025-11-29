import Foundation

// MARK: - Reward Operation Model

typealias RewardHistoryTexts = (title: RewardText, reason: RewardText)

struct RewardOperation: Codable, Identifiable {
    let id: String
    var title: RewardText
    var reason: RewardText
    let amount: Int
    let isReward: Bool
    let date: Date
    
    init(
        id: String = UUID().uuidString,
        title: RewardText,
        reason: RewardText,
        amount: Int,
        isReward: Bool,
        date: Date = Date()
    ) {
        self.id = id
        self.title = title
        self.reason = reason
        self.amount = amount
        self.isReward = isReward
        self.date = date
    }
}

// MARK: - Reward Text Helper

struct RewardText: Codable, Equatable {
    private enum CodingKeys: String, CodingKey {
        case key
        case translations
    }
    
    var key: String?
    var translations: [String: String]
    var localizationKey: String? { key }
    
    init(key: String) {
        self.key = key
        self.translations = [:]
    }
    
    init(translations: [String: String]) {
        self.key = nil
        self.translations = translations
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let string = try? container.decode(String.self) {
            self.key = nil
            self.translations = [LocalizationManager.Language.russian.rawValue: string]
            return
        }
        if container.decodeNil() {
            self.key = nil
            self.translations = [:]
            return
        }
        let keyedContainer = try decoder.container(keyedBy: CodingKeys.self)
        self.key = try keyedContainer.decodeIfPresent(String.self, forKey: .key)
        self.translations = try keyedContainer.decodeIfPresent([String: String].self, forKey: .translations) ?? [:]
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encodeIfPresent(key, forKey: .key)
        if !translations.isEmpty {
            try container.encode(translations, forKey: .translations)
        }
    }
    
    func resolved(with localizationManager: LocalizationManager) -> String {
        let currentLang = localizationManager.currentLanguage.rawValue
        if let custom = translations[currentLang], custom.isEmpty == false {
            return custom
        }
        if let key = key {
            return localizationManager.localized(key)
        }
        return ""
    }
    
    func value(for language: LocalizationManager.Language) -> String? {
        translations[language.rawValue]
    }
    
    mutating func setCustom(_ value: String, for language: LocalizationManager.Language) {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            translations.removeValue(forKey: language.rawValue)
        } else {
            translations[language.rawValue] = trimmed
        }
    }
    
    mutating func clearCustom(for language: LocalizationManager.Language) {
        translations.removeValue(forKey: language.rawValue)
    }
}

extension RewardText {
    static func custom(_ value: String, language: LocalizationManager.Language) -> RewardText {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return RewardText(translations: [:]) }
        return RewardText(translations: [language.rawValue: trimmed])
    }

    static func formatted(key: String, argument: String, localizationManager: LocalizationManager) -> RewardText {
        var translations: [String: String] = [:]
        for language in LocalizationManager.Language.allCases {
            guard let template = localizationManager.translations[language]?[key] else { continue }
            let locale = Locale(identifier: language.rawValue)
            translations[language.rawValue] = String(format: template, locale: locale, argument)
        }
        return RewardText(translations: translations)
    }
}

// MARK: - Shop Reward Model

struct ShopReward: Codable, Identifiable {
    let id: String
    var icon: String
    var title: RewardText
    var desc: RewardText
    var price: Int
    var isEnabled: Bool
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        title: RewardText,
        desc: RewardText,
        price: Int,
        isEnabled: Bool = true
    ) {
        self.id = id
        self.icon = icon
        self.title = title
        self.desc = desc
        self.price = price
        self.isEnabled = isEnabled
    }
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        titleKey: String,
        descKey: String,
        price: Int,
        isEnabled: Bool = true
    ) {
        self.init(
            id: id,
            icon: icon,
            title: RewardText(key: titleKey),
            desc: RewardText(key: descKey),
            price: price,
            isEnabled: isEnabled
        )
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        title.resolved(with: localizationManager)
    }
    
    func localizedDescription(_ localizationManager: LocalizationManager) -> String {
        desc.resolved(with: localizationManager)
    }
    
    func titleValue(for language: LocalizationManager.Language) -> String {
        title.value(for: language) ?? ""
    }
    
    func descriptionValue(for language: LocalizationManager.Language) -> String {
        desc.value(for: language) ?? ""
    }
    
    mutating func updateTitle(_ value: String, language: LocalizationManager.Language) {
        title.setCustom(value, for: language)
    }
    
    mutating func updateDescription(_ value: String, language: LocalizationManager.Language) {
        desc.setCustom(value, for: language)
    }
}

// MARK: - Default Shop Rewards

extension ShopReward {
    static var defaultRewards: [ShopReward] {
        [
            ShopReward(icon: "🎮", titleKey: "child_rewards_shop_item_extra_play_title", descKey: "child_rewards_shop_item_extra_play_desc", price: 50),
            ShopReward(icon: "📱", titleKey: "child_rewards_shop_item_extra_screen_title", descKey: "child_rewards_shop_item_extra_screen_desc", price: 80),
            ShopReward(icon: "🌙", titleKey: "child_rewards_shop_item_bedtime_title", descKey: "child_rewards_shop_item_bedtime_desc", price: 100),
            ShopReward(icon: "🍕", titleKey: "child_rewards_shop_item_pizza_title", descKey: "child_rewards_shop_item_pizza_desc", price: 150),
            ShopReward(icon: "🎬", titleKey: "child_rewards_shop_item_cinema_title", descKey: "child_rewards_shop_item_cinema_desc", price: 200),
            ShopReward(icon: "🎁", titleKey: "child_rewards_shop_item_gift_title", descKey: "child_rewards_shop_item_gift_desc", price: 500)
        ]
    }
}

// MARK: - Earning Way Model

struct EarningWay: Identifiable, Codable {
    let id: String
    var icon: String
    var title: RewardText
    var subtitle: RewardText
    var amount: Int  // Награда в единорогах (положительное число)
    var isEnabled: Bool
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        title: RewardText,
        subtitle: RewardText,
        amount: Int,
        isEnabled: Bool = true
    ) {
        self.id = id
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.amount = amount
        self.isEnabled = isEnabled
    }
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        titleKey: String,
        subtitleKey: String,
        amount: Int,
        isEnabled: Bool = true
    ) {
        self.init(
            id: id,
            icon: icon,
            title: RewardText(key: titleKey),
            subtitle: RewardText(key: subtitleKey),
            amount: amount,
            isEnabled: isEnabled
        )
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        title.resolved(with: localizationManager)
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        subtitle.resolved(with: localizationManager)
    }
    
    mutating func updateTitle(_ value: String, language: LocalizationManager.Language) {
        title.setCustom(value, for: language)
    }
    
    mutating func updateSubtitle(_ value: String, language: LocalizationManager.Language) {
        subtitle.setCustom(value, for: language)
    }
    
    func titleValue(for language: LocalizationManager.Language) -> String {
        title.value(for: language) ?? ""
    }
    
    func subtitleValue(for language: LocalizationManager.Language) -> String {
        subtitle.value(for: language) ?? ""
    }
}

extension EarningWay {
    static var defaultEarningWays: [EarningWay] {
        [
            EarningWay(id: "homework", icon: "📚", titleKey: "child_rewards_earning_homework_title", subtitleKey: "child_rewards_earning_homework_desc", amount: 10, isEnabled: true),
            EarningWay(id: "chores", icon: "🧹", titleKey: "child_rewards_earning_chores_title", subtitleKey: "child_rewards_earning_chores_desc", amount: 5, isEnabled: true),
            EarningWay(id: "behavior", icon: "😊", titleKey: "child_rewards_earning_behavior_title", subtitleKey: "child_rewards_earning_behavior_desc", amount: 15, isEnabled: true),
            EarningWay(id: "reading", icon: "📖", titleKey: "child_rewards_earning_reading_title", subtitleKey: "child_rewards_earning_reading_desc", amount: 20, isEnabled: true),
            EarningWay(id: "achievement", icon: "🏆", titleKey: "child_rewards_earning_achievement_title", subtitleKey: "child_rewards_earning_achievement_desc", amount: 50, isEnabled: true)
        ]
    }
}

// MARK: - Punishment Reason Model

struct PunishmentReason: Identifiable, Codable {
    let id: String
    var icon: String
    var title: RewardText
    var subtitle: RewardText
    var amount: Int  // Штраф в единорогах (положительное число, будет отображаться с минусом)
    var isEnabled: Bool
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        title: RewardText,
        subtitle: RewardText,
        amount: Int,
        isEnabled: Bool = true
    ) {
        self.id = id
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.amount = amount
        self.isEnabled = isEnabled
    }
    
    init(
        id: String = UUID().uuidString,
        icon: String,
        titleKey: String,
        subtitleKey: String,
        amount: Int,
        isEnabled: Bool = true
    ) {
        self.init(
            id: id,
            icon: icon,
            title: RewardText(key: titleKey),
            subtitle: RewardText(key: subtitleKey),
            amount: amount,
            isEnabled: isEnabled
        )
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        title.resolved(with: localizationManager)
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        subtitle.resolved(with: localizationManager)
    }
    
    mutating func updateTitle(_ value: String, language: LocalizationManager.Language) {
        title.setCustom(value, for: language)
    }
    
    mutating func updateSubtitle(_ value: String, language: LocalizationManager.Language) {
        subtitle.setCustom(value, for: language)
    }
    
    func titleValue(for language: LocalizationManager.Language) -> String {
        title.value(for: language) ?? ""
    }
    
    func subtitleValue(for language: LocalizationManager.Language) -> String {
        subtitle.value(for: language) ?? ""
    }
}

extension PunishmentReason {
    static var defaultPunishmentReasons: [PunishmentReason] {
        [
            PunishmentReason(id: "no_homework", icon: "📚", titleKey: "child_rewards_punish_homework_title", subtitleKey: "child_rewards_punish_homework_desc", amount: 10, isEnabled: true),
            PunishmentReason(id: "bad_behavior", icon: "😡", titleKey: "child_rewards_punish_behavior_title", subtitleKey: "child_rewards_punish_behavior_desc", amount: 15, isEnabled: true),
            PunishmentReason(id: "limit_violation", icon: "⏰", titleKey: "child_rewards_punish_limits_title", subtitleKey: "child_rewards_punish_limits_desc", amount: 5, isEnabled: true),
            PunishmentReason(id: "bypass_attempt", icon: "🚫", titleKey: "child_rewards_punish_bypass_title", subtitleKey: "child_rewards_punish_bypass_desc", amount: 20, isEnabled: true),
            PunishmentReason(id: "custom", icon: "😤", titleKey: "child_rewards_punish_custom_title", subtitleKey: "child_rewards_punish_custom_desc", amount: 1, isEnabled: true)
        ]
    }
}

// MARK: - Localization Migration Helper

enum RewardLocalizationMigration {
    private static let migrationFlagKey = "reward_localization_migration_v1"
    private static let shopRewardsKey = "shop_rewards_list"
    private static let earningWaysKey = "earning_ways_list"
    private static let punishmentReasonsKey = "punishment_reasons_list"

    private static let shopTitleMap: [String: (titleKey: String, descKey: String)] = [
        "+30 минут игр": ("child_rewards_shop_item_extra_play_title", "child_rewards_shop_item_extra_play_desc"),
        "+1 час экранного времени": ("child_rewards_shop_item_extra_screen_title", "child_rewards_shop_item_extra_screen_desc"),
        "+30 минут перед сном": ("child_rewards_shop_item_bedtime_title", "child_rewards_shop_item_bedtime_desc"),
        "Заказ пиццы": ("child_rewards_shop_item_pizza_title", "child_rewards_shop_item_pizza_desc"),
        "Поход в кино": ("child_rewards_shop_item_cinema_title", "child_rewards_shop_item_cinema_desc"),
        "Подарок по выбору": ("child_rewards_shop_item_gift_title", "child_rewards_shop_item_gift_desc")
    ]

    private static let shopDescMap: [String: String] = [
        "Дополнительное время": "child_rewards_shop_item_extra_play_desc",
        "На любой день": "child_rewards_shop_item_extra_screen_desc",
        "Сдвинуть время сна": "child_rewards_shop_item_bedtime_desc",
        "Твоя любимая!": "child_rewards_shop_item_pizza_desc",
        "С друзьями!": "child_rewards_shop_item_cinema_desc",
        "До 1000₽": "child_rewards_shop_item_gift_desc"
    ]

    private static let earningTitleMap: [String: String] = [
        "Домашнее задание": "child_rewards_earning_homework_title",
        "Домашние обязанности": "child_rewards_earning_chores_title",
        "Хорошее поведение": "child_rewards_earning_behavior_title",
        "Чтение книг": "child_rewards_earning_reading_title",
        "Достижение в учебе": "child_rewards_earning_achievement_title"
    ]

    private static let earningSubtitleMap: [String: String] = [
        "+10 единорогов за задание": "child_rewards_earning_homework_desc",
        "+5 единорогов за дело": "child_rewards_earning_chores_desc",
        "+15 единорогов за день": "child_rewards_earning_behavior_desc",
        "+20 единорогов за книгу": "child_rewards_earning_reading_desc",
        "+50 единорогов за 5": "child_rewards_earning_achievement_desc"
    ]

    private static let punishmentTitleMap: [String: String] = [
        "Не сделал домашнее задание": "child_rewards_punish_homework_title",
        "Плохое поведение": "child_rewards_punish_behavior_title",
        "Нарушение лимитов": "child_rewards_punish_limits_title",
        "Обход блокировок": "child_rewards_punish_bypass_title",
        "Своя причина": "child_rewards_punish_custom_title"
    ]

    private static let punishmentSubtitleMap: [String: String] = [
        "Забыл или отказался делать": "child_rewards_punish_homework_desc",
        "Грубость, ссоры, непослушание": "child_rewards_punish_behavior_desc",
        "Превышение экранного времени": "child_rewards_punish_limits_desc",
        "Попытка обойти контроль": "child_rewards_punish_bypass_desc",
        "Родители указывают сами": "child_rewards_punish_custom_desc"
    ]

    static func performIfNeeded(using defaults: UserDefaults = .standard) {
        guard defaults.bool(forKey: migrationFlagKey) == false else { return }

        var didUpdate = false

        if let updated = migrateShopRewards(from: defaults.string(forKey: shopRewardsKey)) {
            defaults.set(updated, forKey: shopRewardsKey)
            didUpdate = true
        }

        if let updated = migrateEarningWays(from: defaults.string(forKey: earningWaysKey)) {
            defaults.set(updated, forKey: earningWaysKey)
            didUpdate = true
        }

        if let updated = migratePunishmentReasons(from: defaults.string(forKey: punishmentReasonsKey)) {
            defaults.set(updated, forKey: punishmentReasonsKey)
            didUpdate = true
        }

        if didUpdate {
            defaults.set(true, forKey: migrationFlagKey)
        }
    }

    // MARK: - Private helpers

    private static func migrateShopRewards(from jsonString: String?) -> String? {
        guard let jsonString = jsonString,
              let data = jsonString.data(using: .utf8),
              var rewards = try? JSONDecoder().decode([ShopReward].self, from: data) else {
            return nil
        }

        var changed = false

        for index in rewards.indices {
            var reward = rewards[index]

            if reward.title.key == nil, let ruTitle = reward.title.value(for: .russian), let mapping = shopTitleMap[ruTitle] {
                reward.title = RewardText(key: mapping.titleKey)
                reward.desc = RewardText(key: mapping.descKey)
                changed = true
            } else if reward.desc.key == nil, let ruDesc = reward.desc.value(for: .russian), let descKey = shopDescMap[ruDesc] {
                reward.desc = RewardText(key: descKey)
                changed = true
            }

            rewards[index] = reward
        }

        guard changed,
              let encoded = try? JSONEncoder().encode(rewards),
              let updatedString = String(data: encoded, encoding: .utf8) else {
            return nil
        }

        return updatedString
    }

    private static func migrateEarningWays(from jsonString: String?) -> String? {
        guard let jsonString = jsonString,
              let data = jsonString.data(using: .utf8),
              var ways = try? JSONDecoder().decode([EarningWay].self, from: data) else {
            return nil
        }

        var changed = false

        for index in ways.indices {
            var way = ways[index]

            if way.title.key == nil, let ruTitle = way.title.value(for: .russian), let key = earningTitleMap[ruTitle] {
                way.title = RewardText(key: key)
                changed = true
            }

            if way.subtitle.key == nil, let ruSubtitle = way.subtitle.value(for: .russian), let key = earningSubtitleMap[ruSubtitle] {
                way.subtitle = RewardText(key: key)
                changed = true
            }

            ways[index] = way
        }

        guard changed,
              let encoded = try? JSONEncoder().encode(ways),
              let updatedString = String(data: encoded, encoding: .utf8) else {
            return nil
        }

        return updatedString
    }

    private static func migratePunishmentReasons(from jsonString: String?) -> String? {
        guard let jsonString = jsonString,
              let data = jsonString.data(using: .utf8),
              var reasons = try? JSONDecoder().decode([PunishmentReason].self, from: data) else {
            return nil
        }

        var changed = false

        for index in reasons.indices {
            var reason = reasons[index]

            if reason.title.key == nil, let ruTitle = reason.title.value(for: .russian), let key = punishmentTitleMap[ruTitle] {
                reason.title = RewardText(key: key)
                changed = true
            }

            if reason.subtitle.key == nil, let ruSubtitle = reason.subtitle.value(for: .russian), let key = punishmentSubtitleMap[ruSubtitle] {
                reason.subtitle = RewardText(key: key)
                changed = true
            }

            reasons[index] = reason
        }

        guard changed,
              let encoded = try? JSONEncoder().encode(reasons),
              let updatedString = String(data: encoded, encoding: .utf8) else {
            return nil
        }

        return updatedString
    }
}

// MARK: - Child Family Contact Model

struct ChildFamilyContact: Identifiable, Codable {
    let id: UUID
    var name: String
    var phone: String
    var relation: String
    
    init(id: UUID = UUID(), name: String, phone: String, relation: String) {
        self.id = id
        self.name = name
        self.phone = phone
        self.relation = relation
    }
}

