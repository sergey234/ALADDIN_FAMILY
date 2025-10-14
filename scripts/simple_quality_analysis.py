#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой анализ качества кода для SafeFunctionManager
"""

import os
import sys
import subprocess
from datetime import datetime

def run_flake8_analysis():
    """Запуск flake8 анализа"""
    print("🔍 АНАЛИЗ КАЧЕСТВА КОДА С ПОМОЩЬЮ FLAKE8")
    print("=" * 80)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Основные файлы для анализа
    files_to_analyze = [
        "core/base.py",
        "core/service_base.py", 
        "core/database.py",
        "core/configuration.py",
        "core/logging_module.py",
        "core/security_base.py",
        "security/safe_function_manager.py",
        "security/security_monitoring.py",
        "security/authentication.py",
        "security/access_control.py",
        "security/security_policy.py",
        "security/security_reporting.py",
        "security/family/family_profile_manager.py",
        "security/family/child_protection.py",
        "security/family/elderly_protection.py",
        "security/preliminary/policy_engine.py",
        "security/preliminary/risk_assessment.py",
        "security/preliminary/behavioral_analysis.py",
        "security/preliminary/mfa_service.py",
        "security/preliminary/zero_trust_service.py",
        "security/preliminary/trust_scoring.py",
        "security/preliminary/context_aware_access.py",
        "security/reactive/recovery_service.py",
        "security/reactive/threat_intelligence.py",
        "security/reactive/forensics_service.py",
        "security/microservices/api_gateway.py",
        "security/microservices/load_balancer.py",
        "security/microservices/rate_limiter.py",
        "security/microservices/circuit_breaker.py",
        "security/microservices/user_interface_manager.py",
        "security/microservices/redis_cache_manager.py",
        "security/microservices/service_mesh_manager.py",
        "security/ai_agents/monitor_manager.py",
        "security/ai_agents/alert_manager.py",
        "security/managers/report_manager.py",
        "security/ai_agents/analytics_manager.py",
        "security/ai_agents/dashboard_manager.py",
        "security/ai_agents/data_protection_agent.py",
        "security/ai_agents/mobile_security_agent.py",
        "security/bots/mobile_navigation_bot.py",
        "security/bots/gaming_security_bot.py",
        "security/bots/emergency_response_bot.py",
        "security/bots/parental_control_bot.py",
        "security/bots/notification_bot.py",
        "security/bots/whatsapp_security_bot.py",
        "security/bots/telegram_security_bot.py",
        "security/bots/instagram_security_bot.py",
        "security/bots/analytics_bot.py",
        "security/bots/website_navigation_bot.py",
        "security/bots/browser_security_bot.py",
        "security/bots/cloud_storage_security_bot.py",
        "security/bots/network_security_bot.py",
        "security/bots/device_security_bot.py",
        "security/privacy/universal_privacy_manager.py",
        "security/compliance/russian_child_protection_manager.py",
        "security/compliance/russian_data_protection_manager.py",
        "security/ci_cd/ci_pipeline_manager.py",
        "security/scaling/auto_scaling_engine.py",
        "security/orchestration/kubernetes_orchestrator.py"
    ]
    
    total_files = len(files_to_analyze)
    analyzed_files = 0
    total_issues = 0
    issues_by_category = {
        'E': 0,  # Error
        'W': 0,  # Warning  
        'F': 0,  # Fatal
        'C': 0,  # Convention
        'N': 0   # Naming
    }
    
    print(f"📊 Анализируем {total_files} файлов с помощью flake8...")
    print()
    
    for file_path in files_to_analyze:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"🔍 Анализируем: {file_path}")
            
            try:
                # Запуск flake8
                result = subprocess.run(
                    ['python3', '-m', 'flake8', '--max-line-length=120', '--statistics', full_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Качество: Отлично (0 проблем)")
                else:
                    output = result.stdout
                    lines = output.split('\n')
                    file_issues = 0
                    
                    for line in lines:
                        if ':' in line and ':' in line.split(':')[1]:
                            parts = line.split(':')
                            if len(parts) >= 3:
                                error_code = parts[3].strip().split()[0] if parts[3].strip() else ''
                                if error_code.startswith(('E', 'W', 'F', 'C', 'N')):
                                    category = error_code[0]
                                    issues_by_category[category] += 1
                                    file_issues += 1
                                    total_issues += 1
                    
                    if file_issues > 0:
                        print(f"   ⚠️  Качество: {file_issues} проблем")
                        if file_issues > 20:
                            print(f"   🚨 Критично: Слишком много проблем!")
                        elif file_issues > 10:
                            print(f"   ⚠️  Требует внимания")
                        else:
                            print(f"   ✅ Приемлемо")
                    else:
                        print(f"   ✅ Качество: Отлично")
                
                analyzed_files += 1
                
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Таймаут анализа")
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")
    
    print()
    print("📊 ОБЩАЯ СТАТИСТИКА КАЧЕСТВА:")
    print("-" * 80)
    print(f"📁 Проанализировано файлов: {analyzed_files}/{total_files}")
    print(f"🔍 Всего проблем найдено: {total_issues}")
    print()
    
    if total_issues > 0:
        print("📋 РАСПРЕДЕЛЕНИЕ ПРОБЛЕМ ПО КАТЕГОРИЯМ:")
        print(f"   🔴 Fatal (F):     {issues_by_category['F']:3d} проблем")
        print(f"   ❌ Error (E):     {issues_by_category['E']:3d} проблем")
        print(f"   ⚠️  Warning (W):   {issues_by_category['W']:3d} проблем")
        print(f"   📝 Convention (C): {issues_by_category['C']:3d} проблем")
        print(f"   🏷️  Naming (N):    {issues_by_category['N']:3d} проблем")
        print()
        
        # Оценка качества
        if total_issues < 50:
            quality_grade = "A+"
            quality_desc = "Отличное качество"
        elif total_issues < 100:
            quality_grade = "A"
            quality_desc = "Хорошее качество"
        elif total_issues < 200:
            quality_grade = "B"
            quality_desc = "Удовлетворительное качество"
        elif total_issues < 500:
            quality_grade = "C"
            quality_desc = "Требует улучшения"
        else:
            quality_grade = "D"
            quality_desc = "Критическое качество"
        
        print(f"🎯 ОБЩАЯ ОЦЕНКА: {quality_grade} - {quality_desc}")
        
        # Рекомендации
        print()
        print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        print("-" * 80)
        
        if issues_by_category['F'] > 0:
            print("🚨 КРИТИЧНО: Исправить Fatal ошибки немедленно!")
        
        if issues_by_category['E'] > 0:
            print("❌ ВАЖНО: Исправить Error проблемы")
        
        if issues_by_category['W'] > 0:
            print("⚠️  РЕКОМЕНДУЕТСЯ: Исправить Warning проблемы")
        
        if issues_by_category['C'] > 0:
            print("📝 PEP8: Следовать стандартам кодирования Python")
        
        if issues_by_category['N'] > 0:
            print("🏷️  ИМЕНОВАНИЕ: Улучшить имена переменных и функций")
        
        print()
        print("🔧 КОНКРЕТНЫЕ ДЕЙСТВИЯ:")
        print("   1. Запустить: flake8 --max-line-length=120 [файл]")
        print("   2. Исправить все F и E ошибки")
        print("   3. Добавить docstrings для всех функций")
        print("   4. Следовать PEP8 стандартам")
        print("   5. Улучшить читаемость кода")
        
    else:
        print("🏆 ОТЛИЧНО! Никаких проблем не найдено!")
        print("   Код соответствует высоким стандартам качества")
    
    print()
    print("=" * 80)
    print("✅ АНАЛИЗ КАЧЕСТВА ЗАВЕРШЕН!")
    print("=" * 80)

def analyze_specific_files():
    """Анализ конкретных файлов"""
    print()
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КЛЮЧЕВЫХ ФАЙЛОВ:")
    print("-" * 80)
    
    key_files = [
        "security/safe_function_manager.py",
        "core/base.py",
        "security/authentication.py",
        "security/family/child_protection.py"
    ]
    
    for file_path in key_files:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            print(f"\n📄 {file_path}:")
            
            try:
                result = subprocess.run(
                    ['python3', '-m', 'flake8', '--max-line-length=120', full_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("   ✅ Качество: Отлично")
                else:
                    output = result.stdout
                    lines = output.split('\n')
                    for line in lines[:10]:  # Показываем первые 10 проблем
                        if line.strip():
                            print(f"   ⚠️  {line}")
                    if len(lines) > 10:
                        print(f"   ... и еще {len(lines) - 10} проблем")
                        
            except Exception as e:
                print(f"   ❌ Ошибка анализа: {str(e)}")

if __name__ == "__main__":
    run_flake8_analysis()
    analyze_specific_files()