#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс системы безопасности ALADDIN
"""
import logging
from typing import Optional, Dict, Any

class SecurityBase:
    """Базовый класс для всех компонентов системы безопасности"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, name: str = "SecurityBase"):
        """
        Инициализация базового класса безопасности
        
        Args:
            config: Словарь конфигурации
            name: Имя компонента
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_name(self) -> str:
        """Возвращает имя компонента"""
        return self.name
    
    def validate_security(self) -> bool:
        """Базовая проверка безопасности"""
        try:
            # Базовая проверка безопасности
            if not self.name or len(self.name.strip()) == 0:
                return False
            return True
        except Exception as e:
            # Логирование ошибки (в реальной системе здесь был бы logger)
            self.logger.error(f"Ошибка валидации безопасности: {e}")
            return False
