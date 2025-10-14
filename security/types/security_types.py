#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Security Types
Базовые типы данных для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-04
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IncidentSeverity(Enum):
    """Уровни серьезности инцидентов"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel(Enum):
    """Уровни угроз"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FamilyRole(Enum):
    """Роли в семье"""
    PARENT = "parent"
    CHILD = "child"
    ELDERLY = "elderly"
    GUARDIAN = "guardian"


class AgeGroup(Enum):
    """Возрастные группы"""
    TODDLER = "toddler"  # 1-3 года
    CHILD = "child"      # 3-6 лет
    TEEN = "teen"        # 6-12 лет
    ADULT = "adult"      # 12-18 лет


class ContentCategory(Enum):
    """Категории контента"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    SOCIAL = "social"
    NEWS = "news"
    SHOPPING = "shopping"
    FINANCE = "finance"


@dataclass
class SecurityEvent:
    """Событие безопасности"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: IncidentSeverity
    description: str
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserSessionRecord:
    """Запись пользовательской сессии"""
    id: str
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class VPNSecurityError(Exception):
    """Ошибка безопасности VPN"""
    pass


class MatrixAIColorScheme:
    """Цветовая схема Matrix AI"""
    
    def __init__(self):
        self.colors = {
            'primary': '#00ff00',
            'secondary': '#00cc00',
            'accent': '#ff0000',
            'background': '#000000',
            'text': '#ffffff'
        }
    
    def set_theme(self, theme):
        """Установить тему"""
        pass


class ColorTheme(Enum):
    """Темы цветов"""
    MATRIX_AI = "matrix_ai"
    DARK = "dark"
    LIGHT = "light"
    CUSTOM = "custom"


class FamilyProfileManager:
    """Менеджер семейных профилей"""
    
    def __init__(self):
        self.profiles = {}
    
    def create_profile(self, profile_data):
        """Создать профиль"""
        pass
    
    def get_profile(self, profile_id):
        """Получить профиль"""
        pass


class ChildProtection:
    """Защита детей"""
    
    def __init__(self):
        self.protection_level = "high"
    
    def enable_protection(self):
        """Включить защиту"""
        pass


class ElderlyProtection:
    """Защита пожилых"""
    
    def __init__(self):
        self.protection_level = "medium"
    
    def enable_protection(self):
        """Включить защиту"""
        pass


class ConfigurationManager:
    """Менеджер конфигурации"""
    pass


class Logger:
    """Логгер"""
    pass


class SecurityManager:
    """Менеджер безопасности"""
    pass


class AuthenticationManager:
    """Менеджер аутентификации"""
    pass


class MonitoringManager:
    """Менеджер мониторинга"""
    pass