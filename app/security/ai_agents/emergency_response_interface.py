"""Emergency Response Interface
==============================

Synchronous façade that wraps :mod:`emergency_response_system` and exposes
safe, typed helpers for the rest of the platform.  The interface hides the
async nature of the underlying implementation and centralises common flows
(triggering alerts, fetching statistics, resolving incidents).
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from .emergency_response_system import (
    AlertPriority,
    EmergencyAlert,
    EmergencyResponseSystem,
    EmergencyType,
)


class EmergencyResponseInterface:
    """Synchronous helper that bridges the Safe Function Manager and ERS."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._system = EmergencyResponseSystem(config)

    def trigger_alert(
        self,
        *,
        elderly_id: str,
        emergency_type: EmergencyType,
        title: str,
        message: str,
        priority: AlertPriority = AlertPriority.HIGH,
        phone_number: Optional[str] = None,
        transaction_id: Optional[str] = None,
        risk_score: float = 0.0,
        location: Optional[str] = None,
    ) -> bool:
        """Trigger an emergency mode for a family member."""

        alert = EmergencyAlert(
            alert_id=str(uuid.uuid4()),
            elderly_id=elderly_id,
            emergency_type=emergency_type,
            priority=priority,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            location=location,
            phone_number=phone_number,
            transaction_id=transaction_id,
            risk_score=risk_score,
        )
        return self._run_async(self._system.trigger_emergency_mode(elderly_id, alert))

    def notify_family(
        self,
        *,
        elderly_id: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
    ) -> bool:
        """Send a non-blocking informational message to the family."""

        return self._run_async(self._system.notify_family(elderly_id, message, priority))

    def deactivate_alert(self, elderly_id: str) -> bool:
        """Deactivate the emergency mode for a family member."""

        return self._run_async(self._system.deactivate_emergency_mode(elderly_id))

    def get_emergency_status(self, elderly_id: str) -> Dict[str, Any]:
        """Return the current emergency state for a family member."""

        return self._run_async(self._system.get_emergency_status(elderly_id))

    def get_statistics(self) -> Dict[str, Any]:
        """Return cumulative system statistics."""

        return self._run_async(self._system.get_statistics())

    def get_system_status(self) -> Dict[str, Any]:
        """Return health information about the emergency subsystem."""

        return self._run_async(self._system.get_status())

    @staticmethod
    def _run_async(coro: "asyncio.coroutines.Coroutine[Any, Any, Any]"):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()

        return asyncio.run(coro)


__all__ = [
    "EmergencyResponseInterface",
    "EmergencyType",
    "AlertPriority",
]

