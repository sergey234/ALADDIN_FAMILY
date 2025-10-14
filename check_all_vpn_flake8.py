#!/usr/bin/env python3
"""
Скрипт для проверки всех VPN файлов на ошибки flake8
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
    # Список файлов для проверки
    files_to_check = [
        # Критические ошибки (20+ ошибок)
        "security/vpn/validators/vpn_validators.py",
        "security/vpn/test_final_integration.py", 
        "security/vpn/test_security_systems.py",
        "security/vpn/test_performance_features.py",
        
        # Средние ошибки (20-50 ошибок)
        "security/vpn/analytics/ml_detector.py",
        "security/vpn/factories/vpn_factory.py",
        "security/vpn/test_vpn_modules.py",
        "security/vpn/test_vpn_modules_fixed.py",
        "security/vpn/models/vpn_models.py",
        "security/vpn/web/vpn_web_interface_premium.py",
        "security/vpn/web/vpn_web_server.py",
        "security/vpn/web/vpn_web_interface.py",
        
        # Малые ошибки (1-19 ошибок)
        "security/vpn/config/vpn_constants.py",
        "security/vpn/features/__init__.py",
        "security/vpn/models/__init__.py",
        "security/vpn/validators/__init__.py",
        "security/vpn/web/vpn_variant_1.py",
        "security/vpn/web/vpn_variant_2.py",
        "security/vpn/vpn_integration.py",
        "security/vpn/service_orchestrator.py",
        "security/vpn/test_compliance_152_fz.py",
        "security/vpn/test_intrusion_detection_functionality.py",
        "security/vpn/test_performance_manager_functionality.py",
        "security/vpn/auth/__init__.py",
        "security/vpn/protection/__init__.py",
        "security/vpn/compliance/__init__.py",
        "security/vpn/performance/__init__.py",
        
        # Пропавшие файлы (проверим их наличие)
        "security/vpn/protocols/wireguard_server.py",
        "security/vpn/protocols/openvpn_server.py"
    ]
    
    print("🔍 ПРОВЕРКА ВСЕХ VPN ФАЙЛОВ НА ОШИБКИ FLAKE8")
    print("=" * 60)
    
    total_errors = 0
    files_with_errors = 0
    missing_files = 0
    
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
        else:
            files_with_errors += 1
            error_count = len(stdout.split('\n')) - 1  # -1 для пустой строки в конце
            total_errors += error_count
            
            print(f"❌ Найдено ошибок: {error_count}")
            
            # Показываем первые 10 ошибок
            lines = stdout.strip().split('\n')
            for i, line in enumerate(lines[:10]):
                print(f"   {line}")
            
            if len(lines) > 10:
                print(f"   ... и еще {len(lines) - 10} ошибок")
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего файлов проверено: {len(files_to_check)}")
    print(f"   Файлов с ошибками: {files_with_errors}")
    print(f"   Пропавших файлов: {missing_files}")
    print(f"   Общее количество ошибок: {total_errors}")
    
    if total_errors > 0:
        print(f"\n🔧 РЕКОМЕНДАЦИИ:")
        print("   1. Исправить неиспользуемые импорты (F401)")
        print("   2. Удалить пробелы в пустых строках (W293)")
        print("   3. Добавить пустые строки между функциями (E302)")
        print("   4. Добавить новую строку в конце файла (W292)")
        print("   5. Удалить trailing whitespace (W291)")

if __name__ == "__main__":
    main()