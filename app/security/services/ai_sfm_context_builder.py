# -*- coding: utf-8 -*-
"""
E2.3 — сбор whitelisted агрегатов из SFM для LLM-контекста (без сырых логов).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from security.services.ai_sfm_aggregate_schema import (
    extract_allowed_aggregates,
    merge_aggregate_maps,
)

logger = logging.getLogger(__name__)

ExecuteFn = Callable[[str, Optional[Dict[str, Any]]], Tuple[bool, Any, Optional[str]]]

# SFM-функции, которые возвращают агрегаты (не event logs).
_DEFAULT_AGGREGATE_CALLS: Tuple[Tuple[str, Dict[str, Any]], ...] = (
    ("get_analytics_overview", {"period": "week"}),
    ("get_components_health", {}),
    ("get_phishing_sensitivity", {}),
)


@dataclass
class SFMContextBundle:
    aggregates: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)


class AISFMContextBuilder:
    """Загружает агрегаты через sfm_adapter.execute_function."""

    def __init__(
        self,
        execute_fn: ExecuteFn,
        aggregate_calls: Tuple[Tuple[str, Dict[str, Any]], ...] = _DEFAULT_AGGREGATE_CALLS,
    ):
        self._execute = execute_fn
        self._aggregate_calls = aggregate_calls

    def build(self, user_id: Optional[str] = None) -> SFMContextBundle:
        maps: List[Dict[str, Any]] = []
        sources: List[str] = []

        for func_name, params in self._aggregate_calls:
            call_params = dict(params)
            if user_id:
                call_params.setdefault("user_id", user_id)
            try:
                success, result, message = self._execute(func_name, call_params)
            except Exception as exc:
                logger.warning("SFM aggregate fetch failed func=%s err=%s", func_name, exc)
                continue

            if not success:
                logger.warning("SFM aggregate unavailable func=%s msg=%s", func_name, message)
                continue

            if not isinstance(result, dict):
                continue

            extracted = extract_allowed_aggregates(result)
            if extracted:
                maps.append(extracted)
                sources.append(func_name)

        merged = merge_aggregate_maps(maps)
        if merged:
            merged.setdefault("protection_status", "UNKNOWN")
            merged["context_kind"] = "sfm_aggregates_v1"

        return SFMContextBundle(aggregates=merged, sources=sources)
