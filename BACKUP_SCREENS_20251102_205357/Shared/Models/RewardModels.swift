import Foundation

// MARK: - Reward Operation Model

struct RewardOperation: Codable, Identifiable {
    let id: String
    let title: String
    let reason: String
    let amount: Int
    let isReward: Bool
    let date: Date
}

// MARK: - Shop Reward Model

struct ShopReward: Codable, Identifiable {
    let id: String
    var icon: String
    var title: String
    var desc: String
    var price: Int
    var isEnabled: Bool
    
    init(id: String = UUID().uuidString, icon: String, title: String, desc: String, price: Int, isEnabled: Bool = true) {
        self.id = id
        self.icon = icon
        self.title = title
        self.desc = desc
        self.price = price
        self.isEnabled = isEnabled
    }
}

// MARK: - Default Shop Rewards

extension ShopReward {
    static var defaultRewards: [ShopReward] {
        [
            ShopReward(icon: "🎮", title: "+30 минут игр", desc: "Дополнительное время", price: 50),
            ShopReward(icon: "📱", title: "+1 час экранного времени", desc: "На любой день", price: 80),
            ShopReward(icon: "🌙", title: "+30 минут перед сном", desc: "Сдвинуть время сна", price: 100),
            ShopReward(icon: "🍕", title: "Заказ пиццы", desc: "Твоя любимая!", price: 150),
            ShopReward(icon: "🎬", title: "Поход в кино", desc: "С друзьями!", price: 200),
            ShopReward(icon: "🎁", title: "Подарок по выбору", desc: "До 1000₽", price: 500)
        ]
    }
}

