#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Extra - Дополнительные функции Circuit Breaker
"""

import logging
import threading
from datetime import datetime
from typing import Any, Dict


class CircuitBreakerRecord:
    """Запись состояния Circuit Breaker для базы данных"""

    def __init__(
        self,
        circuit_id: str,
        failure_threshold: int,
        timeout: int,
        current_state: str,
        failure_count: int,
        success_count: int,
        last_failure_time: datetime = None,
        last_success_time: datetime = None,
        metadata: Dict[str, Any] = None,
    ):
        self.id = circuit_id
        self.circuit_id = circuit_id
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.current_state = current_state
        self.failure_count = failure_count
        self.success_count = success_count
        self.last_failure_time = last_failure_time
        self.last_success_time = last_success_time
        self.metadata = metadata or {}


class CircuitBreakerExtra:
    """Дополнительные функции для Circuit Breaker"""

    def __init__(self):
        self.logger = logging.getLogger("ALADDIN.CircuitBreakerExtra")
        self.circuits = {}
        self.lock = threading.Lock()
        self.config = {
            "default_failure_threshold": 5,
            "default_timeout": 60,
            "default_retry_timeout": 30,
        }
        self.stats = {"circuit_operations": 0}
        self.db_session = None

    def _save_circuit_state(
        self, circuit_id: str, circuit: Dict[str, Any]
    ) -> bool:
        """Сохранение состояния Circuit Breaker"""
        try:
            # Валидация входных данных
            if not isinstance(circuit_id, str) or not circuit_id.strip():
                raise ValueError("circuit_id должен быть непустой строкой")
            if not isinstance(circuit, dict):
                raise ValueError("circuit должен быть словарем")
            if not circuit.get("failure_threshold") or not isinstance(
                circuit["failure_threshold"], int
            ):
                raise ValueError("failure_threshold должен быть целым числом")
            if not circuit.get("timeout") or not isinstance(
                circuit["timeout"], int
            ):
                raise ValueError("timeout должен быть целым числом")
            record = CircuitBreakerRecord(
                circuit_id=circuit_id,
                failure_threshold=circuit["failure_threshold"],
                timeout=circuit["timeout"],
                current_state=circuit["state"],
                failure_count=circuit["failure_count"],
                success_count=circuit["success_count"],
                last_failure_time=circuit["last_failure_time"],
                last_success_time=circuit["last_success_time"],
                metadata=circuit,
            )

            if self.db_session:
                # Обновление или создание записи
                existing = (
                    self.db_session.query(CircuitBreakerRecord)
                    .filter(CircuitBreakerRecord.id == record.id)
                    .first()
                )

                if existing:
                    existing.current_state = record.current_state
                    existing.failure_count = record.failure_count
                    existing.success_count = record.success_count
                    existing.last_failure_time = record.last_failure_time
                    existing.last_success_time = record.last_success_time
                else:
                    self.db_session.add(record)

                self.db_session.commit()
                return True
        except Exception as e:
            self.logger.error(
                f"Ошибка сохранения состояния Circuit Breaker: {e}"
            )
            return False

    def create_circuit(
        self, circuit_id: str, config: Dict[str, Any] = None
    ) -> bool:
        """Создание нового Circuit Breaker"""
        try:
            with self.lock:
                if circuit_id in self.circuits:
                    return False

                circuit_config = self.config.copy()
                if config:
                    circuit_config.update(config)

                self.circuits[circuit_id] = {
                    "state": "CLOSED",
                    "failure_count": 0,
                    "success_count": 0,
                    "last_failure_time": None,
                    "last_success_time": None,
                    "failure_threshold": circuit_config[
                        "default_failure_threshold"
                    ],
                    "timeout": circuit_config["default_timeout"],
                    "retry_timeout": circuit_config["default_retry_timeout"],
                }

                self.stats["circuit_operations"] += 1
                return True
        except Exception as e:
            self.logger.error(f"Ошибка создания Circuit Breaker: {e}")
            return False

    def call(self, circuit_id: str, func, *args, **kwargs):
        """Выполнение функции через Circuit Breaker"""
        try:
            with self.lock:
                if circuit_id not in self.circuits:
                    self.create_circuit(circuit_id)

                circuit = self.circuits[circuit_id]

                # Проверка состояния
                if circuit["state"] == "OPEN":
                    if self._should_attempt_reset(circuit):
                        circuit["state"] = "HALF_OPEN"
                    else:
                        raise Exception("Circuit Breaker is OPEN")

                # Выполнение функции
                result = func(*args, **kwargs)

                # Успешное выполнение
                self._on_success(circuit_id, circuit)
                return result

        except Exception as e:
            # Ошибка выполнения
            self._on_failure(circuit_id, circuit)
            raise e

    def _should_attempt_reset(self, circuit: Dict[str, Any]) -> bool:
        """Проверка возможности сброса Circuit Breaker"""
        if circuit["last_failure_time"] is None:
            return True

        time_since_failure = (
            datetime.utcnow() - circuit["last_failure_time"]
        ).total_seconds()
        return time_since_failure >= circuit["retry_timeout"]

    def _on_success(self, circuit_id: str, circuit: Dict[str, Any]):
        """Обработка успешного выполнения"""
        circuit["success_count"] += 1
        circuit["last_success_time"] = datetime.utcnow()

        if circuit["state"] == "HALF_OPEN":
            circuit["state"] = "CLOSED"
            circuit["failure_count"] = 0

        self._save_circuit_state(circuit_id, circuit)

    def _on_failure(self, circuit_id: str, circuit: Dict[str, Any]):
        """Обработка ошибки выполнения"""
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = datetime.utcnow()

        if circuit["failure_count"] >= circuit["failure_threshold"]:
            circuit["state"] = "OPEN"

        self._save_circuit_state(circuit_id, circuit)

    async def get_status(self) -> Dict[str, Any]:
        """Получение статуса Circuit Breaker"""
        try:
            return {
                "active_circuits": len(self.circuits),
                "circuit_states": {
                    cid: c["state"] for cid, c in self.circuits.items()
                },
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
                self.circuits.clear()
                self.stats = {"circuit_operations": 0}
        except Exception as e:
            self.logger.error(f"Ошибка очистки: {e}")


# Глобальный экземпляр
circuit_breaker_extra = CircuitBreakerExtra()
