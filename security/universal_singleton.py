# -*- coding: utf-8 -*-
"""
Universal Singleton Pattern для ALADDIN Security System
Универсальный паттерн Singleton для всех Manager, Agent и Bot классов

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-09-10
"""

import logging
import threading
import weakref
from datetime import datetime
from typing import Any, Dict, Type, TypeVar

# Тип для Generic Singleton
T = TypeVar("T")


class UniversalSingleton:
    """
    Универсальный Singleton для всех компонентов ALADDIN

    Особенности:
    - Thread-safe (потокобезопасный)
    - Memory-safe (безопасный по памяти)
    - Lazy initialization (ленивая инициализация)
    - Weak references (слабые ссылки)
    - Auto cleanup (автоочистка)
    """

    _instances: Dict[Type, Any] = {}
    _lock = threading.RLock()
    _weak_refs: Dict[Type, weakref.ref] = {}

    def __new__(cls, *args, **kwargs):
        """
        Создание или получение существующего экземпляра
        """
        if cls not in cls._instances:
            with cls._lock:
                # Двойная проверка блокировки
                if cls not in cls._instances:
                    # Создаем новый экземпляр
                    instance = super(UniversalSingleton, cls).__new__(cls)
                    cls._instances[cls] = instance

                    # Создаем слабую ссылку для автоочистки
                    cls._weak_refs[cls] = weakref.ref(instance, cls._cleanup)

                    # Инициализируем экземпляр
                    instance._singleton_initialized = False
                    instance._singleton_created_at = datetime.now()
                    instance._singleton_access_count = 0

                    logging.info(f"✅ Singleton создан: {cls.__name__}")

        # Увеличиваем счетчик обращений
        instance = cls._instances[cls]
        instance._singleton_access_count += 1
        instance._singleton_last_access = datetime.now()

        return instance

    @classmethod
    def _cleanup(cls, weak_ref):
        """
        Автоочистка при удалении экземпляра
        """
        for class_type, ref in list(cls._weak_refs.items()):
            if ref is weak_ref:
                if class_type in cls._instances:
                    del cls._instances[class_type]
                del cls._weak_refs[class_type]
                logging.info(f"🧹 Singleton очищен: {class_type.__name__}")
                break

    @classmethod
    def get_instance(cls) -> "UniversalSingleton":
        """
        Получить существующий экземпляр
        """
        return cls()

    @classmethod
    def reset_instance(cls):
        """
        Сбросить экземпляр (для тестирования)
        """
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]
            if cls in cls._weak_refs:
                del cls._weak_refs[cls]
            logging.info(f"🔄 Singleton сброшен: {cls.__name__}")

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Получить статистику Singleton
        """
        if cls not in cls._instances:
            return {"exists": False}

        instance = cls._instances[cls]
        return {
            "exists": True,
            "created_at": instance._singleton_created_at,
            "access_count": instance._singleton_access_count,
            "last_access": getattr(instance, "_singleton_last_access", None),
            "initialized": getattr(instance, "_singleton_initialized", False),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация (вызывается только один раз)
        """
        if not hasattr(self, "_singleton_initialized"):
            self._singleton_initialized = True
            # Вызываем родительский __init__ если есть
            super().__init__(*args, **kwargs)
            logging.info(
                f"🚀 Singleton инициализирован: {self.__class__.__name__}"
            )


def get_component(component_class: Type[T], *args, **kwargs) -> T:
    """
    Универсальная функция получения компонента

    Args:
        component_class: Класс компонента
        *args: Аргументы для инициализации
        **kwargs: Ключевые аргументы для инициализации

    Returns:
        Экземпляр компонента (Singleton)
    """
    if not issubclass(component_class, UniversalSingleton):
        raise TypeError(
            f"Класс {component_class.__name__} должен наследоваться от "
            f"UniversalSingleton"
        )

    return component_class(*args, **kwargs)


def reset_all_singletons():
    """
    Сбросить все Singleton экземпляры (для тестирования)
    """
    with UniversalSingleton._lock:
        UniversalSingleton._instances.clear()
        UniversalSingleton._weak_refs.clear()
        logging.info("🧹 Все Singleton экземпляры сброшены")


def get_all_singleton_stats() -> Dict[str, Dict[str, Any]]:
    """
    Получить статистику всех Singleton экземпляров
    """
    stats = {}
    for class_type, instance in UniversalSingleton._instances.items():
        stats[class_type.__name__] = {
            "created_at": instance._singleton_created_at,
            "access_count": instance._singleton_access_count,
            "last_access": getattr(instance, "_singleton_last_access", None),
            "initialized": getattr(instance, "_singleton_initialized", False),
        }
    return stats


# Декоратор для автоматического применения Singleton
def singleton(cls):
    """
    Декоратор для автоматического применения Singleton
    """

    class SingletonWrapper(cls, UniversalSingleton):
        pass

    SingletonWrapper.__name__ = cls.__name__
    SingletonWrapper.__module__ = cls.__module__
    SingletonWrapper.__doc__ = cls.__doc__

    return SingletonWrapper


# Пример использования:
if __name__ == "__main__":
    # Тестирование Singleton
    class TestManager(UniversalSingleton):
        def __init__(self):
            super().__init__()
            self.data = []

        def add_data(self, item):
            self.data.append(item)

    # Создаем несколько экземпляров
    manager1 = TestManager()
    manager2 = TestManager()
    manager3 = get_component(TestManager)

    # Проверяем, что это один и тот же объект
    print(f"manager1 is manager2: {manager1 is manager2}")
    print(f"manager2 is manager3: {manager2 is manager3}")

    # Добавляем данные в один
    manager1.add_data("test1")

    # Проверяем, что данные видны во всех
    print(f"manager1.data: {manager1.data}")
    print(f"manager2.data: {manager2.data}")
    print(f"manager3.data: {manager3.data}")

    # Статистика
    stats = TestManager.get_stats()
    print(f"Stats: {stats}")
