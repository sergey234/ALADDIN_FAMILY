#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест атрибутов классов - encryption_manager.py
Версия: 2.5
Дата: 2025-09-24
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к модулям ALADDIN_NEW
sys.path.append(str(Path(__file__).resolve().parents[2]))

from security.bots.components.encryption_manager import (
    EncryptionManager,
    EncryptionAlgorithm,
    KeyDerivation,
    EncryptionKey,
    EncryptedData,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEncryptionManagerAttributes:
    """Тест атрибутов классов"""

    def __init__(self):
        self.logger = logger
        self.manager = None
        self.test_results = []

    async def test_encryption_manager_attributes(self):
        """Тест атрибутов EncryptionManager"""
        self.logger.info("🔍 Тестирование атрибутов EncryptionManager...")
        
        try:
            # Создаем экземпляр
            self.manager = EncryptionManager(self.logger)
            
            # Проверяем основные атрибуты
            required_attributes = [
                'logger',
                'master_password',
                'key_derivation',
                'default_algorithm',
                'key_rotation_days',
                'keys',
                'active_key_id',
                '_cipher_cache',
                '_cache_ttl'
            ]
            
            for attr in required_attributes:
                if hasattr(self.manager, attr):
                    value = getattr(self.manager, attr)
                    self.logger.info(f"✅ Атрибут {attr}: {type(value).__name__} = {value}")
                else:
                    self.logger.error(f"❌ Атрибут {attr} не найден")
                    self.test_results.append((f"Атрибут {attr}", False))
                    return False
            
            # Проверяем типы атрибутов
            assert isinstance(self.manager.logger, logging.Logger)
            assert isinstance(self.manager.master_password, str)
            assert isinstance(self.manager.key_derivation, KeyDerivation)
            assert isinstance(self.manager.default_algorithm, EncryptionAlgorithm)
            assert isinstance(self.manager.key_rotation_days, int)
            assert isinstance(self.manager.keys, dict)
            assert isinstance(self.manager._cipher_cache, dict)
            assert isinstance(self.manager._cache_ttl, int)
            
            self.logger.info("✅ Все атрибуты EncryptionManager корректны")
            self.test_results.append(("Атрибуты EncryptionManager", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования атрибутов EncryptionManager: {e}")
            self.test_results.append(("Атрибуты EncryptionManager", False))
            return False

    async def test_encryption_key_attributes(self):
        """Тест атрибутов EncryptionKey"""
        self.logger.info("🔍 Тестирование атрибутов EncryptionKey...")
        
        try:
            from datetime import datetime
            
            # Создаем экземпляр EncryptionKey
            key = EncryptionKey(
                key_id="test_key_1",
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_data=b"test_key_data",
                created_at=datetime.now()
            )
            
            # Проверяем атрибуты
            required_attributes = [
                'key_id',
                'algorithm',
                'key_data',
                'created_at',
                'expires_at',
                'is_active',
                'metadata'
            ]
            
            for attr in required_attributes:
                if hasattr(key, attr):
                    value = getattr(key, attr)
                    self.logger.info(f"✅ Атрибут {attr}: {type(value).__name__} = {value}")
                else:
                    self.logger.error(f"❌ Атрибут {attr} не найден")
                    self.test_results.append((f"Атрибут EncryptionKey.{attr}", False))
                    return False
            
            # Проверяем типы атрибутов
            assert isinstance(key.key_id, str)
            assert isinstance(key.algorithm, EncryptionAlgorithm)
            assert isinstance(key.key_data, bytes)
            assert isinstance(key.created_at, datetime)
            assert key.expires_at is None or isinstance(key.expires_at, datetime)
            assert isinstance(key.is_active, bool)
            assert key.metadata is None or isinstance(key.metadata, dict)
            
            self.logger.info("✅ Все атрибуты EncryptionKey корректны")
            self.test_results.append(("Атрибуты EncryptionKey", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования атрибутов EncryptionKey: {e}")
            self.test_results.append(("Атрибуты EncryptionKey", False))
            return False

    async def test_encrypted_data_attributes(self):
        """Тест атрибутов EncryptedData"""
        self.logger.info("🔍 Тестирование атрибутов EncryptedData...")
        
        try:
            # Создаем экземпляр EncryptedData
            encrypted_data = EncryptedData(
                data=b"encrypted_data",
                key_id="test_key_1",
                algorithm=EncryptionAlgorithm.AES_256_GCM
            )
            
            # Проверяем атрибуты
            required_attributes = [
                'data',
                'key_id',
                'algorithm',
                'iv',
                'tag',
                'metadata',
                'timestamp'
            ]
            
            for attr in required_attributes:
                if hasattr(encrypted_data, attr):
                    value = getattr(encrypted_data, attr)
                    self.logger.info(f"✅ Атрибут {attr}: {type(value).__name__} = {value}")
                else:
                    self.logger.error(f"❌ Атрибут {attr} не найден")
                    self.test_results.append((f"Атрибут EncryptedData.{attr}", False))
                    return False
            
            # Проверяем типы атрибутов
            from datetime import datetime
            assert isinstance(encrypted_data.data, bytes)
            assert isinstance(encrypted_data.key_id, str)
            assert isinstance(encrypted_data.algorithm, EncryptionAlgorithm)
            assert encrypted_data.iv is None or isinstance(encrypted_data.iv, bytes)
            assert encrypted_data.tag is None or isinstance(encrypted_data.tag, bytes)
            assert encrypted_data.metadata is None or isinstance(encrypted_data.metadata, dict)
            assert isinstance(encrypted_data.timestamp, datetime)
            
            self.logger.info("✅ Все атрибуты EncryptedData корректны")
            self.test_results.append(("Атрибуты EncryptedData", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования атрибутов EncryptedData: {e}")
            self.test_results.append(("Атрибуты EncryptedData", False))
            return False

    async def test_enum_attributes(self):
        """Тест атрибутов Enum классов"""
        self.logger.info("🔍 Тестирование атрибутов Enum классов...")
        
        try:
            # Проверяем EncryptionAlgorithm
            assert hasattr(EncryptionAlgorithm, 'AES_256_GCM')
            assert hasattr(EncryptionAlgorithm, 'AES_256_CBC')
            assert hasattr(EncryptionAlgorithm, 'FERNET')
            assert hasattr(EncryptionAlgorithm, 'RSA_OAEP')
            assert hasattr(EncryptionAlgorithm, 'CHACHA20_POLY1305')
            
            # Проверяем KeyDerivation
            assert hasattr(KeyDerivation, 'PBKDF2')
            assert hasattr(KeyDerivation, 'SCRYPT')
            assert hasattr(KeyDerivation, 'ARGON2')
            
            self.logger.info("✅ Все атрибуты Enum классов корректны")
            self.test_results.append(("Атрибуты Enum классов", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования атрибутов Enum классов: {e}")
            self.test_results.append(("Атрибуты Enum классов", False))
            return False

    async def run_all_tests(self):
        """Запуск всех тестов атрибутов"""
        self.logger.info("🚀 ЗАПУСК ТЕСТОВ АТРИБУТОВ КЛАССОВ")
        self.logger.info("============================================================")
        
        results = []
        results.append(await self.test_encryption_manager_attributes())
        results.append(await self.test_encryption_key_attributes())
        results.append(await self.test_encrypted_data_attributes())
        results.append(await self.test_enum_attributes())
        
        self.logger.info("============================================================")
        passed_tests = sum(1 for r in results if r)
        total_tests = len(results)
        
        self.logger.info(f"📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed_tests}/{total_tests} тестов пройдено")
        
        # Детальные результаты
        self.logger.info("📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.test_results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            self.logger.info(f"  {test_name}: {status}")
        
        if all(results):
            self.logger.info("🎉 ВСЕ ТЕСТЫ АТРИБУТОВ ПРОЙДЕНЫ!")
            return True
        else:
            self.logger.error("❌ ЕСТЬ ОШИБКИ В ТЕСТИРОВАНИИ АТРИБУТОВ!")
            return False


if __name__ == "__main__":
    logger.info("✅ Импорт модулей успешен")
    tester = TestEncryptionManagerAttributes()
    asyncio.run(tester.run_all_tests())