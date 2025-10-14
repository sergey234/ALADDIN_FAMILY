#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый анализ flake8 с промежуточным сохранением результатов
"""

import os
import subprocess
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def run_flake8_quick(file_path):
    """Быстрый запуск flake8"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            file_path,
            '--statistics'
        ], capture_output=True, text=True, timeout=10)
        
        return result.returncode, result.stdout, result.stderr
    except:
        return -1, "", "Timeout or error"

def analyze_errors(output):
    """Анализ ошибок"""
    errors = defaultdict(int)
    total_errors = 0
    
    lines = output.strip().split('\n')
    for line in lines:
        if ':' in line and not line.startswith('['):
            parts = line.split(':')
            if len(parts) >= 4:
                error_code = parts[3].strip().split()[0]
                errors[error_code] += 1
                total_errors += 1
    
    return total_errors, dict(errors)

def get_key_files():
    """Получить ключевые файлы для анализа"""
    key_files = []
    
    # CORE файлы
    core_files = [
        'core/base.py', 'core/service_base.py', 'core/database.py',
        'core/configuration.py', 'core/logging_module.py'
    ]
    
    # SECURITY файлы (топ 20)
    security_files = [
        'security/safe_function_manager.py', 'security/enhanced_alerting.py',
        'security/authentication.py', 'security/security_monitoring.py',
        'security/incident_response.py', 'security/threat_detection.py',
        'security/malware_protection.py', 'security/intrusion_prevention.py',
        'security/access_control_manager.py', 'security/data_protection_manager.py',
        'security/zero_trust_manager.py', 'security/security_audit.py',
        'security/compliance_manager.py', 'security/threat_intelligence.py',
        'security/network_monitoring.py', 'security/ransomware_protection.py',
        'security/advanced_alerting.py', 'security/security_core.py',
        'security/minimal_security_integration.py', 'security/security_analytics.py'
    ]
    
    # AI AGENTS (топ 15)
    ai_agent_files = [
        'security/ai_agents/threat_detection_agent.py',
        'security/ai_agents/behavioral_analysis_agent.py',
        'security/ai_agents/password_security_agent.py',
        'security/ai_agents/incident_response_agent.py',
        'security/ai_agents/threat_intelligence_agent.py',
        'security/ai_agents/network_security_agent.py',
        'security/ai_agents/data_protection_agent.py',
        'security/ai_agents/compliance_agent.py',
        'security/ai_agents/voice_analysis_engine.py',
        'security/ai_agents/deepfake_protection_system.py',
        'security/ai_agents/financial_protection_hub.py',
        'security/ai_agents/emergency_response_system.py',
        'security/ai_agents/elderly_protection_interface.py',
        'security/ai_agents/phishing_protection.py',
        'security/ai_agents/malware_detection.py'
    ]
    
    # BOTS (топ 15)
    bot_files = [
        'security/bots/emergency_response_bot.py',
        'security/bots/parental_control_bot.py',
        'security/bots/notification_bot.py',
        'security/bots/whatsapp_security_bot.py',
        'security/bots/telegram_security_bot.py',
        'security/bots/instagram_security_bot.py',
        'security/bots/mobile_navigation_bot.py',
        'security/bots/gaming_security_bot.py',
        'security/bots/analytics_bot.py',
        'security/bots/website_navigation_bot.py',
        'security/bots/browser_security_bot.py',
        'security/bots/cloud_storage_security_bot.py',
        'security/bots/device_security_bot.py',
        'security/bots/incognito_protection_bot.py'
    ]
    
    # MICROSERVICES (топ 10)
    microservice_files = [
        'security/microservices/api_gateway.py',
        'security/microservices/load_balancer.py',
        'security/microservices/rate_limiter.py',
        'security/microservices/circuit_breaker.py',
        'security/microservices/redis_cache_manager.py',
        'security/microservices/service_mesh_manager.py',
        'security/microservices/user_interface_manager.py',
        'security/microservices/emergency_service_caller.py',
        'security/microservices/wake_up_systems.py'
    ]
    
    all_files = core_files + security_files + ai_agent_files + bot_files + microservice_files
    
    # Проверяем существование файлов
    existing_files = []
    for file_path in all_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
    
    return existing_files

def categorize_file(file_path):
    """Определить категорию файла"""
    if 'core/' in file_path:
        return 'core'
    elif 'security/safe_function_manager.py' in file_path:
        return 'security_sfm'
    elif 'security/ai_agents/' in file_path:
        return 'ai_agent'
    elif 'security/bots/' in file_path:
        return 'bot'
    elif 'security/microservices/' in file_path:
        return 'microservice'
    elif 'security/' in file_path:
        return 'security'
    else:
        return 'other'

def main():
    """Основная функция"""
    print("🔍 БЫСТРЫЙ АНАЛИЗ FLAKE8 ДЛЯ КЛЮЧЕВЫХ ФАЙЛОВ SFM СИСТЕМЫ")
    print("=" * 70)
    
    # Получаем ключевые файлы
    key_files = get_key_files()
    print(f"📁 Найдено {len(key_files)} ключевых файлов")
    
    results = {
        'total_files': len(key_files),
        'clean_files': 0,
        'files_with_errors': 0,
        'total_errors': 0,
        'error_types': defaultdict(int),
        'category_stats': defaultdict(lambda: {
            'total': 0,
            'clean': 0,
            'errors': 0,
            'total_error_count': 0
        }),
        'file_details': [],
        'critical_files': [],
        'analysis_time': datetime.now().isoformat()
    }
    
    print(f"\n🔍 АНАЛИЗ {len(key_files)} КЛЮЧЕВЫХ ФАЙЛОВ:")
    print("-" * 70)
    
    for i, file_path in enumerate(key_files, 1):
        category = categorize_file(file_path)
        
        print(f"[{i:2d}/{len(key_files)}] {file_path}")
        
        # Запуск flake8
        returncode, stdout, stderr = run_flake8_quick(file_path)
        
        # Анализ результатов
        if returncode == 0:
            total_errors = 0
            errors = {}
            status = "✅ ЧИСТЫЙ"
            results['clean_files'] += 1
            results['category_stats'][category]['clean'] += 1
        else:
            total_errors, errors = analyze_errors(stdout)
            if total_errors == 0:
                status = "✅ ЧИСТЫЙ"
                results['clean_files'] += 1
                results['category_stats'][category]['clean'] += 1
            else:
                status = f"❌ {total_errors} ошибок"
                results['files_with_errors'] += 1
                results['category_stats'][category]['errors'] += 1
                results['category_stats'][category]['total_error_count'] += total_errors
                
                # Добавляем в критические файлы если много ошибок
                if total_errors > 50:
                    results['critical_files'].append({
                        'file': file_path,
                        'category': category,
                        'errors': total_errors,
                        'error_types': errors
                    })
        
        # Обновление статистики
        results['total_errors'] += total_errors
        results['category_stats'][category]['total'] += 1
        
        for error_type, count in errors.items():
            results['error_types'][error_type] += count
        
        # Сохранение деталей
        file_detail = {
            'file_path': file_path,
            'category': category,
            'is_clean': total_errors == 0,
            'total_errors': total_errors,
            'errors': errors
        }
        results['file_details'].append(file_detail)
        
        print(f"     {status} ({category})")
        
        # Показываем топ-3 ошибки для файлов с ошибками
        if total_errors > 0 and total_errors <= 20:
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"       {error_type}: {count}")
    
    # Сохранение результатов
    output_file = 'FAST_FLAKE8_ANALYSIS_RESULTS.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Преобразуем defaultdict в обычные dict для JSON
        json_results = {
            'total_files': results['total_files'],
            'clean_files': results['clean_files'],
            'files_with_errors': results['files_with_errors'],
            'total_errors': results['total_errors'],
            'error_types': dict(results['error_types']),
            'category_stats': dict(results['category_stats']),
            'file_details': results['file_details'],
            'critical_files': results['critical_files'],
            'analysis_time': results['analysis_time']
        }
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    # Создание текстового отчета
    report_file = 'FAST_FLAKE8_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🔍 БЫСТРЫЙ АНАЛИЗ FLAKE8 ДЛЯ КЛЮЧЕВЫХ ФАЙЛОВ SFM СИСТЕМЫ\n\n")
        f.write(f"**Дата анализа:** {results['analysis_time']}\n")
        f.write(f"**Аналитик:** AI Security Assistant\n")
        f.write(f"**Настройки:** Базовый flake8 (pyproject.toml)\n\n")
        
        f.write("## 📊 ОБЩАЯ СТАТИСТИКА\n\n")
        f.write(f"- **Всего файлов:** {results['total_files']}\n")
        f.write(f"- **Чистых файлов:** {results['clean_files']} ({results['clean_files']/results['total_files']*100:.1f}%)\n")
        f.write(f"- **Файлов с ошибками:** {results['files_with_errors']} ({results['files_with_errors']/results['total_files']*100:.1f}%)\n")
        f.write(f"- **Всего ошибок:** {results['total_errors']}\n\n")
        
        f.write("## 📈 ТОП-10 ОШИБОК ПО ТИПАМ\n\n")
        for i, (error_type, count) in enumerate(sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True)[:10], 1):
            f.write(f"{i:2d}. **{error_type}:** {count} ошибок\n")
        
        f.write("\n## 📁 СТАТИСТИКА ПО КАТЕГОРИЯМ\n\n")
        for category, stats in results['category_stats'].items():
            if stats['total'] > 0:
                clean_percent = stats['clean'] / stats['total'] * 100
                f.write(f"- **{category}:** {stats['clean']}/{stats['total']} чистых ({clean_percent:.1f}%), {stats['total_error_count']} ошибок\n")
        
        f.write("\n## 🚨 КРИТИЧЕСКИЕ ФАЙЛЫ (более 50 ошибок)\n\n")
        if results['critical_files']:
            for file_info in results['critical_files']:
                f.write(f"- **{file_info['file']}** ({file_info['category']}): {file_info['errors']} ошибок\n")
        else:
            f.write("Нет файлов с критическим количеством ошибок.\n")
        
        f.write("\n## 📋 ДЕТАЛЬНЫЙ СПИСОК ФАЙЛОВ\n\n")
        for file_detail in results['file_details']:
            status = "✅ ЧИСТЫЙ" if file_detail['is_clean'] else f"❌ {file_detail['total_errors']} ошибок"
            f.write(f"- **{file_detail['file_path']}** ({file_detail['category']}): {status}\n")
            if not file_detail['is_clean'] and file_detail['total_errors'] <= 10:
                for error_type, count in sorted(file_detail['errors'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  - {error_type}: {count}\n")
    
    # Итоговый отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 70)
    print(f"Всего файлов: {results['total_files']}")
    print(f"Чистых файлов: {results['clean_files']} ({results['clean_files']/results['total_files']*100:.1f}%)")
    print(f"Файлов с ошибками: {results['files_with_errors']} ({results['files_with_errors']/results['total_files']*100:.1f}%)")
    print(f"Всего ошибок: {results['total_errors']}")
    
    print(f"\n📈 ТОП-10 ОШИБОК ПО ТИПАМ:")
    for i, (error_type, count) in enumerate(sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True)[:10], 1):
        print(f"  {i:2d}. {error_type}: {count}")
    
    print(f"\n📁 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    for category, stats in results['category_stats'].items():
        if stats['total'] > 0:
            clean_percent = stats['clean'] / stats['total'] * 100
            print(f"  {category}: {stats['clean']}/{stats['total']} чистых ({clean_percent:.1f}%), {stats['total_error_count']} ошибок")
    
    print(f"\n🚨 КРИТИЧЕСКИЕ ФАЙЛЫ (более 50 ошибок):")
    if results['critical_files']:
        for file_info in results['critical_files']:
            print(f"  {file_info['file']} ({file_info['category']}): {file_info['errors']} ошибок")
    else:
        print("  Нет файлов с критическим количеством ошибок.")
    
    print(f"\n💾 Детальные отчеты сохранены:")
    print(f"  - JSON: {output_file}")
    print(f"  - Markdown: {report_file}")

if __name__ == "__main__":
    main()