"""
Antivirus file scan API (canonical contract for iOS `MalwareFileScanAPIRequest`).

POST /api/antivirus/scan
Body JSON (snake_case): file_data (base64), file_name, file_size, file_hash (optional).

Response JSON (snake_case): clean, threats_found, recommendations, scan_time, confidence.

Notes:
- Max decoded payload 25 MiB (aligned with iOS `maxServerScanUploadMegabytes`).
- Heuristic stub: detects EICAR test string; otherwise returns clean=true.
- Does not persist file contents (only optional client `file_hash` + path/name/size in DB).
- При валидном JWT: найденные угрозы upsert в PostgreSQL (`user_malware_threats`); сессия БД открывается только на этом пути.
"""

from __future__ import annotations

import base64
import binascii
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.auth import get_current_user_optional
from app.database.database import SessionLocal
from app.services.user_malware_threats import upsert_threats_from_scan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/antivirus", tags=["antivirus"])

_MAX_BYTES = 25 * 1024 * 1024

_EICAR_MARKER = b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"


class FileScanRequest(BaseModel):
    file_data: str = Field(..., description="Base64-encoded file contents")
    file_name: str = Field(..., max_length=512)
    file_size: int = Field(..., ge=0, le=_MAX_BYTES)
    file_hash: Optional[str] = Field(None, max_length=128)


class ThreatItem(BaseModel):
    id: str
    name: str
    type: str = "test_signature"
    severity: str = "low"
    description: str
    confidence: float = 1.0


class FileScanResponse(BaseModel):
    clean: bool
    threats_found: List[ThreatItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    scan_time: float
    confidence: float = 0.99


@router.post("/scan", response_model=FileScanResponse)
async def scan_uploaded_file(
    payload: FileScanRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
) -> FileScanResponse:
    t0 = time.perf_counter()
    raw_b64 = payload.file_data.strip()
    if not raw_b64:
        raise HTTPException(status_code=400, detail="file_data is empty")

    try:
        decoded = base64.b64decode(raw_b64, validate=True)
    except binascii.Error as e:
        raise HTTPException(status_code=400, detail=f"invalid base64: {e}") from e

    if len(decoded) > _MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"decoded file exceeds {_MAX_BYTES} bytes",
        )

    threats: List[ThreatItem] = []
    clean = True
    recommendations: List[str] = [
        "Server scan is heuristic; keep local AV enabled.",
    ]

    if _EICAR_MARKER in decoded.upper():
        clean = False
        threats.append(
            ThreatItem(
                id="eicar-test",
                name="EICAR test file",
                description="Standard anti-malware test string detected.",
                severity="low",
                confidence=1.0,
            )
        )
        recommendations.insert(0, "Test signature only — safe to delete the file.")

    scan_time = time.perf_counter() - t0
    response = FileScanResponse(
        clean=clean,
        threats_found=threats,
        recommendations=recommendations,
        scan_time=round(scan_time, 4),
        confidence=0.99 if clean else 1.0,
    )

    if current_user and threats:
        uid = str(current_user.get("id") or "").strip()
        if uid:
            db = SessionLocal()
            try:
                payload_dicts: List[Dict[str, Any]] = []
                for t in threats:
                    payload_dicts.append(
                        {
                            "id": t.id,
                            "name": t.name,
                            "type": t.type,
                            "severity": t.severity,
                            "confidence": t.confidence,
                        }
                    )
                upsert_threats_from_scan(
                    db,
                    uid,
                    payload_dicts,
                    payload.file_name,
                    payload.file_size,
                    logical_file_path=payload.file_name,
                    file_hash=payload.file_hash,
                )
            except Exception as e:
                db.rollback()
                logger.warning(
                    "malware_threats_persist_failed user=%s err=%s",
                    uid,
                    e,
                    exc_info=True,
                )
            finally:
                db.close()

    return response
