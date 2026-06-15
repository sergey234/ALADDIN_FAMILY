"""Persist antifake media uploads for async worker processing (af-3)."""
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Optional

_DEFAULT_DIR = Path(os.environ.get("ANTIFAKE_UPLOAD_DIR", "/var/lib/aladdin/antifake/uploads"))
UPLOAD_TTL_SEC = int(os.environ.get("ANTIFAKE_UPLOAD_TTL_SEC", str(15 * 60)))


def upload_root() -> Path:
    root = _DEFAULT_DIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_name(name: str) -> str:
    base = Path(name or "upload").name
    return re.sub(r"[^\w.\-]", "_", base)[:120] or "upload"


def save_upload(*, user_id: int, job_id: str, file_bytes: bytes, file_name: str) -> Path:
    cleanup_stale_uploads()
    user_dir = upload_root() / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"{job_id}_{_safe_name(file_name)}"
    path.write_bytes(file_bytes)
    return path


def read_upload(path: str | Path) -> bytes:
    from app.services.antifake_security import assert_upload_path_under_root

    upload_path = assert_upload_path_under_root(path, upload_root())
    if not upload_path.is_file():
        return b""
    age = time.time() - upload_path.stat().st_mtime
    if age > UPLOAD_TTL_SEC:
        delete_upload(upload_path)
        return b""
    return upload_path.read_bytes()


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


def cleanup_stale_uploads(*, ttl_sec: Optional[int] = None) -> int:
    """B-08: remove uploads older than TTL (default 15 min). Returns deleted count."""
    ttl = ttl_sec if ttl_sec is not None else UPLOAD_TTL_SEC
    cutoff = time.time() - ttl
    deleted = 0
    root = upload_root()
    for user_dir in root.iterdir():
        if not user_dir.is_dir():
            continue
        for item in user_dir.iterdir():
            try:
                if item.stat().st_mtime < cutoff:
                    delete_upload(item)
                    deleted += 1
            except OSError:
                continue
    return deleted
