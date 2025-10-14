#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Interface Manager Extra - Дополнительные функции UI менеджера
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any
import time
import threading
import logging

class UserInterfaceManagerExtra:
    """Дополнительные функции для управления пользовательским интерфейсом"""
    
    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.UserInterfaceManagerExtra")
        self.user_sessions = {}
        self.adaptive_factors = {}
        self.lock = threading.Lock()
        self.config = {
            "max_adaptive_factor": 2.0,
            "min_adaptive_factor": 0.5
        }
        self.stats = {"adaptive_adjustments": 0}
        self.db_session = None
    
    def _save_user_session(self, record) -> bool:
        """Сохранение записи пользовательской сессии"""
        try:
            if self.db_session:
                # Обновление или создание записи
                existing = self.db_session.query(UserSessionRecord).filter(
                    UserSessionRecord.id == record.id
                ).first()
                
                if existing:
                    existing.last_activity = record.last_activity
                    existing.is_active = record.is_active
                else:
                    self.db_session.add(record)
                
                self.db_session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения записи сессии: {e}")
            return False
    
    def _cleanup_worker(self) -> None:
        """Очистка неактивных сессий"""
        try:
            with self.lock:
                for session_id, session in self.user_sessions.items():
                    # Анализ поведения пользователя
                    session_duration = (datetime.utcnow() - session["start_time"]).total_seconds()
                    
                    # Адаптация фактора на основе длительности сессии
                    if session_duration > 1800:  # Более 30 минут
                        self.adaptive_factors[session_id] = min(
                            self.config["max_adaptive_factor"],
                            self.adaptive_factors[session_id] * 1.1
                        )
                    elif session_duration < 300:  # Менее 5 минут
                        self.adaptive_factors[session_id] = max(
                            self.config["min_adaptive_factor"],
                            self.adaptive_factors[session_id] * 0.9
                        )
                    
                    self.stats["adaptive_adjustments"] += 1
        except Exception as e:
            self.logger.error(f"Ошибка обновления адаптивных факторов: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера"""
        try:
            return {
                "active_sessions": len(self.user_sessions),
                "adaptive_factors": len(self.adaptive_factors),
                "stats": self.stats,
                "status": "active"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            with self.lock:
                self.user_sessions.clear()
                self.adaptive_factors.clear()
                self.stats = {"adaptive_adjustments": 0}
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")

# Глобальный экземпляр
ui_manager = UserInterfaceManagerExtra()

# Enhanced version with improvements
