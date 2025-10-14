# -*- coding: utf-8 -*-
"""
Тестовый файл с ошибками для демонстрации безопасного анализатора
"""

import os
import sys
from typing import List, Dict, Any

class TestClass:
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_data(self, item: str) -> None:
        self.data.append(item)
    
    def get_data(self) -> List[str]:
        return self.data

def test_function(x: int, y: int) -> int:
    return x + y

def another_function():
    # Длинная строка, которая превышает 79 символов и должна вызвать ошибку E501
    result = "Это очень длинная строка, которая превышает рекомендуемую длину в 79 символов и должна вызвать ошибку E501"
    return result

def function_with_whitespace():
    # Функция с пробелами в конце строки (W293)
    data = "test"    
    return data

def function_without_newline():
    # Функция без перевода строки в конце (W292)
    return "no newline"

# Глобальная переменная
global_var = "test"