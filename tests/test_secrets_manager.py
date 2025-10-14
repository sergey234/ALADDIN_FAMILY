#!/usr/bin/env python3
"""
Тесты для SecretsManager
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from security.secrets_manager import (
    SecretsManager, SecretType, SecretStatus, SecretMetadata,
    HashiCorpVaultProvider, AWSSecretsManagerProvider
)
from security.secrets_api import SecretsAPI


class TestSecretsManager(unittest.TestCase):
    """Тесты для SecretsManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "storage_path": self.temp_dir,
            "auto_rotation": False,  # Отключаем для тестов
            "external_providers": {}
        }
        self.secrets_manager = SecretsManager(self.config)
        self.secrets_manager.initialize()
    
    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'secrets_manager'):
            self.secrets_manager.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Тест инициализации"""
        self.assertEqual(self.secrets_manager.name, "SecretsManager")
        self.assertTrue(self.secrets_manager.storage_path.exists())
        self.assertEqual(len(self.secrets_manager.secrets), 0)
        self.assertEqual(len(self.secrets_manager.metadata), 0)
    
    def test_store_secret(self):
        """Тест сохранения секрета"""
        secret_id = self.secrets_manager.store_secret(
            name="test_secret",
            value="test_value",
            secret_type=SecretType.PASSWORD,
            description="Тестовый секрет"
        )
        
        self.assertIsNotNone(secret_id)
        self.assertIn(secret_id, self.secrets_manager.secrets)
        self.assertIn(secret_id, self.secrets_manager.metadata)
        
        metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(metadata.name, "test_secret")
        self.assertEqual(metadata.secret_type, SecretType.PASSWORD)
        self.assertEqual(metadata.description, "Тестовый секрет")
        self.assertEqual(metadata.status, SecretStatus.ACTIVE)
    
    def test_get_secret(self):
        """Тест получения секрета"""
        # Сохранение секрета
        secret_id = self.secrets_manager.store_secret(
            name="test_secret",
            value="test_value",
            secret_type=SecretType.API_KEY
        )
        
        # Получение секрета
        retrieved_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(retrieved_value, "test_value")
        
        # Проверка обновления метаданных
        metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(metadata.access_count, 1)
        self.assertIsNotNone(metadata.last_accessed)
    
    def test_get_secret_by_name(self):
        """Тест получения секрета по имени"""
        # Сохранение секрета
        secret_id = self.secrets_manager.store_secret(
            name="test_secret",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Получение по имени
        retrieved_value = self.secrets_manager.get_secret_by_name("test_secret")
        self.assertEqual(retrieved_value, "test_value")
        
        # Получение несуществующего секрета
        non_existent = self.secrets_manager.get_secret_by_name("non_existent")
        self.assertIsNone(non_existent)
    
    def test_delete_secret(self):
        """Тест удаления секрета"""
        # Сохранение секрета
        secret_id = self.secrets_manager.store_secret(
            name="test_secret",
            value="test_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Проверка существования
        self.assertIn(secret_id, self.secrets_manager.secrets)
        
        # Удаление
        success = self.secrets_manager.delete_secret(secret_id)
        self.assertTrue(success)
        
        # Проверка удаления
        self.assertNotIn(secret_id, self.secrets_manager.secrets)
        self.assertNotIn(secret_id, self.secrets_manager.metadata)
    
    def test_rotate_secret(self):
        """Тест ротации секрета"""
        # Сохранение секрета
        secret_id = self.secrets_manager.store_secret(
            name="test_secret",
            value="old_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Получение исходной версии
        metadata = self.secrets_manager.metadata[secret_id]
        original_version = metadata.version
        
        # Ротация
        success = self.secrets_manager.rotate_secret(secret_id, "new_value")
        self.assertTrue(success)
        
        # Проверка нового значения
        new_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(new_value, "new_value")
        
        # Проверка версии
        updated_metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(updated_metadata.version, original_version + 1)
    
    def test_list_secrets(self):
        """Тест получения списка секретов"""
        # Создание нескольких секретов
        secret_ids = []
        for i in range(3):
            secret_id = self.secrets_manager.store_secret(
                name=f"secret_{i}",
                value=f"value_{i}",
                secret_type=SecretType.PASSWORD
            )
            secret_ids.append(secret_id)
        
        # Получение списка
        secrets_list = self.secrets_manager.list_secrets()
        self.assertEqual(len(secrets_list), 3)
        
        # Проверка содержимого
        names = [secret["name"] for secret in secrets_list]
        self.assertIn("secret_0", names)
        self.assertIn("secret_1", names)
        self.assertIn("secret_2", names)
    
    def test_list_secrets_by_type(self):
        """Тест фильтрации секретов по типу"""
        # Создание секретов разных типов
        self.secrets_manager.store_secret(
            name="password_secret",
            value="password_value",
            secret_type=SecretType.PASSWORD
        )
        
        self.secrets_manager.store_secret(
            name="api_key_secret",
            value="api_key_value",
            secret_type=SecretType.API_KEY
        )
        
        # Фильтрация по типу
        password_secrets = self.secrets_manager.list_secrets(SecretType.PASSWORD)
        self.assertEqual(len(password_secrets), 1)
        self.assertEqual(password_secrets[0]["name"], "password_secret")
        
        api_key_secrets = self.secrets_manager.list_secrets(SecretType.API_KEY)
        self.assertEqual(len(api_key_secrets), 1)
        self.assertEqual(api_key_secrets[0]["name"], "api_key_secret")
    
    def test_expired_secret(self):
        """Тест работы с истекшим секретом"""
        # Создание секрета с истекшим сроком
        expired_time = datetime.now() - timedelta(days=1)
        secret_id = self.secrets_manager.store_secret(
            name="expired_secret",
            value="expired_value",
            secret_type=SecretType.PASSWORD,
            expires_at=expired_time
        )
        
        # Попытка получения истекшего секрета
        retrieved_value = self.secrets_manager.get_secret(secret_id)
        self.assertIsNone(retrieved_value)
        
        # Проверка статуса
        metadata = self.secrets_manager.metadata[secret_id]
        self.assertEqual(metadata.status, SecretStatus.EXPIRED)
    
    def test_encryption_decryption(self):
        """Тест шифрования и расшифровки"""
        # Сохранение секрета
        secret_id = self.secrets_manager.store_secret(
            name="encrypted_secret",
            value="sensitive_data",
            secret_type=SecretType.PASSWORD
        )
        
        # Проверка, что секрет зашифрован в хранилище
        encrypted_value = self.secrets_manager.secrets[secret_id]
        self.assertNotEqual(encrypted_value, "sensitive_data")
        self.assertIsInstance(encrypted_value, str)
        
        # Проверка расшифровки
        decrypted_value = self.secrets_manager.get_secret(secret_id)
        self.assertEqual(decrypted_value, "sensitive_data")
    
    def test_metrics(self):
        """Тест метрик"""
        # Создание и использование секретов
        secret_id = self.secrets_manager.store_secret(
            name="metrics_secret",
            value="metrics_value",
            secret_type=SecretType.PASSWORD
        )
        
        # Получение секрета несколько раз
        for _ in range(3):
            self.secrets_manager.get_secret(secret_id)
        
        # Ротация
        self.secrets_manager.rotate_secret(secret_id)
        
        # Проверка метрик
        metrics = self.secrets_manager.get_metrics()
        self.assertEqual(metrics["secrets_count"], 1)
        self.assertEqual(metrics["access_count"], 3)
        self.assertEqual(metrics["rotation_count"], 1)
    
    def test_health_check(self):
        """Тест проверки здоровья"""
        health = self.secrets_manager.health_check()
        
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["secrets_count"], 0)
        self.assertTrue(health["storage_writable"])
        self.assertFalse(health["rotation_thread"])
        self.assertEqual(len(health["external_providers"]), 0)


class TestSecretsAPI(unittest.TestCase):
    """Тесты для SecretsAPI"""
    
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
    
    def test_create_secret(self):
        """Тест создания секрета через API"""
        result = self.api.create_secret(
            name="api_test_secret",
            value="api_test_value",
            secret_type="password",
            description="Тестовый секрет через API"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("secret_id", result)
        self.assertEqual(result["name"], "api_test_secret")
        self.assertEqual(result["type"], "password")
    
    def test_get_secret(self):
        """Тест получения секрета через API"""
        # Создание секрета
        create_result = self.api.create_secret(
            name="api_get_secret",
            value="api_get_value",
            secret_type="api_key"
        )
        secret_id = create_result["secret_id"]
        
        # Получение секрета
        get_result = self.api.get_secret(secret_id)
        
        self.assertTrue(get_result["success"])
        self.assertEqual(get_result["value"], "api_get_value")
        self.assertEqual(get_result["name"], "api_get_secret")
        self.assertEqual(get_result["type"], "api_key")
    
    def test_get_secret_by_name(self):
        """Тест получения секрета по имени через API"""
        # Создание секрета
        self.api.create_secret(
            name="api_name_secret",
            value="api_name_value",
            secret_type="password"
        )
        
        # Получение по имени
        result = self.api.get_secret("api_name_secret", by_name=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["value"], "api_name_value")
        self.assertEqual(result["name"], "api_name_secret")
    
    def test_update_secret(self):
        """Тест обновления секрета через API"""
        # Создание секрета
        create_result = self.api.create_secret(
            name="api_update_secret",
            value="old_value",
            secret_type="password"
        )
        secret_id = create_result["secret_id"]
        
        # Обновление значения
        update_result = self.api.update_secret(
            secret_id,
            new_value="new_value",
            new_description="Обновленное описание"
        )
        
        self.assertTrue(update_result["success"])
        
        # Проверка обновления
        get_result = self.api.get_secret(secret_id)
        self.assertEqual(get_result["value"], "new_value")
    
    def test_delete_secret(self):
        """Тест удаления секрета через API"""
        # Создание секрета
        create_result = self.api.create_secret(
            name="api_delete_secret",
            value="api_delete_value",
            secret_type="password"
        )
        secret_id = create_result["secret_id"]
        
        # Удаление
        delete_result = self.api.delete_secret(secret_id)
        self.assertTrue(delete_result["success"])
        
        # Проверка удаления
        get_result = self.api.get_secret(secret_id)
        self.assertFalse(get_result["success"])
        self.assertIn("error", get_result)
    
    def test_list_secrets(self):
        """Тест получения списка секретов через API"""
        # Создание нескольких секретов
        for i in range(3):
            self.api.create_secret(
                name=f"api_list_secret_{i}",
                value=f"value_{i}",
                secret_type="password"
            )
        
        # Получение списка
        result = self.api.list_secrets()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(len(result["secrets"]), 3)
    
    def test_search_secrets(self):
        """Тест поиска секретов через API"""
        # Создание секретов с разными описаниями
        self.api.create_secret(
            name="database_password",
            value="db_pass",
            secret_type="password",
            description="Пароль для базы данных"
        )
        
        self.api.create_secret(
            name="api_key_production",
            value="api_key",
            secret_type="api_key",
            description="API ключ для продакшена"
        )
        
        # Поиск по описанию
        result = self.api.search_secrets("база данных")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["name"], "database_password")
    
    def test_statistics(self):
        """Тест получения статистики через API"""
        # Создание секретов
        self.api.create_secret(
            name="stats_secret_1",
            value="value1",
            secret_type="password"
        )
        
        self.api.create_secret(
            name="stats_secret_2",
            value="value2",
            secret_type="api_key"
        )
        
        # Получение статистики
        result = self.api.get_statistics()
        
        self.assertTrue(result["success"])
        stats = result["statistics"]
        self.assertEqual(stats["total_secrets"], 2)
        self.assertEqual(stats["type_distribution"]["password"], 1)
        self.assertEqual(stats["type_distribution"]["api_key"], 1)
    
    def test_bulk_operations(self):
        """Тест массовых операций через API"""
        # Массовое создание
        secrets_data = [
            {
                "name": f"bulk_secret_{i}",
                "value": f"bulk_value_{i}",
                "secret_type": "password"
            }
            for i in range(3)
        ]
        
        create_result = self.api.bulk_create_secrets(secrets_data)
        self.assertTrue(create_result["success"])
        self.assertEqual(create_result["success_count"], 3)
        
        # Получение списка для массового удаления
        list_result = self.api.list_secrets()
        secret_ids = [secret["secret_id"] for secret in list_result["secrets"]]
        
        # Массовое удаление
        delete_result = self.api.bulk_delete_secrets(secret_ids)
        self.assertTrue(delete_result["success"])
        self.assertEqual(delete_result["success_count"], 3)


class TestSecretMetadata(unittest.TestCase):
    """Тесты для SecretMetadata"""
    
    def test_metadata_creation(self):
        """Тест создания метаданных"""
        metadata = SecretMetadata(
            secret_id="test_id",
            name="test_secret",
            secret_type=SecretType.PASSWORD,
            created_at=datetime.now(),
            description="Тестовые метаданные",
            tags={"env": "test"}
        )
        
        self.assertEqual(metadata.secret_id, "test_id")
        self.assertEqual(metadata.name, "test_secret")
        self.assertEqual(metadata.secret_type, SecretType.PASSWORD)
        self.assertEqual(metadata.description, "Тестовые метаданные")
        self.assertEqual(metadata.tags["env"], "test")
        self.assertEqual(metadata.status, SecretStatus.ACTIVE)
        self.assertEqual(metadata.version, 1)
    
    def test_metadata_serialization(self):
        """Тест сериализации метаданных"""
        metadata = SecretMetadata(
            secret_id="test_id",
            name="test_secret",
            secret_type=SecretType.API_KEY,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30),
            description="Тестовые метаданные",
            tags={"env": "test", "service": "api"}
        )
        
        # Преобразование в словарь
        data = metadata.to_dict()
        
        self.assertEqual(data["secret_id"], "test_id")
        self.assertEqual(data["name"], "test_secret")
        self.assertEqual(data["secret_type"], "api_key")
        self.assertEqual(data["description"], "Тестовые метаданные")
        self.assertEqual(data["tags"]["env"], "test")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["version"], 1)
        
        # Восстановление из словаря
        restored_metadata = SecretMetadata.from_dict(data)
        
        self.assertEqual(restored_metadata.secret_id, metadata.secret_id)
        self.assertEqual(restored_metadata.name, metadata.name)
        self.assertEqual(restored_metadata.secret_type, metadata.secret_type)
        self.assertEqual(restored_metadata.description, metadata.description)
        self.assertEqual(restored_metadata.tags, metadata.tags)
        self.assertEqual(restored_metadata.status, metadata.status)
        self.assertEqual(restored_metadata.version, metadata.version)


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)