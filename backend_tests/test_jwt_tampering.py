import unittest
import jwt
import requests
import json
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = "aladdin-jwt-secret-key-2026-production-ready"
BASE_URL = "http://localhost:8000"

class TestJWTSecurity(unittest.TestCase):
    def test_tampered_subscription(self):
        print("\n🛡️ Testing JWT Tampering Protection...")
        
        # 1. Create a valid token with subscription data and signature
        # We need to simulate how the server signs it
        import hmac
        import hashlib
        
        sub_data = {"level": "premium", "status": "active"}
        payload_str = json.dumps(sub_data, sort_keys=True)
        signature = hmac.new(
            SECRET_KEY.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token_payload = {
            "user_id": "test_user_123",
            "subscription": sub_data,
            "signature": signature,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        valid_token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        
        # 2. Verify it works
        headers = {"Authorization": f"Bearer {valid_token}"}
        # Use an endpoint that requires auth
        response = requests.post(
            f"{BASE_URL}/api/subscription/sync", 
            headers=headers,
            json={"userId": "test_user_123", "deviceId": "test_device"}
        )
        print(f"Valid token status: {response.status_code}")
        
        # 3. Create a TAMPERED token (change level but keep old signature)
        tampered_sub = {"level": "premium_unlocked", "status": "active"}
        tampered_payload = token_payload.copy()
        tampered_payload["subscription"] = tampered_sub
        
        tampered_token = jwt.encode(tampered_payload, SECRET_KEY, algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = requests.post(
            f"{BASE_URL}/api/subscription/sync", 
            headers=headers,
            json={"userId": "test_user_123", "deviceId": "test_device"}
        )
        print(f"Tampered token status: {response.status_code}")
        
        self.assertEqual(response.status_code, 401)
        print("✅ Tampering detected and blocked!")

if __name__ == "__main__":
    unittest.main()
