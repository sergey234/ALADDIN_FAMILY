# -*- coding: utf-8 -*-
"""
Multi-agent orchestrator stub.

Phase B: parallel SFM / Hermes / specialist agents, merge single companion reply.
NOW: single-path delegate to ai_assistant_chat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .config import ChatMode


@dataclass
class OrchestratorRequest:
    message: str
    user_id: str
    app_id: str
    mode: ChatMode = ChatMode.FAST
    context: str = "companion"
    character_id: Optional[str] = None
    response_language: Optional[str] = None
    thread_id: Optional[str] = None
    tools_enabled: List[str] = field(default_factory=list)


@dataclass
class OrchestratorResult:
    response_text: str
    intent: Optional[str] = None
    agents_used: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    grounded: Optional[bool] = None
    emotion: str = "happy"
    extra: Dict[str, Any] = field(default_factory=dict)


# Registry for Phase B — map intent → agent callable name
AGENT_REGISTRY = {
    "general": ["hermes", "ai_assistant"],
    "app_help": ["hermes", "ai_assistant"],
    "threat_analysis": ["sfm", "ai_assistant"],
    "emotional": ["psychological_support_agent"],
    "gamification": ["mobile_user_ai_agent"],
    "protection_status": ["sfm", "ai_assistant"],
}


async def run_orchestrator(
    req: OrchestratorRequest,
    *,
    delegate_chat: Callable,
) -> OrchestratorResult:
    """
    delegate_chat: async (message, context, user_id, response_language) -> dict
    with keys matching ChatMessageResponse.
    """
    agents = AGENT_REGISTRY.get(req.context, ["ai_assistant"])
    if req.mode == ChatMode.THINK:
        agents = ["hermes"] + agents

    result = await delegate_chat(
        req.message,
        req.context,
        req.user_id,
        req.response_language,
    )

    intent = result.get("intent")
    emotion = "alert" if intent in ("threat_analysis", "report_incident") else "happy"

    return OrchestratorResult(
        response_text=result.get("response", ""),
        intent=intent,
        agents_used=agents,
        tools_used=result.get("tools_used") or [],
        sources=result.get("sources") or [],
        grounded=result.get("grounded"),
        emotion=emotion,
        extra=result,
    )
