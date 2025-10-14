# 🎯 КОМПЛЕКСНЫЙ ОТЧЕТ ПО АНАЛИЗУ ИМПОРТОВ СИСТЕМЫ ALADDIN
📅 Дата анализа: 2025-10-06T03:50:09.116209

## 📊 СВОДКА ПО СИСТЕМЕ
- **Всего папок проанализировано:** 5
- **Всего файлов:** 515
- **Всего потенциальных проблем:** 562

## 📁 ПАПКА: SECURITY/
- **Файлов:** 514
- **Успешно проанализировано:** 511
- **Ошибок:** 3
- **Потенциальных проблем:** 562

### ⚠️ Файлы с потенциальными проблемами:
- **security/search_indexer.py**
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/optimized_safe_function_manager.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт enum.Enum может быть неиспользуемым
- **security/async_io_manager.py**
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт concurrent.futures может быть неиспользуемым
- **security/compliance_reporting.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт dataclasses.dataclass может быть неиспользуемым
- **security/test_pagination.py**
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт pagination_system.PaginationSystem может быть неиспользуемым
  🟡 Импорт pagination_system.initialize_pagination_system может быть неиспользуемым
- **security/security_analytics.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт dataclasses.field может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/health_check_system.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/security_reporting.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/security_monitoring_fakeradar_expansion.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/test_smart_monitoring_methods.py**
  🟡 Импорт smart_monitoring.AlertStatus может быть неиспользуемым
  🟡 Импорт datetime.datetime может быть неиспользуемым
- **security/security_monitoring.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/test_mode_manager.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
- **security/security_analytics_russian_banking_expansion.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/incident_response.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт dataclasses.field может быть неиспользуемым
- **security/test_search_methods.py**
  🔴 Импорт security.safe_function_manager.FunctionStatus может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/enhanced_safe_function_manager.py**
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🔴 Импорт core.base.SecurityBase может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.safe_function_manager.FunctionStatus может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.safe_function_manager.SecurityFunction может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/lazy_wrappers.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт datetime.datetime может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
- **security/zero_trust_manager.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/test_lazy_loading.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт lazy_wrappers.LazyWrapper может быть неиспользуемым
  🔴 Импорт lazy_wrappers.LazyWrapperManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/compliance_audit.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт dataclasses.dataclass может быть неиспользуемым
- **security/memory_integration.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Set может быть неиспользуемым
- **security/test_demo_function.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🔴 Импорт core.base.SecurityLevel может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🟡 Импорт core.base.ComponentStatus может быть неиспользуемым
- **security/safe_function_manager.py**
  🔴 Импорт security.health_check_system.HealthCheckSystem может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.incident_response.IncidentResponseSystem может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.security_analytics.SecurityAnalytics может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/memory_optimization_system.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
- **security/pagination_system.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
- **security/test_critical_functions.py**
  🟡 Импорт unittest может быть неиспользуемым
  🟡 Импорт concurrent.futures.ThreadPoolExecutor может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/ai_optimization_engine.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/russian_threat_intelligence_original_backup_20250103.py**
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт aiohttp может быть неиспользуемым
- **security/device_security_original_backup_20250103.py**
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
- **security/advanced_monitoring_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/test_enhanced_features.py**
  🟡 Импорт smart_monitoring.AlertRule может быть неиспользуемым
  🟡 Импорт smart_monitoring.AlertSeverity может быть неиспользуемым
- **security/safe_function_manager_backup_20251006_024841.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🔴 Импорт security.async_io_manager.get_io_manager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.health_check_system.HealthCheckSystem может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.incident_response.IncidentResponseSystem может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.security_analytics.SecurityAnalytics может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/security_analytics_antifrod_expansion.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/test_memory_optimization.py**
  🟡 Импорт typing.List может быть неиспользуемым
- **security/security_monitoring_backup.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт pathlib.Path может быть неиспользуемым
- **security/microservices/api_gateway.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/microservices/safe_function_manager_integration.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
- **security/microservices/user_interface_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/microservices/load_balancer.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/microservices/rate_limiter.py**
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/microservices/emergency_base_models.py**
  🟡 Импорт asyncio может быть неиспользуемым
- **security/microservices/wake_up_systems.py**
  🟡 Импорт os может быть неиспользуемым
- **security/microservices/emergency_base_models_refactored.py**
  🟡 Импорт asyncio может быть неиспользуемым
- **security/bots/integration_test_suite.py**
  🟡 Импорт sys может быть неиспользуемым
  🔴 Импорт core.base.SecurityBase может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/bots/network_security_bot.py**
  🟡 Импорт core.base.CoreBase может быть неиспользуемым
  🔴 Импорт security.base.SecurityBase может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/bots/incognito_protection_bot_telegram_expansion.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/bots/gaming_security_bot.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/bots/analytics_bot.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/bots/mobile_navigation_bot.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/bots/parental_control_bot.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/bots/instagram_security_bot.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/bots/browser_security_bot.py**
  🟡 Импорт urllib.parse может быть неиспользуемым
- **security/bots/website_navigation_bot.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/bots/components/encryption_manager.py**
  🟡 Импорт threading может быть неиспользуемым
- **security/hashes/security_hashes.py**
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт core.base.ComponentStatus может быть неиспользуемым
- **security/types/security_types.py**
  🟡 Импорт typing.List может быть неиспользуемым
- **security/lazy_wrappers/lazy_circuit_breaker_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_financial_protection_hub_enhanced_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_rate_limiter_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_device_security_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_financial_protection_hub_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_data_protection_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_behavioral_analytics_engine_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_advanced_monitoring_manager_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_anti_fraud_master_ai_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_notification_bot_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_emergency_response_bot_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_network_monitoring_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_password_security_agent_enhanced_v2_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_mobile_security_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_intrusion_prevention_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_incident_response_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_smart_monitoring_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_safe_function_manager_backup_20251005_121831_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_malware_protection_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_safe_function_manager_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_password_security_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_user_interface_manager_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_threat_detection_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_auto_scaling_engine_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_super_ai_support_assistant_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_super_ai_support_assistant_improved_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_family_profile_manager_enhanced_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_security_analytics_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_emergency_event_manager_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_gaming_security_bot_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_child_interface_manager_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_network_security_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_policy_engine_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_threat_intelligence_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_mobile_security_agent_enhanced_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_incident_response_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_parent_control_panel_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_mobile_security_agent_backup_20250921_103531_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_parental_control_bot_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_compliance_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/lazy_wrappers/lazy_phishing_protection_agent_wrapper.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт importlib.util может быть неиспользуемым
- **security/ci_cd/ci_pipeline_manager.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/vpn/test_business_analytics_functionality.py**
  🟡 Импорт os может быть неиспользуемым
- **security/vpn/sleep_mode_manager.py**
  🟡 Импорт signal может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
- **security/vpn/test_two_factor_auth_functionality.py**
  🟡 Импорт os может быть неиспользуемым
- **security/vpn/test_final_integration.py**
  🟡 Импорт typing.List может быть неиспользуемым
- **security/vpn/test_compliance_152_fz.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт compliance.no_logs_policy.LogType может быть неиспользуемым
- **security/vpn/auto_monitor.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/vpn/auto_sleep_manager.py**
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт typing.Any может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/vpn/test_security_systems.py**
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт auth.two_factor_auth.verify_2fa_code может быть неиспользуемым
- **security/vpn/test_vpn_modules.py**
  🟡 Импорт os может быть неиспользуемым
- **security/vpn/test_performance_manager_functionality.py**
  🟡 Импорт os может быть неиспользуемым
  🔴 Импорт performance.performance_manager.PerformanceMode может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/vpn/test_vpn_modules_fixed.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт collections.defaultdict может быть неиспользуемым
- **security/vpn/security_integration.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт protection.ddos_protection.check_request может быть неиспользуемым
  🟡 Импорт protection.intrusion_detection.analyze_request может быть неиспользуемым
  🟡 Импорт protection.rate_limiter.check_rate_limit может быть неиспользуемым
- **security/vpn/test_performance_features.py**
  🟡 Импорт logging может быть неиспользуемым
- **security/vpn/test_intrusion_detection_functionality.py**
  🟡 Импорт os может быть неиспользуемым
- **security/vpn/test_all_vpn_modules.py**
  🟡 Импорт datetime.datetime может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/vpn/ui/vpn_interface.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
- **security/vpn/auth/two_factor_auth.py**
  🟡 Импорт hmac может быть неиспользуемым
  🟡 Импорт smtplib может быть неиспользуемым
  🟡 Импорт time может быть неиспользуемым
  🟡 Импорт dataclasses.asdict может быть неиспользуемым
  🟡 Импорт email.mime.multipart.MIMEMultipart может быть неиспользуемым
  🟡 Импорт email.mime.text.MIMEText может быть неиспользуемым
- **security/vpn/web/vpn_variant_1.py**
  🟡 Импорт flask.jsonify может быть неиспользуемым
- **security/vpn/web/vpn_web_server.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт time может быть неиспользуемым
  🟡 Импорт datetime.datetime может быть неиспользуемым
- **security/vpn/web/vpn_web_interface.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
- **security/vpn/web/vpn_variant_2.py**
  🟡 Импорт flask.jsonify может быть неиспользуемым
- **security/vpn/integration/aladdin_vpn_integration.py**
  🟡 Импорт logging может быть неиспользуемым
- **security/vpn/features/split_tunneling.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Set может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт asyncio может быть неиспользуемым
- **security/vpn/features/multi_hop.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/features/auto_reconnect.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/tests/unit/test_architecture_components.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт tempfile может быть неиспользуемым
  🟡 Импорт unittest.mock.patch может быть неиспользуемым
  🟡 Импорт unittest.mock.MagicMock может быть неиспользуемым
  🔴 Импорт config.vpn_constants.ServerStatus может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт config.vpn_constants.SecurityLevel может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт config.vpn_constants.ErrorCode может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.VPNServer может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.VPNClient может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.SecurityManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.DDoSProtection может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.RateLimiter может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.IntrusionDetection может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.AuthenticationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.TwoFactorAuth может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.Logger может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.AuditLogger может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.MonitoringManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.MetricsCollector может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.ConfigurationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.NetworkManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.EncryptionManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.DatabaseManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.APIManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт interfaces.vpn_protocols.IntegrationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.VPNServerType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.VPNClientType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.SecuritySystemType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.AuthSystemType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.LoggerType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт factories.vpn_factory.MonitoringSystemType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🟡 Импорт di.dependency_injection.ServiceRegistration может быть неиспользуемым
  🟡 Импорт di.dependency_injection.LifecycleType может быть неиспользуемым
  🟡 Импорт di.dependency_injection.get_container может быть неиспользуемым
  🔴 Импорт di.dependency_injection.register_vpn_services может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт di.dependency_injection.create_vpn_system может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт exceptions.vpn_exceptions.VPNConfigurationError может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт exceptions.vpn_exceptions.InvalidCredentialsError может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🟡 Импорт retry.retry_handler.CircuitState может быть неиспользуемым
  🟡 Импорт retry.retry_handler.retry может быть неиспользуемым
  🟡 Импорт retry.retry_handler.circuit_breaker может быть неиспользуемым
  🟡 Импорт graceful.graceful_degradation.graceful_degradation может быть неиспользуемым
- **security/vpn/tests/unit/test_security_systems.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт unittest.mock.Mock может быть неиспользуемым
  🟡 Импорт unittest.mock.patch может быть неиспользуемым
  🟡 Импорт unittest.mock.MagicMock может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🔴 Импорт exceptions.vpn_exceptions.DDoSAttackDetectedError может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт exceptions.vpn_exceptions.RateLimitExceededError может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт exceptions.vpn_exceptions.IntrusionDetectedError может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/vpn/tests/integration/test_vpn_integration.py**
  🟡 Импорт unittest.mock.Mock может быть неиспользуемым
  🟡 Импорт unittest.mock.MagicMock может быть неиспользуемым
- **security/vpn/models/__init__.py**
  🔴 Импорт vpn_models.* может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/vpn/models/vpn_models.py**
  🟡 Импорт enum.Enum может быть неиспользуемым
  🟡 Импорт pydantic.root_validator может быть неиспользуемым
- **security/vpn/compliance/data_localization.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
- **security/vpn/compliance/integration.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт no_logs_policy.LogType может быть неиспользуемым
- **security/vpn/compliance/no_logs_policy.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт typing.Set может быть неиспользуемым
- **security/vpn/compliance/russia_compliance.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/vpn/integrations/external_services.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/vpn/audit_logging/audit_logger.py**
  🟡 Импорт logging.handlers может быть неиспользуемым
- **security/vpn/protection/intrusion_detection.py**
  🟡 Импорт ipaddress может быть неиспользуемым
  🟡 Импорт random может быть неиспользуемым
  🟡 Импорт string может быть неиспользуемым
- **security/vpn/protection/rate_limiter.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт dataclasses.asdict может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
- **security/vpn/protection/ddos_protection.py**
  🟡 Импорт ipaddress может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
- **security/vpn/factories/vpn_factory.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
- **security/vpn/scripts/check_legal_compliance.py**
  🟡 Импорт pathlib.Path может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/api/websocket_api.py**
  🟡 Импорт aiohttp_cors.setup может быть неиспользуемым
- **security/vpn/api/graphql_api.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт aiohttp_cors.setup может быть неиспользуемым
- **security/vpn/validators/__init__.py**
  🔴 Импорт vpn_validators.* может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/vpn/monitoring/vpn_metrics.py**
  🟡 Импорт json может быть неиспользуемым
- **security/vpn/performance/connection_cache.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт asyncio может быть неиспользуемым
- **security/vpn/performance/async_processor.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
  🟡 Импорт concurrent.futures.ProcessPoolExecutor может быть неиспользуемым
  🟡 Импорт typing.Awaitable может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
- **security/vpn/performance/performance_manager.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт threading может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт async_processor.AsyncTask может быть неиспользуемым
  🟡 Импорт connection_cache.ConnectionState может быть неиспользуемым
  🟡 Импорт connection_pool.PoolState может быть неиспользуемым
- **security/vpn/performance/connection_pool.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт asyncio может быть неиспользуемым
- **security/vpn/backup/backup_manager.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт zipfile может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/vpn/legal/legal_protection.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
- **security/vpn/client/vpn_client.py**
  🟡 Импорт logging может быть неиспользуемым
- **security/vpn/protocols/shadowsocks_client.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/vpn/protocols/v2ray_client.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/vpn/protocols/obfuscation_manager.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/vpn/protocols/openvpn_server.py**
  🟡 Импорт tempfile может быть неиспользуемым
  🟡 Импорт datetime.datetime может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/protocols/wireguard_server.py**
  🟡 Импорт datetime.datetime может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/servers/foreign_server_manager.py**
  🟡 Импорт logging может быть неиспользуемым
- **security/vpn/analytics/ml_detector.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/vpn/analytics/business_analytics.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/managers/analytics_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/managers/monitor_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/managers/alert_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/managers/report_manager.py**
  🟡 Импорт pandas может быть неиспользуемым
- **security/managers/dashboard_manager.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/family/test_simple.py**
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт family_registration.FamilyRegistration может быть неиспользуемым
  🟡 Импорт family_registration.RegistrationMethod может быть неиспользуемым
  🔴 Импорт family_notification_manager.FamilyNotificationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_notification_manager.NotificationType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_notification_manager.NotificationPriority может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_notification_manager.NotificationChannel может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/family/family_communication_hub_enhanced.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/family/family_profile_manager_enhanced.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/family/parent_child_elderly_web_interface.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/family/register_family_system_in_sfm.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🔴 Импорт security.family.family_registration.FamilyRegistration может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.family.family_notification_manager.FamilyNotificationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/integrations/russian_ai_models.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/mobile/mobile_api.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
- **security/ai/super_ai_support_assistant_improved.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/formatting_work/enhanced_user_interface_manager_extra.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/shadowsocks_client_fix/shadowsocks_client_final.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/shadowsocks_client_fix/shadowsocks_client_formatted.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/anonymous_modules_backup/compliance_monitor_152_fz_original.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт pathlib.Path может быть неиспользуемым
- **security/formatting_work/anonymous_modules_backup/anonymous_family_profiles_original.py**
  🟡 Импорт uuid может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/formatting_work/anonymous_modules_backup/comprehensive_anonymous_family_system_original.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт dataclasses.asdict может быть неиспользуемым
  🟡 Импорт pathlib.Path может быть неиспользуемым
- **security/formatting_work/anonymous_modules_backup/anonymous_data_manager_original.py**
  🟡 Импорт uuid может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
- **security/formatting_work/obfuscation_manager_fix/obfuscation_manager_final.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/obfuscation_manager_fix/obfuscation_manager_formatted.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/auto_sleep_manager_fix/auto_sleep_manager_final.py**
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт typing.Any может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/auto_sleep_manager_fix/auto_sleep_manager_formatted.py**
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт typing.Any может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/compliance_integration_fix/integration_final.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт no_logs_policy.LogType может быть неиспользуемым
- **security/formatting_work/compliance_integration_fix/integration_formatted.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт no_logs_policy.LogType может быть неиспользуемым
- **security/formatting_work/backup_files/security_quality_analyzer_enhanced.py**
  🟡 Импорт concurrent.futures может быть неиспользуемым
- **security/formatting_work/backup_files/content_analyzer_enhanced.py**
  🟡 Импорт datetime.datetime может быть неиспользуемым
  🟡 Импорт typing.Any может быть неиспользуемым
- **security/formatting_work/backup_files/notification_service_enhanced.py**
  🟡 Импорт datetime.datetime может быть неиспользуемым
- **security/formatting_work/backup_files/family_communication_hub_enhanced.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/backup_files/safe_quality_analyzer_enhanced.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/formatting_work/backup_files/user_interface_manager_extra_enhanced.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/backup_files/time_monitor_enhanced.py**
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/formatting_work/backup_files/parental_control_bot_v2_enhanced.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🔴 Импорт security.bots.parental_control_bot.ChildProfileData может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.bots.parental_control_bot.ContentAnalysisRequest может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт security.bots.parental_control_bot.TimeLimitData может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/formatting_work/backup_files/performance_optimizer_original_backup_20250103.py**
  🟡 Импорт typing.Union может быть неиспользуемым
  🟡 Импорт weakref может быть неиспользуемым
- **security/formatting_work/backup_files/malware_detection_agent_BACKUP.py**
  🟡 Импорт subprocess может быть неиспользуемым
  🟡 Импорт tempfile может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт typing.Union может быть неиспользуемым
- **security/formatting_work/backup_files/elderly_interface_manager_enhanced.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/formatting_work/v2ray_client_fix/v2ray_client_final.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/v2ray_client_fix/v2ray_client_formatted.py**
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
- **security/formatting_work/russia_compliance_fix/russia_compliance_formatted.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/formatting_work/russia_compliance_fix/russia_compliance_final.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт logging может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
- **security/formatting_work/duplicates/phishing_protection_agent_backup_20250921_104040.py**
  🟡 Импорт urllib.parse может быть неиспользуемым
- **security/formatting_work/duplicates/family_communication_hub_a_plus.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/duplicates/security_monitoring.py**
  🟡 Импорт os может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт pathlib.Path может быть неиспользуемым
- **security/formatting_work/duplicates/behavioral_analytics_engine_main.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/duplicates/circuit_breaker.py**
  🟡 Импорт numpy может быть неиспользуемым
  🟡 Импорт prometheus_client.Gauge может быть неиспользуемым
  🟡 Импорт core.base.CoreBase может быть неиспользуемым
  🔴 Импорт core.configuration.ConfigurationManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт core.database.DatabaseManager может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🟡 Импорт core.service_base.ServiceBase может быть неиспользуемым
  🟡 Импорт fastapi.Depends может быть неиспользуемым
- **security/formatting_work/duplicates/notification_bot_main.py**
  🟡 Импорт time может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/duplicates/behavioral_analytics_engine_extra.py**
  🟡 Импорт typing.List может быть неиспользуемым
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/duplicates/behavioral_analysis.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/formatting_work/duplicates/malware_protection_old_backup_20250928_125507.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт subprocess может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт requests может быть неиспользуемым
  🟡 Импорт pathlib.Path может быть неиспользуемым
- **security/formatting_work/duplicates/family_profile_manager.py**
  🔴 Импорт family_profile_manager_enhanced.FamilyGroup может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_profile_manager_enhanced.FamilyGroupStatus может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_profile_manager_enhanced.MessageType может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_profile_manager_enhanced.MessagePriority может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт family_profile_manager_enhanced.CommunicationChannel может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/preliminary/behavioral_analysis_new.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/ai_agents/emergency_models.py**
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт dataclasses.asdict может быть неиспользуемым
- **security/ai_agents/emergency_ml_models.py**
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/ai_agents/security_quality_analyzer.py**
  🟡 Импорт concurrent.futures может быть неиспользуемым
- **security/ai_agents/russian_fraud_ml_models.py**
  🟡 Импорт numpy может быть неиспользуемым
  🟡 Импорт pandas может быть неиспользуемым
- **security/ai_agents/security_quality_analyzer_enhanced.py**
  🟡 Импорт concurrent.futures может быть неиспользуемым
- **security/ai_agents/news_scraper.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/family_communication_hub_max_messenger_expansion.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/improved_ml_models.py**
  🟡 Импорт numpy может быть неиспользуемым
  🟡 Импорт pandas может быть неиспользуемым
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/cbr_data_collector.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/emergency_ml_analyzer.py**
  🟡 Импорт typing.Optional может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🔴 Импорт emergency_security_utils.EmergencySecurityUtils может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/ai_agents/speech_recognition_engine.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/auto_learning_system.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/natural_language_processor.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/notification_bot.py**
  🟡 Импорт numpy может быть неиспользуемым
- **security/ai_agents/emergency_risk_analyzer.py**
  🟡 Импорт numpy может быть неиспользуемым
  🟡 Импорт geopy.distance может быть неиспользуемым
- **security/ai_agents/educational_platforms_integration.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
  🔴 Импорт core.security_base.SecurityEvent может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
  🔴 Импорт core.security_base.IncidentSeverity может быть неиспользуемым (КРИТИЧЕСКИЙ МОДУЛЬ - требует проверки)
- **security/ai_agents/emergency_utils.py**
  🟡 Импорт hashlib может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/ai_agents/data_protection_agent.py**
  🟡 Импорт concurrent.futures может быть неиспользуемым
- **security/ai_agents/parent_control_panel.py**
  🟡 Импорт sys может быть неиспользуемым
- **security/ai_agents/psychological_support_agent.py**
  🟡 Импорт asyncio может быть неиспользуемым
  🟡 Импорт json может быть неиспользуемым
  🟡 Импорт datetime.timedelta может быть неиспользуемым
  🟡 Импорт typing.Tuple может быть неиспользуемым
- **security/ai_agents/mobile_user_ai_agent.py**
  🟡 Импорт os может быть неиспользуемым
- **security/ai_agents/behavioral_analytics_engine.py**
  🟡 Импорт sys может быть неиспользуемым
  🟡 Импорт numpy может быть неиспользуемым
- **security/ai_agents/compliance_agent.py**
  🟡 Импорт sys может быть неиспользуемым

## 📁 ПАПКА: AI_AGENTS/
- **Файлов:** 1
- **Успешно проанализировано:** 1
- **Ошибок:** 0
- **Потенциальных проблем:** 0

## 🎯 РЕКОМЕНДАЦИИ ПО ПРИМЕНЕНИЮ ПРАВИЛЬНОГО АЛГОРИТМА

### ✅ ПРАВИЛЬНЫЙ ПОДХОД:
1. **Анализировать код** - искать все места использования
2. **Проверять методы инициализации** - смотреть динамическое создание
3. **Тестировать функциональность** - запускать код после изменений
4. **Игнорировать ложные F401** - если импорт действительно нужен

### ❌ НЕПРАВИЛЬНО:
1. Слепо доверять flake8
2. Удалять импорты без анализа контекста
3. Не тестировать функциональность
