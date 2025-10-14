#!/usr/bin/env python3
"""
Регистрация всех основных функций в SafeFunctionManager
"""
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.safe_function_manager import SafeFunctionManager, FunctionStatus, SecurityLevel

def register_all_functions():
    """Регистрирует все основные функции в SFM"""
    print("🔧 РЕГИСТРАЦИЯ ВСЕХ ФУНКЦИЙ В SFM")
    print("=" * 60)
    print(f"Время регистрации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Создаем SFM
    sfm = SafeFunctionManager()
    print("✅ SafeFunctionManager создан")
    
    # Список всех основных функций для регистрации
    functions_to_register = [
        # Microservices
        {
            "id": "load_balancer",
            "name": "LoadBalancer",
            "description": "Балансировщик нагрузки для распределения запросов",
            "type": "Microservice",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "api_gateway",
            "name": "APIGateway", 
            "description": "API Gateway для маршрутизации и аутентификации",
            "type": "Microservice",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "rate_limiter",
            "name": "RateLimiter",
            "description": "Ограничитель скорости запросов",
            "type": "Microservice",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        {
            "id": "circuit_breaker",
            "name": "CircuitBreaker",
            "description": "Предохранитель для защиты от каскадных сбоев",
            "type": "Microservice",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        
        # AI Agents
        {
            "id": "analytics_manager",
            "name": "AnalyticsManager",
            "description": "AI агент для аналитики и отчетности",
            "type": "AI Agent",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "dashboard_manager",
            "name": "DashboardManager",
            "description": "AI агент для управления дашбордами",
            "type": "AI Agent",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "monitor_manager",
            "name": "MonitorManager",
            "description": "AI агент для мониторинга системы",
            "type": "AI Agent",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "report_manager",
            "name": "ReportManager",
            "description": "AI агент для генерации отчетов",
            "type": "AI Agent",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        {
            "id": "behavioral_analysis_agent",
            "name": "BehavioralAnalysisAgent",
            "description": "AI агент для анализа поведения пользователей",
            "type": "AI Agent",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        
        # Privacy & Security
        {
            "id": "privacy_manager",
            "name": "UniversalPrivacyManager",
            "description": "Менеджер конфиденциальности и GDPR",
            "type": "Privacy Manager",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "trust_scoring",
            "name": "TrustScoring",
            "description": "Система оценки доверия пользователей",
            "type": "Preliminary",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "behavioral_analysis",
            "name": "BehavioralAnalysis",
            "description": "Система анализа поведения",
            "type": "Preliminary",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        
        # Family Protection
        {
            "id": "child_protection",
            "name": "ChildProtection",
            "description": "Система защиты детей",
            "type": "Family Protection",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        
        # Security Bots
        {
            "id": "network_security_bot",
            "name": "NetworkSecurityBot",
            "description": "Бот для сетевой безопасности",
            "type": "Security Bot",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        {
            "id": "device_security_bot",
            "name": "DeviceSecurityBot",
            "description": "Бот для безопасности устройств",
            "type": "Security Bot",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        {
            "id": "analytics_bot",
            "name": "AnalyticsBot",
            "description": "Бот для аналитики",
            "type": "Security Bot",
            "security_level": SecurityLevel.MEDIUM,
            "is_critical": False,
            "auto_enable": True
        },
        
        # Antivirus
        {
            "id": "antivirus_core",
            "name": "AntivirusCore",
            "description": "Ядро антивирусной системы",
            "type": "Antivirus",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        
        # VPN
        {
            "id": "vpn_core",
            "name": "VpnCore",
            "description": "Ядро VPN системы",
            "type": "VPN",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        
        # Compliance
        {
            "id": "coppa_compliance",
            "name": "CoppaComplianceManager",
            "description": "Менеджер соответствия COPPA",
            "type": "Compliance",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        },
        {
            "id": "russian_child_protection",
            "name": "RussianChildProtectionManager",
            "description": "Менеджер защиты детей (Россия)",
            "type": "Compliance",
            "security_level": SecurityLevel.HIGH,
            "is_critical": True,
            "auto_enable": True
        }
    ]
    
    print(f"\n📊 Всего функций для регистрации: {len(functions_to_register)}")
    print("\n" + "="*60)
    
    registered_count = 0
    failed_count = 0
    
    for i, func in enumerate(functions_to_register, 1):
        print(f"\n🔧 {i}. Регистрация {func['name']} ({func['type']})")
        
        try:
            success = sfm.register_function(
                function_id=func["id"],
                name=func["name"],
                description=func["description"],
                function_type=func["type"],
                security_level=func["security_level"],
                is_critical=func["is_critical"],
                auto_enable=func["auto_enable"]
            )
            
            if success:
                print(f"   ✅ Успешно зарегистрирован")
                registered_count += 1
                
                # Проверяем статус
                status = sfm.get_function_status(func["id"])
                print(f"   📍 Статус: {status.value}")
                
                # Проверяем включен ли
                if func["auto_enable"]:
                    enabled_status = sfm.get_function_status(func["id"])
                    if enabled_status == FunctionStatus.ENABLED:
                        print(f"   ✅ Автоматически включен")
                    else:
                        print(f"   ⚠️  Не включен (статус: {enabled_status.value})")
            else:
                print(f"   ❌ Ошибка регистрации")
                failed_count += 1
                
        except Exception as e:
            print(f"   ❌ Исключение при регистрации: {e}")
            failed_count += 1
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА РЕГИСТРАЦИИ:")
    print(f"• Всего функций: {len(functions_to_register)}")
    print(f"• Успешно зарегистрировано: {registered_count}")
    print(f"• Ошибок регистрации: {failed_count}")
    print(f"• Процент успеха: {registered_count/len(functions_to_register)*100:.1f}%")
    
    # Показываем все зарегистрированные функции
    print(f"\n🔍 ВСЕ ЗАРЕГИСТРИРОВАННЫЕ ФУНКЦИИ В SFM:")
    print("-" * 60)
    
    if hasattr(sfm, 'functions') and sfm.functions:
        for func_id, func_info in sfm.functions.items():
            status = sfm.get_function_status(func_id)
            print(f"• {func_id}: {func_info.get('name', 'N/A')} ({status.value})")
    else:
        print("❌ Нет зарегистрированных функций")
    
    return registered_count, failed_count

if __name__ == "__main__":
    register_all_functions()