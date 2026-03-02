import hmac
import hashlib
import json
from typing import Dict, Any

# JWT Configuration (matching api_gateway_complete_full.py)
SECRET_KEY = "aladdin-jwt-secret-key-2026-production-ready"

def sign_payload(payload: Dict[str, Any]) -> str:
    """
    Create an HMAC-SHA256 signature for a dictionary payload.
    Used to prevent tampering with subscription data.
    """
    # Sort keys to ensure consistent signature
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_payload_signature(payload: Dict[str, Any], signature: str) -> bool:
    """
    Verify that the signature matches the payload.
    """
    if not signature:
        return False
    
    expected_signature = sign_payload(payload)
    return hmac.compare_digest(expected_signature, signature)
