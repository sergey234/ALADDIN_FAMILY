"""
Receipt Validation Service for ALADDIN Backend
Validates App Store receipts to prevent purchase fraud
"""

import httpx
import json
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReceiptValidationService:
    """Service for validating App Store receipts"""

    # Apple receipt validation URLs
    SANDBOX_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
    PRODUCTION_URL = "https://buy.itunes.apple.com/verifyReceipt"

    # Shared secret for auto-renewable subscriptions (get from App Store Connect)
    SHARED_SECRET = "your_app_store_shared_secret_here"  # TODO: Move to config

    @classmethod
    async def validate_receipt(
        cls,
        receipt_data: str,
        is_sandbox: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate App Store receipt

        Args:
            receipt_data: Base64 encoded receipt data
            is_sandbox: Whether to use sandbox environment

        Returns:
            Tuple of (is_valid, validation_response)
        """
        try:
            # Prepare validation request
            validation_url = cls.SANDBOX_URL if is_sandbox else cls.PRODUCTION_URL

            request_data = {
                "receipt-data": receipt_data,
                "password": cls.SHARED_SECRET,
                "exclude-old-transactions": True
            }

            logger.info(f"Validating receipt with Apple ({'sandbox' if is_sandbox else 'production'})")

            # Send validation request to Apple
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    validation_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    logger.error(f"Apple validation API error: {response.status_code}")
                    return False, {"error": f"API error: {response.status_code}"}

                validation_result = response.json()
                status = validation_result.get("status", -1)

                # Check validation status
                if status == 0:
                    # Receipt is valid
                    receipt_info = validation_result.get("receipt", {})
                    logger.info("Receipt validation successful")
                    return True, cls._extract_receipt_info(receipt_info)

                elif status == 21000:
                    logger.warning("Receipt validation failed: Bad request")
                    return False, {"error": "bad_request", "message": "The receipt is malformed"}

                elif status == 21002:
                    logger.warning("Receipt validation failed: Bad receipt data")
                    return False, {"error": "bad_data", "message": "The receipt data is malformed"}

                elif status == 21003:
                    logger.warning("Receipt validation failed: Receipt could not be authenticated")
                    return False, {"error": "not_authenticated", "message": "Receipt authentication failed"}

                elif status == 21004:
                    logger.warning("Receipt validation failed: Shared secret does not match")
                    return False, {"error": "shared_secret_mismatch", "message": "Invalid shared secret"}

                elif status == 21005:
                    logger.warning("Receipt validation failed: Receipt server unavailable")
                    return False, {"error": "server_unavailable", "message": "Apple servers temporarily unavailable"}

                elif status == 21007:
                    # Receipt is from sandbox but sent to production - retry with sandbox
                    if not is_sandbox:
                        logger.info("Receipt is from sandbox, retrying with sandbox URL")
                        return await cls.validate_receipt(receipt_data, is_sandbox=True)
                    else:
                        return False, {"error": "sandbox_receipt_in_production", "message": "Sandbox receipt sent to production"}

                elif status == 21008:
                    # Receipt is from production but sent to sandbox - retry with production
                    if is_sandbox:
                        logger.info("Receipt is from production, retrying with production URL")
                        return await cls.validate_receipt(receipt_data, is_sandbox=False)
                    else:
                        return False, {"error": "production_receipt_in_sandbox", "message": "Production receipt sent to sandbox"}

                else:
                    logger.error(f"Unknown receipt validation status: {status}")
                    return False, {"error": "unknown_status", "status": status}

        except httpx.TimeoutException:
            logger.error("Receipt validation timeout")
            return False, {"error": "timeout", "message": "Apple validation timeout"}

        except Exception as e:
            logger.error(f"Receipt validation error: {str(e)}")
            return False, {"error": "validation_error", "message": str(e)}

    @classmethod
    def _extract_receipt_info(cls, receipt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract important information from validated receipt

        Args:
            receipt: Apple receipt data

        Returns:
            Extracted receipt information
        """
        try:
            # Get the latest transaction (most recent purchase)
            in_app = receipt.get("in_app", [])
            if not in_app:
                return {"error": "no_transactions", "message": "No in-app purchases found"}

            # Sort by purchase date (newest first)
            latest_transaction = max(
                in_app,
                key=lambda x: int(x.get("purchase_date_ms", 0))
            )

            # Extract key information
            receipt_info = {
                "transaction_id": latest_transaction.get("transaction_id"),
                "product_id": latest_transaction.get("product_id"),
                "purchase_date": cls._convert_ms_to_datetime(
                    latest_transaction.get("purchase_date_ms")
                ),
                "original_purchase_date": cls._convert_ms_to_datetime(
                    latest_transaction.get("original_purchase_date_ms")
                ),
                "expires_date": cls._convert_ms_to_datetime(
                    latest_transaction.get("expires_date_ms")
                ),
                "is_trial": latest_transaction.get("is_trial_period", "false") == "true",
                "is_intro_offer": latest_transaction.get("is_in_intro_offer_period", "false") == "true",
                "cancellation_date": cls._convert_ms_to_datetime(
                    latest_transaction.get("cancellation_date_ms")
                ),
                "bundle_id": receipt.get("bundle_id"),
                "application_version": receipt.get("application_version"),
                "environment": receipt.get("environment", "Production")
            }

            logger.info(f"Extracted receipt info for product: {receipt_info['product_id']}")
            return receipt_info

        except Exception as e:
            logger.error(f"Error extracting receipt info: {str(e)}")
            return {"error": "extraction_error", "message": str(e)}

    @staticmethod
    def _convert_ms_to_datetime(ms_timestamp: Optional[str]) -> Optional[datetime]:
        """Convert milliseconds timestamp to datetime"""
        if not ms_timestamp:
            return None
        try:
            return datetime.fromtimestamp(int(ms_timestamp) / 1000)
        except (ValueError, TypeError):
            return None

    @classmethod
    def validate_product_id(cls, receipt_info: Dict[str, Any], expected_product_ids: list) -> bool:
        """
        Validate that the receipt is for one of the expected products

        Args:
            receipt_info: Extracted receipt information
            expected_product_ids: List of valid product IDs

        Returns:
            True if product ID is valid
        """
        product_id = receipt_info.get("product_id")
        if not product_id:
            logger.warning("No product_id in receipt")
            return False

        if product_id not in expected_product_ids:
            logger.warning(f"Invalid product_id: {product_id}, expected: {expected_product_ids}")
            return False

        return True

    @classmethod
    def check_subscription_status(cls, receipt_info: Dict[str, Any]) -> str:
        """
        Check the status of the subscription from receipt

        Args:
            receipt_info: Extracted receipt information

        Returns:
            Status: 'active', 'expired', 'cancelled', 'trial'
        """
        # Check if cancelled
        if receipt_info.get("cancellation_date"):
            return "cancelled"

        # Check if expired
        expires_date = receipt_info.get("expires_date")
        if expires_date and isinstance(expires_date, datetime):
            if datetime.utcnow() > expires_date:
                return "expired"

        # Check if trial
        if receipt_info.get("is_trial", False):
            return "trial"

        return "active"