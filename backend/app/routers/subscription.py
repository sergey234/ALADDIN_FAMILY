"""
Subscription API Router
Handles all subscription-related endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.subscription import (
    DeviceRegisterRequest, TrialDeviceRegisterRequest,
    UpgradeRequest, SubscriptionStatusResponse,
    TrialActivationResponse, FeatureAccessRequest,
    FeatureAccessResponse, UsageUpdateRequest,
    JWTDeviceRegisterResponse, TrialInfo
)
from app.services.subscription_service import SubscriptionService
from app.services.jwt_service import JWTService

router = APIRouter(prefix="/api", tags=["subscription"])


def get_token_from_header(authorization: str) -> str:
    """Extract token from Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization[7:]


@router.post("/auth/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device(request: DeviceRegisterRequest):
    """Register new device with free subscription"""
    try:
        # Register device
        subscription = SubscriptionService.register_device(request)

        # Create JWT token
        token = JWTService.create_subscription_token(subscription)

        # Parse token back to get full JWT data
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
async def register_device_with_trial(request: TrialDeviceRegisterRequest):
    """Register device with trial period"""
    try:
        # Register device with trial
        subscription = SubscriptionService.register_device_with_trial(request)

        # Create JWT token
        token = JWTService.create_subscription_token(subscription)

        # Parse token back to get full JWT data
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
async def get_subscription_status(token: str = Depends(get_token_from_header)):
    """Get current subscription status"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get subscription from token
        subscription = JWTService.get_subscription_from_token(token)
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


@router.post("/subscription/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    token: str = Depends(get_token_from_header)
):
    """Upgrade subscription to higher level"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Upgrade subscription
        upgraded_subscription = SubscriptionService.upgrade_subscription(
            current_subscription.device_id,
            request.level
        )

        if not upgraded_subscription:
            raise HTTPException(status_code=500, detail="Upgrade failed")

        # Create new JWT token
        new_token = JWTService.create_subscription_token(upgraded_subscription)

        return {
            "success": True,
            "new_token": new_token,
            "subscription": upgraded_subscription,
            "message": f"Successfully upgraded to {request.level.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upgrade failed: {str(e)}")


@router.post("/subscription/validate-receipt")
async def validate_receipt(request: dict, token: str = Depends(get_token_from_header)):
    """Validate App Store receipt and upgrade subscription"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        receipt_data = request.get("receipt_data")
        product_id = request.get("product_id")
        subscription_level = request.get("subscription_level")

        if not receipt_data or not product_id:
            raise HTTPException(status_code=400, detail="Missing receipt_data or product_id")

        # Validate receipt with Apple
        from app.services.receipt_validation_service import ReceiptValidationService

        is_valid, receipt_info = await ReceiptValidationService.validate_receipt(
            receipt_data, is_sandbox=False  # TODO: Detect sandbox vs production
        )

        if not is_valid:
            error_info = receipt_info.get("error", "unknown_error")
            error_message = receipt_info.get("message", "Receipt validation failed")
            raise HTTPException(
                status_code=400,
                detail=f"Receipt validation failed: {error_message}"
            )

        # Validate product ID
        valid_product_ids = [
            "family.aladdin.ios.subscription.individual.v2",
            "family.aladdin.ios.subscription.family",
            "family.aladdin.ios.subscription.premium"
        ]

        if not ReceiptValidationService.validate_product_id(receipt_info, valid_product_ids):
            raise HTTPException(status_code=400, detail="Invalid product ID in receipt")

        # Check subscription status
        subscription_status = ReceiptValidationService.check_subscription_status(receipt_info)
        if subscription_status not in ["active", "trial"]:
            raise HTTPException(
                status_code=400,
                detail=f"Subscription is {subscription_status}, cannot upgrade"
            )

        # Map product ID to subscription level
        level_mapping = {
            "family.aladdin.ios.subscription.individual.v2": "personal",
            "family.aladdin.ios.subscription.family": "family",
            "family.aladdin.ios.subscription.premium": "premium"
        }

        new_level = level_mapping.get(product_id)
        if not new_level:
            raise HTTPException(status_code=400, detail="Unknown product ID")

        # Upgrade subscription
        from app.models.subscription import SubscriptionLevel
        upgraded_subscription = SubscriptionService.upgrade_subscription(
            current_subscription.device_id,
            SubscriptionLevel(new_level)
        )

        if not upgraded_subscription:
            raise HTTPException(status_code=500, detail="Upgrade failed")

        # Create new JWT token
        new_token = JWTService.create_subscription_token(upgraded_subscription)

        return {
            "is_valid": True,
            "subscription_level": new_level,
            "transaction_id": receipt_info.get("transaction_id"),
            "new_token": new_token,
            "subscription": upgraded_subscription,
            "message": f"Successfully validated receipt and upgraded to {new_level}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt validation failed: {str(e)}")


@router.post("/subscription/cancel")
async def cancel_subscription(token: str = Depends(get_token_from_header)):
    """Cancel subscription (downgrade to free)"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Cancel subscription
        success = SubscriptionService.cancel_subscription(current_subscription.device_id)

        if not success:
            raise HTTPException(status_code=500, detail="Cancellation failed")

        # Get updated subscription
        updated_subscription = SubscriptionService.get_subscription(current_subscription.device_id)
        if not updated_subscription:
            raise HTTPException(status_code=500, detail="Failed to get updated subscription")

        # Create new JWT token
        new_token = JWTService.create_subscription_token(updated_subscription)

        return {
            "success": True,
            "new_token": new_token,
            "subscription": updated_subscription,
            "message": "Subscription cancelled, downgraded to free"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")


@router.post("/features/check", response_model=FeatureAccessResponse)
async def check_feature_access(
    request: FeatureAccessRequest,
    token: str = Depends(get_token_from_header)
):
    """Check if device can access specific feature"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check feature access
        access_result = SubscriptionService.check_feature_access(
            request.device_id,
            request.feature_id
        )

        return FeatureAccessResponse(
            feature_id=request.feature_id,
            accessible=access_result["accessible"],
            reason=access_result["reason"],
            subscription_level=access_result["subscription_level"],
            limits=access_result.get("limits")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature check failed: {str(e)}")


@router.post("/usage/track")
async def track_usage(
    request: UsageUpdateRequest,
    token: str = Depends(get_token_from_header)
):
    """Track resource usage"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Track usage
        success = SubscriptionService.track_usage(
            current_subscription.device_id,
            request.resource_type,
            request.amount
        )

        if not success:
            raise HTTPException(
                status_code=429,
                detail=f"Usage limit exceeded for {request.resource_type}"
            )

        return {
            "success": True,
            "resource_type": request.resource_type,
            "amount": request.amount,
            "message": f"Usage tracked: {request.amount} {request.resource_type}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage tracking failed: {str(e)}")


@router.get("/trial/status")
async def get_trial_status(token: str = Depends(get_token_from_header)):
    """Get trial status for device"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Get trial status
        trial_status = SubscriptionService.get_trial_status(current_subscription.device_id)

        if not trial_status:
            return {
                "has_trial": False,
                "message": "No active trial"
            }

        return {
            "has_trial": True,
            "trial_status": trial_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trial status: {str(e)}")


@router.post("/usage/reset")
async def reset_monthly_usage(token: str = Depends(get_token_from_header)):
    """Reset monthly usage counters (admin function)"""
    try:
        # Validate token
        if not JWTService.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get current subscription
        current_subscription = JWTService.get_subscription_from_token(token)
        if not current_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Reset usage
        success = SubscriptionService.reset_monthly_usage(current_subscription.device_id)

        if not success:
            raise HTTPException(status_code=500, detail="Usage reset failed")

        return {
            "success": True,
            "message": "Monthly usage counters reset"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage reset failed: {str(e)}")