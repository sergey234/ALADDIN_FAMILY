# -*- coding: utf-8 -*-
"""Companion prompt priority stack + token budget (hero-x-09)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Rough char budget (~4 chars/token) for companion system-side blocks
DEFAULT_PROMPT_CHAR_BUDGET = 12000
_NEVER_DROP_PREFIXES = ("[WELLNESS", "[Companion ethics", "Этика L3")


@dataclass
class PromptLayer:
    name: str
    content: str
    priority: int
    droppable: bool = True


@dataclass
class AssembledPrompt:
    parts: List[str] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)
    total_chars: int = 0


def assemble_companion_prompt_layers(
    layers: List[PromptLayer],
    *,
    char_budget: int = DEFAULT_PROMPT_CHAR_BUDGET,
    user_message: str = "",
) -> AssembledPrompt:
    """
    Lower priority number = kept first. Ethics/wellness layers are never dropped.
    Trims droppable layers from lowest priority upward when over budget.
    """
    ordered = sorted(layers, key=lambda layer: layer.priority)
    kept: List[PromptLayer] = []
    dropped: List[str] = []
    for layer in ordered:
        if not layer.content:
            continue
        if not layer.droppable or any(layer.content.startswith(p) for p in _NEVER_DROP_PREFIXES):
            kept.append(layer)
        else:
            kept.append(layer)

    def total_len(parts: List[PromptLayer]) -> int:
        return sum(len(p.content) for p in parts) + len(user_message or "")

    # Drop from end (highest priority number among droppable)
    while total_len(kept) > char_budget:
        drop_idx: Optional[int] = None
        for i in range(len(kept) - 1, -1, -1):
            if kept[i].droppable and not any(
                kept[i].content.startswith(p) for p in _NEVER_DROP_PREFIXES
            ):
                drop_idx = i
                break
        if drop_idx is None:
            break
        dropped.append(kept.pop(drop_idx).name)

    parts = [layer.content for layer in kept if layer.content]
    return AssembledPrompt(
        parts=parts,
        dropped=dropped,
        total_chars=sum(len(p) for p in parts) + len(user_message or ""),
    )
