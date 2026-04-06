from functools import lru_cache
from typing import Dict

_DEFAULT_MAP: Dict[str, int] = {
    "trial": 3,
    "free": 1,
    "personal": 2,
    "family": 6,
    "premium": 10,
}

def _normalize(level: str) -> str:
    return (level or "").strip().lower()

@lru_cache(maxsize=1)
def get_limits_map() -> Dict[str, int]:
    return dict(_DEFAULT_MAP)

def getMaxFamilyMembersFor(level: str) -> int:
    m = get_limits_map()
    return m.get(_normalize(level), m["free"])