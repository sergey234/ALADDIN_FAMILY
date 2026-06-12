"""Persist antifake media uploads for async worker processing (af-3)."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

_DEFAULT_DIR = Path(os.environ.get("ANTIFAKE_UPLOAD_DIR", "/tmp/aladdin-antifake/uploads"))


def upload_root() -> Path:
    root = _DEFAULT_DIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_name(name: str) -> str:
    base = Path(name or "upload").name
    return re.sub(r"[^\w.\-]", "_", base)[:120] or "upload"


def save_upload(*, user_id: int, job_id: str, file_bytes: bytes, file_name: str) -> Path:
    user_dir = upload_root() / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"{job_id}_{_safe_name(file_name)}"
    path.write_bytes(file_bytes)
    return path


def read_upload(path: str | Path) -> bytes:
    return Path(path).read_bytes()


def delete_upload(path: str | Path) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


def cleanup_user_uploads(user_id: int, *, keep_job_id: Optional[str] = None) -> None:
    user_dir = upload_root() / str(user_id)
    if not user_dir.is_dir():
        return
    for item in user_dir.iterdir():
        if keep_job_id and keep_job_id in item.name:
            continue
        delete_upload(item)
