#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальный отчет по качеству каждой функции в SafeFunctionManager
"""

import os
import sys
import subprocess
from datetime import datetime

def analyze_function_quality():
    """Анализ качества каждой функции"""
    print("📊 ДЕТАЛЬНЫЙ ОТЧЕТ ПО КАЧЕСТВУ ФУНКЦИЙ В SAFEFUNCTIONMANAGER")
    print("=" * 80)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Все файлы системы
    all_files = [
        # Core файлы
        "core/base.py",
        "core/service_base.py", 
        "core/database.py",
        "core/configuration.py",
        "core/logging_module.py",
        "core/security_base.py",
        
        # Security основные файлы
        "security/safe_function_manager.py",
        "security/security_monitoring.py",
        "security/authentication.py",
        "security/access_control.py",
        "security/security_policy.py",
        "security/security_reporting.py",
        
        # Family функции
        "security/family/family_profile_manager.py",
        "security/family/child_protection.py",
        "security/family/elderly_protection.py",
        
        # Preliminary функции
        "security/preliminary/policy_engine.py",
        "security/preliminary/risk_assessment.py",
        "security/preliminary/behavioral_analysis.py",
        "security/preliminary/mfa_service.py",
        "security/preliminary/zero_trust_service.py",
        "security/preliminary/trust_scoring.py",
        "security/preliminary/context_aware_access.py",
        
        # Reactive функции
        "security/reactive/recovery_service.py",
        "security/reactive/threat_intelligence.py",
        "security/reactive/forensics_service.py",
        
        # Microservices
        "security/microservices/api_gateway.py",
        "security/microservices/load_balancer.py",
        "security/microservices/rate_limiter.py",
        "security/microservices/circuit_breaker.py",
        "security/microservices/user_interface_manager.py",
        "security/microservices/redis_cache_manager.py",
        "security/microservices/service_mesh_manager.py",
        
        # AI Agents
        "security/ai_agents/monitor_manager.py",
        "security/ai_agents/alert_manager.py",
        "security/ai_agents/report_manager.py",
        "security/ai_agents/analytics_manager.py",
        "security/ai_agents/dashboard_manager.py",
        "security/ai_agents/data_protection_agent.py",
        "security/ai_agents/mobile_security_agent.py",
        
        # Bots
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
        
        # Privacy
        "security/privacy/universal_privacy_manager.py",
        
        # Compliance
        "security/compliance/russian_child_protection_manager.py",
        "security/compliance/russian_data_protection_manager.py",
        
        # CI/CD
        "security/ci_cd/ci_pipeline_manager.py",
        
        # Scaling
        "security/scaling/auto_scaling_engine.py",
        
        # Orchestration
        "security/orchestration/kubernetes_orchestrator.py"
    ]
    
    # Категории качества
    excellent_files = []  # A+ (0 проблем)
    good_files = []       # A (1-5 проблем)
    fair_files = []       # B (6-15 проблем)
    poor_files = []       # C (16-30 проблем)
    critical_files = []   # D (30+ проблем)
    
    total_files = 0
    total_issues = 0
    
    print("🔍 АНАЛИЗ КАЧЕСТВА ПО ФАЙЛАМ:")
    print("-" * 80)
    
    for file_path in all_files:
        full_path = os.path.join("/Users/sergejhlystov/ALADDIN_NEW", file_path)
        if os.path.exists(full_path):
            total_files += 1
            print(f"\n📄 {file_path}:")
            
            try:
                result = subprocess.run([
                    'python3', '-m', 'flake8', 
                    '--max-line-length=120',
                    full_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("   ✅ Качество: A+ (0 проблем)")
                    excellent_files.append(file_path)
                else:
                    output = result.stdout
                    lines = output.split('\n')
                    file_issues = len([l for l in lines if l.strip()])
                    total_issues += file_issues
                    
                    # Определяем категорию качества
                    if file_issues == 0:
                        grade = "A+"
                        category = "Отлично"
                        excellent_files.append(file_path)
                    elif file_issues <= 5:
                        grade = "A"
                        category = "Хорошо"
                        good_files.append(file_path)
                    elif file_issues <= 15:
                        grade = "B"
                        category = "Удовлетворительно"
                        fair_files.append(file_path)
                    elif file_issues <= 30:
                        grade = "C"
                        category = "Требует улучшения"
                        poor_files.append(file_path)
                    else:
                        grade = "D"
                        category = "Критично"
                        critical_files.append(file_path)
                    
                    print(f"   📊 Качество: {grade} ({file_issues} проблем) - {category}")
                    
                    # Показываем основные проблемы
                    if file_issues > 0:
                        # Группируем проблемы по типам
                        issue_types = {}
                        for line in lines:
                            if line.strip() and ':' in line:
                                parts = line.split(':')
                                if len(parts) >= 3:
                                    error_code = parts[3].strip().split()[0] if parts[3].strip() else ''
                                    if error_code:
                                        issue_types[error_code] = issue_types.get(error_code, 0) + 1
                        
                        # Показываем топ проблем
                        if issue_types:
                            top_issues = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]
                            for error_code, count in top_issues:
                                print(f"   ⚠️  {error_code}: {count} проблем")
                        
                        # Показываем первые 3 конкретные проблемы
                        for i, line in enumerate(lines[:3]):
                            if line.strip():
                                print(f"   🔍 {line}")
                        if len(lines) > 3:
                            print(f"   ... и еще {len(lines) - 3} проблем")
                            
            except Exception as e:
                print(f"   ❌ Ошибка анализа: {str(e)}")
        else:
            print(f"❌ Файл не найден: {file_path}")
    
    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА КАЧЕСТВА:")
    print("=" * 80)
    print(f"📁 Всего файлов проанализировано: {total_files}")
    print(f"🔍 Всего проблем найдено: {total_issues}")
    print()
    
    # Распределение по категориям
    print("🏆 РАСПРЕДЕЛЕНИЕ ПО КАТЕГОРИЯМ КАЧЕСТВА:")
    print("-" * 80)
    print(f"🥇 A+ (Отлично):     {len(excellent_files):2d} файлов")
    print(f"🥈 A  (Хорошо):      {len(good_files):2d} файлов")
    print(f"🥉 B  (Удовлетворительно): {len(fair_files):2d} файлов")
    print(f"⚠️  C  (Требует улучшения): {len(poor_files):2d} файлов")
    print(f"🚨 D  (Критично):    {len(critical_files):2d} файлов")
    print()
    
    # Детальные списки
    if excellent_files:
        print("🥇 ФАЙЛЫ С ОТЛИЧНЫМ КАЧЕСТВОМ (A+):")
        print("-" * 80)
        for file_path in excellent_files:
            print(f"   ✅ {file_path}")
        print()
    
    if good_files:
        print("🥈 ФАЙЛЫ С ХОРОШИМ КАЧЕСТВОМ (A):")
        print("-" * 80)
        for file_path in good_files:
            print(f"   ✅ {file_path}")
        print()
    
    if fair_files:
        print("🥉 ФАЙЛЫ С УДОВЛЕТВОРИТЕЛЬНЫМ КАЧЕСТВОМ (B):")
        print("-" * 80)
        for file_path in fair_files:
            print(f"   ⚠️  {file_path}")
        print()
    
    if poor_files:
        print("⚠️  ФАЙЛЫ ТРЕБУЮЩИЕ УЛУЧШЕНИЯ (C):")
        print("-" * 80)
        for file_path in poor_files:
            print(f"   🔧 {file_path}")
        print()
    
    if critical_files:
        print("🚨 КРИТИЧЕСКИЕ ФАЙЛЫ (D):")
        print("-" * 80)
        for file_path in critical_files:
            print(f"   🚨 {file_path}")
        print()
    
    # Рекомендации
    print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
    print("-" * 80)
    
    if critical_files:
        print("🚨 КРИТИЧНО: Немедленно исправить файлы с оценкой D")
        for file_path in critical_files:
            print(f"   - {file_path}")
        print()
    
    if poor_files:
        print("⚠️  ВАЖНО: Исправить файлы с оценкой C")
        for file_path in poor_files:
            print(f"   - {file_path}")
        print()
    
    if fair_files:
        print("📝 РЕКОМЕНДУЕТСЯ: Улучшить файлы с оценкой B")
        for file_path in fair_files:
            print(f"   - {file_path}")
        print()
    
    # Общая оценка системы
    if len(excellent_files) + len(good_files) >= total_files * 0.8:
        system_grade = "A+"
        system_desc = "Отличное качество системы"
    elif len(excellent_files) + len(good_files) >= total_files * 0.6:
        system_grade = "A"
        system_desc = "Хорошее качество системы"
    elif len(excellent_files) + len(good_files) >= total_files * 0.4:
        system_grade = "B"
        system_desc = "Удовлетворительное качество системы"
    elif len(critical_files) <= total_files * 0.2:
        system_grade = "C"
        system_desc = "Требует улучшения"
    else:
        system_grade = "D"
        system_desc = "Критическое качество"
    
    print(f"🎯 ОБЩАЯ ОЦЕНКА СИСТЕМЫ: {system_grade} - {system_desc}")
    print()
    
    # План действий
    print("📋 ПЛАН ДЕЙСТВИЙ:")
    print("-" * 80)
    print("1. 🚨 НЕМЕДЛЕННО: Исправить критические файлы (D)")
    print("2. ⚠️  КРАТКОСРОЧНО: Улучшить файлы (C)")
    print("3. 📝 СРЕДНЕСРОЧНО: Оптимизировать файлы (B)")
    print("4. 🏆 ДОЛГОСРОЧНО: Поддерживать качество A+")
    
    print()
    print("=" * 80)
    print("✅ АНАЛИЗ КАЧЕСТВА ФУНКЦИЙ ЗАВЕРШЕН!")
    print("=" * 80)

if __name__ == "__main__":
    analyze_function_quality()