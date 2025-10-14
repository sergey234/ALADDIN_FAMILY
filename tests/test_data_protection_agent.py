# -*- coding: utf-8 -*-
"""
Тесты для DataProtectionAgent
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
# from unittest.mock import patch, MagicMock  # Python 3 only

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.data_protection_agent import (
    DataProtectionAgent,
    DataType,
    ProtectionLevel,
    EncryptionMethod,
    DataStatus,
    DataProtectionEvent,
    DataProtectionResult,
    DataProtectionMetrics
)


class TestDataProtectionAgent(unittest.TestCase):
    """Тесты для DataProtectionAgent"""

    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "encryption_enabled": True,
            "anonymization_enabled": True,
            "backup_enabled": True,
            "compliance_check_enabled": True,
            "risk_assessment_enabled": True,
            "backup_directory": self.temp_dir,
            "state_directory": self.temp_dir
        }
        self.agent = DataProtectionAgent(config=self.config)

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Тест инициализации агента"""
        self.assertTrue(self.agent.initialize())
        self.assertEqual(self.agent.encryption_enabled, True)
        self.assertEqual(self.agent.anonymization_enabled, True)
        self.assertEqual(self.agent.backup_enabled, True)

    def test_protect_personal_data(self):
        """Тест защиты персональных данных"""
        self.agent.initialize()
        
        personal_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        result = self.agent.protect_data(
            data_id="test_personal_001",
            data=personal_data,
            data_type=DataType.PERSONAL,
            protection_level=ProtectionLevel.HIGH
        )
        
        self.assertIsInstance(result, DataProtectionResult)
        self.assertEqual(result.data_id, "test_personal_001")
        self.assertIn(result.protection_status, [DataStatus.PROTECTED, DataStatus.ENCRYPTED, DataStatus.ANONYMIZED])
        self.assertGreater(result.protection_score, 0.0)
        self.assertIsInstance(result.recommendations, list)

    def test_protect_financial_data(self):
        """Тест защиты финансовых данных"""
        self.agent.initialize()
        
        financial_data = {
            "account_number": "1234567890",
            "balance": 10000.50,
            "transactions": ["deposit", "withdrawal"]
        }
        
        result = self.agent.protect_data(
            data_id="test_financial_001",
            data=financial_data,
            data_type=DataType.FINANCIAL,
            protection_level=ProtectionLevel.CRITICAL
        )
        
        self.assertIsInstance(result, DataProtectionResult)
        self.assertEqual(result.data_id, "test_financial_001")
        self.assertLessEqual(result.risk_level, 1.0)
        self.assertGreaterEqual(result.risk_level, 0.0)

    def test_encryption_functionality(self):
        """Тест функциональности шифрования"""
        self.agent.initialize()
        
        test_data = "Sensitive information"
        encrypted = self.agent._encrypt_data(test_data, "test_encrypt_001")
        
        self.assertNotEqual(encrypted, test_data)
        self.assertIsInstance(encrypted, str)
        self.assertGreater(len(encrypted), 0)

    def test_anonymization_functionality(self):
        """Тест функциональности анонимизации"""
        self.agent.initialize()
        
        personal_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        anonymized = self.agent._anonymize_data(personal_data)
        
        self.assertIn("***ANONYMIZED***", str(anonymized))
        self.assertNotEqual(anonymized, personal_data)

    def test_risk_assessment(self):
        """Тест оценки рисков"""
        self.agent.initialize()
        
        # Тест высокого риска
        high_risk = self.agent._assess_data_risk(
            "sensitive data",
            DataType.MEDICAL,
            ProtectionLevel.LOW
        )
        self.assertGreater(high_risk, 0.5)
        
        # Тест низкого риска
        low_risk = self.agent._assess_data_risk(
            "technical data",
            DataType.TECHNICAL,
            ProtectionLevel.CRITICAL
        )
        self.assertLess(low_risk, 0.5)

    def test_compliance_checking(self):
        """Тест проверки соответствия"""
        self.agent.initialize()
        
        personal_data = {"name": "Test User", "email": "test@example.com"}
        
        # Тест соответствия GDPR
        gdpr_compliant = self.agent._check_gdpr_rule(personal_data, "data_minimization")
        self.assertTrue(gdpr_compliant)
        
        # Тест соответствия COPPA
        coppa_compliant = self.agent._check_coppa_rule(personal_data, "parental_consent")
        self.assertTrue(coppa_compliant)
        
        # Тест соответствия 152-ФЗ
        fz152_compliant = self.agent._check_fz152_rule(personal_data, "data_localization")
        self.assertTrue(fz152_compliant)

    def test_backup_functionality(self):
        """Тест функциональности резервного копирования"""
        self.agent.initialize()
        
        test_data = {"test": "backup data"}
        self.agent._backup_data("test_backup_001", test_data)
        
        # Проверяем, что файл резервной копии создан
        backup_files = [f for f in os.listdir(self.temp_dir) if f.startswith("backup_test_backup_001")]
        self.assertGreater(len(backup_files), 0)

    def test_metrics_tracking(self):
        """Тест отслеживания метрик"""
        self.agent.initialize()
        
        initial_metrics = self.agent.get_metrics()
        initial_total = initial_metrics.total_data_items
        
        # Защищаем данные
        self.agent.protect_data(
            data_id="test_metrics_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        updated_metrics = self.agent.get_metrics()
        self.assertEqual(updated_metrics.total_data_items, initial_total + 1)

    def test_protection_status_retrieval(self):
        """Тест получения статуса защиты"""
        self.agent.initialize()
        
        # Защищаем данные
        self.agent.protect_data(
            data_id="test_status_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        # Получаем статус
        status = self.agent.get_protection_status("test_status_001")
        self.assertIsInstance(status, DataProtectionResult)
        self.assertEqual(status.data_id, "test_status_001")

    def test_protection_events(self):
        """Тест событий защиты"""
        self.agent.initialize()
        
        # Защищаем данные
        self.agent.protect_data(
            data_id="test_events_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        # Получаем события
        events = self.agent.get_protection_events()
        self.assertGreater(len(events), 0)
        
        event = events[-1]
        self.assertIsInstance(event, DataProtectionEvent)
        self.assertEqual(event.data_id, "test_events_001")

    def test_cleanup_old_data(self):
        """Тест очистки старых данных"""
        self.agent.initialize()
        
        # Защищаем данные
        self.agent.protect_data(
            data_id="test_cleanup_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        # Симулируем старые данные
        old_time = datetime.now() - timedelta(days=35)
        self.agent.protected_data["test_cleanup_001"]["created_at"] = old_time.isoformat()
        
        # Очищаем старые данные
        self.agent.cleanup_old_data(days=30)
        
        # Проверяем, что старые данные удалены
        self.assertNotIn("test_cleanup_001", self.agent.protected_data)

    def test_recommendation_generation(self):
        """Тест генерации рекомендаций"""
        self.agent.initialize()
        
        recommendations = self.agent._generate_recommendations(
            DataType.PERSONAL,
            ProtectionLevel.LOW,
            0.8
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_protection_score_calculation(self):
        """Тест расчета оценки защиты"""
        self.agent.initialize()
        
        # Тест высокой оценки
        high_score = self.agent._calculate_protection_score(DataStatus.COMPLIANT, 0.1)
        self.assertGreater(high_score, 0.8)
        
        # Тест низкой оценки
        low_score = self.agent._calculate_protection_score(DataStatus.COMPROMISED, 0.9)
        self.assertLess(low_score, 0.2)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным агентом
        result = self.agent.protect_data(
            data_id="test_error_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        # Агент должен обработать ошибку gracefully
        self.assertIsInstance(result, DataProtectionResult)

    def test_state_saving(self):
        """Тест сохранения состояния"""
        self.agent.initialize()
        
        # Защищаем данные
        self.agent.protect_data(
            data_id="test_state_001",
            data="test data",
            data_type=DataType.TECHNICAL
        )
        
        # Сохраняем состояние
        self.agent._save_state()
        
        # Проверяем, что файл состояния создан
        state_file = os.path.join(self.temp_dir, "data_protection_agent_state.json")
        self.assertTrue(os.path.exists(state_file))

    def test_different_data_types(self):
        """Тест различных типов данных"""
        self.agent.initialize()
        
        data_types = [
            DataType.PERSONAL,
            DataType.FINANCIAL,
            DataType.MEDICAL,
            DataType.BUSINESS,
            DataType.TECHNICAL,
            DataType.SENSITIVE
        ]
        
        for i, data_type in enumerate(data_types):
            result = self.agent.protect_data(
                data_id="test_type_{}".format(i),
                data="test data for {}".format(data_type.value),
                data_type=data_type
            )
            
            self.assertIsInstance(result, DataProtectionResult)
            self.assertEqual(result.data_id, "test_type_{}".format(i))

    def test_different_protection_levels(self):
        """Тест различных уровней защиты"""
        self.agent.initialize()
        
        protection_levels = [
            ProtectionLevel.LOW,
            ProtectionLevel.MEDIUM,
            ProtectionLevel.HIGH,
            ProtectionLevel.CRITICAL
        ]
        
        for i, level in enumerate(protection_levels):
            result = self.agent.protect_data(
                data_id="test_level_{}".format(i),
                data="test data",
                data_type=DataType.TECHNICAL,
                protection_level=level
            )
            
            self.assertIsInstance(result, DataProtectionResult)
            self.assertEqual(result.data_id, "test_level_{}".format(i))

    def test_encryption_key_generation(self):
        """Тест генерации ключей шифрования"""
        self.agent.initialize()
        
        key1 = self.agent._generate_encryption_key()
        key2 = self.agent._generate_encryption_key()
        
        self.assertIsInstance(key1, str)
        self.assertIsInstance(key2, str)
        self.assertNotEqual(key1, key2)
        self.assertEqual(len(key1), 64)  # SHA256 hex length

    def test_compliance_rules_setup(self):
        """Тест настройки правил соответствия"""
        self.agent.initialize()
        
        self.assertIn("GDPR", self.agent.compliance_rules)
        self.assertIn("COPPA", self.agent.compliance_rules)
        self.assertIn("152-FZ", self.agent.compliance_rules)
        
        self.assertGreater(len(self.agent.compliance_rules["GDPR"]), 0)
        self.assertGreater(len(self.agent.compliance_rules["COPPA"]), 0)
        self.assertGreater(len(self.agent.compliance_rules["152-FZ"]), 0)


if __name__ == "__main__":
    unittest.main()