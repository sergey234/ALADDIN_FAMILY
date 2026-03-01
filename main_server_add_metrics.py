# Добавить импорт metrics_router после anti_tracker_router
try:
    from security.api.routers.anti_tracker_router import router as anti_tracker_router
    ANTI_TRACKER_ROUTER_AVAILABLE = True
    print("✅ Anti Tracker Router loaded")
except ImportError as e:
    print(f"❌ Anti Tracker Router not available: {e}")
    ANTI_TRACKER_ROUTER_AVAILABLE = False

# Добавить импорт metrics_router
try:
    from security.api.routers.metrics_router import router as metrics_router
    METRICS_ROUTER_AVAILABLE = True
    print("✅ Metrics Router loaded")
except ImportError as e:
    print(f"❌ Metrics Router not available: {e}")
    METRICS_ROUTER_AVAILABLE = False

# Добавить подключение metrics_router после anti_tracker_router
if ANTI_TRACKER_ROUTER_AVAILABLE:
    app.include_router(anti_tracker_router)
    print("✅ Anti Tracker Router connected")

if METRICS_ROUTER_AVAILABLE:
    app.include_router(metrics_router)
    print("✅ Metrics Router connected")