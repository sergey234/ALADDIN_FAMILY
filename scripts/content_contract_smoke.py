#!/usr/bin/env python3
"""
Smoke check for production content contract.

Checks:
1) /api/health
2) OpenAPI contains:
   - /api/content/manifest (GET)
   - /api/content/delta (GET)
3) /api/content/manifest response shape
   - category/item density and metadata quality gates
4) /api/content/delta?fromVersion=0 response shape
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def fetch_json(url: str, timeout: int = 10) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    base = os.environ.get("ALADDIN_API_BASE", "http://149.154.65.180:8002").rstrip("/")
    min_items_per_category = int(os.environ.get("ALADDIN_CONTENT_MIN_ITEMS_PER_CATEGORY", "3"))

    print(f"SMOKE base={base} min_items_per_category={min_items_per_category}")

    health = fetch_json(f"{base}/api/health")
    require(health.get("status") == "ok", f"Health check failed: {health}")
    print("OK health")

    openapi = fetch_json(f"{base}/openapi.json", timeout=15)
    paths = openapi.get("paths", {})
    require("/api/content/manifest" in paths, "Missing /api/content/manifest in OpenAPI")
    require("get" in paths["/api/content/manifest"], "Missing GET for /api/content/manifest")
    require("/api/content/delta" in paths, "Missing /api/content/delta in OpenAPI")
    require("get" in paths["/api/content/delta"], "Missing GET for /api/content/delta")
    print("OK openapi paths")

    manifest = fetch_json(f"{base}/api/content/manifest")
    require("manifest" in manifest, "Manifest envelope key is missing")
    m = manifest["manifest"]
    require(isinstance(m, dict), "manifest must be object")
    for key in ("manifest_version", "generated_at", "min_supported_app_version", "checksum_sha256", "categories", "items"):
        require(key in m, f"manifest missing key: {key}")
    require(isinstance(m.get("categories"), list), "manifest.categories must be list")
    require(isinstance(m.get("items"), list), "manifest.items must be list")
    categories = m.get("categories") or []
    items = m.get("items") or []

    category_ids = []
    for c in categories:
        require(isinstance(c, dict), "each category must be object")
        cid = str(c.get("id", "")).strip()
        require(cid, "category.id must be non-empty")
        category_ids.append(cid)
    require(len(set(category_ids)) == len(category_ids), "category.id must be unique")

    item_ids = []
    counts_by_category = {}
    category_set = set(category_ids)
    for item in items:
        require(isinstance(item, dict), "each item must be object")
        item_id = str(item.get("id", "")).strip()
        require(item_id, "item.id must be non-empty")
        item_ids.append(item_id)

        category_id = str(item.get("category_id") or item.get("categoryId") or "").strip()
        require(category_id in category_set, f"item.category_id must reference known category: {category_id}")
        counts_by_category[category_id] = counts_by_category.get(category_id, 0) + 1

        metadata = item.get("metadata")
        require(isinstance(metadata, dict), "item.metadata must be object")
        require(str(metadata.get("locale", "")).strip(), "item.metadata.locale must be non-empty")
        require(str(metadata.get("title", "")).strip(), "item.metadata.title must be non-empty")
        duration = metadata.get("estimated_duration_sec")
        if duration is None:
            duration = metadata.get("estimatedDurationSec")
        if duration is not None:
            require(int(duration) > 0, "estimated_duration_sec must be > 0 when present")
    require(len(set(item_ids)) == len(item_ids), "item.id must be unique")

    for cid in category_ids:
        require(
            counts_by_category.get(cid, 0) >= min_items_per_category,
            f"category {cid} has fewer than {min_items_per_category} items",
        )
    print("OK manifest response")

    query = urllib.parse.urlencode({"fromVersion": "0"})
    delta = fetch_json(f"{base}/api/content/delta?{query}")
    require("delta" in delta, "Delta envelope key is missing")
    d = delta["delta"]
    require(isinstance(d, dict), "delta must be object")
    for key in ("from_version", "to_version", "added", "updated", "removed_ids", "checksum_sha256"):
        require(key in d, f"delta missing key: {key}")
    require(isinstance(d.get("added"), list), "delta.added must be list")
    require(isinstance(d.get("updated"), list), "delta.updated must be list")
    require(isinstance(d.get("removed_ids"), list), "delta.removed_ids must be list")
    print("OK delta response")

    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)

