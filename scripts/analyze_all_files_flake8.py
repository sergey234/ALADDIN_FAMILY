#!/usr/bin/env python3
"""
🔍 ALADDIN - Flake8 Analysis Script
Анализ всех созданных файлов на ошибки flake8

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import os
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

def run_flake8_on_file(file_path):
    """Запускает flake8 на файле и возвращает количество ошибок"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', str(file_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return 0, []
        else:
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return len(lines), lines
    except Exception as e:
        return -1, [f"Error analyzing {file_path}: {str(e)}"]

def analyze_all_files():
    """Анализирует все созданные файлы"""
    
    # Пути к файлам для анализа
    base_path = Path("/Users/sergejhlystov/ALADDIN_NEW")
    
    file_groups = {
        "🔧 Интеграционные модули": [
            base_path / "security" / "integrations" / "antifrod_integration.py",
            base_path / "security" / "integrations" / "audio_deepfake_detection.py",
            base_path / "security" / "integrations" / "children_cyber_protection.py",
            base_path / "security" / "integrations" / "crypto_fraud_protection.py",
            base_path / "security" / "integrations" / "ddos_protection.py",
            base_path / "security" / "integrations" / "fakeradar_integration.py",
            base_path / "security" / "integrations" / "max_messenger_protection.py",
            base_path / "security" / "integrations" / "national_security_system.py",
            base_path / "security" / "integrations" / "russian_ai_models.py",
            base_path / "security" / "integrations" / "russian_banking_integration.py",
            base_path / "security" / "integrations" / "russian_threat_intelligence.py",
            base_path / "security" / "integrations" / "sim_card_monitoring.py",
            base_path / "security" / "integrations" / "telegram_fake_chat_detection.py",
            base_path / "security" / "integrations" / "vk_messenger_protection.py",
        ],
        
        "🔧 Расширения модулей": [
            base_path / "security" / "security_monitoring_fakeradar_expansion.py",
            base_path / "security" / "security_analytics_antifrod_expansion.py",
            base_path / "security" / "security_analytics_russian_banking_expansion.py",
            base_path / "security" / "threat_intelligence_russian_context_expansion.py",
            base_path / "security" / "ai_agents" / "family_communication_hub_children_protection_expansion.py",
            base_path / "security" / "ai_agents" / "family_communication_hub_max_messenger_expansion.py",
            base_path / "security" / "bots" / "incognito_protection_bot_telegram_expansion.py",
        ],
        
        "📜 Скрипты создания": [
            base_path / "scripts" / "create_sim_card_monitoring.py",
            base_path / "scripts" / "create_max_messenger_integration.py",
            base_path / "scripts" / "create_banking_integration.py",
            base_path / "scripts" / "create_gosuslugi_integration.py",
            base_path / "scripts" / "create_digital_sovereignty.py",
            base_path / "scripts" / "create_telegram_enhancement.py",
            base_path / "scripts" / "create_audio_deepfake_detection.py",
            base_path / "scripts" / "create_vk_messenger_integration.py",
            base_path / "scripts" / "create_crypto_fraud_protection.py",
            base_path / "scripts" / "create_ddos_protection.py",
            base_path / "scripts" / "integrate_fakeradar.py",
            base_path / "scripts" / "integrate_antifrod_system.py",
            base_path / "scripts" / "test_call_protection_system.py",
            base_path / "scripts" / "run_all_integrations.py",
            base_path / "scripts" / "create_children_cyber_threats_protection.py",
        ]
    }
    
    results = {}
    total_files = 0
    total_errors = 0
    
    print("🔍 АНАЛИЗ ВСЕХ СОЗДАННЫХ ФАЙЛОВ НА ОШИБКИ FLAKE8")
    print("=" * 80)
    
    for group_name, file_list in file_groups.items():
        print(f"\n📂 {group_name}:")
        print("-" * 60)
        
        group_errors = 0
        group_files = 0
        
        for file_path in file_list:
            if file_path.exists():
                file_name = file_path.name
                error_count, error_details = run_flake8_on_file(file_path)
                
                if error_count == -1:
                    print(f"❌ {file_name}: ОШИБКА АНАЛИЗА")
                elif error_count == 0:
                    print(f"✅ {file_name}: 0 ошибок")
                else:
                    print(f"⚠️  {file_name}: {error_count} ошибок")
                
                results[file_name] = error_count
                group_errors += max(0, error_count)
                group_files += 1
                total_files += 1
                total_errors += max(0, error_count)
            else:
                print(f"❓ {file_path.name}: ФАЙЛ НЕ НАЙДЕН")
        
        print(f"\n📊 {group_name} - Итого: {group_files} файлов, {group_errors} ошибок")
    
    # Итоговая статистика
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    print(f"📁 Всего файлов проанализировано: {total_files}")
    print(f"⚠️  Всего ошибок flake8: {total_errors}")
    
    if total_files > 0:
        avg_errors = total_errors / total_files
        print(f"📈 Среднее количество ошибок на файл: {avg_errors:.2f}")
    
    # Топ файлов с ошибками
    if results:
        print(f"\n🔝 ТОП-10 ФАЙЛОВ С НАИБОЛЬШИМ КОЛИЧЕСТВОМ ОШИБОК:")
        print("-" * 60)
        
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for i, (file_name, error_count) in enumerate(sorted_results[:10]):
            if error_count > 0:
                print(f"{i+1:2d}. {file_name}: {error_count} ошибок")
    
    # Файлы без ошибок
    clean_files = [name for name, count in results.items() if count == 0]
    if clean_files:
        print(f"\n✅ ФАЙЛЫ БЕЗ ОШИБОК ({len(clean_files)}):")
        print("-" * 60)
        for file_name in clean_files:
            print(f"✅ {file_name}")
    
    return results, total_files, total_errors

if __name__ == "__main__":
    print("🚀 Запуск анализа всех файлов...")
    results, total_files, total_errors = analyze_all_files()
    
    print(f"\n🎯 АНАЛИЗ ЗАВЕРШЕН!")
    print(f"📊 Результаты: {total_files} файлов, {total_errors} ошибок")