"""Rules for the Where-phone family snapshot. No database. No GPS trail."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

CHILD_ROLES = frozenset({"child", "teenager"})


def map_url_ok(raw: Optional[str]) -> bool:
    """One Apple Maps link: https://maps.apple.com/?ll=lat,lon"""
    url = (raw or "").strip()
    if not url or len(url) > 240 or any(ch.isspace() for ch in url):
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "maps.apple.com":
        return False
    if parsed.username or parsed.password or parsed.fragment:
        return False
    ll = (parse_qs(parsed.query).get("ll") or [""])[0]
    if "," not in ll:
        return False
    lat_s, lon_s = ll.split(",", 1)
    try:
        lat = float(lat_s)
        lon = float(lon_s)
    except ValueError:
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def rows_for_viewer(
    rows: List[Dict[str, Any]],
    role: Optional[str],
    own_member_id: Optional[str],
) -> List[Dict[str, Any]]:
    """A child or teenager sees only their own row. A parent sees the family list."""
    if (role or "").strip().lower() in CHILD_ROLES:
        own = (own_member_id or "").strip()
        return [row for row in rows if str(row.get("member_id") or "") == own]
    return list(rows)
