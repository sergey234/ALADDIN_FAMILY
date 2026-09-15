import Foundation

/// Slim RU/EN table for the widget extension (no LocalizationManager in appex).
/// Keys match `LocalizationManager` / LOC-I checklist for SSOT.
enum WidgetL10n {
    static func localized(_ key: String) -> String {
        let preferRU = (Locale.preferredLanguages.first ?? "en").hasPrefix("ru")
        let table = preferRU ? ru : en
        return table[key] ?? en[key] ?? key
    }

    private static let ru: [String: String] = [
        "nav_screen_analytics": "Аналитика",
        "elderly_appointments_time_label": "Время:",
        "family_protection_accessibility": "Защита семьи",
        "nav_screen_network_protection": "Защита сети",
        "widget_label_blocks": "Блокировок:",
        "widget_label_data": "Данные:",
        "widget_label_children_online": "Детей онлайн:",
        "widget_label_apps": "Приложения:",
        "widget_label_sites": "Сайты:",
        "widget_label_server": "Сервер:",
        "widget_label_speed": "Скорость:",
        "widget_label_threats": "Угроз:",
    ]

    private static let en: [String: String] = [
        "nav_screen_analytics": "Analytics",
        "elderly_appointments_time_label": "Time:",
        "family_protection_accessibility": "Family protection",
        "nav_screen_network_protection": "Network Protection",
        "widget_label_blocks": "Blocked:",
        "widget_label_data": "Data:",
        "widget_label_children_online": "Children online:",
        "widget_label_apps": "Apps:",
        "widget_label_sites": "Sites:",
        "widget_label_server": "Server:",
        "widget_label_speed": "Speed:",
        "widget_label_threats": "Threats:",
    ]
}
