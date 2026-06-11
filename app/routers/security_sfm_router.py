"""
Legacy SFM explicit routes — migrated to domain routers (B1-01..B1-06).
Kept as empty router so imports in main.py stay stable.
"""
from fastapi import APIRouter

router = APIRouter(tags=["security-sfm"])
