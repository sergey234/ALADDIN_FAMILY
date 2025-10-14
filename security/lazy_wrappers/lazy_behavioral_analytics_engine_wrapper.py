"""
LazyInitializer wrapper для behavioral_analytics_engine.py
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
    """Ленивая инициализация для behavioral_analytics_engine.py"""
    
    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()
        self._creation_time = None
        self._access_count = 0
        self._file_path = 'security/ai_agents/behavioral_analytics_engine.py'
    
    def get(self) -> Any:
        """Получение экземпляра с ленивой инициализацией"""
        self._access_count += 1
        
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    start_time = time.time()
                    try:
                        # Динамическая загрузка модуля
                        module_name = 'behavioral_analytics_engine'  # убираем .py
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
                                attr_name.lower().replace('_', '') in 'behavioralanalyticsengine'):
                                main_class = attr
                                break
                        
                        if main_class:
                            self._instance = main_class()
                        else:
                            # Если класс не найден, возвращаем модуль
                            self._instance = module
                        
                        self._creation_time = time.time() - start_time
                        print(f'LazyInitializer: behavioral_analytics_engine.py загружен за {self._creation_time:.3f}с')
                        
                    except Exception as e:
                        print(f'Ошибка загрузки behavioral_analytics_engine.py: {e}')
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
            'file': 'behavioral_analytics_engine.py',
            'access_count': self._access_count,
            'creation_time': self._creation_time,
            'is_initialized': self._instance is not None
        }

# Создаем глобальный экземпляр
lazy_behavioral_analytics_engine = LazyInitializer()

def get_behavioral_analytics_engine():
    """Получение behavioral_analytics_engine.py через LazyInitializer"""
    return lazy_behavioral_analytics_engine.get()

def reset_behavioral_analytics_engine():
    """Сброс behavioral_analytics_engine.py"""
    lazy_behavioral_analytics_engine.reset()

def get_behavioral_analytics_engine_stats():
    """Статистика behavioral_analytics_engine.py"""
    return lazy_behavioral_analytics_engine.get_stats()
