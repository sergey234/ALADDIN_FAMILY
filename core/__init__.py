# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Core Module
Основной модуль системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

__version__ = "1.0.0"
__author__ = "ALADDIN Security Team"
__description__ = "Core Module for ALADDIN Family Security System"

# Основные компоненты core модуля
from .base import CoreBase, SecurityBase, ServiceBase, ComponentStatus

__all__ = ["CoreBase", "ServiceBase", "SecurityBase", "ComponentStatus"]
