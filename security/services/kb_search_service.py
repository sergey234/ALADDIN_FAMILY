# -*- coding: utf-8 -*-
"""Internal KB search for RAG v1 (static corpus only)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from security.services import kb_embedding_client, kb_vector_store

logger = logging.getLogger(__name__)


def kb_search(
    query: str,
    *,
    locale: str = "ru",
    top_k: int = 5,
    topic: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k chunks from aladdin_kb_v1.
    Falls back to lexical search if embedding API fails.
    """
    q = (query or "").strip()
    if not q:
        return []

    try:
        vec = kb_embedding_client.embed_texts([q])[0]
        hits = kb_vector_store.search(
            vec, locale=locale, top_k=top_k, topic=topic, kb_version="kb_v1"
        )
        if hits:
            return hits
    except Exception as exc:
        logger.warning("kb_search embedding path failed: %s", exc)

    return kb_vector_store.search_lexical_fallback(
        q, locale=locale, top_k=top_k, kb_version="kb_v1"
    )
