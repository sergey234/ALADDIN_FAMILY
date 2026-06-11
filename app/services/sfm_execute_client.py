"""HTTP client for SFM :8003 — used by explicit mapped routers (W10)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Tuple

from fastapi import HTTPException

SFM_EXECUTE_URL = "http://127.0.0.1:8003/api/execute"


def execute_mapped_function(
    api_function_name: str,
    params: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    try:
        from complete_api_sfm_mapping import get_sfm_function_name
    except ImportError:
        get_sfm_function_name = lambda name: name  # type: ignore

    sfm_function = get_sfm_function_name(api_function_name)
    payload = json.dumps(
        {"function": sfm_function, "params": params or {}}
    ).encode("utf-8")
    request = urllib.request.Request(
        SFM_EXECUTE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"success": False, "error": raw or str(exc)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"sfm_unavailable: {exc}") from exc

    if status >= 500 or not body.get("success", True):
        detail = body.get("error") or body.get("message") or "sfm_execute_failed"
        raise HTTPException(status_code=503, detail=str(detail))

    result = body.get("result", body)
    if isinstance(result, dict) and result.get("status") == "success" and "verdict" not in result:
        raise HTTPException(status_code=503, detail="mock_success_rejected")

    return result if isinstance(result, dict) else {"data": result}
