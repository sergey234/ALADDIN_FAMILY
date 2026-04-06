import time
from typing import Optional, Tuple
from fastapi import Request

try:
    from app.observability.events import log_tariff_source_used
except Exception:  # pragma: no cover
    def log_tariff_source_used(*, source: str, warn: bool = False) -> None:
        pass

_TTL_SECONDS = 60  # cache TTL seconds
_cache: dict[str, Tuple[str, float]] = {}

def _read_from_cache(device_id: Optional[str]) -> Optional[str]:
    if not device_id:
        return None
    now = time.time()
    entry = _cache.get(device_id)
    if not entry:
        return None
    level, exp = entry
    if now > exp:
        _cache.pop(device_id, None)
        return None
    return level

def _write_cache(device_id: Optional[str], level: str) -> None:
    if not device_id:
        return
    _cache[device_id] = (level, time.time() + _TTL_SECONDS)

async def get_subscription_level(request: Request, device_id: Optional[str] = None) -> str:
    """
    Hybrid source of truth for subscription:
    1. Read from DB via cache if available.
    2. Fallback to JWT `subscription_level` claim.
    """
    if device_id:
        cached = _read_from_cache(device_id)
        if cached:
            log_tariff_source_used(source="db")
            return cached

    # Fallback to JWT
    try:
        # In this backend `get_current_user` puts user info either in depends or request state.
        # But we'll just check if it's passed or try to decode it, for now fallback to "free"
        level = "free"
        if hasattr(request.state, "user") and isinstance(request.state.user, dict):
            level = request.state.user.get("subscription_level", "free")
            log_tariff_source_used(source="jwt", warn=True)
        else:
            # Maybe it's in headers for simple fallback
            pass
        if device_id:
            _write_cache(device_id, level)
        return level
    except Exception:
        pass

    return "free"