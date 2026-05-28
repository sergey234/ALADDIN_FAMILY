from __future__ import annotations

from types import SimpleNamespace

from aladdin_shop_vpn_api.locations_util import (
    catalog_items_from_settings,
    resolve_wg_endpoint_host,
)


def test_resolve_endpoint_from_slug() -> None:
    settings = SimpleNamespace(
        vpn_locations_json='{"items":[{"slug":"de","label":"DE","endpoint_host":"de.example.com"}]}',
        vpn_locations_preview_n=3,
        vpn_wg_endpoint_host="default.example.com",
    )
    assert resolve_wg_endpoint_host(settings, "de") == "de.example.com"
    assert resolve_wg_endpoint_host(settings, None) == "default.example.com"


def test_catalog_items_from_strings() -> None:
    settings = SimpleNamespace(
        vpn_locations_json='["🇩🇪 Германия"]',
        vpn_locations_preview_n=3,
        vpn_wg_endpoint_host="x",
        vpn_egress_nodes_json="",
    )
    items = catalog_items_from_settings(settings)
    assert len(items) == 1
    assert items[0].label.startswith("🇩🇪")
    assert items[0].endpoint_host == "x"


def test_catalog_items_endpoint_from_primary_egress() -> None:
    nodes = '[{"id":"primary","wg_host":"wg.primary.test","active":true}]'
    settings = SimpleNamespace(
        vpn_locations_json='{"lines":["🇫🇷 Франция"]}',
        vpn_locations_preview_n=3,
        vpn_wg_endpoint_host="fallback.test",
        vpn_egress_nodes_json=nodes,
    )
    items = catalog_items_from_settings(settings)
    assert items[0].endpoint_host == "wg.primary.test"
