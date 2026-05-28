from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EgressNode:
    id: str
    wg_host: str
    wg_port: int = 51820
    reality_port: int = 8443
    ovpn_port: int = 1194
    active: bool = False


def _parse_node(raw: Any, index: int) -> EgressNode | None:
    if not isinstance(raw, dict):
        return None
    nid = str(raw.get("id") or f"node-{index}").strip()[:48]
    host = str(raw.get("wg_host") or raw.get("host") or "").strip()
    try:
        wg_port = int(raw.get("wg_port") or 51820)
    except (TypeError, ValueError):
        wg_port = 51820
    try:
        reality_port = int(raw.get("reality_port") or 8443)
    except (TypeError, ValueError):
        reality_port = 8443
    try:
        ovpn_port = int(raw.get("ovpn_port") or 1194)
    except (TypeError, ValueError):
        ovpn_port = 1194
    active = bool(raw.get("active"))
    return EgressNode(
        id=nid or f"node-{index}",
        wg_host=host,
        wg_port=wg_port,
        reality_port=reality_port,
        ovpn_port=ovpn_port,
        active=active,
    )


def egress_nodes_from_settings(settings: Any) -> list[EgressNode]:
    raw = (getattr(settings, "vpn_egress_nodes_json", None) or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("VPN_EGRESS_NODES_JSON invalid: %s", e)
        return []
    if not isinstance(data, list):
        logger.warning("VPN_EGRESS_NODES_JSON must be a JSON array")
        return []
    out: list[EgressNode] = []
    for i, item in enumerate(data):
        node = _parse_node(item, i)
        if node:
            out.append(node)
    return out


def active_egress_nodes(settings: Any) -> list[EgressNode]:
    return [n for n in egress_nodes_from_settings(settings) if n.active and n.wg_host]


def primary_egress_node(settings: Any) -> EgressNode | None:
    nodes = egress_nodes_from_settings(settings)
    for n in nodes:
        if n.id == "primary" and n.active and n.wg_host:
            return n
    active = active_egress_nodes(settings)
    return active[0] if active else None


def egress_catalog_payload(settings: Any) -> dict[str, Any]:
    nodes = egress_nodes_from_settings(settings)
    return {
        "nodes": [
            {
                "id": n.id,
                "wg_host": n.wg_host,
                "wg_port": n.wg_port,
                "reality_port": n.reality_port,
                "ovpn_port": n.ovpn_port,
                "active": n.active,
            }
            for n in nodes
        ],
        "active_count": sum(1 for n in nodes if n.active and n.wg_host),
    }
