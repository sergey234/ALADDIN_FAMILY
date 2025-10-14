#!/usr/bin/env python3
"""
Unit тесты для критических исправлений NetworkMonitoringService.

Тестирует:
1. Исправленные методы с корректными параметрами
2. Обработку ошибок и исключений
3. Валидацию параметров
4. Функциональность всех компонентов
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import asyncio
from datetime import datetime

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.active.network_monitoring import (
    NetworkMonitoringService,
    NetworkMonitoringConfig,
    PerformanceMetrics,
    NetworkConnection,
    NetworkAnomaly,
    NetworkRule,
    NetworkStatistics,
    NetworkType,
    TrafficType,
    ThreatLevel,
    MonitoringAction,
    InvalidIPAddressError,
    InvalidPortError,
    InvalidUserAgeError,
    ConnectionTimeoutError,
    FamilyMemberNotFoundError
)


class TestNetworkMonitoringCriticalFixes(unittest.TestCase):
    """Тесты критических исправлений NetworkMonitoringService."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.service = NetworkMonitoringService('TestService')
        self.config = NetworkMonitoringConfig()
        self.metrics = PerformanceMetrics()

    def test_add_family_member_with_defaults(self):
        """Тест метода add_family_member с параметрами по умолчанию."""
        # Тест с минимальными параметрами
        result = self.service.add_family_member('test_user')
        self.assertTrue(result)
        
        # Тест с полными параметрами
        result = self.service.add_family_member('test_user2', 'Test User', 25, 'parent')
        self.assertTrue(result)
        
        # Тест с некорректным user_id
        with self.assertRaises(ValueError):
            self.service.add_family_member('')

    def test_clear_cache_method(self):
        """Тест метода clear_cache."""
        result = self.service.clear_cache()
        self.assertTrue(result)

    def test_get_parental_controls_with_user_id(self):
        """Тест метода get_parental_controls с user_id."""
        # Сначала добавляем пользователя
        self.service.add_family_member('test_user')
        
        result = self.service.get_parental_controls('test_user')
        self.assertIsInstance(result, dict)
        self.assertIn('user_id', result)

    def test_get_time_limits_with_user_id(self):
        """Тест метода get_time_limits с user_id."""
        # Сначала добавляем пользователя
        self.service.add_family_member('test_user')
        
        result = self.service.get_time_limits('test_user')
        self.assertIsInstance(result, dict)
        self.assertIn('user_id', result)

    def test_validation_errors_raise_exceptions(self):
        """Тест что валидация выбрасывает исключения."""
        # Тест некорректного IP
        with self.assertRaises(InvalidIPAddressError):
            self.service._validate_ip_address('invalid_ip')
        
        # Тест некорректного порта
        with self.assertRaises(InvalidPortError):
            self.service._validate_port(99999)
        
        # Тест некорректного возраста
        with self.assertRaises(InvalidUserAgeError):
            self.service._validate_user_age(200)

    def test_monitor_connection_validation(self):
        """Тест валидации в monitor_connection."""
        # Тест с некорректным IP
        with self.assertRaises(InvalidIPAddressError):
            self.service.monitor_connection(
                'invalid_ip', '8.8.8.8', 12345, 80, 'TCP'
            )
        
        # Тест с некорректным портом
        with self.assertRaises(InvalidPortError):
            self.service.monitor_connection(
                '192.168.1.100', '8.8.8.8', 99999, 80, 'TCP'
            )
        
        # Тест с некорректным возрастом
        with self.assertRaises(InvalidUserAgeError):
            self.service.monitor_connection(
                '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP',
                user_age=200
            )

    def test_detect_network_anomaly_validation(self):
        """Тест валидации в detect_network_anomaly."""
        # Создаем валидное соединение
        conn = self.service.monitor_connection(
            '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP'
        )
        
        # Тест с None соединением
        with self.assertRaises(ValueError):
            self.service.detect_network_anomaly(None, 'test', 'test', 0.5)
        
        # Тест с некорректной уверенностью
        with self.assertRaises(ValueError):
            self.service.detect_network_anomaly(conn, 'test', 'test', 1.5)

    def test_async_methods_work_correctly(self):
        """Тест async методов."""
        async def test_async():
            # Тест monitor_connection_async
            conn = await self.service.monitor_connection_async(
                '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP'
            )
            self.assertIsInstance(conn, NetworkConnection)
            
            # Тест detect_network_anomaly_async
            anomaly = await self.service.detect_network_anomaly_async(
                conn, 'test_anomaly', 'Test description', 0.7
            )
            self.assertIsInstance(anomaly, NetworkAnomaly)
            
            # Тест get_network_statistics_async
            stats = await self.service.get_network_statistics_async()
            self.assertIsInstance(stats, NetworkStatistics)
        
        # Запускаем async тест
        asyncio.run(test_async())

    def test_performance_metrics_tracking(self):
        """Тест отслеживания метрик производительности."""
        # Получаем метрики
        metrics = self.service.get_performance_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('method_times', metrics)
        self.assertIn('error_rates', metrics)
        self.assertIn('cache_hits', metrics)
        self.assertIn('cache_misses', metrics)

    def test_configuration_management(self):
        """Тест управления конфигурацией."""
        # Получаем конфигурацию
        config = self.service.get_config()
        self.assertIsInstance(config, NetworkMonitoringConfig)
        
        # Обновляем конфигурацию
        new_config = NetworkMonitoringConfig(max_connections=5000)
        result = self.service.update_config(new_config)
        self.assertTrue(result)
        
        # Проверяем обновление
        updated_config = self.service.get_config()
        self.assertEqual(updated_config.max_connections, 5000)

    def test_caching_functionality(self):
        """Тест функциональности кэширования."""
        # Очищаем кэш
        result = self.service.clear_cache()
        self.assertTrue(result)
        
        # Тестируем кэшированные методы
        network_type = self.service._get_cached_network_type('192.168.1.100')
        self.assertIsInstance(network_type, NetworkType)
        
        traffic_type = self.service._get_cached_traffic_type('example.com', 'TCP')
        self.assertIsInstance(traffic_type, TrafficType)

    def test_error_handling_improvements(self):
        """Тест улучшений обработки ошибок."""
        # Тест с некорректными параметрами
        with self.assertRaises(ValueError):
            self.service.add_family_member('')
        
        # Тест с None параметрами - должен пройти (None разрешен)
        result = self.service._validate_user_id(None)
        self.assertTrue(result)
        
        # Тест с некорректными типами
        with self.assertRaises(InvalidUserAgeError):
            self.service._validate_user_age('not_a_number')

    def test_family_protection_features(self):
        """Тест функций семейной защиты."""
        # Добавляем члена семьи
        self.service.add_family_member('child_user', 'Child', 12, 'child')
        
        # Тест родительского контроля
        controls = self.service.get_parental_controls('child_user')
        self.assertIsInstance(controls, dict)
        
        # Тест временных ограничений
        limits = self.service.get_time_limits('child_user')
        self.assertIsInstance(limits, dict)
        
        # Тест блокировки сайтов
        result = self.service.block_website('inappropriate.com', 'Test blocking')
        self.assertTrue(result)
        
        # Тест получения заблокированных сайтов
        blocked = self.service.get_blocked_websites()
        self.assertIsInstance(blocked, set)

    def test_network_monitoring_comprehensive(self):
        """Комплексный тест мониторинга сети."""
        # Создаем соединение
        conn = self.service.monitor_connection(
            '192.168.1.100', '8.8.8.8', 12345, 80, 'TCP',
            user_id='test_user', user_age=25
        )
        self.assertIsInstance(conn, NetworkConnection)
        
        # Создаем аномалию
        anomaly = self.service.detect_network_anomaly(
            conn, 'suspicious_traffic', 'High data transfer', 0.8
        )
        self.assertIsInstance(anomaly, NetworkAnomaly)
        
        # Получаем статистику
        stats = self.service.get_network_statistics()
        self.assertIsInstance(stats, NetworkStatistics)
        self.assertGreater(stats.total_connections, 0)
        
        # Получаем семейный статус
        family_status = self.service.get_family_network_status()
        self.assertIsInstance(family_status, dict)

    def test_all_classes_instantiation(self):
        """Тест создания всех классов."""
        # NetworkMonitoringService
        service = NetworkMonitoringService('TestService')
        self.assertIsInstance(service, NetworkMonitoringService)
        
        # NetworkMonitoringConfig
        config = NetworkMonitoringConfig()
        self.assertIsInstance(config, NetworkMonitoringConfig)
        
        # PerformanceMetrics
        metrics = PerformanceMetrics()
        self.assertIsInstance(metrics, PerformanceMetrics)
        
        # NetworkConnection
        conn = NetworkConnection(
            connection_id='test_conn',
            source_ip='192.168.1.100',
            destination_ip='8.8.8.8',
            source_port=12345,
            destination_port=80,
            protocol='TCP',
            network_type=NetworkType.WIFI,
            traffic_type=TrafficType.WEB,
            bytes_sent=1024,
            bytes_received=2048,
            start_time=datetime.now(),
            user_id='test_user',
            device_id='test_device',
            metadata={'test': True}
        )
        self.assertIsInstance(conn, NetworkConnection)
        
        # NetworkAnomaly
        anomaly = NetworkAnomaly(
            anomaly_id='test_anomaly',
            connection_id='test_conn',
            anomaly_type='suspicious_traffic',
            threat_level=ThreatLevel.MEDIUM,
            description='Test anomaly',
            timestamp=datetime.now(),
            source_ip='192.168.1.100',
            destination_ip='8.8.8.8',
            confidence=0.7,
            metadata={'test': True}
        )
        self.assertIsInstance(anomaly, NetworkAnomaly)
        
        # NetworkRule
        rule = NetworkRule(
            rule_id='test_rule',
            name='Test Rule',
            description='Test rule for monitoring',
            conditions={'test': True},
            actions=[MonitoringAction.LOG],
            enabled=True,
            family_specific=False,
            age_group=None
        )
        self.assertIsInstance(rule, NetworkRule)
        
        # NetworkStatistics
        stats = NetworkStatistics(
            total_connections=10,
            total_bytes_sent=10240,
            total_bytes_received=20480,
            active_connections=5,
            blocked_connections=2,
            anomalies_detected=1,
            by_traffic_type={'web': 5, 'gaming': 3, 'social': 2},
            by_network_type={'wifi': 8, 'ethernet': 2},
            by_threat_level={'low': 8, 'medium': 2},
            top_destinations=[('8.8.8.8', 5), ('1.1.1.1', 3)],
            top_sources=[('192.168.1.100', 8), ('192.168.1.101', 2)]
        )
        self.assertIsInstance(stats, NetworkStatistics)


if __name__ == '__main__':
    # Настройка тестового окружения
    unittest.main(verbosity=2)