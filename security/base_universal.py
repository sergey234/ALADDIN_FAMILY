#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс системы безопасности ALADDIN
"""
import logging
from typing import Optional, Dict, Any

class SecurityBase:
    """Базовый класс для всех компонентов системы безопасности"""
    
    def __init__(self, *args, **kwargs):
        """
        Универсальный инициализатор для поддержки различных сигнатур:
        1. __init__(self, config) - старые агенты
        2. __init__(self, name) - некоторые агенты
        3. __init__(self, name, config) - новые агенты
        4. __init__(self, config, name) - мой новый формат
        """
        self.config = {}
        self.name = "SecurityBase"
        
        # Обработка позиционных аргументов
        if len(args) > 0:
            arg1 = args[0]
            if isinstance(arg1, dict):
                self.config = arg1
            elif isinstance(arg1, str):
                self.name = arg1
        
        if len(args) > 1:
            arg2 = args[1]
            if isinstance(arg2, dict):
                self.config = arg2
            elif isinstance(arg2, str):
                self.name = arg2
                
        # Обработка именованных аргументов (перекрывают позиционные)
        if "config" in kwargs:
            self.config = kwargs["config"] or {}
        if "name" in kwargs:
            self.name = kwargs["name"]
            
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
