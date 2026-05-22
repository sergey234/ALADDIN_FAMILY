# -*- coding: utf-8 -*-
"""
E2.3 — схема: какие поля SFM допустимы в LLM-контексте (только агрегаты).
"""
from __future__ import annotations

from typing import Any, Dict, FrozenSet, Iterable, List, Mapping, Optional, Tuple

# Ключи, которые никогда не должны попадать в LLM-промпт (сырые логи, токены, история).
FORBIDDEN_LLM_PARAM_KEYS: FrozenSet[str] = frozenset(
    {
        "logs",
        "raw_logs",
        "log_lines",
        "log_entries",
        "events",
        "raw_events",
        "event_log",
        "event_logs",
        "stack_trace",
        "stacktrace",
        "traceback",
        "request_body",
        "response_body",
        "http_log",
        "debug_log",
        "payload_dump",
        "query_log",
        "sql",
        "jwt",
        "access_token",
        "refresh_token",
        "password",
        "headers",
        "chat_history",
        "conversations",
        "messages",
        "history",
        "raw_context",
        "device_logs",
        "network_capture",
        "pcap",
    }
)

# Разрешённые скалярные поля из SFM-ответов (агрегаты / метрики).
ALLOWED_AGGREGATE_SCALAR_KEYS: FrozenSet[str] = frozenset(
    {
        "protection_status",
        "overall_health",
        "period",
        "total_events_processed",
        "security_alerts_generated",
        "threats_blocked",
        "blocked_phishing_attempts",
        "suspicious_sites_detected",
        "false_positives",
        "false_positive_rate",
        "detection_accuracy",
        "system_uptime_percent",
        "average_response_time_ms",
        "active_protections",
        "ml_models_active",
        "active_rules_count",
        "sensitivity_level",
        "detection_mode",
        "total_components",
        "healthy_components",
        "security_score",
        "ml_model_version",
        "last_update",
        "last_model_update",
        "status",
    }
)

# Разрешённые поля внутри элементов списка components (без URL/логов).
ALLOWED_COMPONENT_ITEM_KEYS: FrozenSet[str] = frozenset(
    {"id", "status", "uptime", "health", "is_enabled"}
)

_MAX_STRING_LEN = 256
_MAX_LIST_ITEMS = 16


def _coerce_scalar(value: Any) -> Optional[Any]:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed or len(trimmed) > _MAX_STRING_LEN:
            return None
        return trimmed
    return None


def _sanitize_component_list(items: Any) -> List[Dict[str, Any]]:
    if not isinstance(items, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in items[:_MAX_LIST_ITEMS]:
        if not isinstance(item, dict):
            continue
        row = {
            k: _coerce_scalar(item.get(k))
            for k in ALLOWED_COMPONENT_ITEM_KEYS
            if k in item and _coerce_scalar(item.get(k)) is not None
        }
        if row:
            out.append(row)
    return out


def extract_allowed_aggregates(sfm_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Вырезает только whitelisted агрегаты из ответа SFM."""
    out: Dict[str, Any] = {}
    for key in ALLOWED_AGGREGATE_SCALAR_KEYS:
        if key not in sfm_result:
            continue
        val = _coerce_scalar(sfm_result.get(key))
        if val is not None:
            out[key] = val

    if "components" in sfm_result:
        components = _sanitize_component_list(sfm_result.get("components"))
        if components:
            out["components_summary"] = components
            out["total_components"] = out.get("total_components") or len(components)
            out["healthy_components"] = out.get("healthy_components") or sum(
                1 for c in components if str(c.get("status", "")).lower() in {"healthy", "enabled", "active"}
            )

    recs = sfm_result.get("personal_recommendations")
    if isinstance(recs, list):
        safe_recs = [
            s for s in (_coerce_scalar(x) for x in recs[:8]) if s
        ]
        if safe_recs:
            out["recommendation_topics"] = safe_recs

    return out


def merge_aggregate_maps(maps: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for m in maps:
        for k, v in m.items():
            if k not in merged:
                merged[k] = v
    return merged


def _strip_forbidden_nested(value: Any, path: str, removed: List[str]) -> Any:
    """Рекурсивно убирает запрещённые ключи из dict/list (без raw logs в aggregates)."""
    if isinstance(value, dict):
        clean: Dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            child_path = f"{path}.{key}" if path else key
            if lower in FORBIDDEN_LLM_PARAM_KEYS:
                removed.append(child_path)
                continue
            clean[key] = _strip_forbidden_nested(item, child_path, removed)
        return clean
    if isinstance(value, list):
        return [
            _strip_forbidden_nested(item, f"{path}[]", removed)
            for item in value[:_MAX_LIST_ITEMS]
        ]
    return value


def strip_forbidden_llm_params(data: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Удаляет запрещённые ключи (верхний уровень + вложенные); возвращает (clean, removed_keys)."""
    removed: List[str] = []
    out: Dict[str, Any] = {}
    for key, value in data.items():
        lower = key.lower()
        if lower in FORBIDDEN_LLM_PARAM_KEYS:
            removed.append(key)
            continue
        if key == "sfm_aggregates" and isinstance(value, dict):
            out[key] = _strip_forbidden_nested(value, "sfm_aggregates", removed)
            continue
        out[key] = _strip_forbidden_nested(value, key, removed)
    return out, removed
