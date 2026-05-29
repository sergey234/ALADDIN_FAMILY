# -*- coding: utf-8 -*-
"""
Hermes / OpenRouter API key rotation (429 rate limit, 401 invalid, 403 subscription).

Env:
  HERMES_OPENROUTER_API_KEYS — comma-separated keys (preferred on VPS)
  HERMES_OPENROUTER_KEYS_FILE — one key per line (fallback)
  HERMES_KEY_ROTATOR_STATE — path to persist active index (default under data/)

Cron watchdog: scripts/hermes_llm_watchdog.sh (see scripts/hermes_llm_watchdog.cron.example)
"""
from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import List, Optional, Tuple

_LOCK = threading.Lock()

_HTTP_ROTATE_RE = re.compile(
    r"\b(?:http\s*)?(?:401|429|403)\b|"
    r"rate\s*limit|invalid\s*api\s*key|"
    r"requires\s+a\s+subscription|"
    r"upgrade\s+for\s+access|"
    r"openrouter_api_key",
    re.IGNORECASE,
)


def _default_state_path() -> Path:
    root = os.getenv("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")
    return Path(os.getenv("HERMES_KEY_ROTATOR_STATE", f"{root}/data/hermes_openrouter_key_index"))


def load_api_keys() -> List[str]:
    raw = (os.getenv("HERMES_OPENROUTER_API_KEYS") or "").strip()
    if raw:
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if keys:
            return keys
    path = (os.getenv("HERMES_OPENROUTER_KEYS_FILE") or "").strip()
    if path and os.path.isfile(path):
        keys = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    keys.append(line)
        return keys
    single = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    return [single] if single else []


def _read_index(state_path: Path, key_count: int) -> int:
    if key_count <= 0:
        return 0
    try:
        if state_path.is_file():
            idx = int(state_path.read_text(encoding="utf-8").strip())
            return idx % key_count
    except (OSError, ValueError):
        pass
    return 0


def _write_index(state_path: Path, index: int) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(str(index), encoding="utf-8")
    tmp.replace(state_path)


def current_key_index() -> Tuple[int, int]:
    """Returns (active_index, total_keys)."""
    keys = load_api_keys()
    state_path = _default_state_path()
    with _LOCK:
        return _read_index(state_path, len(keys)), len(keys)


def active_api_key() -> Optional[str]:
    keys = load_api_keys()
    if not keys:
        return None
    state_path = _default_state_path()
    with _LOCK:
        idx = _read_index(state_path, len(keys))
        return keys[idx]


def should_rotate_on_error(error_text: Optional[str]) -> bool:
    if not error_text:
        return False
    return bool(_HTTP_ROTATE_RE.search(error_text))


def rotate_to_next_key(reason: str = "") -> Tuple[bool, Optional[str]]:
    """
    Advance to next key. Returns (rotated, new_key_or_none).
    If only one key, returns (False, that_key).
    """
    keys = load_api_keys()
    if not keys:
        return False, None
    state_path = _default_state_path()
    with _LOCK:
        idx = _read_index(state_path, len(keys))
        if len(keys) == 1:
            return False, keys[0]
        new_idx = (idx + 1) % len(keys)
        _write_index(state_path, new_idx)
        # Optional audit line for watchdog logs
        if reason:
            log_path = state_path.parent / "hermes_key_rotator.log"
            try:
                with open(log_path, "a", encoding="utf-8") as fh:
                    fh.write(f"rotate {idx}->{new_idx} reason={reason[:200]}\n")
            except OSError:
                pass
        return True, keys[new_idx]


def env_with_active_key(base_env: Optional[dict] = None) -> dict:
    """Merge OPENROUTER_API_KEY (and alias) for Hermes CLI subprocess."""
    env = dict(base_env or os.environ)
    key = active_api_key()
    if key:
        env["OPENROUTER_API_KEY"] = key
        env["OPENROUTER_KEY"] = key
    return env
