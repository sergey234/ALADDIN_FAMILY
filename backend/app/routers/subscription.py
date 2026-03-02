"""
Subscription API Router
Handles all subscription-related endpoints with DB persistence
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.subscription import (
    DeviceRegisterRequest, TrialDeviceRegisterRequest,
    UpgradeRequest, SubscriptionStatusResponse,
    TrialActivationResponse, FeatureAccessRequest,
    FeatureAccessResponse, UsageUpdateRequest,
    JWTDeviceRegisterResponse, TrialInfo, SubscriptionLevel
)
from app.services.subscription_service import SubscriptionService
from app.services.jwt_service import JWTService
from app.database.database import get_db

router = APIRouter(prefix="/api", tags=["subscription"])


def get_token_from_header(authorization: str) -> str:
    """Extract token from Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization[7:]


@router.post("/auth/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device(request: DeviceRegisterRequest, db: Session = Depends(get_db)):
    """Register new device with free subscription in DB"""
    try:
        subscription = SubscriptionService.register_device(db, request)
        token = JWTService.create_subscription_token(subscription)
        jwt_token = JWTService.parse_jwt_token(token)

        return JWTDeviceRegisterResponse(
            token=token,
            device_id=request.device_id,
            expires_at=jwt_token.expires_at if jwt_token else datetime.utcnow(),
            registered_at=datetime.utcnow(),
            subscription=subscription
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/auth/register-device-trial", response_model=JWTDeviceRegisterResponse)
async def register_device_with_trial(request: TrialDeviceRegisterRequest, db: Session = Depends(get_db)):
    """Register device with trial period in DB"""
    try:
        subscription = SubscriptionService.register_device_with_trial(db, request)
        token = JWTService.create_subscription_token(subscription)
        jwt_token = JWTService.parse_jwt_token(token)

        return JWTDeviceRegisterResponse(
            token=token,
            device_id=request.device_id,
            expires_at=jwt_token.expires_at if jwt_token else datetime.utcnow(),
            registered_at=datetime.utcnow(),
            subscription=subscription
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trial registration failed: {str(e)}")


@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """Get current subscription status from DB"""
    try:
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        decoded = JWTService.decode_token(token)
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        subscription = SubscriptionService.get_subscription(db, decoded["device_id"])
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return SubscriptionStatusResponse(
            status=subscription,
            server_time=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")


@router.post("/subscription/validate-receipt")
async def validate_receipt(request: dict, token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """Validate App Store receipt and upgrade subscription in DB"""
    try:
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        decoded = JWTService.decode_token(token)
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid token")

        receipt_data = request.get("receipt_data")
        product_id = request.get("product_id")

        if not receipt_data or not product_id:
            raise HTTPException(status_code=400, detail="Missing receipt_data or product_id")

        # Validate receipt with Apple
        from app.services.receipt_validation_service import ReceiptValidationService
        is_valid, receipt_info = await ReceiptValidationService.validate_receipt(receipt_data, is_sandbox=False)

        if not is_valid:
            error_message = receipt_info.get("message", "Receipt validation failed")
            raise HTTPException(status_code=400, detail=f"Receipt validation failed: {error_message}")

        # Map product ID to subscription level
        level_mapping = {
            "family.aladdin.ios.subscription.individual.v2": SubscriptionLevel.PERSONAL,
            "family.aladdin.ios.subscription.family": SubscriptionLevel.FAMILY,
            "family.aladdin.ios.subscription.premium": SubscriptionLevel.PREMIUM
        }

        new_level = level_mapping.get(product_id)
        if not new_level:
            raise HTTPException(status_code=400, detail="Unknown product ID")

        # Upgrade subscription in DB
        upgraded_subscription = SubscriptionService.upgrade_subscription(db, decoded["device_id"], new_level)

        if not upgraded_subscription:
            raise HTTPException(status_code=500, detail="Upgrade failed")

        new_token = JWTService.create_subscription_token(upgraded_subscription)

        return {
            "is_valid": True,
            "subscription_level": new_level.value,
            "transaction_id": receipt_info.get("transaction_id"),
            "new_token": new_token,
            "subscription": upgraded_subscription,
            "message": f"Successfully validated receipt and upgraded to {new_level.value}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt validation failed: {str(e)}")


@router.post("/subscription/cancel")
async def cancel_subscription(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
    """Cancel subscription in DB"""
    try:
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        decoded = JWTService.decode_token(token)
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid token")

        success = SubscriptionService.cancel_subscription(db, decoded["device_id"])
        if not success:
            raise HTTPException(status_code=500, detail="Cancellation failed")

        updated_subscription = SubscriptionService.get_subscription(db, decoded["device_id"])
        new_token = JWTService.create_subscription_token(updated_subscription)

        return {
            "success": True,
            "new_token": new_token,
            "subscription": updated_subscription,
            "message": "Subscription cancelled"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")
