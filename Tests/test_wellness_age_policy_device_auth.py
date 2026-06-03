"""Age band resolution for device-auth wellness smoke (r100-0-02)."""
from security.services.ai_platform.jwt_claims import merge_get_current_user
from security.services.ai_platform.wellness_age_policy import resolve_wellness_age_band


def test_device_auth_smoke_gets_child_band():
    """Raw device_auth before sign."""
    user = merge_get_current_user(
        {"user_id": 1, "sub": "1", "device_id": "smoke", "type": "device_auth"}
    )
    assert resolve_wellness_age_band(user) == "child"


def test_register_device_jwt_shape_after_sign():
    """create_access_token overwrites type→access; device_id + age_band child must stay child."""
    user = merge_get_current_user(
        {
            "user_id": 1,
            "sub": "1",
            "device_id": "smoke",
            "type": "access",
            "age_band": "child",
        }
    )
    assert resolve_wellness_age_band(user) == "child"


def test_stale_child_claim_without_device_id_becomes_parent():
    user = {
        "age_band": "child",
        "type": "access",
        "payload": {"type": "access", "age_band": "child"},
    }
    assert resolve_wellness_age_band(user) == "parent"
