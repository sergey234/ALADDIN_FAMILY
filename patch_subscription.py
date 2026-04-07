import re

# 1. Patch subscription_service.py
sub_path = '/opt/aladdin-backend/app/services/subscription_service.py'
with open(sub_path, 'r') as f:
    sub_code = f.read()

sub_code = sub_code.replace(
    'async def get_subscription_level(request: Request, device_id: Optional[str] = None) -> str:',
    'async def get_subscription_level(request: Request, device_id: Optional[str] = None, current_user: Optional[dict] = None) -> str:'
)

sub_logic_old = """    # Fallback to JWT
    try:
        # In this backend `get_current_user` puts user info either in depends or request state.
        # But we'll just check if it's passed or try to decode it, for now fallback to "free"
        level = "free"
        if hasattr(request.state, "user") and isinstance(request.state.user, dict):
            level = request.state.user.get("subscription_level", "free")
            log_tariff_source_used(source="jwt", warn=True)
        else:
            # Maybe it's in headers for simple fallback
            pass
        if device_id:
            _write_cache(device_id, level)
        return level
    except Exception:
        pass"""

sub_logic_new = """    # Fallback to JWT
    try:
        level = "free"
        if current_user and isinstance(current_user, dict) and "subscription_level" in current_user:
            level = current_user.get("subscription_level", "free")
            log_tariff_source_used(source="jwt", warn=True)
        elif hasattr(request.state, "user") and isinstance(request.state.user, dict):
            level = request.state.user.get("subscription_level", "free")
            log_tariff_source_used(source="jwt", warn=True)
        
        if device_id:
            _write_cache(device_id, level)
        return level
    except Exception:
        pass"""

sub_code = sub_code.replace(sub_logic_old, sub_logic_new)

with open(sub_path, 'w') as f:
    f.write(sub_code)


# 2. Patch family.py
fam_path = '/opt/aladdin-backend/app/routers/family.py'
with open(fam_path, 'r') as f:
    fam_code = f.read()

fam_code = fam_code.replace(
    'tariff_level = await get_subscription_level(request, device_id=request.headers.get("X-Device-Id"))',
    'tariff_level = await get_subscription_level(request, device_id=request.headers.get("X-Device-Id"), current_user=current_user)'
)

with open(fam_path, 'w') as f:
    f.write(fam_code)

print("Patch applied to subscription_service.py and family.py")
