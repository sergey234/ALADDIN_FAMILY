#!/usr/bin/env python3
"""
Проверка исправленных файлов в formatting_work на ошибки flake8
"""

import subprocess
import sys
import os
from pathlib import Path

def run_flake8(file_path):
    """Запуск flake8 для файла"""
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            str(file_path), 
            '--max-line-length=120', 
            '--ignore=E501,W503'
        ], capture_output=True, text=True, cwd='/Users/sergejhlystov/ALADDIN_NEW')
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    # Список файлов для проверки в formatting_work
    files_to_check = [
        # service_orchestrator.py
        "formatting_work/service_orchestrator_analysis/service_orchestrator_formatted.py",
        "formatting_work/service_orchestrator_analysis/service_orchestrator_fixed.py",
        "formatting_work/service_orchestrator_analysis/service_orchestrator_final.py",
        
        # vpn_integration.py
        "formatting_work/vpn_integration_analysis/vpn_integration_formatted.py",
        "formatting_work/vpn_integration_analysis/vpn_integration_fixed.py",
        
        # protocols (проверим, есть ли они)
        "formatting_work/protocols/openvpn_server.py",
        "formatting_work/protocols/wireguard_server.py",
        
        # models/__init__.py
        "formatting_work/models/__init__.py",
        
        # config/vpn_constants.py
        "formatting_work/config/vpn_constants.py",
        
        # validators/__init__.py
        "formatting_work/validators/__init__.py",
        
        # validators/vpn_validators.py
        "formatting_work/validators/vpn_validators.py",
        
        # analytics/ml_detector.py
        "formatting_work/analytics/ml_detector.py",
        
        # factories/vpn_factory.py
        "formatting_work/factories/vpn_factory.py",
        
        # web/vpn_web_interface_premium.py
        "formatting_work/web/vpn_web_interface_premium.py",
        
        # models/vpn_models.py
        "formatting_work/models/vpn_models.py",
    ]
    
    print("🔍 ПРОВЕРКА ИСПРАВЛЕННЫХ ФАЙЛОВ В FORMATTING_WORK НА ОШИБКИ FLAKE8")
    print("=" * 70)
    
    total_errors = 0
    files_with_errors = 0
    missing_files = 0
    clean_files = 0
    
    for file_path in files_to_check:
        full_path = Path('/Users/sergejhlystov/ALADDIN_NEW') / file_path
        
        if not full_path.exists():
            print(f"❌ ПРОПАВШИЙ ФАЙЛ: {file_path}")
            missing_files += 1
            continue
            
        print(f"\n📁 Проверка: {file_path}")
        
        returncode, stdout, stderr = run_flake8(full_path)
        
        if returncode == 0:
            print("✅ Ошибок не найдено")
            clean_files += 1
        else:
            files_with_errors += 1
            error_count = len(stdout.split('\n')) - 1  # -1 для пустой строки в конце
            total_errors += error_count
            
            print(f"❌ Найдено ошибок: {error_count}")
            
            # Показываем первые 5 ошибок
            lines = stdout.strip().split('\n')
            for i, line in enumerate(lines[:5]):
                print(f"   {line}")
            
            if len(lines) > 5:
                print(f"   ... и еще {len(lines) - 5} ошибок")
    
    print("\n" + "=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего файлов проверено: {len(files_to_check)}")
    print(f"   Файлов без ошибок: {clean_files}")
    print(f"   Файлов с ошибками: {files_with_errors}")
    print(f"   Пропавших файлов: {missing_files}")
    print(f"   Общее количество ошибок: {total_errors}")
    
    if clean_files > 0:
        print(f"\n✅ ОТЛИЧНО! {clean_files} файлов уже исправлены и не содержат ошибок flake8!")
    
    if total_errors > 0:
        print(f"\n🔧 РЕКОМЕНДАЦИИ:")
        print("   1. Использовать исправленные версии из formatting_work")
        print("   2. Скопировать чистые файлы в основные директории")
        print("   3. Удалить неиспользуемые импорты (F401)")
        print("   4. Очистить пустые строки от пробелов (W293)")

if __name__ == "__main__":
    main()