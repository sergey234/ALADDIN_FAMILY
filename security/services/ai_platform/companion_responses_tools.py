# -*- coding: utf-8 -*-
"""P2-07 — Responses API style tool registry for companion turns."""

from __future__ import annotations

from typing import Any, Dict, List

from .feature_flags import WEB_SEARCH_ENABLED, VISION_ENABLED


def companion_tool_manifest(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Tool definitions exposed to orchestrator / assistant layer."""
    tools: List[Dict[str, Any]] = [
        {
            "type": "function",
            "name": "companion_emotion",
            "description": "Pick hero emotion for reply",
        },
        {
            "type": "function",
            "name": "family_safety_tip",
            "description": "PG safety tip when domain=safety",
        },
    ]
    if WEB_SEARCH_ENABLED:
        tools.append(
            {
                "type": "function",
                "name": "web_search",
                "description": "Search the public web for factual questions",
            }
        )
    if VISION_ENABLED:
        tools.append(
            {
                "type": "function",
                "name": "describe_attachment",
                "description": "Describe uploaded image/PDF",
            }
        )
    age = (ctx.get("age_band") or "parent").lower()
    if age == "senior":
        tools.append(
            {
                "type": "function",
                "name": "nostalgic_topic",
                "description": "Gentle nostalgic conversation starter",
            }
        )
    return tools


def tools_used_for_turn(
    *,
    web_search: bool,
    attachments: bool,
    orchestrator: bool,
) -> List[str]:
    used = ["companion_chat"]
    if orchestrator:
        used.append("orchestrator")
    if web_search:
        used.append("web_search")
    if attachments:
        used.append("attachments")
    return used
