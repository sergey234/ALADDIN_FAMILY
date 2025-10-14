package com.aladdin.mobile.api

import kotlinx.serialization.Serializable

// MARK: - Support Categories Enum для Android
@Serializable
enum class SupportCategory(val value: String) {
    // Основные категории
    GENERAL("general"),
    SECURITY("security"),
    FAMILY("family"),
    SETTINGS("settings"),
    HELP("help"),
    
    // Технические категории
    TECHNICAL("technical"),
    INSTALLATION("installation"),
    CONFIGURATION("configuration"),
    TROUBLESHOOTING("troubleshooting"),
    PERFORMANCE("performance"),
    
    // Безопасность
    PARENTAL_CONTROL("parental_control"),
    CHILD_PROTECTION("child_protection"),
    ELDERLY_PROTECTION("elderly_protection"),
    DEVICE_SECURITY("device_security"),
    NETWORK_SECURITY("network_security"),
    DATA_PROTECTION("data_protection"),
    
    // VPN и сеть
    VPN("vpn"),
    NETWORK("network"),
    CONNECTIVITY("connectivity"),
    FIREWALL("firewall"),
    
    // Платежи и подписки
    PAYMENTS("payments"),
    SUBSCRIPTION("subscription"),
    BILLING("billing"),
    REFUNDS("refunds"),
    
    // Кризисные ситуации
    CRISIS("crisis"),
    EMERGENCY("emergency"),
    PSYCHOLOGICAL("psychological"),
    CHILD_SAFETY("child_safety"),
    CYBERBULLYING("cyberbullying"),
    
    // Дополнительные
    FEEDBACK("feedback"),
    SUGGESTIONS("suggestions"),
    COMPLAINTS("complaints"),
    OTHER("other");
    
    // MARK: - Computed Properties
    val displayName: String
        get() = when (this) {
            GENERAL -> "Общие вопросы"
            SECURITY -> "Безопасность"
            FAMILY -> "Семья"
            SETTINGS -> "Настройки"
            HELP -> "Помощь"
            TECHNICAL -> "Техническая поддержка"
            INSTALLATION -> "Установка"
            CONFIGURATION -> "Конфигурация"
            TROUBLESHOOTING -> "Устранение неполадок"
            PERFORMANCE -> "Производительность"
            PARENTAL_CONTROL -> "Родительский контроль"
            CHILD_PROTECTION -> "Защита детей"
            ELDERLY_PROTECTION -> "Защита пожилых"
            DEVICE_SECURITY -> "Безопасность устройства"
            NETWORK_SECURITY -> "Сетевая безопасность"
            DATA_PROTECTION -> "Защита данных"
            VPN -> "VPN"
            NETWORK -> "Сеть"
            CONNECTIVITY -> "Подключение"
            FIREWALL -> "Файрвол"
            PAYMENTS -> "Платежи"
            SUBSCRIPTION -> "Подписка"
            BILLING -> "Биллинг"
            REFUNDS -> "Возвраты"
            CRISIS -> "Кризисная ситуация"
            EMERGENCY -> "Экстренная помощь"
            PSYCHOLOGICAL -> "Психологическая поддержка"
            CHILD_SAFETY -> "Безопасность детей"
            CYBERBULLYING -> "Кибербуллинг"
            FEEDBACK -> "Обратная связь"
            SUGGESTIONS -> "Предложения"
            COMPLAINTS -> "Жалобы"
            OTHER -> "Другое"
        }
    
    val description: String
        get() = when (this) {
            GENERAL -> "Общие вопросы и информация"
            SECURITY -> "Вопросы безопасности и защиты"
            FAMILY -> "Семейные настройки и профили"
            SETTINGS -> "Настройки приложения"
            HELP -> "Справка и инструкции"
            TECHNICAL -> "Технические проблемы и решения"
            INSTALLATION -> "Установка и обновления"
            CONFIGURATION -> "Настройка параметров"
            TROUBLESHOOTING -> "Диагностика и исправление ошибок"
            PERFORMANCE -> "Оптимизация производительности"
            PARENTAL_CONTROL -> "Настройка родительского контроля"
            CHILD_PROTECTION -> "Защита детей в интернете"
            ELDERLY_PROTECTION -> "Защита пожилых пользователей"
            DEVICE_SECURITY -> "Безопасность мобильного устройства"
            NETWORK_SECURITY -> "Защита сетевого соединения"
            DATA_PROTECTION -> "Защита персональных данных"
            VPN -> "Настройка и использование VPN"
            NETWORK -> "Сетевые подключения"
            CONNECTIVITY -> "Проблемы с подключением"
            FIREWALL -> "Настройка файрвола"
            PAYMENTS -> "Платежи и транзакции"
            SUBSCRIPTION -> "Управление подпиской"
            BILLING -> "Счета и оплата"
            REFUNDS -> "Возврат средств"
            CRISIS -> "Кризисные ситуации и экстренная помощь"
            EMERGENCY -> "Экстренная поддержка"
            PSYCHOLOGICAL -> "Психологическая помощь"
            CHILD_SAFETY -> "Экстренная помощь по безопасности детей"
            CYBERBULLYING -> "Помощь при кибербуллинге"
            FEEDBACK -> "Отзывы и предложения"
            SUGGESTIONS -> "Предложения по улучшению"
            COMPLAINTS -> "Жалобы и проблемы"
            OTHER -> "Другие вопросы"
        }
    
    val priority: SupportPriority
        get() = when (this) {
            CRISIS, EMERGENCY, CHILD_SAFETY, CYBERBULLYING -> SupportPriority.CRITICAL
            PSYCHOLOGICAL, TECHNICAL, TROUBLESHOOTING -> SupportPriority.HIGH
            SECURITY, PARENTAL_CONTROL, CHILD_PROTECTION, ELDERLY_PROTECTION -> SupportPriority.HIGH
            VPN, NETWORK, CONNECTIVITY, DEVICE_SECURITY -> SupportPriority.MEDIUM
            PAYMENTS, SUBSCRIPTION, BILLING -> SupportPriority.MEDIUM
            SETTINGS, CONFIGURATION, PERFORMANCE -> SupportPriority.MEDIUM
            GENERAL, HELP, FEEDBACK, SUGGESTIONS -> SupportPriority.LOW
            OTHER, COMPLAINTS -> SupportPriority.LOW
        }
    
    val icon: String
        get() = when (this) {
            GENERAL -> "ic_help_outline"
            SECURITY -> "ic_security"
            FAMILY -> "ic_family"
            SETTINGS -> "ic_settings"
            HELP -> "ic_help"
            TECHNICAL -> "ic_build"
            INSTALLATION -> "ic_download"
            CONFIGURATION -> "ic_tune"
            TROUBLESHOOTING -> "ic_bug_report"
            PERFORMANCE -> "ic_speed"
            PARENTAL_CONTROL -> "ic_child_care"
            CHILD_PROTECTION -> "ic_child_friendly"
            ELDERLY_PROTECTION -> "ic_elderly"
            DEVICE_SECURITY -> "ic_phone_android"
            NETWORK_SECURITY -> "ic_network_check"
            DATA_PROTECTION -> "ic_lock"
            VPN -> "ic_vpn_lock"
            NETWORK -> "ic_wifi"
            CONNECTIVITY -> "ic_signal_cellular_alt"
            FIREWALL -> "ic_security"
            PAYMENTS -> "ic_payment"
            SUBSCRIPTION -> "ic_repeat"
            BILLING -> "ic_receipt"
            REFUNDS -> "ic_undo"
            CRISIS -> "ic_warning"
            EMERGENCY -> "ic_emergency"
            PSYCHOLOGICAL -> "ic_favorite"
            CHILD_SAFETY -> "ic_child_care"
            CYBERBULLYING -> "ic_report"
            FEEDBACK -> "ic_feedback"
            SUGGESTIONS -> "ic_lightbulb"
            COMPLAINTS -> "ic_report_problem"
            OTHER -> "ic_more_horiz"
        }
    
    val color: String
        get() = when (this) {
            CRISIS, EMERGENCY, CHILD_SAFETY, CYBERBULLYING -> "error"
            PSYCHOLOGICAL, TECHNICAL, TROUBLESHOOTING -> "warning"
            SECURITY, PARENTAL_CONTROL, CHILD_PROTECTION, ELDERLY_PROTECTION -> "accent"
            VPN, NETWORK, CONNECTIVITY, DEVICE_SECURITY -> "primary"
            PAYMENTS, SUBSCRIPTION, BILLING -> "secondary"
            SETTINGS, CONFIGURATION, PERFORMANCE -> "info"
            GENERAL, HELP, FEEDBACK, SUGGESTIONS -> "success"
            OTHER, COMPLAINTS -> "text"
        }
}

// MARK: - Support Priority Enum
@Serializable
enum class SupportPriority(val value: String) {
    LOW("low"),
    MEDIUM("medium"),
    HIGH("high"),
    CRITICAL("critical");
    
    val displayName: String
        get() = when (this) {
            LOW -> "Низкий"
            MEDIUM -> "Средний"
            HIGH -> "Высокий"
            CRITICAL -> "Критический"
        }
    
    val description: String
        get() = when (this) {
            LOW -> "Обычный вопрос, не требует срочного решения"
            MEDIUM -> "Важный вопрос, требует внимания"
            HIGH -> "Срочный вопрос, требует быстрого решения"
            CRITICAL -> "Критическая ситуация, требует немедленного решения"
        }
    
    val responseTimeMillis: Long
        get() = when (this) {
            LOW -> 24 * 60 * 60 * 1000L // 24 часа
            MEDIUM -> 4 * 60 * 60 * 1000L // 4 часа
            HIGH -> 1 * 60 * 60 * 1000L // 1 час
            CRITICAL -> 15 * 60 * 1000L // 15 минут
        }
    
    val color: String
        get() = when (this) {
            LOW -> "success"
            MEDIUM -> "info"
            HIGH -> "warning"
            CRITICAL -> "error"
        }
}

// MARK: - Crisis Type Enum
@Serializable
enum class CrisisType(val value: String) {
    CHILD_SAFETY("child_safety"),
    CYBERBULLYING("cyberbullying"),
    PSYCHOLOGICAL("psychological"),
    EMERGENCY("emergency"),
    SECURITY("security"),
    OTHER("other");
    
    val displayName: String
        get() = when (this) {
            CHILD_SAFETY -> "Безопасность детей"
            CYBERBULLYING -> "Кибербуллинг"
            PSYCHOLOGICAL -> "Психологическая помощь"
            EMERGENCY -> "Экстренная ситуация"
            SECURITY -> "Безопасность"
            OTHER -> "Другое"
        }
    
    val description: String
        get() = when (this) {
            CHILD_SAFETY -> "Критическая ситуация с безопасностью ребенка"
            CYBERBULLYING -> "Случай кибербуллинга или травли"
            PSYCHOLOGICAL -> "Психологическая кризисная ситуация"
            EMERGENCY -> "Экстренная ситуация, требующая немедленного вмешательства"
            SECURITY -> "Критическая угроза безопасности"
            OTHER -> "Другая кризисная ситуация"
        }
    
    val urgencyLevel: Int
        get() = when (this) {
            CHILD_SAFETY, EMERGENCY -> 1
            CYBERBULLYING, SECURITY -> 2
            PSYCHOLOGICAL -> 3
            OTHER -> 4
        }
}

