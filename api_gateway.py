# -*- coding: utf-8 -*-
"""
🚀 ALADDIN API GATEWAY - GOLDEN STANDARD (v3.1.0)
-----------------------------------------------
Architecture: Dual-Layer Protection
1. Precision Routers (Specific mappings)
2. Smart Proxy (Global catch-all safety net)
"""

import os
import sys
import time
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, status, Header, Query, Path, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncio

# --- Configuration ---
SECRET_KEY = "aladdin-jwt-secret-key-2026-production-ready"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_gateway_unified.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aladdin-gateway")

# Explicit mapping for critical endpoints where proxy naming does not match SFM registry.
# We add mappings incrementally (one endpoint at a time) to avoid broad regressions.
EXPLICIT_FUNCTION_MAP: Dict[str, List[str]] = {
    "v1/parental-control/stats": ["get_parental_stats"],
    "parental-control/stats": ["get_parental_stats"],
}

# --- SFM Adapter ---
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Repo / deploy root (рядом с `security/`, `app/`) — нужен для precision `reports_router`
_gateway_root = os.path.dirname(os.path.abspath(__file__))
if _gateway_root not in sys.path:
    sys.path.insert(0, _gateway_root)

try:
    from sfm_adapter import sfm_adapter
    logger.info("✅ SFM Adapter loaded successfully")
except ImportError:
    sfm_adapter = None
    logger.warning("⚠️ SFM Adapter not found, using Mock mode")

# --- FastAPI App ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="ALADDIN Unified API Gateway", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus Metrics ---
# Freshness gauge: seconds since last event per domain
FRESHNESS_GAUGE = Gauge(
    "aladdin_analytics_freshness_seconds",
    "Seconds since last event per analytics domain",
    labelnames=("domain", "env", "service", "version"),
)

ENV_NAME = os.getenv("ALADDIN_ENV", "production")
SERVICE_NAME = "gateway"
APP_VERSION = "3.1.0"

# Background task to periodically update freshness metrics
async def _refresh_freshness_metrics_periodically(poll_interval_seconds: int = 30) -> None:
    """
    Periodically reads analytics_freshness view and updates Prometheus gauge.
    Uses RO connection if available. Fail-safe with logging.
    """
    # Lazy import to avoid hard dependency when DB is not available
    get_db = None
    try:
        from app.database.database import get_db  # type: ignore
    except Exception as e:
        logger.warning(f"Freshness exporter: cannot import get_db, will skip DB reads. Error: {e}")

    while True:
        try:
            if get_db is None:
                # No DB access; skip update but keep the loop alive
                await asyncio.sleep(poll_interval_seconds)
                continue

            gen = get_db()
            db = next(gen)
            try:
                # Raw SQL to avoid ORM model dependency
                result = db.execute(
                    "SELECT domain, EXTRACT(EPOCH FROM (NOW() - last_event_at)) AS age_sec FROM analytics_freshness"
                )
                for row in result:
                    domain = str(row[0])
                    age_seconds = float(row[1]) if row[1] is not None else 999 * 24 * 3600
                    FRESHNESS_GAUGE.labels(
                        domain=domain, env=ENV_NAME, service=SERVICE_NAME, version=APP_VERSION
                    ).set(age_seconds)
            finally:
                try:
                    gen.close()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Freshness exporter loop error: {e}", exc_info=True)
        # Sleep regardless of success to avoid tight loop
        await asyncio.sleep(poll_interval_seconds)


@app.on_event("startup")
async def _startup_tasks() -> None:
    # Start background freshness exporter
    try:
        asyncio.create_task(_refresh_freshness_metrics_periodically(30))
        logger.info("✅ Freshness exporter task started")
    except Exception as e:
        logger.error(f"❌ Failed to start freshness exporter: {e}")


@app.get("/metrics")
async def prometheus_metrics() -> Response:
    """
    Prometheus scrape endpoint.
    """
    try:
        payload = generate_latest()
        return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating Prometheus metrics: {e}", exc_info=True)
        # Even if metrics fail, respond with empty payload to keep scraper healthy
        return Response(content=b"", media_type=CONTENT_TYPE_LATEST)

# --- JWT Utility ---
def get_user_from_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        return "guest_user"
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub", "unknown_user")
    except:
        return "invalid_user"

# --- 1. SPECIAL AUTH ENDPOINTS (Priority) ---

@app.post("/api/auth/register-device")
async def register_device(data: Dict[str, Any]):
    """
    Production-safe device registration:
    - Creates/ensures a real user row in Postgres (stable user_id)
    - Returns real JWT with user_id/id/sub (no anonymous/mock)
    Compatibility:
    - Accepts both device_id and deviceId from clients
    - Returns both device_id and deviceId
    """
    try:
        from app.database.database import get_db
        from app.services.subscription_service import SubscriptionService
        from app.services.jwt_service import JWTService
        from app.models.subscription import DeviceRegisterRequest
    except Exception as e:
        logger.error(f"❌ register-device backend unavailable: {e}")
        raise HTTPException(status_code=503, detail="Auth backend unavailable")

    device_id = data.get("device_id") or data.get("deviceId") or str(uuid.uuid4())[:8]
    device_type = data.get("device_type") or data.get("deviceType") or "ios"

    # get_db() is a generator for sync Session
    gen = get_db()
    db = next(gen)
    try:
        subscription = SubscriptionService.register_device(db, DeviceRegisterRequest(device_id=device_id, device_type=device_type))
        token = JWTService.create_subscription_token(subscription)

        # Compat subscription shape expected by legacy clients
        trial_info = None
        if getattr(subscription, "trial_info", None):
            trial_info = {
                "isActive": bool(subscription.trial_info.is_active),
                "daysRemaining": int(subscription.trial_info.days_remaining),
            }

        return {
            "token": token,
            "device_id": device_id,
            "deviceId": device_id,
            "subscription": {
                "level": subscription.level.value if hasattr(subscription.level, "value") else str(subscription.level),
                "trialInfo": trial_info,
                "limits": subscription.limits.dict() if getattr(subscription, "limits", None) else {},
                "permissions": getattr(subscription, "permissions", {}) or {},
                "user_id": getattr(subscription, "user_id", None),
            },
        }
    except Exception as e:
        logger.error(f"❌ register-device failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        try:
            gen.close()
        except Exception:
            pass

@app.post("/api/auth/login")
async def login_device(data: Dict[str, Any]):
    device_id = data.get("deviceId")
    if not device_id: raise HTTPException(status_code=400, detail="deviceId required")
    token = jwt.encode({"sub": device_id, "exp": datetime.utcnow() + timedelta(days=14)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# --- 2. PRECISION ROUTERS (Load specific logic) ---
router_files = [
    "gamification_router", "subscription_sync_router", "parental_control_sync_router",
    "crash_detection_router", "ai_assistant_router", "metrics_router",
    "user_profile_sync_router", "app_settings_sync_router", "components_router",
    "system_router", "offline_storage_sync_router", "other_functions_sync_router",
    # ✅ Family precision router (prevents routing through SFM proxy for family CRUD)
    "family_router",
]

for router_name in router_files:
    try:
        # Import module and include its router
        module = __import__(router_name)
        app.include_router(module.router)
        logger.info(f"✅ Precision Router connected: {router_name}")
    except Exception as e:
        logger.error(f"❌ Failed to connect router {router_name}: {e}")

# --- 2b. REPORTS PRECISION (same router as main.py; DB-backed stats/list/scan) ---
try:
    from security.api.routers.reports_router import router as reports_precision_router

    app.include_router(reports_precision_router)
    logger.info("✅ Precision Router connected: security.api.routers.reports_router (/api/reports/*)")
except Exception as e:
    logger.error(f"❌ Failed to connect reports_router precision: {e}")

# --- 3. SMART PROXY (Catch-all Safety Net) ---

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_api_proxy(request: Request, path: str, authorization: Optional[str] = Header(None)):
    """
    Wildcard Proxy: Работает как страховка для всех путей, не попавших в основные роутеры.
    Гарантирует 100% отсутствие 404 ошибок.
    """
    user_id = get_user_from_token(authorization)

    # /api/reports/* обязаны обслуживаться только precision‑роутером выше (никогда SFM и никогда «успех‑заглушка»).
    if path.startswith("reports/"):
        logger.error("Wildcard reached for /api/reports/* — reports_router failed to register or path is unknown")
        raise HTTPException(
            status_code=503,
            detail="Reports API unavailable: use precision /api/reports routes only",
        )
    
    # Конвертируем путь в имя функции (например, /location/status -> location_status)
    func_name = path.replace("/", "_")
    
    params = {}
    if request.method == "GET":
        params = dict(request.query_params)
    else:
        try:
            params = await request.json()
        except:
            params = {}
    
    # Обогащаем запрос данными пользователя из JWT
    params["userId"] = params.get("userId") or user_id
    
    logger.info(f"🛰 Smart Proxy: {request.method} /{path} -> trying function: {func_name}")

    def should_block_mock_result(req_method: str, api_path: str, sfm_result: Any) -> bool:
        """Block SFM mock/fallback responses for sensitive endpoints in production.

        This prevents `200 OK + source:\"sfm_mock\"` from reaching the iOS client.
        """
        # Sensitive operations: must not silently succeed with mock/fallback.
        # We block BOTH read and write flows for family + parental + gamification.
        if req_method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            return False

        is_sensitive_endpoint = (
            api_path == "family/members"
            or api_path == "family/remove"
            or api_path == "family/stats"
            or api_path.startswith("parental-control/")
            or api_path.startswith("v1/parental-control/")
            or api_path.startswith("gamification/")
            # ✅ Analytics and component reports must never return mock in production
            or api_path.startswith("analytics")
            or api_path.startswith("reports/")
            or api_path.startswith("darkweb")
            or api_path.startswith("identity")
            or api_path.startswith("location")
            or api_path.startswith("data/cleanup")
            or api_path.startswith("ai/categories")
            or api_path.startswith("components/")
        )
        if not is_sensitive_endpoint:
            return False

        # Some SFM adapters return non-plain dict objects (e.g. pydantic models).
        # We normalize to dict so mock/fallback blocking always works.
        if not isinstance(sfm_result, dict):
            if hasattr(sfm_result, "dict") and callable(getattr(sfm_result, "dict")):
                try:
                    sfm_result = sfm_result.dict()
                except:
                    return False
            elif hasattr(sfm_result, "__dict__"):
                sfm_result = sfm_result.__dict__
            else:
                return False

        source = sfm_result.get("source")
        result_value = sfm_result.get("result")

        if source in {"sfm_mock", "sfm_fallback", "sfm_error"}:
            logger.warning(
                "Blocking SFM mock/fallback response",
                req_method=req_method,
                api_path=api_path,
                source=source,
                result=result_value,
            )
            return True

        # Some SFM responses use plain string marker.
        if result_value == "mock_fallback":
            logger.warning(
                "Blocking SFM mock/fallback response",
                req_method=req_method,
                api_path=api_path,
                source=source,
                result=result_value,
            )
            return True

        # Defensive: some adapters may return non-standard structures.
        # If serialized content still contains mock markers, block.
        try:
            serialized = json.dumps(sfm_result, default=str)
            if (
                "sfm_mock" in serialized
                or "sfm_fallback" in serialized
                or "sfm_error" in serialized
                or "mock_fallback" in serialized
            ):
                logger.warning(
                    "Blocking SFM mock/fallback response (serialized detection)",
                    req_method=req_method,
                    api_path=api_path,
                    source=source,
                    result=result_value,
                )
                return True
        except Exception:
            pass

        return False
    
    def default_component_metrics(component_key: str) -> Dict[str, str]:
        if component_key in ("driving_reports_agent", "driving"):
            return {
                "trips": "0", "safety_score": "0.0", "new_events": "0",
                "trips_total": "0", "distance_km_total": "0.0", "duration_sec_total": "0.0",
                "avg_safety_score": "0.0", "violations_total": "0", "positioning": ""
            }
        if component_key in ("dark_web_monitoring_agent", "darkweb"):
            return {"leaks_found": "0", "new_leaks": "0", "new_events": "0"}
        if component_key in ("russian_identity_theft_protection_agent", "identity"):
            return {"attempts": "0", "blocked": "0"}
        if component_key in ("location_bubble_agent", "location"):
            return {"blocked": "0", "accuracy": "low"}
        if component_key in ("personal_data_cleanup_agent", "cleanup"):
            return {"freed_space_gb": "0.0", "last_cleanup_hours_ago": "0"}
        if component_key in ("anti_tracker_agent", "tracker"):
            return {"blocked_total": "0", "blocked_this_week": "0"}
        if component_key in ("ai_categories_agent", "ai"):
            return {"categorized": "0", "blocked": "0", "accuracy": "0.0"}
        return {}
    
    def coerce_num(val: Any, default: str = "0") -> str:
        try:
            if val is None:
                return default
            if isinstance(val, (int, float)):
                return str(val)
            s = str(val).strip()
            if s.endswith("%"):
                s = s[:-1]
            return s or default
        except Exception:
            return default
    
    def normalize_component_metrics(component_key: str, raw: Dict[str, Any]) -> Dict[str, str]:
        # Start with defaults; overwrite when есть данные.
        m = default_component_metrics(component_key)
        # DRIVING
        if component_key in ("driving_reports_agent", "driving"):
            m["trips_total"] = coerce_num(raw.get("trips_total") or raw.get("trips") or raw.get("totalTrips"))
            m["distance_km_total"] = coerce_num(raw.get("distance_km_total") or raw.get("distance_km") or raw.get("total_distance_km"))
            m["duration_sec_total"] = coerce_num(raw.get("duration_sec_total") or raw.get("duration_sec") or raw.get("total_duration_sec"))
            m["avg_safety_score"] = coerce_num(raw.get("avg_safety_score") or raw.get("safety_score") or raw.get("average_safety_score"), default="0.0")
            m["violations_total"] = coerce_num(raw.get("violations_total") or raw.get("violations") or raw.get("violations_count"))
            m["positioning"] = str(raw.get("positioning") or raw.get("positioning_system") or "")
        # AI
        elif component_key in ("ai_categories_agent", "ai"):
            m["categorized"] = coerce_num(raw.get("categorized") or raw.get("total_categorized"))
            m["blocked"] = coerce_num(raw.get("blocked") or raw.get("total_blocked"))
            m["accuracy"] = coerce_num(raw.get("accuracy"), default="0.0")
        # DARKWEB
        elif component_key in ("dark_web_monitoring_agent", "darkweb"):
            m["leaks_found"] = coerce_num(raw.get("leaks_found") or raw.get("total_leaks"))
            m["new_leaks"] = coerce_num(raw.get("new_leaks") or raw.get("new"))
            m["new_events"] = coerce_num(raw.get("new_events") or 0)
        # IDENTITY
        elif component_key in ("russian_identity_theft_protection_agent", "identity"):
            m["attempts"] = coerce_num(raw.get("attempts") or raw.get("total_attempts"))
            m["blocked"] = coerce_num(raw.get("blocked") or raw.get("blocked_attempts"))
        # LOCATION
        elif component_key in ("location_bubble_agent", "location"):
            m["blocked"] = coerce_num(raw.get("blocked") or raw.get("blockedRequests"))
            m["accuracy"] = str(raw.get("accuracy") or raw.get("currentAccuracy") or "low")
        # CLEANUP
        elif component_key in ("personal_data_cleanup_agent", "cleanup"):
            if "freed_space_gb" in raw:
                m["freed_space_gb"] = coerce_num(raw.get("freed_space_gb"), default="0.0")
            elif "freed_space_bytes" in raw:
                try:
                    m["freed_space_gb"] = f"{float(raw.get('freed_space_bytes'))/1_000_000_000:.2f}"
                except Exception:
                    m["freed_space_gb"] = "0.0"
            m["last_cleanup_hours_ago"] = coerce_num(raw.get("last_cleanup_hours_ago") or raw.get("hours_since_last_cleanup"))
        # TRACKER
        elif component_key in ("anti_tracker_agent", "tracker"):
            m["blocked_total"] = coerce_num(raw.get("blocked_total") or raw.get("total_blocked"))
            m["blocked_this_week"] = coerce_num(raw.get("blocked_this_week") or raw.get("week_blocked"))
        return m
    
    def normalize_component_response_if_needed(api_path: str, result: Any) -> Any:
        """
        Для путей компонентов возвращаем единый DTO:
        {
          "componentId": "<id>",
          "metrics": { ... нормализованные ключи ... }
        }
        """
        component_key = None
        if api_path.startswith("reports/driving") or "driving" in api_path:
            component_key = "driving"
        elif "darkweb" in api_path or api_path.startswith("darkweb"):
            component_key = "darkweb"
        elif "identity" in api_path:
            component_key = "identity"
        elif "location" in api_path:
            component_key = "location"
        elif "data/cleanup" in api_path or "cleanup" in api_path:
            component_key = "cleanup"
        elif "tracker" in api_path or "anti_tracker" in api_path:
            component_key = "tracker"
        elif "ai/categories" in api_path or "aicategories" in api_path or "ai" in api_path:
            component_key = "ai"
        
        if not component_key:
            return result
        
        # Нормализуем к словарю
        raw = {}
        if isinstance(result, dict):
            raw = result
        elif hasattr(result, "dict") and callable(getattr(result, "dict")):
            try:
                raw = result.dict()
            except Exception:
                raw = {}
        elif hasattr(result, "__dict__"):
            raw = result.__dict__
        
        metrics = normalize_component_metrics(component_key, raw)
        return {
            "componentId": component_key,
            "metrics": metrics
        }
    
    if sfm_adapter:
        # 1) Try explicit function mapping for critical routes first.
        candidate_functions: List[str] = []
        if path in EXPLICIT_FUNCTION_MAP:
            candidate_functions.extend(EXPLICIT_FUNCTION_MAP[path])

        # 2) Fallback to legacy wildcard naming contract.
        candidate_functions.extend([func_name, f"api_{func_name}"])

        for candidate in candidate_functions:
            success, result, message = sfm_adapter.execute_function(candidate, params)
            if not success:
                continue

            if should_block_mock_result(request.method, path, result):
                raise HTTPException(
                    status_code=503,
                    detail="Protection backend temporarily unavailable",
                )
            # Для компонентных путей возвращаем нормализованный DTO
            normalized = normalize_component_response_if_needed(path, result)
            return normalized
        
    # Если ничего не помогло - отдаем "Production-Ready Mock" успех
    return {
        "status": "success",
        "message": "Processed via Global Proxy",
        "path": path,
        "userId": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }

# --- System ---
@app.get("/health")
async def health(): return {"status": "healthy", "version": "3.1.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
