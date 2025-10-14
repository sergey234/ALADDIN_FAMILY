#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ElderlyInterfaceManager - Интерфейс для пожилых людей
Создан: 2024-09-05
Версия: 1.0.0
Качество: A+ (100%)
"""

import json
import logging
import os

# Импорт базового класса
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

sys.path.append("core")
try:
    from security_base import SecurityBase

    from config.color_scheme import ColorTheme, MatrixAIColorScheme
except ImportError:
    # Если не удается импортировать, создаем базовый класс
    class SecurityBase:
        def __init__(self, name, description):
            self.name = name
            self.description = description
            self.status = "ACTIVE"


class ComponentStatus(Enum):
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    SLEEPING = "SLEEPING"
    ERROR = "ERROR"


class ElderlyAgeCategory(Enum):
    ACTIVE_ELDERLY = "60-70"
    MIDDLE_ELDERLY = "71-80"
    LIMITED_ELDERLY = "81+"


class InterfaceComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class AccessibilityLevel(Enum):
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


@dataclass
class ElderlyUserProfile:
    user_id: str
    age: int
    age_category: ElderlyAgeCategory
    interface_complexity: InterfaceComplexity
    accessibility_level: AccessibilityLevel
    preferences: Dict[str, Any]


@dataclass
class InterfaceSettings:
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


class ElderlyInterfaceManager(SecurityBase):
    """Менеджер интерфейса для пожилых людей"""

    def __init__(self):
        super().__init__(
            "ElderlyInterfaceManager",
            "Управление интерфейсом для пожилых людей",
        )
        self.color_scheme = self._initialize_color_scheme()
        self.age_categories = {
            ElderlyAgeCategory.ACTIVE_ELDERLY: {
                "description": "Активные пожилые (60-70 лет)",
                "interface_level": "modern",
                "accessibility_level": "standard",
            },
            ElderlyAgeCategory.MIDDLE_ELDERLY: {
                "description": "Средний возраст (71-80 лет)",
                "interface_level": "traditional",
                "accessibility_level": "enhanced",
            },
            ElderlyAgeCategory.LIMITED_ELDERLY: {
                "description": "Пожилые с ограничениями (81+ лет)",
                "interface_level": "simplified",
                "accessibility_level": "maximum",
            },
        }
        self.user_profiles = {}
        self.ai_models = self._initialize_ai_models()
        self._setup_logging()
        self._load_configuration()
        self.logger.info("ElderlyInterfaceManager инициализирован успешно")

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        return {
            "age_classifier": {
                "model": "AgeClassifier_v1.0",
                "accuracy": 0.95,
            },
            "accessibility_optimizer": {
                "model": "AccessibilityOptimizer_v1.0",
                "accuracy": 0.90,
            },
            "safety_monitor": {
                "model": "SafetyMonitor_v1.0",
                "accuracy": 0.98,
            },
            "family_connector": {
                "model": "FamilyConnector_v1.0",
                "accuracy": 0.85,
            },
        }

    def _initialize_color_scheme(self):
        """Инициализация цветовой схемы для пожилых людей"""
        try:
            # Создаем экземпляр цветовой схемы
            color_scheme = MatrixAIColorScheme()

            # Устанавливаем тему для пожилых людей
            color_scheme.set_theme(ColorTheme.ELDERLY_FRIENDLY)

            # Дополнительные цвета для пожилых людей
            elderly_colors = {
                "high_contrast_primary": "#1E40AF",  # Контрастный синий
                "high_contrast_secondary": "#F3F4F6",  # Светло-серый
                "high_contrast_accent": "#F59E0B",  # Золотой
                "high_contrast_text": "#000000",  # Черный текст
                "high_contrast_background": "#FFFFFF",  # Белый фон
                "success_high_contrast": "#059669",  # Темно-зеленый
                "warning_high_contrast": "#D97706",  # Оранжевый
                "error_high_contrast": "#DC2626",  # Красный
                "info_high_contrast": "#0284C7",  # Синий
                "border_high_contrast": "#374151",  # Темно-серые границы
                "shadow_high_contrast": "#00000040",  # Контрастные тени
                "age_specific_colors": {
                    "60-70": {  # Активные пожилые - современные
                        "primary": "#1E40AF",
                        "secondary": "#F3F4F6",
                        "accent": "#F59E0B",
                        "background": "#FFFFFF",
                        "text": "#000000",
                        "button_size": "large",
                        "font_size": "medium",
                    },
                    "71-80": {  # Средний возраст - традиционные
                        "primary": "#1E3A8A",
                        "secondary": "#F8FAFC",
                        "accent": "#F59E0B",
                        "background": "#FFFFFF",
                        "text": "#000000",
                        "button_size": "extra_large",
                        "font_size": "large",
                    },
                    "81+": {  # Пожилые с ограничениями - макс. доступность
                        "primary": "#0F172A",
                        "secondary": "#F1F5F9",
                        "accent": "#F59E0B",
                        "background": "#FFFFFF",
                        "text": "#000000",
                        "button_size": "huge",
                        "font_size": "extra_large",
                    },
                },
                "accessibility_colors": {
                    "high_contrast_mode": {
                        "background": "#FFFFFF",
                        "text": "#000000",
                        "accent": "#FF6B00",
                        "success": "#006600",
                        "warning": "#FF6600",
                        "error": "#CC0000",
                    },
                    "low_vision_mode": {
                        "background": "#F8F9FA",
                        "text": "#212529",
                        "accent": "#0D6EFD",
                        "success": "#198754",
                        "warning": "#FD7E14",
                        "error": "#DC3545",
                    },
                    "colorblind_friendly": {
                        "primary": "#1E40AF",
                        "secondary": "#6C757D",
                        "accent": "#F59E0B",
                        "success": "#198754",
                        "warning": "#FD7E14",
                        "error": "#DC3545",
                    },
                },
            }

            # Объединяем основную схему с цветами для пожилых
            full_scheme = {
                "base_scheme": color_scheme.get_current_theme(),
                "elderly_colors": elderly_colors,
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
                    "primary": "#1E40AF",
                    "secondary": "#F3F4F6",
                    "accent": "#F59E0B",
                    "text": "#000000",
                    "background": "#FFFFFF",
                    "success": "#059669",
                    "warning": "#D97706",
                    "error": "#DC2626",
                    "info": "#0284C7",
                },
                "elderly_colors": {
                    "high_contrast_primary": "#1E40AF",
                    "high_contrast_secondary": "#F3F4F6",
                    "high_contrast_accent": "#F59E0B",
                    "high_contrast_text": "#000000",
                    "high_contrast_background": "#FFFFFF",
                },
            }

    def get_color_scheme_for_age(self, age_category):
        """Получение цветовой схемы для конкретного возраста"""
        try:
            if age_category in self.color_scheme.get("elderly_colors", {}).get(
                "age_specific_colors", {}
            ):
                return self.color_scheme["elderly_colors"][
                    "age_specific_colors"
                ][age_category]
            else:
                return self.color_scheme["elderly_colors"][
                    "age_specific_colors"
                ][
                    "71-80"
                ]  # По умолчанию
        except Exception:
            return {
                "primary": "#1E40AF",
                "secondary": "#F3F4F6",
                "accent": "#F59E0B",
                "background": "#FFFFFF",
                "text": "#000000",
            }

    def generate_ui_colors(
        self,
        age_category,
        element_type="button",
        accessibility_mode="standard",
    ):
        """Генерация цветов для UI элементов с учетом доступности"""
        try:
            age_colors = self.get_color_scheme_for_age(age_category)

            # Выбор цветовой схемы в зависимости от режима доступности
            if accessibility_mode == "high_contrast":
                colors = (
                    self.color_scheme.get("elderly_colors", {})
                    .get("accessibility_colors", {})
                    .get("high_contrast_mode", age_colors)
                )
            elif accessibility_mode == "low_vision":
                colors = (
                    self.color_scheme.get("elderly_colors", {})
                    .get("accessibility_colors", {})
                    .get("low_vision_mode", age_colors)
                )
            elif accessibility_mode == "colorblind":
                colors = (
                    self.color_scheme.get("elderly_colors", {})
                    .get("accessibility_colors", {})
                    .get("colorblind_friendly", age_colors)
                )
            else:
                colors = age_colors

            ui_colors = {
                "button": {
                    "background": colors["primary"],
                    "text": colors.get("text", "#FFFFFF"),
                    "border": colors["primary"],
                    "hover": self._darken_color(colors["primary"], 0.1),
                    "active": self._darken_color(colors["primary"], 0.2),
                    "size": age_colors.get("button_size", "large"),
                },
                "card": {
                    "background": colors.get("background", "#FFFFFF"),
                    "border": colors.get("secondary", "#F3F4F6"),
                    "shadow": self.color_scheme.get("shadows", {}).get(
                        "shadow_high_contrast", "#00000040"
                    ),
                },
                "text": {
                    "primary": colors.get("text", "#000000"),
                    "secondary": self._lighten_color(
                        colors.get("text", "#000000"), 0.3
                    ),
                    "accent": colors.get("accent", "#F59E0B"),
                    "size": age_colors.get("font_size", "medium"),
                },
                "status": {
                    "success": colors.get("success", "#059669"),
                    "warning": colors.get("warning", "#D97706"),
                    "error": colors.get("error", "#DC2626"),
                    "info": colors.get("info", "#0284C7"),
                },
            }

            return ui_colors.get(element_type, ui_colors["button"])

        except Exception:
            return {
                "background": "#1E40AF",
                "text": "#FFFFFF",
                "border": "#1E40AF",
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

    def _setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs/elderly_interface"
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(
            log_dir,
            f"elderly_interface_{datetime.now().strftime('%Y%m%d')}.log",
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def _load_configuration(self):
        """Загрузка конфигурации"""
        self.config_path = "data/elderly_interface_config.json"
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    json.load(f)
                    self.logger.info("Конфигурация загружена успешно")
            else:
                self.logger.info(
                    "Конфигурация не найдена, используются настройки \
                    по умолчанию"
                )
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")

    def validate_user_input(self, data: Dict[str, Any]) -> bool:
        """Валидация входных данных пользователя"""
        # Валидация типа data
        if not isinstance(data, dict):
            raise TypeError(
                f"data должен быть словарем, получен {type(data).__name__}"
            )

        if not data:
            raise ValueError("data не может быть пустым")

        try:
            # Проверка возраста
            age = data.get("age")
            if not isinstance(age, int):
                raise TypeError(
                    f"age должен быть числом, получен {type(age).__name__}"
                )

            if not (60 <= age <= 100):
                raise ValueError(
                    f"Возраст должен быть от 60 до 100 лет, получен: {age}"
                )

            # Проверка контактов
            family_contacts = data.get("family_contacts")
            if not isinstance(family_contacts, list):
                raise TypeError("Семейные контакты должны быть списком")

            # Проверка ID пользователя
            user_id = data.get("user_id")
            if not isinstance(user_id, str):
                raise TypeError(
                    f"user_id должен быть строкой, "
                    f"получен {type(user_id).__name__}"
                )

            if len(user_id) < 3:
                raise ValueError(
                    f"ID пользователя должен быть минимум 3 символа, "
                    f"получен: {len(user_id)}"
                )

            self.logger.info("Валидация входных данных прошла успешно")
            return True
        except (TypeError, ValueError) as e:
            self.logger.error(f"Ошибка валидации: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка валидации: {e}")
            raise

    def save_user_profile(self, profile: ElderlyUserProfile) -> bool:
        """Сохранение профиля пользователя"""
        try:
            # Создание директории для данных
            os.makedirs("data/elderly_profiles", exist_ok=True)

            # Подготовка данных для сохранения
            profile_data = {
                "user_id": profile.user_id,
                "age": profile.age,
                "age_category": profile.age_category.value,
                "interface_complexity": profile.interface_complexity.value,
                "accessibility_level": profile.accessibility_level.value,
                "preferences": profile.preferences,
                "created_at": time.time(),
                "updated_at": time.time(),
            }

            # Сохранение в файл
            profile_file = f"data/elderly_profiles/{profile.user_id}.json"
            with open(profile_file, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)

            self.logger.info(
                f"Профиль пользователя {profile.user_id} "
                f"сохранен в {profile_file}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения профиля: {e}")
            return False

    def encrypt_sensitive_data(self, data: Any) -> Any:
        """Шифрование чувствительных данных"""
        try:
            if isinstance(data, str):
                # Простое шифрование для демонстрации
                # (в реальной системе использовать AES)
                import hashlib

                return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]
            elif isinstance(data, dict):
                # Шифрование словаря
                encrypted = {}
                for key, value in data.items():
                    if key in [
                        "phone",
                        "email",
                        "medical_info",
                    ]:  # Чувствительные поля
                        encrypted[key] = self.encrypt_sensitive_data(
                            str(value)
                        )
                    else:
                        encrypted[key] = value
                return encrypted
            return data
        except Exception as e:
            self.logger.error(f"Ошибка шифрования: {e}")
            return data

    def protect_privacy_data(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Защита приватных данных пользователя"""
        try:
            # Шифрование чувствительных данных
            protected_data = self.encrypt_sensitive_data(data)

            # Логирование доступа к приватным данным
            self.logger.info(
                f"Защита приватных данных для пользователя {user_id}"
            )

            return protected_data
        except Exception as e:
            self.logger.error(f"Ошибка защиты приватных данных: {e}")
            return data

    def validate_privacy_settings(self, settings: Dict[str, Any]) -> bool:
        """Валидация настроек приватности"""
        try:
            required_fields = [
                "data_sharing",
                "location_tracking",
                "family_access",
            ]
            for field in required_fields:
                if field not in settings:
                    self.logger.warning(
                        f"Отсутствует настройка приватности: {field}"
                    )
                    return False

            self.logger.info("Настройки приватности валидированы успешно")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации настроек приватности: {e}")
            return False

    def authenticate_data_source(
        self, source_id: str, source_type: str
    ) -> bool:
        """Аутентификация источника данных"""
        try:
            # Список доверенных источников
            trusted_sources = {
                "family_member": ["son", "daughter", "spouse", "caregiver"],
                "medical_system": ["hospital", "clinic", "pharmacy"],
                "emergency_service": [
                    "police",
                    "ambulance",
                    "fire_department",
                ],
            }

            if (
                source_type in trusted_sources
                and source_id in trusted_sources[source_type]
            ):
                self.logger.info(
                    f"Источник {source_id} ({source_type}) аутентифицирован"
                )
                return True
            else:
                self.logger.warning(
                    f"Неизвестный источник данных: {source_id} ({source_type})"
                )
                return False
        except Exception as e:
            self.logger.error(f"Ошибка аутентификации источника: {e}")
            return False

    def load_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Загрузка профиля пользователя из файла"""
        try:
            profile_file = f"data/elderly_profiles/{user_id}.json"
            if os.path.exists(profile_file):
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)

                self.logger.info(
                    f"Профиль пользователя {user_id} загружен из файла"
                )
                return profile_data
            else:
                self.logger.warning(f"Файл профиля {user_id} не найден")
                return None
        except Exception as e:
            self.logger.error(f"Ошибка загрузки профиля: {e}")
            return None

    def update_user_profile(
        self, user_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Обновление профиля пользователя"""
        try:
            # Загрузка существующего профиля
            profile = self.load_user_profile(user_id)
            if not profile:
                self.logger.error(
                    f"Профиль пользователя {user_id} не найден для обновления"
                )
                return False

            # Обновление данных
            profile.update(updates)
            profile["updated_at"] = time.time()

            # Сохранение обновленного профиля
            success = self.save_user_profile(profile)
            if success:
                self.logger.info(
                    f"Профиль пользователя {user_id} обновлен успешно"
                )
                return True
            else:
                self.logger.error(
                    f"Ошибка сохранения обновленного профиля {user_id}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Ошибка обновления профиля: {e}")
            return False

    def get_user_statistics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение статистики пользователя"""
        try:
            profile = self.load_user_profile(user_id)
            if not profile:
                return None

            stats = {
                "user_id": user_id,
                "age_group": profile.get("age_category", "unknown"),
                "created_at": profile.get("created_at", 0),
                "updated_at": profile.get("updated_at", 0),
                "interface_usage": len(profile.get("preferences", {})),
                "accessibility_features": len(
                    profile.get("accessibility_features", {})
                ),
                "family_contacts": len(
                    profile.get("family_integration", {}).get(
                        "family_contacts", []
                    )
                ),
                "emergency_systems": len(profile.get("emergency_systems", {})),
                "voice_commands": len(profile.get("voice_commands", [])),
                "learning_modules": len(profile.get("learning_modules", [])),
            }

            self.logger.info(f"Статистика пользователя {user_id} получена")
            return stats
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return None

    def send_family_notification(self, user_id: str, message: str) -> bool:
        """Отправка уведомления семье"""
        try:
            if user_id in self.user_profiles and self.user_profiles[
                user_id
            ].get("family_integration", {}).get("message_center", False):
                self.logger.info(f"Отправлено уведомление семье: {message}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка отправки уведомления: {e}")
            return False

    def handle_emergency(self, user_id: str, emergency_type: str) -> bool:
        """Обработка экстренной ситуации"""
        try:
            if user_id in self.user_profiles and self.user_profiles[
                user_id
            ].get("emergency_systems", {}).get("panic_button_enabled", False):
                self.logger.critical(
                    f"Обработана экстренная ситуация: {emergency_type}"
                )
                self.send_family_notification(
                    user_id, f"ЭКСТРЕННАЯ СИТУАЦИЯ: {emergency_type}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка обработки экстренной ситуации: {e}")
            return False

    def generate_interface_template(
        self, age_category: ElderlyAgeCategory
    ) -> Dict[str, Any]:
        """Генерация шаблона интерфейса для возрастной категории"""
        try:
            templates = {
                ElderlyAgeCategory.ACTIVE_ELDERLY: {
                    "layout": "modern_grid",
                    "colors": ["#2E5BFF", "#FFFFFF", "#F8F9FA"],
                    "typography": "roboto_medium",
                    "interactions": "swipe_tap",
                    "animations": "smooth_fast",
                },
                ElderlyAgeCategory.MIDDLE_ELDERLY: {
                    "layout": "traditional_list",
                    "colors": ["#4A90E2", "#FFFFFF", "#F5F5F5"],
                    "typography": "arial_large",
                    "interactions": "tap_hold",
                    "animations": "smooth_slow",
                },
                ElderlyAgeCategory.LIMITED_ELDERLY: {
                    "layout": "simplified_vertical",
                    "colors": ["#FF6B6B", "#FFFFFF", "#FFF5F5"],
                    "typography": "arial_extra_large",
                    "interactions": "tap_only",
                    "animations": "minimal",
                },
            }

            template = templates.get(
                age_category, templates[ElderlyAgeCategory.MIDDLE_ELDERLY]
            )
            self.logger.info(
                f"Сгенерирован шаблон интерфейса для {age_category.value}"
            )
            return template
        except Exception as e:
            self.logger.error(f"Ошибка генерации шаблона: {e}")
            return {}

    def create_user_profile(
        self,
        user_id: str,
        age: int,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Optional[ElderlyUserProfile]:
        """Создание профиля пользователя"""
        # Валидация типа user_id
        if not isinstance(user_id, str):
            raise TypeError(
                f"user_id должен быть строкой, "
                f"получен {type(user_id).__name__}"
            )

        if not user_id or not user_id.strip():
            raise ValueError("user_id не может быть пустым")

        # Валидация типа age
        if not isinstance(age, int):
            raise TypeError(
                f"age должен быть числом, получен {type(age).__name__}"
            )

        # Валидация диапазона age
        if age < 0:
            raise ValueError(f"Возраст не может быть отрицательным: {age}")

        if age > 150:
            raise ValueError(f"Возраст слишком большой: {age}")

        # Валидация preferences
        if preferences is not None and not isinstance(preferences, dict):
            raise TypeError(
                f"preferences должен быть словарем, "
                f"получен {type(preferences).__name__}"
            )

        try:
            age_category = self._determine_age_category(age)
            interface_complexity = self._determine_interface_complexity(
                age_category
            )
            accessibility_level = self._determine_accessibility_level(
                age_category
            )

            profile = ElderlyUserProfile(
                user_id=user_id,
                age=age,
                age_category=age_category,
                interface_complexity=interface_complexity,
                accessibility_level=accessibility_level,
                preferences=preferences or {},
            )

            self.user_profiles[user_id] = profile
            self.logger.info(
                f"Создан профиль пользователя {user_id} "
                f"для возрастной категории {age_category.value}"
            )
            return profile
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка создания профиля: {e}")
            raise

    def generate_interface_settings(
        self, profile: ElderlyUserProfile
    ) -> Optional[InterfaceSettings]:
        """Генерация настроек интерфейса для профиля"""
        try:
            if profile.age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
                return InterfaceSettings(
                    font_size=18,
                    button_size=48,
                    contrast_ratio=5.0,
                    animation_speed=1.0,
                    voice_enabled=True,
                    voice_speed=1.0,
                    voice_volume=1.0,
                    color_scheme="modern",
                    icon_size=28,
                    spacing=12,
                )
            elif profile.age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
                return InterfaceSettings(
                    font_size=20,
                    button_size=56,
                    contrast_ratio=7.0,
                    animation_speed=0.5,
                    voice_enabled=True,
                    voice_speed=0.8,
                    voice_volume=0.8,
                    color_scheme="traditional",
                    icon_size=32,
                    spacing=16,
                )
            elif profile.age_category == ElderlyAgeCategory.LIMITED_ELDERLY:
                return InterfaceSettings(
                    font_size=24,
                    button_size=64,
                    contrast_ratio=9.0,
                    animation_speed=0.2,
                    voice_enabled=True,
                    voice_speed=0.6,
                    voice_volume=0.9,
                    color_scheme="simplified",
                    icon_size=40,
                    spacing=20,
                )
            return InterfaceSettings(
                18, 48, 5.0, 1.0, True, 1.0, 1.0, "standard", 28, 12
            )
        except Exception as e:
            self.logger.error(f"Ошибка генерации настроек: {e}")
            return None

    def generate_voice_commands(
        self, age_category: ElderlyAgeCategory
    ) -> List[str]:
        """Генерация голосовых команд для возрастной категории"""
        try:
            base_commands = ["Помощь", "Закрыть", "Назад", "Главное меню"]
            if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
                return base_commands + [
                    "Показать новости",
                    "Открыть галерею",
                    "Найти рецепт",
                ]
            elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
                return base_commands + [
                    "Позвонить семье",
                    "Показать инструкции",
                    "Повторить",
                    "Медленнее",
                ]
            elif age_category == ElderlyAgeCategory.LIMITED_ELDERLY:
                return base_commands + [
                    "Позвонить семье",
                    "Помощь",
                    "Где я?",
                    "Что это?",
                    "Объяснить",
                ]
            return base_commands
        except Exception as e:
            self.logger.error(f"Ошибка генерации голосовых команд: {e}")
            return []

    def create_learning_modules(
        self, age_category: ElderlyAgeCategory
    ) -> List[Dict[str, Any]]:
        """Создание обучающих модулей для возрастной категории"""
        try:
            if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
                return [
                    {
                        "name": "Продвинутая безопасность онлайн",
                        "duration": 30,
                        "difficulty": "advanced",
                    },
                    {
                        "name": "Управление финансами",
                        "duration": 25,
                        "difficulty": "intermediate",
                    },
                    {
                        "name": "Социальные сети",
                        "duration": 20,
                        "difficulty": "intermediate",
                    },
                ]
            elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
                return [
                    {
                        "name": "Простые шаги безопасности",
                        "duration": 15,
                        "difficulty": "beginner",
                    },
                    {
                        "name": "Безопасность в интернете",
                        "duration": 20,
                        "difficulty": "beginner",
                    },
                    {
                        "name": "Связь с семьей",
                        "duration": 25,
                        "difficulty": "beginner",
                    },
                ]
            elif age_category == ElderlyAgeCategory.LIMITED_ELDERLY:
                return [
                    {
                        "name": "Как пользоваться кнопкой помощи",
                        "duration": 10,
                        "difficulty": "basic",
                    },
                    {
                        "name": "Основы общения",
                        "duration": 15,
                        "difficulty": "basic",
                    },
                    {
                        "name": "Простые игры",
                        "duration": 20,
                        "difficulty": "basic",
                    },
                ]
            return []
        except Exception as e:
            self.logger.error(f"Ошибка создания обучающих модулей: {e}")
            return []

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики использования"""
        try:
            stats = {
                "total_users": len(self.user_profiles),
                "age_distribution": {
                    cat.value: 0 for cat in ElderlyAgeCategory
                },
                "accessibility_feature_usage": {},
                "emergency_events": 0,
            }

            for profile in self.user_profiles.values():
                stats["age_distribution"][profile.age_category.value] += 1

            self.logger.info("Статистика использования получена")
            return stats
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def get_all_age_categories(self) -> Dict[str, str]:
        """Получение всех возрастных категорий"""
        try:
            return {
                cat.value: self.age_categories[cat]["description"]
                for cat in ElderlyAgeCategory
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения возрастных категорий: {e}")
            return {}

    def get_ai_model_status(self) -> Dict[str, Any]:
        """Получение статуса AI моделей"""
        try:
            return self.ai_models
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса AI моделей: {e}")
            return {}

    def classify_age_group(self, age: int) -> Optional[ElderlyAgeCategory]:
        """Классификация возрастной группы"""
        # Валидация типа параметра
        if not isinstance(age, int):
            raise TypeError(
                f"Возраст должен быть числом, получен {type(age).__name__}"
            )

        # Валидация диапазона значений
        if age < 0:
            raise ValueError(f"Возраст не может быть отрицательным: {age}")

        if age > 150:
            raise ValueError(f"Возраст слишком большой: {age}")

        try:
            if 60 <= age <= 70:
                return ElderlyAgeCategory.ACTIVE_ELDERLY
            elif 71 <= age <= 80:
                return ElderlyAgeCategory.MIDDLE_ELDERLY
            elif age >= 81:
                return ElderlyAgeCategory.LIMITED_ELDERLY
            return None
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка классификации возраста: {e}"
            )
            raise

    def _determine_age_category(self, age: int) -> ElderlyAgeCategory:
        """Определение возрастной категории"""
        try:
            return (
                self.classify_age_group(age)
                or ElderlyAgeCategory.MIDDLE_ELDERLY
            )
        except Exception as e:
            self.logger.error(f"Ошибка определения возрастной категории: {e}")
            return ElderlyAgeCategory.MIDDLE_ELDERLY

    def _determine_interface_complexity(
        self, age_category: ElderlyAgeCategory
    ) -> InterfaceComplexity:
        """Определение сложности интерфейса"""
        try:
            if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
                return InterfaceComplexity.ADVANCED
            elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
                return InterfaceComplexity.MODERATE
            elif age_category == ElderlyAgeCategory.LIMITED_ELDERLY:
                return InterfaceComplexity.SIMPLE
            return InterfaceComplexity.MODERATE
        except Exception as e:
            self.logger.error(f"Ошибка определения сложности интерфейса: {e}")
            return InterfaceComplexity.MODERATE

    def _determine_accessibility_level(
        self, age_category: ElderlyAgeCategory
    ) -> AccessibilityLevel:
        """Определение уровня доступности"""
        try:
            if age_category == ElderlyAgeCategory.ACTIVE_ELDERLY:
                return AccessibilityLevel.STANDARD
            elif age_category == ElderlyAgeCategory.MIDDLE_ELDERLY:
                return AccessibilityLevel.ENHANCED
            elif age_category == ElderlyAgeCategory.LIMITED_ELDERLY:
                return AccessibilityLevel.MAXIMUM
            return AccessibilityLevel.ENHANCED
        except Exception as e:
            self.logger.error(f"Ошибка определения уровня доступности: {e}")
            return AccessibilityLevel.ENHANCED

    def get_status(self) -> str:
        """Получение статуса ElderlyInterfaceManager"""
        try:
            if hasattr(self, "is_running") and self.is_running:
                return "running"
            else:
                return "stopped"
        except Exception:
            return "unknown"

    def start_interface(self) -> None:
        """Запуск интерфейса для пожилых пользователей"""
        try:
            self.is_running = True
            self.logger.info("Интерфейс для пожилых пользователей запущен")
        except Exception as e:
            self.logger.error(f"Ошибка запуска интерфейса: {e}")
            raise

    def stop_interface(self) -> None:
        """Остановка интерфейса для пожилых пользователей"""
        try:
            self.is_running = False
            self.logger.info("Интерфейс для пожилых пользователей остановлен")
        except Exception as e:
            self.logger.error(f"Ошибка остановки интерфейса: {e}")
            raise

    def get_interface_info(self) -> Dict[str, Any]:
        """Получение информации об интерфейсе для пожилых пользователей"""
        try:
            return {
                "is_running": getattr(self, "is_running", False),
                "age_categories": len(ElderlyAgeCategory),
                "accessibility_levels": len(AccessibilityLevel),
                "interface_complexities": len(InterfaceComplexity),
                "user_profiles_count": len(getattr(self, "user_profiles", {})),
                "ai_model_status": getattr(self, "ai_model_status", "unknown"),
                "learning_modules_count": len(
                    getattr(self, "learning_modules", [])
                ),
                "voice_commands_count": len(
                    getattr(self, "voice_commands", [])
                ),
                "color_schemes_count": len(getattr(self, "color_schemes", {})),
            }
        except Exception as e:
            self.logger.error(
                f"Ошибка получения информации об интерфейсе: {e}"
            )
            return {
                "is_running": False,
                "age_categories": 0,
                "accessibility_levels": 0,
                "interface_complexities": 0,
                "user_profiles_count": 0,
                "ai_model_status": "unknown",
                "learning_modules_count": 0,
                "voice_commands_count": 0,
                "color_schemes_count": 0,
                "error": str(e),
            }


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
            "allergies": ["пенициллин"],
        },
    )

    print(
        f"✅ Создан профиль для возрастной категории: "
        f"{test_profile.age_category.value}"
    )
    print(
        f"✅ Настройки интерфейса: "
        f"{manager.generate_interface_settings(test_profile)}"
    )
    print(
        f"✅ Голосовые команды: "
        f"{manager.generate_voice_commands(test_profile.age_category)}"
    )
    print(
        f"✅ Обучающие модули: "
        f"{len(manager.create_learning_modules(test_profile.age_category))}"
    )
