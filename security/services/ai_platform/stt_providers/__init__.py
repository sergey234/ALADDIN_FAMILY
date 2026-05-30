# -*- coding: utf-8 -*-
"""Companion server STT providers (Yandex primary, OpenAI EU backup)."""

from .router import active_provider_name, server_stt_configured, transcribe_with_fallback

__all__ = ["active_provider_name", "server_stt_configured", "transcribe_with_fallback"]
