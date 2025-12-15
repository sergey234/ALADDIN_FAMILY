import Foundation

private let suiteName = "com.aladdin.rewardMigrationSmoke"

@main
struct RewardMigrationSmoke {
    static func main() throws {
        print("[RewardMigrationSmoke] start")
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            throw NSError(domain: "RewardMigrationSmoke", code: 1, userInfo: [NSLocalizedDescriptionKey: "Не удалось создать UserDefaults suite"])
        }
        defaults.removePersistentDomain(forName: suiteName)

        try seedLegacyData(into: defaults)

        print("== До миграции ==")
        dumpData(from: defaults)

        RewardLocalizationMigration.performIfNeeded(using: defaults)

        print("\n== После миграции ==")
        dumpData(from: defaults)
    }

    private static func seedLegacyData(into defaults: UserDefaults) throws {
        let encoder = JSONEncoder()

        let legacyRewards = [
            ShopReward(id: "reward_standard_play", icon: "🎮", title: RewardText(translations: ["ru": "+30 минут игр"]), desc: RewardText(translations: ["ru": "Дополнительное время"]), price: 50),
            ShopReward(id: "reward_custom", icon: "🎉", title: RewardText(translations: ["ru": "Праздничный день"]), desc: RewardText(translations: ["ru": "На выбор ребёнка"]), price: 250)
        ]
        let rewardsJSON = try encoder.encode(legacyRewards)
        defaults.set(String(data: rewardsJSON, encoding: .utf8), forKey: "shop_rewards_list")

        let legacyEarningWays = [
            EarningWay(id: "earning_homework", icon: "📚", title: RewardText(translations: ["ru": "Домашнее задание"]), subtitle: RewardText(translations: ["ru": "+10 единорогов за задание"]), amount: 10),
            EarningWay(id: "earning_custom", icon: "🎨", title: RewardText(translations: ["ru": "Творчество"]), subtitle: RewardText(translations: ["ru": "За рисунок или поделку"]), amount: 12)
        ]
        let earningJSON = try encoder.encode(legacyEarningWays)
        defaults.set(String(data: earningJSON, encoding: .utf8), forKey: "earning_ways_list")

        let legacyPunishments = [
            PunishmentReason(id: "punish_behavior", icon: "😡", title: RewardText(translations: ["ru": "Плохое поведение"]), subtitle: RewardText(translations: ["ru": "Грубость, ссоры, непослушание"]), amount: 15),
            PunishmentReason(id: "punish_custom", icon: "⚠️", title: RewardText(translations: ["ru": "Своя причина"]), subtitle: RewardText(translations: ["ru": "Родители указывают сами"]), amount: 5)
        ]
        let punishJSON = try encoder.encode(legacyPunishments)
        defaults.set(String(data: punishJSON, encoding: .utf8), forKey: "punishment_reasons_list")
    }

    private static func dumpData(from defaults: UserDefaults) {
        let decoder = JSONDecoder()

        if let rewardsString = defaults.string(forKey: "shop_rewards_list"),
           let data = rewardsString.data(using: .utf8),
           let rewards = try? decoder.decode([ShopReward].self, from: data) {
            print("-- Магазин (\(rewards.count))")
            for reward in rewards {
                print("  • id=\(reward.id) icon=\(reward.icon) price=\(reward.price) titleKey=\(reward.title.localizationKey ?? "nil") descKey=\(reward.desc.localizationKey ?? "nil") translations=\(reward.title.translations)")
            }
        } else {
            print("-- Магазин: нет данных")
        }

        if let earningString = defaults.string(forKey: "earning_ways_list"),
           let data = earningString.data(using: .utf8),
           let ways = try? decoder.decode([EarningWay].self, from: data) {
            print("-- Способы заработка (\(ways.count))")
            for way in ways {
                print("  • id=\(way.id) icon=\(way.icon) amount=\(way.amount) titleKey=\(way.title.localizationKey ?? "nil") subtitleKey=\(way.subtitle.localizationKey ?? "nil") translations=\(way.title.translations)")
            }
        } else {
            print("-- Способы заработка: нет данных")
        }

        if let punishString = defaults.string(forKey: "punishment_reasons_list"),
           let data = punishString.data(using: .utf8),
           let reasons = try? decoder.decode([PunishmentReason].self, from: data) {
            print("-- Причины наказания (\(reasons.count))")
            for reason in reasons {
                print("  • id=\(reason.id) icon=\(reason.icon) amount=\(reason.amount) titleKey=\(reason.title.localizationKey ?? "nil") subtitleKey=\(reason.subtitle.localizationKey ?? "nil") translations=\(reason.title.translations)")
            }
        } else {
            print("-- Причины наказания: нет данных")
        }

        let flag = defaults.bool(forKey: "reward_localization_migration_v1")
        print("-- Флаг миграции: \(flag ? "✅" : "❌")")
    }
}
