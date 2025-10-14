"""
LazyInitializer wrapper для compliance_agent.py
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
    """Ленивая инициализация для compliance_agent.py"""
    
    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()
        self._creation_time = None
        self._access_count = 0
        self._file_path = 'security/ai_agents/compliance_agent.py'
    
    def get(self) -> Any:
        """Получение экземпляра с ленивой инициализацией"""
        self._access_count += 1
        
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    start_time = time.time()
                    try:
                        # Динамическая загрузка модуля
                        module_name = 'compliance_agent'  # убираем .py
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
                                attr_name.lower().replace('_', '') in 'complianceagent'):
                                main_class = attr
                                break
                        
                        if main_class:
                            self._instance = main_class()
                        else:
                            # Если класс не найден, возвращаем модуль
                            self._instance = module
                        
                        self._creation_time = time.time() - start_time
                        print(f'LazyInitializer: compliance_agent.py загружен за {self._creation_time:.3f}с')
                        
                    except Exception as e:
                        print(f'Ошибка загрузки compliance_agent.py: {e}')
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
            'file': 'compliance_agent.py',
            'access_count': self._access_count,
            'creation_time': self._creation_time,
            'is_initialized': self._instance is not None
        }

# Создаем глобальный экземпляр
lazy_compliance_agent = LazyInitializer()

def get_compliance_agent():
    """Получение compliance_agent.py через LazyInitializer"""
    return lazy_compliance_agent.get()

def reset_compliance_agent():
    """Сброс compliance_agent.py"""
    lazy_compliance_agent.reset()

def get_compliance_agent_stats():
    """Статистика compliance_agent.py"""
    return lazy_compliance_agent.get_stats()
