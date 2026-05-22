# -*- coding: utf-8 -*-
"""Embeddings for static KB (OpenRouter or OpenAI-compatible API)."""
from __future__ import annotations

import os
from typing import List, Optional

KB_EMBEDDING_DIM = 1536
DEFAULT_MODEL = os.getenv("KB_EMBEDDING_MODEL", "openai/text-embedding-3-small")


def _client():
    from openai import OpenAI  # type: ignore

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY or OPENAI_API_KEY required for KB embeddings")
    base_url = os.getenv("KB_EMBEDDING_BASE_URL")
    if not base_url and os.getenv("OPENROUTER_API_KEY"):
        base_url = "https://openrouter.ai/api/v1"
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def embed_texts(texts: List[str], *, model: Optional[str] = None) -> List[List[float]]:
    if not texts:
        return []
    client = _client()
    model_name = model or DEFAULT_MODEL
    # OpenAI SDK accepts batch input
    resp = client.embeddings.create(model=model_name, input=texts)
    ordered = sorted(resp.data, key=lambda row: row.index)
    vectors = [row.embedding for row in ordered]
    for vec in vectors:
        if len(vec) != KB_EMBEDDING_DIM:
            raise RuntimeError(f"unexpected embedding dim {len(vec)} (expected {KB_EMBEDDING_DIM})")
    return vectors
