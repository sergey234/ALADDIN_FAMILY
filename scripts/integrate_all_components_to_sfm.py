#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция всех компонентов в SafeFunctionManager
Полная интеграция всех Manager, Agent и Bot классов

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-10
"""

import sys
import os
sys.path.insert(0, '/Users/sergejhlystov/ALADDIN_NEW')

from security.safe_function_manager import SafeFunctionManager
from security.universal_singleton import get_component, get_all_singleton_stats
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def integrate_all_components():
    """
    Интегрируем все компоненты в SFM
    """
    print("🚀 ИНТЕГРАЦИЯ ВСЕХ КОМПОНЕНТОВ В SFM")
    print("================================================")
    
    try:
        # Получаем SFM (Singleton)
        sfm = get_component(SafeFunctionManager)
        print("✅ SFM получен (Singleton)")
        
        # Список всех компонентов для интеграции
        components_to_integrate = [
            # MANAGER КЛАССЫ
            {
                "name": "AnalyticsManager",
                "module": "security.managers.analytics_manager",
                "class": "AnalyticsManager",
                "description": "Менеджер аналитики безопасности",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "DashboardManager", 
                "module": "security.ai_agents.dashboard_manager",
                "class": "DashboardManager",
                "description": "Менеджер панели управления",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "MonitorManager",
                "module": "security.managers.monitor_manager", 
                "class": "MonitorManager",
                "description": "Менеджер мониторинга",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "ReportManager",
                "module": "security.ai_agents.report_manager",
                "class": "ReportManager", 
                "description": "Менеджер отчетов",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "APIGateway",
                "module": "security.microservices.api_gateway",
                "class": "APIGateway",
                "description": "API шлюз",
                "function_type": "microservice",
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "LoadBalancer",
                "module": "security.microservices.load_balancer",
                "class": "LoadBalancer",
                "description": "Балансировщик нагрузки",
                "function_type": "microservice", 
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "UniversalPrivacyManager",
                "module": "security.privacy.universal_privacy_manager",
                "class": "UniversalPrivacyManager",
                "description": "Менеджер приватности",
                "function_type": "privacy",
                "security_level": "critical",
                "is_critical": True
            },
            # AGENT КЛАССЫ
            {
                "name": "BehavioralAnalysisAgent",
                "module": "security.ai_agents.behavioral_analysis_agent",
                "class": "BehavioralAnalysisAgent",
                "description": "Агент анализа поведения",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "ThreatDetectionAgent",
                "module": "security.ai_agents.threat_detection_agent",
                "class": "ThreatDetectionAgent",
                "description": "Агент обнаружения угроз",
                "function_type": "ai_agent",
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "PasswordSecurityAgent",
                "module": "security.ai_agents.password_security_agent",
                "class": "PasswordSecurityAgent",
                "description": "Агент безопасности паролей",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "IncidentResponseAgent",
                "module": "security.ai_agents.incident_response_agent",
                "class": "IncidentResponseAgent",
                "description": "Агент реагирования на инциденты",
                "function_type": "ai_agent",
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "ThreatIntelligenceAgent",
                "module": "security.ai_agents.threat_intelligence_agent",
                "class": "ThreatIntelligenceAgent",
                "description": "Агент разведки угроз",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "NetworkSecurityAgent",
                "module": "security.ai_agents.network_security_agent",
                "class": "NetworkSecurityAgent",
                "description": "Агент сетевой безопасности",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "DataProtectionAgent",
                "module": "security.ai_agents.data_protection_agent",
                "class": "DataProtectionAgent",
                "description": "Агент защиты данных",
                "function_type": "ai_agent",
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "ComplianceAgent",
                "module": "security.ai_agents.compliance_agent",
                "class": "ComplianceAgent",
                "description": "Агент соответствия требованиям",
                "function_type": "ai_agent",
                "security_level": "high",
                "is_critical": True
            },
            # BOT КЛАССЫ
            {
                "name": "MobileNavigationBot",
                "module": "security.bots.mobile_navigation_bot",
                "class": "MobileNavigationBot",
                "description": "Бот навигации по мобильным устройствам",
                "function_type": "bot",
                "security_level": "medium",
                "is_critical": False
            },
            {
                "name": "GamingSecurityBot",
                "module": "security.bots.gaming_security_bot",
                "class": "GamingSecurityBot",
                "description": "Бот безопасности игр",
                "function_type": "bot",
                "security_level": "medium",
                "is_critical": False
            },
            {
                "name": "EmergencyResponseBot",
                "module": "security.bots.emergency_response_bot",
                "class": "EmergencyResponseBot",
                "description": "Бот экстренного реагирования",
                "function_type": "bot",
                "security_level": "critical",
                "is_critical": True
            },
            {
                "name": "ParentalControlBot",
                "module": "security.bots.parental_control_bot",
                "class": "ParentalControlBot",
                "description": "Бот родительского контроля",
                "function_type": "bot",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "NotificationBot",
                "module": "security.bots.notification_bot",
                "class": "NotificationBot",
                "description": "Бот уведомлений",
                "function_type": "bot",
                "security_level": "medium",
                "is_critical": False
            },
            {
                "name": "WhatsAppSecurityBot",
                "module": "security.bots.whatsapp_security_bot",
                "class": "WhatsAppSecurityBot",
                "description": "Бот безопасности WhatsApp",
                "function_type": "bot",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "TelegramSecurityBot",
                "module": "security.bots.telegram_security_bot",
                "class": "TelegramSecurityBot",
                "description": "Бот безопасности Telegram",
                "function_type": "bot",
                "security_level": "high",
                "is_critical": True
            },
            {
                "name": "InstagramSecurityBot",
                "module": "security.bots.instagram_security_bot",
                "class": "InstagramSecurityBot",
                "description": "Бот безопасности Instagram",
                "function_type": "bot",
                "security_level": "high",
                "is_critical": True
            }
        ]
        
        # Интегрируем каждый компонент
        integrated_count = 0
        failed_count = 0
        
        for component in components_to_integrate:
            try:
                print(f"\n🔄 Интегрируем {component['name']}...")
                
                # Регистрируем функцию в SFM
                success = sfm.register_function(
                    function_id=component['name'].lower(),
                    name=component['name'],
                    description=component['description'],
                    function_type=component['function_type'],
                    security_level=component['security_level'],
                    is_critical=component['is_critical'],
                    auto_enable=False,  # По умолчанию в спящем режиме
                    auto_sleep=True,
                    sleep_after_hours=24
                )
                
                if success:
                    print(f"✅ {component['name']} интегрирован успешно")
                    integrated_count += 1
                else:
                    print(f"❌ Ошибка интеграции {component['name']}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ Ошибка при интеграции {component['name']}: {e}")
                failed_count += 1
        
        # Показываем результаты
        print(f"\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИИ:")
        print(f"✅ Успешно интегрировано: {integrated_count}")
        print(f"❌ Ошибок интеграции: {failed_count}")
        print(f"📈 Общий прогресс: {integrated_count}/{len(components_to_integrate)} ({integrated_count/len(components_to_integrate)*100:.1f}%)")
        
        # Проверяем текущее состояние SFM
        all_functions = sfm.get_all_functions_status()
        print(f"\n📋 ТЕКУЩЕЕ СОСТОЯНИЕ SFM:")
        print(f"Всего функций: {len(all_functions)}")
        
        # Статистика Singleton
        singleton_stats = get_all_singleton_stats()
        print(f"\n🔧 СТАТИСТИКА SINGLETON:")
        print(f"Активных Singleton: {len(singleton_stats)}")
        
        return integrated_count, failed_count
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1

if __name__ == "__main__":
    integrated, failed = integrate_all_components()
    
    if integrated > 0:
        print(f"\n🎉 ИНТЕГРАЦИЯ ЗАВЕРШЕНА!")
        print(f"Успешно интегрировано {integrated} компонентов")
    else:
        print(f"\n💥 ИНТЕГРАЦИЯ НЕ УДАЛАСЬ!")
        print(f"Ошибок: {failed}")