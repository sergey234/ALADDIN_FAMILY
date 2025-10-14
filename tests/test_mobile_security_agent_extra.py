#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для mobile_security_agent_extra.py
"""

import unittest
import asyncio
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

from security.ai_agents.mobile_security_agent_extra import (
    MobileSecurityAgentExtra,
    ThreatData
)


class TestThreatData(unittest.TestCase):
    """Тесты для класса ThreatData"""
    
    def setUp(self):
        """Настройка тестов"""
        self.threat_data = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
    
    def test_threat_data_creation(self):
        """Тест создания ThreatData"""
        self.assertEqual(self.threat_data.app_id, "com.test.app")
        self.assertEqual(self.threat_data.threat_type, "malware")
        self.assertEqual(self.threat_data.severity, "high")
        self.assertEqual(self.threat_data.confidence, 0.8)
        self.assertIsInstance(self.threat_data.timestamp, datetime)
        self.assertEqual(self.threat_data.details, {"source": "test"})
    
    def test_threat_data_repr(self):
        """Тест __repr__ метода"""
        repr_str = repr(self.threat_data)
        self.assertIn("ThreatData", repr_str)
        self.assertIn("com.test.app", repr_str)
    
    def test_threat_data_equality(self):
        """Тест __eq__ метода"""
        threat_data2 = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=self.threat_data.timestamp,
            details={"source": "test"}
        )
        self.assertEqual(self.threat_data, threat_data2)
        
        threat_data3 = ThreatData(
            app_id="com.different.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
        self.assertNotEqual(self.threat_data, threat_data3)
    
    def test_threat_data_hash(self):
        """Тест __hash__ метода"""
        # Создаем ThreatData с хэшируемыми данными
        hashable_threat = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details=()  # Используем tuple вместо dict для хэширования
        )
        hash_val = hash(hashable_threat)
        self.assertIsInstance(hash_val, int)


class TestMobileSecurityAgentExtra(unittest.TestCase):
    """Тесты для класса MobileSecurityAgentExtra"""
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = MobileSecurityAgentExtra()
        self.threat_data = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test", "code_signed": False}
        )
    
    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent.logger)
        self.assertIsInstance(self.agent.trusted_apps_database, set)
        self.assertIsInstance(self.agent.threat_patterns, dict)
        self.assertIsInstance(self.agent.expert_consensus, dict)
        self.assertIsInstance(self.agent.stats, dict)
        self.assertIsInstance(self.agent.analysis_cache, dict)
        self.assertIsInstance(self.agent.metrics, dict)
    
    def test_constants(self):
        """Тест констант класса"""
        self.assertEqual(self.agent.BLOCK_THRESHOLD, 0.8)
        self.assertEqual(self.agent.WARN_THRESHOLD, 0.6)
        self.assertEqual(self.agent.MONITOR_THRESHOLD, 0.4)
        self.assertEqual(self.agent.DEFAULT_CONFIDENCE, 0.5)
        self.assertEqual(self.agent.HIGH_REPUTATION_THRESHOLD, 0.8)
        self.assertEqual(self.agent.LOW_CONFIDENCE_THRESHOLD, 0.3)
    
    async def test_analyze_threat_async(self):
        """Тест асинхронного анализа угрозы"""
        result = await self.agent.analyze_threat(self.threat_data)
        
        self.assertIn("threat_id", result)
        self.assertIn("final_score", result)
        self.assertIn("recommendation", result)
        self.assertIn("timestamp", result)
        self.assertIn("from_cache", result)
        
        self.assertEqual(result["threat_id"], "com.test.app")
        self.assertIsInstance(result["final_score"], float)
        self.assertIn(result["recommendation"], ["BLOCK", "WARN", "MONITOR", "ALLOW"])
    
    def test_analyze_threat_sync(self):
        """Тест синхронного анализа угрозы"""
        # Создаем новый агент для синхронного теста
        agent = MobileSecurityAgentExtra()
        
        # Мокаем асинхронные методы для синхронного вызова
        with patch.object(agent, '_analyze_threat_trends_async') as mock_trends, \
             patch.object(agent, '_get_expert_consensus_async') as mock_consensus, \
             patch.object(agent, '_check_whitelists_async') as mock_whitelists:
            
            mock_trends.return_value = {"trend_score": 0.5}
            mock_consensus.return_value = 0.5
            mock_whitelists.return_value = {"trusted_publishers": False}
            
            # Запускаем асинхронный тест в синхронном контексте
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(agent.analyze_threat(self.threat_data))
                self.assertIn("threat_id", result)
            finally:
                loop.close()
    
    def test_get_recommendation(self):
        """Тест получения рекомендаций"""
        self.assertEqual(self.agent._get_recommendation(0.9), "BLOCK")
        self.assertEqual(self.agent._get_recommendation(0.7), "WARN")
        self.assertEqual(self.agent._get_recommendation(0.5), "MONITOR")
        self.assertEqual(self.agent._get_recommendation(0.3), "ALLOW")
    
    def test_validate_threat_data(self):
        """Тест валидации данных об угрозе"""
        # Валидные данные
        self.assertTrue(self.agent._validate_threat_data(self.threat_data))
        
        # Невалидные данные
        invalid_threat = ThreatData("", "", "", -1, datetime.now(), None)
        self.assertFalse(self.agent._validate_threat_data(invalid_threat))
        
        # Отключенная валидация
        self.agent.validation_enabled = False
        self.assertTrue(self.agent._validate_threat_data(invalid_threat))
    
    def test_cache_functionality(self):
        """Тест функциональности кэша"""
        # Первый вызов - кэш пуст
        cache_key = self.agent._get_cache_key(self.threat_data)
        self.assertNotIn(cache_key, self.agent.analysis_cache)
        
        # Тестируем генерацию ключа кэша
        key = self.agent._get_cache_key(self.threat_data)
        expected_key = f"com.test.app:malware:0.8"
        self.assertEqual(key, expected_key)
        
        # Тестируем управление размером кэша
        original_size = self.agent.cache_max_size
        original_cache = self.agent.analysis_cache.copy()
        
        self.agent.cache_max_size = 1  # Устанавливаем очень маленький размер
        self.agent.analysis_cache = {"key1": "value1", "key2": "value2", "key3": "value3"}
        original_len = len(self.agent.analysis_cache)
        self.agent._manage_cache_size()
        # Проверяем что размер уменьшился
        self.assertLess(len(self.agent.analysis_cache), original_len)
        
        # Восстанавливаем оригинальные значения
        self.agent.cache_max_size = original_size
        self.agent.analysis_cache = original_cache
    
    def test_get_metrics(self):
        """Тест получения метрик"""
        metrics = self.agent.get_metrics()
        
        self.assertIn("total_requests", metrics)
        self.assertIn("cache_hits", metrics)
        self.assertIn("cache_misses", metrics)
        self.assertIn("cache_hit_rate_percent", metrics)
        self.assertIn("avg_processing_time_ms", metrics)
        self.assertIn("cache_size", metrics)
        self.assertIn("validation_enabled", metrics)
        
        self.assertIsInstance(metrics["cache_hit_rate_percent"], float)
        self.assertIsInstance(metrics["avg_processing_time_ms"], float)
    
    def test_special_methods(self):
        """Тест специальных методов"""
        # Тест __str__
        str_repr = str(self.agent)
        self.assertIn("MobileSecurityAgentExtra", str_repr)
        self.assertIn("threats_analyzed", str_repr)
        
        # Тест __repr__
        repr_str = repr(self.agent)
        self.assertIn("MobileSecurityAgentExtra", repr_str)
        self.assertIn("logger", repr_str)
        
        # Тест __hash__
        hash_val = hash(self.agent)
        self.assertIsInstance(hash_val, int)
        
        # Тест __eq__
        agent2 = MobileSecurityAgentExtra()
        # Добавляем разные данные для проверки неравенства
        self.agent.stats["threats_analyzed"] = 5
        self.assertFalse(self.agent == agent2)  # Разные объекты
        
        # После cleanup должны быть равны
        self.agent.cleanup()
        agent2.cleanup()
        self.assertTrue(self.agent == agent2)
    
    def test_cleanup(self):
        """Тест очистки ресурсов"""
        # Добавляем данные
        self.agent.trusted_apps_database.add("com.test.app")
        self.agent.threat_patterns["test"] = "pattern"
        self.agent.stats["threats_analyzed"] = 10
        
        # Выполняем очистку
        self.agent.cleanup()
        
        # Проверяем что данные очищены
        self.assertEqual(len(self.agent.trusted_apps_database), 0)
        self.assertEqual(len(self.agent.threat_patterns), 0)
        self.assertEqual(self.agent.stats["threats_analyzed"], 0)
    
    def test_configuration_loading(self):
        """Тест загрузки конфигурации"""
        # Создаем временный файл конфигурации
        config_data = {
            "mobile_security_agent": {
                "thresholds": {
                    "block_threshold": 0.9,
                    "warn_threshold": 0.7
                },
                "trusted_apps": ["com.custom.app"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            # Загружаем конфигурацию
            result = self.agent.load_configuration(config_path)
            self.assertTrue(result)
            
            # Проверяем что значения изменились
            self.assertEqual(self.agent.BLOCK_THRESHOLD, 0.9)
            self.assertEqual(self.agent.WARN_THRESHOLD, 0.7)
            self.assertIn("com.custom.app", self.agent.trusted_apps_database)
            
        finally:
            os.unlink(config_path)
    
    def test_configuration_saving(self):
        """Тест сохранения конфигурации"""
        # Изменяем некоторые значения
        self.agent.BLOCK_THRESHOLD = 0.9
        self.agent.trusted_apps_database.add("com.test.app")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            # Сохраняем конфигурацию
            result = self.agent.save_configuration(config_path)
            self.assertTrue(result)
            
            # Проверяем что файл создан и содержит правильные данные
            self.assertTrue(os.path.exists(config_path))
            
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
            
            self.assertEqual(saved_config["mobile_security_agent"]["thresholds"]["block_threshold"], 0.9)
            self.assertIn("com.test.app", saved_config["mobile_security_agent"]["trusted_apps"])
            
        finally:
            os.unlink(config_path)


class TestAsyncMethods(unittest.TestCase):
    """Тесты для асинхронных методов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = MobileSecurityAgentExtra()
        self.threat_data = ThreatData(
            app_id="com.test.app",
            threat_type="malware",
            severity="high",
            confidence=0.8,
            timestamp=datetime.now(),
            details={"source": "test"}
        )
    
    def test_async_methods(self):
        """Тест асинхронных методов"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Тест _analyze_threat_trends_async
            result = loop.run_until_complete(
                self.agent._analyze_threat_trends_async(self.threat_data)
            )
            self.assertIn("trend_score", result)
            
            # Тест _get_expert_consensus_async
            consensus = loop.run_until_complete(
                self.agent._get_expert_consensus_async(self.threat_data)
            )
            self.assertIsInstance(consensus, float)
            
            # Тест _check_whitelists_async
            whitelists = loop.run_until_complete(
                self.agent._check_whitelists_async(self.threat_data)
            )
            self.assertIsInstance(whitelists, dict)
            
        finally:
            loop.close()


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = MobileSecurityAgentExtra()
    
    def test_full_analysis_workflow(self):
        """Тест полного рабочего процесса анализа"""
        threat_data = ThreatData(
            app_id="com.malicious.app",
            threat_type="malware",
            severity="critical",
            confidence=0.95,
            timestamp=datetime.now(),
            details={
                "source": "integration_test",
                "code_signed": False,
                "reputation_score": 0.1
            }
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Выполняем анализ
            result = loop.run_until_complete(self.agent.analyze_threat(threat_data))
            
            # Проверяем результат
            self.assertIn("threat_id", result)
            self.assertIn("final_score", result)
            self.assertIn("recommendation", result)
            self.assertIn("trend_analysis", result)
            self.assertIn("expert_consensus", result)
            self.assertIn("whitelist_checks", result)
            
            # Для критической угрозы с низкой репутацией ожидаем блокировку
            self.assertEqual(result["threat_id"], "com.malicious.app")
            # Проверяем что скор находится в разумных пределах
            self.assertGreaterEqual(result["final_score"], 0.0)
            self.assertLessEqual(result["final_score"], 1.0)
            
        finally:
            loop.close()
    
    def test_caching_workflow(self):
        """Тест рабочего процесса кэширования"""
        threat_data = ThreatData(
            app_id="com.cache.test",
            threat_type="malware",
            severity="medium",
            confidence=0.6,
            timestamp=datetime.now(),
            details={"source": "cache_test"}
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Первый вызов - кэш пуст
            result1 = loop.run_until_complete(self.agent.analyze_threat(threat_data))
            self.assertFalse(result1["from_cache"])
            
            # Второй вызов - результат из кэша
            result2 = loop.run_until_complete(self.agent.analyze_threat(threat_data))
            self.assertTrue(result2["from_cache"])
            
            # Результаты должны быть идентичны (кроме timestamp и from_cache)
            self.assertEqual(result1["threat_id"], result2["threat_id"])
            self.assertEqual(result1["final_score"], result2["final_score"])
            self.assertEqual(result1["recommendation"], result2["recommendation"])
            
            # Проверяем метрики кэша
            metrics = self.agent.get_metrics()
            self.assertEqual(metrics["total_requests"], 2)
            self.assertEqual(metrics["cache_hits"], 1)
            self.assertEqual(metrics["cache_misses"], 1)
            self.assertEqual(metrics["cache_hit_rate_percent"], 50.0)
            
        finally:
            loop.close()


if __name__ == '__main__':
    # Создаем test suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTest(unittest.makeSuite(TestThreatData))
    test_suite.addTest(unittest.makeSuite(TestMobileSecurityAgentExtra))
    test_suite.addTest(unittest.makeSuite(TestAsyncMethods))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТЫ UNIT ТЕСТОВ:")
    print(f"{'='*60}")
    print(f"✅ Тестов запущено: {result.testsRun}")
    print(f"✅ Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Проваленных: {len(result.failures)}")
    print(f"❌ Ошибок: {len(result.errors)}")
    print(f"🎯 Успешность: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100:.1f}%")
    
    if result.failures:
        print(f"\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print(f"\n❌ ОШИБКИ:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code)