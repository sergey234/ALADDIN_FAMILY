from pathlib import Path

# SSOT: main.py подключает `security.api.routers.parental_control_router` из дерева security/.
# Патчить нужно канонический файл на сервере; путь app/security/... — legacy и не должен быть целью деплоя.
_canonical = Path('/opt/aladdin-backend/security/api/routers/parental_control_router.py')
_legacy_wrong = Path('/opt/aladdin-backend/app/security/api/routers/parental_control_router.py')
router_path = _canonical if _canonical.is_file() else _legacy_wrong
main_path = Path('/opt/aladdin-backend/main.py')

text = router_path.read_text(encoding='utf-8')

if 'class BypassApplyRequest(BaseModel):' not in text:
    anchor = 'class BypassStatsResponse(BaseModel):\n'
    insert = '''class BypassApplyRequest(BaseModel):
    childId: Optional[str] = None
    incognito: bool = Field(default=True)
    tor: bool = Field(default=True)
    proxy: bool = Field(default=True)


class APIBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None


'''
    text = text.replace(anchor, insert + anchor, 1)

if '@bypass_router.post("/bypass/apply", response_model=APIBoolResponse)' not in text:
    endpoint = '''

@bypass_router.post("/bypass/apply", response_model=APIBoolResponse)
async def apply_bypass_protection(
    payload: BypassApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Применить настройки bypass без wildcard/SFM mock fallback."""
    try:
        user_id = str(current_user["id"])
        child_id = _resolve_child_id(payload.childId)
        await _ensure_protection_session(child_id)

        current = get_bypass_stats_from_db(db, user_id, child_id)
        updated = {
            "today": int(current.get("today", 0)),
            "week": int(current.get("week", 0)),
            "blocked": int(current.get("blocked", 0)),
            "incognito": int(current.get("incognito", 0)),
            "tor": int(current.get("tor", 0)),
            "proxy": int(current.get("proxy", 0)),
            "message": "Защита обновлена."
        }

        if payload.incognito:
            updated["incognito"] = max(updated["incognito"], 1)
        if payload.tor:
            updated["tor"] = max(updated["tor"], 1)
        if payload.proxy:
            updated["proxy"] = max(updated["proxy"], 1)

        ok = upsert_bypass_stats_to_db(db, user_id, child_id, updated)
        if not ok:
            return APIBoolResponse(success=False, data=False, message="Не удалось сохранить настройки обхода")

        return APIBoolResponse(success=True, data=True, message="Bypass protection applied")
    except Exception as e:
        logger.error(f"❌ Error applying bypass protection: {str(e)}")
        return APIBoolResponse(success=False, data=False, message=f"Ошибка применения защиты от обхода: {str(e)}")
'''
    text = text.replace('\n\n@router.get("/status")\n', endpoint + '\n\n@router.get("/status")\n', 1)

router_path.write_text(text, encoding='utf-8')

main = main_path.read_text(encoding='utf-8')
if 'request_path.startswith("/api/parental/")' not in main:
    main = main.replace(
        '                or request_path.startswith("/api/components/")\n',
        '                or request_path.startswith("/api/components/")\n                or request_path.startswith("/api/parental/")\n',
        1,
    )

if 'parental/bypass mutations' not in main:
    block = '''    if normalized_path.startswith("components/status") and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed for wildcard on components/status mutations",
                "hint": "Use explicit router endpoint for components status updates"
            },
        )

'''
    replace = block + '''    # Production safety: parental bypass apply must use explicit router, never wildcard->SFM fallback/mock
    if normalized_path.startswith("parental/bypass/") and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed for wildcard on parental/bypass mutations",
                "hint": "Use explicit parental bypass router endpoint"
            },
        )

'''
    main = main.replace(block, replace, 1)

main_path.write_text(main, encoding='utf-8')
print('OK: backend files patched')
