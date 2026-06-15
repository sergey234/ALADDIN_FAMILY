"""M-03 / M-04 — antifake upload hardening + PII-safe logging helpers."""
from __future__ import annotations

import hashlib
import ipaddress
import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from app.services.antifake_call_directory_store import phone_log_hash

logger = logging.getLogger(__name__)

_BLOCKED_URL_SCHEMES = frozenset(
    {"file", "ftp", "gopher", "data", "javascript", "vbscript", "blob"}
)
_PRIVATE_NETS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
)

_MEDIA_MIME_ALLOWLIST = {
    "audio": frozenset({"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/aac", "audio/ogg", "application/octet-stream"}),
    "video": frozenset({"video/mp4", "video/quicktime", "video/webm", "application/octet-stream"}),
    "document": frozenset({"application/pdf", "image/jpeg", "image/png", "application/octet-stream"}),
    "call": frozenset({"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/aac", "application/octet-stream"}),
}


class AntifakeSecurityError(ValueError):
    """Client-safe validation failure (no internal details)."""


def redact_text_for_log(text: str, *, max_len: int = 48) -> str:
    """M-04: never log raw user text — hash prefix only."""
    raw = (text or "").strip()
    if not raw:
        return "empty"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"sha256:{digest}:len={len(raw)}"


def redact_url_for_log(url: str) -> str:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return redact_text_for_log(url)
    path = parsed.path or "/"
    if len(path) > 64:
        path = path[:32] + "…"
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def redact_phone_for_log(phone: Optional[str]) -> str:
    return phone_log_hash(phone or "")


def validate_check_url(url: str) -> str:
    """M-03: block SSRF-prone URLs before SFM/heuristic analysis."""
    raw = (url or "").strip()
    if not raw:
        raise AntifakeSecurityError("empty_url")
    if len(raw) > 2048:
        raise AntifakeSecurityError("url_too_long")

    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise AntifakeSecurityError("unsupported_url_scheme")
    if scheme in _BLOCKED_URL_SCHEMES:
        raise AntifakeSecurityError("blocked_url_scheme")

    host = (parsed.hostname or "").lower().strip(".")
    if not host:
        raise AntifakeSecurityError("invalid_url_host")
    if host in ("localhost", "metadata.google.internal"):
        raise AntifakeSecurityError("blocked_url_host")
    if host.endswith(".local") or host.endswith(".internal"):
        raise AntifakeSecurityError("blocked_url_host")

    if _host_is_private(host):
        raise AntifakeSecurityError("blocked_private_url")

    # Credentials in URL are suspicious for user-submitted checks
    if parsed.username or parsed.password:
        raise AntifakeSecurityError("url_credentials_not_allowed")

    return raw if "://" in raw else f"https://{raw}"


def _host_is_private(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
            try:
                addr = ipaddress.ip_address(host)
            except ValueError:
                return False
        else:
            return False
    return any(addr in net for net in _PRIVATE_NETS)


def validate_media_upload(
    *,
    job_type: str,
    file_name: str,
    file_bytes: bytes,
    content_type: Optional[str],
) -> None:
    """M-03: size/MIME/filename guards for multipart uploads."""
    if not file_bytes:
        raise AntifakeSecurityError("empty_upload")
    if len(file_bytes) > 25 * 1024 * 1024:
        raise AntifakeSecurityError("file_too_large")

    name = Path(file_name or "upload").name
    if name != file_name and ".." in (file_name or ""):
        raise AntifakeSecurityError("invalid_filename")
    if not re.fullmatch(r"[\w.\-]{1,120}", name):
        raise AntifakeSecurityError("invalid_filename")

    allowed = _MEDIA_MIME_ALLOWLIST.get(job_type)
    if allowed is None:
        raise AntifakeSecurityError("unsupported_media_type")
    ctype = (content_type or "application/octet-stream").split(";")[0].strip().lower()
    if ctype not in allowed:
        raise AntifakeSecurityError("unsupported_content_type")


def assert_upload_path_under_root(file_path: str | Path, upload_root: Path) -> Path:
    """Prevent path traversal when worker reads queued uploads."""
    resolved = Path(file_path).resolve()
    root = upload_root.resolve()
    if root not in resolved.parents and resolved != root:
        logger.warning("antifake_upload_path_escape blocked path=%s", redact_text_for_log(str(file_path)))
        raise AntifakeSecurityError("invalid_upload_path")
    return resolved
