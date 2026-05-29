# -*- coding: utf-8 -*-
"""Optional Hermes CLI bridge for h3-api-wire (AI_BACKEND=hermes, kb_only intents)."""
from __future__ import annotations

import os
import re
import subprocess
from typing import Optional, Tuple

from security.services.hermes_key_rotator import (
    env_with_active_key,
    load_api_keys,
    rotate_to_next_key,
    should_rotate_on_error,
)

HERMES_BIN = os.getenv("HERMES_BIN", "/opt/aladdin-backend/venv/bin/hermes")

# Max attempts = number of keys (at least 1)
_MAX_ROTATE_ATTEMPTS = max(1, min(8, int(os.getenv("HERMES_KEY_ROTATE_MAX_ATTEMPTS", "4"))))


def hermes_available() -> bool:
    return os.path.isfile(HERMES_BIN) and os.access(HERMES_BIN, os.X_OK)


_HERMES_STDERR_LINE_PREFIXES = (
    "no auxiliary llm",
    "context compression",
    "run `hermes setup`",
    "openrouter_api_key",
    "api call failed",
    "http 402",
    "http 403",
    "http 429",
    "http 401",
    "requires a subscription",
    "upgrade for access",
    "prompt tokens limit",
)


def _strip_hermes_cli_noise(raw: str) -> str:
    lines = []
    for line in (raw or "").splitlines():
        stripped = line.strip()
        low = stripped.lower()
        if line.startswith("session_id:"):
            continue
        if stripped.startswith("Resume this session"):
            continue
        if stripped.startswith("⚠") or stripped.startswith("Warning:"):
            continue
        if any(low.startswith(p) or p in low for p in _HERMES_STDERR_LINE_PREFIXES):
            continue
        lines.append(line)
    text = "\n".join(lines).strip()
    text = re.sub(r"╭[─╮].*?╰[─╯]", "", text, flags=re.DOTALL)
    return text.strip()


def _run_hermes_once(
    cmd: list,
    env: dict,
    timeout_sec: int,
) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env=env,
    )
    err_raw = proc.stderr or proc.stdout or ""
    err = _strip_hermes_cli_noise(err_raw)[:500]
    out = _strip_hermes_cli_noise(proc.stdout or "")
    return proc.returncode, out, err


def chat_once(
    message: str,
    *,
    skill: Optional[str] = None,
    timeout_sec: int = 150,
) -> Tuple[bool, str, Optional[str]]:
    """Returns (success, response_text, error). Rotates OpenRouter keys on 401/429/403."""
    if not hermes_available():
        return False, "", "hermes binary not found"
    keys = load_api_keys()
    if not keys:
        return False, "", "no OPENROUTER API keys configured"

    prompt = (message or "").replace("\x00", "")[:4000]
    cmd = [HERMES_BIN, "chat", "-q", prompt, "-Q"]
    if skill:
        cmd.extend(["-s", skill])

    attempts = min(_MAX_ROTATE_ATTEMPTS, max(1, len(keys)))
    last_err: Optional[str] = None

    for attempt in range(attempts):
        base_env = {
            **os.environ,
            "PATH": os.path.dirname(HERMES_BIN) + ":" + os.environ.get("PATH", ""),
        }
        env = env_with_active_key(base_env)
        try:
            code, out, err = _run_hermes_once(cmd, env, timeout_sec)
        except subprocess.TimeoutExpired:
            return False, "", "hermes timeout"
        except Exception as exc:
            return False, "", str(exc)

        if code == 0 and out:
            return True, out, None

        last_err = err or "hermes failed"
        combined = (err or "") + " " + (out or "")
        if attempt + 1 < attempts and should_rotate_on_error(combined):
            rotated, _ = rotate_to_next_key(reason=combined[:200])
            if rotated:
                continue
        break

    return False, "", last_err
