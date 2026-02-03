#!/usr/bin/env python3
"""
TEST SINGLE API ENDPOINT WITH REAL SFM
Тестируем один эндпоинт с реальной SFM интеграцией
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Import SFM components
try:
    from complete_api_sfm_mapping import get_sfm_function_name, API_TO_SFM_MAPPING
    SFM_MAPPING_AVAILABLE = True
    print(f"SFM mapping loaded: {len(API_TO_SFM_MAPPING)} functions")
except ImportError as e:
    SFM_MAPPING_AVAILABLE = False
    print(f"SFM mapping not available: {e}")
    API_TO_SFM_MAPPING = {}
    def get_sfm_function_name(name):
        return name

# Import SFM adapter
try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
    print("SFM adapter loaded")
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    print(f"SFM adapter not available: {e}")
    sfm_adapter = None

@app.get("/")
async def root():
    return {"message": "ALADDIN API Test", "status": "running"}

@app.get("/api/phishing/sensitivity")
async def get_phishing_sensitivity():
    """TEST: Real SFM integration for phishing sensitivity"""

    # PRODUCTION: Real SFM integration with mapping
    if SFM_ADAPTER_AVAILABLE and sfm_adapter and SFM_MAPPING_AVAILABLE:
        try:
            # Get mapped SFM function name
            sfm_func_name = get_sfm_function_name("get_phishing_sensitivity")
            print(f"Calling SFM function: {sfm_func_name}")

            success, result, error = sfm_adapter.execute_function(sfm_func_name, {})

            if success:
                # Ensure result has source marker
                if isinstance(result, dict):
                    if "source" not in result:
                        result["source"] = "sfm_real"
                    return result
                else:
                    # Wrap non-dict results
                    return {"data": result, "function": "get_phishing_sensitivity", "source": "sfm_real"}
            else:
                print(f"SFM call failed: {error}")
                return {"error": error, "function": "get_phishing_sensitivity", "sfm_function": sfm_func_name, "source": "sfm_error"}

        except Exception as e:
            print(f"SFM exception: {e}")
            return {"error": str(e), "function": "get_phishing_sensitivity", "source": "sfm_exception"}

    # FALLBACK: Mock response when SFM not available
    return {
        "sensitivity": "high",
        "level": "aggressive",
        "blocked_sites": 15420,
        "last_update": "2026-02-02T13:00:00Z",
        "source": "mock_protection_active",
        "status": "PROTECTING_USERS"
    }

if __name__ == "__main__":
    print("🚀 Starting ALADDIN API Test Server...")
    uvicorn.run(app, host="127.0.0.1", port=8003)