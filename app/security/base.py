#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый класс системы безопасности ALADDIN
"""


class SecurityBase:
    """Базовый класс для всех компонентов системы безопасности"""
    
    def __init__(self, name: str = "SecurityBase"):
        """Инициализация базового класса безопасности"""
        self.name = name
    
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
            print(f"Ошибка валидации безопасности: {e}")
            return False
