//
//  AppStoreConfig.swift
//  ALADDIN Security
//
//  Created by AI Assistant on 2025-01-27.
//  Copyright © 2025 ALADDIN Security. All rights reserved.
//

import Foundation

/**
 * App Store Configuration
 * Конфигурация для публикации в App Store
 */

struct AppStoreConfig {
    
    // MARK: - App Information
    static let appName = "ALADDIN Security"
    static let bundleIdentifier = "com.aladdin.security"
    static let version = "1.0.0"
    static let buildNumber = "1"
    
    // MARK: - App Store Metadata
    static let appDescription = """
    ALADDIN Security - Комплексная защита семьи в цифровом мире
    
    🛡️ ЗАЩИТА СЕМЬИ:
    • VPN с российскими серверами
    • Родительский контроль
    • Защита от мошенничества
    • AI-помощник безопасности
    
    🔒 БЕЗОПАСНОСТЬ:
    • Шифрование AES-256
    • Защита от фишинга
    • Блокировка вредоносных сайтов
    • Мониторинг угроз в реальном времени
    
    👨‍👩‍👧‍👦 ДЛЯ ВСЕЙ СЕМЬИ:
    • Простой интерфейс для пожилых
    • Игровой интерфейс для детей
    • Расширенный контроль для родителей
    • AI-рекомендации по безопасности
    
    🇷🇺 РОССИЙСКИЕ ТЕХНОЛОГИИ:
    • Соответствие 152-ФЗ
    • Интеграция с Госуслугами
    • Российские серверы
    • Поддержка SBP и СберPay
    
    Скачайте ALADDIN Security и защитите свою семью!
    """
    
    static let keywords = [
        "безопасность",
        "семья",
        "VPN",
        "родительский контроль",
        "защита детей",
        "мошенничество",
        "фишинг",
        "антивирус",
        "AI",
        "искусственный интеллект",
        "152-ФЗ",
        "Госуслуги",
        "SBP",
        "СберPay",
        "российские технологии"
    ]
    
    static let category = "Utilities"
    static let subcategory = "Security"
    
    // MARK: - App Store Screenshots
    static let screenshots = [
        "screenshot_1_main_screen",
        "screenshot_2_vpn_interface",
        "screenshot_3_family_control",
        "screenshot_4_ai_assistant",
        "screenshot_5_settings",
        "screenshot_6_analytics"
    ]
    
    // MARK: - App Store Review Information
    static let reviewNotes = """
    ALADDIN Security - это комплексная система безопасности для семей.
    
    ОСНОВНЫЕ ФУНКЦИИ:
    1. VPN с российскими серверами
    2. Родительский контроль с AI
    3. Защита от мошенничества
    4. Специализированные интерфейсы для разных возрастов
    
    ТЕСТОВЫЕ АККАУНТЫ:
    - Демо режим доступен без регистрации
    - Полный функционал в течение 30 дней
    - Тестовые данные для всех функций
    
    ПРИМЕЧАНИЯ:
    - Приложение использует VPN для защиты трафика
    - Родительский контроль требует настройки профилей
    - AI-помощник работает на русском языке
    - Все данные хранятся в соответствии с 152-ФЗ
    """
    
    // MARK: - Privacy Information
    static let privacyPolicy = """
    Политика конфиденциальности ALADDIN Security
    
    1. СБОР ДАННЫХ:
    - Минимально необходимые данные для работы
    - Данные о безопасности (зашифрованы)
    - Анонимная аналитика производительности
    
    2. ИСПОЛЬЗОВАНИЕ ДАННЫХ:
    - Обеспечение безопасности семьи
    - Улучшение качества сервиса
    - Соответствие требованиям 152-ФЗ
    
    3. ЗАЩИТА ДАННЫХ:
    - Шифрование AES-256
    - Российские серверы
    - Регулярные аудиты безопасности
    
    4. ПРАВА ПОЛЬЗОВАТЕЛЯ:
    - Доступ к своим данным
    - Удаление данных
    - Отзыв согласия
    """
    
    // MARK: - App Store Connect Configuration
    static let appStoreConnectConfig = AppStoreConnectConfig(
        primaryLanguage: "ru",
        bundleId: bundleIdentifier,
        sku: "aladdin-security-ios",
        contentRights: true,
        ageRating: AgeRating(
            violence: .none,
            profanity: .none,
            sexualContent: .none,
            realisticViolence: .none,
            prolongedViolence: .none,
            sexualContentNudity: .none,
            sexualContentOrNudity: .none,
            alcoholTobaccoDrugs: .none,
            matureSuggestive: .none,
            horrorFear: .none,
            realisticViolence: .none,
            prolongedViolence: .none,
            sexualContentNudity: .none,
            sexualContentOrNudity: .none,
            alcoholTobaccoDrugs: .none,
            matureSuggestive: .none,
            horrorFear: .none
        )
    )
    
    // MARK: - In-App Purchase Configuration
    static let inAppPurchases = [
        InAppPurchase(
            productId: "com.aladdin.security.premium.monthly",
            type: .autoRenewableSubscription,
            duration: .monthly,
            price: 299.0,
            currency: "RUB",
            title: "ALADDIN Premium (Месяц)",
            description: "Полный доступ ко всем функциям безопасности"
        ),
        InAppPurchase(
            productId: "com.aladdin.security.premium.yearly",
            type: .autoRenewableSubscription,
            duration: .yearly,
            price: 2990.0,
            currency: "RUB",
            title: "ALADDIN Premium (Год)",
            description: "Полный доступ ко всем функциям безопасности со скидкой"
        )
    ]
    
    // MARK: - App Store Optimization
    static let asoKeywords = [
        "безопасность семьи",
        "VPN Россия",
        "родительский контроль",
        "защита детей",
        "антивирус мобильный",
        "AI безопасность",
        "152-ФЗ",
        "Госуслуги",
        "SBP",
        "СберPay"
    ]
    
    static let asoDescription = """
    ALADDIN Security - защита семьи в цифровом мире. VPN, родительский контроль, AI-помощник, защита от мошенничества. Российские технологии, соответствие 152-ФЗ.
    """
}

// MARK: - Supporting Types

struct AppStoreConnectConfig {
    let primaryLanguage: String
    let bundleId: String
    let sku: String
    let contentRights: Bool
    let ageRating: AgeRating
}

struct AgeRating {
    let violence: AgeRatingLevel
    let profanity: AgeRatingLevel
    let sexualContent: AgeRatingLevel
    let realisticViolence: AgeRatingLevel
    let prolongedViolence: AgeRatingLevel
    let sexualContentNudity: AgeRatingLevel
    let sexualContentOrNudity: AgeRatingLevel
    let alcoholTobaccoDrugs: AgeRatingLevel
    let matureSuggestive: AgeRatingLevel
    let horrorFear: AgeRatingLevel
}

enum AgeRatingLevel {
    case none
    case infrequent
    case frequent
    case intense
}

struct InAppPurchase {
    let productId: String
    let type: PurchaseType
    let duration: PurchaseDuration
    let price: Double
    let currency: String
    let title: String
    let description: String
}

enum PurchaseType {
    case autoRenewableSubscription
    case nonRenewingSubscription
    case consumable
    case nonConsumable
}

enum PurchaseDuration {
    case weekly
    case monthly
    case yearly
    case lifetime
}

