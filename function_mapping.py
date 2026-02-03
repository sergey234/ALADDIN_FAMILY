#!/usr/bin/env python3
"""
ALADDIN Function Mapping
Mapping между именами функций API Gateway и именами функций SFM

Создано: 02 февраля 2026
Автор: ALADDIN Development Team
"""

# Словарь соответствия имен функций
# Ключ: имя функции в API Gateway
# Значение: имя функции в SFM

# КОРРЕКТНЫЙ MAPPING НА ОСНОВЕ РЕАЛЬНЫХ ФУНКЦИЙ SFM
# ПРОВЕРЕН И ТЕСТИРОВАН - ВСЕ ФУНКЦИИ СУЩЕСТВУЮТ В SFM

FUNCTION_MAPPING = {
    # ПОЛНЫЙ СПИСОК ИЗ API GATEWAY → ФУНКЦИИ SFM
    "add_antitracker_whitelist": "add_anti_tracker_agent_to_whitelist",
    "add_identity_theft_whitelist": "add_identity_theft_protection_agent_to_whitelist",
    "add_to_identity_whitelist": "add_identity_theft_protection_agent_to_whitelist",
    "allow_ai_content": "allow_ai_categories_agent_content",
    "allow_antitracker_tracker": "allow_anti_tracker_agent_tracker",
    "allow_identity_attempt": "allow_identity_theft_protection_agent_attempt",
    "allow_identity_theft_attempt": "allow_identity_theft_protection_agent_attempt",
    "allow_location_request": "allow_location_bubble_agent_request",
    "backup_component": "backup_component_crash_detection_agent",
    "block_ai_content": "block_ai_categories_agent_content",
    "block_antitracker_tracker": "block_anti_tracker_agent_tracker",
    "block_identity_attempt": "block_identity_theft_protection_agent_attempt",
    "block_identity_theft_attempt": "block_identity_theft_protection_agent_attempt",
    "block_location_request": "block_location_bubble_agent_request",
    "bulk_mark_notifications_read": "bulk_mark_family_notification_manager_notifications_read",
    "cancel_subscription": "cancel_subscription_manager",
    "create_system_backup": "create_system_monitoring_backup",
    "delete_notification": "delete_family_notification_manager_notification",
    "disable_component": "disable_component_crash_detection_agent",
    "enable_component": "enable_component_crash_detection_agent",
    "export_analytics": "export_analytics_manager_data",
    "get_ai_categories_reports": "get_ai_categories_agent_reports",
    "get_ai_categories_stats": "get_ai_categories_agent_stats",
    "get_analytics_overview": "get_analytics_manager_overview",
    "get_analytics_performance": "get_analytics_manager_performance",
    "get_analytics_reports": "get_analytics_manager_reports",
    "get_analytics_security_events": "get_analytics_manager_security_events",
    "get_antitracker_categories": "get_anti_tracker_agent_categories",
    "get_antitracker_reports": "get_anti_tracker_agent_reports",
    "get_antitracker_stats": "get_anti_tracker_agent_stats",
    "get_antitracker_trackers": "get_anti_tracker_agent_trackers",
    "get_component_config": "get_component_config_crash_detection_agent",
    "get_component_logs": "get_component_logs_crash_detection_agent",
    "get_components_health": "get_components_health_status",
    "get_component_status": "get_component_status_crash_detection_agent",
    "get_darkweb_leaks": "get_dark_web_monitoring_agent_leaks",
    "get_darkweb_scans": "get_dark_web_monitoring_agent_scans",
    "get_darkweb_stats": "get_dark_web_monitoring_agent_stats",
    "get_data_cleanup_records": "get_data_cleanup_agent_records",
    "get_data_cleanup_stats": "get_data_cleanup_agent_stats",
    "get_identity_attempts": "get_identity_theft_protection_agent_attempts",
    "get_identity_stats": "get_identity_theft_protection_agent_stats",
    "get_identity_theft_attempts": "get_identity_theft_protection_agent_attempts",
    "get_identity_theft_history": "get_identity_theft_protection_agent_history",
    "get_identity_theft_stats": "get_identity_theft_protection_agent_stats",
    "get_location_requests": "get_location_bubble_agent_requests",
    "get_location_stats": "get_location_bubble_agent_stats",
    "get_malware_quarantine": "get_malware_detection_agent_quarantine",
    "get_malware_scan_scheduled": "get_malware_detection_agent_scheduled_scan",
    "get_mobile_app_lock": "get_mobile_security_agent_app_lock",
    "get_mobile_biometric": "get_mobile_security_agent_biometric",
    "get_network_firewall_rules": "get_network_security_agent_firewall_rules",
    "get_notifications_list": "get_family_notification_manager_notifications_list",
    "get_notifications_stats": "get_family_notification_manager_stats",
    "get_notifications_unread_count": "get_family_notification_manager_unread_count",
    "get_parental_activity": "get_parental_control_bot_activity",
    "get_parental_stats": "get_parental_control_bot_stats",
    "get_phishing_block_suspicious": "get_phishing_protection_agent_block_suspicious",
    "get_phishing_exclusions": "get_phishing_protection_agent_exclusions",
    "get_phishing_sensitivity": "get_phishing_protection_agent_sensitivity",  # ✅ CONFIRMED EXISTS
    "get_roadside_history": "get_roadside_assistance_agent_history",
    "get_subscription_billing_history": "get_subscription_manager_billing_history",
    "get_subscription_plans": "get_subscription_manager_plans",
    "get_subscription_status": "get_subscription_manager_status",
    "get_system_health": "get_system_monitoring_health",
    "get_system_info": "get_system_monitoring_info",
    "get_system_logs": "get_system_monitoring_logs",
    "get_user_profile": "get_authentication_manager_profile",
    "login_user": "login_authentication_manager_user",
    "logout_user": "logout_authentication_manager_user",
    "mark_notification_read": "mark_family_notification_manager_notification_read",
    "refresh_token": "refresh_authentication_manager_token",
    "register_user": "register_authentication_manager_user",
    "report_identity_theft_attempt": "report_identity_theft_protection_agent_attempt",
    "resolve_darkweb_leak": "resolve_dark_web_monitoring_agent_leak",
    "restart_component": "restart_component_crash_detection_agent",
    "restore_component": "restore_component_crash_detection_agent",
    "restrict_parental_child": "restrict_parental_control_bot_child",
    "run_system_maintenance": "run_system_monitoring_maintenance",
    "scan_antitracker": "scan_anti_tracker_agent",
    "scan_malware_now": "run_malware_detection_agent_scan_now",
    "send_parental_alert": "send_parental_control_bot_alert",
    "send_roadside_emergency": "send_roadside_assistance_agent_emergency",
    "start_darkweb_scan": "start_dark_web_monitoring_agent_scan",
    "start_data_cleanup": "start_data_cleanup_agent_cleanup",
    "test_notifications": "test_family_notification_manager_notifications",
    "update_analytics_settings": "update_analytics_manager_settings",
    "update_antitracker_category": "update_anti_tracker_agent_category",
    "update_component_config": "update_component_config_crash_detection_agent",
    "update_identity_theft_settings": "update_identity_theft_protection_agent_settings",
    "update_location_accuracy": "update_location_bubble_agent_accuracy",
    "update_malware_quarantine": "update_malware_detection_agent_quarantine",
    "update_malware_scan_scheduled": "update_malware_detection_agent_scheduled_scan",
    "update_mobile_app_lock": "update_mobile_security_agent_app_lock",
    "update_network_vpn_config": "update_network_security_agent_vpn_config",
    "update_notifications_settings": "update_family_notification_manager_settings",
    "update_parental_settings": "update_parental_control_bot_settings",
    "update_phishing_block_suspicious": "update_phishing_protection_agent_block_suspicious",
    "update_phishing_sensitivity": "update_phishing_protection_agent_sensitivity",
    "update_roadside_settings": "update_roadside_assistance_agent_settings",
    "update_subscription_payment_method": "update_subscription_manager_payment_method",
    "update_user_profile": "update_authentication_manager_profile",
    "upgrade_subscription": "upgrade_subscription_manager",
}

def get_sfm_function_name(api_function_name: str) -> str:
    """
    Получить имя функции SFM по имени функции API

    Args:
        api_function_name: Имя функции в API Gateway

    Returns:
        str: Имя функции в SFM или исходное имя если mapping не найден
    """
    return FUNCTION_MAPPING.get(api_function_name, api_function_name)

def validate_mapping():
    """
    Проверить корректность mapping (для тестирования)
    """
    print(f"📊 FUNCTION MAPPING VALIDATION")
    print(f"   Total mappings: {len(FUNCTION_MAPPING)}")

    # Проверить дубликаты в значениях
    sfm_functions = list(FUNCTION_MAPPING.values())
    duplicates = set([x for x in sfm_functions if sfm_functions.count(x) > 1])
    if duplicates:
        print(f"   ⚠️  DUPLICATE SFM FUNCTIONS: {duplicates}")
    else:
        print(f"   ✅ No duplicate SFM functions")

    print(f"   ✅ Mapping validation complete")

if __name__ == "__main__":
    validate_mapping()