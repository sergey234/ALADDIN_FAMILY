#!/usr/bin/env python3
"""
ALADDIN VPN - Graceful Degradation Module
Модуль graceful degradation для VPN системы
"""

# Основные классы
from .graceful_degradation import GracefulDegradationManager, ServiceConfig, DegradationRule

# Перечисления
from .graceful_degradation import DegradationLevel, ServiceStatus

# Декораторы
from .graceful_degradation import graceful_degradation

# Контекстные менеджеры
from .graceful_degradation import degradation_context

# Предустановленные правила
from .graceful_degradation import create_default_degradation_rules, create_default_manager

# Вспомогательные функции
from .graceful_degradation import get_degradation_status

__all__ = [
    # Основные классы
    "GracefulDegradationManager", "ServiceConfig", "DegradationRule",

    # Перечисления
    "DegradationLevel", "ServiceStatus",

    # Декораторы
    "graceful_degradation",

    # Контекстные менеджеры
    "degradation_context",

    # Предустановленные правила
    "create_default_degradation_rules", "create_default_manager",

    # Вспомогательные функции
    "get_degradation_status"
]
