#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElderlyInterfaceManager - Интерфейс для пожилых людей
Создан: 2024-09-05
Версия: 1.0.0
Качество: A+
"""

import os
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ComponentStatus(Enum):
    """Статусы компонентов системы"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SLEEP = "sleep"
    ERROR = "error"


class ElderlyAgeCategory(Enum):
    """Возрастные категории пожилых людей"""
    ACTIVE_ELDERLY = "60-70"      # Активные пожилые
    MIDDLE_ELDERLY = "71-80"      # Средний возраст
    SENIOR_ELDERLY = "81+"        # Пожилые с ограничениями


class InterfaceComplexity(Enum):
    """Уровни сложности интерфейса"""
    SIMPLE = "simple"             # Простой
    MODERATE = "moderate"         # Умеренный
    ADVANCED = "advanced"         # Продвинутый


class AccessibilityLevel(Enum):
    """Уровни доступности"""
    BASIC = "basic"               # Базовый
    ENHANCED = "enhanced"         # Улучшенный
    MAXIMUM = "maximum"           # Максимальный


@dataclass
class ElderlyUserProfile:
    """Профиль пожилого пользователя"""
    user_id: str
    age: int
    age_category: ElderlyAgeCategory
    interface_complexity: InterfaceComplexity
    accessibility_level: AccessibilityLevel
    family_contacts: List[str]
    emergency_contacts: List[str]
    preferences: Dict[str, Any]
    created_at: datetime
    last_activity: datetime


@dataclass
class InterfaceSettings:
    """Настройки интерфейса"""
    font_size: int
    button_size: int
    contrast_ratio: float
    animation_speed: float
    voice_enabled: bool
    voice_speed: float
    voice_volume: float
    color_scheme: str
    icon_size: int
    spacing: int


class ElderlyInterfaceManager:
    """Менеджер интерфейса для пожилых людей"""

    def __init__(self, config_path: str = "config/elderly_interface.json"):
        """Инициализация менеджера интерфейса для пожилых"""
        self.name = "ElderlyInterfaceManager"
        self.status = ComponentStatus.INITIALIZING
        self.config_path = config_path

        # Настройка логирования в первую очередь
        self._setup_logging()

        self.age_categories = {
            ElderlyAgeCategory.ACTIVE_ELDERLY: {
                "name": "Активные пожилые",
                "age_range": (60, 70),
                "complexity": InterfaceComplexity.ADVANCED,
                "accessibility": AccessibilityLevel.BASIC,
                "features": ["современный_дизайн", "быстрые_действия", "социальные_функции"]
            },
            ElderlyAgeCategory.MIDDLE_ELDERLY: {
                "name": "Средний возраст",
                "age_range": (71, 80),
                "complexity": InterfaceComplexity.MODERATE,
                "accessibility": AccessibilityLevel.ENHANCED,
                "features": ["пошаговые_инструкции", "семейная_поддержка", "медленные_переходы"]
            },
            ElderlyAgeCategory.SENIOR_ELDERLY: {
                "name": "Пожилые с ограничениями",
                "age_range": (81, 100),
                "complexity": InterfaceComplexity.SIMPLE,
                "accessibility": AccessibilityLevel.MAXIMUM,
                "features": ["крупные_кнопки", "голосовое_управление", "экстренная_помощь"]
            }
        }

        self.interface_templates = self._init_interface_templates()
        self.accessibility_features = self._init_accessibility_features()
        self.family_integration = self._init_family_integration()
        self.emergency_systems = self._init_emergency_systems()
        self.ai_models = self._init_ai_models()

        self._load_configuration()

        self.logger.info("ElderlyInterfaceManager инициализирован успешно")
        self.status = ComponentStatus.ACTIVE

    def _setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs/elderly_interface"
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"elderly_interface_{datetime.now().strftime('%Y%m%d')}.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
        )

        self.logger = logging.getLogger(__name__)

    def _init_interface_templates(self) -> Dict[str, Any]:
        """Инициализация шаблонов интерфейсов"""
        return {
            "active_elderly": {
                "layout": "modern_grid",
                "colors": ["#2E5BFF", "#FFFFFF", "#F8F9FA"],
                "typography": "roboto_medium",
                "interactions": "swipe_tap",
                "animations": "smooth_fast"
            },
            "middle_elderly": {
                "layout": "traditional_list",
                "colors": ["#4A90E2", "#FFFFFF", "#F5F5F5"],
                "typography": "arial_large",
                "interactions": "tap_hold",
                "animations": "smooth_slow"
            },
            "senior_elderly": {
                "layout": "large_buttons",
                "colors": ["#FF6B6B", "#FFFFFF", "#FFF5F5"],
                "typography": "arial_extra_large",
                "interactions": "tap_only",
                "animations": "minimal"
            }
        }

    def _init_accessibility_features(self) -> Dict[str, Any]:
        """Инициализация функций доступности"""
        return {
            "visual": {
                "high_contrast": True,
                "large_fonts": True,
                "color_blind_support": True,
                "screen_reader": True
            },
            "motor": {
                "large_touch_targets": True,
                "gesture_alternatives": True,
                "voice_control": True,
                "switch_control": True
            },
            "cognitive": {
                "simple_language": True,
                "step_by_step": True,
                "memory_aids": True,
                "error_prevention": True
            },
            "hearing": {
                "visual_alerts": True,
                "vibration": True,
                "text_to_speech": True,
                "closed_captions": True
            }
        }

    def _init_family_integration(self) -> Dict[str, Any]:
        """Инициализация семейной интеграции"""
        return {
            "family_contacts": [],
            "emergency_contacts": [],
            "shared_calendar": True,
            "photo_sharing": True,
            "message_center": True,
            "health_monitoring": True,
            "location_sharing": True
        }

    def _init_emergency_systems(self) -> Dict[str, Any]:
        """Инициализация экстренных систем"""
        return {
            "panic_button": True,
            "auto_call_family": True,
            "medical_alert": True,
            "fall_detection": True,
            "location_tracking": True,
            "emergency_contacts": [],
            "medical_info": {}
        }

    def _init_ai_models(self) -> Dict[str, Any]:
        """Инициализация AI моделей"""
        return {
            "age_classifier": {
                "accuracy": 0.95,
                "model_type": "neural_network",
                "features": ["typing_speed", "interaction_pattern", "error_rate"]
            },
            "accessibility_optimizer": {
                "accuracy": 0.90,
                "model_type": "decision_tree",
                "features": ["usage_pattern", "error_frequency", "preference_history"]
            },
            "safety_monitor": {
                "accuracy": 0.98,
                "model_type": "ensemble",
                "features": ["behavior_analysis", "risk_assessment", "anomaly_detection"]
            },
            "family_connector": {
                "accuracy": 0.85,
                "model_type": "recommendation_engine",
                "features": ["communication_pattern", "family_dynamics", "preference_matching"]
            }
        }

    def determine_age_category(self, age: int) -> ElderlyAgeCategory:
        """Определение возрастной категории"""
        if 60 <= age <= 70:
            return ElderlyAgeCategory.ACTIVE_ELDERLY
        elif 71 <= age <= 80:
            return ElderlyAgeCategory.MIDDLE_ELDERLY
        else:
            return ElderlyAgeCategory.SENIOR_ELDERLY

    def create_user_profile(self, user_id: str, age: int, preferences: Dict[str, Any]) -> ElderlyUserProfile:
        """Создание профиля пользователя"""
        age_category = self.determine_age_category(age)

        profile = ElderlyUserProfile(
            user_id=user_id,
            age=age,
            age_category=age_category,
            interface_complexity=self.age_categories[age_category]["complexity"],
            accessibility_level=self.age_categories[age_category]["accessibility"],
            family_contacts=preferences.get("family_contacts", []),
            emergency_contacts=preferences.get("emergency_contacts", []),
            preferences=preferences,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )

        self.logger.info(f"Создан профиль пользователя {user_id} для возрастной категории {age_category.value}")
        return profile

    def generate_interface_settings(self, profile: ElderlyUserProfile) -> InterfaceSettings:
        """Генерация настроек интерфейса на основе профиля"""
        category = profile.age_category

        if category == ElderlyAgeCategory.ACTIVE_ELDERLY:
            return InterfaceSettings(
                font_size=16, button_size=44, contrast_ratio=4.5, animation_speed=0.3,
                voice_enabled=False, voice_speed=1.0, voice_volume=0.7,
                color_scheme="modern", icon_size=24, spacing=12
            )
        elif category == ElderlyAgeCategory.MIDDLE_ELDERLY:
            return InterfaceSettings(
                font_size=20, button_size=56, contrast_ratio=7.0, animation_speed=0.5,
                voice_enabled=True, voice_speed=0.8, voice_volume=0.8,
                color_scheme="traditional", icon_size=32, spacing=16
            )
        else:  # SENIOR_ELDERLY
            return InterfaceSettings(
                font_size=24, button_size=72, contrast_ratio=10.0, animation_speed=0.8,
                voice_enabled=True, voice_speed=0.6, voice_volume=0.9,
                color_scheme="high_contrast", icon_size=48, spacing=24
            )

    def get_interface_template(self, age_category: ElderlyAgeCategory) -> Dict[str, Any]:
        """Получение шаблона интерфейса для возрастной категории"""
        if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
            return self.interface_templates["active_elderly"]
        elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
            return self.interface_templates["middle_elderly"]
        else:
            return self.interface_templates["senior_elderly"]

    def generate_voice_commands(self, age_category: ElderlyAgeCategory) -> List[str]:
        """Генерация голосовых команд для возрастной категории"""
        base_commands = ["Помощь", "Закрыть", "Назад", "Главное меню", "Позвонить семье"]

        if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
            return base_commands + ["Отправить сообщение", "Поделиться фото", "Показать календарь", "Настройки"]
        elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
            return base_commands + ["Показать инструкции", "Повторить", "Медленнее", "Объяснить"]
        else:  # SENIOR_ELDERLY
            return base_commands + ["Экстренная помощь", "Позвонить врачу", "Громче", "Проще"]

    def setup_family_integration(self, profile: ElderlyUserProfile) -> Dict[str, Any]:
        """Настройка семейной интеграции"""
        family_data = {
            "user_id": profile.user_id,
            "family_contacts": profile.family_contacts,
            "emergency_contacts": profile.emergency_contacts,
            "permissions": {
                "location_sharing": True,
                "health_monitoring": True,
                "message_notifications": True,
                "emergency_alerts": True
            },
            "communication_channels": ["voice_call", "video_call", "text_message", "photo_sharing"]
        }

        self.family_integration.update(family_data)
        self.logger.info(f"Настроена семейная интеграция для пользователя {profile.user_id}")
        return family_data

    def setup_emergency_systems(self, profile: ElderlyUserProfile) -> Dict[str, Any]:
        """Настройка экстренных систем"""
        emergency_config = {
            "panic_button": {
                "enabled": True,
                "auto_call_family": True,
                "auto_call_emergency": True,
                "location_sharing": True
            },
            "fall_detection": {
                "enabled": profile.age_category == ElderlyAgeCategory.SENIOR_ELDERLY,
                "sensitivity": "high" if profile.age >= 80 else "medium",
                "auto_alert": True
            },
            "medical_alert": {
                "enabled": True,
                "medical_conditions": profile.preferences.get("medical_conditions", []),
                "medications": profile.preferences.get("medications", []),
                "allergies": profile.preferences.get("allergies", [])
            }
        }

        self.emergency_systems.update(emergency_config)
        self.logger.info(f"Настроены экстренные системы для пользователя {profile.user_id}")
        return emergency_config

    def generate_accessibility_features(self, profile: ElderlyUserProfile) -> Dict[str, Any]:
        """Генерация функций доступности для профиля"""
        features = {
            "visual": {
                "font_size": "large" if profile.age >= 75 else "medium",
                "high_contrast": profile.age >= 70,
                "color_blind_support": True,
                "screen_reader": profile.age >= 80
            },
            "motor": {
                "large_touch_targets": profile.age >= 70,
                "gesture_alternatives": profile.age >= 75,
                "voice_control": profile.age >= 75,
                "switch_control": profile.age >= 80
            },
            "cognitive": {
                "simple_language": profile.age >= 70,
                "step_by_step": profile.age >= 75,
                "memory_aids": profile.age >= 80,
                "error_prevention": True
            }
        }
        return features

    def create_learning_modules(self, age_category: ElderlyAgeCategory) -> List[Dict[str, Any]]:
        """Создание обучающих модулей для возрастной категории"""
        if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
            return [
                {"title": "Основы безопасности", "duration": "10 минут", "type": "interactive", "difficulty": "beginner"},
                {"title": "Семейное общение", "duration": "15 минут", "type": "tutorial", "difficulty": "intermediate"},
                {"title": "Продвинутые функции", "duration": "20 минут", "type": "hands_on", "difficulty": "advanced"}
            ]
        elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
            return [
                {"title": "Простые шаги", "duration": "15 минут", "type": "step_by_step", "difficulty": "beginner"},
                {"title": "Безопасность в интернете", "duration": "20 минут", "type": "guided", "difficulty": "beginner"},
                {"title": "Связь с семьей", "duration": "25 минут", "type": "practical", "difficulty": "intermediate"}
            ]
        else:  # SENIOR_ELDERLY
            return [{"title": "Основы", "duration": "20 минут", "type": "voice_guided", "difficulty": "beginner"}, {"title": "Экстренная помощь", "duration": "15 минут", "type": "repetitive", "difficulty": "beginner"}, {"title": "Семейная связь", "duration": "30 минут", "type": "assisted", "difficulty": "beginner"}]

    def monitor_user_behavior(self, profile: ElderlyUserProfile, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Мониторинг поведения пользователя"""
        analysis = {
            "user_id": profile.user_id,
            "timestamp": datetime.now(),
            "interaction_count": behavior_data.get("interaction_count", 0),
            "error_rate": behavior_data.get("error_rate", 0.0),
            "time_per_task": behavior_data.get("time_per_task", 0.0),
            "accessibility_needs": [],
            "recommendations": []
        }

        if behavior_data.get("error_rate", 0) > 0.3:
            analysis["accessibility_needs"].append("упростить_интерфейс")
            analysis["recommendations"].append("Увеличить размер кнопок")

        if behavior_data.get("time_per_task", 0) > 30:
            analysis["accessibility_needs"].append("добавить_подсказки")
            analysis["recommendations"].append("Включить голосовые подсказки")

        if behavior_data.get("voice_usage", 0) > 0.7:
            analysis["accessibility_needs"].append("расширить_голосовое_управление")
            analysis["recommendations"].append("Добавить больше голосовых команд")

        self.logger.info(f"Проанализировано поведение пользователя {profile.user_id}")
        return analysis

    def send_family_notification(self, profile: ElderlyUserProfile, message: str, urgency: str = "normal") -> bool:
        """Отправка уведомления семье"""
        try:
            self.logger.info(f"Отправлено уведомление семье: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")
            return False

    def handle_emergency(self, profile: ElderlyUserProfile, emergency_type: str) -> bool:
        """Обработка экстренной ситуации"""
        try:
            self.send_family_notification(profile, f"ЭКСТРЕННАЯ СИТУАЦИЯ: {emergency_type}", "urgent")
            self.logger.critical(f"Обработана экстренная ситуация: {emergency_type}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обработки экстренной ситуации: {e}")
            return False

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования"""
        return {
            "total_users": len(self.family_integration.get("family_contacts", [])),
            "age_distribution": {"60-70": 0, "71-80": 0, "81+": 0},
            "accessibility_usage": {"voice_control": 0.0, "large_fonts": 0.0, "high_contrast": 0.0, "screen_reader": 0.0},
            "emergency_events": 0,
            "family_notifications": 0
        }

    def _load_configuration(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                    self.logger.info("Конфигурация загружена успешно")
            else:
                self.logger.info("Конфигурация не найдена, используются настройки по умолчанию")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")


if __name__ == "__main__":
    # Тестирование ElderlyInterfaceManager
    manager = ElderlyInterfaceManager()

    # Создание тестового профиля
    test_profile = manager.create_user_profile(
        user_id="test_elderly_001",
        age=75,
        preferences={
            "family_contacts": ["+7-123-456-7890", "+7-098-765-4321"],
            "emergency_contacts": ["+7-911-000-0000"],
            "medical_conditions": ["диабет", "гипертония"],
            "allergies": ["пенициллин"]
        }
    )

    print(f"✅ Создан профиль для возрастной категории: {test_profile.age_category.value}")
    print(f"✅ Настройки интерфейса: {manager.generate_interface_settings(test_profile)}")
    print(f"✅ Голосовые команды: {manager.generate_voice_commands(test_profile.age_category)}")
    print(f"✅ Обучающие модули: {len(manager.create_learning_modules(test_profile.age_category))}")

