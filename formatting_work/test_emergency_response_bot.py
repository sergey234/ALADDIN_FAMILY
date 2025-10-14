#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для EmergencyResponseBot

Тестирует основную функциональность бота экстренного реагирования
"""

import unittest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулю
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.bots.emergency_response_bot import (
    EmergencyResponseBot,
    EmergencyResponse,
    EmergencyType,
    EmergencySeverity,
    EmergencyContactInfo
)


class TestEmergencyResponseBot(unittest.TestCase):
    """Тесты для EmergencyResponseBot"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        # Мокаем внешние зависимости
        with patch('security.bots.emergency_response_bot.redis.Redis'), \
             patch('security.bots.emergency_response_bot.sqlalchemy.create_engine'), \
             patch('security.bots.emergency_response_bot.sqlalchemy.orm.sessionmaker'):
            
            self.bot = EmergencyResponseBot("TestBot")
            self.bot.logger = Mock()
            self.bot.redis_client = Mock()
            self.bot.db_engine = Mock()
            self.bot.db_session = Mock()
    
    def test_initialization(self):
        """Тест инициализации бота"""
        self.assertEqual(self.bot.name, "TestBot")
        self.assertFalse(self.bot.running)
        self.assertEqual(len(self.bot.active_incidents), 0)
        self.assertIsInstance(self.bot.config, dict)
        self.assertIsInstance(self.bot.stats, dict)
    
    def test_is_healthy_property(self):
        """Тест свойства is_healthy"""
        # Бот не запущен - должен быть нездоровым
        self.assertFalse(self.bot.is_healthy)
        
        # Имитируем запущенный бот
        self.bot.running = True
        self.bot.emergency_contacts = {"contact1": Mock()}
        self.bot.stats["total_incidents"] = 0
        
        self.assertTrue(self.bot.is_healthy)
    
    def test_uptime_property(self):
        """Тест свойства uptime"""
        # Без времени запуска
        self.assertEqual(self.bot.uptime, 0.0)
        
        # С временем запуска
        self.bot._start_time = datetime.utcnow()
        uptime = self.bot.uptime
        self.assertGreaterEqual(uptime, 0.0)
    
    def test_validate_emergency_data_static(self):
        """Тест статического метода validate_emergency_data"""
        # Валидные данные
        valid_data = {
            'incident_id': 'inc_12345678',
            'emergency_type': 'medical',
            'severity': 'high',
            'location': {'lat': 55.7558, 'lon': 37.6176}
        }
        self.assertTrue(EmergencyResponseBot.validate_emergency_data(valid_data))
        
        # Невалидные данные
        invalid_data = {'incident_id': 'inc_12345678'}
        self.assertFalse(EmergencyResponseBot.validate_emergency_data(invalid_data))
        
        # Пустые данные
        self.assertFalse(EmergencyResponseBot.validate_emergency_data({}))
        
        # None
        self.assertFalse(EmergencyResponseBot.validate_emergency_data(None))
    
    def test_get_supported_emergency_types_class(self):
        """Тест class метода get_supported_emergency_types"""
        types = EmergencyResponseBot.get_supported_emergency_types()
        self.assertIsInstance(types, list)
        self.assertGreater(len(types), 0)
        self.assertIn('medical', types)
        self.assertIn('fire', types)
    
    def test_set_security_level(self):
        """Тест установки уровня безопасности"""
        # Валидный уровень
        result = self.bot.set_security_level('high')
        self.assertTrue(result)
        self.assertEqual(self.bot.config['security_level'], 'high')
        
        # Невалидный уровень
        result = self.bot.set_security_level('invalid')
        self.assertFalse(result)
        
        # None
        result = self.bot.set_security_level(None)
        self.assertFalse(result)
    
    def test_add_security_event(self):
        """Тест добавления события безопасности"""
        # Валидное событие
        result = self.bot.add_security_event('test_event', 'Test description', 'high')
        self.assertTrue(result)
        self.assertEqual(len(self.bot.security_events), 1)
        
        # Пустое описание
        result = self.bot.add_security_event('test_event', '', 'high')
        self.assertFalse(result)
        
        # None
        result = self.bot.add_security_event(None, 'Test', 'high')
        self.assertFalse(result)
    
    def test_detect_threat(self):
        """Тест обнаружения угрозы"""
        # Валидная угроза
        threat_data = {
            'type': 'malware',
            'severity': 'high',
            'source': 'network'
        }
        result = self.bot.detect_threat(threat_data)
        self.assertTrue(result)
        
        # Невалидные данные
        result = self.bot.detect_threat(None)
        self.assertFalse(result)
        
        result = self.bot.detect_threat({'type': 'malware'})  # Без severity
        self.assertFalse(result)
    
    def test_update_metrics(self):
        """Тест обновления метрик"""
        # Валидная метрика
        result = self.bot.update_metrics('response_time', 150.5, {'type': 'avg'})
        self.assertTrue(result)
        self.assertIn('response_time', self.bot.metrics)
        
        # Невалидная метрика
        result = self.bot.update_metrics('', 150.5)
        self.assertFalse(result)
        
        result = self.bot.update_metrics('metric', 'invalid')
        self.assertFalse(result)
    
    def test_get_security_report(self):
        """Тест получения отчета по безопасности"""
        report = self.bot.get_security_report()
        self.assertIsInstance(report, dict)
        self.assertIn('bot_name', report)
        self.assertIn('security_level', report)
        self.assertIn('health_status', report)
        self.assertEqual(report['bot_name'], 'TestBot')
    
    def test_string_representations(self):
        """Тест строковых представлений"""
        # __str__
        str_repr = str(self.bot)
        self.assertIn('TestBot', str_repr)
        self.assertIn('stopped', str_repr)
        
        # __repr__
        repr_str = repr(self.bot)
        self.assertIn('TestBot', repr_str)
        self.assertIn('config_keys', repr_str)
    
    @patch('security.bots.emergency_response_bot.asyncio')
    def test_start_sync(self, mock_asyncio):
        """Тест синхронного запуска"""
        mock_loop = Mock()
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = True
        
        result = self.bot.start_sync()
        self.assertTrue(result)
        mock_asyncio.new_event_loop.assert_called_once()
    
    @patch('security.bots.emergency_response_bot.asyncio')
    def test_stop_sync(self, mock_asyncio):
        """Тест синхронной остановки"""
        mock_loop = Mock()
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = True
        
        result = self.bot.stop_sync()
        self.assertTrue(result)
        mock_asyncio.new_event_loop.assert_called_once()
    
    def test_report_emergency_sync_validation(self):
        """Тест валидации в синхронном отчете"""
        # None
        with self.assertRaises(ValueError):
            self.bot.report_emergency_sync(None)
        
        # Неправильный тип
        with self.assertRaises(TypeError):
            self.bot.report_emergency_sync("invalid")
    
    def test_get_incident_status_sync_validation(self):
        """Тест валидации в синхронном получении статуса"""
        # Пустой ID
        with self.assertRaises(ValueError):
            self.bot.get_incident_status_sync('')
        
        # Неправильный формат ID
        with self.assertRaises(ValueError):
            self.bot.get_incident_status_sync('invalid_id')
    
    def test_resolve_incident_sync_validation(self):
        """Тест валидации в синхронном разрешении инцидента"""
        # Пустой ID
        with self.assertRaises(ValueError):
            self.bot.resolve_incident_sync('')
        
        # Неправильный формат ID
        with self.assertRaises(ValueError):
            self.bot.resolve_incident_sync('invalid_id')


class TestEmergencyResponseModels(unittest.TestCase):
    """Тесты для моделей данных"""
    
    def test_emergency_response_creation(self):
        """Тест создания EmergencyResponse"""
        response = EmergencyResponse(
            incident_id="test-001",
            emergency_type=EmergencyType.MEDICAL,
            severity=EmergencySeverity.HIGH,
            location={'lat': 55.7558, 'lon': 37.6176},
            description="Test emergency",
            reported_by="test_user",
            timestamp=datetime.now()
        )
        
        self.assertEqual(response.incident_id, "test-001")
        self.assertEqual(response.emergency_type, EmergencyType.MEDICAL)
        self.assertEqual(response.severity, EmergencySeverity.HIGH)
        self.assertIsInstance(response.location, dict)
    
    def test_emergency_contact_info_creation(self):
        """Тест создания EmergencyContactInfo"""
        contact = EmergencyContactInfo(
            name="Test Contact",
            phone="+1234567890",
            email="test@example.com",
            service_type="medical",
            priority=1
        )
        
        self.assertEqual(contact.name, "Test Contact")
        self.assertEqual(contact.phone, "+1234567890")
        self.assertEqual(contact.service_type, "medical")
        self.assertTrue(contact.is_active)


if __name__ == '__main__':
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.WARNING)  # Отключаем логи во время тестов
    
    # Запуск тестов
    unittest.main(verbosity=2)