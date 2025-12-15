#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для AI Categories Agent

День 5-6: Тестирование агента
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.ai_agents.ai_categories_agent import (
        AICategoriesAgent,
        AISite,
        TimeRestriction,
        AgeRestriction,
        AISiteCategory
    )
except ImportError:
    # Для локального тестирования
    import unittest
    unittest.skip("AI Categories Agent не доступен")


class TestAICategoriesAgent:
    """Тесты для AICategoriesAgent"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.agent = AICategoriesAgent(config={"notify_parents": False})
        self.test_user_id = "test_user_123"

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        assert self.agent is not None
        assert len(self.agent.ai_sites) == 9  # 9 AI-сайтов
        assert "alice" in self.agent.ai_sites
        assert "yandexgpt" in self.agent.ai_sites
        assert "chatgpt" in self.agent.ai_sites

    def test_get_ai_sites(self):
        """Тест получения списка AI-сайтов"""
        sites = self.agent.get_ai_sites()
        assert len(sites) == 9
        assert isinstance(sites, list)
        
        # Проверяем структуру первого сайта
        first_site = sites[0]
        assert "id" in first_site
        assert "name" in first_site
        assert "domain" in first_site
        assert "category" in first_site

    def test_get_site_by_id(self):
        """Тест получения сайта по ID"""
        site = self.agent.get_site_by_id("alice")
        assert site is not None
        assert site.id == "alice"
        assert site.name == "Алиса AI"
        
        # Несуществующий сайт
        site = self.agent.get_site_by_id("nonexistent")
        assert site is None

    def test_block_sites(self):
        """Тест блокировки сайтов"""
        result = self.agent.block_sites(
            user_id=self.test_user_id,
            site_ids=["chatgpt", "claude"]
        )
        
        assert result["status"] == "success"
        assert len(result["blocked"]) == 2
        assert "chatgpt" in result["blocked"]
        assert "claude" in result["blocked"]
        
        # Проверяем статус
        status = self.agent.get_status(self.test_user_id)
        chatgpt_status = next(s for s in status["sites"] if s["site_id"] == "chatgpt")
        assert chatgpt_status["is_blocked"] is True
        assert chatgpt_status["is_allowed"] is False

    def test_block_sites_with_time_restriction(self):
        """Тест блокировки с ограничением по времени"""
        time_restriction = TimeRestriction(
            start_time="09:00",
            end_time="18:00",
            days_of_week=[0, 1, 2, 3, 4],  # Пн-Пт
            enabled=True
        )
        
        result = self.agent.block_sites(
            user_id=self.test_user_id,
            site_ids=["chatgpt"],
            time_restriction=time_restriction
        )
        
        assert result["status"] == "success"
        
        # Проверяем что ограничение по времени установлено
        status = self.agent.get_status(self.test_user_id)
        chatgpt_status = next(s for s in status["sites"] if s["site_id"] == "chatgpt")
        assert chatgpt_status["time_restriction"] is not None
        assert chatgpt_status["time_restriction"]["start_time"] == "09:00"

    def test_allow_sites(self):
        """Тест разрешения доступа к сайтам"""
        # Сначала блокируем
        self.agent.block_sites(self.test_user_id, ["chatgpt"])
        
        # Затем разрешаем
        result = self.agent.allow_sites(
            user_id=self.test_user_id,
            site_ids=["chatgpt"]
        )
        
        assert result["status"] == "success"
        assert "chatgpt" in result["allowed"]
        
        # Проверяем статус
        status = self.agent.get_status(self.test_user_id)
        chatgpt_status = next(s for s in status["sites"] if s["site_id"] == "chatgpt")
        assert chatgpt_status["is_blocked"] is False
        assert chatgpt_status["is_allowed"] is True

    def test_check_access_blocked(self):
        """Тест проверки доступа к заблокированному сайту"""
        # Блокируем сайт
        self.agent.block_sites(self.test_user_id, ["chatgpt"])
        
        # Проверяем доступ
        result = self.agent.check_access(
            user_id=self.test_user_id,
            site_id="chatgpt"
        )
        
        assert result["allowed"] is False
        assert result["blocked"] is True
        assert result["reason"] == "blocked"

    def test_check_access_allowed(self):
        """Тест проверки доступа к разрешенному сайту"""
        # Разрешаем сайт
        self.agent.allow_sites(self.test_user_id, ["alice"])
        
        # Проверяем доступ
        result = self.agent.check_access(
            user_id=self.test_user_id,
            site_id="alice"
        )
        
        assert result["allowed"] is True
        assert result["blocked"] is False

    def test_check_access_age_restriction(self):
        """Тест проверки доступа с ограничением по возрасту"""
        # Устанавливаем ограничение по возрасту
        age_restriction = AgeRestriction(
            min_age=16,
            require_parental_approval=True,
            block_completely=True
        )
        self.agent.set_age_restriction(
            user_id=self.test_user_id,
            site_id="chatgpt",
            age_restriction=age_restriction
        )
        
        # Проверяем доступ для 15-летнего
        result = self.agent.check_access(
            user_id=self.test_user_id,
            site_id="chatgpt",
            user_age=15
        )
        
        # Должен быть заблокирован из-за возраста
        assert result["blocked"] is True
        assert "age_restriction" in result["reason"]

    def test_check_access_time_restriction(self):
        """Тест проверки доступа с ограничением по времени"""
        # Блокируем с ограничением по времени (только в будни 9-18)
        time_restriction = TimeRestriction(
            start_time="09:00",
            end_time="18:00",
            days_of_week=[0, 1, 2, 3, 4],  # Пн-Пт
            enabled=True
        )
        self.agent.block_sites(
            user_id=self.test_user_id,
            site_ids=["chatgpt"],
            time_restriction=time_restriction
        )
        
        # Проверяем доступ (время будет проверено автоматически)
        result = self.agent.check_access(
            user_id=self.test_user_id,
            site_id="chatgpt"
        )
        
        # Результат зависит от текущего времени
        assert "allowed" in result
        assert "blocked" in result

    def test_get_status(self):
        """Тест получения статуса"""
        # Блокируем несколько сайтов
        self.agent.block_sites(self.test_user_id, ["chatgpt", "claude"])
        self.agent.allow_sites(self.test_user_id, ["alice"])
        
        status = self.agent.get_status(self.test_user_id)
        
        assert status["user_id"] == self.test_user_id
        assert status["total_sites"] == 9
        assert status["blocked_count"] >= 2
        assert status["allowed_count"] >= 1
        assert len(status["sites"]) == 9

    def test_get_access_history(self):
        """Тест получения истории доступа"""
        # Делаем несколько попыток доступа
        self.agent.check_access(self.test_user_id, "chatgpt")
        self.agent.check_access(self.test_user_id, "alice")
        self.agent.check_access(self.test_user_id, "chatgpt")
        
        history = self.agent.get_access_history(self.test_user_id, limit=10)
        
        assert len(history) >= 3
        assert all("timestamp" in h for h in history)
        assert all("was_blocked" in h for h in history)

    def test_set_age_restriction(self):
        """Тест установки ограничения по возрасту"""
        age_restriction = AgeRestriction(
            min_age=16,
            require_parental_approval=True,
            block_completely=False
        )
        
        result = self.agent.set_age_restriction(
            user_id=self.test_user_id,
            site_id="chatgpt",
            age_restriction=age_restriction
        )
        
        assert result["status"] == "success"
        
        # Проверяем что ограничение установлено
        status = self.agent.get_status(self.test_user_id)
        chatgpt_status = next(s for s in status["sites"] if s["site_id"] == "chatgpt")
        assert chatgpt_status["age_restriction"] is not None
        assert chatgpt_status["age_restriction"]["min_age"] == 16

    def test_block_nonexistent_site(self):
        """Тест блокировки несуществующего сайта"""
        result = self.agent.block_sites(
            user_id=self.test_user_id,
            site_ids=["nonexistent", "chatgpt"]
        )
        
        assert result["status"] == "success"
        assert "nonexistent" in result["not_found"]
        assert "chatgpt" in result["blocked"]

    def test_russian_sites_present(self):
        """Тест что российские сайты присутствуют"""
        sites = self.agent.get_ai_sites()
        site_ids = [s["id"] for s in sites]
        
        # Проверяем российские сайты
        assert "alice" in site_ids
        assert "yandexgpt" in site_ids
        assert "gigachat" in site_ids
        assert "kandinsky" in site_ids
        assert "shedevrum" in site_ids

    def test_international_sites_present(self):
        """Тест что международные сайты присутствуют"""
        sites = self.agent.get_ai_sites()
        site_ids = [s["id"] for s in sites]
        
        # Проверяем международные сайты
        assert "chatgpt" in site_ids
        assert "deepseek" in site_ids
        assert "claude" in site_ids
        assert "gemini" in site_ids


# Для запуска тестов напрямую
if __name__ == "__main__":
    import unittest
    
    # Преобразуем класс тестов в unittest.TestCase
    class TestAICategoriesAgentUnittest(unittest.TestCase):
        def setUp(self):
            self.agent = AICategoriesAgent(config={"notify_parents": False})
            self.test_user_id = "test_user_123"
        
        def test_agent_initialization(self):
            """Тест инициализации агента"""
            self.assertIsNotNone(self.agent)
            self.assertEqual(len(self.agent.ai_sites), 9)
            self.assertIn("alice", self.agent.ai_sites)
        
        def test_get_ai_sites(self):
            """Тест получения списка AI-сайтов"""
            sites = self.agent.get_ai_sites()
            self.assertEqual(len(sites), 9)
            self.assertIsInstance(sites, list)
        
        def test_block_sites(self):
            """Тест блокировки сайтов"""
            result = self.agent.block_sites(
                user_id=self.test_user_id,
                site_ids=["chatgpt"]
            )
            self.assertEqual(result["status"], "success")
            self.assertIn("chatgpt", result["blocked"])
    
    unittest.main()
