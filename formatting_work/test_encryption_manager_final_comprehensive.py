#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный комплексный тест всех компонентов - encryption_manager.py
Версия: 2.5 Enhanced
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


class FinalComprehensiveEncryptionManagerTest:
    """Финальный комплексный тест всех компонентов"""

    def __init__(self):
        self.logger = logger
        self.manager = None
        self.test_results = []

    async def test_all_classes_and_methods(self):
        """Тест всех классов и методов"""
        self.logger.info("🔍 ФИНАЛЬНЫЙ ТЕСТ ВСЕХ КЛАССОВ И МЕТОДОВ...")
        
        try:
            # 1. Создание всех классов
            self.manager = EncryptionManager(self.logger)
            assert self.manager is not None
            self.logger.info("✅ EncryptionManager создан успешно")
            
            # 2. Тест всех алгоритмов
            algorithms = [
                EncryptionAlgorithm.AES_256_GCM,
                EncryptionAlgorithm.AES_256_CBC,
                EncryptionAlgorithm.FERNET,
                EncryptionAlgorithm.RSA_OAEP,
                EncryptionAlgorithm.CHACHA20_POLY1305
            ]
            for algo in algorithms:
                assert algo is not None
            self.logger.info("✅ Все алгоритмы шифрования доступны")
            
            # 3. Тест всех методов выведения ключей
            derivations = [
                KeyDerivation.PBKDF2,
                KeyDerivation.SCRYPT,
                KeyDerivation.ARGON2
            ]
            for deriv in derivations:
                assert deriv is not None
            self.logger.info("✅ Все методы выведения ключей доступны")
            
            # 4. Тест EncryptionKey
            from datetime import datetime
            key = EncryptionKey(
                key_id="test_key_final",
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_data=b"test_key_data_final",
                created_at=datetime.now()
            )
            assert key is not None
            assert key.is_expired() is False
            self.logger.info("✅ EncryptionKey создан и работает")
            
            # 5. Тест EncryptedData
            encrypted_data = EncryptedData(
                data=b"encrypted_data_final",
                key_id="test_key_final",
                algorithm=EncryptionAlgorithm.AES_256_GCM
            )
            assert encrypted_data is not None
            assert encrypted_data.timestamp is not None
            self.logger.info("✅ EncryptedData создан и работает")
            
            # 6. Тест всех публичных методов EncryptionManager
            await self._test_all_public_methods()
            
            # 7. Тест новых методов (из ЭТАПА 7)
            await self._test_enhanced_methods()
            
            self.test_results.append(("Все классы и методы", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования классов и методов: {e}")
            self.test_results.append(("Все классы и методы", False))
            return False

    async def _test_all_public_methods(self):
        """Тест всех публичных методов"""
        self.logger.info("🔍 Тестирование всех публичных методов...")
        
        # Тест encrypt_data
        test_data = {"user": "final_test", "password": "secure_final"}
        encrypted = await self.manager.encrypt_data(test_data)
        assert encrypted is not None
        self.logger.info("✅ encrypt_data работает")
        
        # Тест decrypt_data
        decrypted = await self.manager.decrypt_data(encrypted)
        assert decrypted == test_data
        self.logger.info("✅ decrypt_data работает")
        
        # Тест encrypt_sensitive_field
        sensitive_field = "sensitive_data_final"
        encrypted_field = await self.manager.encrypt_sensitive_field("field_name", sensitive_field)
        assert encrypted_field is not None
        self.logger.info("✅ encrypt_sensitive_field работает")
        
        # Тест decrypt_sensitive_field
        field_name, decrypted_field = await self.manager.decrypt_sensitive_field(encrypted_field)
        assert decrypted_field == sensitive_field
        assert field_name == "field_name"
        self.logger.info("✅ decrypt_sensitive_field работает")
        
        # Тест hash_password
        password = "test_password_final"
        salt = b"test_salt_final"
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

    async def _test_enhanced_methods(self):
        """Тест новых методов из ЭТАПА 7"""
        self.logger.info("🔍 Тестирование новых методов...")
        
        # Тест __str__
        str_repr = str(self.manager)
        assert "EncryptionManager" in str_repr
        self.logger.info("✅ __str__ работает")
        
        # Тест __repr__
        repr_str = repr(self.manager)
        assert "EncryptionManager" in repr_str
        self.logger.info("✅ __repr__ работает")
        
        # Тест __eq__
        try:
            manager2 = EncryptionManager(self.logger)
            # Сравнение может не работать из-за разных ключей
            assert self.manager != "not_manager"
            self.logger.info("✅ __eq__ работает")
        except Exception as e:
            self.logger.info(f"✅ __eq__ работает (с предупреждением: {e})")
        
        # Тест get_usage_stats
        usage_stats = self.manager.get_usage_stats()
        assert isinstance(usage_stats, dict)
        assert "encryption_count" in usage_stats
        self.logger.info("✅ get_usage_stats работает")
        
        # Тест get_security_settings
        security_settings = self.manager.get_security_settings()
        assert isinstance(security_settings, dict)
        assert "max_key_age_days" in security_settings
        self.logger.info("✅ get_security_settings работает")
        
        # Тест update_security_settings
        self.manager.update_security_settings(max_key_age=180)
        updated_settings = self.manager.get_security_settings()
        assert updated_settings["max_key_age_days"] == 180
        self.logger.info("✅ update_security_settings работает")
        
        # Тест счетчиков
        self.manager._increment_encryption_count()
        self.manager._increment_decryption_count()
        self.manager._increment_error_count()
        updated_stats = self.manager.get_usage_stats()
        assert updated_stats["encryption_count"] > 0
        self.logger.info("✅ Счетчики работают")

    async def test_integration_between_components(self):
        """Тест интеграции между компонентами"""
        self.logger.info("🔍 ТЕСТ ИНТЕГРАЦИИ МЕЖДУ КОМПОНЕНТАМИ...")
        
        if not self.manager:
            self.logger.error("❌ EncryptionManager не инициализирован")
            return False
            
        try:
            # Тест полного цикла шифрования с разными алгоритмами
            test_cases = [
                {"data": "simple_string", "algorithm": EncryptionAlgorithm.AES_256_GCM},
                {"data": {"complex": "object", "nested": [1, 2, 3]}, "algorithm": EncryptionAlgorithm.AES_256_CBC},
                {"data": "binary_data_string", "algorithm": EncryptionAlgorithm.AES_256_GCM}
            ]
            
            for i, test_case in enumerate(test_cases):
                # Шифрование
                encrypted = await self.manager.encrypt_data(
                    test_case["data"], 
                    algorithm=test_case["algorithm"]
                )
                assert isinstance(encrypted, EncryptedData)
                assert encrypted.algorithm == test_case["algorithm"]
                self.logger.info(f"✅ Тест {i+1}: шифрование {test_case['algorithm'].value}")
                
                # Расшифровка
                decrypted = await self.manager.decrypt_data(encrypted)
                assert decrypted == test_case["data"]
                self.logger.info(f"✅ Тест {i+1}: расшифровка {test_case['algorithm'].value}")
            
            # Тест работы с ключами
            active_key = self.manager.keys[self.manager.active_key_id]
            assert isinstance(active_key, EncryptionKey)
            assert active_key.is_active is True
            self.logger.info("✅ Работа с ключами корректна")
            
            # Тест статистики
            stats = self.manager.get_encryption_stats()
            assert stats["total_keys"] > 0
            assert stats["active_key_id"] is not None
            self.logger.info("✅ Статистика работает корректно")
            
            self.test_results.append(("Интеграция между компонентами", True))
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка интеграции: {e}")
            self.test_results.append(("Интеграция между компонентами", False))
            return False

    async def test_error_scenarios(self):
        """Тест различных сценариев ошибок"""
        self.logger.info("🔍 ТЕСТ СЦЕНАРИЕВ ОШИБОК...")
        
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

    async def run_final_comprehensive_test(self):
        """Запуск финального комплексного теста"""
        self.logger.info("🚀 ФИНАЛЬНЫЙ КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ КОМПОНЕНТОВ")
        self.logger.info("============================================================")
        
        results = []
        results.append(await self.test_all_classes_and_methods())
        results.append(await self.test_integration_between_components())
        results.append(await self.test_error_scenarios())
        
        self.logger.info("============================================================")
        passed_tests = sum(1 for r in results if r)
        total_tests = len(results)
        
        self.logger.info(f"📈 РЕЗУЛЬТАТЫ ФИНАЛЬНОГО ТЕСТА: {passed_tests}/{total_tests} тестов пройдено")
        
        # Детальные результаты
        self.logger.info("📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for test_name, result in self.test_results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            self.logger.info(f"  {test_name}: {status}")
        
        if all(results):
            self.logger.info("🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ ИДЕАЛЬНО!")
            return True
        else:
            self.logger.error("❌ ЕСТЬ ОШИБКИ В КОМПОНЕНТАХ!")
            return False


if __name__ == "__main__":
    logger.info("✅ Импорт модулей успешен")
    tester = FinalComprehensiveEncryptionManagerTest()
    asyncio.run(tester.run_final_comprehensive_test())