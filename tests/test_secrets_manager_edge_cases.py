#!/usr/bin/env python3
"""
Тесты для edge cases SecretsManager
"""

import unittest
import tempfile
import shutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from security.secrets_manager import (
    SecretsManager, SecretType, SecretStatus, SecretMetadata,
    HashiCorpVaultProvider, AWSSecretsManagerProvider
)
from security.secrets_api import SecretsAPI


class TestSecretsManagerEdgeCases(unittest.TestCase):
    """Тесты для edge cases SecretsManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "storage_path": self.temp_dir,
            "auto_rotation": False,
            "external_providers": {}
        }
        self.secrets_manager = SecretsManager(self.config)
        self.secrets_manager.initialize()
    
    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'secrets_manager'):
            self.secrets_manager.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_concurrent_access(self):
        """Тест одновременного доступа к секретам"""
        # Создание секрета
        secret_id = self.secrets_manager.store_secret(
            name="concurrent_test",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        results = []
        errors = []
        
        def access_secret():
            try:
                for _ in range(10):
                    value = self.secrets_manager.get_secret(secret_id)
                    results.append(value)
                    time.sleep(0.001)  # Небольшая задержка
            except Exception as e:
                errors.append(e)
        
        # Запуск нескольких потоков
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=access_secret)
            threads.append(thread)
            thread.start()
        
        # Ожидание завершения
        for thread in threads:
            thread.join()
        
        # Проверка результатов
        self.assertEqual(len(errors), 0, f"Ошибки при concurrent access: {errors}")
        self.assertEqual(len(results), 50)  # 5 потоков * 10 обращений
        self.assertTrue(all(r == "test_value" for r in results))
    
    def test_concurrent_rotation(self):
        """Тест одновременной ротации секретов"""
        # Создание секрета
        secret_id = self.secrets_manager.store_secret(
            name="rotation_test",
            value="original_value",
            secret_type=SecretType.PASSWORD
        )
        
        results = []
        errors = []
        
        def rotate_secret():
            try:
                success = self.secrets_manager.rotate_secret(secret_id, "new_value")
                results.append(success)
            except Exception as e:
                errors.append(e)
        
        # Запуск нескольких потоков ротации
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=rotate_secret)
            threads.append(thread)
            thread.start()
        
        # Ожидание завершения
        for thread in threads:
            thread.join()
        
        # Проверка результатов
        self.assertEqual(len(errors), 0, f"Ошибки при concurrent rotation: {errors}")
        # Только одна ротация должна быть успешной
        self.assertEqual(sum(results), 1)
        
        # Проверка финального значения
        final_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(final_value, "new_value")
    
    def test_large_secret_value(self):
        """Тест работы с большими значениями секретов"""
        # Создание большого секрета (1MB)
        large_value = "x" * (1024 * 1024)  # 1MB
        
        secret_id = self.secrets_manager.store_secret(
            name="large_secret",
            value=large_value,
            secret_type=SecretType.CUSTOM
        )
        
        # Получение секрета
        retrieved_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(retrieved_value, large_value)
        self.assertEqual(len(retrieved_value), 1024 * 1024)
    
    def test_special_characters_in_secret(self):
        """Тест работы с специальными символами"""
        special_values = [
            "password with spaces",
            "password\nwith\nnewlines",
            "password\twith\ttabs",
            "password with unicode: 中文, русский, العربية",
            "password with symbols: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "password with null: \x00\x01\x02",
            "password with quotes: \"'`",
            "password with backslashes: \\\\\\",
        ]
        
        for i, special_value in enumerate(special_values):
            secret_id = self.secrets_manager.store_secret(
                name=f"special_secret_{i}",
                value=special_value,
                secret_type=SecretType.PASSWORD
            )
            
            retrieved_value = self.secrets_manager.get_secret(secret_id)
            self.assertEqual(retrieved_value, special_value)
    
    def test_empty_and_none_values(self):
        """Тест работы с пустыми и None значениями"""
        # Пустая строка
        secret_id = self.secrets_manager.store_secret(
            name="empty_secret",
            value="",
            secret_type=SecretType.CUSTOM
        )
        
        retrieved_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(retrieved_value, "")
        
        # None значение (должно вызывать ошибку)
        with self.assertRaises(Exception):
            self.secrets_manager.store_secret(
                name="none_secret",
                value=None,
                secret_type=SecretType.CUSTOM
            )
    
    def test_very_long_secret_name(self):
        """Тест работы с очень длинными именами секретов"""
        long_name = "a" * 1000  # 1000 символов
        
        secret_id = self.secrets_manager.store_secret(
            name=long_name,
            value="test_value",
            secret_type=SecretType.CUSTOM
        )
        
        # Получение по имени
        retrieved_value = self.secrets_manager.get_secret_by_name(long_name)
        self.assertEqual(retrieved_value, "test_value")
    
    def test_duplicate_secret_names(self):
        """Тест работы с дублирующимися именами секретов"""
        # Создание первого секрета
        secret_id1 = self.secrets_manager.store_secret(
            name="duplicate_name",
            value="value1",
            secret_type=SecretType.PASSWORD
        )
        
        # Создание второго секрета с тем же именем
        secret_id2 = self.secrets_manager.store_secret(
            name="duplicate_name",
            value="value2",
            secret_type=SecretType.PASSWORD
        )
        
        # Оба секрета должны существовать
        self.assertNotEqual(secret_id1, secret_id2)
        
        # Получение по имени должно возвращать последний созданный
        retrieved_value = self.secrets_manager.get_secret_by_name("duplicate_name")
        self.assertEqual(retrieved_value, "value2")
    
    def test_rapid_rotation(self):
        """Тест быстрой ротации секретов"""
        secret_id = self.secrets_manager.store_secret(
            name="rapid_rotation",
            value="original",
            secret_type=SecretType.PASSWORD
        )
        
        # Быстрая ротация
        for i in range(10):
            new_value = f"value_{i}"
            success = self.secrets_manager.rotate_secret(secret_id, new_value)
            self.assertTrue(success)
            
            # Проверка значения
            retrieved_value = self.secrets_manager.get_secret(secret_id)
            self.assertEqual(retrieved_value, new_value)
        
        # Проверка версии
        metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(metadata.version, 11)  # 1 исходная + 10 ротаций
    
    def test_corrupted_storage(self):
        """Тест восстановления после повреждения хранилища"""
        # Создание секрета
        secret_id = self.secrets_manager.store_secret(
            name="corruption_test",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Повреждение файла секретов
        secrets_file = self.secrets_manager.storage_path / "secrets.json"
        with open(secrets_file, 'w') as f:
            f.write("corrupted json content")
        
        # Создание нового менеджера (должен восстановиться)
        new_manager = SecretsManager(self.config)
        new_manager.initialize()
        
        # Секрет должен быть недоступен
        retrieved_value = new_manager.get_secret(secret_id)
        self.assertIsNone(retrieved_value)
        
        new_manager.stop()
    
    def test_missing_metadata_file(self):
        """Тест работы при отсутствии файла метаданных"""
        # Создание секрета
        secret_id = self.secrets_manager.store_secret(
            name="metadata_test",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Удаление файла метаданных
        metadata_file = self.secrets_manager.storage_path / "metadata.json"
        metadata_file.unlink()
        
        # Создание нового менеджера
        new_manager = SecretsManager(self.config)
        new_manager.initialize()
        
        # Секрет должен быть недоступен
        retrieved_value = new_manager.get_secret(secret_id)
        self.assertIsNone(retrieved_value)
        
        new_manager.stop()
    
    def test_encryption_key_rotation(self):
        """Тест ротации ключа шифрования"""
        # Создание секрета
        secret_id = self.secrets_manager.store_secret(
            name="encryption_test",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Сохранение старого ключа
        old_key = self.secrets_manager.encryption_key
        
        # Генерация нового ключа
        new_key = self.secrets_manager._generate_or_load_encryption_key()
        
        # Новый ключ должен отличаться от старого
        self.assertNotEqual(old_key, new_key)
        
        # Секрет должен быть недоступен с новым ключом
        with self.assertRaises(Exception):
            self.secrets_manager.get_secret(secret_id)
    
    def test_memory_usage(self):
        """Тест использования памяти при большом количестве секретов"""
        # Создание большого количества секретов
        secret_ids = []
        for i in range(1000):
            secret_id = self.secrets_manager.store_secret(
                name=f"memory_test_{i}",
                value=f"value_{i}",
                secret_type=SecretType.PASSWORD
            )
            secret_ids.append(secret_id)
        
        # Проверка, что все секреты доступны
        for i, secret_id in enumerate(secret_ids):
            value = self.secrets_manager.get_secret(secret_id)
            self.assertEqual(value, f"value_{i}")
        
        # Проверка метрик
        metrics = self.secrets_manager.get_metrics()
        self.assertEqual(metrics["secrets_count"], 1000)
    
    def test_expired_secret_cleanup(self):
        """Тест очистки истекших секретов"""
        # Создание истекшего секрета
        expired_time = datetime.now() - timedelta(days=1)
        secret_id = self.secrets_manager.store_secret(
            name="expired_secret",
            value="expired_value",
            secret_type=SecretType.PASSWORD,
            expires_at=expired_time
        )
        
        # Секрет должен быть недоступен
        retrieved_value = self.secrets_manager.get_secret(secret_id)
        self.assertIsNone(retrieved_value)
        
        # Статус должен быть EXPIRED
        metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(metadata.status, SecretStatus.EXPIRED)
    
    def test_metadata_serialization_edge_cases(self):
        """Тест сериализации метаданных с edge cases"""
        # Создание метаданных с None значениями
        metadata = SecretMetadata(
            secret_id="test_id",
            name="test_name",
            secret_type=SecretType.PASSWORD,
            created_at=datetime.now(),
            expires_at=None,
            tags=None,
            description=None,
            owner=None
        )
        
        # Сериализация и десериализация
        data = metadata.to_dict()
        restored_metadata = SecretMetadata.from_dict(data)
        
        # Проверка восстановления
        self.assertEqual(metadata.secret_id, restored_metadata.secret_id)
        self.assertEqual(metadata.name, restored_metadata.name)
        self.assertEqual(metadata.secret_type, restored_metadata.secret_type)
        self.assertIsNone(restored_metadata.expires_at)
        self.assertEqual(restored_metadata.tags, {})
        self.assertIsNone(restored_metadata.description)
        self.assertIsNone(restored_metadata.owner)


class TestSecretsAPIEdgeCases(unittest.TestCase):
    """Тесты для edge cases SecretsAPI"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "storage_path": self.temp_dir,
            "auto_rotation": False
        }
        self.secrets_manager = SecretsManager(self.config)
        self.secrets_manager.initialize()
        self.api = SecretsAPI(self.secrets_manager)
        self.api.initialize()
    
    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'secrets_manager'):
            self.secrets_manager.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_secret_types(self):
        """Тест работы с недопустимыми типами секретов"""
        result = self.api.create_secret(
            name="invalid_type",
            value="test_value",
            secret_type="invalid_type"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("Неизвестный тип секрета", result["error"])
    
    def test_malformed_requests(self):
        """Тест работы с некорректными запросами"""
        # Пустое имя
        result = self.api.create_secret(
            name="",
            value="test_value",
            secret_type="password"
        )
        self.assertFalse(result["success"])
        
        # None имя
        result = self.api.create_secret(
            name=None,
            value="test_value",
            secret_type="password"
        )
        self.assertFalse(result["success"])
        
        # Пустое значение
        result = self.api.create_secret(
            name="test_name",
            value="",
            secret_type="password"
        )
        self.assertFalse(result["success"])
    
    def test_nonexistent_secret_operations(self):
        """Тест операций с несуществующими секретами"""
        # Получение несуществующего секрета
        result = self.api.get_secret("nonexistent_id")
        self.assertFalse(result["success"])
        
        # Обновление несуществующего секрета
        result = self.api.update_secret("nonexistent_id", new_value="new_value")
        self.assertFalse(result["success"])
        
        # Удаление несуществующего секрета
        result = self.api.delete_secret("nonexistent_id")
        self.assertFalse(result["success"])
        
        # Ротация несуществующего секрета
        result = self.api.rotate_secret("nonexistent_id")
        self.assertFalse(result["success"])
    
    def test_bulk_operations_with_errors(self):
        """Тест массовых операций с ошибками"""
        # Создание секретов с ошибками
        secrets_data = [
            {"name": "valid_secret", "value": "valid_value", "secret_type": "password"},
            {"name": "", "value": "invalid_value", "secret_type": "password"},  # Ошибка
            {"name": "another_valid", "value": "another_value", "secret_type": "password"},
        ]
        
        result = self.api.bulk_create_secrets(secrets_data)
        self.assertTrue(result["success"])
        self.assertEqual(result["success_count"], 2)
        self.assertEqual(result["error_count"], 1)
    
    def test_search_with_special_characters(self):
        """Тест поиска с специальными символами"""
        # Создание секрета с специальными символами
        self.api.create_secret(
            name="special_search",
            value="test_value",
            secret_type="password",
            description="Секрет с специальными символами: !@#$%^&*()"
        )
        
        # Поиск с регулярными выражениями
        result = self.api.search_secrets("!@#")
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        
        # Поиск с SQL injection попыткой
        result = self.api.search_secrets("'; DROP TABLE secrets; --")
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 0)
    
    def test_pagination_edge_cases(self):
        """Тест пагинации с edge cases"""
        # Создание секретов
        for i in range(5):
            self.api.create_secret(
                name=f"page_test_{i}",
                value=f"value_{i}",
                secret_type="password"
            )
        
        # Тест с отрицательным offset
        result = self.api.list_secrets(offset=-1)
        self.assertTrue(result["success"])
        self.assertEqual(result["offset"], -1)
        
        # Тест с большим limit
        result = self.api.list_secrets(limit=1000)
        self.assertTrue(result["success"])
        self.assertLessEqual(result["returned_count"], 1000)
        
        # Тест с offset больше количества секретов
        result = self.api.list_secrets(offset=100)
        self.assertTrue(result["success"])
        self.assertEqual(result["returned_count"], 0)


class TestExternalProvidersEdgeCases(unittest.TestCase):
    """Тесты для edge cases внешних провайдеров"""
    
    def test_vault_connection_failure(self):
        """Тест обработки ошибок подключения к Vault"""
        config = {
            "vault_url": "http://nonexistent-vault:8200",
            "token": "invalid-token",
            "mount_point": "secret"
        }
        
        provider = HashiCorpVaultProvider(config)
        success = provider.connect()
        
        self.assertFalse(success)
        self.assertFalse(provider.connected)
    
    def test_aws_connection_failure(self):
        """Тест обработки ошибок подключения к AWS"""
        config = {
            "region": "nonexistent-region"
        }
        
        provider = AWSSecretsManagerProvider(config)
        success = provider.connect()
        
        self.assertFalse(success)
        self.assertFalse(provider.connected)
    
    def test_provider_health_check_failure(self):
        """Тест проверки здоровья провайдера при сбоях"""
        config = {
            "vault_url": "http://localhost:8200",
            "token": "invalid-token",
            "mount_point": "secret"
        }
        
        provider = HashiCorpVaultProvider(config)
        health = provider.health_check()
        
        self.assertFalse(health)
    
    @patch('security.secrets_manager.hvac')
    def test_vault_operations_with_mock(self, mock_hvac):
        """Тест операций Vault с моком"""
        # Настройка мока
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_hvac.Client.return_value = mock_client
        
        config = {
            "vault_url": "http://localhost:8200",
            "token": "test-token",
            "mount_point": "secret"
        }
        
        provider = HashiCorpVaultProvider(config)
        success = provider.connect()
        
        self.assertTrue(success)
        self.assertTrue(provider.connected)
        
        # Тест получения секрета
        mock_client.secrets.kv.v2.read_secret_version.return_value = {
            'data': {'data': {'value': 'test_secret'}}
        }
        
        secret_value = provider.get_secret("test_key")
        self.assertEqual(secret_value, "test_secret")
        
        # Тест сохранения секрета
        success = provider.set_secret("test_key", "test_value")
        self.assertTrue(success)
        
        # Тест удаления секрета
        success = provider.delete_secret("test_key")
        self.assertTrue(success)
    
    @patch('security.secrets_manager.boto3')
    def test_aws_operations_with_mock(self, mock_boto3):
        """Тест операций AWS с моком"""
        # Настройка мока
        mock_client = Mock()
        mock_client.list_secrets.return_value = {'SecretList': []}
        mock_boto3.client.return_value = mock_client
        
        config = {
            "region": "us-east-1"
        }
        
        provider = AWSSecretsManagerProvider(config)
        success = provider.connect()
        
        self.assertTrue(success)
        self.assertTrue(provider.connected)
        
        # Тест получения секрета
        mock_client.get_secret_value.return_value = {
            'SecretString': 'test_secret'
        }
        
        secret_value = provider.get_secret("test_key")
        self.assertEqual(secret_value, "test_secret")
        
        # Тест сохранения секрета
        success = provider.set_secret("test_key", "test_value")
        self.assertTrue(success)
        
        # Тест удаления секрета
        success = provider.delete_secret("test_key")
        self.assertTrue(success)


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)