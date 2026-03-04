#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Interface Manager Extra - Дополнительные функции UI менеджера
"""

from datetime import datetime
from typing import Dict, Any
import threading
import logging
from security.types.security_types import UserSessionRecord


class UserInterfaceManagerExtra:
    """Дополнительные функции для управления пользовательским интерфейсом"""

    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.UserInterfaceManagerExtra")
        self.user_sessions = {}
        self.adaptive_factors = {}
        self.lock = threading.Lock()
        self.config = {"max_adaptive_factor": 2.0, "min_adaptive_factor": 0.5}
        self.stats = {"adaptive_adjustments": 0}
        self.db_session = None

    def _save_user_session(self, record) -> bool:
        """Сохранение записи пользовательской сессии"""
        try:
            if self.db_session:
                # Обновление или создание записи
                existing = self.db_session.query(UserSessionRecord).filter(UserSessionRecord.id == record.id).first()

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
                            self.config["max_adaptive_factor"], self.adaptive_factors[session_id] * 1.1
                        )
                    elif session_duration < 300:  # Менее 5 минут
                        self.adaptive_factors[session_id] = max(
                            self.config["min_adaptive_factor"], self.adaptive_factors[session_id] * 0.9
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
                "status": "active",
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

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния UI менеджера

        Returns:
            Dict[str, Any]: Статус здоровья UI менеджера
        """
        try:
            import asyncio

            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "UserInterfaceManagerExtra",
                "components": {
                    "logger_initialized": self.logger is not None,
                    "user_sessions_tracking": len(self.user_sessions) >= 0,
                    "adaptive_factors_tracking": len(self.adaptive_factors) >= 0,
                    "lock_available": self.lock is not None,
                    "config_loaded": self.config is not None,
                    "db_session_available": self.db_session is not None
                },
                "metrics": {
                    "total_user_sessions": len(self.user_sessions),
                    "total_adaptive_factors": len(self.adaptive_factors),
                    "adaptive_adjustments": self.stats.get("adaptive_adjustments", 0),
                    "max_adaptive_factor": self.config.get("max_adaptive_factor", 2.0),
                    "min_adaptive_factor": self.config.get("min_adaptive_factor", 0.5)
                }
            }

            # Проверка состояния сессий
            if len(self.user_sessions) > 1000:  # Большое количество сессий
                health_status["status"] = "degraded"
                health_status["components"]["high_session_count"] = True

            # Проверка адаптивных факторов
            if len(self.adaptive_factors) > 500:  # Большое количество факторов
                health_status["status"] = "degraded"
                health_status["components"]["high_adaptive_factors"] = True

            # Проверка базы данных
            if not self.db_session:
                health_status["status"] = "degraded"
                health_status["components"]["db_session_available"] = False

            return health_status

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "UserInterfaceManagerExtra",
                "error": str(e)
            }


# Глобальный экземпляр
ui_manager = UserInterfaceManagerExtra()
