#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест доступности методов и классов - encryption_manager.py
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


class TestEncryptionManagerAccessibility:
    """Тест доступности методов и классов"""

    def __init__(self):
        self.logger = logger
        self.manager = None
        self.test_results = []

    async def test_class_instantiation(self):
        """Тест создания экземпляров классов"""
        self.logger.info("🔍 Тестирование создания экземпляров классов...")
        
        try:
            # 1. EncryptionManager
            self.manager = EncryptionManager(self.logger)
            assert self.manager is not None
            self.logger.info("✅ EncryptionManager создан успешно")
            
            # 2. EncryptionAlgorithm (Enum)
            aes_algorithm = EncryptionAlgorithm.AES_256_GCM
            assert aes_algorithm is not None
            self.logger.info("✅ EncryptionAlgorithm создан успешно")
            
            # 3. KeyDerivation (Enum)
            pbkdf2_method = KeyDerivation.PBKDF2
            assert pbkdf2_method is not None
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
            
            self.test_results.append(("Создание экземпляров классов", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания экземпляров: {e}")
            self.test_results.append(("Создание экземпляров классов", False))
            return False

    async def test_public_methods_accessibility(self):
        """Тест доступности public методов"""
        self.logger.info("🔍 Тестирование доступности public методов...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Список public методов
            public_methods = [
                'encrypt_data',
                'decrypt_data', 
                'encrypt_sensitive_field',
                'decrypt_sensitive_field',
                'hash_password',
                'verify_password',
                'encrypt_file',
                'decrypt_file',
                'get_encryption_stats',
                'cleanup_expired_keys',
                'export_key',
                'import_key'
            ]
            
            for method_name in public_methods:
                if hasattr(self.manager, method_name):
                    method = getattr(self.manager, method_name)
                    assert callable(method)
                    self.logger.info(f"✅ Метод {method_name} доступен и вызываем")
                else:
                    self.logger.error(f"❌ Метод {method_name} не найден")
                    self.test_results.append((f"Доступность {method_name}", False))
                    return False
            
            self.test_results.append(("Доступность public методов", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки public методов: {e}")
            self.test_results.append(("Доступность public методов", False))
            return False

    async def test_method_calls_with_correct_parameters(self):
        """Тест вызова методов с корректными параметрами"""
        self.logger.info("🔍 Тестирование вызова методов с корректными параметрами...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Тест encrypt_data
            test_data = {"user": "test", "password": "secret"}
            encrypted = await self.manager.encrypt_data(test_data)
            assert encrypted is not None
            assert hasattr(encrypted, 'data')
            assert hasattr(encrypted, 'key_id')
            assert hasattr(encrypted, 'algorithm')
            self.logger.info("✅ encrypt_data работает корректно")
            
            # Тест decrypt_data
            decrypted = await self.manager.decrypt_data(encrypted)
            assert decrypted == test_data
            self.logger.info("✅ decrypt_data работает корректно")
            
            # Тест hash_password
            password = "test_password"
            salt = b"test_salt"
            hashed, returned_salt = self.manager.hash_password(password, salt)
            assert isinstance(hashed, str)
            assert len(hashed) > 0
            assert isinstance(returned_salt, bytes)
            self.logger.info("✅ hash_password работает корректно")
            
            # Тест verify_password
            is_valid = self.manager.verify_password(password, hashed, returned_salt)
            assert is_valid is True
            self.logger.info("✅ verify_password работает корректно")
            
            # Тест get_encryption_stats
            try:
                stats = self.manager.get_encryption_stats()
                assert isinstance(stats, dict)
                assert "total_keys" in stats
                assert "active_key_id" in stats
                self.logger.info("✅ get_encryption_stats работает корректно")
            except Exception as e:
                self.logger.error(f"❌ Ошибка в get_encryption_stats: {e}")
                raise
            
            self.test_results.append(("Вызов методов с корректными параметрами", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка вызова методов: {e}")
            self.test_results.append(("Вызов методов с корректными параметрами", False))
            return False

    async def test_exception_handling(self):
        """Тест обработки исключений в методах"""
        self.logger.info("🔍 Тестирование обработки исключений...")
        
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
            
            # Тест с некорректным EncryptedData
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
            
            # Тест с некорректным паролем
            try:
                result = self.manager.verify_password("wrong_password", "invalid_hash")
                # verify_password может возвращать False вместо исключения
                if result is False:
                    self.logger.info("✅ Корректно обработано неверный пароль (возврат False)")
                else:
                    self.logger.error("❌ Ожидалось False для неверного пароля")
                    return False
            except Exception:
                self.logger.info("✅ Корректно обработано исключение для неверного пароля")
            
            self.test_results.append(("Обработка исключений", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования исключений: {e}")
            self.test_results.append(("Обработка исключений", False))
            return False

    async def run_all_tests(self):
        """Запуск всех тестов доступности"""
        self.logger.info("🚀 ЗАПУСК ТЕСТОВ ДОСТУПНОСТИ МЕТОДОВ И КЛАССОВ")
        self.logger.info("============================================================")
        
        results = []
        results.append(await self.test_class_instantiation())
        results.append(await self.test_public_methods_accessibility())
        results.append(await self.test_method_calls_with_correct_parameters())
        results.append(await self.test_exception_handling())
        
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
            self.logger.info("🎉 ВСЕ ТЕСТЫ ДОСТУПНОСТИ ПРОЙДЕНЫ!")
            return True
        else:
            self.logger.error("❌ ЕСТЬ ОШИБКИ В ТЕСТИРОВАНИИ ДОСТУПНОСТИ!")
            return False


if __name__ == "__main__":
    logger.info("✅ Импорт модулей успешен")
    tester = TestEncryptionManagerAccessibility()
    asyncio.run(tester.run_all_tests())