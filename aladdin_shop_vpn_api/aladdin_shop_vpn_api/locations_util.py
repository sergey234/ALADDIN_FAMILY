from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_LOC_FOOTER = "⚙ Профили «белые списки» — см. полную инструкцию на сайте"

_BUILTIN: list[str] = [
    "🇪🇺 Автовыбор",
    "🇫🇷 Франция",
    "🇩🇪 Германия",
    "🇳🇱 Нидерланды",
    "🇮🇹 Италия",
    "🇭🇺 Венгрия",
    "🇬🇧 Великобритания",
    "🇺🇸 США",
]


@dataclass(frozen=True)
class LocationItem:
    slug: str
    label: str
    endpoint_host: str | None = None


def _slugify(label: str, index: int) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    if not s:
        return f"loc-{index}"
    return s[:48]


def _parse_item(raw: Any, index: int) -> LocationItem | None:
    if isinstance(raw, str):
        label = raw.strip()
        if not label:
            return None
        return LocationItem(slug=_slugify(label, index), label=label, endpoint_host=None)
    if isinstance(raw, dict):
        label = str(raw.get("label") or raw.get("line") or "").strip()
        if not label:
            return None
        slug = str(raw.get("slug") or "").strip() or _slugify(label, index)
        eh = str(raw.get("endpoint_host") or raw.get("endpoint") or "").strip() or None
        return LocationItem(slug=slug[:48], label=label, endpoint_host=eh)
    return None


def catalog_items_from_settings(settings: Any) -> list[LocationItem]:
    preview_n = max(1, min(int(settings.vpn_locations_preview_n), 50))
    raw = (settings.vpn_locations_json or "").strip()
    items: list[LocationItem] = []
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                if isinstance(data.get("items"), list):
                    for i, x in enumerate(data["items"]):
                        it = _parse_item(x, i)
                        if it:
                            items.append(it)
                else:
                    for i, x in enumerate(data.get("lines", [])):
                        it = _parse_item(x, i)
                        if it:
                            items.append(it)
                pn = data.get("preview_n")
                if pn is not None:
                    try:
                        preview_n = max(1, min(int(pn), 50))
                    except (TypeError, ValueError):
                        pass
            elif isinstance(data, list):
                for i, x in enumerate(data):
                    it = _parse_item(x, i)
                    if it:
                        items.append(it)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logger.warning("VPN_LOCATIONS_JSON invalid, using built-in catalog: %s", e)
            items = []
    if not items:
        items = [LocationItem(slug=_slugify(s, i), label=s) for i, s in enumerate(_BUILTIN)]
    default_ep = _default_wg_endpoint(settings)
    if default_ep:
        items = [
            LocationItem(
                slug=it.slug,
                label=it.label,
                endpoint_host=(it.endpoint_host or default_ep).strip() or default_ep,
            )
            for it in items
        ]
    return items


def _default_wg_endpoint(settings: Any) -> str:
    """Активная egress-нода или VPN_WG_ENDPOINT_HOST (single-node)."""
    try:
        from aladdin_shop_vpn_api.egress_nodes_util import primary_egress_node

        node = primary_egress_node(settings)
        if node and node.wg_host:
            return node.wg_host.strip()
    except ImportError:
        pass
    return (getattr(settings, "vpn_wg_endpoint_host", None) or "").strip()


def catalog_lines_from_settings(settings: Any) -> tuple[list[str], int]:
    """Полный список строк для UI «локации» и число строк в свёрнутом виде."""
    items = catalog_items_from_settings(settings)
    lines = [it.label for it in items]
    preview_n = max(1, min(int(settings.vpn_locations_preview_n), 50))
    full = list(lines)
    if _LOC_FOOTER not in "\n".join(full):
        full = full + [_LOC_FOOTER]
    preview_n = min(preview_n, max(1, len(full)))
    return full, preview_n


def catalog_payload_from_settings(settings: Any) -> dict[str, Any]:
    items = catalog_items_from_settings(settings)
    lines, preview_n = catalog_lines_from_settings(settings)
    return {
        "lines": lines,
        "preview_n": preview_n,
        "items": [
            {"slug": it.slug, "label": it.label, "endpoint_host": it.endpoint_host or ""}
            for it in items
            if it.label != _LOC_FOOTER
        ],
    }


def resolve_wg_endpoint_host(settings: Any, preferred_slug: str | None) -> str:
    default = (settings.vpn_wg_endpoint_host or "").strip()
    slug = (preferred_slug or "").strip()
    if not slug:
        return default
    for it in catalog_items_from_settings(settings):
        if it.slug == slug and it.endpoint_host:
            return it.endpoint_host.strip()
    return default
