# -*- coding: utf-8 -*-
"""
DEPRECATED shim — canonical router:
  security/api/routers/ai_assistant_router.py

Prod deploy must use security/api/ only (see ai-router-unify).
"""
from security.api.routers.ai_assistant_router import router  # noqa: F401

__all__ = ["router"]
