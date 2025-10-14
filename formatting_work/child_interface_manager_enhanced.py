#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChildInterfaceManager - Игровой интерфейс для детей всех возрастов
Поддерживает 5 возрастных категорий: 1-6, 7-9, 10-13, 14-18, 19-24 лет
"""

import hashlib
import os
import random
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple

# Добавляем путь к core модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "core"))

try:
    from config.color_scheme import ColorTheme, MatrixAIColorScheme
    from core.base import BaseAgent
except ImportError:
    # Fallback для совместимости
    class BaseAgent:
        """Базовый класс агента (fallback для совместимости)"""
        
        def __init__(self, name, config=None):
            self.name = name
            self.config = config or {}
            self.is_active = True
            self.created_at = datetime.now()
            self.last_update = datetime.now()

        def __str__(self) -> str:
            """Строковое представление агента для отладки"""
            return f"BaseAgent(name={self.name}, is_active={self.is_active})"

        def __repr__(self) -> str:
            """Детальное представление агента для отладки"""
            return (f"BaseAgent(name={self.name}, "
                    f"config={self.config}, "
                    f"is_active={self.is_active}, "
                    f"created_at={self.created_at}, "
                    f"last_update={self.last_update})")


class ChildAgeCategory(Enum):
    """Возрастные категории детей"""

    TODDLER = "1-6"  # Малыши-Исследователи
    CHILD = "7-9"  # Юные Защитники
    TWEEN = "10-13"  # Подростки-Хакеры
    TEEN = "14-18"  # Молодые Эксперты
    YOUNG_ADULT = "19-24"  # Молодые Профессионалы

    def __str__(self) -> str:
        """Строковое представление возрастной категории"""
        return f"{self.value} лет"

    def __repr__(self) -> str:
        """Детальное представление возрастной категории"""
        return f"ChildAgeCategory.{self.name}"

    def __lt__(self, other) -> bool:
        """Сравнение по возрасту (меньше)"""
        if not isinstance(other, ChildAgeCategory):
            return NotImplemented
        age_order = [self.TODDLER, self.CHILD, self.TWEEN, self.TEEN, self.YOUNG_ADULT]
        return age_order.index(self) < age_order.index(other)

    def __le__(self, other) -> bool:
        """Сравнение по возрасту (меньше или равно)"""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Сравнение по возрасту (больше)"""
        if not isinstance(other, ChildAgeCategory):
            return NotImplemented
        age_order = [self.TODDLER, self.CHILD, self.TWEEN, self.TEEN, self.YOUNG_ADULT]
        return age_order.index(self) > age_order.index(other)

    def __ge__(self, other) -> bool:
        """Сравнение по возрасту (больше или равно)"""
        return self == other or self > other

    @property
    def min_age(self) -> int:
        """Минимальный возраст в категории"""
        return int(self.value.split('-')[0])

    @property
    def max_age(self) -> int:
        """Максимальный возраст в категории"""
        return int(self.value.split('-')[1])


class GameLevel(Enum):
    """Игровые уровни безопасности"""

    BEGINNER = "Новичок"
    EXPLORER = "Исследователь"
    GUARDIAN = "Защитник"
    EXPERT = "Эксперт"
    MASTER = "Мастер"

    def __str__(self) -> str:
        """Строковое представление игрового уровня"""
        return self.value

    def __repr__(self) -> str:
        """Детальное представление игрового уровня"""
        return f"GameLevel.{self.name}"

    def __lt__(self, other) -> bool:
        """Сравнение по уровню (меньше)"""
        if not isinstance(other, GameLevel):
            return NotImplemented
        level_order = [self.BEGINNER, self.EXPLORER, self.GUARDIAN, self.EXPERT, self.MASTER]
        return level_order.index(self) < level_order.index(other)

    def __le__(self, other) -> bool:
        """Сравнение по уровню (меньше или равно)"""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Сравнение по уровню (больше)"""
        if not isinstance(other, GameLevel):
            return NotImplemented
        level_order = [self.BEGINNER, self.EXPLORER, self.GUARDIAN, self.EXPERT, self.MASTER]
        return level_order.index(self) > level_order.index(other)

    def __ge__(self, other) -> bool:
        """Сравнение по уровню (больше или равно)"""
        return self == other or self > other

    @property
    def level_number(self) -> int:
        """Номер уровня (1-5)"""
        level_order = [self.BEGINNER, self.EXPLORER, self.GUARDIAN, self.EXPERT, self.MASTER]
        return level_order.index(self) + 1

    @property
    def required_score(self) -> int:
        """Требуемый счет для достижения уровня"""
        level_scores = {self.BEGINNER: 0, self.EXPLORER: 100, self.GUARDIAN: 300, 
                       self.EXPERT: 600, self.MASTER: 1000}
        return level_scores[self]


class AchievementType(Enum):
    """Типы достижений"""

    SAFETY_RULE = "Правило безопасности"
    DAILY_QUEST = "Ежедневный квест"
    FAMILY_TEAM = "Семейная команда"
    LEARNING = "Обучение"
    PROTECTION = "Защита"


class ChildInterfaceManager(BaseAgent):
    """Менеджер игрового интерфейса для детей"""

    def __init__(self, config=None):
        BaseAgent.__init__(self, "ChildInterfaceManager", config)
        self.color_scheme = self._initialize_color_scheme()
        self.age_categories = {
            ChildAgeCategory.TODDLER: self._init_toddler_interface(),
            ChildAgeCategory.CHILD: self._init_child_interface(),
            ChildAgeCategory.TWEEN: self._init_tween_interface(),
            ChildAgeCategory.TEEN: self._init_teen_interface(),
            ChildAgeCategory.YOUNG_ADULT: self._init_young_adult_interface(),
        }
        self.game_system = self._init_game_system()
        self.learning_modules = self._init_learning_modules()
        self.family_integration = self._init_family_integration()
        self._initialize_ai_models()

    def __str__(self) -> str:
        """Строковое представление менеджера для отладки"""
        return (f"ChildInterfaceManager(name={self.name}, "
                f"age_categories={len(self.age_categories)}, "
                f"is_active={self.is_active})")

    def __repr__(self) -> str:
        """Детальное представление менеджера для отладки"""
        return (f"ChildInterfaceManager(name={self.name}, "
                f"config={self.config}, "
                f"is_active={self.is_active}, "
                f"created_at={self.created_at}, "
                f"last_update={self.last_update}, "
                f"age_categories={list(self.age_categories.keys())}, "
                f"game_system={bool(self.game_system)}, "
                f"learning_modules={bool(self.learning_modules)}, "
                f"family_integration={bool(self.family_integration)})")

    @property
    def total_age_categories(self) -> int:
        """Количество поддерживаемых возрастных категорий"""
        return len(self.age_categories)

    @property
    def is_fully_initialized(self) -> bool:
        """Проверка полной инициализации менеджера"""
        return (bool(self.age_categories) and 
                bool(self.game_system) and 
                bool(self.learning_modules) and 
                bool(self.family_integration))

    @property
    def supported_ages(self) -> List[str]:
        """Список поддерживаемых возрастных категорий"""
        return [category.value for category in self.age_categories.keys()]

    def _init_toddler_interface(self):
        """Интерфейс для малышей 1-6 лет"""
        return {
            "design": {
                "theme": "Мультяшный мир",
                "colors": [
                    "#FF6B6B",
                    "#4ECDC4",
                    "#45B7D1",
                    "#96CEB4",
                    "#FFEAA7",
                ],
                "characters": [
                    "Мудрый Зайчик",
                    "Храбрая Белочка",
                    "Умный Мишка",
                ],
                "sounds": ["giggle", "clap", "cheer", "magic"],
                "animations": ["bounce", "spin", "fade", "slide"],
            },
            "interaction": {
                "input_methods": ["touch", "voice"],
                "button_size": "large",
                "text_size": "huge",
                "simplicity": "maximum",
            },
            "safety_rules": [
                "Не разговаривай с незнакомцами",
                "Не нажимай на странные кнопки",
                "Скажи родителям, если что-то страшное",
                "Играй только в безопасные игры",
            ],
            "games": [
                "Найди безопасную игрушку",
                "Покажи, где дом",
                "Собери картинку безопасности",
                "Спой песенку о правилах",
            ],
        }

    def _init_child_interface(self):
        """Интерфейс для детей 7-9 лет"""
        return {
            "design": {
                "theme": "Супергерои",
                "colors": [
                    "#FF4757",
                    "#2ED573",
                    "#1E90FF",
                    "#FFA502",
                    "#FF6348",
                ],
                "characters": [
                    "Капитан Безопасность",
                    "Щит-Защитник",
                    "Кибер-Герой",
                ],
                "sounds": ["hero_theme", "victory", "power_up", "shield"],
                "animations": [
                    "hero_pose",
                    "shield_up",
                    "power_blast",
                    "victory_dance",
                ],
            },
            "interaction": {
                "input_methods": ["touch", "voice", "gesture"],
                "button_size": "medium",
                "text_size": "large",
                "simplicity": "high",
            },
            "safety_rules": [
                "Проверяй, кто пишет тебе",
                "Не скачивай файлы от незнакомцев",
                "Используй сложные пароли",
                "Расскажи родителям о странных сообщениях",
            ],
            "games": [
                "Квест безопасности",
                "Собери команду защитников",
                "Пройди лабиринт правил",
                "Соревнование по безопасности",
            ],
        }

    def _init_tween_interface(self):
        """Интерфейс для подростков 10-13 лет"""
        return {
            "design": {
                "theme": "Технологии и гаджеты",
                "colors": [
                    "#6C5CE7",
                    "#A29BFE",
                    "#FD79A8",
                    "#FDCB6E",
                    "#00B894",
                ],
                "characters": ["Кибер-Ниндзя", "Хакер-Защитник", "Код-Мастер"],
                "sounds": [
                    "tech_beep",
                    "hack_success",
                    "code_complete",
                    "system_online",
                ],
                "animations": [
                    "matrix_rain",
                    "hack_effect",
                    "code_glow",
                    "system_boot",
                ],
            },
            "interaction": {
                "input_methods": ["touch", "keyboard", "voice"],
                "button_size": "small",
                "text_size": "medium",
                "simplicity": "medium",
            },
            "safety_rules": [
                "Проверяй ссылки перед переходом",
                "Используй двухфакторную аутентификацию",
                "Не делись личной информацией",
                "Обновляй программы регулярно",
            ],
            "games": [
                "Симулятор хакера-защитника",
                "Кодирование безопасности",
                "Логические головоломки",
                "Командные миссии",
            ],
        }

    def _init_teen_interface(self):
        """Интерфейс для подростков 14-18 лет"""
        return {
            "design": {
                "theme": "Профессиональный, но дружелюбный",
                "colors": [
                    "#2D3436",
                    "#636E72",
                    "#74B9FF",
                    "#0984E3",
                    "#00CEC9",
                ],
                "characters": [
                    "Кибер-Аналитик",
                    "Сетевой Эксперт",
                    "Безопасность-Гуру",
                ],
                "sounds": [
                    "professional_beep",
                    "analysis_complete",
                    "threat_detected",
                    "system_secure",
                ],
                "animations": [
                    "data_flow",
                    "analysis_scan",
                    "threat_block",
                    "success_check",
                ],
            },
            "interaction": {
                "input_methods": ["touch", "keyboard", "voice", "gesture"],
                "button_size": "small",
                "text_size": "small",
                "simplicity": "low",
            },
            "safety_rules": [
                "Анализируй угрозы перед действием",
                "Используй профессиональные инструменты",
                "Следи за трендами безопасности",
                "Помогай младшим братьям и сестрам",
            ],
            "games": [
                "Реальные сценарии безопасности",
                "Проекты защиты",
                "Анализ угроз",
                "Командная работа",
            ],
        }

    def _init_young_adult_interface(self):
        """Интерфейс для молодых взрослых 19-24 лет"""
        return {
            "design": {
                "theme": "Корпоративный, но современный",
                "colors": [
                    "#2D3436",
                    "#636E72",
                    "#74B9FF",
                    "#0984E3",
                    "#00CEC9",
                ],
                "characters": [
                    "Кибер-Архитектор",
                    "Безопасность-Лидер",
                    "Инноватор",
                ],
                "sounds": [
                    "corporate_chime",
                    "leadership_theme",
                    "innovation_sound",
                    "success_fanfare",
                ],
                "animations": [
                    "corporate_flow",
                    "leadership_pose",
                    "innovation_spark",
                    "success_celebration",
                ],
            },
            "interaction": {
                "input_methods": [
                    "touch",
                    "keyboard",
                    "voice",
                    "gesture",
                    "api",
                ],
                "button_size": "small",
                "text_size": "small",
                "simplicity": "minimal",
            },
            "safety_rules": [
                "Архитектура безопасности",
                "Управление рисками",
                "Инновации в защите",
                "Лидерство в команде",
            ],
            "games": [
                "Архитектурные проекты",
                "Управление командами",
                "Инновационные решения",
                "Лидерские вызовы",
            ],
        }

    def _init_game_system(self):
        """Инициализация игровой системы"""
        return {
            "levels": {
                GameLevel.BEGINNER: {
                    "min_score": 0,
                    "max_score": 100,
                    "rewards": ["badge", "character"],
                },
                GameLevel.EXPLORER: {
                    "min_score": 101,
                    "max_score": 300,
                    "rewards": ["badge", "character", "theme"],
                },
                GameLevel.GUARDIAN: {
                    "min_score": 301,
                    "max_score": 600,
                    "rewards": ["badge", "character", "theme", "power"],
                },
                GameLevel.EXPERT: {
                    "min_score": 601,
                    "max_score": 1000,
                    "rewards": [
                        "badge",
                        "character",
                        "theme",
                        "power",
                        "title",
                    ],
                },
                GameLevel.MASTER: {
                    "min_score": 1001,
                    "max_score": 9999,
                    "rewards": [
                        "badge",
                        "character",
                        "theme",
                        "power",
                        "title",
                        "crown",
                    ],
                },
            },
            "achievements": {
                AchievementType.SAFETY_RULE: {
                    "points": 10,
                    "description": "Изучил правило безопасности",
                },
                AchievementType.DAILY_QUEST: {
                    "points": 25,
                    "description": "Выполнил ежедневный квест",
                },
                AchievementType.FAMILY_TEAM: {
                    "points": 50,
                    "description": "Помог семье с безопасностью",
                },
                AchievementType.LEARNING: {
                    "points": 30,
                    "description": "Прошел обучающий модуль",
                },
                AchievementType.PROTECTION: {
                    "points": 40,
                    "description": "Защитил от угрозы",
                },
            },
            "quests": {
                "daily": [
                    "Проверь безопасность",
                    "Изучи новое правило",
                    "Помоги семье",
                ],
                "weekly": [
                    "Семейный квест",
                    "Командная миссия",
                    "Экспертный вызов",
                ],
                "monthly": [
                    "Мастер-класс",
                    "Семейный турнир",
                    "Инновационный проект",
                ],
            },
        }

    def _init_learning_modules(self):
        """Инициализация обучающих модулей"""
        return {
            "interactive_lessons": {
                "toddler": [
                    "Сказки безопасности",
                    "Песенки правил",
                    "Игры с персонажами",
                ],
                "child": ["Квесты героев", "Викторины", "Мини-игры"],
                "tween": [
                    "Симуляции хакера",
                    "Логические задачи",
                    "Кодирование",
                ],
                "teen": ["Реальные сценарии", "Анализ угроз", "Проекты"],
                "young_adult": [
                    "Архитектурные решения",
                    "Управление командами",
                    "Инновации",
                ],
            },
            "quizzes": {
                "basic": [
                    "Что такое пароль?",
                    "Кто такие хакеры?",
                    "Как защитить данные?",
                ],
                "intermediate": [
                    "Двухфакторная аутентификация",
                    "Фишинг",
                    "Социальная инженерия",
                ],
                "advanced": [
                    "Архитектура безопасности",
                    "Управление рисками",
                    "Кибер-атаки",
                ],
            },
            "simulations": {
                "phishing": "Симуляция фишинговых атак",
                "malware": "Симуляция вредоносного ПО",
                "social_engineering": "Симуляция социальной инженерии",
                "network_attack": "Симуляция сетевых атак",
            },
        }

    def _init_family_integration(self):
        """Инициализация семейной интеграции"""
        return {
            "parental_control": {
                "soft_management": True,
                "progress_monitoring": True,
                "safety_reports": True,
                "emergency_functions": True,
                "privacy_protection": True,
                "data_encryption": True,
            },
            "family_features": {
                "shared_quests": True,
                "family_dashboard": True,
                "group_notifications": True,
                "unified_settings": True,
                "private_family_data": True,
            },
            "communication": {
                "parent_notifications": True,
                "child_requests": True,
                "family_chat": True,
                "emergency_alerts": True,
                "confidential_messages": True,
            },
        }

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        self.ai_models = {
            "age_detector": {
                "accuracy": 0.95,
                "features": [
                    "interaction_pattern",
                    "preference_analysis",
                    "behavior_analysis",
                ],
                "description": "Определение возрастной категории по поведению",
            },
            "learning_optimizer": {
                "accuracy": 0.90,
                "features": [
                    "progress_tracking",
                    "difficulty_adjustment",
                    "personalization",
                ],
                "description": "Оптимизация обучения под ребенка",
            },
            "safety_analyzer": {
                "accuracy": 0.98,
                "features": [
                    "threat_detection",
                    "risk_assessment",
                    "protection_recommendations",
                ],
                "description": "Анализ безопасности действий ребенка",
            },
            "engagement_predictor": {
                "accuracy": 0.85,
                "features": [
                    "interest_analysis",
                    "motivation_tracking",
                    "retention_prediction",
                ],
                "description": "Предсказание вовлеченности ребенка",
            },
        }

    def detect_age_category(self, user_data: Dict[str, Any]) -> ChildAgeCategory:
        """Определение возрастной категории пользователя"""
        try:
            # Анализ данных пользователя
            interaction_pattern = user_data.get("interaction_pattern", {})
            preferences = user_data.get("preferences", {})
            behavior = user_data.get("behavior", {})

            # AI анализ для определения возраста
            age_score = self._calculate_age_score(
                interaction_pattern, preferences, behavior
            )

            # Определение категории по баллам
            if age_score < 20:
                return ChildAgeCategory.TODDLER
            elif age_score < 40:
                return ChildAgeCategory.CHILD
            elif age_score < 60:
                return ChildAgeCategory.TWEEN
            elif age_score < 80:
                return ChildAgeCategory.TEEN
            else:
                return ChildAgeCategory.YOUNG_ADULT

        except Exception as e:
            self.log_error(f"Ошибка определения возрастной категории: {str(e)}")
            return ChildAgeCategory.CHILD  # По умолчанию

    def _calculate_age_score(self, interaction_pattern, preferences, behavior):
        """Расчет балла возраста"""
        score = 0

        # Анализ паттернов взаимодействия
        if interaction_pattern.get("touch_heavy", False):
            score += 5
        if interaction_pattern.get("voice_commands", False):
            score += 10
        if interaction_pattern.get("keyboard_use", False):
            score += 15
        if interaction_pattern.get("gesture_control", False):
            score += 20

        # Анализ предпочтений
        if preferences.get("simple_games", False):
            score += 5
        if preferences.get("complex_games", False):
            score += 15
        if preferences.get("educational_content", False):
            score += 10
        if preferences.get("professional_tools", False):
            score += 25

        # Анализ поведения
        if behavior.get("help_seeking", False):
            score += 5
        if behavior.get("independent_learning", False):
            score += 15
        if behavior.get("team_leadership", False):
            score += 25

        return min(score, 100)

    def get_interface_for_age(self, age_category: Union[ChildAgeCategory, str]) -> Dict[str, Any]:
        """Получение интерфейса для возрастной категории"""
        try:
            if age_category in self.age_categories:
                return self.age_categories[age_category]
            else:
                return self.age_categories[ChildAgeCategory.CHILD]
        except Exception as e:
            self.log_error(f"Ошибка получения интерфейса: {str(e)}")
            return None

    def start_learning_module(self, age_category: Union[ChildAgeCategory, str], module_type: str) -> Dict[str, Any]:
        """Запуск обучающего модуля"""
        try:
            interface = self.get_interface_for_age(age_category)
            if not interface:
                return False

            # Выбор модуля по возрасту
            if age_category == ChildAgeCategory.TODDLER:
                modules = self.learning_modules["interactive_lessons"][
                    "toddler"
                ]
            elif age_category == ChildAgeCategory.CHILD:
                modules = self.learning_modules["interactive_lessons"]["child"]
            elif age_category == ChildAgeCategory.TWEEN:
                modules = self.learning_modules["interactive_lessons"]["tween"]
            elif age_category == ChildAgeCategory.TEEN:
                modules = self.learning_modules["interactive_lessons"]["teen"]
            else:
                modules = self.learning_modules["interactive_lessons"][
                    "young_adult"
                ]

            # Запуск модуля
            selected_module = random.choice(modules)
            return {
                "module": selected_module,
                "age_category": age_category.value,
                "interface": interface,
                "status": "started",
            }

        except Exception as e:
            self.log_error(f"Ошибка запуска модуля: {str(e)}")
            return False

    def complete_quest(self, user_id: str, quest_type: str, score: int) -> Dict[str, Any]:
        """Завершение квеста"""
        try:
            # Обновление прогресса
            progress = self._update_user_progress(user_id, quest_type, score)

            # Проверка достижений
            achievements = self._check_achievements(user_id, quest_type, score)

            # Обновление уровня
            new_level = self._update_user_level(
                user_id, progress["total_score"]
            )

            return {
                "progress": progress,
                "achievements": achievements,
                "new_level": new_level,
                "rewards": self._calculate_rewards(new_level, achievements),
            }

        except Exception as e:
            self.log_error(f"Ошибка завершения квеста: {str(e)}")
            return False

    def _update_user_progress(self, user_id, quest_type, score):
        """Обновление прогресса пользователя"""
        # Здесь должна быть логика обновления в базе данных
        return {
            "user_id": user_id,
            "quest_type": quest_type,
            "score": score,
            "total_score": score * 1.2,  # Бонус за выполнение
            "timestamp": datetime.now().isoformat(),
        }

    def _check_achievements(self, user_id, quest_type, score):
        """Проверка достижений"""
        achievements = []

        # Проверка различных типов достижений
        if quest_type == "daily":
            achievements.append(
                {
                    "type": AchievementType.DAILY_QUEST.value,
                    "points": self.game_system["achievements"][
                        AchievementType.DAILY_QUEST
                    ]["points"],
                    "description": self.game_system["achievements"][
                        AchievementType.DAILY_QUEST
                    ]["description"],
                }
            )

        if score >= 100:
            achievements.append(
                {
                    "type": AchievementType.SAFETY_RULE.value,
                    "points": self.game_system["achievements"][
                        AchievementType.SAFETY_RULE
                    ]["points"],
                    "description": self.game_system["achievements"][
                        AchievementType.SAFETY_RULE
                    ]["description"],
                }
            )

        return achievements

    def _update_user_level(self, user_id, total_score):
        """Обновление уровня пользователя"""
        for level, data in self.game_system["levels"].items():
            if data["min_score"] <= total_score <= data["max_score"]:
                return level.value

        return GameLevel.BEGINNER.value

    def _calculate_rewards(self, level, achievements):
        """Расчет наград"""
        rewards = []

        # Награды за уровень
        level_data = None
        for lvl, data in self.game_system["levels"].items():
            if lvl.value == level:
                level_data = data
                break

        if level_data:
            rewards.extend(level_data["rewards"])

        # Награды за достижения
        for achievement in achievements:
            rewards.append("achievement_{}".format(achievement["type"]))

        return rewards

    def get_family_dashboard_data(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Получение данных семейной панели"""
        try:
            # Здесь должна быть логика получения данных семьи
            return {
                "family_id": family_id,
                "children": [
                    {
                        "name": "Ребенок 1",
                        "age_category": "7-9",
                        "level": "Защитник",
                        "score": 450,
                    },
                    {
                        "name": "Ребенок 2",
                        "age_category": "10-13",
                        "level": "Эксперт",
                        "score": 750,
                    },
                ],
                "family_quests": ["Семейная безопасность", "Командная миссия"],
                "achievements": ["Семейная команда", "Защитники дома"],
                "notifications": [
                    "Новый квест доступен",
                    "Достижение разблокировано",
                ],
            }
        except Exception as e:
            self.log_error(f"Ошибка получения данных семьи: {str(e)}")
            return None

    def send_parent_notification(self, parent_id: str, message: str, priority: str = "normal") -> Union[Dict[str, Any], bool]:
        """Отправка уведомления родителю"""
        try:
            notification = {
                "parent_id": parent_id,
                "message": message,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "read": False,
            }

            # Здесь должна быть логика отправки уведомления
            return notification

        except Exception as e:
            self.log_error(f"Ошибка отправки уведомления: {str(e)}")
            return False

    def log_error(self, message: str) -> None:
        """Логирование ошибок"""
        print(f"ERROR [ChildInterfaceManager]: {message}")

    def log_info(self, message: str) -> None:
        """Логирование информации"""
        print(f"INFO [ChildInterfaceManager]: {message}")

    def protect_privacy_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Защита приватных данных пользователя"""
        try:
            # Шифрование чувствительных данных
            protected_data = user_data.copy()

            # Удаление или маскирование приватной информации
            if "personal_info" in protected_data:
                protected_data["personal_info"] = "***MASKED***"

            if "location" in protected_data:
                protected_data["location"] = "***MASKED***"

            if "device_id" in protected_data:
                # Хеширование ID устройства
                protected_data["device_id"] = hashlib.sha256(
                    str(protected_data["device_id"]).encode()
                ).hexdigest()[:8]

            return protected_data

        except Exception as e:
            self.log_error(f"Ошибка защиты приватности: {str(e)}")
            return user_data

    def encrypt_sensitive_data(self, data):
        """Шифрование чувствительных данных"""
        try:
            # Простое шифрование для демонстрации
            if isinstance(data, str):
                return hashlib.sha256(data.encode()).hexdigest()
            elif isinstance(data, dict):
                encrypted = {}
                for key, value in data.items():
                    if key in ["password", "token", "secret"]:
                        encrypted[key] = hashlib.sha256(
                            str(value).encode()
                        ).hexdigest()
                    else:
                        encrypted[key] = value
                return encrypted
            else:
                return data

        except Exception as e:
            self.log_error(f"Ошибка шифрования: {str(e)}")
            return data

    def validate_privacy_settings(self, settings):
        """Валидация настроек приватности"""
        try:
            required_privacy_settings = [
                "data_collection",
                "data_sharing",
                "data_retention",
                "parental_consent",
                "child_protection",
            ]

            for setting in required_privacy_settings:
                if setting not in settings:
                    return False

            return True

        except Exception as e:
            self.log_error(f"Ошибка валидации приватности: {str(e)}")
            return False

    def _initialize_color_scheme(self):
        """Инициализация цветовой схемы для детей"""
        try:
            # Создаем экземпляр цветовой схемы
            color_scheme = MatrixAIColorScheme()

            # Устанавливаем тему для детей
            color_scheme.set_theme(ColorTheme.CHILD_FRIENDLY)

            # Дополнительные цвета для детского интерфейса
            child_colors = {
                "game_primary": "#3B82F6",  # Ярко-синий для игр
                "game_secondary": "#FEF3C7",  # Светло-желтый
                "game_accent": "#F59E0B",  # Золотой
                "success_green": "#10B981",  # Зеленый успеха
                "warning_orange": "#F59E0B",  # Оранжевый предупреждения
                "error_red": "#EF4444",  # Красный ошибки
                "info_purple": "#8B5CF6",  # Фиолетовый информации
                "background_light": "#F0F9FF",  # Очень светло-синий фон
                "text_dark": "#1F2937",  # Темно-серый текст
                "border_light": "#E5E7EB",  # Светло-серые границы
                "shadow_soft": "#3B82F620",  # Мягкие тени
                "gradient_start": "#3B82F6",  # Начало градиента
                "gradient_end": "#8B5CF6",  # Конец градиента
                "character_colors": [  # Цвета для персонажей
                    "#FF6B6B",  # Красный
                    "#4ECDC4",  # Бирюзовый
                    "#45B7D1",  # Голубой
                    "#96CEB4",  # Зеленый
                    "#FFEAA7",  # Желтый
                    "#DDA0DD",  # Фиолетовый
                    "#98D8C8",  # Мятный
                    "#F7DC6F",  # Золотистый
                ],
                "age_specific_colors": {
                    "1-6": {  # Малыши - яркие, контрастные
                        "primary": "#FF6B6B",
                        "secondary": "#4ECDC4",
                        "accent": "#FFEAA7",
                        "background": "#FFF8E1",
                    },
                    "7-9": {  # Младшие дети - игровые
                        "primary": "#3B82F6",
                        "secondary": "#FEF3C7",
                        "accent": "#F59E0B",
                        "background": "#F0F9FF",
                    },
                    "10-13": {  # Подростки - современные
                        "primary": "#8B5CF6",
                        "secondary": "#E0E7FF",
                        "accent": "#F59E0B",
                        "background": "#FAFAFA",
                    },
                    "14-18": {  # Старшие подростки - профессиональные
                        "primary": "#1E40AF",
                        "secondary": "#F3F4F6",
                        "accent": "#F59E0B",
                        "background": "#FFFFFF",
                    },
                    "19-24": {  # Молодые взрослые - зрелые
                        "primary": "#1E3A8A",
                        "secondary": "#F8FAFC",
                        "accent": "#F59E0B",
                        "background": "#FFFFFF",
                    },
                },
            }

            # Объединяем основную схему с детскими цветами
            full_scheme = {
                "base_scheme": color_scheme.get_current_theme(),
                "child_colors": child_colors,
                "css_variables": color_scheme.get_css_variables(),
                "tailwind_colors": color_scheme.get_tailwind_colors(),
                "gradients": color_scheme.get_gradient_colors(),
                "shadows": color_scheme.get_shadow_colors(),
                "accessible_colors": color_scheme.get_accessible_colors(),
            }

            return full_scheme

        except Exception:
            # Fallback цветовая схема
            return {
                "base_scheme": {
                    "primary": "#3B82F6",
                    "secondary": "#FEF3C7",
                    "accent": "#F59E0B",
                    "text": "#1F2937",
                    "background": "#F0F9FF",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444",
                    "info": "#8B5CF6",
                },
                "child_colors": {
                    "game_primary": "#3B82F6",
                    "game_secondary": "#FEF3C7",
                    "game_accent": "#F59E0B",
                    "success_green": "#10B981",
                    "warning_orange": "#F59E0B",
                    "error_red": "#EF4444",
                    "info_purple": "#8B5CF6",
                },
            }

    def get_color_scheme_for_age(self, age_category):
        """Получение цветовой схемы для конкретного возраста"""
        try:
            if age_category in self.color_scheme.get("child_colors", {}).get(
                "age_specific_colors", {}
            ):
                return self.color_scheme["child_colors"][
                    "age_specific_colors"
                ][age_category]
            else:
                return self.color_scheme["child_colors"][
                    "age_specific_colors"
                ][
                    "7-9"
                ]  # По умолчанию
        except Exception:
            return {
                "primary": "#3B82F6",
                "secondary": "#FEF3C7",
                "accent": "#F59E0B",
                "background": "#F0F9FF",
            }

    def generate_ui_colors(self, age_category, element_type="button"):
        """Генерация цветов для UI элементов"""
        try:
            age_colors = self.get_color_scheme_for_age(age_category)

            ui_colors = {
                "button": {
                    "background": age_colors["primary"],
                    "text": "#FFFFFF",
                    "border": age_colors["primary"],
                    "hover": self._darken_color(age_colors["primary"], 0.1),
                    "active": self._darken_color(age_colors["primary"], 0.2),
                },
                "card": {
                    "background": age_colors["background"],
                    "border": age_colors["secondary"],
                    "shadow": self.color_scheme.get("shadows", {}).get(
                        "shadow_soft", "#3B82F620"
                    ),
                },
                "text": {
                    "primary": age_colors.get("text", "#1F2937"),
                    "secondary": self._lighten_color(
                        age_colors.get("text", "#1F2937"), 0.3
                    ),
                    "accent": age_colors["accent"],
                },
                "status": {
                    "success": self.color_scheme.get("child_colors", {}).get(
                        "success_green", "#10B981"
                    ),
                    "warning": self.color_scheme.get("child_colors", {}).get(
                        "warning_orange", "#F59E0B"
                    ),
                    "error": self.color_scheme.get("child_colors", {}).get(
                        "error_red", "#EF4444"
                    ),
                    "info": self.color_scheme.get("child_colors", {}).get(
                        "info_purple", "#8B5CF6"
                    ),
                },
            }

            return ui_colors.get(element_type, ui_colors["button"])

        except Exception:
            return {
                "background": "#3B82F6",
                "text": "#FFFFFF",
                "border": "#3B82F6",
            }

    def _darken_color(self, hex_color, factor):
        """Затемнение цвета"""
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            r = int(r * (1 - factor))
            g = int(g * (1 - factor))
            b = int(b * (1 - factor))

            return f"#{r:02x}{g:02x}{b:02x}"
        except BaseException:
            return hex_color

    def _lighten_color(self, hex_color, factor):
        """Осветление цвета"""
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)

            return f"#{r:02x}{g:02x}{b:02x}"
        except BaseException:
            return hex_color


class ChildInterfaceMetrics:
    """Метрики ChildInterfaceManager"""

    def __init__(self):
        self.total_users = 0
        self.age_distribution = {}
        self.learning_progress = {}
        self.game_engagement = {}
        self.family_participation = {}
        self.safety_improvements = {}
        self.created_at = datetime.now()
        self.last_update = datetime.now()

    def __str__(self) -> str:
        """Строковое представление метрик для отладки"""
        return (f"ChildInterfaceMetrics(total_users={self.total_users}, "
                f"age_distribution={len(self.age_distribution)}, "
                f"achievements={len(self.safety_improvements)})")

    def __repr__(self) -> str:
        """Детальное представление метрик для отладки"""
        return (f"ChildInterfaceMetrics(total_users={self.total_users}, "
                f"age_distribution={self.age_distribution}, "
                f"learning_progress={self.learning_progress}, "
                f"game_engagement={self.game_engagement}, "
                f"family_participation={self.family_participation}, "
                f"safety_improvements={self.safety_improvements}, "
                f"last_update={self.last_update})")

    def update_metrics(self, user_data, learning_data, game_data, family_data):
        """Обновление метрик"""
        self.total_users += 1
        self.last_update = datetime.now()

        # Обновление распределения по возрастам
        age_category = user_data.get("age_category", "unknown")
        self.age_distribution[age_category] = (
            self.age_distribution.get(age_category, 0) + 1
        )

        # Обновление прогресса обучения
        self.learning_progress.update(learning_data)

        # Обновление вовлеченности в игры
        self.game_engagement.update(game_data)

        # Обновление семейного участия
        self.family_participation.update(family_data)

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "total_users": self.total_users,
            "age_distribution": self.age_distribution,
            "learning_progress": self.learning_progress,
            "game_engagement": self.game_engagement,
            "family_participation": self.family_participation,
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update.isoformat(),
        }


# Пример использования
if __name__ == "__main__":
    # Создание менеджера
    manager = ChildInterfaceManager()

    # Тестирование определения возраста
    user_data = {
        "interaction_pattern": {"touch_heavy": True, "voice_commands": True},
        "preferences": {"simple_games": True, "educational_content": True},
        "behavior": {"help_seeking": True},
    }

    age_category = manager.detect_age_category(user_data)
    print("Определенная возрастная категория: {}".format(age_category.value))

    # Получение интерфейса
    interface = manager.get_interface_for_age(age_category)
    print("Интерфейс загружен: {}".format(interface["design"]["theme"]))

    # Запуск обучающего модуля
    module = manager.start_learning_module(age_category, "interactive")
    print("Модуль запущен: {}".format(module["module"]))
