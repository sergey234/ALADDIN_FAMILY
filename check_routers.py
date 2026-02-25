#!/usr/bin/env python3
print("Checking router imports...")

try:
    from security.api.routers.ai_categories_router import router as ai_router
    print("ai_categories_router: LOADED")
except Exception as e:
    print(f"ai_categories_router: ERROR - {str(e)[:50]}")

try:
    from security.api.routers.parental_control_router import router as parental_router
    print("parental_control_router: LOADED")
except Exception as e:
    print(f"parental_control_router: ERROR - {str(e)[:50]}")

try:
    from app.routers.referral_fixed import router as referral_router
    print("referral_fixed: LOADED")
except Exception as e:
    print(f"referral_fixed: ERROR - {str(e)[:50]}")

try:
    from security.api.routers.crash_detection_router import router as crash_router
    print("crash_detection_router: LOADED")
except Exception as e:
    print(f"crash_detection_router: ERROR - {str(e)[:50]}")

print("Check completed")
