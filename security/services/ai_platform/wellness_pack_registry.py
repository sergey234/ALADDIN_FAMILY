# -*- coding: utf-8 -*-
"""p3-20 — Knowledge Pack folder + pack_version locked per pillar session."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .wellness_prompt_builder import load_pillar_pack

# Folder under wellness_knowledge/{pillar}/{folder}/pack.yaml
DEFAULT_PACK_FOLDER = "v1"


def resolve_pack_for_pillar(
    pillar: str,
    *,
    locale: str = "ru",
    folder: str = DEFAULT_PACK_FOLDER,
) -> Tuple[str, str]:
    """Return (pack_folder, pack_version label from yaml)."""
    pack = load_pillar_pack(pillar, locale=locale, version=folder)
    version_label = str(pack.get("pack_version") or f"{pillar}_v1.0")
    return folder, version_label


def lock_session_pack(
    store: Any,
    user_id: str,
    pillar: str,
    *,
    locale: str = "ru",
    force: bool = False,
) -> Tuple[str, str]:
    """
    Pin pack folder + pack_version for the active wellness session.
    Reuses locked values while session_pillar_locked matches pillar.
    """
    ws = store.get_wellness_settings(user_id)
    locked_pillar = ws.get("session_pillar_locked") or ws.get("primary_pillar")
    existing_folder = ws.get("session_pack_folder")
    existing_version = ws.get("session_pack_version")
    if (
        not force
        and locked_pillar == pillar
        and existing_folder
        and existing_version
    ):
        return str(existing_folder), str(existing_version)

    folder, version_label = resolve_pack_for_pillar(pillar, locale=locale)
    store.update_wellness_misc(
        user_id,
        session_pack_folder=folder,
        session_pack_version=version_label,
    )
    return folder, version_label


def get_session_pack(
    store: Any,
    user_id: str,
    pillar: str,
    *,
    locale: str = "ru",
) -> Tuple[str, str]:
    """Read locked pack or resolve + lock for pillar."""
    ws = store.get_wellness_settings(user_id)
    if (
        ws.get("session_pack_folder")
        and ws.get("session_pack_version")
        and (ws.get("session_pillar_locked") or ws.get("primary_pillar")) == pillar
    ):
        return str(ws["session_pack_folder"]), str(ws["session_pack_version"])
    return lock_session_pack(store, user_id, pillar, locale=locale)


def session_pack_payload(
    store: Any,
    user_id: str,
    pillar: str,
    *,
    locale: str = "ru",
) -> Dict[str, str]:
    folder, version_label = get_session_pack(store, user_id, pillar, locale=locale)
    return {
        "pack_folder": folder,
        "pack_version": version_label,
    }
