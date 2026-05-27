# -*- coding: utf-8 -*-
"""
Контракт модуля платформы.

Каждая фича (голос, поиск, память…) — отдельный класс:
  - id: строка для capabilities API
  - enabled(): читает feature_flags
  - capability_fragment(): что отдать iOS (кнопки, лимиты)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModuleContext:
    """Контекст запроса для модуля."""

    user_id: str
    app_id: str
    age_band: str
    age_verified: bool
    content_policy: str
    subscription_level: str = "free"
    character_id: Optional[str] = None


@dataclass
class CapabilityFragment:
    """Фрагмент ответа GET /capabilities для одной фичи."""

    id: str
    enabled: bool
    ui: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)


class PlatformModule(ABC):
    """Базовый класс модуля. Наследники лежат в modules/*.py"""

    module_id: str = "base"

    @abstractmethod
    def enabled(self, ctx: ModuleContext) -> bool:
        """Серверная проверка: модуль активен для этого пользователя."""

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        """Что показать iOS (кнопки, доступность)."""
        on = self.enabled(ctx)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={"visible": on},
            limits={},
        )

    async def before_chat(self, ctx: ModuleContext, message: str) -> Optional[str]:
        """Хук до чата. Вернуть str = заблокировать с причиной."""
        return None

    async def after_chat(self, ctx: ModuleContext, result: Dict[str, Any]) -> Dict[str, Any]:
        """Хук после чата — можно обогатить ответ."""
        return result
