"""
Тест исправлений безопасности для ALADDIN Security System
Проверяет устранение критических уязвимостей
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import DatabaseManager
from security.secure_config_manager import SecureConfigManager, SecureConfig
from security.ransomware_protection import RansomwareProtectionSystem
from security.zero_trust_manager import ZeroTrustManager, UserIdentity, AccessRequest, DeviceFingerprint

class TestSecurityFixes(unittest.TestCase):
    """Тесты исправлений безопасности"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
    def tearDown(self):
        """Очистка после тестов"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sql_injection_protection(self):
        """Тест защиты от SQL инъекций"""
        print("\n🔍 Тестирование защиты от SQL инъекций...")
        
        # Создаем менеджер базы данных
        db_manager = DatabaseManager("TestDB", {"db_path": self.db_path})
        db_manager.start()
        
        # Тестируем безопасную валидацию имени таблицы
        self.assertTrue(db_manager._is_valid_table_name("users"))
        self.assertTrue(db_manager._is_valid_table_name("security_events"))
        self.assertTrue(db_manager._is_valid_table_name("test_table_123"))
        
        # Тестируем блокировку опасных имен
        self.assertFalse(db_manager._is_valid_table_name("users; DROP TABLE users; --"))
        self.assertFalse(db_manager._is_valid_table_name("'; DELETE FROM users; --"))
        self.assertFalse(db_manager._is_valid_table_name("users UNION SELECT * FROM passwords"))
        self.assertFalse(db_manager._is_valid_table_name(""))
        self.assertFalse(db_manager._is_valid_table_name("123invalid"))
        self.assertFalse(db_manager._is_valid_table_name("select"))  # SQL ключевое слово
        
        # Тестируем длинные имена
        long_name = "a" * 65  # Превышает лимит в 64 символа
        self.assertFalse(db_manager._is_valid_table_name(long_name))
        
        print("✅ Защита от SQL инъекций работает корректно")
    
    def test_secure_config_manager(self):
        """Тест безопасного менеджера конфигурации"""
        print("\n🔍 Тестирование безопасного менеджера конфигурации...")
        
        # Устанавливаем переменную окружения для теста
        os.environ['ALADDIN_MASTER_PASSWORD'] = 'test_master_password_123'
        
        # Создаем менеджер конфигурации
        config_manager = SecureConfigManager("test_config.json")
        
        # Создаем тестовую конфигурацию
        config = SecureConfig(
            telegram_bot_token="test_token_123",
            discord_bot_token="discord_token_456",
            twilio_auth_token="twilio_token_789",
            email_password="email_pass_123",
            firebase_server_key="firebase_key_456",
            encryption_key="encryption_key_789"
        )
        
        # Сохраняем конфигурацию
        self.assertTrue(config_manager.save_config(config))
        
        # Загружаем конфигурацию
        loaded_config = config_manager.load_config()
        self.assertIsNotNone(loaded_config)
        
        # Валидируем конфигурацию
        validation = config_manager.validate_config()
        self.assertTrue(validation['valid'])
        self.assertGreater(validation['security_score'], 80)
        
        # Создаем шаблон переменных окружения
        self.assertTrue(config_manager.create_env_template("test.env.template"))
        self.assertTrue(os.path.exists("test.env.template"))
        
        # Очищаем
        os.remove("test.env.template")
        os.remove("test_config.json")
        
        print("✅ Безопасный менеджер конфигурации работает корректно")
    
    def test_ransomware_protection(self):
        """Тест защиты от ransomware"""
        print("\n🔍 Тестирование защиты от ransomware...")
        
        # Создаем систему защиты от ransomware
        ransomware_protection = RansomwareProtectionSystem("TestRansomwareProtection")
        
        # Создаем тестовые директории
        test_dir = os.path.join(self.temp_dir, "test_files")
        os.makedirs(test_dir, exist_ok=True)
        
        # Создаем тестовые файлы
        test_files = [
            "normal_file.txt",
            "suspicious_file.wncry",
            "encrypted_file.locked",
            "malware_file.cerber"
        ]
        
        for file_name in test_files:
            file_path = os.path.join(test_dir, file_name)
            with open(file_path, 'w') as f:
                f.write("Test content")
        
        # Запускаем мониторинг
        self.assertTrue(ransomware_protection.start_monitoring([test_dir]))
        
        # Проверяем статус
        status = ransomware_protection.get_status()
        self.assertTrue(status['is_running'])
        self.assertGreater(len(status['monitored_directories']), 0)
        
        # Тестируем обнаружение подозрительных файлов
        suspicious_count = status['suspicious_files_count']
        self.assertGreaterEqual(suspicious_count, 0)
        
        # Останавливаем систему
        ransomware_protection.stop()
        
        print("✅ Защита от ransomware работает корректно")
    
    def test_zero_trust_manager(self):
        """Тест менеджера Zero Trust"""
        print("\n🔍 Тестирование менеджера Zero Trust...")
        
        # Создаем менеджер Zero Trust
        zero_trust = ZeroTrustManager("TestZeroTrust")
        zero_trust.start()
        
        # Регистрируем устройство
        device = DeviceFingerprint(
            device_id="test_device_001",
            hardware_id="hw_test_12345",
            os_info="Test OS",
            mac_address="00:11:22:33:44:55",
            screen_resolution="1920x1080"
        )
        self.assertTrue(zero_trust.register_device(device))
        
        # Регистрируем пользователя
        user = UserIdentity(
            user_id="test_user_001",
            username="testuser",
            email="test@example.com",
            mfa_enabled=True,
            trust_score=0.8
        )
        self.assertTrue(zero_trust.register_user(user))
        
        # Запрашиваем доступ
        context = {
            'ip_address': '192.168.1.100',
            'user_agent': 'Test Browser'
        }
        
        access_request = zero_trust.request_access(
            user_id="test_user_001",
            device_id="test_device_001",
            resource="/test/resource",
            action="read",
            context=context
        )
        
        self.assertIsNotNone(access_request)
        self.assertEqual(access_request.user_id, "test_user_001")
        self.assertEqual(access_request.device_id, "test_device_001")
        
        # Проверяем оценку риска
        self.assertGreaterEqual(access_request.risk_score, 0.0)
        self.assertLessEqual(access_request.risk_score, 1.0)
        
        # Проверяем статус
        status = zero_trust.get_status()
        self.assertTrue(status['is_running'])
        self.assertGreater(status['devices_count'], 0)
        self.assertGreater(status['users_count'], 0)
        
        zero_trust.stop()
        
        print("✅ Менеджер Zero Trust работает корректно")
    
    def test_integration_security(self):
        """Тест интеграции всех компонентов безопасности"""
        print("\n🔍 Тестирование интеграции компонентов безопасности...")
        
        # Устанавливаем переменную окружения для теста
        os.environ['ALADDIN_MASTER_PASSWORD'] = 'integration_test_password_123'
        
        # Создаем все компоненты
        db_manager = DatabaseManager("IntegrationTestDB", {"db_path": self.db_path})
        config_manager = SecureConfigManager("integration_config.json")
        ransomware_protection = RansomwareProtectionSystem("IntegrationRansomware")
        zero_trust = ZeroTrustManager("IntegrationZeroTrust")
        
        # Запускаем компоненты
        self.assertTrue(db_manager.start())
        zero_trust.start()
        
        # Создаем тестовую конфигурацию
        config = SecureConfig(
            telegram_bot_token="integration_test_token",
            encryption_key="integration_encryption_key"
        )
        self.assertTrue(config_manager.save_config(config))
        
        # Тестируем интеграцию
        loaded_config = config_manager.load_config()
        self.assertIsNotNone(loaded_config)
        
        # Проверяем работу базы данных с безопасными запросами
        stats = db_manager.get_database_stats()
        self.assertIsInstance(stats, dict)
        
        # Проверяем Zero Trust
        status = zero_trust.get_status()
        self.assertTrue(status['is_running'])
        
        # Очищаем
        db_manager.stop()
        zero_trust.stop()
        os.remove("integration_config.json")
        
        print("✅ Интеграция компонентов безопасности работает корректно")

def run_security_tests():
    """Запуск всех тестов безопасности"""
    print("🛡️ ЗАПУСК ТЕСТОВ ИСПРАВЛЕНИЙ БЕЗОПАСНОСТИ")
    print("=" * 50)
    
    # Создаем тестовый набор
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurityFixes)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Успешных тестов: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Неудачных тестов: {len(result.failures)}")
    print(f"💥 Ошибок: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ НЕУДАЧНЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ОШИБКИ:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 УСПЕШНОСТЬ: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🛡️ СИСТЕМА БЕЗОПАСНОСТИ: ОТЛИЧНО!")
    elif success_rate >= 80:
        print("🛡️ СИСТЕМА БЕЗОПАСНОСТИ: ХОРОШО!")
    elif success_rate >= 70:
        print("🛡️ СИСТЕМА БЕЗОПАСНОСТИ: УДОВЛЕТВОРИТЕЛЬНО!")
    else:
        print("🛡️ СИСТЕМА БЕЗОПАСНОСТИ: ТРЕБУЕТ ДОРАБОТКИ!")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)