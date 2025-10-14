#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест работоспособности encryption_manager.py
Проверяет все основные функции после форматирования
"""

import sys
import os
import logging
import asyncio
from datetime import datetime

# Добавляем путь к модулю
sys.path.append('.')

try:
    from security.bots.components.encryption_manager import (
        EncryptionManager,
        EncryptionAlgorithm,
        EncryptedData,
        KeyDerivation
    )
    print("✅ Импорт модулей успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Тест базовой функциональности"""
    print("\n🔍 Тестирование базовой функциональности...")
    
    # Создаем логгер
    logger = logging.getLogger("test_encryption")
    logger.setLevel(logging.INFO)
    
    try:
        # Создаем экземпляр менеджера
        manager = EncryptionManager(
            logger=logger,
            master_password="test_password_123",
            key_derivation=KeyDerivation.PBKDF2,
            default_algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_rotation_days=90
        )
        print("✅ Создание EncryptionManager успешно")
        
        # Проверяем основные атрибуты
        assert hasattr(manager, 'logger'), "Отсутствует атрибут logger"
        assert hasattr(manager, 'master_password'), "Отсутствует атрибут master_password"
        assert hasattr(manager, 'default_algorithm'), "Отсутствует атрибут default_algorithm"
        print("✅ Основные атрибуты присутствуют")
        
        # Проверяем методы
        assert hasattr(manager, 'encrypt_data'), "Отсутствует метод encrypt_data"
        assert hasattr(manager, 'decrypt_data'), "Отсутствует метод decrypt_data"
        assert hasattr(manager, 'get_encryption_stats'), "Отсутствует метод get_encryption_stats"
        print("✅ Основные методы присутствуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в базовой функциональности: {e}")
        return False

async def test_encryption_workflow():
    """Тест рабочего процесса шифрования"""
    print("\n🔐 Тестирование рабочего процесса шифрования...")
    
    logger = logging.getLogger("test_encryption")
    logger.setLevel(logging.INFO)
    
    try:
        manager = EncryptionManager(
            logger=logger,
            master_password="test_password_123"
        )
        
        # Тестовые данные
        test_data = {
            "message": "Тестовое сообщение для шифрования",
            "timestamp": datetime.now().isoformat(),
            "user_id": 12345
        }
        
        # Шифрование
        encrypted = await manager.encrypt_data(test_data)
        print("✅ Шифрование данных успешно")
        
        # Проверяем структуру зашифрованных данных
        assert isinstance(encrypted, EncryptedData), "Неправильный тип зашифрованных данных"
        assert hasattr(encrypted, 'data'), "Отсутствует атрибут data"
        assert hasattr(encrypted, 'key_id'), "Отсутствует атрибут key_id"
        assert hasattr(encrypted, 'algorithm'), "Отсутствует атрибут algorithm"
        print("✅ Структура зашифрованных данных корректна")
        
        # Расшифровка
        decrypted = await manager.decrypt_data(encrypted)
        print("✅ Расшифровка данных успешна")
        
        # Проверяем, что данные совпадают
        assert decrypted == test_data, "Данные после расшифровки не совпадают"
        print("✅ Данные после расшифровки совпадают с оригиналом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в рабочем процессе шифрования: {e}")
        return False

def test_statistics():
    """Тест статистики"""
    print("\n📊 Тестирование статистики...")
    
    logger = logging.getLogger("test_encryption")
    logger.setLevel(logging.INFO)
    
    try:
        manager = EncryptionManager(
            logger=logger,
            master_password="test_password_123"
        )
        
        stats = manager.get_encryption_stats()
        print("✅ Получение статистики успешно")
        
        # Проверяем структуру статистики
        assert isinstance(stats, dict), "Статистика должна быть словарем"
        print("✅ Структура статистики корректна")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в статистике: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА РАБОТОСПОСОБНОСТИ")
    print("=" * 60)
    
    tests = [
        ("Базовая функциональность", test_basic_functionality),
        ("Рабочий процесс шифрования", test_encryption_workflow),
        ("Статистика", test_statistics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Тест: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name}: ПРОЙДЕН")
            else:
                print(f"❌ {test_name}: ПРОВАЛЕН")
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
    
    print("\n" + "=" * 60)
    print(f"📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Функциональность работает корректно.")
        return True
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ. Требуется дополнительная проверка.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)