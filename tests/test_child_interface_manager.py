#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для ChildInterfaceManager
"""

import unittest
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'security', 'ai_agents'))

from child_interface_manager import ChildInterfaceManager, ChildAgeCategory, GameLevel, AchievementType, ChildInterfaceMetrics

class TestChildInterfaceManager(unittest.TestCase):
    """Тесты для ChildInterfaceManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.manager = ChildInterfaceManager()
    
    def test_age_category_detection_toddler(self):
        """Тест определения возрастной категории для малышей"""
        user_data = {
            "interaction_pattern": {"touch_heavy": True, "voice_commands": True},
            "preferences": {"simple_games": True},
            "behavior": {"help_seeking": True}
        }
        age_category = self.manager.detect_age_category(user_data)
        self.assertEqual(age_category, ChildAgeCategory.TODDLER)
    
    def test_age_category_detection_child(self):
        """Тест определения возрастной категории для детей"""
        user_data = {
            "interaction_pattern": {"touch_heavy": True, "voice_commands": True, "gesture_control": True},
            "preferences": {"simple_games": True, "educational_content": True},
            "behavior": {"help_seeking": True, "independent_learning": True}
        }
        age_category = self.manager.detect_age_category(user_data)
        self.assertEqual(age_category, ChildAgeCategory.CHILD)
    
    def test_age_category_detection_tween(self):
        """Тест определения возрастной категории для подростков"""
        user_data = {
            "interaction_pattern": {"keyboard_use": True, "gesture_control": True},
            "preferences": {"complex_games": True, "educational_content": True},
            "behavior": {"independent_learning": True}
        }
        age_category = self.manager.detect_age_category(user_data)
        self.assertEqual(age_category, ChildAgeCategory.TWEEN)
    
    def test_age_category_detection_teen(self):
        """Тест определения возрастной категории для подростков 14-18"""
        user_data = {
            "interaction_pattern": {"keyboard_use": True, "gesture_control": True},
            "preferences": {"complex_games": True, "professional_tools": True},
            "behavior": {"independent_learning": True, "team_leadership": True}
        }
        age_category = self.manager.detect_age_category(user_data)
        self.assertEqual(age_category, ChildAgeCategory.TEEN)
    
    def test_age_category_detection_young_adult(self):
        """Тест определения возрастной категории для молодых взрослых"""
        user_data = {
            "interaction_pattern": {"keyboard_use": True, "gesture_control": True, "api_use": True},
            "preferences": {"professional_tools": True, "complex_games": True},
            "behavior": {"team_leadership": True, "independent_learning": True}
        }
        age_category = self.manager.detect_age_category(user_data)
        self.assertEqual(age_category, ChildAgeCategory.YOUNG_ADULT)
    
    def test_get_interface_for_age(self):
        """Тест получения интерфейса для возрастной категории"""
        interface = self.manager.get_interface_for_age(ChildAgeCategory.TODDLER)
        self.assertIsNotNone(interface)
        self.assertIn("design", interface)
        self.assertIn("interaction", interface)
        self.assertIn("safety_rules", interface)
        self.assertIn("games", interface)
    
    def test_get_interface_for_unknown_age(self):
        """Тест получения интерфейса для неизвестной возрастной категории"""
        # Создаем неизвестную категорию
        class UnknownAge(Enum):
            UNKNOWN = "unknown"
        
        interface = self.manager.get_interface_for_age(UnknownAge.UNKNOWN)
        self.assertIsNotNone(interface)
        self.assertEqual(interface["design"]["theme"], "Супергерои")  # Должен вернуть интерфейс для детей
    
    def test_start_learning_module_toddler(self):
        """Тест запуска обучающего модуля для малышей"""
        module = self.manager.start_learning_module(ChildAgeCategory.TODDLER, "interactive")
        self.assertIsNotNone(module)
        self.assertEqual(module["age_category"], "1-6")
        self.assertIn("module", module)
        self.assertIn("interface", module)
        self.assertEqual(module["status"], "started")
    
    def test_start_learning_module_child(self):
        """Тест запуска обучающего модуля для детей"""
        module = self.manager.start_learning_module(ChildAgeCategory.CHILD, "interactive")
        self.assertIsNotNone(module)
        self.assertEqual(module["age_category"], "7-9")
        self.assertIn("module", module)
        self.assertIn("interface", module)
        self.assertEqual(module["status"], "started")
    
    def test_start_learning_module_tween(self):
        """Тест запуска обучающего модуля для подростков"""
        module = self.manager.start_learning_module(ChildAgeCategory.TWEEN, "interactive")
        self.assertIsNotNone(module)
        self.assertEqual(module["age_category"], "10-13")
        self.assertIn("module", module)
        self.assertIn("interface", module)
        self.assertEqual(module["status"], "started")
    
    def test_start_learning_module_teen(self):
        """Тест запуска обучающего модуля для подростков 14-18"""
        module = self.manager.start_learning_module(ChildAgeCategory.TEEN, "interactive")
        self.assertIsNotNone(module)
        self.assertEqual(module["age_category"], "14-18")
        self.assertIn("module", module)
        self.assertIn("interface", module)
        self.assertEqual(module["status"], "started")
    
    def test_start_learning_module_young_adult(self):
        """Тест запуска обучающего модуля для молодых взрослых"""
        module = self.manager.start_learning_module(ChildAgeCategory.YOUNG_ADULT, "interactive")
        self.assertIsNotNone(module)
        self.assertEqual(module["age_category"], "19-24")
        self.assertIn("module", module)
        self.assertIn("interface", module)
        self.assertEqual(module["status"], "started")
    
    def test_complete_quest_daily(self):
        """Тест завершения ежедневного квеста"""
        result = self.manager.complete_quest("user123", "daily", 150)
        self.assertIsNotNone(result)
        self.assertIn("progress", result)
        self.assertIn("achievements", result)
        self.assertIn("new_level", result)
        self.assertIn("rewards", result)
        
        # Проверка прогресса
        self.assertEqual(result["progress"]["user_id"], "user123")
        self.assertEqual(result["progress"]["quest_type"], "daily")
        self.assertEqual(result["progress"]["score"], 150)
        
        # Проверка достижений
        self.assertTrue(len(result["achievements"]) > 0)
    
    def test_complete_quest_weekly(self):
        """Тест завершения еженедельного квеста"""
        result = self.manager.complete_quest("user456", "weekly", 300)
        self.assertIsNotNone(result)
        self.assertIn("progress", result)
        self.assertIn("achievements", result)
        self.assertIn("new_level", result)
        self.assertIn("rewards", result)
    
    def test_complete_quest_monthly(self):
        """Тест завершения месячного квеста"""
        result = self.manager.complete_quest("user789", "monthly", 500)
        self.assertIsNotNone(result)
        self.assertIn("progress", result)
        self.assertIn("achievements", result)
        self.assertIn("new_level", result)
        self.assertIn("rewards", result)
    
    def test_get_family_dashboard_data(self):
        """Тест получения данных семейной панели"""
        data = self.manager.get_family_dashboard_data("family123")
        self.assertIsNotNone(data)
        self.assertEqual(data["family_id"], "family123")
        self.assertIn("children", data)
        self.assertIn("family_quests", data)
        self.assertIn("achievements", data)
        self.assertIn("notifications", data)
    
    def test_send_parent_notification(self):
        """Тест отправки уведомления родителю"""
        notification = self.manager.send_parent_notification("parent123", "Тестовое уведомление", "high")
        self.assertIsNotNone(notification)
        self.assertEqual(notification["parent_id"], "parent123")
        self.assertEqual(notification["message"], "Тестовое уведомление")
        self.assertEqual(notification["priority"], "high")
        self.assertFalse(notification["read"])
    
    def test_send_parent_notification_normal_priority(self):
        """Тест отправки уведомления родителю с обычным приоритетом"""
        notification = self.manager.send_parent_notification("parent456", "Обычное уведомление")
        self.assertIsNotNone(notification)
        self.assertEqual(notification["parent_id"], "parent456")
        self.assertEqual(notification["message"], "Обычное уведомление")
        self.assertEqual(notification["priority"], "normal")
        self.assertFalse(notification["read"])
    
    def test_ai_models_initialization(self):
        """Тест инициализации AI моделей"""
        self.assertIn("age_detector", self.manager.ai_models)
        self.assertIn("learning_optimizer", self.manager.ai_models)
        self.assertIn("safety_analyzer", self.manager.ai_models)
        self.assertIn("engagement_predictor", self.manager.ai_models)
        
        # Проверка структуры AI моделей
        for model_name, model_data in self.manager.ai_models.items():
            self.assertIn("accuracy", model_data)
            self.assertIn("features", model_data)
            self.assertIn("description", model_data)
            self.assertIsInstance(model_data["accuracy"], float)
            self.assertIsInstance(model_data["features"], list)
            self.assertIsInstance(model_data["description"], str)
    
    def test_game_system_initialization(self):
        """Тест инициализации игровой системы"""
        self.assertIn("levels", self.manager.game_system)
        self.assertIn("achievements", self.manager.game_system)
        self.assertIn("quests", self.manager.game_system)
        
        # Проверка уровней
        for level in GameLevel:
            self.assertIn(level, self.manager.game_system["levels"])
            level_data = self.manager.game_system["levels"][level]
            self.assertIn("min_score", level_data)
            self.assertIn("max_score", level_data)
            self.assertIn("rewards", level_data)
        
        # Проверка достижений
        for achievement in AchievementType:
            self.assertIn(achievement, self.manager.game_system["achievements"])
            achievement_data = self.manager.game_system["achievements"][achievement]
            self.assertIn("points", achievement_data)
            self.assertIn("description", achievement_data)
    
    def test_learning_modules_initialization(self):
        """Тест инициализации обучающих модулей"""
        self.assertIn("interactive_lessons", self.manager.learning_modules)
        self.assertIn("quizzes", self.manager.learning_modules)
        self.assertIn("simulations", self.manager.learning_modules)
        
        # Проверка интерактивных уроков
        for age_group in ["toddler", "child", "tween", "teen", "young_adult"]:
            self.assertIn(age_group, self.manager.learning_modules["interactive_lessons"])
            lessons = self.manager.learning_modules["interactive_lessons"][age_group]
            self.assertIsInstance(lessons, list)
            self.assertTrue(len(lessons) > 0)
    
    def test_family_integration_initialization(self):
        """Тест инициализации семейной интеграции"""
        self.assertIn("parental_control", self.manager.family_integration)
        self.assertIn("family_features", self.manager.family_integration)
        self.assertIn("communication", self.manager.family_integration)
        
        # Проверка родительского контроля
        parental_control = self.manager.family_integration["parental_control"]
        self.assertTrue(parental_control["soft_management"])
        self.assertTrue(parental_control["progress_monitoring"])
        self.assertTrue(parental_control["safety_reports"])
        self.assertTrue(parental_control["emergency_functions"])
        
        # Проверка семейных функций
        family_features = self.manager.family_integration["family_features"]
        self.assertTrue(family_features["shared_quests"])
        self.assertTrue(family_features["family_dashboard"])
        self.assertTrue(family_features["group_notifications"])
        self.assertTrue(family_features["unified_settings"])
    
    def test_error_handling_invalid_user_data(self):
        """Тест обработки ошибок с неверными данными пользователя"""
        # Тест с None
        age_category = self.manager.detect_age_category(None)
        self.assertEqual(age_category, ChildAgeCategory.CHILD)
        
        # Тест с пустым словарем
        age_category = self.manager.detect_age_category({})
        self.assertEqual(age_category, ChildAgeCategory.CHILD)
        
        # Тест с неполными данными
        age_category = self.manager.detect_age_category({"interaction_pattern": {}})
        self.assertEqual(age_category, ChildAgeCategory.CHILD)
    
    def test_error_handling_invalid_interface_request(self):
        """Тест обработки ошибок с неверным запросом интерфейса"""
        # Тест с None
        interface = self.manager.get_interface_for_age(None)
        self.assertIsNotNone(interface)
        
        # Тест с несуществующей категорией
        class InvalidAge(Enum):
            INVALID = "invalid"
        
        interface = self.manager.get_interface_for_age(InvalidAge.INVALID)
        self.assertIsNotNone(interface)
    
    def test_error_handling_invalid_module_request(self):
        """Тест обработки ошибок с неверным запросом модуля"""
        # Тест с None
        module = self.manager.start_learning_module(None, "interactive")
        self.assertFalse(module)
        
        # Тест с несуществующей категорией
        class InvalidAge(Enum):
            INVALID = "invalid"
        
        module = self.manager.start_learning_module(InvalidAge.INVALID, "interactive")
        self.assertFalse(module)
    
    def test_metrics_initialization(self):
        """Тест инициализации метрик"""
        metrics = ChildInterfaceMetrics()
        self.assertEqual(metrics.total_users, 0)
        self.assertEqual(metrics.age_distribution, {})
        self.assertEqual(metrics.learning_progress, {})
        self.assertEqual(metrics.game_engagement, {})
        self.assertEqual(metrics.family_participation, {})
        self.assertIsNotNone(metrics.created_at)
        self.assertIsNotNone(metrics.last_update)
    
    def test_metrics_update(self):
        """Тест обновления метрик"""
        metrics = ChildInterfaceMetrics()
        
        user_data = {"age_category": "7-9"}
        learning_data = {"module_completed": 1}
        game_data = {"quest_completed": 1}
        family_data = {"family_quest": 1}
        
        metrics.update_metrics(user_data, learning_data, game_data, family_data)
        
        self.assertEqual(metrics.total_users, 1)
        self.assertEqual(metrics.age_distribution["7-9"], 1)
        self.assertEqual(metrics.learning_progress["module_completed"], 1)
        self.assertEqual(metrics.game_engagement["quest_completed"], 1)
        self.assertEqual(metrics.family_participation["family_quest"], 1)
    
    def test_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = ChildInterfaceMetrics()
        metrics_dict = metrics.to_dict()
        
        self.assertIn("total_users", metrics_dict)
        self.assertIn("age_distribution", metrics_dict)
        self.assertIn("learning_progress", metrics_dict)
        self.assertIn("game_engagement", metrics_dict)
        self.assertIn("family_participation", metrics_dict)
        self.assertIn("created_at", metrics_dict)
        self.assertIn("last_update", metrics_dict)

if __name__ == "__main__":
    unittest.main()