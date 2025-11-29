# Регистрация IoT Security Router
try:
    from security.api.routers.iot_router import router as iot_router
    app.include_router(iot_router)
    logger.info("✅ IoT Security Router зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ Не удалось зарегистрировать IoT Router: {e}")

# Регистрация Parental Control Router
try:
    from security.api.routers.parental_control_router import (
        router as parental_control_router,
        bypass_router as parental_bypass_router,
    )
    app.include_router(parental_control_router)
    app.include_router(parental_bypass_router)
    logger.info("✅ Parental Control Router зарегистрирован")
except Exception as e:
    logger.warning(f"⚠️ Не удалось зарегистрировать Parental Control Router: {e}")
