#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singleton для Safe Function Manager
Обеспечивает единственный экземпляр SFM в системе

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-09
"""

import threading
from typing import Optional
from security.safe_function_manager import SafeFunctionManager

class SFMSingleton:
    """Singleton для Safe Function Manager"""
    
    _instance: Optional['SFMSingleton'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._sfm = None
                    cls._instance._initialized = False
        return cls._instance
    
    def get_sfm(self) -> SafeFunctionManager:
        """Получить единственный экземпляр SFM"""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._sfm = SafeFunctionManager("MainSFM")
                    self._initialized = True
        return self._sfm
    
    def reset(self):
        """Сбросить singleton (для тестов)"""
        with self._lock:
            self._instance = None
            self._sfm = None
            self._initialized = False

# Глобальный экземпляр singleton
sfm_singleton = SFMSingleton()

def get_sfm() -> SafeFunctionManager:
    """Получить единственный экземпляр SFM"""
    return sfm_singleton.get_sfm()

def reset_sfm():
    """Сбросить SFM singleton (для тестов)"""
    sfm_singleton.reset()