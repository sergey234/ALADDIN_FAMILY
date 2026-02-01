#!/usr/bin/env python3
"""
ALADDIN API Gateway - Централизованная маршрутизация через SFM
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
# from security.safe_function_manager import SafeFunctionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ALADDIN API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# sfm = SafeFunctionManager()

# Маппинг основных endpoints
ENDPOINT_MAPPING = {
    "/api/components/status/{component_id}": "get_component_status",
    "/api/components/enable/{component_id}": "enable_component",
    "/api/components/disable/{component_id}": "disable_component",
}

@app.get("/health")
async def health():
    return {"status": "healthy", "gateway": "active"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_route(request: Request, path: str):
    endpoint = f"/{path}"

    if endpoint in ENDPOINT_MAPPING:
        function_name = ENDPOINT_MAPPING[endpoint]
        return {
            "endpoint": endpoint,
            "function": function_name,
            "message": "Route found but SFM not implemented yet"
        }

    return {"error": "Endpoint not found", "endpoint": endpoint}


