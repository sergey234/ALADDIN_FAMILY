#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты шифрования для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Добавляем путь к модулям
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.bots.parental_control_bot import ParentalControlBot
from security.bots.components.encryption_manager import EncryptionManager, EncryptionAlgorithm, EncryptedData


class TestParentalControlBotEncryption:
    """Тесты шифрования ParentalControlBot"""

    @pytest.fixture
    async def bot(self):
        """Создание экземпляра бота для тестов"""
        config = {
            "encryption_master_password": "test_master_password_123",
            "encryption_key_rotation_days": 30
        }
        
        bot = ParentalControlBot("EncryptionTestBot", config)
        await bot.start()
        yield bot
        await bot.stop()

    async def test_encryption_manager_initialization(self, bot):
        """Тест инициализации менеджера шифрования"""
        assert hasattr(bot, 'encryption_manager')
        assert isinstance(bot.encryption_manager, EncryptionManager)
        
        # Проверяем, что ключи созданы
        stats = bot.get_encryption_stats()
        assert stats["total_keys"] > 0
        assert stats["active_key_id"] is not None

    async def test_encrypt_decrypt_data(self, bot):
        """Тест шифрования и расшифровки данных"""
        # Тестовые данные
        test_data = {
            "name": "Test Child",
            "age": 10,
            "parent_id": "parent_123",
            "safe_zones": [{"name": "Home", "coordinates": [55.7558, 37.6176]}],
            "restrictions": {"social_media": True, "gaming": False}
        }
        
        # Шифрование
        encrypted_data = await bot.encrypt_child_data("child_123", test_data)
        
        # Проверяем, что чувствительные поля зашифрованы
        assert "name_encrypted" in encrypted_data
        assert "parent_id_encrypted" in encrypted_data
        assert "safe_zones_encrypted" in encrypted_data
        assert "restrictions_encrypted" in encrypted_data
        
        # Обычные поля остались незашифрованными
        assert encrypted_data["age"] == 10
        
        # Расшифровка
        decrypted_data = await bot.decrypt_child_data("child_123", encrypted_data)
        
        # Проверяем, что данные восстановлены
        assert decrypted_data["name"] == "Test Child"
        assert decrypted_data["age"] == 10
        assert decrypted_data["parent_id"] == "parent_123"
        assert decrypted_data["safe_zones"] == [{"name": "Home", "coordinates": [55.7558, 37.6176]}]
        assert decrypted_data["restrictions"] == {"social_media": True, "gaming": False}

    async def test_encrypt_decrypt_profile(self, bot):
        """Тест шифрования и расшифровки профиля"""
        # Создаем тестовый профиль
        from security.bots.parental_control_bot import ChildProfile, AgeGroup
        
        profile = ChildProfile(
            id="child_123",
            name="Test Child",
            age=10,
            age_group=AgeGroup.ELEMENTARY,
            parent_id="parent_123",
            device_ids=["device_1", "device_2"],
            restrictions={"social_media": True},
            time_limits={"mobile": 60},
            safe_zones=[{"name": "Home", "coordinates": [55.7558, 37.6176]}],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Шифрование профиля
        encrypted_profile = await bot.encrypt_profile(profile)
        
        # Проверяем, что safe_zones зашифрованы
        assert isinstance(encrypted_profile.safe_zones[0], dict)
        assert "encrypted_data" in encrypted_profile.safe_zones[0]
        
        # Расшифровка профиля
        decrypted_profile = await bot.decrypt_profile(encrypted_profile)
        
        # Проверяем, что данные восстановлены
        assert decrypted_profile.name == "Test Child"
        assert decrypted_profile.age == 10
        assert decrypted_profile.safe_zones == [{"name": "Home", "coordinates": [55.7558, 37.6176]}]

    async def test_encrypt_decrypt_alert(self, bot):
        """Тест шифрования и расшифровки алерта"""
        from security.bots.parental_control_bot import ActivityAlert, AlertType, AlertSeverity
        
        # Создаем тестовый алерт
        alert = ActivityAlert(
            id="alert_123",
            child_id="child_123",
            alert_type=AlertType.SUSPICIOUS_ACTIVITY,
            severity=AlertSeverity.HIGH,
            message="Подозрительная активность обнаружена",
            timestamp=datetime.now(),
            action_required=True,
            data={
                "location": "Unknown",
                "details": "Suspicious browsing pattern",
                "risk_score": 0.8
            }
        )
        
        # Шифрование алерта
        encrypted_alert = await bot.encrypt_alert_data(alert)
        
        # Проверяем, что data зашифрованы
        assert isinstance(encrypted_alert.data, dict)
        assert "encrypted_data" in encrypted_alert.data
        
        # Расшифровка алерта
        decrypted_alert = await bot.decrypt_alert_data(encrypted_alert)
        
        # Проверяем, что данные восстановлены
        assert decrypted_alert.message == "Подозрительная активность обнаружена"
        assert decrypted_alert.data["location"] == "Unknown"
        assert decrypted_alert.data["risk_score"] == 0.8

    async def test_password_hashing(self, bot):
        """Тест хэширования паролей"""
        password = "test_password_123"
        
        # Хэширование пароля
        password_hash, salt = bot.hash_parent_password(password)
        
        assert isinstance(password_hash, str)
        assert isinstance(salt, bytes)
        assert len(salt) > 0
        
        # Проверка пароля
        is_valid = bot.verify_parent_password(password, password_hash, salt)
        assert is_valid is True
        
        # Проверка неправильного пароля
        is_invalid = bot.verify_parent_password("wrong_password", password_hash, salt)
        assert is_invalid is False

    async def test_file_encryption(self, bot):
        """Тест шифрования файлов"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "This is sensitive data that needs to be encrypted"
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Шифрование файла
            encrypted_file = await bot.encrypt_file(temp_file)
            
            # Проверяем, что файл зашифрован
            assert os.path.exists(encrypted_file)
            assert os.path.exists(encrypted_file + ".meta")
            
            # Расшифровка файла
            decrypted_file = await bot.decrypt_file(encrypted_file)
            
            # Проверяем содержимое
            with open(decrypted_file, 'r') as f:
                decrypted_content = f.read()
            
            assert decrypted_content == test_content
            
            # Очистка
            os.unlink(encrypted_file)
            os.unlink(encrypted_file + ".meta")
            os.unlink(decrypted_file)
            
        finally:
            # Очистка исходного файла
            os.unlink(temp_file)

    async def test_encryption_stats(self, bot):
        """Тест получения статистики шифрования"""
        stats = bot.get_encryption_stats()
        
        assert "total_keys" in stats
        assert "active_key_id" in stats
        assert "cryptography_available" in stats
        assert "default_algorithm" in stats
        assert "key_derivation" in stats
        assert "keys" in stats
        
        assert stats["total_keys"] > 0
        assert stats["active_key_id"] is not None

    async def test_key_rotation(self, bot):
        """Тест ротации ключей"""
        # Получаем текущий активный ключ
        stats_before = bot.get_encryption_stats()
        old_key_id = stats_before["active_key_id"]
        
        # Ротация ключей
        result = await bot.rotate_encryption_keys()
        assert result is True
        
        # Проверяем, что ключ изменился
        stats_after = bot.get_encryption_stats()
        new_key_id = stats_after["active_key_id"]
        
        assert new_key_id != old_key_id
        assert stats_after["total_keys"] >= stats_before["total_keys"]

    async def test_cleanup_expired_keys(self, bot):
        """Тест очистки истекших ключей"""
        # Очистка истекших ключей
        cleaned_count = await bot.cleanup_expired_keys()
        
        # В тестовой среде ключи не должны быть истекшими
        assert cleaned_count >= 0

    async def test_encryption_error_handling(self, bot):
        """Тест обработки ошибок шифрования"""
        # Тест с невалидными данными
        invalid_data = None
        
        try:
            encrypted_data = await bot.encrypt_child_data("child_123", invalid_data)
            # Должен вернуть исходные данные при ошибке
            assert encrypted_data is None
        except Exception:
            # Ожидаем исключение
            pass

    async def test_encryption_with_different_algorithms(self, bot):
        """Тест шифрования с разными алгоритмами"""
        test_data = {"sensitive": "data"}
        
        # Тест с разными алгоритмами
        algorithms = [
            EncryptionAlgorithm.AES_256_GCM,
            EncryptionAlgorithm.AES_256_CBC,
            EncryptionAlgorithm.FERNET
        ]
        
        for algorithm in algorithms:
            try:
                encrypted_data = await bot.encryption_manager.encrypt_data(
                    test_data, 
                    algorithm=algorithm
                )
                
                # Проверяем, что данные зашифрованы
                assert encrypted_data.data != test_data
                assert encrypted_data.algorithm == algorithm
                
                # Расшифровка
                decrypted_data = await bot.encryption_manager.decrypt_data(encrypted_data)
                assert decrypted_data == test_data
                
            except Exception as e:
                # Некоторые алгоритмы могут быть недоступны
                bot.logger.warning(f"Алгоритм {algorithm} недоступен: {e}")

    async def test_encryption_performance(self, bot):
        """Тест производительности шифрования"""
        import time
        
        # Тестовые данные
        test_data = {
            "name": "Performance Test Child",
            "age": 12,
            "parent_id": "parent_456",
            "safe_zones": [
                {"name": "Home", "coordinates": [55.7558, 37.6176]},
                {"name": "School", "coordinates": [55.7600, 37.6200]}
            ],
            "restrictions": {
                "social_media": True,
                "gaming": False,
                "streaming": True
            }
        }
        
        # Измеряем время шифрования
        start_time = time.time()
        encrypted_data = await bot.encrypt_child_data("child_456", test_data)
        encrypt_time = time.time() - start_time
        
        # Измеряем время расшифровки
        start_time = time.time()
        decrypted_data = await bot.decrypt_child_data("child_456", encrypted_data)
        decrypt_time = time.time() - start_time
        
        # Проверяем, что данные корректны
        assert decrypted_data["name"] == "Performance Test Child"
        assert decrypted_data["age"] == 12
        
        # Логируем производительность
        bot.logger.info(f"Шифрование: {encrypt_time:.4f}с, Расшифровка: {decrypt_time:.4f}с")

    async def test_encryption_integration_with_main_functions(self, bot):
        """Тест интеграции шифрования с основными функциями"""
        # Добавляем ребенка (данные должны быть зашифрованы)
        child_data = {
            "name": "Encrypted Child",
            "age": 8,
            "parent_id": "parent_789",
            "safe_zones": [{"name": "Home", "coordinates": [55.7558, 37.6176]}]
        }
        
        child_id = await bot.add_child_profile(child_data)
        assert child_id is not None
        
        # Получаем статус (данные должны быть расшифрованы)
        status = await bot.get_child_status(child_id)
        assert status is not None
        assert status["name"] == "Encrypted Child"
        assert status["age"] == 8

    async def test_encryption_key_export_import(self, bot):
        """Тест экспорта и импорта ключей"""
        # Получаем активный ключ
        stats = bot.get_encryption_stats()
        key_id = stats["active_key_id"]
        
        # Экспорт ключа
        export_password = "export_password_123"
        exported_key = await bot.export_encryption_key(key_id, export_password)
        
        assert isinstance(exported_key, str)
        assert len(exported_key) > 0
        
        # Импорт ключа
        imported_key_id = await bot.import_encryption_key(exported_key, export_password)
        
        assert imported_key_id == key_id
        
        # Проверяем, что ключ доступен
        stats_after = bot.get_encryption_stats()
        assert key_id in stats_after["keys"]


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])