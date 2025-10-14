# -*- coding: utf-8 -*-
"""
Lazy Wrappers - Главный файл системы ленивой загрузки
Управляет всеми lazy wrappers в системе ALADDIN
"""

import asyncio
import importlib
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
import threading
import weakref

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LazyWrapper:
    """Базовый класс для ленивой загрузки компонентов"""
    
    def __init__(self, module_path: str, class_name: str, *args, **kwargs):
        """Инициализация lazy wrapper"""
        self.module_path = module_path
        self.class_name = class_name
        self.args = args
        self.kwargs = kwargs
        self._instance = None
        self._loading = False
        self._load_time = None
        self._error = None
        self._lock = threading.Lock()
        
    def __getattr__(self, name: str) -> Any:
        """Ленивая загрузка атрибута"""
        if self._instance is None and not self._loading:
            self._load_instance()
        
        if self._instance is None:
            raise AttributeError(f"Component not loaded: {name}")
        
        return getattr(self._instance, name)
    
    def _load_instance(self) -> None:
        """Загрузка экземпляра компонента"""
        with self._lock:
            if self._instance is not None or self._loading:
                return
            
            self._loading = True
            try:
                # Динамический импорт модуля
                module = importlib.import_module(self.module_path)
                class_obj = getattr(module, self.class_name)
                
                # Создание экземпляра
                self._instance = class_obj(*self.args, **self.kwargs)
                self._load_time = time.time()
                
                logger.info(f"Lazy loaded: {self.module_path}.{self.class_name}")
                
            except Exception as e:
                self._error = str(e)
                logger.error(f"Failed to load {self.module_path}.{self.class_name}: {e}")
            finally:
                self._loading = False
    
    def is_loaded(self) -> bool:
        """Проверка загружен ли компонент"""
        return self._instance is not None
    
    def get_load_time(self) -> Optional[float]:
        """Получение времени загрузки"""
        return self._load_time
    
    def get_error(self) -> Optional[str]:
        """Получение ошибки загрузки"""
        return self._error
    
    def force_load(self) -> bool:
        """Принудительная загрузка"""
        if self._instance is None:
            self._load_instance()
        return self._instance is not None
    
    def unload(self) -> None:
        """Выгрузка компонента"""
        with self._lock:
            if self._instance is not None:
                # Попытка вызвать cleanup если есть
                if hasattr(self._instance, 'cleanup'):
                    try:
                        self._instance.cleanup()
                    except Exception as e:
                        logger.warning(f"Cleanup failed for {self.module_path}.{self.class_name}: {e}")
                
                self._instance = None
                self._load_time = None
                self._error = None
    
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о wrapper"""
        return {
            'module_path': self.module_path,
            'class_name': self.class_name,
            'is_loaded': self.is_loaded(),
            'load_time': self._load_time,
            'error': self._error,
            'args_count': len(self.args),
            'kwargs_count': len(self.kwargs)
        }

class LazyWrapperManager:
    """Менеджер для управления всеми lazy wrappers"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.wrappers: Dict[str, LazyWrapper] = {}
        self.load_stats = {
            'total_wrappers': 0,
            'loaded_wrappers': 0,
            'failed_wrappers': 0,
            'total_load_time': 0.0
        }
        self._lock = threading.Lock()
        
    def create_wrapper(self, name: str, module_path: str, class_name: str, 
                      *args, **kwargs) -> LazyWrapper:
        """Создание нового wrapper"""
        with self._lock:
            if name in self.wrappers:
                logger.warning(f"Wrapper {name} already exists, replacing...")
            
            wrapper = LazyWrapper(module_path, class_name, *args, **kwargs)
            self.wrappers[name] = wrapper
            self.load_stats['total_wrappers'] += 1
            
            logger.info(f"Created wrapper: {name} -> {module_path}.{class_name}")
            return wrapper
    
    def get_wrapper(self, name: str) -> Optional[LazyWrapper]:
        """Получение wrapper по имени"""
        return self.wrappers.get(name)
    
    def load_wrapper(self, name: str) -> bool:
        """Загрузка wrapper"""
        wrapper = self.get_wrapper(name)
        if wrapper is None:
            logger.error(f"Wrapper {name} not found")
            return False
        
        success = wrapper.force_load()
        if success:
            self.load_stats['loaded_wrappers'] += 1
            if wrapper.get_load_time():
                self.load_stats['total_load_time'] += wrapper.get_load_time()
        else:
            self.load_stats['failed_wrappers'] += 1
        
        return success
    
    def unload_wrapper(self, name: str) -> bool:
        """Выгрузка wrapper"""
        wrapper = self.get_wrapper(name)
        if wrapper is None:
            return False
        
        wrapper.unload()
        if wrapper.is_loaded():
            self.load_stats['loaded_wrappers'] -= 1
        else:
            self.load_stats['failed_wrappers'] -= 1
        
        return True
    
    def load_all_wrappers(self) -> Dict[str, bool]:
        """Загрузка всех wrappers"""
        results = {}
        for name in self.wrappers:
            results[name] = self.load_wrapper(name)
        return results
    
    def unload_all_wrappers(self) -> Dict[str, bool]:
        """Выгрузка всех wrappers"""
        results = {}
        for name in self.wrappers:
            results[name] = self.unload_wrapper(name)
        return results
    
    def get_wrapper_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о wrapper"""
        wrapper = self.get_wrapper(name)
        return wrapper.get_info() if wrapper else None
    
    def get_all_wrappers_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех wrappers"""
        return {name: wrapper.get_info() for name, wrapper in self.wrappers.items()}
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        current_loaded = sum(1 for w in self.wrappers.values() if w.is_loaded())
        return {
            **self.load_stats,
            'current_loaded': current_loaded,
            'current_failed': len(self.wrappers) - current_loaded,
            'average_load_time': (
                self.load_stats['total_load_time'] / max(self.load_stats['loaded_wrappers'], 1)
            )
        }
    
    def cleanup_failed_wrappers(self) -> int:
        """Очистка неудачных wrappers"""
        failed_names = []
        for name, wrapper in self.wrappers.items():
            if not wrapper.is_loaded() and wrapper.get_error():
                failed_names.append(name)
        
        for name in failed_names:
            del self.wrappers[name]
            self.load_stats['total_wrappers'] -= 1
            self.load_stats['failed_wrappers'] -= 1
        
        logger.info(f"Cleaned up {len(failed_names)} failed wrappers")
        return len(failed_names)

# Глобальный менеджер
_lazy_manager = LazyWrapperManager()

def create_lazy_wrapper(name: str, module_path: str, class_name: str, 
                       *args, **kwargs) -> LazyWrapper:
    """Создание lazy wrapper через глобальный менеджер"""
    return _lazy_manager.create_wrapper(name, module_path, class_name, *args, **kwargs)

def get_lazy_wrapper(name: str) -> Optional[LazyWrapper]:
    """Получение lazy wrapper через глобальный менеджер"""
    return _lazy_manager.get_wrapper(name)

def load_lazy_wrapper(name: str) -> bool:
    """Загрузка lazy wrapper через глобальный менеджер"""
    return _lazy_manager.load_wrapper(name)

def unload_lazy_wrapper(name: str) -> bool:
    """Выгрузка lazy wrapper через глобальный менеджер"""
    return _lazy_manager.unload_wrapper(name)

def get_lazy_manager() -> LazyWrapperManager:
    """Получение глобального менеджера"""
    return _lazy_manager

# Декоратор для ленивой загрузки функций
def lazy_load(module_path: str, class_name: str, *args, **kwargs):
    """Декоратор для ленивой загрузки функций"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            # Создание lazy wrapper
            lazy_wrapper = create_lazy_wrapper(
                f"{func.__name__}_lazy", 
                module_path, 
                class_name, 
                *args, 
                **kwargs
            )
            
            # Загрузка если нужно
            if not lazy_wrapper.is_loaded():
                lazy_wrapper.force_load()
            
            # Вызов оригинальной функции с lazy компонентом
            return func(lazy_wrapper, *func_args, **func_kwargs)
        
        return wrapper
    return decorator

# Функции для интеграции с SFM
def initialize_lazy_system() -> bool:
    """Инициализация системы lazy loading"""
    try:
        # Загрузка всех существующих wrappers
        lazy_dir = os.path.join(os.path.dirname(__file__), 'lazy_wrappers')
        if os.path.exists(lazy_dir):
            for file_name in os.listdir(lazy_dir):
                if file_name.endswith('_wrapper.py'):
                    wrapper_name = file_name.replace('_wrapper.py', '')
                    module_path = f"security.lazy_wrappers.{wrapper_name}_wrapper"
                    
                    # Попытка создать wrapper
                    try:
                        create_lazy_wrapper(wrapper_name, module_path, f"Lazy{wrapper_name.title()}Wrapper")
                    except Exception as e:
                        logger.warning(f"Failed to create wrapper for {wrapper_name}: {e}")
        
        logger.info("Lazy system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize lazy system: {e}")
        return False

def get_lazy_system_stats() -> Dict[str, Any]:
    """Получение статистики системы lazy loading"""
    return _lazy_manager.get_stats()

def cleanup_lazy_system() -> int:
    """Очистка системы lazy loading"""
    return _lazy_manager.cleanup_failed_wrappers()

# Основные функции для SFM
def get_lazy_functions() -> List[str]:
    """Получение списка функций lazy loading"""
    return [
        'create_lazy_wrapper',
        'get_lazy_wrapper', 
        'load_lazy_wrapper',
        'unload_lazy_wrapper',
        'get_lazy_manager',
        'lazy_load',
        'initialize_lazy_system',
        'get_lazy_system_stats',
        'cleanup_lazy_system',
        'get_lazy_functions'
    ]

if __name__ == "__main__":
    # Тестирование
    def test_lazy_system():
        print("🧪 Тестирование Lazy Wrappers System")
        
        # Создание тестового wrapper
        wrapper = create_lazy_wrapper(
            "test_wrapper",
            "security.safe_function_manager", 
            "SafeFunctionManager"
        )
        
        print(f"✅ Wrapper создан: {wrapper.get_info()}")
        
        # Загрузка
        success = load_lazy_wrapper("test_wrapper")
        print(f"✅ Загрузка: {'Успешно' if success else 'Ошибка'}")
        
        # Статистика
        stats = get_lazy_system_stats()
        print(f"📊 Статистика: {stats}")
        
        # Очистка
        cleanup_lazy_system()
        print("✅ Система очищена")
    
    test_lazy_system()
