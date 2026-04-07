import re

with open('server_auth_router.py', 'r') as f:
    content = f.read()

new_route = """

@router.post("/auth/register-device-trial", response_model=LoginResponse)
async def register_device_trial(request: TrialDeviceRegisterRequest):
    \"\"\"
    Anonymous device registration endpoint with trial activation.
    \"\"\"
    try:
        if not request.device_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="device_id is required",
            )

        pseudo_user_id = int(hashlib.sha256(request.device_id.encode()).hexdigest()[:8], 16) % 2147483647
        token_data = {
            "user_id": pseudo_user_id,
            "id": pseudo_user_id,
            "sub": str(pseudo_user_id),
            "device_id": request.device_id,
            "device_type": request.device_type,
            "type": "device_auth",
            "subscription_level": "trial"  # Inject trial level
        }
        
        # Merge trial info if provided
        if request.trial_info:
            token_data["trial_info"] = request.trial_info

        access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(token_data)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=86400,
            token_type="Bearer",
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
"""

# Insert right after register_device
pattern = r'(@router\.post\("/auth/register-device", response_model=LoginResponse\).*?token_type="Bearer",\n        \)\n    except HTTPException:\n        raise\n    except Exception as e:\n        print\(f"Отройства: \{e\}"\)\n        raise HTTPException\(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=f"Внутренняя ошибка сервера: \{str\(e\)\}"\n        \))'

def replacement(match):
    return match.group(1) + new_route

modified = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('server_auth_router.py', 'w') as f:
    f.write(modified)

print("Patched locally.")
