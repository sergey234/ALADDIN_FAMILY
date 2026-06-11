"""Shared smoke secret loader for GATE-D prod scripts."""
from __future__ import annotations

import os
from pathlib import Path


def smoke_secret(key: str, env_path: str | None = None) -> str:
    if os.environ.get(key):
        return os.environ[key]
    path = Path(env_path or os.environ.get("ALADDIN_ENV", "/opt/aladdin-backend/.env"))
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""
