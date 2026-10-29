import Foundation

/// F1a / F1: канон id пустых карточек pay-pains (§20–21).
/// Скрываем с глаз. Ключи локализации и типы тарифа **не** удаляем.
enum PayPainsHiddenComponents {

    // MARK: - Component ids (Advanced / Network / Parental)

    /// Единый список. Карточка с таким id не рисуется.
    static let hiddenComponentIds: Set<String> = [
        // Advanced — мессенджеры / игры / браузер
        "telegram_security_bot",
        "whatsapp_security_bot",
        "instagram_security_bot",
        "max_messenger_security_bot",
        "gaming_security_bot",
        "browser_security_bot",
        // Advanced — приватность
        "location_bubble_agent",
        "personal_data_cleanup_agent",
        "anti_tracker_agent",
        // Advanced — мониторинг (пустые / нечестные)
        "dark_web_monitoring_agent",
        "russian_identity_theft_protection_agent",
        "ai_categories_agent",
        "driving_reports_agent",
        // Network — эвакуатор / диспетчер / авария как 112
        "roadside_assistance_agent",
        "emergency_response_bot",
        "emergency_event_manager",
        "crash_detection_agent",
        // Parental — обещают чтение переписок
        "self_harm_detection_agent",
        "grooming_detection_agent",
        "online_predators_agent",
        "psychological_support_agent",
    ]

    /// Псевдо-id UI без ComponentToggleCard (VPN-остатки на Network).
    static let hiddenUIElementIds: Set<String> = [
        "network_kill_switch",
        "network_dns_leak",
        "network_server_selection",
        "network_help_kill_switch",
        "network_help_dns_leak",
    ]

    static func isComponentHidden(_ componentId: String) -> Bool {
        hiddenComponentIds.contains(componentId)
    }

    static func isUIElementHidden(_ elementId: String) -> Bool {
        hiddenUIElementIds.contains(elementId)
    }

    // MARK: - Целые секции Advanced (если прячем все карточки внутри)

    /// Safari-фильтр и семейный блок в Advanced — дело на двери «Ребёнок» / Семья (§20).
    static let hideAdvancedSafariSection = true
    static let hideAdvancedFamilySection = true
    static let hideAdvancedMessengersSection = true
    static let hideAdvancedPrivacySection = true
    static let hideAdvancedMonitoringSection = true
}
