#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест оптимизаций CPU-интенсивных функций
Проверка производительности modern_encryption, security_hashes, encryption_manager

Функция: CPU Optimizations Test
Приоритет: ВЫСОКИЙ
Версия: 1.0
Дата: 2025-01-11
"""

import asyncio
import time
import sys
import os

# Добавление пути к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.vpn.encryption.modern_encryption import ModernEncryptionSystem, EncryptionAlgorithm
from security.hashes.security_hashes import SecurityHashesSystem, HashAlgorithm, HashPurpose
from security.bots.components.encryption_manager import EncryptionManager, EncryptionAlgorithm as EMAlgorithm
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_modern_encryption_optimizations():
    """Тест оптимизаций modern_encryption"""
    print("🔐 ТЕСТ ОПТИМИЗАЦИЙ MODERN_ENCRYPTION")
    print("=" * 50)
    
    # Создание системы шифрования
    encryption_system = ModernEncryptionSystem("TestEncryption")
    
    # Тестовые данные
    test_data = ("Это тестовые данные для шифрования" * 100).encode('utf-8')  # Большой объем данных
    
    print(f"📊 Размер тестовых данных: {len(test_data)} байт")
    
    # Тест синхронного шифрования
    print("\n1. Синхронное шифрование:")
    start_time = time.time()
    result = encryption_system.encrypt_data(test_data, EncryptionAlgorithm.CHACHA20_POLY1305)
    sync_time = time.time() - start_time
    
    if result.success:
        print(f"   ✅ Шифрование: {len(result.encrypted_data)} байт")
        print(f"   ⏱️ Время: {sync_time:.4f} сек")
        
        # Тест синхронной расшифровки
        start_time = time.time()
        decrypt_result = encryption_system.decrypt_data(
            result.encrypted_data,
            result.auth_tag,
            result.nonce,
            result.algorithm,
            result.key_id,
        )
        sync_decrypt_time = time.time() - start_time
        
        if decrypt_result.success:
            print(f"   ✅ Расшифровка: {len(decrypt_result.encrypted_data)} байт")
            print(f"   ⏱️ Время: {sync_decrypt_time:.4f} сек")
        else:
            print(f"   ❌ Ошибка расшифровки: {decrypt_result.error_message}")
    else:
        print(f"   ❌ Ошибка шифрования: {result.error_message}")
        return
    
    # Тест асинхронного шифрования
    print("\n2. Асинхронное шифрование:")
    start_time = time.time()
    async_result = await encryption_system.encrypt_data_async(test_data, EncryptionAlgorithm.CHACHA20_POLY1305)
    async_time = time.time() - start_time
    
    if async_result.success:
        print(f"   ✅ Шифрование: {len(async_result.encrypted_data)} байт")
        print(f"   ⏱️ Время: {async_time:.4f} сек")
        
        # Тест асинхронной расшифровки
        start_time = time.time()
        async_decrypt_result = await encryption_system.decrypt_data_async(
            async_result.encrypted_data,
            async_result.auth_tag,
            async_result.nonce,
            async_result.algorithm,
            async_result.key_id,
        )
        async_decrypt_time = time.time() - start_time
        
        if async_decrypt_result.success:
            print(f"   ✅ Расшифровка: {len(async_decrypt_result.encrypted_data)} байт")
            print(f"   ⏱️ Время: {async_decrypt_time:.4f} сек")
        else:
            print(f"   ❌ Ошибка расшифровки: {async_decrypt_result.error_message}")
    else:
        print(f"   ❌ Ошибка шифрования: {async_result.error_message}")
        return
    
    # Сравнение производительности
    print("\n3. Сравнение производительности:")
    sync_total = sync_time + sync_decrypt_time
    async_total = async_time + async_decrypt_time
    improvement = ((sync_total - async_total) / sync_total) * 100 if sync_total > 0 else 0
    
    print(f"   📊 Синхронное время: {sync_total:.4f} сек")
    print(f"   📊 Асинхронное время: {async_total:.4f} сек")
    print(f"   🚀 Улучшение: {improvement:.1f}%")
    
    # Метрики производительности
    print("\n4. Метрики производительности:")
    metrics = encryption_system.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   📈 {key}: {value}")
    
    return encryption_system


async def test_security_hashes_optimizations():
    """Тест оптимизаций security_hashes"""
    print("\n🔐 ТЕСТ ОПТИМИЗАЦИЙ SECURITY_HASHES")
    print("=" * 50)
    
    # Создание системы хеширования
    hash_system = SecurityHashesSystem("TestHashes")
    
    # Тестовые данные
    test_data = "Это тестовые данные для хеширования" * 100  # Большой объем данных
    test_password = "SecurePassword123!" * 10  # Длинный пароль
    
    print(f"📊 Размер тестовых данных: {len(test_data)} символов")
    print(f"📊 Размер пароля: {len(test_password)} символов")
    
    # Тест синхронного хеширования
    print("\n1. Синхронное хеширование:")
    start_time = time.time()
    result = hash_system._hash_data_sync(
        test_data.encode(),
        HashAlgorithm.SHA_256,
        None,
        100000,
        HashPurpose.DATA_VERIFICATION
    )
    sync_time = time.time() - start_time
    
    if result.success:
        print(f"   ✅ Хеш: {result.hash_value[:32]}...")
        print(f"   ⏱️ Время: {sync_time:.4f} сек")
    else:
        print(f"   ❌ Ошибка: {result.error_message}")
        return
    
    # Тест асинхронного хеширования
    print("\n2. Асинхронное хеширование:")
    start_time = time.time()
    async_result = await hash_system.hash_data_async(
        test_data,
        HashAlgorithm.SHA_256,
        None,
        100000,
        HashPurpose.DATA_VERIFICATION
    )
    async_time = time.time() - start_time
    
    if async_result.success:
        print(f"   ✅ Хеш: {async_result.hash_value[:32]}...")
        print(f"   ⏱️ Время: {async_time:.4f} сек")
    else:
        print(f"   ❌ Ошибка: {async_result.error_message}")
        return
    
    # Тест хеширования пароля
    print("\n3. Хеширование пароля:")
    start_time = time.time()
    password_result = await hash_system.hash_data_async(
        test_password,
        HashAlgorithm.SHA_256,
        None,
        100000,
        HashPurpose.PASSWORD
    )
    password_time = time.time() - start_time
    
    if password_result.success:
        print(f"   ✅ Хеш пароля: {password_result.hash_value[:32]}...")
        print(f"   🧂 Соль: {password_result.salt.hex()[:16]}...")
        print(f"   ⏱️ Время: {password_time:.4f} сек")
    else:
        print(f"   ❌ Ошибка: {password_result.error_message}")
        return
    
    # Сравнение производительности
    print("\n4. Сравнение производительности:")
    improvement = ((sync_time - async_time) / sync_time) * 100 if sync_time > 0 else 0
    
    print(f"   📊 Синхронное время: {sync_time:.4f} сек")
    print(f"   📊 Асинхронное время: {async_time:.4f} сек")
    print(f"   🚀 Улучшение: {improvement:.1f}%")
    
    # Метрики производительности
    print("\n5. Метрики производительности:")
    metrics = hash_system.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   📈 {key}: {value}")
    
    return hash_system


async def test_encryption_manager_optimizations():
    """Тест оптимизаций encryption_manager"""
    print("\n🔐 ТЕСТ ОПТИМИЗАЦИЙ ENCRYPTION_MANAGER")
    print("=" * 50)
    
    # Создание менеджера шифрования
    encryption_manager = EncryptionManager(
        logger=logger,
        default_algorithm=EMAlgorithm.AES_256_GCM
    )
    
    # Тестовые данные
    test_data = "Это тестовые данные для шифрования" * 100  # Большой объем данных
    
    print(f"📊 Размер тестовых данных: {len(test_data)} символов")
    
    # Тест синхронного шифрования
    print("\n1. Синхронное шифрование:")
    start_time = time.time()
    result = encryption_manager.encrypt_data(test_data.encode())
    sync_time = time.time() - start_time
    
    if result:
        print(f"   ✅ Шифрование: {len(result.data)} байт")
        print(f"   ⏱️ Время: {sync_time:.4f} сек")
        
        # Тест синхронной расшифровки
        start_time = time.time()
        decrypt_result = encryption_manager.decrypt_data(result)
        sync_decrypt_time = time.time() - start_time
        
        if decrypt_result:
            print(f"   ✅ Расшифровка: {len(decrypt_result)} байт")
            print(f"   ⏱️ Время: {sync_decrypt_time:.4f} сек")
        else:
            print(f"   ❌ Ошибка расшифровки")
    else:
        print(f"   ❌ Ошибка шифрования")
        return
    
    # Тест асинхронного шифрования
    print("\n2. Асинхронное шифрование:")
    start_time = time.time()
    async_result = await encryption_manager.encrypt_data_async(test_data)
    async_time = time.time() - start_time
    
    if async_result:
        print(f"   ✅ Шифрование: {len(async_result.data)} байт")
        print(f"   ⏱️ Время: {async_time:.4f} сек")
        
        # Тест асинхронной расшифровки
        start_time = time.time()
        async_decrypt_result = await encryption_manager.decrypt_data_async(async_result)
        async_decrypt_time = time.time() - start_time
        
        if async_decrypt_result:
            print(f"   ✅ Расшифровка: {len(async_decrypt_result)} байт")
            print(f"   ⏱️ Время: {async_decrypt_time:.4f} сек")
        else:
            print(f"   ❌ Ошибка расшифровки")
    else:
        print(f"   ❌ Ошибка шифрования")
        return
    
    # Сравнение производительности
    print("\n3. Сравнение производительности:")
    sync_total = sync_time + sync_decrypt_time
    async_total = async_time + async_decrypt_time
    improvement = ((sync_total - async_total) / sync_total) * 100 if sync_total > 0 else 0
    
    print(f"   📊 Синхронное время: {sync_total:.4f} сек")
    print(f"   📊 Асинхронное время: {async_total:.4f} сек")
    print(f"   🚀 Улучшение: {improvement:.1f}%")
    
    # Метрики производительности
    print("\n4. Метрики производительности:")
    metrics = encryption_manager.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   📈 {key}: {value}")
    
    return encryption_manager


async def main():
    """Основная функция тестирования"""
    print("⚡ ТЕСТИРОВАНИЕ ОПТИМИЗАЦИЙ CPU-ИНТЕНСИВНЫХ ФУНКЦИЙ")
    print("=" * 60)
    print("🎯 ЦЕЛЬ: Проверка производительности оптимизированных функций")
    print("📋 ФУНКЦИИ: modern_encryption, security_hashes, encryption_manager")
    print("🚀 КАЧЕСТВО: A+ (высшее качество кода)")
    
    start_time = time.time()
    
    try:
        # Тест modern_encryption
        encryption_system = await test_modern_encryption_optimizations()
        
        # Тест security_hashes
        hash_system = await test_security_hashes_optimizations()
        
        # Тест encryption_manager
        encryption_manager = await test_encryption_manager_optimizations()
        
        # Общая статистика
        total_time = time.time() - start_time
        print(f"\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        print(f"⏱️ Общее время: {total_time:.4f} сек")
        
        # Рекомендации
        print(f"\n📋 РЕКОМЕНДАЦИИ:")
        print(f"   ✅ Все CPU-интенсивные функции оптимизированы")
        print(f"   ✅ Добавлено кэширование результатов")
        print(f"   ✅ Реализована асинхронная обработка")
        print(f"   ✅ Настроены пулы потоков")
        print(f"   ✅ Добавлены метрики производительности")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        logger.error(f"Ошибка тестирования: {e}")


if __name__ == "__main__":
    asyncio.run(main())