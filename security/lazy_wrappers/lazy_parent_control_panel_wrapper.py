"""
LazyInitializer wrapper для parent_control_panel.py
Автоматически сгенерирован: 2025-10-05 12:49:39
"""

import os
import sys
import time
import threading
from typing import Any, Optional

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LazyInitializer:
    """Ленивая инициализация для parent_control_panel.py"""
    
    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()
        self._creation_time = None
        self._access_count = 0
        self._file_path = 'security/ai_agents/parent_control_panel.py'
    
    def get(self) -> Any:
        """Получение экземпляра с ленивой инициализацией"""
        self._access_count += 1
        
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    start_time = time.time()
                    try:
                        # Динамическая загрузка модуля
                        module_name = 'parent_control_panel'  # убираем .py
                        if module_name not in sys.modules:
                            import importlib.util
                            spec = importlib.util.spec_from_file_location(module_name, self._file_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            sys.modules[module_name] = module
                        
                        # Получаем основной класс из модуля
                        module = sys.modules[module_name]
                        main_class = None
                        
                        # Ищем основной класс (обычно с именем файла)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                not attr_name.startswith('_') and 
                                attr_name.lower().replace('_', '') in 'parentcontrolpanel'):
                                main_class = attr
                                break
                        
                        if main_class:
                            self._instance = main_class()
                        else:
                            # Если класс не найден, возвращаем модуль
                            self._instance = module
                        
                        self._creation_time = time.time() - start_time
                        print(f'LazyInitializer: parent_control_panel.py загружен за {self._creation_time:.3f}с')
                        
                    except Exception as e:
                        print(f'Ошибка загрузки parent_control_panel.py: {e}')
                        self._instance = None
        
        return self._instance
    
    def reset(self) -> None:
        """Сброс экземпляра"""
        with self._lock:
            self._instance = None
            self._creation_time = None
    
    def get_stats(self) -> dict:
        """Статистика использования"""
        return {
            'file': 'parent_control_panel.py',
            'access_count': self._access_count,
            'creation_time': self._creation_time,
            'is_initialized': self._instance is not None
        }

# Создаем глобальный экземпляр
lazy_parent_control_panel = LazyInitializer()

def get_parent_control_panel():
    """Получение parent_control_panel.py через LazyInitializer"""
    return lazy_parent_control_panel.get()

def reset_parent_control_panel():
    """Сброс parent_control_panel.py"""
    lazy_parent_control_panel.reset()

def get_parent_control_panel_stats():
    """Статистика parent_control_panel.py"""
    return lazy_parent_control_panel.get_stats()
