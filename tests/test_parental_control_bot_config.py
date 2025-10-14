"""
Тесты для системы конфигурации ParentalControlBot.
"""

import pytest
import tempfile
import os
import json
import yaml
from pathlib import Path

from security.bots.components.config_manager import (
    ConfigManager, ParentalControlConfig, DatabaseConfig, RedisConfig,
    SecurityConfig, MonitoringConfig, NotificationConfig, CacheConfig,
    LoggingConfig, ConfigFormat
)


class TestConfigManager:
    """Тесты для ConfigManager."""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию."""
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.bot_name == "ParentalControlBot"
        assert config.version == "2.5"
        assert config.debug is False
        assert config.database.url == "sqlite:///parental_control.db"
        assert config.redis.url == "redis://localhost:6379/0"
        assert config.security.encryption_master_password == ""
        assert config.monitoring.content_analysis_enabled is True
        assert config.notification.push_enabled is True
        assert config.cache.max_size == 1000
        assert config.logging.level == "INFO"
    
    def test_config_to_dict(self):
        """Тест конвертации конфигурации в словарь."""
        config = ParentalControlConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'bot_name' in config_dict
        assert 'version' in config_dict
        assert 'database' in config_dict
        assert 'redis' in config_dict
        assert 'security' in config_dict
        assert 'monitoring' in config_dict
        assert 'notification' in config_dict
        assert 'cache' in config_dict
        assert 'logging' in config_dict
    
    def test_load_from_env(self):
        """Тест загрузки конфигурации из переменных окружения."""
        # Устанавливаем переменные окружения
        os.environ['PARENTAL_BOT_NAME'] = 'TestBot'
        os.environ['PARENTAL_DEBUG'] = 'true'
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        os.environ['REDIS_URL'] = 'redis://localhost:6380/1'
        os.environ['ENCRYPTION_MASTER_PASSWORD'] = 'test_password_123'
        os.environ['CONTENT_ANALYSIS_ENABLED'] = 'false'
        os.environ['EMAIL_ENABLED'] = 'true'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        manager = ConfigManager()
        config = manager.load_from_env()
        
        assert config.bot_name == 'TestBot'
        assert config.debug is True
        assert config.database.url == 'postgresql://test:test@localhost/test'
        assert config.redis.url == 'redis://localhost:6380/1'
        assert config.security.encryption_master_password == 'test_password_123'
        assert config.monitoring.content_analysis_enabled is False
        assert config.notification.email_enabled is True
        assert config.logging.level == 'DEBUG'
        
        # Очищаем переменные окружения
        for key in ['PARENTAL_BOT_NAME', 'PARENTAL_DEBUG', 'DATABASE_URL', 
                   'REDIS_URL', 'ENCRYPTION_MASTER_PASSWORD', 
                   'CONTENT_ANALYSIS_ENABLED', 'EMAIL_ENABLED', 'LOG_LEVEL']:
            if key in os.environ:
                del os.environ[key]
    
    def test_validate_config(self):
        """Тест валидации конфигурации."""
        manager = ConfigManager()
        
        # Валидная конфигурация
        valid_config = ParentalControlConfig()
        errors = manager.validate_config(valid_config)
        assert len(errors) == 0
        
        # Невалидная конфигурация
        invalid_config = ParentalControlConfig()
        invalid_config.bot_name = ""
        invalid_config.database.url = ""
        invalid_config.redis.url = ""
        invalid_config.security.encryption_master_password = "123"
        invalid_config.security.password_min_length = 3
        invalid_config.cache.max_size = 0
        invalid_config.logging.level = "INVALID"
        
        errors = manager.validate_config(invalid_config)
        assert len(errors) > 0
        assert any("bot_name не может быть пустым" in error for error in errors)
        assert any("database.url не может быть пустым" in error for error in errors)
        assert any("redis.url не может быть пустым" in error for error in errors)
        assert any("encryption_master_password должен содержать минимум 8 символов" in error for error in errors)
        assert any("password_min_length должен быть минимум 6" in error for error in errors)
        assert any("cache.max_size должен быть больше 0" in error for error in errors)
        assert any("logging.level должен быть одним из" in error for error in errors)
    
    def test_get_config_schema(self):
        """Тест получения схемы конфигурации."""
        manager = ConfigManager()
        schema = manager.get_config_schema()
        
        assert isinstance(schema, dict)
        assert schema['type'] == 'object'
        assert 'properties' in schema
        assert 'required' in schema
        assert 'bot_name' in schema['properties']
        assert 'database' in schema['properties']
        assert 'redis' in schema['properties']
        assert 'security' in schema['properties']
        assert 'monitoring' in schema['properties']
        assert 'notification' in schema['properties']
        assert 'cache' in schema['properties']
        assert 'logging' in schema['properties']
    
    def test_save_and_load_yaml_config(self):
        """Тест сохранения и загрузки YAML конфигурации."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            manager = ConfigManager()
            config = ParentalControlConfig()
            config.bot_name = "TestBot"
            config.debug = True
            config.database.url = "postgresql://test:test@localhost/test"
            config.redis.url = "redis://localhost:6380/1"
            config.security.encryption_master_password = "test_password_123"
            config.monitoring.content_analysis_enabled = False
            config.notification.email_enabled = True
            config.logging.level = "DEBUG"
            
            # Сохраняем конфигурацию
            success = manager.save_config(config, config_path, ConfigFormat.YAML)
            assert success is True
            assert os.path.exists(config_path)
            
            # Загружаем конфигурацию
            loaded_config = manager.load_config(config_path)
            assert loaded_config.bot_name == "TestBot"
            assert loaded_config.debug is True
            assert loaded_config.database.url == "postgresql://test:test@localhost/test"
            assert loaded_config.redis.url == "redis://localhost:6380/1"
            assert loaded_config.security.encryption_master_password == "test_password_123"
            assert loaded_config.monitoring.content_analysis_enabled is False
            assert loaded_config.notification.email_enabled is True
            assert loaded_config.logging.level == "DEBUG"
            
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_save_and_load_json_config(self):
        """Тест сохранения и загрузки JSON конфигурации."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            manager = ConfigManager()
            config = ParentalControlConfig()
            config.bot_name = "TestBot"
            config.debug = True
            config.database.url = "postgresql://test:test@localhost/test"
            config.redis.url = "redis://localhost:6380/1"
            config.security.encryption_master_password = "test_password_123"
            config.monitoring.content_analysis_enabled = False
            config.notification.email_enabled = True
            config.logging.level = "DEBUG"
            
            # Сохраняем конфигурацию
            success = manager.save_config(config, config_path, ConfigFormat.JSON)
            assert success is True
            assert os.path.exists(config_path)
            
            # Загружаем конфигурацию
            loaded_config = manager.load_config(config_path)
            assert loaded_config.bot_name == "TestBot"
            assert loaded_config.debug is True
            assert loaded_config.database.url == "postgresql://test:test@localhost/test"
            assert loaded_config.redis.url == "redis://localhost:6380/1"
            assert loaded_config.security.encryption_master_password == "test_password_123"
            assert loaded_config.monitoring.content_analysis_enabled is False
            assert loaded_config.notification.email_enabled is True
            assert loaded_config.logging.level == "DEBUG"
            
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_load_nonexistent_config(self):
        """Тест загрузки несуществующего файла конфигурации."""
        manager = ConfigManager()
        config = manager.load_config("nonexistent_config.yaml")
        
        # Должна вернуться конфигурация по умолчанию
        assert config.bot_name == "ParentalControlBot"
        assert config.version == "2.5"
        assert config.debug is False
    
    def test_load_invalid_config(self):
        """Тест загрузки невалидного файла конфигурации."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            manager = ConfigManager()
            config = manager.load_config(config_path)
            
            # Должна вернуться конфигурация по умолчанию
            assert config.bot_name == "ParentalControlBot"
            assert config.version == "2.5"
            assert config.debug is False
            
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_config_components(self):
        """Тест компонентов конфигурации."""
        # Тест DatabaseConfig
        db_config = DatabaseConfig()
        assert db_config.url == "sqlite:///parental_control.db"
        assert db_config.pool_size == 10
        assert db_config.max_overflow == 20
        
        # Тест RedisConfig
        redis_config = RedisConfig()
        assert redis_config.url == "redis://localhost:6379/0"
        assert redis_config.max_connections == 10
        assert redis_config.socket_timeout == 5
        
        # Тест SecurityConfig
        security_config = SecurityConfig()
        assert security_config.encryption_master_password == ""
        assert security_config.encryption_key_rotation_days == 30
        assert security_config.session_timeout == 3600
        
        # Тест MonitoringConfig
        monitoring_config = MonitoringConfig()
        assert monitoring_config.content_analysis_enabled is True
        assert monitoring_config.location_tracking_enabled is True
        assert monitoring_config.ml_enabled is True
        
        # Тест NotificationConfig
        notification_config = NotificationConfig()
        assert notification_config.email_enabled is False
        assert notification_config.sms_enabled is False
        assert notification_config.push_enabled is True
        
        # Тест CacheConfig
        cache_config = CacheConfig()
        assert cache_config.max_size == 1000
        assert cache_config.max_memory_mb == 100
        assert cache_config.default_ttl == 3600
        
        # Тест LoggingConfig
        logging_config = LoggingConfig()
        assert logging_config.level == "INFO"
        assert logging_config.log_file == "logs/parental_control.log"
        assert logging_config.enable_console is True


class TestConfigIntegration:
    """Интеграционные тесты конфигурации."""
    
    def test_full_config_cycle(self):
        """Тест полного цикла работы с конфигурацией."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            manager = ConfigManager()
            
            # Создаем кастомную конфигурацию
            config = ParentalControlConfig()
            config.bot_name = "IntegrationTestBot"
            config.debug = True
            config.database.url = "postgresql://user:pass@localhost:5432/testdb"
            config.database.pool_size = 20
            config.redis.url = "redis://localhost:6380/2"
            config.redis.max_connections = 15
            config.security.encryption_master_password = "integration_test_password_123"
            config.security.encryption_key_rotation_days = 15
            config.monitoring.content_analysis_enabled = False
            config.monitoring.ml_enabled = False
            config.notification.email_enabled = True
            config.notification.smtp_server = "smtp.gmail.com"
            config.notification.smtp_username = "test@gmail.com"
            config.cache.max_size = 2000
            config.cache.max_memory_mb = 200
            config.logging.level = "DEBUG"
            config.logging.log_file = "logs/integration_test.log"
            
            # Валидируем конфигурацию
            errors = manager.validate_config(config)
            assert len(errors) == 0
            
            # Сохраняем конфигурацию
            success = manager.save_config(config, config_path, ConfigFormat.YAML)
            assert success is True
            
            # Загружаем конфигурацию
            loaded_config = manager.load_config(config_path)
            
            # Проверяем все настройки
            assert loaded_config.bot_name == "IntegrationTestBot"
            assert loaded_config.debug is True
            assert loaded_config.database.url == "postgresql://user:pass@localhost:5432/testdb"
            assert loaded_config.database.pool_size == 20
            assert loaded_config.redis.url == "redis://localhost:6380/2"
            assert loaded_config.redis.max_connections == 15
            assert loaded_config.security.encryption_master_password == "integration_test_password_123"
            assert loaded_config.security.encryption_key_rotation_days == 15
            assert loaded_config.monitoring.content_analysis_enabled is False
            assert loaded_config.monitoring.ml_enabled is False
            assert loaded_config.notification.email_enabled is True
            assert loaded_config.notification.smtp_server == "smtp.gmail.com"
            assert loaded_config.notification.smtp_username == "test@gmail.com"
            assert loaded_config.cache.max_size == 2000
            assert loaded_config.cache.max_memory_mb == 200
            assert loaded_config.logging.level == "DEBUG"
            assert loaded_config.logging.log_file == "logs/integration_test.log"
            
            # Проверяем конвертацию в словарь
            config_dict = loaded_config.to_dict()
            assert config_dict['bot_name'] == "IntegrationTestBot"
            assert config_dict['debug'] is True
            assert config_dict['database']['url'] == "postgresql://user:pass@localhost:5432/testdb"
            assert config_dict['database']['pool_size'] == 20
            assert config_dict['redis']['url'] == "redis://localhost:6380/2"
            assert config_dict['redis']['max_connections'] == 15
            assert config_dict['security']['encryption_master_password'] == "integration_test_password_123"
            assert config_dict['security']['encryption_key_rotation_days'] == 15
            assert config_dict['monitoring']['content_analysis_enabled'] is False
            assert config_dict['monitoring']['ml_enabled'] is False
            assert config_dict['notification']['email_enabled'] is True
            assert config_dict['notification']['smtp_server'] == "smtp.gmail.com"
            assert config_dict['notification']['smtp_username'] == "test@gmail.com"
            assert config_dict['cache']['max_size'] == 2000
            assert config_dict['cache']['max_memory_mb'] == 200
            assert config_dict['logging']['level'] == "DEBUG"
            assert config_dict['logging']['log_file'] == "logs/integration_test.log"
            
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_config_merging(self):
        """Тест слияния конфигураций."""
        manager = ConfigManager()
        
        # Базовая конфигурация
        base_config = ParentalControlConfig()
        base_config.bot_name = "BaseBot"
        base_config.database.url = "sqlite:///base.db"
        
        # Переопределяем некоторые настройки
        override_data = {
            'bot_name': 'OverrideBot',
            'database': {
                'pool_size': 25
            },
            'security': {
                'encryption_master_password': 'override_password_123'
            }
        }
        
        # Создаем новую конфигурацию с переопределениями
        new_config = ParentalControlConfig()
        new_config.bot_name = override_data['bot_name']
        new_config.database.url = base_config.database.url  # Берем из базовой
        new_config.database.pool_size = override_data['database']['pool_size']
        new_config.security.encryption_master_password = override_data['security']['encryption_master_password']
        
        # Проверяем результат
        assert new_config.bot_name == "OverrideBot"
        assert new_config.database.url == "sqlite:///base.db"  # Из базовой
        assert new_config.database.pool_size == 25  # Переопределено
        assert new_config.security.encryption_master_password == "override_password_123"  # Переопределено
        assert new_config.redis.url == "redis://localhost:6379/0"  # По умолчанию


if __name__ == "__main__":
    pytest.main([__file__])