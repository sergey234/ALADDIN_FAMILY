#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singleton pattern implementation for ALADDIN system
"""

import threading
from typing import Any, Dict


class Singleton:
    """
    Thread-safe Singleton pattern implementation
    """

    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__new__(cls)
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        # Инициализация только один раз
        if not hasattr(self, "_initialized"):
            super().__init__(*args, **kwargs)
            self._initialized = True


class ThreadSafeSingleton:
    """
    Enhanced thread-safe Singleton with additional safety features
    """

    _instances: Dict[type, Any] = {}
    _locks: Dict[type, threading.Lock] = {}
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._locks:
                    cls._locks[cls] = threading.Lock()
                with cls._locks[cls]:
                    if cls not in cls._instances:
                        cls._instances[cls] = super(
                            ThreadSafeSingleton, cls
                        ).__new__(cls)
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "_initialized"):
            with self._locks[self.__class__]:
                if not hasattr(self, "_initialized"):
                    super().__init__(*args, **kwargs)
                    self._initialized = True


def get_singleton(cls):
    """
    Decorator for creating singleton classes

    Usage:
        @get_singleton
        class MyClass:
            pass
    """
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class SingletonMeta(type):
    """
    Metaclass for creating singleton classes
    """

    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(SingletonMeta, cls).__call__(
                        *args, **kwargs
                    )
        return cls._instances[cls]


# Пример использования
if __name__ == "__main__":
    # Тест базового Singleton
    class TestSingleton(Singleton):
        def __init__(self):
            self.value = "test"

    s1 = TestSingleton()
    s2 = TestSingleton()
    print(f"Same instance: {s1 is s2}")

    # Тест ThreadSafeSingleton
    class TestThreadSafeSingleton(ThreadSafeSingleton):
        def __init__(self):
            self.value = "thread_safe_test"

    ts1 = TestThreadSafeSingleton()
    ts2 = TestThreadSafeSingleton()
    print(f"Same thread-safe instance: {ts1 is ts2}")

    print("Singleton pattern implementation working correctly!")
