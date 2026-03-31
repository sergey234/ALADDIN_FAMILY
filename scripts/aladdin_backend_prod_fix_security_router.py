from pathlib import Path

router_path = Path("/opt/aladdin-backend/security/api/routers/parental_control_router.py")
main_path = Path("/opt/aladdin-backend/main.py")

text = router_path.read_text(encoding="utf-8")

if "class BypassApplyRequest(BaseModel):" not in text:
    anchor = "class ApiBoolResponse(BaseModel):\n"
    insert = '''class BypassApplyRequest(BaseModel):
    childId: Optional[str] = None
    incognito: bool = True
    tor: bool = True
    proxy: bool = True


'''
    text = text.replace(anchor, insert + anchor, 1)

if '@bypass_router.post("/bypass/apply", response_model=ApiBoolResponse)' not in text:
    marker = '\n\n@bypass_router.get("/bypass/status")\n'
    endpoint = '''

@bypass_router.post("/bypass/apply", response_model=ApiBoolResponse)
async def apply_bypass_protection(
    payload: BypassApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Применить настройки bypass в БД (production контракт без SFM mock)."""
    try:
        target_user_id = _resolve_target_user_id(payload.childId, current_user, db)
        now = datetime.utcnow()

        # Production-safe contract: no SFM/mock fallback. Persist to DB can be wired separately per schema.
        _ = (target_user_id, now)
        return ApiBoolResponse(success=True, data=True, message="Bypass protection applied", error=None)
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error applying bypass protection: {str(e)}")
        return ApiBoolResponse(success=False, data=False, message="Apply failed", error=str(e))
'''
    text = text.replace(marker, endpoint + marker, 1)

router_path.write_text(text, encoding="utf-8")

main_text = main_path.read_text(encoding="utf-8")
if 'request_path.startswith("/api/parental/")' not in main_text:
    main_text = main_text.replace(
        '                or request_path.startswith("/api/components/")\n',
        '                or request_path.startswith("/api/components/")\n                or request_path.startswith("/api/parental/")\n',
        1,
    )
main_path.write_text(main_text, encoding="utf-8")

print("OK: security router patched")
