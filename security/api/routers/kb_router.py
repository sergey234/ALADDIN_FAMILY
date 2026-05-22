# -*- coding: utf-8 -*-
"""Internal KB search API (RAG v1 static corpus)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from security.services.kb_search_service import kb_search

router = APIRouter(prefix="/api/internal/kb", tags=["KB RAG"])


class KBSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field("ru", pattern="^(ru|en)$")
    top_k: int = Field(5, ge=1, le=20)
    topic: Optional[str] = None


class KBSearchHit(BaseModel):
    chunk_id: str
    parent_id: str
    topic: str
    title: Optional[str] = None
    text: str
    source: Optional[str] = None
    score: float


class KBSearchResponse(BaseModel):
    index: str = "aladdin_kb_v1"
    hits: List[KBSearchHit]


@router.post("/search", response_model=KBSearchResponse)
async def kb_search_endpoint(body: KBSearchRequest) -> KBSearchResponse:
    try:
        raw = kb_search(
            body.query,
            locale=body.locale,
            top_k=body.top_k,
            topic=body.topic,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"kb_search failed: {exc}") from exc
    hits = [
        KBSearchHit(
            chunk_id=h["chunk_id"],
            parent_id=h["parent_id"],
            topic=h["topic"],
            title=h.get("title"),
            text=h["text"],
            source=h.get("source"),
            score=float(h.get("score", 0)),
        )
        for h in raw
    ]
    return KBSearchResponse(hits=hits)
