"""
ALADDIN Backend - FastAPI приложение
Главный файл для запуска API сервера
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import time
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import referral
from app.routers import referral_test
from app.routers import payments
from app.database.database import Base, engine
import asyncio
import os
from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import re
from sqlalchemy import text
from security.api.routers.location_bubble_router import router as location_router
from security.api.routers.identity_theft_protection_router import router as identity_router
from security.api.routers.driving_reports_router import router as driving_router

# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Импортируем роутер для авторизации
try:
    from app.routers import auth_router
    auth_router_available = True
except ImportError:
    # Если файл находится в docs/server, используем прямой импорт
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from auth_router import router as auth_router_router
        auth_router_available = True
    except ImportError:
        print("⚠️ Предупреждение: auth_router не найден. Endpoint /api/auth/login будет недоступен.")
        auth_router_available = False

# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Импортируем роутер для компонентов
try:
    from app.routers import components
    components_router_available = True
except ImportError:
    # Если файл находится в docs/server, используем прямой импорт
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from COMPONENTS_API_ENDPOINTS import router as components_router
        components_router_available = True
    except ImportError:
        print("⚠️ Предупреждение: COMPONENTS_API_ENDPOINTS не найден. Endpoints для компонентов будут недоступны.")
        components_router_available = False

# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Импортируем роутер для Protection API (138 функций)
try:
    from app.routers import protection
    protection_router_available = True
except ImportError:
    # Если файл находится в docs/server, используем прямой импорт
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from PROTECTION_API_ENDPOINTS import router as protection_router
        protection_router_available = True
    except ImportError:
        print("⚠️ Предупреждение: PROTECTION_API_ENDPOINTS не найден. Endpoints для защиты будут недоступны.")
        protection_router_available = False

# ✅ ДОБАВЛЕНО: Импортируем роутер для Family API
try:
    from app.routers import family
    family_router_available = True
except ImportError:
    # Если файл находится в docs/server, используем прямой импорт
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from FAMILY_API_ENDPOINTS import router as family_router
        family_router_available = True
    except ImportError:
        print("⚠️ Предупреждение: FAMILY_API_ENDPOINTS не найден. Endpoint /api/family/stats будет недоступен.")
        family_router_available = False

# ✅ ДОБАВЛЕНО: Импортируем роутер для User API compat
try:
    from app.routers import user as user_router_module
    user_router_available = True
except ImportError:
    user_router_available = False

# ✅ ДОБАВЛЕНО: Импортируем роутер для System/AI compat
try:
    from app.routers import system_ai_compat
    system_ai_compat_available = True
except ImportError:
    system_ai_compat_available = False

try:
    from app.routers import network_protection_compat
    network_protection_compat_available = True
except ImportError:
    network_protection_compat_available = False

try:
    from app.routers import subscription_compat
    subscription_compat_available = True
except ImportError:
    subscription_compat_available = False

try:
    from app.routers import subscription_events
    subscription_events_available = True
except ImportError:
    subscription_events_available = False

try:
    from app.routers import notifications_compat
    notifications_compat_available = True
except ImportError:
    notifications_compat_available = False

try:
    from app.routers import crash_detection_compat
    crash_detection_compat_available = True
except ImportError:
    crash_detection_compat_available = False

try:
    from app.routers import parental_compat
    parental_compat_available = True
except ImportError:
    parental_compat_available = False

try:
    from app.routers import misc_other_compat
    misc_other_compat_available = True
except ImportError:
    misc_other_compat_available = False

# ✅ ДОБАВЛЕНО: Импортируем роутер для Analytics API
try:
    from app.routers import analytics_router
    analytics_router_available = True
except ImportError:
    # Если файл находится в docs/server, используем прямой импорт
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    try:
        from analytics_router import router as analytics_router_router
        analytics_router_available = True
    except ImportError:
        print("⚠️ Предупреждение: analytics_router не найден. Endpoint /api/analytics будет недоступен.")
        analytics_router_available = False
# ✅ ДОБАВЛЕНО: Импортируем Security Routers
security_routers = {}

# AI Categories Router
try:
    from security.api.routers.ai_categories_router import router as ai_categories_router
    security_routers['ai_categories'] = ai_categories_router
except ImportError as e:
    print(f"⚠️ ai_categories_router недоступен: {e}")

# Anti Tracker Router
try:
    from security.api.routers.anti_tracker_router import router as anti_tracker_router
    security_routers['anti_tracker'] = anti_tracker_router
except ImportError as e:
    print(f"⚠️ anti_tracker_router недоступен: {e}")

# Crash Detection Router (используем оптимизированную версию)
try:
    from security.api.routers.crash_detection_router_optimized import router as crash_detection_router
    security_routers['crash_detection'] = crash_detection_router
    print("✅ Crash Detection Router (optimized) подключен")
except ImportError as e:
    # Fallback на обычную версию, если optimized недоступна
    try:
        from security.api.routers.crash_detection_router import router as crash_detection_router
        security_routers['crash_detection'] = crash_detection_router
        print("✅ Crash Detection Router подключен (fallback)")
    except ImportError as e2:
        print(f"⚠️ crash_detection_router недоступен: {e2}")

# Dark Web Monitoring Router
try:
    from security.api.routers.dark_web_monitoring_router import router as dark_web_router
    security_routers['dark_web'] = dark_web_router
except ImportError as e:
    print(f"⚠️ dark_web_monitoring_router недоступен: {e}")

# Data Cleanup Router
try:
    from security.api.routers.data_cleanup_router import router as data_cleanup_router
    security_routers['data_cleanup'] = data_cleanup_router
except ImportError as e:
    print(f"⚠️ data_cleanup_router недоступен: {e}")

# Identity Theft Protection Router
try:
    from security.api.routers.identity_theft_protection_router import router as identity_theft_router
    security_routers['identity_theft'] = identity_theft_router
except ImportError as e:
    print(f"⚠️ identity_theft_protection_router недоступен: {e}")

# Location Bubble Router
try:
    from security.api.routers.location_bubble_router import router as location_bubble_router
    security_routers['location_bubble'] = location_bubble_router
except ImportError as e:
    print(f"⚠️ location_bubble_router недоступен: {e}")

# Roadside Assistance Router
try:
    from security.api.routers.roadside_assistance_router import router as roadside_assistance_router
    security_routers["roadside_assistance"] = roadside_assistance_router
except ImportError as e:
    print(f"⚠️ roadside_assistance_router недоступен: {e}")
# ✅ ДОБАВЛЕНО: Импортируем Parental Control Router
try:
    from security.api.routers.parental_control_router import (
        router as parental_control_router,
        legacy_router as parental_control_legacy_router,
        bypass_router as parental_bypass_router
    )
    parental_control_available = True
except ImportError as e:
    print(f"⚠️ parental_control_router недоступен: {e}")
    parental_control_available = False

# ✅ ДОБАВЛЕНО: Импортируем IoT Router
try:
    from security.api.routers.iot_router import router as iot_router
    iot_available = True
except ImportError as e:
    print(f"⚠️ iot_router недоступен: {e}")
    iot_available = False

# ✅ ДОБАВЛЕНО: Импортируем Notifications Router
try:
    from security.api.routers.notifications_router import router as notifications_router
    NOTIFICATIONS_ROUTER_AVAILABLE = True
    notifications_available = True
except ImportError as e:
    print(f"⚠️ notifications_router недоступен: {e}")
    notifications_available = False

# ✅ ДОБАВЛЕНО: Импортируем AI Assistant Router
try:
    from security.api.routers.ai_assistant_router import router as ai_assistant_router
    ai_assistant_available = True
    print("✅ AI Assistant Router loaded")
except ImportError as e:
    print(f"❌ AI Assistant Router not available: {e}")
    ai_assistant_available = False
    ai_assistant_router = None

# ✅ ЗАДАЧА 21: Импортируем Components Router
try:
    from security.api.routers.components_router import router as components_router
    components_router_available = True
except ImportError as e:
    print(f"⚠️ components_router недоступен: {e}")
    components_router_available = False
    components_router = None

# ✅ ЗАДАЧА 23: Импортируем System Router
try:
    from security.api.routers.system_router import router as system_router
    from security.api.routers.metrics_router import router as metrics_router
    system_router_available = True
    metrics_router_available = True
except ImportError as e:
    print(f"⚠️ system_router недоступен: {e}")
    system_router_available = False
    system_router = None
    metrics_router = None

# ✅ ГЕЙМИФИКАЦИЯ: Импортируем Gamification Router
try:
    from security.api.routers.gamification_router import router as gamification_router
    gamification_router_available = True
except ImportError as e:
    print(f"⚠️ gamification_router недоступен: {e}")
    gamification_router_available = False
    gamification_router = None

# ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Импортируем Parental Control Sync Router
try:
    from security.api.routers.parental_control_sync_router import router as parental_control_sync_router
    parental_control_sync_router_available = True
except ImportError as e:
    print(f"⚠️ parental_control_sync_router недоступен: {e}")
    parental_control_sync_router_available = False
    parental_control_sync_router = None

# ✅ ЭТАП 2: Импортируем User Profile Sync Router
try:
    from security.api.routers.user_profile_sync_router import router as user_profile_sync_router
    user_profile_sync_router_available = True
except ImportError as e:
    print(f"⚠️ user_profile_sync_router недоступен: {e}")
    user_profile_sync_router_available = False
    user_profile_sync_router = None

# ✅ ЭТАП 2: Импортируем Subscription Sync Router
try:
    from security.api.routers.subscription_sync_router import router as subscription_sync_router
    subscription_sync_router_available = True
except ImportError as e:
    print(f"⚠️ subscription_sync_router недоступен: {e}")
    subscription_sync_router_available = False
    subscription_sync_router = None

# ✅ ЭТАП 2: Импортируем основной Subscription Router
try:
    from app.routers.subscription import router as subscription_router
    print(f"✅ subscription_router импортирован: {subscription_router}")
    subscription_router_available = True
except ImportError as e:
    print(f"⚠️ subscription_router недоступен: {e}")
    subscription_router_available = False
    subscription_router = None

# ✅ ЭТАП 2: Импортируем App Settings Sync Router
try:
    from security.api.routers.app_settings_sync_router import router as app_settings_sync_router
    app_settings_sync_router_available = True
except ImportError as e:
    print(f"⚠️ app_settings_sync_router недоступен: {e}")
    app_settings_sync_router_available = False
    app_settings_sync_router = None

# ✅ ЭТАП 2: Импортируем Other Functions Sync Router
try:
    from security.api.routers.other_functions_sync_router import router as other_functions_sync_router
    other_functions_sync_router_available = True
except ImportError as e:
    print(f"⚠️ other_functions_sync_router недоступен: {e}")
    other_functions_sync_router_available = False
    other_functions_sync_router = None

# ✅ ЭТАП 3: Импортируем Offline Storage Sync Router
try:
    from security.api.routers.offline_storage_sync_router import router as offline_storage_sync_router
    offline_storage_sync_router_available = True
except ImportError as e:
    print(f"⚠️ offline_storage_sync_router недоступен: {e}")
    offline_storage_sync_router_available = False
    offline_storage_sync_router = None

# ✅ ЭТАП 3: Импортируем Crash Detection Sync Router
try:
    from security.api.routers.crash_detection_sync_router import router as crash_detection_sync_router
    crash_detection_sync_router_available = True
except ImportError as e:
    print(f"⚠️ crash_detection_sync_router недоступен: {e}")
    crash_detection_sync_router_available = False
    crash_detection_sync_router = None

# ✅ ЭТАП 3: Импортируем Elderly Interface Sync Router
try:
    from security.api.routers.elderly_interface_sync_router import router as elderly_interface_sync_router
    elderly_interface_sync_router_available = True
except ImportError as e:
    print(f"⚠️ elderly_interface_sync_router недоступен: {e}")
    elderly_interface_sync_router_available = False
    elderly_interface_sync_router = None

# Создание приложения FastAPI
app = FastAPI(
    title="ALADDIN API",
    version="1.0.0",
    description="Backend API для приложения ALADDIN"
)

# Настройка CORS (разрешить запросы с любых доменов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ВАРИАНТ 5: Middleware для отключения кэширования API ответов
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# ✅ Tочечный фикс для прод-API:
# если backend защиты отдал mock/fallback/error (SFM) в виде `source:*`,
# возвращаем 503, чтобы iOS не воспринимала ответ как успешный `200 OK`.
class SfmMockTo503Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        try:
            # Важно: не трогаем реально отсутствующие маршруты (404).
            if response.status_code == 404:
                return response

            request_path = request.url.path
            is_target_endpoint = (
                request_path in {
                    "/api/user/profile",
                    "/api/family/members",
                    "/api/family/stats",
                    "/api/family/remove",
                }
                or request_path.startswith("/api/parental-control/")
                or request_path.startswith("/api/v1/parental-control/")
                or request_path.startswith("/api/gamification/")
                or request_path.startswith("/api/components/")
                # ✅ Блокируем mock/fallback для аналитики и компонентных отчётов
                or request_path.startswith("/api/analytics")
                or request_path.startswith("/api/reports/")
                or request_path.startswith("/api/darkweb")
                or request_path.startswith("/api/identity")
                or request_path.startswith("/api/location")
                or request_path.startswith("/api/data/cleanup")
                or request_path.startswith("/api/ai/categories")
            )
            if not is_target_endpoint:
                return response

            # BaseHTTPMiddleware часто не заполняет response.body, поэтому буферизуем body.
            body = b""
            try:
                if hasattr(response, "body_iterator") and response.body_iterator is not None:
                    async for chunk in response.body_iterator:
                        body += chunk
            except Exception:
                body = getattr(response, "body", b"") or b""

            if (
                b'"source":"sfm_mock"' in body
                or b'"source":"sfm_fallback"' in body
                or b'"source":"sfm_error"' in body
                or b'"result":"mock_fallback"' in body
            ):
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Protection backend temporarily unavailable"},
                )

            # Вернём оригинальный JSON (без изменения), но уже из буфера.
            from starlette.responses import Response as StarletteResponse

            return StarletteResponse(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception:
            # Middleware не должен ломать обычные ответы.
            return response

app.add_middleware(SfmMockTo503Middleware)

# --- PII masking for logs ---
class PIIMaskingFilter(logging.Filter):
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    PHONE_RE = re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}")
    # Very generic hash-like (min length 16 hex) — avoid overmasking shorter ids
    HASH_RE = re.compile(r"\b[0-9a-fA-F]{16,}\b")

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = str(record.getMessage())
            masked = self.EMAIL_RE.sub("[email_masked]", msg)
            masked = self.PHONE_RE.sub("[phone_masked]", masked)
            masked = self.HASH_RE.sub("[hash_masked]", masked)
            # rewrite record message safely
            record.msg = masked
            record.args = ()
        except Exception:
            pass
        return True

# Attach filter to root logger (covers uvicorn/gunicorn app logs as well)
logging.getLogger().addFilter(PIIMaskingFilter())

# Создание таблиц при запуске (если их нет)
@app.on_event("startup")
async def startup_event():
    """Создание таблиц при запуске приложения"""
    Base.metadata.create_all(bind=engine)

# --- Prometheus Freshness Exporter (pull) ---
ENV_NAME = os.getenv("ALADDIN_ENV", "production")
SERVICE_NAME = "gateway"
APP_VERSION = "1.0.0"

FRESHNESS_GAUGE = Gauge(
    "aladdin_analytics_freshness_seconds",
    "Seconds since last event per analytics domain",
    labelnames=("domain", "env", "service", "version"),
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by gateway",
    labelnames=("job", "route", "method", "code", "env", "version"),
)

HTTP_5XX_TOTAL = Counter(
    "http_5xx_total",
    "Total HTTP 5xx responses handled by gateway",
    labelnames=("job", "route", "method", "env", "version"),
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=("job", "route", "method", "code", "env", "version"),
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
)

@app.middleware("http")
async def observe_http_requests(request: Request, call_next):
    start = time.perf_counter()
    route = request.url.path
    method = request.method
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    except Exception:
        status_code = "500"
        raise
    finally:
        duration = max(time.perf_counter() - start, 0.0)
        labels = {
            "job": SERVICE_NAME,
            "route": route,
            "method": method,
            "code": status_code,
            "env": ENV_NAME,
            "version": APP_VERSION,
        }
        HTTP_REQUESTS_TOTAL.labels(**labels).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(**labels).observe(duration)
        if status_code.startswith("5"):
            HTTP_5XX_TOTAL.labels(
                job=SERVICE_NAME,
                route=route,
                method=method,
                env=ENV_NAME,
                version=APP_VERSION,
            ).inc()

def _refresh_freshness_once() -> None:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT domain, EXTRACT(EPOCH FROM (NOW() - last_event_at)) AS age_sec FROM analytics_freshness")
            )
            for row in result:
                domain = str(row[0])
                age_seconds = float(row[1]) if row[1] is not None else 999 * 24 * 3600
                FRESHNESS_GAUGE.labels(
                    domain=domain, env=ENV_NAME, service=SERVICE_NAME, version=APP_VERSION
                ).set(age_seconds)
    except Exception:
        # ignore startup refresh errors
        pass

async def _refresh_freshness_metrics_periodically(poll_interval_seconds: int = 30) -> None:
    """
    Periodically reads analytics_freshness view and updates Prometheus gauge.
    Safe to run even if DB temporarily unavailable.
    """
    while True:
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT domain, EXTRACT(EPOCH FROM (NOW() - last_event_at)) AS age_sec FROM analytics_freshness")
                )
                for row in result:
                    domain = str(row[0])
                    age_seconds = float(row[1]) if row[1] is not None else 999 * 24 * 3600
                    FRESHNESS_GAUGE.labels(
                        domain=domain, env=ENV_NAME, service=SERVICE_NAME, version=APP_VERSION
                    ).set(age_seconds)
        except Exception:
            # swallow, keep loop running
            pass
        await asyncio.sleep(poll_interval_seconds)

@app.on_event("startup")
async def _start_freshness_exporter_task() -> None:
    try:
        _refresh_freshness_once()
        asyncio.create_task(_refresh_freshness_metrics_periodically(30))
    except Exception:
        pass

@app.get("/metrics")
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint."""
    try:
        payload = generate_latest()
        return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
    except Exception:
        return Response(content=b"", media_type=CONTENT_TYPE_LATEST)

# Подключение роутеров
# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен роутер для авторизации
if auth_router_available:
    try:
        app.include_router(auth_router.router, prefix="/api", tags=["auth"])
        print("✅ Роутер авторизации подключен: /api/auth/login доступен")
    except (NameError, AttributeError):
        try:
            app.include_router(auth_router_router, prefix="/api", tags=["auth"])
            print("✅ Роутер авторизации подключен (альтернативный импорт): /api/auth/login доступен")
        except NameError:
            print("⚠️ Не удалось подключить роутер авторизации")
else:
    print("⚠️ Роутер авторизации недоступен")

app.include_router(referral.router, prefix="/api/referral", tags=["referral"])
app.include_router(referral_test.router, tags=["referral-test"])  # Тестовые endpoints
app.include_router(payments.router, tags=["payments"])  # Endpoints для платежей

# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен роутер для компонентов
if components_router_available:
    try:
        app.include_router(components.router, tags=["components"])
        print("✅ Роутер компонентов подключен: /api/components/* доступен")
    except NameError:
        try:
            # Роутер уже имеет prefix="/api/components", поэтому не добавляем дополнительный префикс
            app.include_router(components_router, tags=["components"])
            print("✅ Роутер компонентов подключен (альтернативный импорт): /api/components/* доступен")
        except NameError:
            print("⚠️ Не удалось подключить роутер компонентов")
else:
    print("⚠️ Роутер компонентов недоступен")

# ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлен роутер для Protection API (138 функций)
if protection_router_available:
    try:
        app.include_router(protection.router, tags=["protection"])
        print("✅ Роутер Protection API подключен: /protection/* доступен")
    except NameError:
        try:
            # Роутер уже имеет prefix="/protection", поэтому не добавляем дополнительный префикс
            app.include_router(protection_router, tags=["protection"])
            print("✅ Роутер Protection API подключен (альтернативный импорт): /protection/* доступен")
        except NameError:
            print("⚠️ Не удалось подключить роутер Protection API")
else:
    print("⚠️ Роутер Protection API недоступен")

# ✅ ДОБАВЛЕНО: Добавлен роутер для Family API
if family_router_available:
    try:
        app.include_router(family.router, tags=["family"])
        print("✅ Роутер Family API подключен: /api/family/* доступен")
    except NameError:
        try:
            # Роутер уже имеет prefix="/api/family", поэтому не добавляем дополнительный префикс
            app.include_router(family_router, tags=["family"])
            print("✅ Роутер Family API подключен (альтернативный импорт): /api/family/* доступен")
        except NameError:
            print("⚠️ Не удалось подключить роутер Family API")
else:
    print("⚠️ Роутер Family API недоступен")

# ✅ ДОБАВЛЕНО: Добавлен роутер для User API compat
if user_router_available:
    try:
        app.include_router(user_router_module.router, tags=["user"])
        print("✅ Роутер User API подключен: /api/user/* доступен")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер User API: {e}")
else:
    print("⚠️ Роутер User API недоступен")

# ✅ ДОБАВЛЕНО: Добавлен роутер для System/AI compat
if system_ai_compat_available:
    try:
        app.include_router(system_ai_compat.router, tags=["system-ai-compat"])
        print("✅ Роутер System/AI compat подключен: /api/system/* и /api/ai/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер System/AI compat: {e}")
else:
    print("⚠️ Роутер System/AI compat недоступен")

if network_protection_compat_available:
    try:
        app.include_router(network_protection_compat.router, tags=["network-protection-compat"])
        print("✅ Роутер Network Protection compat подключен: /api/network-protection/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Network Protection compat: {e}")
else:
    print("⚠️ Роутер Network Protection compat недоступен")

if subscription_compat_available:
    try:
        app.include_router(subscription_compat.router, tags=["subscription-compat"])
        print("✅ Роутер Subscription compat подключен: /api/subscription/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Subscription compat: {e}")
else:
    print("⚠️ Роутер Subscription compat недоступен")

if subscription_events_available:
    try:
        app.include_router(subscription_events.router, tags=["subscription-events"])
        print("✅ Роутер Subscription events подключен: /api/subscription/events/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Subscription events: {e}")
else:
    print("⚠️ Роутер Subscription events недоступен")

if notifications_compat_available:
    try:
        app.include_router(notifications_compat.router, tags=["notifications-compat"])
        print("✅ Роутер Notifications compat подключен: /api/notifications/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Notifications compat: {e}")
else:
    print("⚠️ Роутер Notifications compat недоступен")

if crash_detection_compat_available:
    try:
        app.include_router(crash_detection_compat.router, tags=["crash-detection-compat"])
        print("✅ Роутер Crash Detection compat подключен: /api/crash-detection/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Crash Detection compat: {e}")
else:
    print("⚠️ Роутер Crash Detection compat недоступен")

if parental_compat_available:
    try:
        app.include_router(parental_compat.router, tags=["parental-compat"])
        print("✅ Роутер Parental compat подключен: /api/parental/*")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Parental compat: {e}")
else:
    print("⚠️ Роутер Parental compat недоступен")

if misc_other_compat_available:
    try:
        app.include_router(misc_other_compat.router, tags=["misc-other-compat"])
        print("✅ Роутер Misc Other compat подключен")
    except Exception as e:
        print(f"⚠️ Не удалось подключить роутер Misc Other compat: {e}")
else:
    print("⚠️ Роутер Misc Other compat недоступен")

# ✅ ДОБАВЛЕНО: Добавлен роутер для Analytics API
if analytics_router_available:
    try:
        app.include_router(analytics_router.router, tags=["analytics"])
        print("✅ Роутер Analytics API подключен: /api/analytics доступен")
    except NameError:
        try:
            # Роутер уже имеет prefix="/api", поэтому не добавляем дополнительный префикс
            app.include_router(analytics_router_router, tags=["analytics"])
            print("✅ Роутер Analytics API подключен (альтернативный импорт): /api/analytics доступен")
        except NameError:
            print("⚠️ Не удалось подключить роутер Analytics API")
else:
    print("⚠️ Роутер Analytics API недоступен")

# ✅ ВАРИАНТ 5: Добавлен роутер для Reports API (stats endpoints)
try:
    from security.api.routers.reports_router import router as reports_router
    reports_router_available = True
except ImportError as e:
    print(f"⚠️ reports_router недоступен: {e}")
    reports_router_available = False
    reports_router = None

if reports_router_available:
    try:
        app.include_router(reports_router)
        print("✅ Роутер Reports API подключен: /api/reports/*/stats доступны")
    except Exception as e:
        print(f"❌ Ошибка подключения Reports Router: {e}")
else:
    print("⚠️ Роутер Reports API недоступен")

# ✅ ДОБАВЛЕНО: Подключение Security Routers
print(f"📦 Подключение Security Routers (найдено: {len(security_routers)} роутеров)")
for router_name, router in sorted(security_routers.items()):
    try:
        app.include_router(router)
        print(f"✅ Роутер {router_name} подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения {router_name}: {e}")


# ✅ ДОБАВЛЕНО: Подключение Parental Control Router
if parental_control_available:
    try:
        app.include_router(parental_control_router)
        app.include_router(parental_control_legacy_router)
        app.include_router(parental_bypass_router)
        print("✅ Роутеры Parental Control подключены")
    except Exception as e:
        print(f"❌ Ошибка подключения Parental Control: {e}")

# ✅ ДОБАВЛЕНО: Подключение IoT Router
if iot_available:
    try:
        app.include_router(iot_router)
        print("✅ Роутер IoT подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения IoT: {e}")

app.include_router(location_router)
app.include_router(anti_tracker_router)
app.include_router(data_cleanup_router)
app.include_router(identity_router)
app.include_router(dark_web_router)
app.include_router(driving_router)
app.include_router(ai_categories_router)

# ✅ ДОБАВЛЕНО: Подключение Notifications Router
if notifications_available:
    try:
        app.include_router(notifications_router)
        print("✅ Роутер Notifications подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Notifications: {e}")

# ✅ ДОБАВЛЕНО: Подключение AI Assistant Router
if ai_assistant_available:
    try:
        app.include_router(ai_assistant_router)
        print("✅ Роутер AI Assistant подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения AI Assistant: {e}")

# ✅ ЗАДАЧА 21: Подключение Components Router
if components_router_available and components_router is not None:
    try:
        app.include_router(components_router)
        print("✅ Роутер Components подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Components: {e}")
else:
    print("⚠️ Components Router недоступен (components_router is None)")

# ✅ ЗАДАЧА 23: Подключение System Router
if system_router_available:
    try:
        app.include_router(system_router)
        if metrics_router_available:
            app.include_router(metrics_router)
        print("✅ Роутер System подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения System: {e}")

# ✅ ГЕЙМИФИКАЦИЯ: Подключение Gamification Router
if gamification_router_available:
    try:
        app.include_router(gamification_router)
        print("✅ Роутер Gamification подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Gamification: {e}")

# ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Подключение Parental Control Sync Router
if parental_control_sync_router_available:
    try:
        app.include_router(parental_control_sync_router)
        print("✅ Роутер Parental Control Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Parental Control Sync: {e}")

# ✅ ЭТАП 2: Подключение User Profile Sync Router
if user_profile_sync_router_available:
    try:
        app.include_router(user_profile_sync_router)
        print("✅ Роутер User Profile Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения User Profile Sync: {e}")

# ✅ ЭТАП 2: Подключение Subscription Sync Router
if subscription_sync_router_available:
    try:
        app.include_router(subscription_sync_router)
        print("✅ Роутер Subscription Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Subscription Sync: {e}")

# ✅ ЭТАП 2: Подключение основного Subscription Router
if subscription_router_available:
    try:
        app.include_router(subscription_router)
        print("✅ Основной роутер Subscription подключен")
        print(f"✅ Subscription router routes: {[route.path for route in subscription_router.routes]}")
    except Exception as e:
        print(f"❌ Ошибка подключения основного Subscription: {e}")
else:
    print("⚠️ Основной subscription_router недоступен, пропускаем подключение")

# ✅ ЭТАП 2: Подключение App Settings Sync Router
if app_settings_sync_router_available:
    try:
        app.include_router(app_settings_sync_router)
        print("✅ Роутер App Settings Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения App Settings Sync: {e}")

# ✅ ЭТАП 2: Подключение Other Functions Sync Router
if other_functions_sync_router_available:
    try:
        app.include_router(other_functions_sync_router)
        print("✅ Роутер Other Functions Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Other Functions Sync: {e}")

# ✅ ЭТАП 3: Подключение Offline Storage Sync Router
if offline_storage_sync_router_available:
    try:
        app.include_router(offline_storage_sync_router)
        print("✅ Роутер Offline Storage Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Offline Storage Sync: {e}")

# ✅ ЭТАП 3: Подключение Crash Detection Sync Router
if crash_detection_sync_router_available:
    try:
        app.include_router(crash_detection_sync_router)
        print("✅ Роутер Crash Detection Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Crash Detection Sync: {e}")

# ✅ ЭТАП 3: Подключение Elderly Interface Sync Router
if elderly_interface_sync_router_available:
    try:
        app.include_router(elderly_interface_sync_router)
        print("✅ Роутер Elderly Interface Sync подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Elderly Interface Sync: {e}")

# Корневой endpoint
@app.get("/")
async def root():
    return {
        "service": "ALADDIN API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# ✅ ВАРИАНТ 5: ФИНАЛЬНЫЙ СЛОЙ: Wildcard Proxy (Global Safety Net)
# Подключен ПОСЛЕДНИМ - обрабатывает только endpoints без конкретных роутеров
# Импортируем SFM Adapter и маппинг
try:
    import sys
    backend_path = "/opt/aladdin-backend"
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    from sfm_adapter_server import SFMAdapter
    from complete_api_sfm_mapping import get_sfm_function_name
    
    sfm_adapter_wildcard = SFMAdapter()
    SFM_ADAPTER_WILDCARD_AVAILABLE = True
    print("✅ SFM Adapter для Wildcard Proxy инициализирован")
except ImportError as e:
    print(f"⚠️ SFM Adapter для Wildcard Proxy недоступен: {e}")
    sfm_adapter_wildcard = None
    get_sfm_function_name = None
    SFM_ADAPTER_WILDCARD_AVAILABLE = False

def path_to_function_name(path: str, method: str = "GET") -> str:
    """
    Преобразует API путь в имя функции
    
    Примеры:
    - /api/analytics → get_analytics_overview
    - /api/reports/driving/stats → get_driving_reports_stats
    """
    # Убираем query параметры
    path = path.split("?")[0]
    
    # Убираем префикс /api если есть
    if path.startswith("/api/"):
        path = path[5:]
    elif path.startswith("/"):
        path = path[1:]
    
    # Преобразуем путь в имя функции
    parts = path.split("/")
    
    # Определяем префикс по методу
    prefix = {
        "GET": "get_",
        "POST": "create_",
        "PUT": "update_",
        "DELETE": "delete_"
    }.get(method, "get_")
    
    # Собираем имя функции
    func_name = prefix + "_".join(parts)
    
    # Специальные случаи
    if func_name == "get_analytics":
        func_name = "get_analytics_overview"
    
    return func_name

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def wildcard_handler(request: Request, path: str):
    """
    Wildcard Handler для endpoints без конкретных роутеров.
    Преобразует путь в SFM функцию и вызывает её через adapter.
    
    ВАРИАНТ 5: Упрощенная версия - только вызов SFM, без исключений.
    FastAPI автоматически обработает все конкретные роутеры первыми.
    """
    print(f"📡 [WILDCARD] Обработка пути: /api/{path} [{request.method}]")
    
    # 0. Жёсткий guard: запрещаем проксировать мутационные вызовы components через wildcard
    normalized_path = path.split("?")[0]
    if normalized_path.startswith("components/status") and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed for wildcard on components/status mutations",
                "hint": "Use explicit router endpoint for components status updates"
            },
        )

    # Production safety: critical families must never fallback to wildcard -> SFM mock path.
    # Unknown routes should fail explicitly instead of reaching wildcard SFM execution.
    critical_prefixes = ("reports/", "family/", "parental/", "components/")
    if normalized_path.startswith(critical_prefixes):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Critical endpoint not found",
                "path": f"/api/{normalized_path}",
                "method": request.method,
                "hint": "Use explicit router endpoint",
            },
        )

    # 1. Преобразуем путь в имя функции
    func_name = path_to_function_name(path, request.method)
    print(f"🔍 [WILDCARD] Имя функции: {func_name}")
    
    # 2. Извлекаем параметры из запроса
    params = {}
    if request.method in ["POST", "PUT"]:
        try:
            params = await request.json()
        except:
            pass
    
    # 3. Извлекаем query параметры
    query_params = dict(request.query_params)
    params.update(query_params)
    
    # 4. Вызываем SFM через adapter
    if SFM_ADAPTER_WILDCARD_AVAILABLE and sfm_adapter_wildcard:
        try:
            # Получаем правильное имя функции SFM через маппинг (если доступен)
            if get_sfm_function_name:
                sfm_function_name = get_sfm_function_name(func_name)
                print(f"🔄 [WILDCARD] Маппинг: {func_name} → {sfm_function_name}")
            else:
                sfm_function_name = func_name
                print(f"🔄 [WILDCARD] Используем имя функции как есть: {func_name}")
            
            # Вызываем SFM функцию
            success, result, message = sfm_adapter_wildcard.execute_function(sfm_function_name, params)
            
            if success:
                print(f"✅ [WILDCARD] SFM функция выполнена успешно: {sfm_function_name}")
                return JSONResponse(
                    status_code=200,
                    content=result  # ✅ Возвращаем реальные данные!
                )
            else:
                print(f"⚠️ [WILDCARD] SFM функция не выполнена: {message}")
        except Exception as e:
            print(f"❌ [WILDCARD] Ошибка вызова SFM: {e}")
            import traceback
            traceback.print_exc()
    
    # 5. Fallback: возвращаем 404 если SFM недоступен
    return JSONResponse(
        status_code=404,
        content={
            "error": f"Endpoint /api/{path} not found",
            "path": path,
            "method": request.method,
            "message": "No router found and SFM unavailable",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
    )

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
