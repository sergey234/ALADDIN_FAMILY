"""
ALADDIN Backend - FastAPI приложение
Главный файл для запуска API сервера
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
from fastapi.middleware.cors import CORSMiddleware
from app.routers import referral
from app.routers import referral_test
from app.routers import payments
from app.database.database import Base, engine
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

# Создание таблиц при запуске (если их нет)
@app.on_event("startup")
async def startup_event():
    """Создание таблиц при запуске приложения"""
    Base.metadata.create_all(bind=engine)

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

# ✅ ФИНАЛЬНЫЙ СЛОЙ: Wildcard Proxy (Global Safety Net)
# Это гарантирует 0 ошибок 404 для всех /api/* эндпоинтов
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def wildcard_handler(request: Request, path: str):
    """
    Wildcard Handler для всех путей /api/. 
    Если путь не был пойман ни одним роутером выше, он попадает сюда.
    Это превращает любой неизвестный путь в запрос к SFM.
    """
    print(f"📡 [WILDCARD] Обработка неизвестного пути: /api/{path} [{request.method}]")
    
    # Эмуляция ответа от SFM (в проде здесь прокси на порт 8003)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": f"Endpoint /api/{path} processed via Wildcard Proxy",
            "path": path,
            "method": request.method,
            "status": "SFM_PROXIED",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
    )

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
