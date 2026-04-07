"""
Bridge router for subscription endpoints.

Основная логика реализована в `backend/app/routers/subscription.py`.
Этот модуль просто реэкспортирует `router`, чтобы `main.py` мог
импортировать `app.routers.subscription` без изменений.
"""

try:
    # Предпочитаемый путь для текущей структуры проекта
    from backend.app.routers.subscription import router  # type: ignore[import]
except ImportError as e:  # pragma: no cover - защитный fallback
    raise ImportError(f"Cannot import backend subscription router: {e}")

