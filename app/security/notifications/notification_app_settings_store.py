"""
In-process хранилище настроек уведомлений приложения (fallback без SFM/БД).
Аналогично push_token_registry: в проде заменяется персистентным слоем без смены контракта API.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


_lock = threading.Lock()
# userId -> запись
_by_user: Dict[str, Dict[str, Any]] = {}


@dataclass
class NotificationAppSettingsRecord:
    enabled: bool = True
    push_enabled: bool = True
    email_enabled: bool = False
    sound_enabled: bool = True
    device_id: Optional[str] = None
    version: int = 1
    last_modified: datetime = field(default_factory=datetime.now)

    def to_response_dict(self, user_id: str) -> Dict[str, Any]:
        return {
            "userId": user_id,
            "enabled": self.enabled,
            "pushEnabled": self.push_enabled,
            "emailEnabled": self.email_enabled,
            "soundEnabled": self.sound_enabled,
            "lastModified": self.last_modified,
            "deviceId": self.device_id,
            "version": self.version,
        }


def _record_from_dict(d: Dict[str, Any]) -> NotificationAppSettingsRecord:
    return NotificationAppSettingsRecord(
        enabled=bool(d.get("enabled", True)),
        push_enabled=bool(d.get("pushEnabled", True)),
        email_enabled=bool(d.get("emailEnabled", False)),
        sound_enabled=bool(d.get("soundEnabled", True)),
        device_id=d.get("deviceId"),
        version=int(d.get("version", 1)),
        last_modified=d.get("lastModified") or datetime.now(),
    )


def get_notification_settings(user_id: str) -> Dict[str, Any]:
    uid = (user_id or "").strip()
    if not uid:
        return NotificationAppSettingsRecord().to_response_dict("")
    with _lock:
        raw = _by_user.get(uid)
    if not raw:
        return NotificationAppSettingsRecord().to_response_dict(uid)
    return _record_from_dict(raw).to_response_dict(uid)


def update_notification_settings(
    user_id: str,
    enabled: Optional[bool] = None,
    push_enabled: Optional[bool] = None,
    email_enabled: Optional[bool] = None,
    sound_enabled: Optional[bool] = None,
    device_id: Optional[str] = None,
    version: Optional[int] = None,
) -> Dict[str, Any]:
    _ = version
    uid = (user_id or "").strip()
    if not uid:
        rec = NotificationAppSettingsRecord()
        return rec.to_response_dict(uid)

    with _lock:
        prev = _by_user.get(uid)
        if prev:
            cur = _record_from_dict(prev)
        else:
            cur = NotificationAppSettingsRecord()

        if enabled is not None:
            cur.enabled = enabled
        if push_enabled is not None:
            cur.push_enabled = push_enabled
        if email_enabled is not None:
            cur.email_enabled = email_enabled
        if sound_enabled is not None:
            cur.sound_enabled = sound_enabled
        if device_id is not None:
            cur.device_id = device_id

        cur.version = cur.version + 1
        cur.last_modified = datetime.now()
        out = cur.to_response_dict(uid)
        _by_user[uid] = {
            "enabled": out["enabled"],
            "pushEnabled": out["pushEnabled"],
            "emailEnabled": out["emailEnabled"],
            "soundEnabled": out["soundEnabled"],
            "deviceId": out["deviceId"],
            "version": out["version"],
            "lastModified": out["lastModified"],
        }
    return out
