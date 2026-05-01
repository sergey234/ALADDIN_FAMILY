"""
Public content manifest / delta for iOS ContentSync (DeltaContractDTO / ManifestContractDTO).
Snake_case JSON at top level matches NetworkContentAPIClient decoders.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/content", tags=["content-compat"])

# Совпадает с ContentSeedProvider.manifestVersion (2): при уже засидированном локально каталоге клиент ходит только в /delta (noop).
CURRENT_MANIFEST_VERSION = 2

_GAME_CAT = "child_interface_category_games"


def _item(idx: int) -> Dict[str, Any]:
    return {
        "id": f"{_GAME_CAT}.{idx}",
        "categoryId": _GAME_CAT,
        "type": "game",
        "ageBand": "school_7_12",
        "version": 1,
        "metadata": {
            "locale": "ru",
            "title": f"Bootstrap контент {idx}",
            "subtitle": "Контент-пакет",
            "description": "Серверный bootstrap-манифест для ALADDIN",
            "tags": ["bootstrap", "server", _GAME_CAT],
            "estimatedDurationSec": 300 + idx * 30,
        },
        "payloadURL": None,
        "checksumSHA256": None,
        "isOfflineAvailable": True,
    }


def build_manifest_dict() -> Dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    categories: List[Dict[str, Any]] = [
        {
            "id": _GAME_CAT,
            "titleKey": _GAME_CAT,
            "icon": "🎮",
            "ageBand": "school_7_12",
        }
    ]
    items = [_item(1), _item(2), _item(3)]
    blob = json.dumps(
        {"v": CURRENT_MANIFEST_VERSION, "categories": categories, "items": items},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    checksum = hashlib.sha256(blob).hexdigest()
    return {
        "manifest_version": CURRENT_MANIFEST_VERSION,
        "generated_at": now,
        "min_supported_app_version": "1.0.0",
        "checksum_sha256": checksum,
        "signature": None,
        "categories": categories,
        "items": items,
    }


_MANIFEST_CACHE: Dict[str, Any] | None = None


def get_manifest() -> Dict[str, Any]:
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        _MANIFEST_CACHE = build_manifest_dict()
    return _MANIFEST_CACHE


@router.get("/manifest")
def content_manifest() -> Dict[str, Any]:
    return get_manifest()


@router.get("/delta")
def content_delta(from_version: int = Query(..., alias="fromVersion")) -> Dict[str, Any]:
    """
    iOS sends query param fromVersion (camelCase). Empty patch when already up to date.
    Wrong chain → client refetches full manifest after error (see ContentSyncManager).
    """
    if from_version == CURRENT_MANIFEST_VERSION:
        base = "delta-noop"
        h = hashlib.sha256(base.encode("utf-8")).hexdigest()
        return {
            "from_version": from_version,
            "to_version": CURRENT_MANIFEST_VERSION,
            "added": [],
            "updated": [],
            "removed_ids": [],
            "checksum_sha256": h,
        }
    raise HTTPException(
        status_code=400,
        detail=f"content_delta chain mismatch: fromVersion={from_version} expected {CURRENT_MANIFEST_VERSION}",
    )
