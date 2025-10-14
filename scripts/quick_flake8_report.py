#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый анализ flake8 для ключевых компонентов
"""

import subprocess
import json
from collections import defaultdict

def run_flake8_quick(file_path):
    """Быстрый запуск flake8"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            file_path, 
            '--max-line-length=120',
            '--statistics'
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

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

def main():
    """Основная функция"""
    print("🔍 БЫСТРЫЙ АНАЛИЗ FLAKE8 ДЛЯ КЛЮЧЕВЫХ КОМПОНЕНТОВ")
    print("=" * 60)
    
    # Ключевые файлы для проверки
    key_files = [
        # CORE (5 функций)
        ('core/base.py', 'CORE - Базовая архитектура'),
        ('core/service_base.py', 'CORE - Базовый сервис'),
        ('core/database.py', 'CORE - База данных'),
        ('core/configuration.py', 'CORE - Конфигурация'),
        ('core/logging_module.py', 'CORE - Логирование'),
        
        # SECURITY - основные (топ 20)
        ('security/safe_function_manager.py', 'SECURITY - Главный менеджер'),
        ('security/enhanced_alerting.py', 'SECURITY - Расширенные алерты'),
        ('security/authentication.py', 'SECURITY - Аутентификация'),
        ('security/security_monitoring.py', 'SECURITY - Мониторинг'),
        ('security/incident_response.py', 'SECURITY - Реагирование на инциденты'),
        ('security/threat_detection.py', 'SECURITY - Обнаружение угроз'),
        ('security/malware_protection.py', 'SECURITY - Защита от malware'),
        ('security/intrusion_prevention.py', 'SECURITY - Предотвращение вторжений'),
        ('security/access_control_manager.py', 'SECURITY - Контроль доступа'),
        ('security/data_protection_manager.py', 'SECURITY - Защита данных'),
        ('security/zero_trust_manager.py', 'SECURITY - Zero Trust'),
        ('security/security_audit.py', 'SECURITY - Аудит безопасности'),
        ('security/compliance_manager.py', 'SECURITY - Соответствие'),
        ('security/threat_intelligence.py', 'SECURITY - Разведка угроз'),
        ('security/network_monitoring.py', 'SECURITY - Мониторинг сети'),
        ('security/ransomware_protection.py', 'SECURITY - Защита от ransomware'),
        ('security/advanced_alerting.py', 'SECURITY - Продвинутые алерты'),
        
        # AI AGENTS - основные (топ 15)
        ('security/ai_agents/threat_detection_agent.py', 'AI_AGENT - Обнаружение угроз'),
        ('security/ai_agents/behavioral_analysis_agent.py', 'AI_AGENT - Анализ поведения'),
        ('security/ai_agents/password_security_agent.py', 'AI_AGENT - Безопасность паролей'),
        ('security/ai_agents/incident_response_agent.py', 'AI_AGENT - Реагирование на инциденты'),
        ('security/ai_agents/threat_intelligence_agent.py', 'AI_AGENT - Разведка угроз'),
        ('security/ai_agents/network_security_agent.py', 'AI_AGENT - Сетевая безопасность'),
        ('security/ai_agents/data_protection_agent.py', 'AI_AGENT - Защита данных'),
        ('security/ai_agents/compliance_agent.py', 'AI_AGENT - Соответствие'),
        ('security/ai_agents/voice_analysis_engine.py', 'AI_AGENT - Анализ голоса'),
        ('security/ai_agents/deepfake_protection_system.py', 'AI_AGENT - Защита от deepfake'),
        ('security/ai_agents/financial_protection_hub.py', 'AI_AGENT - Финансовая защита'),
        ('security/ai_agents/emergency_response_system.py', 'AI_AGENT - Экстренное реагирование'),
        ('security/ai_agents/elderly_protection_interface.py', 'AI_AGENT - Защита пожилых'),
        ('security/ai_agents/phishing_protection.py', 'AI_AGENT - Защита от фишинга'),
        ('security/ai_agents/malware_detection.py', 'AI_AGENT - Обнаружение malware'),
        
        # BOTS - основные (топ 15)
        ('security/bots/emergency_response_bot.py', 'BOT - Экстренное реагирование'),
        ('security/bots/parental_control_bot.py', 'BOT - Родительский контроль'),
        ('security/bots/notification_bot.py', 'BOT - Уведомления'),
        ('security/bots/whatsapp_security_bot.py', 'BOT - WhatsApp безопасность'),
        ('security/bots/telegram_security_bot.py', 'BOT - Telegram безопасность'),
        ('security/bots/instagram_security_bot.py', 'BOT - Instagram безопасность'),
        ('security/bots/mobile_navigation_bot.py', 'BOT - Мобильная навигация'),
        ('security/bots/gaming_security_bot.py', 'BOT - Безопасность игр'),
        ('security/bots/analytics_bot.py', 'BOT - Аналитика'),
        ('security/bots/website_navigation_bot.py', 'BOT - Навигация по сайтам'),
        ('security/bots/browser_security_bot.py', 'BOT - Безопасность браузера'),
        ('security/bots/cloud_storage_security_bot.py', 'BOT - Облачное хранилище'),
        ('security/bots/device_security_bot.py', 'BOT - Безопасность устройств'),
        ('security/bots/incognito_protection_bot.py', 'BOT - Защита инкогнито'),
        ('security/bots/parental_control_bot.py', 'BOT - Родительский контроль'),
        
        # MICROSERVICES - основные (топ 10)
        ('security/microservices/api_gateway.py', 'MICROSERVICE - API Gateway'),
        ('security/microservices/load_balancer.py', 'MICROSERVICE - Балансировщик'),
        ('security/microservices/rate_limiter.py', 'MICROSERVICE - Ограничитель скорости'),
        ('security/microservices/circuit_breaker.py', 'MICROSERVICE - Предохранитель'),
        ('security/microservices/redis_cache_manager.py', 'MICROSERVICE - Redis кэш'),
        ('security/microservices/service_mesh_manager.py', 'MICROSERVICE - Сервисная сетка'),
        ('security/microservices/user_interface_manager.py', 'MICROSERVICE - UI менеджер'),
        ('security/microservices/emergency_service_caller.py', 'MICROSERVICE - Экстренные сервисы'),
        ('security/microservices/wake_up_systems.py', 'MICROSERVICE - Системы пробуждения'),
        ('security/microservices/safe_function_manager_integration.py', 'MICROSERVICE - SFM интеграция'),
    ]
    
    results = {
        'total_files': len(key_files),
        'clean_files': 0,
        'files_with_errors': 0,
        'total_errors': 0,
        'error_types': defaultdict(int),
        'files_by_category': defaultdict(list),
        'category_stats': defaultdict(lambda: {
            'total': 0,
            'clean': 0,
            'errors': 0,
            'total_error_count': 0
        }),
        'file_details': []
    }
    
    print(f"Проверяем {len(key_files)} ключевых файлов...\n")
    
    for i, (file_path, description) in enumerate(key_files, 1):
        print(f"[{i:2d}/{len(key_files)}] {file_path}")
        
        # Определение категории
        category = 'other'
        if 'CORE' in description:
            category = 'core'
        elif 'SECURITY' in description:
            category = 'security'
        elif 'AI_AGENT' in description:
            category = 'ai_agent'
        elif 'BOT' in description:
            category = 'bot'
        elif 'MICROSERVICE' in description:
            category = 'microservice'
        
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
        
        # Обновление статистики
        results['total_errors'] += total_errors
        results['category_stats'][category]['total'] += 1
        
        for error_type, count in errors.items():
            results['error_types'][error_type] += count
        
        # Сохранение деталей
        file_detail = {
            'file_path': file_path,
            'description': description,
            'category': category,
            'is_clean': total_errors == 0,
            'total_errors': total_errors,
            'errors': errors
        }
        results['file_details'].append(file_detail)
        results['files_by_category'][category].append(file_detail)
        
        print(f"     {status}")
        
        # Показываем топ-3 ошибки для файлов с ошибками
        if total_errors > 0 and total_errors <= 10:
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"       {error_type}: {count}")
    
    # Сохранение результатов
    with open('QUICK_FLAKE8_REPORT.json', 'w', encoding='utf-8') as f:
        # Преобразуем defaultdict в обычные dict для JSON
        json_results = {
            'total_files': results['total_files'],
            'clean_files': results['clean_files'],
            'files_with_errors': results['files_with_errors'],
            'total_errors': results['total_errors'],
            'error_types': dict(results['error_types']),
            'category_stats': dict(results['category_stats']),
            'file_details': results['file_details']
        }
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    # Итоговый отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 60)
    print(f"Всего файлов: {results['total_files']}")
    print(f"Чистых файлов: {results['clean_files']} ({results['clean_files']/results['total_files']*100:.1f}%)")
    print(f"Файлов с ошибками: {results['files_with_errors']} ({results['files_with_errors']/results['total_files']*100:.1f}%)")
    print(f"Всего ошибок: {results['total_errors']}")
    
    print(f"\n📈 ТОП-10 ОШИБОК ПО ТИПАМ:")
    for error_type, count in sorted(results['error_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {error_type}: {count}")
    
    print(f"\n📁 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    for category, stats in results['category_stats'].items():
        if stats['total'] > 0:
            clean_percent = stats['clean'] / stats['total'] * 100
            print(f"  {category}: {stats['clean']}/{stats['total']} чистых ({clean_percent:.1f}%), {stats['total_error_count']} ошибок")
    
    print(f"\n💾 Детальный отчет сохранен в: QUICK_FLAKE8_REPORT.json")

if __name__ == "__main__":
    main()