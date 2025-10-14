#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое тестирование Antivirus Security System
Быстрый тест основных функций антивируса
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.antivirus.antivirus_security_system import AntivirusSecuritySystem, AntivirusEngine

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_antivirus_simple():
    """Простое тестирование антивируса"""
    print("🛡️ ПРОСТОЕ ТЕСТИРОВАНИЕ ANTIVIRUS SECURITY SYSTEM")
    print("=" * 60)
    
    try:
        # Создание антивирусной системы
        print("1. Создание Antivirus Security System...")
        antivirus = AntivirusSecuritySystem("SimpleTestAntivirus")
        print("✅ Antivirus Security System создан")
        
        # Проверка статуса
        print("\n2. Проверка статуса системы...")
        status = antivirus.get_status()
        print(f"   Статус: {status['status']}")
        print(f"   Сообщение: {status['message']}")
        
        # Получение статистики
        print("\n3. Получение статистики...")
        stats = antivirus.get_system_statistics()
        print(f"   Время работы: {stats['uptime']} секунд")
        print(f"   Всего сканирований: {stats['total_scans']}")
        print(f"   Найдено угроз: {stats['threats_found']}")
        
        # Создание тестового файла с EICAR
        print("\n4. Создание тестового файла с EICAR...")
        test_file = "security/antivirus/temp/eicar_test.txt"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write("X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        print(f"   Создан тестовый файл: {test_file}")
        
        # Сканирование файла
        print("\n5. Сканирование тестового файла...")
        result = await antivirus.scan_file(test_file, AntivirusEngine.ALL)
        
        if result['threats_found']:
            print(f"   ✅ Найдены угрозы: {len(result['threats'])}")
            for threat in result['threats']:
                if hasattr(threat, 'name'):
                    threat_type = getattr(threat, 'threat_type', getattr(threat, 'malware_type', 'unknown'))
                    if hasattr(threat_type, 'value'):
                        print(f"      - {threat.name} ({threat_type.value})")
                    else:
                        print(f"      - {threat.name} ({threat_type})")
                else:
                    print(f"      - {threat.get('name', 'Unknown')} ({threat.get('type', 'Unknown')})")
        else:
            print("   ℹ️ Угрозы не найдены")
        
        print(f"   Время сканирования: {result['total_scan_time']:.2f}с")
        
        # Создание тестового файла с подозрительным содержимым
        print("\n6. Создание файла с подозрительным содержимым...")
        suspicious_file = "security/antivirus/temp/suspicious_test.txt"
        
        with open(suspicious_file, 'w') as f:
            f.write("This is a test file with suspicious PowerShell command: powershell -enc UwB0AGEAcgB0AC0AUwBsAGUAZQBwACAAMQAwAA==")
        print(f"   Создан файл: {suspicious_file}")
        
        # Сканирование подозрительного файла
        print("\n7. Сканирование подозрительного файла...")
        result2 = await antivirus.scan_file(suspicious_file, AntivirusEngine.ALL)
        
        if result2['threats_found']:
            print(f"   ✅ Найдены угрозы: {len(result2['threats'])}")
            for threat in result2['threats']:
                if hasattr(threat, 'name'):
                    threat_type = getattr(threat, 'threat_type', getattr(threat, 'malware_type', 'unknown'))
                    if hasattr(threat_type, 'value'):
                        print(f"      - {threat.name} ({threat_type.value})")
                    else:
                        print(f"      - {threat.name} ({threat_type})")
                else:
                    print(f"      - {threat.get('name', 'Unknown')} ({threat.get('type', 'Unknown')})")
        else:
            print("   ℹ️ Угрозы не найдены")
        
        # Проверка карантина
        print("\n8. Проверка карантина...")
        quarantine_items = antivirus.get_quarantine_items()
        print(f"   Файлов в карантине: {len(quarantine_items)}")
        
        for item in quarantine_items:
            print(f"      - {item['original_path']} (угроз: {len(item['threats'])})")
        
        # Финальная статистика
        print("\n9. Финальная статистика...")
        final_stats = antivirus.get_system_statistics()
        print(f"   Всего сканирований: {final_stats['total_scans']}")
        print(f"   Найдено угроз: {final_stats['threats_found']}")
        print(f"   Файлов в карантине: {final_stats['files_quarantined']}")
        print(f"   Движки: {final_stats['engines']}")
        
        # Очистка тестовых файлов
        print("\n10. Очистка тестовых файлов...")
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(suspicious_file):
                os.remove(suspicious_file)
            print("   ✅ Тестовые файлы удалены")
        except Exception as e:
            print(f"   ⚠️ Ошибка удаления файлов: {e}")
        
        print("\n🎉 ПРОСТОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🛡️ ANTIVIRUS SECURITY SYSTEM - ПРОСТОЕ ТЕСТИРОВАНИЕ")
    print("=" * 70)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Простое тестирование
    success = await test_antivirus_simple()
    
    print("\n" + "=" * 70)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
