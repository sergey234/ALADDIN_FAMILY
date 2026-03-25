"""
Precision Family Router bridge for API Gateway.

This module is intentionally importable from the gateway's flat router list:
`api_gateway.py` does `__import__(router_name)` and expects `router` symbol.

We re-export the real router from `app.routers.family`.
"""

try:
    from app.routers.family import router  # noqa: F401
except Exception as e:
    # Keep failure explicit; gateway will log the exception and continue.
    raise RuntimeError(f"Failed to import app.routers.family router: {e}")

