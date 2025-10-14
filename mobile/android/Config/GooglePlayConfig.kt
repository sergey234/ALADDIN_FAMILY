package com.aladdin.security.config

/**
 * Google Play Configuration
 * Конфигурация для публикации в Google Play
 */

object GooglePlayConfig {
    
    // MARK: - App Information
    const val APP_NAME = "ALADDIN Security"
    const val PACKAGE_NAME = "com.aladdin.security"
    const val VERSION_NAME = "1.0.0"
    const val VERSION_CODE = 1
    
    // MARK: - Google Play Store Metadata
    const val APP_DESCRIPTION = """
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
    
    val KEYWORDS = listOf(
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
    )
    
    const val CATEGORY = "TOOLS"
    const val CONTENT_RATING = "EVERYONE"
    
    // MARK: - Google Play Screenshots
    val SCREENSHOTS = listOf(
        "screenshot_1_main_screen",
        "screenshot_2_vpn_interface",
        "screenshot_3_family_control",
        "screenshot_4_ai_assistant",
        "screenshot_5_settings",
        "screenshot_6_analytics"
    )
    
    // MARK: - Google Play Review Information
    const val REVIEW_NOTES = """
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
    const val PRIVACY_POLICY = """
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
    
    // MARK: - Google Play Console Configuration
    val GOOGLE_PLAY_CONFIG = GooglePlayConsoleConfig(
        primaryLanguage = "ru",
        packageName = PACKAGE_NAME,
        contentRating = ContentRating(
            violence = ContentRatingLevel.NONE,
            profanity = ContentRatingLevel.NONE,
            sexualContent = ContentRatingLevel.NONE,
            realisticViolence = ContentRatingLevel.NONE,
            prolongedViolence = ContentRatingLevel.NONE,
            sexualContentNudity = ContentRatingLevel.NONE,
            sexualContentOrNudity = ContentRatingLevel.NONE,
            alcoholTobaccoDrugs = ContentRatingLevel.NONE,
            matureSuggestive = ContentRatingLevel.NONE,
            horrorFear = ContentRatingLevel.NONE
        ),
        targetSdkVersion = 34,
        minSdkVersion = 21,
        compileSdkVersion = 34
    )
    
    // MARK: - In-App Purchase Configuration
    val IN_APP_PURCHASES = listOf(
        InAppPurchase(
            productId = "com.aladdin.security.premium.monthly",
            type = PurchaseType.AUTO_RENEWABLE_SUBSCRIPTION,
            duration = PurchaseDuration.MONTHLY,
            price = 299.0,
            currency = "RUB",
            title = "ALADDIN Premium (Месяц)",
            description = "Полный доступ ко всем функциям безопасности"
        ),
        InAppPurchase(
            productId = "com.aladdin.security.premium.yearly",
            type = PurchaseType.AUTO_RENEWABLE_SUBSCRIPTION,
            duration = PurchaseDuration.YEARLY,
            price = 2990.0,
            currency = "RUB",
            title = "ALADDIN Premium (Год)",
            description = "Полный доступ ко всем функциям безопасности со скидкой"
        )
    )
    
    // MARK: - Google Play Optimization
    val ASO_KEYWORDS = listOf(
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
    )
    
    const val ASO_DESCRIPTION = """
    ALADDIN Security - защита семьи в цифровом мире. VPN, родительский контроль, AI-помощник, защита от мошенничества. Российские технологии, соответствие 152-ФЗ.
    """
    
    // MARK: - Permissions
    val REQUIRED_PERMISSIONS = listOf(
        "android.permission.INTERNET",
        "android.permission.ACCESS_NETWORK_STATE",
        "android.permission.ACCESS_WIFI_STATE",
        "android.permission.CHANGE_WIFI_STATE",
        "android.permission.VIBRATE",
        "android.permission.WAKE_LOCK",
        "android.permission.FOREGROUND_SERVICE",
        "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
    )
    
    val OPTIONAL_PERMISSIONS = listOf(
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.CAMERA",
        "android.permission.RECORD_AUDIO",
        "android.permission.READ_CONTACTS",
        "android.permission.READ_SMS",
        "android.permission.READ_CALL_LOG"
    )
    
    // MARK: - App Bundle Configuration
    val APP_BUNDLE_CONFIG = AppBundleConfig(
        enableDynamicDelivery = true,
        enableOnDemandDelivery = true,
        enableConditionalDelivery = true,
        enableAssetPacks = true,
        enableTextureCompression = true,
        enableLanguageSplits = true,
        enableDensitySplits = true
    )
}

// MARK: - Supporting Types

data class GooglePlayConsoleConfig(
    val primaryLanguage: String,
    val packageName: String,
    val contentRating: ContentRating,
    val targetSdkVersion: Int,
    val minSdkVersion: Int,
    val compileSdkVersion: Int
)

data class ContentRating(
    val violence: ContentRatingLevel,
    val profanity: ContentRatingLevel,
    val sexualContent: ContentRatingLevel,
    val realisticViolence: ContentRatingLevel,
    val prolongedViolence: ContentRatingLevel,
    val sexualContentNudity: ContentRatingLevel,
    val sexualContentOrNudity: ContentRatingLevel,
    val alcoholTobaccoDrugs: ContentRatingLevel,
    val matureSuggestive: ContentRatingLevel,
    val horrorFear: ContentRatingLevel
)

enum class ContentRatingLevel {
    NONE,
    INFREQUENT,
    FREQUENT,
    INTENSE
}

data class InAppPurchase(
    val productId: String,
    val type: PurchaseType,
    val duration: PurchaseDuration,
    val price: Double,
    val currency: String,
    val title: String,
    val description: String
)

enum class PurchaseType {
    AUTO_RENEWABLE_SUBSCRIPTION,
    NON_RENEWING_SUBSCRIPTION,
    CONSUMABLE,
    NON_CONSUMABLE
}

enum class PurchaseDuration {
    WEEKLY,
    MONTHLY,
    YEARLY,
    LIFETIME
}

data class AppBundleConfig(
    val enableDynamicDelivery: Boolean,
    val enableOnDemandDelivery: Boolean,
    val enableConditionalDelivery: Boolean,
    val enableAssetPacks: Boolean,
    val enableTextureCompression: Boolean,
    val enableLanguageSplits: Boolean,
    val enableDensitySplits: Boolean
)

