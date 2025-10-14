#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест всех компонентов - encryption_manager.py
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


class ComprehensiveEncryptionManagerTest:
    """Комплексный тест всех компонентов"""

    def __init__(self):
        self.logger = logger
        self.manager = None
        self.test_results = []

    async def test_all_classes_instantiation(self):
        """Тест создания всех классов"""
        self.logger.info("🔍 Тестирование создания всех классов...")
        
        try:
            # 1. EncryptionManager
            self.manager = EncryptionManager(self.logger)
            assert self.manager is not None
            self.logger.info("✅ EncryptionManager создан успешно")
            
            # 2. EncryptionAlgorithm (Enum)
            algorithms = [
                EncryptionAlgorithm.AES_256_GCM,
                EncryptionAlgorithm.AES_256_CBC,
                EncryptionAlgorithm.FERNET,
                EncryptionAlgorithm.RSA_OAEP,
                EncryptionAlgorithm.CHACHA20_POLY1305
            ]
            for algo in algorithms:
                assert algo is not None
            self.logger.info("✅ EncryptionAlgorithm создан успешно")
            
            # 3. KeyDerivation (Enum)
            derivations = [
                KeyDerivation.PBKDF2,
                KeyDerivation.SCRYPT,
                KeyDerivation.ARGON2
            ]
            for deriv in derivations:
                assert deriv is not None
            self.logger.info("✅ KeyDerivation создан успешно")
            
            # 4. EncryptionKey (Dataclass)
            from datetime import datetime
            key = EncryptionKey(
                key_id="test_key_1",
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_data=b"test_key_data",
                created_at=datetime.now()
            )
            assert key is not None
            self.logger.info("✅ EncryptionKey создан успешно")
            
            # 5. EncryptedData (Dataclass)
            encrypted_data = EncryptedData(
                data=b"encrypted_data",
                key_id="test_key_1",
                algorithm=EncryptionAlgorithm.AES_256_GCM
            )
            assert encrypted_data is not None
            self.logger.info("✅ EncryptedData создан успешно")
            
            self.test_results.append(("Создание всех классов", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания классов: {e}")
            self.test_results.append(("Создание всех классов", False))
            return False

    async def test_all_public_methods(self):
        """Тест всех публичных методов"""
        self.logger.info("🔍 Тестирование всех публичных методов...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Тест encrypt_data
            test_data = {"user": "test", "password": "secret"}
            encrypted = await self.manager.encrypt_data(test_data)
            assert encrypted is not None
            self.logger.info("✅ encrypt_data работает")
            
            # Тест decrypt_data
            decrypted = await self.manager.decrypt_data(encrypted)
            assert decrypted == test_data
            self.logger.info("✅ decrypt_data работает")
            
            # Тест encrypt_sensitive_field
            sensitive_field = "sensitive_data"
            encrypted_field = await self.manager.encrypt_sensitive_field("field_name", sensitive_field)
            assert encrypted_field is not None
            self.logger.info("✅ encrypt_sensitive_field работает")
            
            # Тест decrypt_sensitive_field
            try:
                field_name, decrypted_field = await self.manager.decrypt_sensitive_field(encrypted_field)
                assert decrypted_field == sensitive_field
                assert field_name == "field_name"
                self.logger.info("✅ decrypt_sensitive_field работает")
            except Exception as e:
                self.logger.error(f"❌ Ошибка в decrypt_sensitive_field: {e}")
                raise
            
            # Тест hash_password
            password = "test_password"
            salt = b"test_salt"
            hashed, returned_salt = self.manager.hash_password(password, salt)
            assert isinstance(hashed, str)
            assert isinstance(returned_salt, bytes)
            self.logger.info("✅ hash_password работает")
            
            # Тест verify_password
            is_valid = self.manager.verify_password(password, hashed, returned_salt)
            assert is_valid is True
            self.logger.info("✅ verify_password работает")
            
            # Тест get_encryption_stats
            stats = self.manager.get_encryption_stats()
            assert isinstance(stats, dict)
            assert "total_keys" in stats
            self.logger.info("✅ get_encryption_stats работает")
            
            # Тест cleanup_expired_keys
            cleaned = await self.manager.cleanup_expired_keys()
            assert isinstance(cleaned, int)
            self.logger.info("✅ cleanup_expired_keys работает")
            
            self.test_results.append(("Все публичные методы", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования публичных методов: {e}")
            self.test_results.append(("Все публичные методы", False))
            return False

    async def test_integration_between_components(self):
        """Тест интеграции между компонентами"""
        self.logger.info("🔍 Тестирование интеграции между компонентами...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Тест полного цикла шифрования
            original_data = {
                "user_id": "12345",
                "password": "secure_password",
                "email": "user@example.com",
                "sensitive_info": "confidential_data"
            }
            
            # Шифрование
            encrypted = await self.manager.encrypt_data(original_data)
            assert isinstance(encrypted, EncryptedData)
            assert encrypted.key_id in self.manager.keys
            self.logger.info("✅ Интеграция: шифрование работает")
            
            # Расшифровка
            decrypted = await self.manager.decrypt_data(encrypted)
            assert decrypted == original_data
            self.logger.info("✅ Интеграция: расшифровка работает")
            
            # Тест работы с ключами
            key = self.manager.keys[encrypted.key_id]
            assert isinstance(key, EncryptionKey)
            assert key.algorithm == encrypted.algorithm
            self.logger.info("✅ Интеграция: работа с ключами работает")
            
            # Тест статистики
            stats = self.manager.get_encryption_stats()
            assert stats["total_keys"] > 0
            assert stats["active_key_id"] == encrypted.key_id
            self.logger.info("✅ Интеграция: статистика работает")
            
            self.test_results.append(("Интеграция между компонентами", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка интеграции: {e}")
            self.test_results.append(("Интеграция между компонентами", False))
            return False

    async def test_error_scenarios(self):
        """Тест различных сценариев ошибок"""
        self.logger.info("🔍 Тестирование сценариев ошибок...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Тест с некорректными данными
            try:
                await self.manager.encrypt_data(None)
                self.logger.error("❌ Ожидалось исключение для None")
                return False
            except Exception:
                self.logger.info("✅ Корректно обработано исключение для None")
            
            # Тест с несуществующим ключом
            try:
                invalid_encrypted = EncryptedData(
                    data=b"invalid",
                    key_id="nonexistent_key",
                    algorithm=EncryptionAlgorithm.AES_256_GCM
                )
                await self.manager.decrypt_data(invalid_encrypted)
                self.logger.error("❌ Ожидалось исключение для несуществующего ключа")
                return False
            except Exception:
                self.logger.info("✅ Корректно обработано исключение для несуществующего ключа")
            
            # Тест с неверным паролем
            try:
                result = self.manager.verify_password("wrong_password", "invalid_hash", b"invalid_salt")
                if result is False:
                    self.logger.info("✅ Корректно обработано неверный пароль (возврат False)")
                else:
                    self.logger.error("❌ Ожидалось False для неверного пароля")
                    return False
            except Exception:
                self.logger.info("✅ Корректно обработано исключение для неверного пароля")
            
            self.test_results.append(("Сценарии ошибок", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования сценариев ошибок: {e}")
            self.test_results.append(("Сценарии ошибок", False))
            return False

    async def run_comprehensive_test(self):
        """Запуск комплексного теста"""
        self.logger.info("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА ВСЕХ КОМПОНЕНТОВ")
        self.logger.info("============================================================")
        
        results = []
        results.append(await self.test_all_classes_instantiation())
        results.append(await self.test_all_public_methods())
        results.append(await self.test_integration_between_components())
        results.append(await self.test_error_scenarios())
        
        self.logger.info("============================================================")
        passed_tests = sum(1 for r in results if r)
        total_tests = len(results)
        
        self.logger.info(f"📈 РЕЗУЛЬТАТЫ КОМПЛЕКСНОГО ТЕСТА: {passed_tests}/{total_tests} тестов пройдено")
        
        # Детальные результаты
        self.logger.info("📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.test_results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            self.logger.info(f"  {test_name}: {status}")
        
        if all(results):
            self.logger.info("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ КОРРЕКТНО!")
            return True
        else:
            self.logger.error("❌ ЕСТЬ ОШИБКИ В КОМПОНЕНТАХ!")
            return False


if __name__ == "__main__":
    logger.info("✅ Импорт модулей успешен")
    tester = ComprehensiveEncryptionManagerTest()
    asyncio.run(tester.run_comprehensive_test())