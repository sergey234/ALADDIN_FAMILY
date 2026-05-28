from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Response

router = APIRouter(prefix="/v1/legal", tags=["legal"])

_LEGAL_FILES: dict[str, str] = {
    "vpn-terms": "vpn-terms.md",
    "vpn-aup": "vpn-aup.md",
    "vpn-data": "vpn-data.md",
    "vpn-instructions": "vpn-instructions.md",
}

_DOCS_DIR = Path(__file__).resolve().parent.parent / "legal_docs"


@router.get("/{slug}")
def get_legal_document(slug: str) -> Response:
    """Публичные тексты VPN (оферта, AUP, минимизация). Без авторизации — только статический markdown."""
    name = _LEGAL_FILES.get(slug)
    if name is None:
        raise HTTPException(status_code=404, detail="unknown document")
    path = _DOCS_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=503, detail="legal document missing on server")
    text = path.read_text(encoding="utf-8")
    return Response(
        content=text,
        status_code=200,
        media_type="text/markdown; charset=utf-8",
        headers={"Cache-Control": "public, max-age=3600"},
    )
