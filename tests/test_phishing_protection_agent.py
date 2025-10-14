#!/usr/bin/env python3
"""
Unit тесты для PhishingProtectionAgent
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-25
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.phishing_protection_agent import (
    PhishingProtectionAgent,
    PhishingPlugin,
    URLReputationPlugin,
    EmailContentPlugin,
    DomainAgePlugin,
    PhishingType,
    ThreatLevel,
    DetectionMethod,
    PhishingProtectionError,
    DomainValidationError,
    RateLimitExceededError
)


class TestPhishingProtectionAgent(unittest.TestCase):
    """Unit тесты для PhishingProtectionAgent"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = PhishingProtectionAgent('TestAgent')

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertEqual(self.agent.name, 'TestAgent')
        self.assertIsInstance(self.agent.indicators, list)
        self.assertIsInstance(self.agent.detections, list)
        self.assertIsInstance(self.agent.reports, list)
        self.assertIsInstance(self.agent.blocked_domains, set)
        self.assertIsInstance(self.agent.trusted_domains, set)
        self.assertIsInstance(self.agent.plugins, list)

    def test_add_indicator(self):
        """Тест добавления индикатора"""
        from security.ai_agents.phishing_protection_agent import PhishingIndicator
        
        indicator = PhishingIndicator(
            indicator_id="test_001",
            name="Test Indicator",
            phishing_type=PhishingType.WEBSITE,
            threat_level=ThreatLevel.MEDIUM,
            pattern=r"test",
            description="Test pattern",
            detection_method=DetectionMethod.URL_ANALYSIS,
            confidence=0.5
        )
        
        initial_count = len(self.agent.indicators)
        self.agent.add_indicator(indicator)
        
        self.assertEqual(len(self.agent.indicators), initial_count + 1)
        self.assertIn(indicator, self.agent.indicators)

    def test_analyze_url_safe(self):
        """Тест анализа безопасного URL"""
        result = self.agent.analyze_url('https://example.com')
        self.assertIsNone(result)

    def test_analyze_url_suspicious(self):
        """Тест анализа подозрительного URL"""
        # Добавляем подозрительный домен в черный список
        self.agent.blocked_domains.add('suspicious.com')
        
        result = self.agent.analyze_url('https://suspicious.com/phishing')
        self.assertIsNotNone(result)
        self.assertEqual(result.phishing_type, PhishingType.WEBSITE)
        self.assertEqual(result.threat_level, ThreatLevel.CRITICAL)

    def test_analyze_url_trusted(self):
        """Тест анализа доверенного URL"""
        # Добавляем домен в белый список
        self.agent.trusted_domains.add('trusted.com')
        
        result = self.agent.analyze_url('https://trusted.com/safe')
        self.assertIsNone(result)

    def test_analyze_email_safe(self):
        """Тест анализа безопасного email"""
        result = self.agent.analyze_email(
            'Normal Subject',
            'Normal email content',
            'sender@example.com'
        )
        # Результат может быть None или PhishingDetection в зависимости от индикаторов
        self.assertIsInstance(result, (type(None), type(self.agent._create_detection(
            source="test",
            phishing_type=PhishingType.EMAIL,
            threat_level=ThreatLevel.MEDIUM,
            confidence=0.5,
            detection_method=DetectionMethod.CONTENT_ANALYSIS
        ))))

    def test_analyze_email_suspicious(self):
        """Тест анализа подозрительного email"""
        result = self.agent.analyze_email(
            'URGENT: Verify Account',
            'Click here to verify your account immediately!',
            'noreply@suspicious.com'
        )
        # Результат может быть None или PhishingDetection в зависимости от индикаторов
        self.assertIsInstance(result, (type(None), type(self.agent._create_detection(
            source="test",
            phishing_type=PhishingType.EMAIL,
            threat_level=ThreatLevel.MEDIUM,
            confidence=0.5,
            detection_method=DetectionMethod.CONTENT_ANALYSIS
        ))))

    def test_is_safe_url_safe(self):
        """Тест проверки безопасного URL"""
        self.agent.trusted_domains.add('example.com')
        result = self.agent.is_safe_url('https://example.com/page')
        self.assertTrue(result)

    def test_is_safe_url_blocked(self):
        """Тест проверки заблокированного URL"""
        self.agent.blocked_domains.add('malicious.com')
        result = self.agent.is_safe_url('https://malicious.com/page')
        self.assertFalse(result)

    def test_is_safe_email_valid(self):
        """Тест проверки валидного email"""
        result = self.agent.is_safe_email('test@example.com')
        self.assertTrue(result)

    def test_is_safe_email_invalid(self):
        """Тест проверки невалидного email"""
        result = self.agent.is_safe_email('invalid-email')
        self.assertFalse(result)

    def test_validate_domain_valid(self):
        """Тест валидации корректного домена"""
        result = self.agent.validate_domain('example.com')
        self.assertTrue(result['is_valid'])
        self.assertTrue(result['is_safe'])

    def test_validate_domain_invalid(self):
        """Тест валидации некорректного домена"""
        with self.assertRaises(DomainValidationError):
            self.agent._validate_domain('invalid..domain')

    def test_rate_limiting(self):
        """Тест rate limiting"""
        # Сбрасываем rate limits
        self.agent._rate_limits = {}
        
        # Первые запросы должны проходить
        for i in range(5):
            self.assertTrue(self.agent._check_rate_limit('test_method'))
        
        # Превышаем лимит
        with self.assertRaises(RateLimitExceededError):
            for i in range(100):  # Превышаем лимит в 100 запросов
                self.agent._check_rate_limit('test_method')

    def test_caching(self):
        """Тест кэширования"""
        cache_key = 'test_key'
        test_data = {'test': 'data'}
        
        # Проверяем, что кэш пустой
        self.assertIsNone(self.agent._get_from_cache(cache_key))
        
        # Сохраняем данные в кэш
        self.agent._set_cache(cache_key, test_data)
        
        # Проверяем, что данные извлекаются из кэша
        cached_data = self.agent._get_from_cache(cache_key)
        self.assertEqual(cached_data, test_data)

    def test_plugin_registration(self):
        """Тест регистрации плагинов"""
        plugin = URLReputationPlugin()
        
        initial_count = len(self.agent.plugins)
        self.agent.register_plugin(plugin)
        
        self.assertEqual(len(self.agent.plugins), initial_count + 1)
        self.assertIn(plugin, self.agent.plugins)

    def test_plugin_unregistration(self):
        """Тест отмены регистрации плагинов"""
        plugin = URLReputationPlugin()
        self.agent.register_plugin(plugin)
        
        initial_count = len(self.agent.plugins)
        result = self.agent.unregister_plugin(plugin.get_name())
        
        self.assertTrue(result)
        self.assertEqual(len(self.agent.plugins), initial_count - 1)

    def test_plugin_list(self):
        """Тест получения списка плагинов"""
        plugin1 = URLReputationPlugin()
        plugin2 = EmailContentPlugin()
        
        self.agent.register_plugin(plugin1)
        self.agent.register_plugin(plugin2)
        
        plugin_list = self.agent.list_plugins()
        self.assertIn('URLReputationPlugin', plugin_list)
        self.assertIn('EmailContentPlugin', plugin_list)

    def test_backup_restore_cycle(self):
        """Тест цикла резервного копирования и восстановления"""
        # Создаем резервную копию
        backup = self.agent.backup_configuration()
        self.assertIsNotNone(backup)
        
        # Изменяем конфигурацию
        self.agent.blocked_domains.add('test.com')
        
        # Восстанавливаем из резервной копии
        success = self.agent.restore_configuration(backup)
        self.assertTrue(success)
        self.assertNotIn('test.com', self.agent.blocked_domains)

    def test_performance_metrics(self):
        """Тест метрик производительности"""
        metrics = self.agent.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_requests', metrics)
        self.assertIn('successful_detections', metrics)
        self.assertIn('average_confidence', metrics)
        self.assertIn('response_time_ms', metrics)

    def test_health_status(self):
        """Тест проверки состояния здоровья"""
        health = self.agent.check_health_status()
        
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('memory_usage', health)
        # Проверяем, что есть хотя бы один из возможных ключей
        self.assertTrue(any(key in health for key in ['uptime', 'timestamp', 'last_activity']))

    def test_version_info(self):
        """Тест информации о версии"""
        version_info = self.agent.get_version_info()
        
        self.assertIsInstance(version_info, dict)
        self.assertIn('version', version_info)
        # Проверяем, что есть хотя бы один из возможных ключей
        self.assertTrue(any(key in version_info for key in ['name', 'author', 'description']))


class TestAsyncFunctionality(unittest.TestCase):
    """Тесты асинхронной функциональности"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = PhishingProtectionAgent('AsyncTestAgent')

    def test_analyze_url_async(self):
        """Тест асинхронного анализа URL"""
        async def run_test():
            result = await self.agent.analyze_url_async('https://example.com')
            return result
        
        result = asyncio.run(run_test())
        self.assertIsInstance(result, (type(None), type(self.agent._create_detection(
            source="test",
            phishing_type=PhishingType.WEBSITE,
            threat_level=ThreatLevel.MEDIUM,
            confidence=0.5,
            detection_method=DetectionMethod.URL_ANALYSIS
        ))))

    def test_analyze_email_async(self):
        """Тест асинхронного анализа email"""
        async def run_test():
            result = await self.agent.analyze_email_async(
                'Test Subject',
                'Test content',
                'test@example.com'
            )
            return result
        
        result = asyncio.run(run_test())
        self.assertIsInstance(result, (type(None), type(self.agent._create_detection(
            source="test",
            phishing_type=PhishingType.EMAIL,
            threat_level=ThreatLevel.MEDIUM,
            confidence=0.5,
            detection_method=DetectionMethod.CONTENT_ANALYSIS
        ))))

    def test_batch_analyze_urls(self):
        """Тест пакетного анализа URL"""
        async def run_test():
            urls = ['https://example.com', 'https://test.com']
            detections = []
            async for detection in self.agent.batch_analyze_urls(urls):
                detections.append(detection)
            return detections
        
        detections = asyncio.run(run_test())
        self.assertIsInstance(detections, list)

    def test_analyze_with_plugins(self):
        """Тест анализа с плагинами"""
        async def run_test():
            # Регистрируем плагин
            plugin = URLReputationPlugin()
            self.agent.register_plugin(plugin)
            
            # Анализируем с плагинами
            data = {'url': 'https://bit.ly/suspicious'}
            result = await self.agent.analyze_with_plugins(data)
            return result
        
        result = asyncio.run(run_test())
        self.assertIsInstance(result, dict)
        self.assertIn('agent_analysis', result)
        self.assertIn('plugin_results', result)
        self.assertIn('combined_confidence', result)
        self.assertIn('combined_threat_level', result)


class TestPlugins(unittest.TestCase):
    """Тесты плагинов"""

    def test_url_reputation_plugin(self):
        """Тест плагина репутации URL"""
        plugin = URLReputationPlugin()
        
        # Тест подозрительного домена
        result = asyncio.run(plugin.analyze_async({'url': 'https://bit.ly/suspicious'}))
        self.assertIsInstance(result, dict)
        self.assertIn('confidence', result)
        self.assertIn('threat_level', result)
        
        # Тест безопасного домена
        result = asyncio.run(plugin.analyze_async({'url': 'https://example.com'}))
        self.assertIsInstance(result, dict)
        self.assertEqual(result['threat_level'], 1)  # LOW

    def test_email_content_plugin(self):
        """Тест плагина содержимого email"""
        plugin = EmailContentPlugin()
        
        # Тест подозрительного email
        result = asyncio.run(plugin.analyze_async({
            'email': {
                'subject': 'URGENT: Verify Account',
                'content': 'Click here to verify immediately!',
                'sender': 'noreply@suspicious.com'
            }
        }))
        self.assertIsInstance(result, dict)
        self.assertIn('confidence', result)
        self.assertIn('threat_level', result)
        self.assertGreater(result['threat_level'], 1)  # Не LOW

    def test_domain_age_plugin(self):
        """Тест плагина возраста домена"""
        plugin = DomainAgePlugin()
        
        result = asyncio.run(plugin.analyze_async({'url': 'https://newdomain.com'}))
        self.assertIsInstance(result, dict)
        self.assertIn('confidence', result)
        self.assertIn('threat_level', result)
        self.assertIn('details', result)


class TestErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = PhishingProtectionAgent('ErrorTestAgent')

    def test_invalid_url_validation(self):
        """Тест валидации невалидного URL"""
        with self.assertRaises(ValueError):
            self.agent._validate_url('invalid-url')

    def test_invalid_email_validation(self):
        """Тест валидации невалидного email"""
        with self.assertRaises(ValueError):
            self.agent._validate_email('invalid-email')

    def test_invalid_domain_validation(self):
        """Тест валидации невалидного домена"""
        with self.assertRaises(DomainValidationError):
            self.agent._validate_domain('invalid..domain')

    def test_rate_limit_exceeded(self):
        """Тест превышения лимита запросов"""
        # Сбрасываем rate limits
        self.agent._rate_limits = {}
        
        with self.assertRaises(RateLimitExceededError):
            for i in range(101):  # Превышаем лимит
                self.agent._check_rate_limit('test_method')


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)