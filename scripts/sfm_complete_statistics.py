#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полная статистика всех функций в SafeFunctionManager
"""

import os
import sys
import subprocess
from datetime import datetime

def get_sfm_statistics():
    """Получение полной статистики SFM"""
    print("📊 ПОЛНАЯ СТАТИСТИКА SAFEFUNCTIONMANAGER")
    print("=" * 100)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Все функции системы (из предыдущего анализа)
    all_functions = [
        # Core функции
        {"id": "core_base", "name": "CoreBase", "file": "core/base.py", "type": "Core", "status": "Active"},
        {"id": "core_service_base", "name": "ServiceBase", "file": "core/service_base.py", "type": "Core", "status": "Active"},
        {"id": "core_database", "name": "Database", "file": "core/database.py", "type": "Core", "status": "Active"},
        {"id": "core_configuration", "name": "Configuration", "file": "core/configuration.py", "type": "Core", "status": "Active"},
        {"id": "core_logging", "name": "LoggingModule", "file": "core/logging_module.py", "type": "Core", "status": "Active"},
        {"id": "core_security_base", "name": "SecurityBase", "file": "core/security_base.py", "type": "Core", "status": "Active"},
        
        # Security основные функции
        {"id": "function_1", "name": "SafeFunctionManager", "file": "security/safe_function_manager.py", "type": "Security", "status": "Active"},
        {"id": "function_2", "name": "SecurityMonitoring", "file": "security/security_monitoring.py", "type": "Security", "status": "Active"},
        {"id": "function_3", "name": "Authentication", "file": "security/authentication.py", "type": "Security", "status": "Active"},
        {"id": "function_4", "name": "AccessControl", "file": "security/access_control.py", "type": "Security", "status": "Active"},
        {"id": "function_5", "name": "SecurityPolicy", "file": "security/security_policy.py", "type": "Security", "status": "Active"},
        {"id": "function_6", "name": "SecurityReporting", "file": "security/security_reporting.py", "type": "Security", "status": "Active"},
        
        # Family функции
        {"id": "function_7", "name": "FamilyProfileManager", "file": "security/family/family_profile_manager.py", "type": "Family", "status": "Active"},
        {"id": "function_8", "name": "ChildProtection", "file": "security/family/child_protection.py", "type": "Family", "status": "Active"},
        {"id": "function_9", "name": "ElderlyProtection", "file": "security/family/elderly_protection.py", "type": "Family", "status": "Active"},
        
        # Preliminary функции
        {"id": "function_10", "name": "PolicyEngine", "file": "security/preliminary/policy_engine.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_11", "name": "RiskAssessment", "file": "security/preliminary/risk_assessment.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_12", "name": "BehavioralAnalysis", "file": "security/preliminary/behavioral_analysis.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_13", "name": "MFAService", "file": "security/preliminary/mfa_service.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_14", "name": "ZeroTrustService", "file": "security/preliminary/zero_trust_service.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_15", "name": "TrustScoring", "file": "security/preliminary/trust_scoring.py", "type": "Preliminary", "status": "Active"},
        {"id": "function_16", "name": "ContextAwareAccess", "file": "security/preliminary/context_aware_access.py", "type": "Preliminary", "status": "Active"},
        
        # Reactive функции
        {"id": "function_17", "name": "RecoveryService", "file": "security/reactive/recovery_service.py", "type": "Reactive", "status": "Active"},
        {"id": "function_18", "name": "ThreatIntelligence", "file": "security/reactive/threat_intelligence.py", "type": "Reactive", "status": "Active"},
        {"id": "function_19", "name": "ForensicsService", "file": "security/reactive/forensics_service.py", "type": "Reactive", "status": "Active"},
        
        # Microservices
        {"id": "function_20", "name": "APIGateway", "file": "security/microservices/api_gateway.py", "type": "Microservices", "status": "Active"},
        {"id": "function_21", "name": "LoadBalancer", "file": "security/microservices/load_balancer.py", "type": "Microservices", "status": "Active"},
        {"id": "function_22", "name": "RateLimiter", "file": "security/microservices/rate_limiter.py", "type": "Microservices", "status": "Active"},
        {"id": "function_23", "name": "CircuitBreaker", "file": "security/microservices/circuit_breaker.py", "type": "Microservices", "status": "Active"},
        {"id": "function_24", "name": "UserInterfaceManager", "file": "security/microservices/user_interface_manager.py", "type": "Microservices", "status": "Active"},
        {"id": "function_25", "name": "RedisCacheManager", "file": "security/microservices/redis_cache_manager.py", "type": "Microservices", "status": "Active"},
        {"id": "function_26", "name": "ServiceMeshManager", "file": "security/microservices/service_mesh_manager.py", "type": "Microservices", "status": "Active"},
        
        # AI Agents
        {"id": "function_27", "name": "MonitorManager", "file": "security/managers/monitor_manager.py", "type": "Managers", "status": "Active"},
        {"id": "function_28", "name": "AlertManager", "file": "security/managers/alert_manager.py", "type": "Managers", "status": "Active"},
        {"id": "function_29", "name": "ReportManager", "file": "security/ai_agents/report_manager.py", "type": "AI Agents", "status": "Active"},
        {"id": "function_30", "name": "AnalyticsManager", "file": "security/managers/analytics_manager.py", "type": "Managers", "status": "Active"},
        {"id": "function_31", "name": "DashboardManager", "file": "security/ai_agents/dashboard_manager.py", "type": "AI Agents", "status": "Active"},
        {"id": "function_32", "name": "DataProtectionAgent", "file": "security/ai_agents/data_protection_agent.py", "type": "AI Agents", "status": "Active"},
        {"id": "function_33", "name": "MobileSecurityAgent", "file": "security/ai_agents/mobile_security_agent.py", "type": "AI Agents", "status": "Active"},
        
        # Bots
        {"id": "function_34", "name": "MobileNavigationBot", "file": "security/bots/mobile_navigation_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_35", "name": "GamingSecurityBot", "file": "security/bots/gaming_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_36", "name": "EmergencyResponseBot", "file": "security/bots/emergency_response_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_37", "name": "ParentalControlBot", "file": "security/bots/parental_control_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_38", "name": "NotificationBot", "file": "security/bots/notification_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_39", "name": "WhatsAppSecurityBot", "file": "security/bots/whatsapp_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_40", "name": "TelegramSecurityBot", "file": "security/bots/telegram_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_41", "name": "InstagramSecurityBot", "file": "security/bots/instagram_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_42", "name": "AnalyticsBot", "file": "security/bots/analytics_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_43", "name": "WebsiteNavigationBot", "file": "security/bots/website_navigation_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_44", "name": "BrowserSecurityBot", "file": "security/bots/browser_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_45", "name": "CloudStorageSecurityBot", "file": "security/bots/cloud_storage_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_46", "name": "NetworkSecurityBot", "file": "security/bots/network_security_bot.py", "type": "Bots", "status": "Active"},
        {"id": "function_47", "name": "DeviceSecurityBot", "file": "security/bots/device_security_bot.py", "type": "Bots", "status": "Active"},
        
        # Privacy
        {"id": "function_48", "name": "UniversalPrivacyManager", "file": "security/privacy/universal_privacy_manager.py", "type": "Privacy", "status": "Active"},
        
        # Compliance
        {"id": "function_49", "name": "RussianChildProtectionManager", "file": "security/compliance/russian_child_protection_manager.py", "type": "Compliance", "status": "Active"},
        {"id": "function_152_fz_compliance", "name": "RussianDataProtectionManager", "file": "security/compliance/russian_data_protection_manager.py", "type": "Compliance", "status": "Active"},
        
        # CI/CD
        {"id": "function_50", "name": "CIPipelineManager", "file": "security/ci_cd/ci_pipeline_manager.py", "type": "CI/CD", "status": "Active"},
        
        # Scaling
        {"id": "function_51", "name": "AutoScalingEngine", "file": "security/scaling/auto_scaling_engine.py", "type": "Scaling", "status": "Active"},
        
        # Orchestration
        {"id": "function_52", "name": "KubernetesOrchestrator", "file": "security/orchestration/kubernetes_orchestrator.py", "type": "Orchestration", "status": "Active"}
    ]
    
    # Анализ качества каждой функции
    print("🔍 АНАЛИЗ КАЧЕСТВА ФУНКЦИЙ:")
    print("-" * 100)
    
    total_functions = len(all_functions)
    functions_with_issues = 0
    total_issues = 0
    
    # Статистика по типам
    type_stats = {}
    
    for func in all_functions:
        file_path = f"/Users/sergejhlystov/ALADDIN_NEW/{func['file']}"
        
        if os.path.exists(file_path):
            try:
                result = subprocess.run([
                    'python3', '-m', 'flake8', 
                    '--max-line-length=120',
                    file_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    issues = 0
                    grade = "A+"
                    desc = "Отлично"
                else:
                    output = result.stdout
                    lines = output.split('\n')
                    issues = len([l for l in lines if l.strip()])
                    total_issues += issues
                    
                    if issues <= 5:
                        grade = "A"
                        desc = "Хорошо"
                    elif issues <= 15:
                        grade = "B"
                        desc = "Удовлетворительно"
                    elif issues <= 30:
                        grade = "C"
                        desc = "Требует улучшения"
                    else:
                        grade = "D"
                        desc = "Критично"
                
                if issues > 0:
                    functions_with_issues += 1
                
                # Обновляем статистику по типам
                if func['type'] not in type_stats:
                    type_stats[func['type']] = {
                        'total': 0,
                        'excellent': 0,
                        'good': 0,
                'fair': 0,
                        'poor': 0,
                        'critical': 0,
                        'issues': 0
                    }
                
                type_stats[func['type']]['total'] += 1
                type_stats[func['type']]['issues'] += issues
                
                if grade == "A+":
                    type_stats[func['type']]['excellent'] += 1
                elif grade == "A":
                    type_stats[func['type']]['good'] += 1
                elif grade == "B":
                    type_stats[func['type']]['fair'] += 1
                elif grade == "C":
                    type_stats[func['type']]['poor'] += 1
                elif grade == "D":
                    type_stats[func['type']]['critical'] += 1
                
                func['issues'] = issues
                func['grade'] = grade
                func['description'] = desc
                
            except Exception as e:
                func['issues'] = 999
                func['grade'] = "ERROR"
                func['description'] = f"Ошибка: {str(e)}"
                functions_with_issues += 1
        else:
            func['issues'] = 999
            func['grade'] = "MISSING"
            func['description'] = "Файл не найден"
            functions_with_issues += 1
    
    # Выводим таблицу функций
    print(f"{'№':<3} {'ID':<25} {'Название':<30} {'Тип':<12} {'Файл':<40} {'Проблем':<8} {'Оценка':<3} {'Статус'}")
    print("-" * 100)
    
    for i, func in enumerate(all_functions, 1):
        print(f"{i:<3} {func['id']:<25} {func['name']:<30} {func['type']:<12} {func['file']:<40} {func.get('issues', 0):<8} {func.get('grade', 'N/A'):<3} {func['status']}")
    
    # Общая статистика
    print("\n" + "=" * 100)
    print("📊 ОБЩАЯ СТАТИСТИКА SAFEFUNCTIONMANAGER:")
    print("=" * 100)
    print(f"🔢 Всего функций зарегистрировано: {total_functions}")
    print(f"🔍 Функций с проблемами: {functions_with_issues}")
    print(f"✅ Функций без проблем: {total_functions - functions_with_issues}")
    print(f"📈 Общее количество проблем: {total_issues}")
    print(f"📊 Среднее количество проблем на функцию: {total_issues / total_functions:.1f}")
    
    # Статистика по типам
    print("\n📋 СТАТИСТИКА ПО ТИПАМ ФУНКЦИЙ:")
    print("-" * 100)
    print(f"{'Тип':<15} {'Всего':<6} {'A+':<4} {'A':<4} {'B':<4} {'C':<4} {'D':<4} {'Проблем':<8} {'% Проблем'}")
    print("-" * 100)
    
    for type_name, stats in type_stats.items():
        problem_percentage = (stats['issues'] / (stats['total'] * 100)) * 100 if stats['total'] > 0 else 0
        print(f"{type_name:<15} {stats['total']:<6} {stats['excellent']:<4} {stats['good']:<4} {stats['fair']:<4} {stats['poor']:<4} {stats['critical']:<4} {stats['issues']:<8} {problem_percentage:.1f}%")
    
    # Топ проблемных функций
    print("\n🚨 ТОП 10 ПРОБЛЕМНЫХ ФУНКЦИЙ:")
    print("-" * 100)
    print(f"{'№':<3} {'Название':<30} {'Тип':<12} {'Проблем':<8} {'Оценка':<3} {'Файл'}")
    print("-" * 100)
    
    sorted_functions = sorted([f for f in all_functions if f.get('issues', 0) > 0], key=lambda x: x.get('issues', 0), reverse=True)
    
    for i, func in enumerate(sorted_functions[:10], 1):
        print(f"{i:<3} {func['name']:<30} {func['type']:<12} {func.get('issues', 0):<8} {func.get('grade', 'N/A'):<3} {func['file']}")
    
    # Функции без проблем
    print("\n✅ ФУНКЦИИ БЕЗ ПРОБЛЕМ (A+):")
    print("-" * 100)
    print(f"{'№':<3} {'Название':<30} {'Тип':<12} {'Файл'}")
    print("-" * 100)
    
    excellent_functions = [f for f in all_functions if f.get('grade') == 'A+']
    
    for i, func in enumerate(excellent_functions, 1):
        print(f"{i:<3} {func['name']:<30} {func['type']:<12} {func['file']}")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("-" * 100)
    
    if functions_with_issues > 0:
        print(f"🚨 КРИТИЧНО: {len([f for f in all_functions if f.get('grade') == 'D'])} функций требуют немедленного исправления")
        print(f"⚠️  ВАЖНО: {len([f for f in all_functions if f.get('grade') == 'C'])} функций требуют улучшения")
        print(f"📝 РЕКОМЕНДУЕТСЯ: {len([f for f in all_functions if f.get('grade') == 'B'])} функций можно оптимизировать")
        print(f"✅ ОТЛИЧНО: {len([f for f in all_functions if f.get('grade') == 'A+'])} функций работают идеально")
    else:
        print("🏆 ОТЛИЧНО! Все функции работают без проблем!")
    
    print(f"\n🎯 ЦЕЛЬ: Довести все функции до уровня A+ (0 проблем)")
    print(f"📈 ПРОГРЕСС: {((total_functions - functions_with_issues) / total_functions * 100):.1f}% функций без проблем")
    
    print("\n" + "=" * 100)
    print("✅ СТАТИСТИКА SAFEFUNCTIONMANAGER ЗАВЕРШЕНА!")
    print("=" * 100)

if __name__ == "__main__":
    get_sfm_statistics()