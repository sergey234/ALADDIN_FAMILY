import SwiftUI

/// 🎮 Games Settings Manager
/// Singleton для хранения всех настроек игр
/// Хранит настройки в UserDefaults через @AppStorage
@MainActor
class GamesSettingsManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = GamesSettingsManager()
    
    // MARK: - AppStorage для сохранения настроек
    
    // 🛡️ ЮНЫЙ ЗАЩИТНИК (YoungDefender)
    @AppStorage("game_young_defender_enabled") var youngDefenderEnabled: Bool = true
    @AppStorage("game_young_defender_lesson_reward") var lessonReward: Int = 20
    @AppStorage("game_young_defender_bonus_5lessons") var bonus5Lessons: Int = 50
    @AppStorage("game_young_defender_bonus_all6") var bonusAll6: Int = 100
    
    // 🦄 ПИТОМЕЦ (UnicornPet)
    @AppStorage("game_pet_enabled") var petEnabled: Bool = true
    @AppStorage("game_pet_feed_cost") var petFeedCost: Int = 5
    @AppStorage("game_pet_play_cost") var petPlayCost: Int = 3
    @AppStorage("game_pet_pet_cost") var petPetCost: Int = 2
    @AppStorage("game_pet_care_bonus") var petCareBonus: Int = 20
    
    // 🕵️ Я ЗАЩИТНИК (FamilyProtector)
    @AppStorage("game_protector_enabled") var protectorEnabled: Bool = true
    @AppStorage("game_protector_phishing_reward") var phishingReward: Int = 5
    @AppStorage("game_protector_device_reward") var deviceReward: Int = 10
    @AppStorage("game_protector_communication_reward") var communicationReward: Int = 15
    @AppStorage("game_protector_weekly_test_bonus") var weeklyTestBonus: Int = 50
    
    // 🏆 ТУРНИР (FamilyTournament)
    @AppStorage("game_tournament_enabled") var tournamentEnabled: Bool = true
    @AppStorage("game_tournament_first_place") var firstPlaceReward: Int = 50
    @AppStorage("game_tournament_second_place") var secondPlaceReward: Int = 30
    @AppStorage("game_tournament_third_place") var thirdPlaceReward: Int = 20
    @AppStorage("game_tournament_participation") var participationReward: Int = 10
    @AppStorage("game_tournament_duration_days") var durationDays: Int = 7
    
    // 🏪 МАГАЗИН (Shop)
    @AppStorage("game_shop_enabled") var shopEnabled: Bool = true
    @AppStorage("game_shop_confirm_purchases") var confirmPurchases: Bool = true
    @AppStorage("game_shop_daily_limit") var dailyLimit: Int = 200
    
    // Цены товаров магазина
    @AppStorage("game_shop_game_30min_price") var game30minPrice: Int = 50
    @AppStorage("game_shop_screen_1hour_price") var screen1hourPrice: Int = 80
    @AppStorage("game_shop_sleep_30min_price") var sleep30minPrice: Int = 100
    @AppStorage("game_shop_pizza_price") var pizzaPrice: Int = 150
    @AppStorage("game_shop_cinema_price") var cinemaPrice: Int = 200
    @AppStorage("game_shop_gift_price") var giftPrice: Int = 500
    
    // 📊 ОБЩИЕ НАСТРОЙКИ
    @AppStorage("game_notifications_enabled") var notificationsEnabled: Bool = true
    @AppStorage("game_achievements_enabled") var achievementsEnabled: Bool = true
    
    // MARK: - Init
    
    private init() {
        print("✅ GamesSettingsManager инициализирован")
    }
    
    // MARK: - Methods
    
    /// Сброс всех настроек к базовым значениям
    func resetToDefaults() {
        youngDefenderEnabled = true
        lessonReward = 20
        bonus5Lessons = 50
        bonusAll6 = 100
        
        petEnabled = true
        petFeedCost = 5
        petPlayCost = 3
        petPetCost = 2
        petCareBonus = 20
        
        protectorEnabled = true
        phishingReward = 5
        deviceReward = 10
        communicationReward = 15
        weeklyTestBonus = 50
        
        tournamentEnabled = true
        firstPlaceReward = 50
        secondPlaceReward = 30
        thirdPlaceReward = 20
        participationReward = 10
        durationDays = 7
        
        shopEnabled = true
        confirmPurchases = true
        dailyLimit = 200
        
        game30minPrice = 50
        screen1hourPrice = 80
        sleep30minPrice = 100
        pizzaPrice = 150
        cinemaPrice = 200
        giftPrice = 500
    }
}


