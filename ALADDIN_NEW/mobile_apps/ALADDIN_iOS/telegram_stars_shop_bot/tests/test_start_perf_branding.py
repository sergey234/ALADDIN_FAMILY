from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from aiogram.types import FSInputFile

from bot.services import branding_media


def test_hero_photo_prefers_env_file_id(tmp_path: Path, monkeypatch) -> None:
    branding_media.clear_hero_file_id_cache_for_tests()
    monkeypatch.setattr(branding_media, "BRANDING_LOGO_PATH", tmp_path / "monkey.jpg")
    (tmp_path / "monkey.jpg").write_bytes(b"fake")
    settings = SimpleNamespace(start_photo_file_id="AAA:env_file_id")
    assert branding_media.hero_photo_input(settings) == "AAA:env_file_id"


def test_hero_photo_prefers_process_cache_over_upload(tmp_path: Path, monkeypatch) -> None:
    branding_media.clear_hero_file_id_cache_for_tests()
    monkeypatch.setattr(branding_media, "BRANDING_LOGO_PATH", tmp_path / "monkey.jpg")
    monkeypatch.setattr(branding_media, "BRANDING_LOGO_LEGACY_PATH", tmp_path / "legacy.png")
    (tmp_path / "monkey.jpg").write_bytes(b"fake")
    settings = SimpleNamespace(start_photo_file_id="")
    branding_media.remember_hero_file_id("BBB:cached")
    assert branding_media.hero_photo_input(settings) == "BBB:cached"


def test_hero_photo_falls_back_to_local_file(tmp_path: Path, monkeypatch) -> None:
    branding_media.clear_hero_file_id_cache_for_tests()
    logo = tmp_path / "monkey.jpg"
    logo.write_bytes(b"fake")
    monkeypatch.setattr(branding_media, "BRANDING_LOGO_PATH", logo)
    monkeypatch.setattr(branding_media, "BRANDING_LOGO_LEGACY_PATH", tmp_path / "legacy.png")
    settings = SimpleNamespace(start_photo_file_id="")
    out = branding_media.hero_photo_input(settings)
    assert isinstance(out, FSInputFile)
