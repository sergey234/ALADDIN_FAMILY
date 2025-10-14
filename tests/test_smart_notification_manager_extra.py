#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit тесты для SmartNotificationManagerExtra
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from smart_notification_manager_extra import (
    SmartNotificationManagerExtra,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
    NotificationStatus,
    NotificationMetrics
)


class TestSmartNotificationManagerExtra(unittest.TestCase):
    """Тесты для SmartNotificationManagerExtra"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = SmartNotificationManagerExtra()
        self.test_notification = {
            'id': 'test_001',
            'type': 'info',
            'title': 'Тестовое уведомление',
            'message': 'Это тестовое сообщение',
            'user_id': 'test_user_001'
        }
        self.test_user_id = 'test_user_001'

    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsInstance(self.manager, SmartNotificationManagerExtra)
        self.assertIsNotNone(self.manager.logger)
        self.assertIsInstance(self.manager.metrics, NotificationMetrics)
        self.assertIsInstance(self.manager.notification_history, list)
        self.assertIsInstance(self.manager.user_preferences, dict)

    def test_send_notification(self):
        """Тест отправки уведомления"""
        result = self.manager.send_notification(self.test_notification)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_validate_notification(self):
        """Тест валидации уведомления"""
        # Корректное уведомление
        result = self.manager.validate_notification(self.test_notification)
        self.assertTrue(result)
        
        # Некорректное уведомление
        invalid_notification = {'id': 'test'}
        result = self.manager.validate_notification(invalid_notification)
        self.assertFalse(result)

    def test_format_notification(self):
        """Тест форматирования уведомления"""
        result = self.manager.format_notification(self.test_notification)
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        self.assertIn('title', result)

    def test_get_user_preferences(self):
        """Тест получения предпочтений пользователя"""
        result = self.manager.get_user_preferences(self.test_user_id)
        self.assertIsInstance(result, dict)
        
        # Тест без параметров (используем _get_user_preferences)
        result = self.manager._get_user_preferences()
        self.assertIsInstance(result, dict)

    def test_update_user_preferences(self):
        """Тест обновления предпочтений пользователя"""
        preferences = {'theme': 'dark', 'notifications': True}
        result = self.manager.update_user_preferences(self.test_user_id, preferences)
        self.assertTrue(result)

    def test_get_notification_history(self):
        """Тест получения истории уведомлений"""
        result = self.manager.get_notification_history(self.test_user_id)
        self.assertIsInstance(result, list)

    def test_clear_notification_history(self):
        """Тест очистки истории уведомлений"""
        result = self.manager.clear_notification_history(self.test_user_id)
        self.assertTrue(result)

    def test_get_notification_statistics(self):
        """Тест получения статистики уведомлений"""
        result = self.manager.get_notification_statistics()
        self.assertIsInstance(result, dict)
        self.assertIn('total_notifications', result)

    def test_reset_statistics(self):
        """Тест сброса статистики"""
        result = self.manager.reset_statistics()
        self.assertTrue(result)

    def test_is_notification_enabled(self):
        """Тест проверки включенности уведомлений"""
        result = self.manager.is_notification_enabled(self.test_user_id)
        self.assertIsInstance(result, bool)

    def test_enable_notification(self):
        """Тест включения уведомлений"""
        result = self.manager.enable_notification(self.test_user_id)
        self.assertTrue(result)

    def test_disable_notification(self):
        """Тест отключения уведомлений"""
        result = self.manager.disable_notification(self.test_user_id)
        self.assertTrue(result)

    def test_get_notification_settings(self):
        """Тест получения настроек уведомлений"""
        # С user_id
        result = self.manager.get_notification_settings(self.test_user_id)
        self.assertIsInstance(result, dict)
        
        # Без параметров
        result = self.manager.get_notification_settings()
        self.assertIsInstance(result, dict)

    def test_update_notification_settings(self):
        """Тест обновления настроек уведомлений"""
        settings = {'max_notifications': 100, 'timeout': 30}
        result = self.manager.update_notification_settings(self.test_user_id, settings)
        self.assertTrue(result)

    def test_schedule_notification(self):
        """Тест планирования уведомления"""
        scheduled_time = '2024-01-01T12:00:00'
        result = self.manager.schedule_notification(self.test_notification, scheduled_time)
        self.assertTrue(result)

    def test_cancel_notification(self):
        """Тест отмены уведомления"""
        result = self.manager.cancel_notification('scheduled_001')
        # Метод может вернуть False если уведомление не найдено, это нормально
        self.assertIsInstance(result, bool)

    def test_get_scheduled_notifications(self):
        """Тест получения запланированных уведомлений"""
        result = self.manager.get_scheduled_notifications()
        self.assertIsInstance(result, list)

    def test_process_notification_queue(self):
        """Тест обработки очереди уведомлений"""
        result = self.manager.process_notification_queue()
        self.assertIsInstance(result, int)

    def test_get_notification_templates(self):
        """Тест получения шаблонов уведомлений"""
        result = self.manager.get_notification_templates()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_create_notification_template(self):
        """Тест создания шаблона уведомления"""
        template = {'id': 'test_template', 'name': 'Тестовый шаблон'}
        result = self.manager.create_notification_template(template)
        self.assertTrue(result)

    def test_update_notification_template(self):
        """Тест обновления шаблона уведомления"""
        template = {'id': 'test_template', 'name': 'Обновленный шаблон'}
        result = self.manager.update_notification_template('test_template', template)
        self.assertTrue(result)
        
        # Без template
        result = self.manager.update_notification_template('test_template')
        self.assertTrue(result)

    def test_delete_notification_template(self):
        """Тест удаления шаблона уведомления"""
        result = self.manager.delete_notification_template('test_template')
        self.assertTrue(result)

    def test_get_comprehensive_metrics(self):
        """Тест получения комплексных метрик"""
        result = self.manager.get_comprehensive_metrics()
        self.assertIsInstance(result, dict)
        self.assertIn('delivered_notifications', result)
        self.assertIn('success_rate', result)

    def test_cleanup(self):
        """Тест очистки"""
        result = self.manager.cleanup()
        self.assertIsNone(result)

    def test_optimize_user_engagement(self):
        """Тест оптимизации вовлеченности пользователя"""
        # С user_id
        result = self.manager.optimize_user_engagement(self.test_user_id)
        self.assertIsInstance(result, dict)
        self.assertIn('user_id', result)
        
        # Без параметров
        result = self.manager.optimize_user_engagement()
        self.assertIsInstance(result, dict)

    def test_smart_route_notification(self):
        """Тест умной маршрутизации уведомлений"""
        # С параметрами
        result = self.manager.smart_route_notification(self.test_notification, self.test_user_id)
        self.assertIsInstance(result, dict)
        self.assertIn('optimal_channel', result)
        
        # Без параметров
        result = self.manager.smart_route_notification()
        self.assertIsInstance(result, dict)

    def test_private_methods(self):
        """Тест private методов"""
        # Тестируем private методы
        result = self.manager._analyze_engagement_patterns()
        self.assertIsInstance(result, dict)
        
        result = self.manager._analyze_notification_context()
        self.assertIsInstance(result, dict)
        
        result = self.manager._assess_urgency()
        self.assertIsInstance(result, str)
        
        result = self.manager._classify_content_type()
        self.assertIsInstance(result, str)
        
        result = self.manager._assess_time_sensitivity()
        self.assertIsInstance(result, str)
        
        result = self.manager._select_optimal_channel()
        self.assertIsInstance(result, str)
        
        result = self.manager._select_optimal_time()
        self.assertIsInstance(result, str)
        
        result = self.manager._generate_routing_recommendations()
        self.assertIsInstance(result, list)
        
        result = self.manager._generate_engagement_recommendations()
        self.assertIsInstance(result, list)
        
        result = self.manager._get_user_preferences()
        self.assertIsInstance(result, dict)
        
        result = self.manager._init_smart_features()
        self.assertTrue(result)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с None параметрами
        result = self.manager.send_notification(None)
        self.assertFalse(result)
        
        result = self.manager.validate_notification(None)
        self.assertFalse(result)
        
        result = self.manager.format_notification(None)
        self.assertIsNone(result)

    def test_enum_classes(self):
        """Тест Enum классов"""
        # NotificationType
        self.assertEqual(NotificationType.INFO.value, 'info')
        self.assertEqual(NotificationType.WARNING.value, 'warning')
        
        # NotificationPriority
        self.assertEqual(NotificationPriority.LOW.value, 'low')
        self.assertEqual(NotificationPriority.HIGH.value, 'high')
        
        # NotificationChannel
        self.assertEqual(NotificationChannel.PUSH.value, 'push')
        self.assertEqual(NotificationChannel.EMAIL.value, 'email')
        
        # NotificationStatus
        self.assertEqual(NotificationStatus.PENDING.value, 'pending')
        self.assertEqual(NotificationStatus.SENT.value, 'sent')

    def test_notification_metrics(self):
        """Тест NotificationMetrics"""
        metrics = NotificationMetrics()
        self.assertEqual(metrics.total_notifications, 0)
        self.assertEqual(metrics.delivered_notifications, 0)
        self.assertEqual(metrics.read_notifications, 0)
        self.assertEqual(metrics.failed_notifications, 0)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = SmartNotificationManagerExtra()

    def test_notification_workflow(self):
        """Тест полного workflow уведомления"""
        notification = {
            'id': 'workflow_test',
            'type': 'info',
            'title': 'Workflow Test',
            'message': 'Testing complete workflow',
            'user_id': 'workflow_user'
        }
        
        # 1. Валидация
        is_valid = self.manager.validate_notification(notification)
        self.assertTrue(is_valid)
        
        # 2. Форматирование
        formatted = self.manager.format_notification(notification)
        self.assertIsInstance(formatted, dict)
        
        # 3. Отправка
        sent = self.manager.send_notification(notification)
        self.assertTrue(sent)
        
        # 4. Проверка истории
        history = self.manager.get_notification_history('workflow_user')
        self.assertIsInstance(history, list)

    def test_user_preferences_workflow(self):
        """Тест workflow предпочтений пользователя"""
        user_id = 'prefs_user'
        preferences = {'theme': 'dark', 'notifications': True}
        
        # 1. Обновление предпочтений
        updated = self.manager.update_user_preferences(user_id, preferences)
        self.assertTrue(updated)
        
        # 2. Получение предпочтений
        prefs = self.manager.get_user_preferences(user_id)
        self.assertIsInstance(prefs, dict)
        
        # 3. Включение уведомлений
        enabled = self.manager.enable_notification(user_id)
        self.assertTrue(enabled)
        
        # 4. Проверка статуса
        is_enabled = self.manager.is_notification_enabled(user_id)
        self.assertIsInstance(is_enabled, bool)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)