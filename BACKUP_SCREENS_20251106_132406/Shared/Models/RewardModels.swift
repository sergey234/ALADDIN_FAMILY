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

// MARK: - Earning Way Model

struct EarningWay: Identifiable, Codable {
    let id: String
    var icon: String
    var title: String
    var subtitle: String
    var amount: Int  // Награда в единорогах (положительное число)
    var isEnabled: Bool
    
    init(id: String = UUID().uuidString, icon: String, title: String, subtitle: String, amount: Int, isEnabled: Bool = true) {
        self.id = id
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.amount = amount
        self.isEnabled = isEnabled
    }
}

extension EarningWay {
    static var defaultEarningWays: [EarningWay] {
        [
            EarningWay(id: "homework", icon: "📚", title: "Домашнее задание", subtitle: "+10 единорогов за задание", amount: 10, isEnabled: true),
            EarningWay(id: "chores", icon: "🧹", title: "Домашние обязанности", subtitle: "+5 единорогов за дело", amount: 5, isEnabled: true),
            EarningWay(id: "behavior", icon: "😊", title: "Хорошее поведение", subtitle: "+15 единорогов за день", amount: 15, isEnabled: true),
            EarningWay(id: "reading", icon: "📖", title: "Чтение книг", subtitle: "+20 единорогов за книгу", amount: 20, isEnabled: true),
            EarningWay(id: "achievement", icon: "🏆", title: "Достижение в учебе", subtitle: "+50 единорогов за 5", amount: 50, isEnabled: true)
        ]
    }
}

// MARK: - Punishment Reason Model

struct PunishmentReason: Identifiable, Codable {
    let id: String
    var icon: String
    var title: String
    var subtitle: String
    var amount: Int  // Штраф в единорогах (положительное число, будет отображаться с минусом)
    var isEnabled: Bool
    
    init(id: String = UUID().uuidString, icon: String, title: String, subtitle: String, amount: Int, isEnabled: Bool = true) {
        self.id = id
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.amount = amount
        self.isEnabled = isEnabled
    }
}

extension PunishmentReason {
    static var defaultPunishmentReasons: [PunishmentReason] {
        [
            PunishmentReason(id: "no_homework", icon: "📚", title: "Не сделал домашнее задание", subtitle: "Забыл или отказался делать", amount: 10, isEnabled: true),
            PunishmentReason(id: "bad_behavior", icon: "😡", title: "Плохое поведение", subtitle: "Грубость, ссоры, непослушание", amount: 15, isEnabled: true),
            PunishmentReason(id: "limit_violation", icon: "⏰", title: "Нарушение лимитов", subtitle: "Превышение экранного времени", amount: 5, isEnabled: true),
            PunishmentReason(id: "bypass_attempt", icon: "🚫", title: "Обход блокировок", subtitle: "Попытка обойти контроль", amount: 20, isEnabled: true),
            PunishmentReason(id: "custom", icon: "😤", title: "Своя причина", subtitle: "Родители указывают сами", amount: 1, isEnabled: true)
        ]
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

