"""
Family invite Open Graph images (JOB13 / H20) — Life360-style link previews.

GET  /api/family/invite/og.jpg?code=FAM-...  → personal JPEG or default silhouette
POST /api/family/invite/og.jpg               → upload composed 1200×630 (auth)

Static default also lives on the site as:
  https://aladdin-ai.ru/og/family-invite-default-1200x630.jpg

Deploy (owner GO): copy landing/og/* to web root /og/ and restart nginx if needed.
Personal files: {OG_DIR}/{COMPACT_CODE}.jpg
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from app.auth.auth import get_current_user

router = APIRouter(prefix="/api/family/invite", tags=["family-invite-og"])

_OG_DIR = Path(os.environ.get("ALADDIN_INVITE_OG_DIR", "/var/www/aladdin-ai.ru/og/family-invite"))
_DEFAULT = Path(
    os.environ.get(
        "ALADDIN_INVITE_OG_DEFAULT",
        "/var/www/aladdin-ai.ru/og/family-invite-default-1200x630.jpg",
    )
)
_MAX_BYTES = 2_500_000


def _compact_code(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (raw or "").upper())


def _personal_path(code: str) -> Path:
    compact = _compact_code(code)
    if not compact.startswith("FAM") or len(compact) < 8:
        raise HTTPException(status_code=400, detail="invalid_invite_code")
    # prevent path traversal
    safe = re.sub(r"[^A-Z0-9]", "", compact)
    return _OG_DIR / f"{safe}.jpg"


@router.get("/og.jpg")
def get_invite_og(code: str = Query(..., min_length=6, max_length=64)):
    """Crawlers / landing may use this URL as og:image (personal or default)."""
    try:
        path = _personal_path(code)
    except HTTPException:
        path = None
    if path and path.is_file():
        return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=3600"})
    if _DEFAULT.is_file():
        return FileResponse(_DEFAULT, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})
    # Repo-relative fallback for local/dev
    repo_default = (
        Path(__file__).resolve().parents[2]
        / "landing"
        / "og"
        / "family-invite-default-1200x630.jpg"
    )
    if repo_default.is_file():
        return FileResponse(repo_default, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="og_image_missing")


@router.post("/og.jpg")
async def upload_invite_og(
    code: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """iOS uploads InviteOGComposer JPEG after creating an invite (JWT required)."""
    _ = current_user  # auth gate
    data = await file.read()
    if not data or len(data) > _MAX_BYTES:
        raise HTTPException(status_code=400, detail="invalid_image_size")
    if data[:3] != b"\xff\xd8\xff":
        raise HTTPException(status_code=400, detail="jpeg_required")
    path = _personal_path(code)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"ok": True, "code": _compact_code(code), "path": str(path.name)}
