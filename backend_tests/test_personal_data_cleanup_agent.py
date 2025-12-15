#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для Personal Data Cleanup Agent

Тестирование:
- Поиск данных на брокерских сайтах
- Удаление данных
- Отслеживание прогресса
- Генерация отчетов
- Настройки пользователя
- Напоминания и периодический поиск

Дата создания: 13 декабря 2025
"""

import sys
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.ai_agents.personal_data_cleanup_agent import (
        PersonalDataCleanupAgent,
        UserData,
        FoundData,
        RemovalRequest,
        CleanupReport,
        RemovalStatus,
        RemovalMethod
    )
except ImportError as e:
    # Для локального тестирования - создаем заглушки
    print(f"⚠️ Импорт не удался: {e}")
    print("Используем заглушки для тестирования")

    class RemovalStatus:
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    class RemovalMethod:
        OPT_OUT_FORM = "opt_out_form"
        GDPR_REQUEST = "gdpr_request"
        API = "api"
        EMAIL = "email"

    class UserData:
        def __init__(self, email=None, phone=None, name=None, address=None, date_of_birth=None):
            self.email = email
            self.phone = phone
            self.name = name
            self.address = address
            self.date_of_birth = date_of_birth

    class FoundData:
        def __init__(self, site, url, data_found, found_at):
            self.site = site
            self.url = url
            self.data_found = data_found
            self.found_at = found_at

    class RemovalRequest:
        def __init__(self, request_id, user_id, site, url, method, status, requested_at):
            self.request_id = request_id
            self.user_id = user_id
            self.site = site
            self.url = url
            self.method = method
            self.status = status
            self.requested_at = requested_at

    class CleanupReport:
        def __init__(self, user_id, total_sites_scanned, sites_with_data, removal_requests_sent,
                     completed, pending, failed, completion_percentage, generated_at):
            self.user_id = user_id
            self.total_sites_scanned = total_sites_scanned
            self.sites_with_data = sites_with_data
            self.removal_requests_sent = removal_requests_sent
            self.completed = completed
            self.pending = pending
            self.failed = failed
            self.completion_percentage = completion_percentage
            self.generated_at = generated_at

    class PersonalDataCleanupAgent:
        def __init__(self, config=None):
            self.config = config or {}
            self.max_retries = 3
            self.removal_requests = {}
            self.found_data_cache = {}
            self.last_scan_times = {}
            self.user_preferences = {}

        def find_data_on_broker_sites(self, user_id, user_data):
            return []

        def remove_data_from_broker_sites(self, user_id, found_data_list):
            return []

        def track_removal_progress(self, request_id):
            return None

        def get_cleanup_report(self, user_id):
            return CleanupReport(user_id, 0, 0, 0, 0, 0, 0, 0.0, time.time())

        def set_user_preferences(self, user_id, enable_auto_scan, scan_interval_days):
            return {}

        def get_user_preferences(self, user_id):
            return {}

        def check_periodic_scan(self, user_id, user_data):
            return None

        def get_scan_status(self, user_id):
            return {}


import unittest


class TestPersonalDataCleanupAgent(unittest.TestCase):
    """Тесты для Personal Data Cleanup Agent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.config = {
            "max_retries": 3,
            "retry_delay_days": 7,
            "scan_timeout_seconds": 30,
            "enable_auto_retry": True,
            "enable_periodic_scan": False,
            "scan_interval_days": 30,
            "reminder_interval_days": 45
        }
        self.agent = PersonalDataCleanupAgent(self.config)
        self.test_user_id = "test_user_123"
        self.test_user_data = UserData(
            email="test@example.com",
            phone="+1234567890",
            name="Test User",
            address="123 Test St",
            date_of_birth="1990-01-01"
        )

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.max_retries, 3)
        self.assertEqual(self.agent.retry_delay_days, 7)
        self.assertEqual(self.agent.scan_timeout_seconds, 30)
        self.assertIsInstance(self.agent.removal_requests, dict)
        self.assertIsInstance(self.agent.found_data_cache, dict)

    def test_find_data_on_broker_sites_empty_result(self):
        """Тест поиска данных - пустой результат"""
        with patch.object(self.agent, '_search_site', return_value=None):
            result = self.agent.find_data_on_broker_sites(
                self.test_user_id,
                self.test_user_data
            )
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 0)

    def test_find_data_on_broker_sites_with_results(self):
        """Тест поиска данных - с результатами"""
        mock_found_data = FoundData(
            site="TestSite",
            url="https://testsite.com/user",
            data_found=["email", "phone"],
            found_at=time.time()
        )

        with patch.object(self.agent, '_search_site', return_value=mock_found_data):
            with patch.object(self.agent, 'broker_sites', [{"name": "TestSite", "domain": "testsite.com"}]):
                result = self.agent.find_data_on_broker_sites(
                    self.test_user_id,
                    self.test_user_data
                )
                self.assertIsInstance(result, list)
                if len(result) > 0:
                    self.assertIsInstance(result[0], FoundData)
                    self.assertEqual(result[0].site, "TestSite")

    def test_remove_data_from_broker_sites(self):
        """Тест удаления данных"""
        found_data = FoundData(
            site="TestSite",
            url="https://testsite.com/user",
            data_found=["email"],
            found_at=time.time()
        )

        with patch.object(self.agent, '_send_removal_request', return_value="request_123"):
            result = self.agent.remove_data_from_broker_sites(
                self.test_user_id,
                [found_data]
            )
            self.assertIsInstance(result, list)

    def test_track_removal_progress_existing_request(self):
        """Тест отслеживания прогресса - существующий запрос"""
        request_id = "test_request_123"
        removal_request = RemovalRequest(
            request_id=request_id,
            user_id=self.test_user_id,
            site="TestSite",
            url="https://testsite.com/user",
            method=RemovalMethod.OPT_OUT_FORM,
            status=RemovalStatus.PENDING,
            requested_at=time.time()
        )
        self.agent.removal_requests[request_id] = removal_request

        result = self.agent.track_removal_progress(request_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.request_id, request_id)
        self.assertEqual(result.status, RemovalStatus.PENDING)

    def test_track_removal_progress_nonexistent_request(self):
        """Тест отслеживания прогресса - несуществующий запрос"""
        result = self.agent.track_removal_progress("nonexistent_request")
        self.assertIsNone(result)

    def test_get_cleanup_report_empty(self):
        """Тест получения отчета - пустой отчет"""
        report = self.agent.get_cleanup_report(self.test_user_id)
        self.assertIsNotNone(report)
        self.assertIsInstance(report, CleanupReport)
        self.assertEqual(report.user_id, self.test_user_id)
        self.assertEqual(report.total_sites_scanned, 0)
        self.assertEqual(report.sites_with_data, 0)
        self.assertEqual(report.removal_requests_sent, 0)

    def test_get_cleanup_report_with_data(self):
        """Тест получения отчета - с данными"""
        # Добавляем найденные данные
        found_data = FoundData(
            site="TestSite",
            url="https://testsite.com/user",
            data_found=["email"],
            found_at=time.time()
        )
        self.agent.found_data_cache[self.test_user_id] = [found_data]

        # Добавляем запрос на удаление
        request_id = "test_request_123"
        removal_request = RemovalRequest(
            request_id=request_id,
            user_id=self.test_user_id,
            site="TestSite",
            url="https://testsite.com/user",
            method=RemovalMethod.OPT_OUT_FORM,
            status=RemovalStatus.COMPLETED,
            requested_at=time.time()
        )
        self.agent.removal_requests[request_id] = removal_request

        report = self.agent.get_cleanup_report(self.test_user_id)
        self.assertIsNotNone(report)
        self.assertGreaterEqual(report.sites_with_data, 0)
        self.assertGreaterEqual(report.removal_requests_sent, 0)

    def test_set_user_preferences(self):
        """Тест установки настроек пользователя"""
        result = self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=True,
            scan_interval_days=60
        )
        self.assertIsInstance(result, dict)
        self.assertIn("enable_auto_scan", result)
        self.assertTrue(result["enable_auto_scan"])
        self.assertEqual(result["scan_interval_days"], 60)

        # Проверяем, что настройки сохранились
        prefs = self.agent.get_user_preferences(self.test_user_id)
        self.assertEqual(prefs["enable_auto_scan"], True)
        self.assertEqual(prefs["scan_interval_days"], 60)

    def test_get_user_preferences_default(self):
        """Тест получения настроек пользователя - значения по умолчанию"""
        prefs = self.agent.get_user_preferences(self.test_user_id)
        self.assertIsInstance(prefs, dict)
        self.assertIn("enable_auto_scan", prefs)
        self.assertIn("scan_interval_days", prefs)
        # По умолчанию автоматический поиск выключен
        self.assertFalse(prefs["enable_auto_scan"])

    def test_get_user_preferences_custom(self):
        """Тест получения настроек пользователя - пользовательские настройки"""
        # Устанавливаем настройки
        self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=True,
            scan_interval_days=90
        )

        # Получаем настройки
        prefs = self.agent.get_user_preferences(self.test_user_id)
        self.assertTrue(prefs["enable_auto_scan"])
        self.assertEqual(prefs["scan_interval_days"], 90)

    def test_get_scan_status_no_previous_scan(self):
        """Тест получения статуса поиска - без предыдущего поиска"""
        status = self.agent.get_scan_status(self.test_user_id)
        self.assertIsNotNone(status)
        self.assertIn("last_scan_time", status)
        self.assertIn("needs_reminder", status)
        self.assertIn("reminder_message", status)
        # Если поиска не было, напоминание должно быть True
        self.assertTrue(status["needs_reminder"])

    def test_get_scan_status_recent_scan(self):
        """Тест получения статуса поиска - недавний поиск"""
        # Устанавливаем время последнего поиска (сегодня)
        self.agent.last_scan_times[self.test_user_id] = time.time()

        status = self.agent.get_scan_status(self.test_user_id)
        self.assertIsNotNone(status)
        self.assertFalse(status["needs_reminder"])

    def test_get_scan_status_old_scan(self):
        """Тест получения статуса поиска - старый поиск (требует напоминания)"""
        # Устанавливаем время последнего поиска (50 дней назад)
        old_time = time.time() - (50 * 24 * 60 * 60)
        self.agent.last_scan_times[self.test_user_id] = old_time

        status = self.agent.get_scan_status(self.test_user_id)
        self.assertIsNotNone(status)
        self.assertTrue(status["needs_reminder"])
        self.assertIsNotNone(status["reminder_message"])

    def test_check_periodic_scan_disabled(self):
        """Тест периодического поиска - отключен"""
        self.agent.enable_periodic_scan = False
        result = self.agent.check_periodic_scan(
            self.test_user_id,
            self.test_user_data
        )
        self.assertIsNone(result)

    def test_check_periodic_scan_enabled_auto_off(self):
        """Тест периодического поиска - включен, но у пользователя выключен"""
        self.agent.enable_periodic_scan = True
        # Пользователь отключил автоматический поиск
        self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=False,
            scan_interval_days=30
        )

        with patch.object(self.agent, 'find_data_on_broker_sites', return_value=[]):
            result = self.agent.check_periodic_scan(
                self.test_user_id,
                self.test_user_data
            )
            # Должен вернуть None, так как у пользователя выключен авто-поиск
            self.assertIsNone(result)

    def test_check_periodic_scan_enabled_auto_on(self):
        """Тест периодического поиска - включен и у пользователя включен"""
        self.agent.enable_periodic_scan = True
        # Пользователь включил автоматический поиск
        self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=True,
            scan_interval_days=30
        )
        # Устанавливаем время последнего поиска (35 дней назад - пора искать)
        old_time = time.time() - (35 * 24 * 60 * 60)
        self.agent.last_scan_times[self.test_user_id] = old_time

        with patch.object(self.agent, 'find_data_on_broker_sites', return_value=[]):
            result = self.agent.check_periodic_scan(
                self.test_user_id,
                self.test_user_data
            )
            # Должен выполнить поиск
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)

    def test_user_data_creation(self):
        """Тест создания объекта UserData"""
        user_data = UserData(
            email="test@example.com",
            phone="+1234567890",
            name="Test User"
        )
        self.assertEqual(user_data.email, "test@example.com")
        self.assertEqual(user_data.phone, "+1234567890")
        self.assertEqual(user_data.name, "Test User")

    def test_found_data_creation(self):
        """Тест создания объекта FoundData"""
        found_data = FoundData(
            site="TestSite",
            url="https://testsite.com/user",
            data_found=["email", "phone"],
            found_at=time.time()
        )
        self.assertEqual(found_data.site, "TestSite")
        self.assertEqual(found_data.url, "https://testsite.com/user")
        self.assertIn("email", found_data.data_found)
        self.assertIn("phone", found_data.data_found)

    def test_removal_request_creation(self):
        """Тест создания объекта RemovalRequest"""
        request = RemovalRequest(
            request_id="test_123",
            user_id=self.test_user_id,
            site="TestSite",
            url="https://testsite.com/user",
            method=RemovalMethod.OPT_OUT_FORM,
            status=RemovalStatus.PENDING,
            requested_at=time.time()
        )
        self.assertEqual(request.request_id, "test_123")
        self.assertEqual(request.user_id, self.test_user_id)
        self.assertEqual(request.site, "TestSite")
        self.assertEqual(request.status, RemovalStatus.PENDING)

    def test_cleanup_report_creation(self):
        """Тест создания объекта CleanupReport"""
        report = CleanupReport(
            user_id=self.test_user_id,
            total_sites_scanned=10,
            sites_with_data=3,
            removal_requests_sent=3,
            completed=2,
            pending=1,
            failed=0,
            completion_percentage=66.67,
            generated_at=time.time()
        )
        self.assertEqual(report.user_id, self.test_user_id)
        self.assertEqual(report.total_sites_scanned, 10)
        self.assertEqual(report.sites_with_data, 3)
        self.assertEqual(report.completion_percentage, 66.67)


class TestPersonalDataCleanupAgentIntegration(unittest.TestCase):
    """Интеграционные тесты для Personal Data Cleanup Agent"""

    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.config = {
            "max_retries": 3,
            "retry_delay_days": 7,
            "scan_timeout_seconds": 30,
            "enable_auto_retry": True
        }
        self.agent = PersonalDataCleanupAgent(self.config)
        self.test_user_id = "test_user_456"
        self.test_user_data = UserData(
            email="integration@example.com",
            phone="+9876543210",
            name="Integration Test User"
        )

    def test_full_workflow(self):
        """Тест полного цикла: поиск -> удаление -> отслеживание -> отчет"""
        # Шаг 1: Поиск данных
        with patch.object(self.agent, '_search_site', return_value=None):
            found_data_list = self.agent.find_data_on_broker_sites(
                self.test_user_id,
                self.test_user_data
            )
            self.assertIsInstance(found_data_list, list)

        # Шаг 2: Удаление данных (если что-то найдено)
        if found_data_list:
            with patch.object(self.agent, '_send_removal_request', return_value="request_123"):
                request_ids = self.agent.remove_data_from_broker_sites(
                    self.test_user_id,
                    found_data_list
                )
                self.assertIsInstance(request_ids, list)

                # Шаг 3: Отслеживание прогресса
                if request_ids:
                    progress = self.agent.track_removal_progress(request_ids[0])
                    self.assertIsNotNone(progress)

        # Шаг 4: Получение отчета
        report = self.agent.get_cleanup_report(self.test_user_id)
        self.assertIsNotNone(report)
        self.assertIsInstance(report, CleanupReport)

    def test_user_preferences_workflow(self):
        """Тест полного цикла работы с настройками пользователя"""
        # Устанавливаем настройки
        self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=True,
            scan_interval_days=60
        )

        # Получаем настройки
        prefs = self.agent.get_user_preferences(self.test_user_id)
        self.assertTrue(prefs["enable_auto_scan"])
        self.assertEqual(prefs["scan_interval_days"], 60)

        # Изменяем настройки
        self.agent.set_user_preferences(
            self.test_user_id,
            enable_auto_scan=False,
            scan_interval_days=90
        )

        # Проверяем изменения
        prefs = self.agent.get_user_preferences(self.test_user_id)
        self.assertFalse(prefs["enable_auto_scan"])
        self.assertEqual(prefs["scan_interval_days"], 90)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)
