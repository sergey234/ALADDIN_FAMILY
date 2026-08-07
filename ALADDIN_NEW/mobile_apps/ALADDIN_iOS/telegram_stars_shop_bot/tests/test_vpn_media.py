from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from bot.services import vpn_media as vm


def test_happ_region_video_canonical_path() -> None:
    assert vm.HAPP_REGION_VIDEO_FILENAME == "happ_appstore_region_guide.mp4"
    assert vm.HAPP_REGION_VIDEO_PATH.name == vm.HAPP_REGION_VIDEO_FILENAME
    assert vm.HAPP_APP_ICON_FILENAME == "happ_app_icon.png"
    assert vm.HAPP_APP_ICON_PATH.is_file(), "place icon at assets/vpn/happ_app_icon.png"
    assert vm.HAPP_REGION_VIDEO_PATH.is_file(), "place mp4 at assets/vpn/happ_appstore_region_guide.mp4"


def test_file_id_cache_roundtrip(tmp_path: Path, monkeypatch) -> None:
    cache = tmp_path / "happ_media_file_ids.json"
    monkeypatch.setattr(vm, "_FILE_ID_CACHE_CANDIDATES", (cache,))
    assert vm._load_file_id_cache() == {}
    vm._save_file_id_cache({"video": "vid123", "icon": "ico456"})
    assert json.loads(cache.read_text(encoding="utf-8")) == {
        "video": "vid123",
        "icon": "ico456",
    }
    assert vm._load_file_id_cache()["video"] == "vid123"


def test_extract_file_ids_from_album_messages() -> None:
    photo_msg = SimpleNamespace(
        photo=[SimpleNamespace(file_id="ph1"), SimpleNamespace(file_id="ph2")],
        video=None,
    )
    video_msg = SimpleNamespace(photo=None, video=SimpleNamespace(file_id="vid9"))
    assert vm._extract_file_ids([photo_msg, video_msg]) == {"icon": "ph2", "video": "vid9"}


def test_happ_region_video_prefers_env_file_id(monkeypatch) -> None:
    monkeypatch.setattr(vm, "_load_file_id_cache", lambda: {"video": "cached"})
    settings = SimpleNamespace(vpn_happ_region_video_file_id="env-fid")
    assert vm.happ_region_video_input(settings) == "env-fid"


def test_happ_region_video_uses_cache_when_no_env(monkeypatch) -> None:
    monkeypatch.setattr(vm, "_load_file_id_cache", lambda: {"video": "cached-fid"})
    settings = SimpleNamespace(vpn_happ_region_video_file_id="")
    assert vm.happ_region_video_input(settings) == "cached-fid"
