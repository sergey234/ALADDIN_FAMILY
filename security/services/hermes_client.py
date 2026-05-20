# -*- coding: utf-8 -*-
"""Optional Hermes CLI bridge for h3-api-wire (AI_BACKEND=hermes, kb_only intents)."""
from __future__ import annotations

import os
import re
import subprocess
from typing import Optional, Tuple

HERMES_BIN = os.getenv("HERMES_BIN", "/opt/aladdin-backend/venv/bin/hermes")


def hermes_available() -> bool:
    return os.path.isfile(HERMES_BIN) and os.access(HERMES_BIN, os.X_OK)


def _strip_hermes_cli_noise(raw: str) -> str:
    lines = []
    for line in (raw or "").splitlines():
        if line.startswith("session_id:"):
            continue
        if line.strip().startswith("Resume this session"):
            continue
        lines.append(line)
    text = "\n".join(lines).strip()
    # Drop box-drawing banners if quiet mode was not used
    text = re.sub(r"╭[─╮].*?╰[─╯]", "", text, flags=re.DOTALL)
    return text.strip()


def chat_once(
    message: str,
    *,
    skill: Optional[str] = None,
    timeout_sec: int = 150,
) -> Tuple[bool, str, Optional[str]]:
    """Returns (success, response_text, error)."""
    if not hermes_available():
        return False, "", "hermes binary not found"
    prompt = (message or "").replace("\x00", "")[:4000]
    cmd = [HERMES_BIN, "chat", "-q", prompt, "-Q"]
    if skill:
        cmd.extend(["-s", skill])
    env = {
        **os.environ,
        "PATH": os.path.dirname(HERMES_BIN) + ":" + os.environ.get("PATH", ""),
    }
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "", "hermes timeout"
    except Exception as exc:
        return False, "", str(exc)

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "hermes failed")[:500]
        return False, "", err
    out = _strip_hermes_cli_noise(proc.stdout or "")
    if not out:
        out = _strip_hermes_cli_noise(proc.stderr or "")
    if not out:
        return False, "", "empty hermes response"
    return True, out, None
