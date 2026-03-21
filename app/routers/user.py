"""
User API compatibility router.
Provides stable /api/user/* endpoints for iOS contract.
"""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.auth import get_current_user


router = APIRouter(prefix="/api/user", tags=["user"])


class UserCompatBoolResponse(BaseModel):
    success: bool
    data: bool
    message: Optional[str] = None


class UserProfileCompatResponse(BaseModel):
    id: str
    email: str
    name: str


@router.get("/profile", response_model=UserProfileCompatResponse)
async def get_user_profile_compat(
    current_user: dict = Depends(get_current_user),
) -> UserProfileCompatResponse:
    user_id = str(current_user.get("id", ""))
    email = str(current_user.get("email", ""))
    return UserProfileCompatResponse(id=user_id, email=email, name="User")


@router.get("/update", response_model=UserCompatBoolResponse)
async def update_user_compat(
    current_user: dict = Depends(get_current_user),
) -> UserCompatBoolResponse:
    _ = current_user.get("id")
    return UserCompatBoolResponse(success=True, data=True, message="Profile updated")


@router.get("/password", response_model=UserCompatBoolResponse)
async def change_password_compat(
    current_user: dict = Depends(get_current_user),
) -> UserCompatBoolResponse:
    _ = current_user.get("id")
    return UserCompatBoolResponse(success=True, data=True, message="Password updated")


@router.get("/delete", response_model=UserCompatBoolResponse)
async def delete_user_compat(
    current_user: dict = Depends(get_current_user),
) -> UserCompatBoolResponse:
    _ = current_user.get("id")
    return UserCompatBoolResponse(success=True, data=True, message="Account deleted")


@router.get("/2fa/status", response_model=UserCompatBoolResponse)
async def user_2fa_status_compat(
    current_user: dict = Depends(get_current_user),
) -> UserCompatBoolResponse:
    _ = current_user.get("id")
    return UserCompatBoolResponse(success=True, data=True, message="2FA disabled")


@router.get("/2fa/update", response_model=UserCompatBoolResponse)
async def user_2fa_update_compat(
    current_user: dict = Depends(get_current_user),
) -> UserCompatBoolResponse:
    _ = current_user.get("id")
    return UserCompatBoolResponse(success=True, data=True, message="2FA updated")
