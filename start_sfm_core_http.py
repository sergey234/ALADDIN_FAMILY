# -*- coding: utf-8 -*-
"""SFM HTTP API (:8003) — real SafeFunctionManager, honest health, no silent fallback."""
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from aiohttp import web

APP_PATH = os.environ.get("ALADDIN_APP_PATH", "/opt/aladdin-backend/app")
BACKEND_PATH = os.environ.get("ALADDIN_BACKEND_PATH", "/opt/aladdin-backend")
REGISTRY_PATH = os.path.join(APP_PATH, "data/sfm/function_registry.json")

# Script lives in backend root — that dir shadows app/security unless removed first.
_script_dir = os.path.dirname(os.path.abspath(__file__))
for _shadow in (_script_dir, BACKEND_PATH):
    while _shadow in sys.path:
        sys.path.remove(_shadow)
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

sfm = None
sfm_load_error: Optional[str] = None

try:
    from security.safe_function_manager import SafeFunctionManager

    sfm = SafeFunctionManager()
except Exception as exc:
    sfm_load_error = str(exc)


def _registry_count_from_file() -> int:
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        functions = data.get("functions", data)
        return len(functions) if hasattr(functions, "__len__") else 0
    except OSError:
        return 0


def _runtime_functions_count() -> int:
    if sfm is not None and hasattr(sfm, "functions"):
        return len(sfm.functions)
    return _registry_count_from_file()


def _sfm_status_payload() -> Dict[str, Any]:
    registry_count = _registry_count_from_file()
    runtime_count = _runtime_functions_count()
    return {
        "sfm_loaded": sfm is not None,
        "fallback_mode": sfm is None,
        "registry_count": registry_count,
        "runtime_functions_count": runtime_count,
        "code_path": os.path.join(APP_PATH, "security/safe_function_manager.py"),
        "load_error": sfm_load_error,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _normalize_execute_result(
    ok: bool, result: Any, message: str
) -> Tuple[int, Dict[str, Any]]:
    if not ok:
        lowered = (message or "").lower()
        if "not found" in lowered or "не найден" in lowered or "unknown" in lowered:
            return 503, {
                "success": False,
                "error": message or "function_not_registered",
                "source": "real_sfm",
            }
        return 422, {
            "success": False,
            "error": message or "execute_failed",
            "source": "real_sfm",
        }
    return 200, {
        "success": True,
        "result": result,
        "source": "real_sfm",
    }


async def _run_sfm_execute(func: str, params: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    if sfm is None:
        return 503, {
            "success": False,
            "error": "sfm_not_loaded",
            "load_error": sfm_load_error,
            "source": "real_sfm",
        }

    try:
        from security.services.ai_prompt_gate import PIIPromptBlockedError, redact_sfm_params
        from security.services.ai_sfm_aggregate_schema import strip_forbidden_llm_params

        params, _removed = strip_forbidden_llm_params(params)
        try:
            params = redact_sfm_params(func, params)
        except PIIPromptBlockedError:
            return 422, {
                "success": False,
                "error": "PII blocked in AI prompt",
                "source": "real_sfm",
            }
    except ImportError:
        pass

    try:
        outcome = sfm.execute_function(func, params)
    except Exception as exc:
        return 500, {"success": False, "error": str(exc), "source": "real_sfm"}

    if isinstance(outcome, tuple) and len(outcome) >= 3:
        ok, result, message = outcome[0], outcome[1], outcome[2]
        return _normalize_execute_result(bool(ok), result, str(message or ""))

    if isinstance(outcome, dict):
        if outcome.get("success") is False or outcome.get("error"):
            return 503, {
                "success": False,
                "error": outcome.get("error", "execute_failed"),
                "source": "real_sfm",
            }
        return 200, {
            "success": True,
            "result": outcome.get("result", outcome),
            "source": "real_sfm",
        }

    return 200, {"success": True, "result": outcome, "source": "real_sfm"}


async def execute(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response(
            {"success": False, "error": "invalid_json"},
            status=400,
        )

    func = str(data.get("function", "") or "").strip()
    params = data.get("params") or {}
    if not func:
        return web.json_response(
            {"success": False, "error": "function_required"},
            status=400,
        )

    status, body = await _run_sfm_execute(func, params)
    return web.json_response(body, status=status)


async def health(request: web.Request) -> web.Response:
    runtime_count = _runtime_functions_count()
    payload = {
        "status": "healthy" if sfm is not None else "degraded",
        "sfm_loaded": sfm is not None,
        "functions_count": runtime_count,
        "registry_count": _registry_count_from_file(),
        "fallback_mode": sfm is None,
        "timestamp": datetime.utcnow().isoformat(),
    }
    code = 200 if sfm is not None else 503
    return web.json_response(payload, status=code)


async def sfm_status(request: web.Request) -> web.Response:
    payload = _sfm_status_payload()
    code = 200 if payload["sfm_loaded"] else 503
    return web.json_response(payload, status=code)


def _build_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/api/execute", execute)
    app.router.add_get("/api/health", health)
    app.router.add_get("/api/sfm/status", sfm_status)
    return app


if __name__ == "__main__":
    web.run_app(_build_app(), host="127.0.0.1", port=8003)
